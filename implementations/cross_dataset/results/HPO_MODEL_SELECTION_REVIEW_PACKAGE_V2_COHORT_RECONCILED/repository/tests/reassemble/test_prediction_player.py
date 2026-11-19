"""Synthetic guard tests only: no raw dataset, model assets, or research writes."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

SPEC = importlib.util.spec_from_file_location(
    'prediction_player', Path(__file__).resolve().parents[2] / 'tutorials/EDA/reassemble_prediction_player.py')
player = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(player)


def test_native_clock_holds_latest_frame_and_never_selects_outside_segment():
    sample = dict(start=100., duration=2., clock=np.array([99., 100.2, 100.7, 101.8, 103.]), indices=np.array([1, 2, 3]))
    assert [player.frame_at(sample, t) for t in [0., .5, .9, 2.]] == [1, 1, 2, 3]
    assert not player.results_visible(sample, 1.999, False)
    assert player.results_visible(sample, 2., False)
    assert player.results_visible(sample, 0., True)


def test_decision_uses_retained_threshold_not_half():
    player.validate_scores(np.array([.2, .05]), np.array([1, 0]), np.array([0, 1]), .14, 2)
    with pytest.raises(ValueError, match='threshold mismatch'):
        player.validate_scores(np.array([.2, .05]), np.array([0, 0]), np.array([0, 1]), .14, 2)


@pytest.mark.parametrize('p', [np.array([np.nan]), np.array([1.01]), np.array([-.01])])
def test_bad_probabilities_are_rejected_not_clamped(p):
    with pytest.raises(ValueError, match='Invalid P'):
        player.validate_scores(p, np.array([0]), np.array([0]), .1, 1)


def test_missing_bank_disables_result_without_loading_other_sample():
    evidence = object.__new__(player.Evidence)
    evidence.base_error = None
    evidence.fold = np.array([0])
    evidence.m1 = Path('synthetic-unused-manifest')
    def missing(*args):
        raise FileNotFoundError('synthetic missing prediction bank')
    evidence.bank = missing
    result = evidence.prediction(0, 'visual', 'F2')
    assert not result['available']
    assert 'missing prediction bank' in result['reason']
    assert 'probability' not in result


def test_unverified_row_contract_disables_predictions_before_bank_access():
    evidence = object.__new__(player.Evidence)
    evidence.base_error = 'synthetic frozen cohort order mismatch'
    result = evidence.prediction(0, 'fusion', 'F2')
    assert not result['available']
    assert 'cohort order mismatch' in result['reason']


def test_equal_length_is_insufficient_when_labels_or_folds_differ():
    evidence = object.__new__(player.Evidence)
    evidence.frame = pd.DataFrame({'failure': [0, 1]})
    evidence.fold = np.array([0, 1])
    with pytest.raises(ValueError, match='labels/order'):
        evidence.check_global({'y': np.array([1, 0]), 'fold': np.array([0, 1])})
    with pytest.raises(ValueError, match='folds/order'):
        evidence.check_global({'y': np.array([0, 1]), 'fold': np.array([1, 0])})


def test_manual_selection_uses_both_ids():
    evidence = SimpleNamespace(frame=pd.DataFrame({'recording_id': ['a', 'b'], 'segment_id': ['2', '2']}))
    args = SimpleNamespace(recording_id='b', segment_id='2')
    assert player.choose_samples(evidence, args)[0] == [1]
    args.recording_id = 'missing'
    with pytest.raises(ValueError, match='Unknown'):
        player.choose_samples(evidence, args)
