"""Scientific admission and bounded-read regressions; no models or real relabeling."""
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from build_blocker_tables_v2 import eligible_binary, split_gate
from verify_usbc_identity_v2 import BoundedIdentityFile, check_identity_rows


@pytest.mark.parametrize('value', [None, 'recovery', 'expert', True])
def test_source_role_and_unverified_values_are_not_binary_targets(value):
    assert not eligible_binary({'binary_target': value, 'target_verified': True})
    assert not eligible_binary({'binary_target': 1, 'target_verified': False})


def test_both_classes_do_not_resolve_missing_or_single_group_identity():
    rows = [{'binary_target': i % 2, 'target_verified': True} for i in range(12)]
    result = split_gate(rows, 'physical_session', 3, 2)
    assert result['positive'] == result['negative'] == 6
    assert result['status'] == 'BLOCKED' and not result['folds_materialized']
    assert 'Missing verified grouping identities' in result['reasons']
    for row in rows:
        row['physical_session'] = 'same-session'
    result = split_gate(rows, 'physical_session', 3, 2)
    assert result['eligible_known_groups'] == 1 and result['status'] == 'BLOCKED'
    assert result['per_fold_class_support'] is None and result['group_overlap'] is None


def test_actual_numeric_identity_values_reject_gaps_and_invalid_times():
    rows = [{'episode_index': 7, 'frame_index': i, 'index': 100 + i,
             'timestamp': i / 30, 'task_index': 0} for i in range(4)]
    good = check_identity_rows(rows)[0]
    assert good['episode_index'] == 7 and good['rows'] == 4
    assert good['frame_indices_contiguous_zero_based']
    rows[2]['frame_index'] = 9
    rows[2]['index'] = 999
    rows[3]['timestamp'] = float('nan')
    bad = check_identity_rows(rows)[0]
    assert not bad['frame_indices_contiguous_zero_based']
    assert not bad['global_indices_contiguous']
    assert not bad['timestamps_finite_strictly_increasing']


def test_identity_reader_refuses_full_depth_download_before_network(tmp_path):
    reader = BoundedIdentityFile('https://example.invalid/depth.parquet', 500_000_000, tmp_path)
    with pytest.raises(ValueError, match='budget exceeded'):
        reader.read(-1)
    with pytest.raises(ValueError, match='budget exceeded'):
        reader.read(1_000_001)
    assert reader.total_bytes == 0 and not reader.receipts
