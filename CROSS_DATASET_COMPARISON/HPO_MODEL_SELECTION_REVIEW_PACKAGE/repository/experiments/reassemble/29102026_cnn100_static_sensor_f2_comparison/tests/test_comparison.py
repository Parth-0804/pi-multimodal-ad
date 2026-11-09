"""Meaningful guards for tied metrics, keyed joins, fitting roles and F2 math."""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
from pathlib import Path
import sys

import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from common import ROOT, REPO, CONFIG, read
from evaluate import align, metrics, independent_metrics


def test_keyed_join_accepts_reordering_but_not_duplicate_or_missing_ids():
    bank = [{'sample_id': 'b'}, {'sample_id': 'a'}]
    assert [r['sample_id'] for r in align(bank, ['a', 'b'])] == ['a', 'b']
    with pytest.raises(AssertionError, match='DUPLICATE'):
        align([{'sample_id': 'a'}, {'sample_id': 'a'}], ['a', 'b'])
    with pytest.raises(AssertionError, match='SET_MISMATCH'):
        align(bank, ['a', 'c'])


@pytest.mark.parametrize('p', [np.array([.1, .1, .8, .8, .8, .9]),
                              np.array([0., 1., .5, .5, .2, .6]),
                              np.repeat(.1, 6)])
def test_independent_metric_implementation_handles_ties_and_boundaries(p):
    y = np.array([0, 1, 0, 1, 1, 0])
    standard = metrics(y, p)
    separate = independent_metrics(y, p)
    assert max(abs(standard[k]-v) for k, v in separate.items()) < 1e-12


def test_protocol_uses_original_full_outer_sensor_baseline_and_holdout_inputs():
    config = read(CONFIG)
    assert config['sensor_test_fit_role'] == 'original_section1b_outer_refit'
    assert config['sensor_fitting_bank_role'] == 'original_section1b_outer0_inner2'
    assert config['sensor_training_sizes'] == {'F2_bank_fit': 2857, 'F2_bank_OOF_calibration': 2857,
                                               'test_fit': 3777, 'test_OOF_calibration': 3777}
    assert config['sensor_selected_C'] == {'F2_fitting_bank': .1, 'outer_test': 1.}
    assert not set(config['training_bank_indices']) & set(config['outer_test_indices'])
    assert config['frames'] == 16 and config['primary_threshold'] == .5
    assert config['locked_before_new_fusion_test_metrics']


def test_original_unconstrained_F2_matches_logistic_on_probabilities():
    from original_api import load
    original, _ = load()
    # Deliberately anticorrelated visual probabilities; negative coefficients
    # are legitimate under original F2 and must not be silently constrained.
    x = np.array([[.9, .1], [.8, .2], [.7, .3], [.3, .7], [.2, .8], [.1, .9]])
    y = np.array([0, 0, 0, 1, 1, 1])
    model = original.stacker(x, y)
    reference = LogisticRegression(C=1, class_weight=None, max_iter=2000, random_state=42).fit(x, y)
    assert model['coefficient'][0] < 0 and model['coefficient'][1] > 0
    assert np.allclose(original.fused(x, model), reference.predict_proba(x)[:, 1], atol=1e-12, rtol=0)


def test_fusion_bank_loader_never_opens_outer_labels_or_predictions(monkeypatch):
    import evaluate
    ids = ['sampleA', 'sampleB']
    roles = {'original_inner_prediction_indices': {'sample_ids': ids, 'recording_ids': ['groupA', 'groupB']},
             **{k: {'recording_ids': [k+'OtherGroup']} for k in ['training', 'validation', 'C', 'predict']}}
    base = [{'sample_id': i, 'recording_id': g, 'segment_id': '1', 'failure': y,
             'p_visual': p, 'p_sensor': q} for i,g,y,p,q in
            [('sampleA', 'groupA', 0, .1, .2), ('sampleB', 'groupB', 1, .8, .7)]]
    opened = []
    def safe_read(path):
        name = Path(path).name;opened.append(name)
        if name == 'VERIFICATION.json':return {'roles': roles}
        if name in ['FROZEN100_HELDOUT.json', 'FINETUNED100_HELDOUT.json']:return base
        if name == 'CANONICAL_TRAINING_BANK_PREDICTIONS.json':return {'data': base}
        raise AssertionError('Unexpected access to data outside the fitting bank')
    monkeypatch.setattr(evaluate, 'read', safe_read)
    monkeypatch.setattr(evaluate, 'cohort', lambda: (_ for _ in ()).throw(AssertionError('Outer labels must not be read')))
    monkeypatch.setattr(evaluate, 'job', lambda: (_ for _ in ()).throw(AssertionError('Full split/cohort load must not be needed')))
    entries, labels, groups, probabilities = evaluate.fitting_bank()
    assert len(entries) == 2 and labels.tolist() == [0, 1]
    assert all('OUTER' not in name for name in opened)
    assert np.array_equal(probabilities['frozen'][:, 1], probabilities['finetuned'][:, 1])


def test_canonical_original_F2_preserves_threshold_selection_and_coefficients():
    sys.path.insert(0, str(REPO/'src'))
    from reassemble.section1b import fit_stacker
    x = np.array([[.05,.2],[.1,.3],[.2,.4],[.6,.7],[.7,.8],[.8,.9]])
    y = np.array([0,0,0,1,1,1])
    plan = [(np.array([0,1,3,4]),np.array([2,5])),(np.array([2,5]),np.array([0,1,3,4]))]
    settings = read(REPO/'configs/reassemble/section1b.json')['stacker']
    _,_,model = fit_stacker(x,y,np.arange(6),plan,np.array([[.5,.5]]),settings)
    separate = LogisticRegression(C=1,class_weight=None,max_iter=2000,random_state=0).fit(x,y)
    assert np.allclose(model['coefficient'],separate.coef_[0],atol=1e-12,rtol=0)
    assert abs(model['intercept']-separate.intercept_[0])<1e-12
    assert .01<=model['threshold']<=.99 and np.isfinite(model['meta_crossfit_Brier'])
