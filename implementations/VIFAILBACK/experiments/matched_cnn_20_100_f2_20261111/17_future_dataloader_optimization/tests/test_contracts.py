"""Negative data/receipt checks with tiny metadata; no media decoding."""
import copy
import json
import os

import numpy as np
import pytest
import torch

from future_dataloader import contracts
from matched_vifailback.common import signature


def tiny_context():
    ids = [70, 5, 43, 21, 90, 8, 35, 62]
    return {'jobs': {'outer0_inner0': {'ids': {'T': ids}}},
            'lookup': {eid: {'episode_index': eid, 'frame_count': length, 'label': i % 2}
                       for i, (eid, length) in enumerate(zip(ids, [500, 80, 200, 80, 900, 120, 300, 600]))}}


def test_frame_count_selection_is_proper_T_label_blind_and_stable():
    ctx = tiny_context()
    selected = contracts.select_contract_ids(ctx)
    assert selected == [5, 8, 70, 90]
    for row in ctx['lookup'].values():
        row['label'] = 1 - row['label']
    assert contracts.select_contract_ids(ctx) == selected
    with pytest.raises(ValueError, match='at most four'):
        contracts.select_contract_ids(ctx, 5)


def test_zero_based_epoch_order_preserves_membership_and_numpy_global_rng():
    ctx = tiny_context()
    before = np.random.get_state()
    for seed in (42, 123, 20261023):
        first = contracts.epoch_ids(ctx, seed, 0)
        later = contracts.epoch_ids(ctx, seed, 19)
        assert first == contracts.epoch_ids(ctx, seed, 0)
        assert first != later
        assert sorted(first) == sorted(later) == sorted(ctx['jobs']['outer0_inner0']['ids']['T'])
    after = np.random.get_state()
    assert before[0] == after[0] and np.array_equal(before[1], after[1]) and before[2:] == after[2:]
    with pytest.raises(ValueError, match='nonnegative'):
        contracts.epoch_ids(ctx, epoch_index=-1)


def receipt_fixture(monkeypatch, tmp_path):
    binding = {'protocol_sha256': 'fixed', 'isolated_source_sha256': {'loader.py': 'code'},
               'configurations': {'base': {'workers': 2}, 'future': {'workers': 4}}}
    monkeypatch.setattr(contracts, 'validation_binding',
                        lambda ctx, names: dict(binding, configurations={name: binding['configurations'][name] for name in names}))
    receipt = {'schema': 1, 'status': 'PASS', 'binding': copy.deepcopy(binding),
               'binding_sha256': signature(binding), 'checked_config_names': ['base', 'future'],
               'selected_episode_ids': [70, 90]}
    path = tmp_path / 'receipt.json'
    path.write_text(json.dumps(receipt))
    return path, receipt


def test_receipt_accepts_valid_subset_and_rejects_source_drift(monkeypatch, tmp_path):
    path, receipt = receipt_fixture(monkeypatch, tmp_path)
    assert contracts.check_cpu_receipt(path, tiny_context(), ['base'])['status'] == 'PASS'
    receipt['binding']['isolated_source_sha256']['loader.py'] = 'changed'
    receipt['binding_sha256'] = signature(receipt['binding'])
    path.write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match='source/data binding drift'):
        contracts.check_cpu_receipt(path, tiny_context(), ['base'])


@pytest.mark.parametrize('tamper', ['failed', 'digest', 'preset', 'heldout_id'])
def test_receipt_refuses_invalid_evidence(monkeypatch, tmp_path, tamper):
    path, receipt = receipt_fixture(monkeypatch, tmp_path)
    if tamper == 'failed':
        receipt['status'] = 'FAIL'
    elif tamper == 'digest':
        receipt['binding_sha256'] = 'wrong'
    elif tamper == 'preset':
        receipt['checked_config_names'] = ['base']
    else:
        receipt['selected_episode_ids'] = [999999]
    path.write_text(json.dumps(receipt))
    with pytest.raises(ValueError):
        contracts.check_cpu_receipt(path, tiny_context(), ['future'])


def test_tensor_identity_rejects_wrong_shape_before_hashing():
    with pytest.raises(ValueError, match='shape drift'):
        contracts.tensor_identity(torch.zeros(3, 16, 3, 2, 2))


def test_validation_rejects_cuda_visibility_before_loading_context(monkeypatch, tmp_path):
    monkeypatch.setenv('CUDA_VISIBLE_DEVICES', '0')
    with pytest.raises(ValueError, match='Hide CUDA'):
        contracts.validate_cpu(tmp_path, ['baseline_w2_p1'])
