"""Separately reviewable conservative QC refinement; never edit V1 outputs."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import pandas as pd
import numpy as np
from audit_sensors_and_splits import build_splits, table, save

RUN = Path(__file__).resolve().parents[1]
SOURCE = RUN.parent.parent


if __name__ == '__main__':
    policy = json.loads((RUN / 'config/COHORT_QC_POLICY_V2.json').read_text())
    dest = RUN / '02_COHORT_AND_SPLITS/V2_CONSERVATIVE_CORE'
    dest.mkdir(exist_ok=False)
    prefix = '02_COHORT_AND_SPLITS/V2_CONSERVATIVE_CORE/'
    q = pd.read_csv(RUN / '02_COHORT_AND_SPLITS/EPISODE_ELIGIBILITY_AND_EXCLUSIONS.csv')
    channels = pd.read_csv(RUN / '03_SENSOR_QUALITY/ALL_EPISODE_CHANNEL_QC.csv')
    outlier_ids = {}
    outliers = []
    for stream, key in [('observation.state', 'gross_position_absolute_limit_native_units'),
                        ('observation.velocity', 'gross_velocity_absolute_limit_native_units')]:
        part = channels[channels.stream == stream]
        bad = part[np.maximum(abs(part['min']), abs(part['max'])) > policy[key]]
        outlier_ids[stream] = set(bad.episode_index.astype(int))
        for row in bad.to_dict('records'):
            outliers.append({key: value for key, value in row.items() if key in ['episode_index', 'stream', 'channel', 'min', 'max']})
    regime, task_diagnostics = [], []
    rules = policy['systematic_coordinate_regime']
    for tid, members in q.groupby('canonical_task_id'):
        valid = members.velocity_position_derivative_median_correlation.dropna()
        fraction = float((valid < 0).mean()) if len(valid) else 0
        median = float(valid.median()) if len(valid) else None
        flag = len(valid) >= rules['minimum_episodes_with_derivative_diagnostic'] and fraction > rules['minimum_negative_correlation_fraction'] and median < rules['maximum_group_median_correlation']
        task_diagnostics.append({'canonical_task_id': int(tid), 'episodes': len(members), 'diagnostic_rows': len(valid),
                                 'negative_correlation_fraction': fraction, 'median_signed_correlation': median,
                                 'coordinate_convention_quarantine': flag})
        if flag: regime.append(int(tid))
    assert regime == [55], 'Unexpected regime map requires separate audit/adjudication'
    quality = []
    for row in q.replace({np.nan: None}).to_dict('records'):
        eid = int(row['episode_index'])
        reasons = (row.get('exclusion_reasons') or '').split('|')
        reasons = [reason for reason in reasons if reason]
        row['primary_acquisition_cohort_eligible_v1'] = row.pop('primary_acquisition_cohort_eligible')
        row['v1_outer_test_fold'] = row.pop('outer_test_fold')
        row.pop('independence_group', None)
        if eid in outlier_ids['observation.state']:
            reasons.append('GROSS_NATIVE_POSITION_OUTLIER_QUARANTINE')
        if eid in outlier_ids['observation.velocity']:
            reasons.append('GROSS_NATIVE_VELOCITY_OUTLIER_QUARANTINE')
        if row['canonical_task_id'] in regime:
            reasons.append('UNRESOLVED_POSITION_VELOCITY_COORDINATE_REGIME')
        row['core_eligible_v2'] = not reasons
        row['exclusion_reasons_v2'] = '|'.join(reasons)
        row['training_readiness_v2'] = 'PILOT_PAIRED_MEDIA_VERIFIED' if not reasons and row['all_three_videos_pilot_decoded'] else (
            'FULL_RGB_PAYLOAD_QC_PENDING' if not reasons else 'QUARANTINED_OR_EXCLUDED')
        row.pop('training_readiness', None)
        quality.append(row)
    core = [row for row in quality if row['core_eligible_v2']]
    old = json.loads((RUN / '03_SENSOR_QUALITY/FULL_SENSOR_AND_COHORT_AUDIT.json').read_text())
    plans, counts, groups, fits = build_splits(core, old['exact_sensor_content_components'])
    table(prefix + 'CORE_ELIGIBILITY_AND_EXCLUSIONS_V2.csv', quality)
    table(prefix + 'ELIGIBLE_CORE_EPISODES_V2.csv', core)
    table(prefix + 'EXCLUDED_OR_QUARANTINED_EPISODES_V2.csv', [row for row in quality if not row['core_eligible_v2']])
    table(prefix + 'SPLIT_CLASS_COUNTS_V2.csv', counts)
    table('03_SENSOR_QUALITY/GROSS_NUMERICAL_OUTLIERS.csv', outliers)
    table('03_SENSOR_QUALITY/TASK_POSITION_VELOCITY_CONSISTENCY.csv', task_diagnostics)
    save(prefix + 'OUTER_INNER_SPLITS_V2.json', {'version': policy['version'], 'assignment_seed': 20261029,
         'assignment': 'Hash ordered task-component identities; no labels used', 'outer_folds': 5, 'inner_folds': 4,
         'partitions': plans, 'group_count': groups,
         'freeze_condition': 'Researcher review and full RGB acquisition/QC; any eligibility change creates another cohort version, never overwrites V1/V2'})
    save(prefix + 'BASE_FIT_T_V_C_ASSESSMENT_V2.json', {'version': policy['version'], 'fits': fits,
         'T_role': 'Fit model/feature scalers', 'V_role': 'Finite hyperparameter/epoch selection',
         'C_role': 'Fit unweighted sigmoid probability calibration', 'assessment_role': 'Predict only; excluded from T/V/C'})
    all_files = {row['rfilename']: row for row in json.loads((SOURCE / 'source_evidence/vifailback_files.json').read_text())['siblings']}
    acquisition = []
    for row in core:
        for camera, key in [('cam_high', 'video_high'), ('cam_left_wrist', 'video_left'), ('cam_right_wrist', 'video_right')]:
            item = all_files[row[key]]
            path = SOURCE / 'source_evidence/vifailback' / row[key]
            present = path.exists()
            if present:
                assert hashlib.sha256(path.read_bytes()).hexdigest() == item['lfs']['sha256']
            acquisition.append({'episode_index': row['episode_index'], 'canonical_task_id': row['canonical_task_id'],
                                'camera': camera, 'relative_path': row[key], 'source_sha256': item['lfs']['sha256'],
                                'bytes': item['size'], 'local_verified': present, 'outer_test_fold': row['outer_test_fold']})
    table(prefix + 'REQUIRED_RGB_FILE_MANIFEST_V2.csv', acquisition)
    task_rows = []
    for tid in sorted({row['canonical_task_id'] for row in quality}):
        native = [row for row in quality if row['canonical_task_id'] == tid]
        kept = [row for row in core if row['canonical_task_id'] == tid]
        task_rows.append({'canonical_task_id': tid, 'source_directories': '|'.join(sorted({row['source_task'] for row in native})),
                          'native_episodes': len(native), 'core_episodes': len(kept),
                          'failures': sum(row['label'] for row in kept), 'successes': sum(1 - row['label'] for row in kept),
                          'outer_test_fold': kept[0]['outer_test_fold'] if kept else None})
    table(prefix + 'TASK_GROUPS_V2.csv', task_rows)
    summary = {'version': policy['version'], 'v1_primary_candidates': 4883, 'core_episodes': len(core),
               'core_counts': dict(Counter(row['native_outcome'] for row in core)), 'core_task_groups': groups,
               'groups_with_both_outcomes': sum(row['failures'] > 0 and row['successes'] > 0 for row in task_rows),
               'excluded_unique': len(quality) - len(core), 'new_quarantines_vs_v1': sum(row['primary_acquisition_cohort_eligible_v1'] and not row['core_eligible_v2'] for row in quality),
               'overlapping_reason_counts': dict(Counter(reason for row in quality for reason in row['exclusion_reasons_v2'].split('|') if reason)),
               'unresolved_coordinate_task_ids': regime, 'coordinate_regime_native_episodes': int(q.canonical_task_id.isin(regime).sum()),
               'gross_position_episode_indices': sorted(outlier_ids['observation.state']),
               'gross_velocity_episode_indices': sorted(outlier_ids['observation.velocity']),
               'pilot_verified_core_episodes': [row['episode_index'] for row in core if row['all_three_videos_pilot_decoded']],
               'full_rgb_payloads_pending_episodes': sum(not row['all_three_videos_pilot_decoded'] for row in core),
               'required_rgb': {scope: {'files': len(rows), 'bytes': sum(row['bytes'] for row in rows),
                     'missing_files': sum(not row['local_verified'] for row in rows),
                     'missing_bytes': sum(row['bytes'] for row in rows if not row['local_verified'])}
                    for scope, rows in [('primary_high', [row for row in acquisition if row['camera'] == 'cam_high']), ('all_three_cameras', acquisition)]},
               'training_T_presentations_one_epoch_all25fits': sum(len(fit['T_episode_indices']) for fit in fits),
               'status': 'Exactly enumerated conservative acquisition/core protocol cohort; full visual training cohort is not yet certified'}
    save(prefix + 'CORE_SUMMARY_V2.json', summary)
    print(json.dumps(summary, indent=2))
