"""Full numerical payload QC, exact duplicate joins and task-disjoint split plan."""
from pathlib import Path
from collections import Counter, defaultdict
import csv
import hashlib
import json
import numpy as np
import pyarrow.parquet as pq

RUN = Path(__file__).resolve().parents[1]
SOURCE = RUN.parent.parent
KINDS = ['observation.state', 'observation.velocity', 'observation.effort']


def load(path):
    return json.loads(path.read_text())


def save(relative, obj):
    with (RUN / relative).open('x') as stream:
        json.dump(obj, stream, indent=2, allow_nan=False)
        stream.write('\n')


def table(relative, rows):
    with (RUN / relative).open('x', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(dict.fromkeys(key for row in rows for key in row)))
        writer.writeheader()
        writer.writerows(rows)


def signature(arrays):
    hasher = hashlib.sha256()
    for array in arrays:
        array = np.ascontiguousarray(array, dtype='<f4')
        hasher.update(str(array.shape).encode())
        hasher.update(array.tobytes())
    return hasher.hexdigest()


def parse_bool(value):
    return value is True or value == 'True'


def split_order(group, namespace):
    return hashlib.sha256(f'ViFailback-task-split-v1:20261029:{namespace}:{group}'.encode()).hexdigest()


class UnionFind:
    def __init__(self, values):
        self.parent = {value: value for value in values}

    def find(self, value):
        if self.parent[value] != value:
            self.parent[value] = self.find(self.parent[value])
        return self.parent[value]

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        self.parent[max(a, b)] = min(a, b)


def build_splits(eligible, related):
    task_union = UnionFind({row['canonical_task_id'] for row in eligible})
    by_id = {row['episode_index']: row for row in eligible}
    for members in related:
        tasks = sorted({by_id[eid]['canonical_task_id'] for eid in members if eid in by_id})
        for a, b in zip(tasks, tasks[1:]):
            task_union.union(a, b)
    for row in eligible:
        row['independence_group'] = task_union.find(row['canonical_task_id'])
    groups = sorted({row['independence_group'] for row in eligible}, key=lambda group: split_order(group, 'outer'))
    outer = {group: i % 5 for i, group in enumerate(groups)}
    plans, counts, base_fits = [], [], []

    def fit_plan(pool, assessment, k, role):
        pool_groups = sorted({row['independence_group'] for row in pool}, key=lambda group: split_order(group, f'fit{k}:{role}'))
        part = {group: ('T' if i % 10 < 6 else 'V' if i % 10 < 8 else 'C') for i, group in enumerate(pool_groups)}
        split = {name: [row for row in pool if part[row['independence_group']] == name] for name in ('T', 'V', 'C')}
        split['assessment'] = assessment
        group_sets = [{row['independence_group'] for row in rows} for rows in split.values()]
        assert all(not a & b for i, a in enumerate(group_sets) for b in group_sets[i + 1:])
        assert all({row['label'] for row in rows} == {0, 1} for rows in split.values())
        base_fits.append({'outer_fold': k, 'role': role,
                          **{name + '_episode_indices': sorted(row['episode_index'] for row in rows) for name, rows in split.items()},
                          **{name + '_task_ids': sorted({row['canonical_task_id'] for row in rows}) for name, rows in split.items()}})
    for k in range(5):
        test = [row for row in eligible if outer[row['independence_group']] == k]
        development = [row for row in eligible if outer[row['independence_group']] != k]
        dg = sorted({row['independence_group'] for row in development}, key=lambda group: split_order(group, f'outer{k}:inner'))
        inner = {group: i % 4 for i, group in enumerate(dg)}
        fit_plan(development, test, k, 'outer_assessment')
        for j in range(4):
            train = [row for row in development if inner[row['independence_group']] != j]
            validation = [row for row in development if inner[row['independence_group']] == j]
            roles = {'train': train, 'validation': validation, 'test': test}
            fit_plan(train, validation, k, f'inner_oof_{j}')
            ids = {name: {row['episode_index'] for row in rows} for name, rows in roles.items()}
            tasks = {name: {row['canonical_task_id'] for row in rows} for name, rows in roles.items()}
            assert ids['train'] | ids['validation'] | ids['test'] == set(by_id)
            for a, b in [('train', 'validation'), ('train', 'test'), ('validation', 'test')]:
                assert not ids[a] & ids[b] and not tasks[a] & tasks[b]
            assert all({row['label'] for row in rows} == {0, 1} for rows in roles.values())
            plans.append({'outer_fold': k, 'inner_fold': j,
                          **{name + '_episode_indices': sorted(values) for name, values in ids.items()},
                          **{name + '_task_ids': sorted(values) for name, values in tasks.items()}})
            counts.append({'outer_fold': k, 'inner_fold': j,
                           **{f'{name}_{key}': value for name, rows in roles.items() for key, value in {
                               'episodes': len(rows), 'tasks': len(tasks[name]), 'failure': sum(row['label'] for row in rows),
                               'success': sum(not row['label'] for row in rows)}.items()}})
    for row in eligible:
        row['outer_test_fold'] = outer[row['independence_group']]
    return plans, counts, len(groups), base_fits


if __name__ == '__main__':
    policy = load(RUN / 'config/COHORT_QC_POLICY.json')
    inventory = load(RUN / 'provenance/SENSOR_TABLE_INVENTORY.json')
    available = {row['path']: row for row in inventory if row['status'] != 'BLOCKED'}
    native = list(csv.DictReader((RUN / '02_COHORT_AND_SPLITS/ALL_NATIVE_EPISODES.csv').open()))
    meta = SOURCE / 'source_evidence/vifailback/meta'
    annotations = {row['episode_index']: row for row in map(json.loads, (meta / 'vifailback_annotations.jsonl').open())}
    published = {row['episode_index']: row['stats'] for row in map(json.loads, (meta / 'episodes_stats.jsonl').open())}
    files = {row['rfilename']: row for row in load(SOURCE / 'source_evidence/vifailback_files.json')['siblings']}
    pilot = {row['episode_index'] for row in load(SOURCE / 'checks/pilot_numerical_audit.json')}
    stream_hashes, rounded_hashes, video_triplets = defaultdict(list), defaultdict(list), defaultdict(list)
    quality, stream_rows = [], []
    cumulative = 0
    total_nonfinite = 0
    global_min = {kind: np.full(14, np.inf) for kind in KINDS}
    global_max = {kind: np.full(14, -np.inf) for kind in KINDS}
    valid_count = 0
    for raw in native:
        row = dict(raw)
        for key in ('episode_index', 'canonical_task_id', 'label', 'frame_count'):
            row[key] = int(row[key])
        eid, n = row['episode_index'], row['frame_count']
        row['native_human_intervention'] = parse_bool(row['native_human_intervention'])
        row['remote_four_file_join'] = parse_bool(row['remote_four_file_join'])
        problems = []
        record = available.get(row['data'])
        if record is None:
            problems.append('NUMERICAL_PAYLOAD_UNAVAILABLE')
        arrays = {}
        if record is not None:
            path = SOURCE / record['local_path']
            assert hashlib.sha256(path.read_bytes()).hexdigest() == record['expected_sha256']
            frame = pq.read_table(path, use_threads=False).to_pandas(use_threads=False)
            if len(frame) != n:
                problems.append('LENGTH_MISMATCH')
            tests = {
                'FRAME_INDEX_MISMATCH': np.array_equal(frame.frame_index, np.arange(n)),
                'GLOBAL_INDEX_MISMATCH': np.array_equal(frame['index'], np.arange(cumulative, cumulative + n)),
                'EPISODE_ID_MISMATCH': bool((frame.episode_index == eid).all()),
                'TASK_ID_MISMATCH': bool((frame.task_index == row['canonical_task_id']).all()),
            }
            times = frame.timestamp.to_numpy(dtype=float)
            time_error = float(np.max(np.abs(times - np.arange(n) / 25)))
            tests['TIMESTAMP_MISMATCH'] = bool(np.isfinite(times).all() and np.all(np.diff(times) > 0) and time_error < 1e-5)
            flags = np.stack(frame['complementary_info.vifailback_flags']).astype(bool)
            tests['LABEL_FLAG_MISMATCH'] = flags.shape == (n, 3) and bool((flags[:, 0] == bool(row['label'])).all())
            for i, kind in enumerate(['avoid', 'correct'], 1):
                tests[kind.upper() + '_FLAG_MISMATCH'] = np.flatnonzero(flags[:, i]).tolist() == annotations[eid][kind + '_keyframe_indices']
            problems.extend(name for name, passed in tests.items() if not passed)
            row['timestamp_max_error_seconds'] = time_error
            for kind in KINDS:
                array = np.stack(frame[kind]).astype(np.float32)
                arrays[kind] = array
                if array.shape != (n, 14):
                    problems.append(kind + ':SHAPE')
                    continue
                nonfinite = int((~np.isfinite(array)).sum())
                total_nonfinite += nonfinite
                if nonfinite:
                    problems.append(kind + ':NONFINITE')
                values = array.astype(float)
                low, high = values.min(0), values.max(0)
                ptp = high - low
                active = ptp > policy['position_variation_epsilon']
                means, stds = values.mean(0), values.std(0)
                old = published[eid][kind]
                extrema_match = bool(np.allclose(low, old['min'], rtol=1e-6, atol=1e-7) and np.allclose(high, old['max'], rtol=1e-6, atol=1e-7))
                if not extrema_match:
                    problems.append(kind + ':PUBLISHED_EXTREMA_MISMATCH')
                global_min[kind] = np.minimum(global_min[kind], low)
                global_max[kind] = np.maximum(global_max[kind], high)
                row[kind + '_varying_channels'] = int(active.sum())
                row[kind + '_nonfinite'] = nonfinite
                for channel in range(14):
                    stream_rows.append({'episode_index': eid, 'stream': kind, 'channel': channel,
                                        'min': low[channel], 'max': high[channel], 'mean_float64': means[channel],
                                        'std_float64': stds[channel], 'varies': bool(active[channel]),
                                        'published_std': old['std'][channel], 'extrema_match': extrema_match})
            if all(kind in arrays and arrays[kind].shape == (n, 14) for kind in KINDS):
                row['sensor_content_sha256'] = signature([arrays[kind] for kind in KINDS])
                stream_hashes[row['sensor_content_sha256']].append(eid)
                selected = np.linspace(0, n - 1, 32).round().astype(int)
                rounded = np.round(arrays['observation.state'][selected], decimals=3)
                rounded_hashes[signature([rounded])].append(eid)
                position = arrays['observation.state'].astype(float)
                velocity = arrays['observation.velocity'].astype(float)
                finite_difference = np.gradient(position, axis=0) * 25
                correlations = []
                for channel in [0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12]:
                    a, b = finite_difference[:, channel], velocity[:, channel]
                    if np.std(a) > 1e-6 and np.std(b) > 1e-6:
                        correlations.append(float(np.corrcoef(a, b)[0, 1]))
                row['velocity_position_derivative_median_correlation'] = float(np.median(correlations)) if correlations else None
                row['constant_position'] = row['observation.state_varying_channels'] == 0
            valid_count += not bool(problems)
        row['constant_position'] = row.get('constant_position', False)
        row['numerical_qc_issues'] = '|'.join(problems)
        row['numerical_payload_valid'] = not problems
        row['all_three_videos_pilot_decoded'] = eid in pilot
        triplet = tuple(files[row[key]]['lfs']['sha256'] for key in ('video_high', 'video_left', 'video_right'))
        video_triplets[triplet].append(eid)
        row['video_triplet_hash'] = hashlib.sha256(''.join(triplet).encode()).hexdigest()
        quality.append(row)
        cumulative += n
        if len(quality) % 500 == 0:
            print('Actual numerical payloads audited', len(quality), '/ 5202', flush=True)

    by_id = {row['episode_index']: row for row in quality}
    exact_sensor = [members for members in stream_hashes.values() if len(members) > 1]
    exact_three_camera = [members for members in video_triplets.values() if len(members) > 1]
    duplicates = []
    duplicate_copies = set()
    for members in exact_three_camera:
        if len({by_id[eid].get('sensor_content_sha256') for eid in members}) == 1:
            assert len({by_id[eid]['label'] for eid in members}) == 1, 'Duplicate outcome conflict requires separate adjudication'
            duplicates.append(sorted(members))
            duplicate_copies.update(sorted(members)[1:])
    for row in quality:
        reasons = []
        if not row['numerical_payload_valid']:
            reasons.append('NUMERICAL_QC_FAILED')
        if not row['remote_four_file_join']:
            reasons.append('PUBLISHED_MODALITY_MISSING')
        if row['frame_count'] < 16:
            reasons.append('INSUFFICIENT_FRAME_POSITIONS')
        if row['constant_position']:
            reasons.append('CONSTANT_POSITION_QUARANTINE')
        if row['episode_index'] in duplicate_copies:
            reasons.append('EXACT_MULTIMODAL_DUPLICATE_HIGHER_ID')
        row['sensor_cohort_eligible'] = not reasons
        if row['native_human_intervention']:
            reasons.append('NATIVE_ANNOTATED_HUMAN_INTERVENTION')
        row['primary_acquisition_cohort_eligible'] = not reasons
        row['exclusion_reasons'] = '|'.join(reasons)
        row['training_readiness'] = 'PILOT_PAIRED_MEDIA_VERIFIED' if not reasons and row['all_three_videos_pilot_decoded'] else (
            'FULL_RGB_PAYLOAD_QC_PENDING' if not reasons else 'EXCLUDED_BY_DECLARED_POLICY')
    eligible = [row for row in quality if row['primary_acquisition_cohort_eligible']]
    related = exact_sensor + exact_three_camera
    plans, split_counts, groups, base_fits = build_splits(eligible, related)
    table('02_COHORT_AND_SPLITS/EPISODE_ELIGIBILITY_AND_EXCLUSIONS.csv', quality)
    table('02_COHORT_AND_SPLITS/PRIMARY_ACQUISITION_COHORT.csv', eligible)
    table('02_COHORT_AND_SPLITS/EXCLUDED_EPISODES.csv', [row for row in quality if not row['primary_acquisition_cohort_eligible']])
    table('03_SENSOR_QUALITY/ALL_EPISODE_CHANNEL_QC.csv', stream_rows)
    table('02_COHORT_AND_SPLITS/SPLIT_CLASS_COUNTS.csv', split_counts)
    save('02_COHORT_AND_SPLITS/OUTER_INNER_TASK_DISJOINT_SPLITS.json', {
        'protocol': 'VIFAILBACK-TASKDISJOINT-v1', 'seed': 20261029, 'assignment': 'SHA-256 ordering of input-identity groups; modulo folds; no labels used',
        'status': 'Frozen task-disjoint acquisition/sensor cohort; visual payload QC must pass without selective outcome-based edits before training',
        'outer_folds': 5, 'inner_folds': 4, 'group_count': groups, 'partitions': plans})
    save('02_COHORT_AND_SPLITS/BASE_FIT_T_V_C_ASSESSMENT_PLAN.json', {
        'roles': {'T': 'gradient/logistic/boosting fit and feature normalization', 'V': 'epoch or finite candidate selection',
                  'C': 'unweighted sigmoid calibration only', 'assessment': 'base-branch prediction only; labels withheld until outer evaluation or F2/gate fitting as appropriate'},
        'assignment': 'Task-component hash ordering within each pool, 60/20/20 by modulo10; fixed across models and model seeds',
        'fits_per_condition_and_seed': len(base_fits), 'fits': base_fits})
    task_rows = []
    for tid in sorted({row['canonical_task_id'] for row in quality}):
        members = [row for row in quality if row['canonical_task_id'] == tid]
        kept = [row for row in eligible if row['canonical_task_id'] == tid]
        task_rows.append({'canonical_task_id': tid, 'instruction': members[0]['task_instruction'],
                          'source_directories': '|'.join(sorted({row['source_task'] for row in members})),
                          'native_episodes': len(members), 'eligible_episodes': len(kept),
                          'eligible_failures': sum(row['label'] for row in kept), 'eligible_successes': sum(not row['label'] for row in kept),
                          'independence_group': kept[0]['independence_group'] if kept else None,
                          'outer_test_fold': kept[0]['outer_test_fold'] if kept else None})
    table('02_COHORT_AND_SPLITS/TASK_GROUP_ASSIGNMENTS.csv', task_rows)
    summary = {'episodes': len(quality), 'actual_sensor_rows': cumulative, 'actual_tables_valid': int(valid_count),
               'nonfinite_values': total_nonfinite,
               'constant_position_episode_indices': [row['episode_index'] for row in quality if row['constant_position']],
               'native_human_intervention_episode_indices': [row['episode_index'] for row in quality if row['native_human_intervention']],
               'verified_exact_multimodal_duplicate_components': duplicates,
               'exact_sensor_content_components': exact_sensor,
               'rounded_32_position_trace_candidate_groups': [members for members in rounded_hashes.values() if len(members) > 1],
               'rounded_trace_limitation': 'Candidate search only, 3-decimal qpos at 32 uniform positions; not exhaustive near-duplicate or session detection',
               'sensor_cohort_counts': dict(Counter(row['native_outcome'] for row in quality if row['sensor_cohort_eligible'])),
               'primary_acquisition_cohort_counts': dict(Counter(row['native_outcome'] for row in eligible)),
               'primary_acquisition_cohort_size': len(eligible), 'eligible_task_groups': groups,
               'groups_with_both_outcomes': sum(row['eligible_failures'] > 0 and row['eligible_successes'] > 0 for row in task_rows),
               'fully_pilot_media_verified_primary_episodes': [row['episode_index'] for row in eligible if row['all_three_videos_pilot_decoded']],
               'exclusion_reason_counts': dict(Counter(reason for row in quality for reason in row['exclusion_reasons'].split('|') if reason)),
               'total_excluded': sum(not row['primary_acquisition_cohort_eligible'] for row in quality),
               'global_sensor_channels': {kind: {'global_min': global_min[kind].tolist(), 'global_max': global_max[kind].tolist(),
                   'globally_zero_indices': np.flatnonzero((global_min[kind] == 0) & (global_max[kind] == 0)).tolist()} for kind in KINDS},
               'maximum_converted_clock_error_seconds': max(row.get('timestamp_max_error_seconds', 0) for row in quality),
               'human_policy_limitation': 'Native human-intervention category is outcome-derived and incomplete for incidental hands; this defines a restricted estimand, not label-blind QC or proof of human absence',
               'full_visual_cohort_certified': False}
    save('03_SENSOR_QUALITY/FULL_SENSOR_AND_COHORT_AUDIT.json', summary)
    print(json.dumps({key: value for key, value in summary.items() if not isinstance(value, (list, dict)) or key.endswith('_counts')}, indent=2))
