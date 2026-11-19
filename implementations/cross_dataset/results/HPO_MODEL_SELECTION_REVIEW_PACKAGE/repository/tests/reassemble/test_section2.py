import json
import numpy as np
import pandas as pd
import pytest
import torch
from reassemble.section2_models import DecisionGate, context, logit, fit_head
from reassemble.section2_data import quality_features
from reassemble.section1b import guard_partition


def test_context_cannot_bypass_weights():
    torch.manual_seed(3)
    gate = DecisionGate(6, 8)
    logits = torch.full((12, 2), .7)
    a, w = gate(torch.randn(12, 6), logits, torch.ones(12, 2))
    b, other = gate(torch.randn(12, 6) * 100, logits, torch.ones(12, 2))
    assert torch.allclose(a, b, atol=1e-6)
    assert torch.allclose(a, torch.full((12,), .7), atol=1e-6)
    assert not torch.allclose(w, other)


def test_mask_handles_unavailable_nan_and_rejects_all_missing():
    gate = DecisionGate(6, 8)
    logits = torch.tensor([[.3, float('nan')], [float('nan'), -.8]])
    mask = torch.tensor([[1., 0.], [0., 1.]])
    value, weights = gate(torch.zeros(2, 6), logits, mask)
    assert torch.allclose(value, torch.tensor([.3, -.8]))
    assert torch.equal(weights, mask)
    with pytest.raises(ValueError):
        gate(torch.zeros(2, 6), logits, torch.zeros(2, 2))


def test_weighted_logit_is_convex():
    gate = DecisionGate(6, 8)
    logits = torch.randn(20, 2)
    value, weights = gate(torch.randn(20, 6), logits, torch.ones(20, 2))
    assert torch.all(value >= logits.min(1).values - 1e-6)
    assert torch.all(value <= logits.max(1).values + 1e-6)
    assert torch.allclose(weights.sum(1), torch.ones(20))


def test_quality_gate_excludes_action():
    a = np.eye(4, dtype='float32'); q = np.arange(12).reshape(4, 3); mask = np.ones((4, 2))
    assert np.array_equal(context('F5', a, q, mask), context('F5', a[::-1], q, mask))
    assert not np.array_equal(context('F4', a, q, mask), context('F4', a[::-1], q, mask))
    assert np.isfinite(logit(np.array([0., 1.]))).all()


def test_restricted_subfolds_exclude_inner_assessment():
    frame = pd.DataFrame({'recording_id': np.repeat(np.arange(10), 2)})
    train = np.arange(16); assessment = np.arange(16, 20)
    original = [(np.setdiff1d(train, v), v) for v in np.array_split(train, 4)]
    guard_partition(frame, train, assessment, original)
    for i, (tr, va) in enumerate(original):
        restricted = [(np.intersect1d(a, tr), b) for j, (a, b) in enumerate(original) if i != j]
        guard_partition(frame, tr, va, restricted)
        assert all(not set(assessment) & (set(a) | set(b)) for a, b in restricted)


def test_quality_loader_explicit_fields_only(tmp_path):
    folder = tmp_path / 'records'; folder.mkdir()
    record = {'segments': [{'segment_id': 's', 'failure': 1, 'video': {'hand': {'focus_proxy': .2}}, 'sensor': {'force': {'finite_fraction': .9}}}, {'segment_id': 'unused'}]}
    (folder / 'r.json').write_text(json.dumps(record))
    frame = pd.DataFrame({'recording_id': ['r'], 'segment_id': ['s']})
    config = {'quality_visual': ['focus_proxy'], 'quality_sensor': ['finite_fraction']}
    base = {'audit_run': str(tmp_path), 'sensor': {'channels': ['force']}}
    q, names, _ = quality_features(frame, base, config)
    assert np.allclose(q, [[.2, .9]]) and len(names) == 2
    record['segments'][0]['failure'] = 0
    (folder / 'r.json').write_text(json.dumps(record))
    assert np.array_equal(q, quality_features(frame, base, config)[0])


@pytest.mark.skipif(not torch.cuda.is_available(), reason='research GPU required')
def test_neural_normalizers_ignore_assessment_values():
    rng = np.random.default_rng(9)
    train = {'visual': rng.normal(size=(12, 128)).astype('float32'), 'statistics': rng.normal(size=(12, 5)).astype('float32'), 'quality': rng.normal(size=(12, 3)).astype('float32'), 'probabilities': rng.uniform(.1, .9, size=(12, 2)), 'action': np.eye(4)[np.arange(12) % 4], 'availability': np.ones((12, 2))}
    test = {k: v[:4].copy() for k, v in train.items()}; poison = {k: v.copy() for k, v in test.items()}; poison['quality'][:] = 1e6
    config = {'dropout': .1, 'probability_clip': 1e-6, 'batch_size': 8}
    settings = {'hidden': 8, 'lr': .001, 'epochs': 1, 'weight_decay': .001}; labels = np.arange(12) % 2
    _, first = fit_head('F6', train, test, labels, settings, config, 7)
    _, second = fit_head('F6', train, poison, labels, settings, config, 7)
    assert first['normalizers'] == second['normalizers']
    assert first['loss_by_epoch'] == second['loss_by_epoch']
    output, _ = fit_head('F3', train, test, labels, settings, config, 7)
    assert output['raw'].shape == (4,) and np.isfinite(output['raw']).all()


def test_full_assessment_and_a_to_v_handoff(tmp_path, monkeypatch):
    from reassemble.section2_report import assess, MODELS, ABLATIONS
    from reassemble.section1_report import metrics, METRICS
    from reassemble import section2
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(section2, 'progress', lambda *args: None)
    for path in ['run/predictions', 'old/assessment', 'artifacts/reassemble/reports']:
        (tmp_path / path).mkdir(parents=True)
    rng = np.random.default_rng(11); y = np.arange(100) % 3 == 0; fold = np.arange(100) % 5
    predictions = {'y': y.astype(int), 'fold': fold}
    for i, m in enumerate(MODELS):
        p = np.clip(.2 + .5 * y + rng.normal(0, .25, len(y)), .01, .99)
        predictions[m+'_p'] = p; predictions[m+'_hard'] = (p >= .5).astype(int)
        if m in ['F3', 'F4', 'F5', 'F6']:
            predictions[m+'_seed_p'] = np.stack([p, p, p])
        if m in ABLATIONS:
            predictions[m+'_weights'] = np.tile([.3, .7], (len(y), 1))
            predictions[m+'_seed_weights'] = np.tile([.3, .7], (3, len(y), 1))
            for a in ABLATIONS[m]:
                predictions[m+'_'+a+'_p'] = p.copy()
                predictions[m+'_'+a+'_weights'] = predictions[m+'_weights'].copy()
    np.savez('run/predictions/oof.npz', **predictions)
    original = dict(zip(METRICS, metrics(y, predictions['F2_p'], predictions['F2_hard'])))
    (tmp_path/'old/assessment/results.json').write_text(json.dumps({'metrics': {'minimal_late_fusion': {k: {'estimate': v} for k, v in original.items()}}}))
    for k in range(5):
        detail = {'fold': k, 'models': {m: {'selected_config': 0, 'settings': {}, 'inner_AP': [[.4]*4], 'threshold': .5, 'inner_training_seconds': 1, 'final_fits': [{'parameters': 50, 'training_seconds': 1, 'inference_batch_seconds': .01, 'inference_batch_rows': 20}]*3} for m in ['F3','F4','F5','F6']}}
        (tmp_path/f'run/predictions/outer{k}.json').write_text(json.dumps(detail))
    (tmp_path/'run/implementation.json').write_text(json.dumps({'constant_quality_fields': [], 'device': 'synthetic', 'git_commit': 'fixture', 'split_sha256': 'fixture'}))
    config = {'run_dir': 'run', 'section1b_run': 'old', 'seed': 11, 'seeds': [1,2,3], 'bootstrap_replicates': 20, 'actions': ['pick','insert','remove','place'], 'concat_configs': [], 'gate_configs': []}
    frame = pd.DataFrame({'recording_id': np.repeat(np.arange(20).astype(str),5), 'action': np.array(config['actions'])[np.arange(100)%4]})
    assess(config, frame)
    text = (tmp_path/'artifacts/reassemble/reports/SECTION_2_FUSION_HANDOFF.md').read_text()
    assert all('## '+letter+'. ' in text for letter in 'ABCDEFGHIJKLMNOPQRSTUV')
    assert 'NOT YET ANSWERED' in text
    result = json.loads((tmp_path/'run/assessment/results.json').read_text())
    assert result['F2_exact_metric_reuse']
    assert len(result['paired']) == 9
