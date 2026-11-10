"""Synthetic tests of labels, multiview aggregation and group-safe role lineage."""
from copy import deepcopy
import numpy as np
import pytest

from matched_vifailback.data import (old_signature, pool_bank, selection_epoch, sensor_join,
                                     verify_frame_contract, verify_roles, verify_rows)


def frame_row(eid=0, task=0, label=0, length=33):
    indices = np.round(np.linspace(0, length - 1, 16)).astype(int).tolist()
    return {'episode_index': eid, 'canonical_task_id': task, 'label': label,
            'frame_count': length, 'frame_indices': indices,
            'frame_times_seconds': [i / 25 for i in indices],
            'camera_sha256': ['a' * 64, 'b' * 64, 'c' * 64],
            'camera_bytes': [100, 100, 100], 'camera_mtime_ns': [1, 1, 1],
            'selected_RGB_sha256': [['d' * 64] * 16 for _ in range(3)]}


def role_fixture():
    lookup = {}
    job = {'id': 'outer0_inner0', 'ids': {}, 'groups': {}, 'class_counts': {}}
    for i, role in enumerate(('T', 'V', 'C', 'A')):
        values = [i * 2, i * 2 + 1]
        for eid, label in zip(values, (0, 1)):
            lookup[eid] = frame_row(eid, i, label)
        job['ids'][role] = values; job['groups'][role] = [i]
        job['class_counts'][role] = {'0': 1, '1': 1}
    for eid, label in [(8, 0), (9, 1)]:
        lookup[eid] = frame_row(eid, 4, label)
    return job, lookup


def test_native_labels_and_uniform_camera_frame_contract():
    rows = [frame_row(1, 2, 0), frame_row(2, 3, 1)]
    report = verify_rows(rows, {1: 0, 2: 1})
    assert report['episodes'] == 2 and report['failures'] == report['successes'] == 1
    assert len(verify_frame_contract(rows[0])) == 16
    # Stationary RGB can repeat; temporal indices must remain distinct.
    assert len(set(rows[0]['selected_RGB_sha256'][0])) == 1


@pytest.mark.parametrize('mutation', ['duplicate', 'label', 'native', 'task55'])
def test_invalid_identity_or_native_label_is_rejected(mutation):
    rows = [frame_row(0, 1, 0), frame_row(1, 2, 1)]
    native = {0: 0, 1: 1}
    if mutation == 'duplicate': rows[1]['episode_index'] = 0
    if mutation == 'label': rows[0]['label'] = 'failure'
    if mutation == 'native': rows[0]['label'] = 1
    if mutation == 'task55': rows[0]['canonical_task_id'] = 55
    with pytest.raises(ValueError): verify_rows(rows, native)


@pytest.mark.parametrize('mutation', ['indices', 'camera', 'hash', 'clock'])
def test_changed_frame_contract_is_rejected(mutation):
    row = frame_row()
    if mutation == 'indices': row['frame_indices'][3] += 1
    if mutation == 'camera': row['selected_RGB_sha256'].pop()
    if mutation == 'hash': row['selected_RGB_sha256'][1][2] = 'not-a-hash'
    if mutation == 'clock': row['frame_times_seconds'][1] += .04
    with pytest.raises(ValueError): verify_frame_contract(row)


def test_pilot_meta_and_outer_are_distinct_without_rewriting_A():
    job, lookup = role_fixture(); before = deepcopy(job)
    report = verify_roles(job, lookup, extra_ids=[8, 9])
    assert job == before and job['ids']['A'] == [6, 7]
    assert report['A']['episodes'] == report['OUTER']['episodes'] == 2
    assert report['A']['ordered_episode_ids_sha256'] != report['OUTER']['ordered_episode_ids_sha256']


def test_episode_or_task_leakage_is_rejected_even_with_distinct_ids():
    job, lookup = role_fixture()
    with pytest.raises(ValueError): verify_roles(job, lookup, extra_ids=[6, 7])
    lookup[8]['canonical_task_id'] = 0; lookup[9]['canonical_task_id'] = 0
    with pytest.raises(ValueError): verify_roles(job, lookup, extra_ids=[8, 9])


def test_single_class_and_incorrect_declared_groups_are_rejected():
    job, lookup = role_fixture(); lookup[0]['label'] = 1
    with pytest.raises(ValueError, match='Single-class'): verify_roles(job, lookup)
    job, lookup = role_fixture(); job['groups']['T'] = [99]
    with pytest.raises(ValueError, match='Declared group'): verify_roles(job, lookup)


def test_multiview_features_are_pooled_once_per_episode():
    array = np.arange(2 * 3 * 16 * 896, dtype=np.float32).reshape(2, 3, 16, 896)
    pooled = pool_bank(array)
    assert pooled.shape == (2, 896) and not pooled.flags.writeable
    np.testing.assert_array_equal(pooled, array.mean((1, 2)))
    # Averaging features precedes a nonlinear classifier; averaging logits/probabilities is not substituted.
    square_after = pooled ** 2
    assert not np.array_equal(square_after, (array ** 2).mean((1, 2)))
    with pytest.raises(ValueError): pool_bank(array[:, 0])
    with pytest.raises(ValueError): pool_bank(array.astype(np.float64))


def test_sensor_join_respects_native_ids_and_retains_excluded_source_rows():
    bank = np.zeros((4, 280), np.float32); ids = [10, 20, 30, 40]
    index = sensor_join(ids, bank, [40, 10, 30])
    np.testing.assert_array_equal(bank[[index[e] for e in [40, 10, 30]]], bank[[3, 0, 2]])
    assert len(index) == 4
    with pytest.raises(ValueError): sensor_join([10, 10, 30, 40], bank, [10])
    with pytest.raises(ValueError): sensor_join(ids, bank, [50])
    with pytest.raises(ValueError): sensor_join(ids, bank[:, :28], [10])
    bank[1, 5] = np.nan
    with pytest.raises(ValueError): sensor_join(ids, bank, [10])


def test_selection_orders_macro_ap_then_weighted_bce_then_earliest():
    history = [dict(epoch=1, V_macro_AP=.6, V_weighted_BCE_same_T_positive_weight=.7),
               dict(epoch=2, V_macro_AP=.6, V_weighted_BCE_same_T_positive_weight=.5),
               dict(epoch=3, V_macro_AP=.6, V_weighted_BCE_same_T_positive_weight=.5),
               dict(epoch=4, V_macro_AP=.59, V_weighted_BCE_same_T_positive_weight=.1)]
    assert selection_epoch(history) == 2


def test_historical_signature_preserves_original_separators():
    import hashlib, json
    value = {'ids': [1, 3], 'seed': 42}
    assert old_signature(value) == hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def test_partial_task_membership_is_rejected():
    job, lookup = role_fixture()
    lookup[10] = frame_row(10, 0, 0)
    with pytest.raises(ValueError, match='Incomplete task membership'): verify_roles(job, lookup)
