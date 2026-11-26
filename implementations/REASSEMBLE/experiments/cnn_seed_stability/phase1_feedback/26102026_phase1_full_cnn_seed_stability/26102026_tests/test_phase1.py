"""Synthetic protocol, normalization, recovery and multiprocessing regressions."""
import sys
from pathlib import Path
import uuid

import numpy as np
import pytest
import torch
from torch import nn
from torch.utils.data import Dataset

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '26102026_source'))
sys.path.insert(0, str(ROOT / '26102026_tests'))
from synthetic_actions import SyntheticActions
from phase_common import EVIDENCE, EXEC, read
from phase_model import promote_normalization_affine, make_scheduler
from phase_loader import EpochLoader, epoch_order
from phase_metrics import metrics, stop_after_epoch, better, aligned_keys
from phase_checkpoint import EpochRecovery, restore_rng
from phase_training import tensor_equal_tree


def fresh_folder():
    path = EXEC / ('26102026_synthetic_validation_' + uuid.uuid4().hex[:10])
    path.mkdir(parents=True)
    return path


def test_normalization_promotion_preserves_forward_and_exposes_gradients():
    from transformers.models.rt_detr.modeling_rt_detr import RTDetrFrozenBatchNorm2d
    module = nn.Sequential(RTDetrFrozenBatchNorm2d(3))
    x = torch.arange(24, dtype=torch.float32).reshape(2, 3, 2, 2) / 10
    expected = module(x).detach()
    old_buffers = {n: v.clone() for n, v in module.named_buffers()}
    promoted = promote_normalization_affine(module)
    assert len(promoted) == 2
    assert torch.equal(expected, module(x))
    module(x).square().sum().backward()
    assert all(p.grad is not None and torch.isfinite(p.grad).all() and p.grad.abs().sum() > 0 for p in module.parameters())
    assert all(torch.equal(old_buffers[n], v) for n, v in module.named_buffers())


def test_split_plan_has_no_training_selection_calibration_prediction_overlap():
    plan = read(EVIDENCE / 'PHASE1_FIT_PLAN.json')
    from phase_common import STUDY
    rows = read(STUDY / 'data_manifests/cohort_and_frames.json')
    assert len(plan) == 25
    for job in plan:
        scopes = [set(rows[i]['recording_id'] for i in job[k]) for k in ['training', 'validation', 'C', 'predict']]
        assert all(not scopes[a] & scopes[b] for a in range(4) for b in range(a))
        assert set(job['training']) | set(job['validation']) == set(job['G'])
        assert all(set(rows[i]['failure'] for i in job[k]) == {0, 1} for k in ['training', 'validation', 'C', 'predict'])


@pytest.mark.parametrize('early_exception', [False, True])
def test_loader_epochs_exhaustion_and_early_exception_cleanup(early_exception):
    folder = fresh_folder()
    loader = EpochLoader(range(8), folder, 'synthetic', workers=2, mapped=SyntheticActions(), pin_memory=False)
    try:
        for epoch in range(1, 3):
            order = epoch_order(range(8), 42, epoch)
            loader.set_order(order)
            iterator = iter(loader)
            if early_exception:
                next(iterator)
                raise RuntimeError('simulated checkpoint interruption')
            assert [int(row[3]) for row in iterator] == order.tolist()
    except RuntimeError as exc:
        assert early_exception and str(exc) == 'simulated checkpoint interruption'
    finally:
        loader.close()
    records = list((folder / '26102026_checks').glob('*.json'))
    assert len(records) == 1
    assert read(records[0])['worker_exitcodes'] == [0, 0]


def test_completed_epoch_resume_matches_uninterrupted_optimizer_scheduler_rng():
    folder = fresh_folder()
    torch.manual_seed(42)
    model = nn.Sequential(nn.Linear(4, 5), nn.Dropout(.1), nn.Linear(5, 1))
    optimizer = torch.optim.AdamW(model.parameters(), lr=.001)
    scheduler = make_scheduler(optimizer)
    x = torch.arange(32, dtype=torch.float32).reshape(8, 4) / 10
    y = torch.arange(8).float() % 2

    def epoch(m, opt, sched, number):
        for index in epoch_order(range(8), 42, number):
            opt.zero_grad(set_to_none=True)
            loss = nn.functional.binary_cross_entropy_with_logits(m(x[index:index+1]).squeeze(1), y[index:index+1])
            loss.backward()
            opt.step()
        sched.step()

    epoch(model, optimizer, scheduler, 1)
    recovery = EpochRecovery(folder, 'synthetic-v1')
    recovery.save({'model': model.state_dict(), 'optimizer': optimizer.state_dict(), 'scheduler': scheduler.state_dict(), 'completed_epoch': 1})
    epoch(model, optimizer, scheduler, 2)
    expected = {n: v.clone() for n, v in model.state_dict().items()}
    expected_optimizer = optimizer.state_dict()
    expected_rng = torch.get_rng_state()
    saved = recovery.load()
    model.load_state_dict(saved['model'])
    optimizer = torch.optim.AdamW(model.parameters(), lr=.001)
    scheduler = make_scheduler(optimizer)
    optimizer.load_state_dict(saved['optimizer'])
    scheduler.load_state_dict(saved['scheduler'])
    restore_rng(saved['random'])
    epoch(model, optimizer, scheduler, saved['completed_epoch'] + 1)
    assert tensor_equal_tree(expected, model.state_dict())
    assert tensor_equal_tree(expected_optimizer, optimizer.state_dict())
    assert torch.equal(expected_rng, torch.get_rng_state())


def test_checkpoint_tampering_is_detected():
    folder = fresh_folder()
    recovery = EpochRecovery(folder, 'synthetic-v1')
    recovery.save({'completed_epoch': 1, 'value': torch.ones(1)})
    pointer = read(recovery.pointer)
    with (folder / pointer['slot']).open('ab') as stream:
        stream.write(b'not a valid checkpoint append')
    with pytest.raises(AssertionError, match='CHECKPOINT_INTEGRITY_FAILURE'):
        recovery.load()


def test_protocol_minimum_and_validation_selection_are_distinct():
    assert not stop_after_epoch(24, 1)
    assert stop_after_epoch(25, 1)
    assert not stop_after_epoch(25, 24)
    assert stop_after_epoch(50, 49)
    assert better({'epoch': 5, 'validation_AP': .4, 'validation_loss': .3}, {'epoch': 25, 'validation_AP': .3, 'validation_loss': .2})


def test_metrics_and_prediction_key_integrity():
    value = metrics([0, 1, 0, 1], [.1, .8, .2, .9])
    assert value['AP'] == value['AUROC'] == 1 and value['prevalence'] == .5
    with pytest.raises(AssertionError, match='PREDICTION_ALIGNMENT_FAILURE'):
        aligned_keys([{'sample_id': 'one'}, {'sample_id': 'one'}], ['one', 'two'])


def test_selected_checkpoint_rollback_after_uncommitted_replacement():
    from phase_checkpoint import atomic_torch_save, selected_payloads, restore_selections
    folder = fresh_folder()
    path = folder / 'PHASE1_BEST_MODEL.pt'
    original = {'model': {'weight': torch.tensor([1.0])}, 'selected_epoch': 1}
    atomic_torch_save(path, original)
    recovery = EpochRecovery(folder, 'selection-transaction-v1')
    recovery.save({'completed_epoch': 1, 'selected_payloads': selected_payloads(folder, {'epoch': 1}, None)})
    atomic_torch_save(path, {'model': {'weight': torch.tensor([9.0])}, 'selected_epoch': 2})
    restore_selections(folder, recovery.load())
    assert tensor_equal_tree(torch.load(path, weights_only=True), original)


def test_oof_lineage_rejects_checkpoint_selection_and_calibration_leakage():
    from phase_evaluation import assert_oof_lineage
    cohort = [{'sample_id': str(i), 'recording_id': f'recording{i}'} for i in range(5)]
    job = {'training': [0], 'validation': [1], 'G': [0, 1], 'C': [2], 'predict': [3, 4]}
    assert_oof_lineage(job, cohort[3:], cohort)
    for scope in ['training', 'validation', 'G', 'C']:
        leaking = dict(job, **{scope: [3]})
        with pytest.raises(AssertionError, match='OOF_BRANCH_LEAKAGE'):
            assert_oof_lineage(leaking, cohort[3:], cohort)


def test_f2_uses_calibrated_probability_columns_and_consistent_ap():
    from phase_model import stacker, fused
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import average_precision_score
    x = np.array([[.1, .2], [.4, .3], [.8, .6], [.7, .9], [.2, .8], [.6, .1]])
    y = np.array([0, 0, 1, 1, 0, 1])
    p = fused(x, stacker(x, y))
    reference = LogisticRegression(C=1, max_iter=1000, solver='lbfgs').fit(x, y).predict_proba(x)[:, 1]
    assert np.allclose(p, reference, atol=1e-6)
    assert metrics(y, p)['AP'] == average_precision_score(y, reference)


def test_actual_f2_fold_is_invariant_to_outer_assessment_labels(monkeypatch):
    import phase_evaluation as evaluation
    cohort = [{'sample_id': str(i), 'recording_id': f'r{i}', 'segment_id': '1', 'failure': i % 2}
              for i in range(10)]
    jobs = []
    for inner in range(4):
        held = [2*inner, 2*inner+1]
        remaining = [i for i in range(8) if i not in held]
        jobs.append({'outer_fold_original': 0, 'role': f'inner_{inner}', 'predict': held,
                     'training': remaining[:4], 'validation': remaining[4:5],
                     'G': remaining[:5], 'C': remaining[5:]})
    jobs.append({'outer_fold_original': 0, 'role': 'outer_assessment', 'predict': [8, 9],
                 'training': [0, 1, 2, 3, 4], 'validation': [5], 'G': list(range(6)),
                 'C': [6, 7], 'A_recordings': [f'r{i}' for i in range(8)]})
    original_read = evaluation.read

    def inputs(path):
        if Path(path).name == 'PHASE1_FIT_PLAN.json':
            return jobs
        if Path(path).name == 'PHASE1_INPUT_IDENTITY_MANIFEST.json':
            return cohort
        return original_read(path)

    def visual(job, seed, arm, short=False):
        return [dict(cohort[i], p_visual=.2 + .55*(i % 2) + .01*i) for i in job['predict']]

    def sensor(job):
        return [dict(cohort[i], p_sensor=.3 + .2*(i % 2) + .01*i) for i in job['predict']]

    monkeypatch.setattr(evaluation, 'read', inputs)
    monkeypatch.setattr(evaluation, 'visual', visual)
    monkeypatch.setattr(evaluation, 'sensor', sensor)
    root = fresh_folder()
    monkeypatch.setattr(evaluation, 'EXEC', root/'26102026_original_outer_labels')
    before = evaluation.evaluate_fold(42, 0, 'B_long_frozen16')
    model_before = next((root/'26102026_original_outer_labels').rglob('PHASE1_F2_MODEL.json'))
    coefficients_before = original_read(model_before)['model']
    for row in cohort[8:]:
        row['failure'] = 1-row['failure']
    monkeypatch.setattr(evaluation, 'EXEC', root/'26102026_changed_outer_labels')
    after = evaluation.evaluate_fold(42, 0, 'B_long_frozen16')
    model_after = next((root/'26102026_changed_outer_labels').rglob('PHASE1_F2_MODEL.json'))
    assert coefficients_before == original_read(model_after)['model']
    assert [r['p_fused'] for r in before] == [r['p_fused'] for r in after]
    assert [r['failure'] for r in before] != [r['failure'] for r in after]
