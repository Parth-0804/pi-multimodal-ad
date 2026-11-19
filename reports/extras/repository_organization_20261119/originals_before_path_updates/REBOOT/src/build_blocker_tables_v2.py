"""Audit counts and prospective split support, never manufactures binary labels."""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path

import pyarrow.parquet as pq

PROJECT = Path(__file__).resolve().parents[2]
BASE = PROJECT / 'REBOOT'
CAMERAS = ['cam_high', 'cam_low', 'cam_left_wrist', 'cam_right_wrist']


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')


def eligible_binary(row):
    target = row.get('binary_target')
    return type(target) is int and target in (0, 1) and row.get('target_verified') is True


def split_gate(rows, grouping, requested_outer, requested_inner):
    eligible = [r for r in rows if eligible_binary(r)]
    known = [r for r in eligible if r.get(grouping)]
    counts = Counter(r['binary_target'] for r in eligible)
    groups = defaultdict(Counter)
    for r in known:
        groups[r[grouping]][r['binary_target']] += 1
    reasons = []
    if not eligible:
        reasons.append('No verified binary examples')
    if len(known) != len(eligible):
        reasons.append('Missing verified grouping identities')
    if len(groups) < requested_outer:
        reasons.append('Insufficient independent groups for requested outer partitions')
    if any(counts[k] == 0 for k in (0, 1)):
        reasons.append('Missing class support')
    # Counts alone cannot certify physical identity or produce a scientific split.
    return {'eligible_examples': len(eligible), 'positive': counts[1], 'negative': counts[0],
            'eligible_known_groups': len(groups), 'requested_outer': requested_outer, 'requested_inner': requested_inner,
            'folds_materialized': False, 'per_fold_class_support': None, 'group_overlap': None,
            'status': 'BLOCKED' if reasons else 'REQUIRES_EXPLICIT_GROUP_FOLD_VALIDATION', 'reasons': reasons}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--run', type=Path, required=True)
    args = p.parse_args()
    run = args.run.resolve()
    inventory = json.loads((BASE / '00_dataset_overview/PINNED_DATASET_INVENTORY.json').read_text())
    taskmap = {r['repo_id']: r for r in csv.DictReader((BASE / '00_dataset_overview/OBJECT_TASK_COLLECTION_COVERAGE.csv').open())}
    native = {r['episode_index']: r for r in json.loads((BASE / '02_labels_and_annotations/NATIVE_PHASE_RECORD_AUDIT.json').read_text())}
    identities = json.loads((run / 'reports/USBC_INDEPENDENT_IDENTITY_VERIFICATION.json').read_text())
    rows, errors = [], []
    media_signatures = defaultdict(list)
    chunk_episodes = defaultdict(list)
    for entry in inventory:
        repo = entry['repo_id']
        tr = taskmap[repo] if repo in taskmap else taskmap['REBOOT26/16mm-cylinder_recovery_install']
        role = tr['collection_role_inferred_from_repo_name']
        task = tr['object_inferred_from_repo_name'] + ':' + tr['direction_inferred_from_repo_name']
        tree = {f['path']: f for f in json.loads((PROJECT / entry['file_tree']).read_text()) if f['type'] == 'file'}
        episode_rows = []
        for path in sorted((PROJECT / entry['local_root'] / 'meta/episodes').rglob('*.parquet')):
            try:
                pf = pq.ParquetFile(path)
                columns = [c for c in pf.schema_arrow.names if c in ('episode_index', 'length', 'tasks', 'dataset_from_index', 'dataset_to_index') or c.startswith('videos/')]
                episode_rows.extend(pf.read(columns=columns).to_pylist())
            except Exception as exc:
                errors.append({'repo_id': repo, 'path': str(path.relative_to(PROJECT)), 'error': str(exc)[:180]})
        if repo == identities['source'] and not episode_rows:
            episode_rows = [{'episode_index': ep['episode_index'], 'length': ep['rows'], 'independent_identity_only': True}
                            for f in identities['files'] for ep in f.get('episodes', [])]
        for ep in episode_rows:
            idx = int(ep['episode_index'])
            ident = f'{repo}@{entry["revision"]}#episode={idx}'
            is_sample = repo == 'REBOOT26/sample_recovery-demonstration'
            is_full_alias = repo == 'REBOOT26/16mm-cylinder_recovery_install'
            ann = native.get(idx) if is_sample or is_full_alias else None
            row = {'source_episode_id': ident, 'repo_id': repo, 'revision': entry['revision'], 'episode_index': idx,
                   'length': int(ep['length']), 'task_name_inference': task, 'role_name_inference': role,
                   'index_parsed': not ep.get('independent_identity_only', False),
                   'identity_original_numeric_columns_verified': bool(ep.get('independent_identity_only', False)),
                   'native_phase_record_available': ann is not None, 'annotation_binding': 'direct_sample' if is_sample else 'exact_media_alias_to_sample' if ann else 'none',
                   'native_operator': ann['operator_id_native'] if ann else '', 'native_session_string': ann['collection_session_native'] if ann else '',
                   'physical_session_verified': False, 'expert_recovery_pair_verified': False,
                   'binary_target': None, 'target_verified': False, 'verified_positive_windows': 0, 'verified_negative_windows': 0,
                   'failure_completion_frame_available': False,
                   'native_annotation_sha256': '1d61ff591ff9f52628c49e71a0435ab83a62c87a4d607ae91a50478dbaf5813b' if ann else '',
                   'exclusion': 'Unresolved event/index semantics and no certified normal controls' if ann else 'No original window-level normal/failure targets located'}
            rows.append(row)
            if not ep.get('independent_identity_only'):
                signature = []
                for cam in CAMERAS:
                    key = 'observation.images.' + cam
                    prefix = 'videos/' + key + '/'
                    path = f"videos/{key}/chunk-{int(ep[prefix+'chunk_index']):03d}/file-{int(ep[prefix+'file_index']):03d}.mp4"
                    file = tree[path]
                    sha = file['lfs']['oid']
                    signature.append((sha, round(float(ep[prefix + 'from_timestamp']), 8), round(float(ep[prefix + 'to_timestamp']), 8)))
                    chunk_episodes[sha].append(ident)
                media_signatures[(tuple(signature), row['length'])].append(ident)
    alias_clusters = [ids for ids in media_signatures.values() if len(ids) > 1]
    alias_lookup = {}
    for ids in alias_clusters:
        canonical = sorted(ids, key=lambda x: ('sample_' in x, x))[0]
        alias_lookup.update({i: canonical for i in ids})
    for row in rows:
        row['canonical_media_episode_id'] = alias_lookup.get(row['source_episode_id'], row['source_episode_id'])
        row['analysis_alias_excluded'] = row['source_episode_id'] != row['canonical_media_episode_id']
    # Connected original-media components bind all windows/aliases sharing any video chunk.
    parent = {r['source_episode_id']: r['source_episode_id'] for r in rows}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for ids in chunk_episodes.values():
        for item in ids[1:]:
            parent[find(item)] = find(ids[0])
    groups = defaultdict(list)
    for r in rows:
        if r['index_parsed']:
            groups[find(r['source_episode_id'])].append(r['source_episode_id'])
    for row in rows:
        row['source_chunk_component'] = hashlib.sha256(find(row['source_episode_id']).encode()).hexdigest()[:16] if row['index_parsed'] else ''
    canonical = [r for r in rows if not r['analysis_alias_excluded']]
    label_csv = BASE / '02_labels_and_annotations/VERIFIED_LABEL_COVERAGE.csv'
    with label_csv.open('x', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    tasks = []
    for task in sorted({r['task_name_inference'] for r in canonical}):
        subset = [r for r in canonical if r['task_name_inference'] == task]
        tasks.append({'task_name_inference': task, 'inventory_episodes': len(subset), 'roles_not_binary_labels': dict(Counter(r['role_name_inference'] for r in subset)),
                      'native_annotation_episode_aliases': sum(r['native_phase_record_available'] for r in subset),
                      'verified_positive': 0, 'verified_negative': 0, 'unknown_binary_targets': len(subset),
                      'eligible_loto_train': 0, 'eligible_loto_test': 0,
                      'loto_class_support_train_test': False, 'loto_group_overlap_if_partitioned_by_task_name': 0,
                      'physical_session_overlap': 'unknown; no physical session registry'})
    protocols = {name: split_gate(canonical, group, outer, inner) for name, group, outer, inner in [
        ('session_disjoint', 'verified_physical_session', 2, 2),
        ('task_disjoint', 'task_name_inference', 2, 2),
        ('leave_one_task_out', 'task_name_inference', 18, 2),
        ('three_outer_two_inner', 'verified_physical_recording_group', 3, 2)]}
    audit = {'scope': 'Original identity evidence and inventories; NO binary fold assignments or model metrics',
             'repository_entries': len(rows), 'parseable_index_entries': sum(r['index_parsed'] for r in rows),
             'independent_usbc_numeric_identities': sum(r['identity_original_numeric_columns_verified'] for r in rows),
             'media_alias_clusters': len(alias_clusters), 'media_alias_extra_entries': len(rows) - len(canonical),
             'unique_media_inventory_upper_bound': len(canonical), 'native_annotated_unique_episodes': sum(r['native_phase_record_available'] for r in canonical),
             'roles_not_binary_labels': dict(Counter(r['role_name_inference'] for r in canonical)),
             'native_operator_counts_annotated_only': dict(Counter(r['native_operator'] for r in canonical if r['native_phase_record_available'])),
             'native_session_counts_annotated_only': dict(Counter(r['native_session_string'] for r in canonical if r['native_phase_record_available'])),
             'unknown_session_inventory_episodes': sum(not r['native_session_string'] for r in canonical),
             'verified_physical_sessions': 0, 'verified_binary_examples': 0,
             'original_chunk_components': len(groups), 'shared_video_chunk_hashes': sum(len(set(ids)) > 1 for ids in chunk_episodes.values()),
             'task_inventory': tasks, 'protocols': protocols,
             'group_overlap_note': 'null for unmaterialized supervised folds; zero task-name overlap is not proof of physical independence',
             'remaining_uniqueness_limit': 'No complete raw trajectory comparison; exact media identities establish aliases, not independence of all other recordings',
             'metadata_parse_errors_preserved': errors}
    write_json(BASE / '06_evaluation_feasibility/VERIFIED_SPLIT_FEASIBILITY.json', audit)
    write_json(run / 'reports/EXACT_EPISODE_MEDIA_ALIASES.json', alias_clusters)
    write_json(run / 'reports/ORIGINAL_CHUNK_COMPONENTS.json', list(groups.values()))
    print(json.dumps({k: v for k, v in audit.items() if k not in ('task_inventory', 'protocols', 'metadata_parse_errors_preserved')}, indent=2))


if __name__ == '__main__':
    main()
