"""Final independent metric, model, ID and evidence-integrity gate."""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import ast
import csv
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
from scipy.special import expit
from PIL import Image

from common import ROOT, REPO, RUN, CONFIG, read, write, sha, relative, identity, utc, cohort, job, status
from evaluate import independent_metrics, NAMES

REQUIRED = ['EXPERIMENT_OVERVIEW.md', 'ARCHITECTURE_VERIFICATION.md',
            'DATA_SPLIT_AND_LEAKAGE_AUDIT.md', 'MODEL_COMPARISON_RESULTS.md',
            'PAIRED_STATISTICAL_COMPARISON.md', 'FUSION_COEFFICIENT_ANALYSIS.md',
            'REPRODUCIBILITY_REPORT.md', 'FINAL_SCIENTIFIC_CONCLUSION.md']


def main():
    sources = read(RUN/'manifests/INPUT_IDENTITIES.json')
    for source in sources:
        path = REPO/source['path']
        assert path.stat().st_size == source['bytes'] and sha(path) == source['sha256'], ('ORIGINAL_EVIDENCE_DRIFT', source['path'])
    for source in read(RUN/'manifests/CANONICAL_INPUT_IDENTITIES.json'):
        assert sha(REPO/source['path']) == source['sha256']
    verification = read(ROOT/'02_checkpoint_verification/VERIFICATION.json')
    assert verification['passed'] and verification['protocol_sha256'] == read(CONFIG)['upstream_visual_verification_protocol_sha256']
    controls = read(ROOT/'02_checkpoint_verification/FULL_CNN_CPU_FORWARD_PARITY_ACTIVE.json')
    assert controls['passed'] and sha(REPO/controls['path']) == controls['sha256']
    assert read(REPO/controls['path'])['passed']
    sensor_features = read(ROOT/'03_static_sensor_evidence/ORIGINAL_FEATURE_PARITY.json')
    assert sensor_features['passed'] and sensor_features['cached_statistics_match_original_exactly']
    assert sensor_features['rows'] == 4530 and sensor_features['original_recording_blocks'] == 148
    for source in sensor_features['sources']:
        assert sha(REPO/source['metadata_path']) == source['metadata_sha256']
    replay = read(ROOT/'03_static_sensor_evidence/ORIGINAL_SENSOR_FIT_REPLAY.json')
    assert replay['passed']
    for fit in replay['receipts']:
        for key in ['source_model', 'source_predictions']:
            assert sha(REPO/fit[key]['path']) == fit[key]['sha256']
    gradient = read(ROOT/'02_checkpoint_verification/ORIGINAL_FULL_CNN_GRADIENT_EVIDENCE.json')
    assert gradient['passed'] and sha(REPO/gradient['source']['path']) == gradient['source']['sha256']
    native = read(ROOT/'02_checkpoint_verification/ORIGINAL_COHORT_LABEL_ID_PARITY.json')
    assert native['passed'] and native['actions'] == 4530
    assert sha(REPO/native['original_cohort']['path']) == native['original_cohort']['sha256']
    assert sha(REPO/native['role_manifest']['path']) == native['role_manifest']['sha256']
    inference = read(ROOT/'04_training_side_predictions/INFERENCE_RECEIPT.json')
    assert inference['new_CNN_fits'] == 0 and inference['CPU_only'] and inference['actions_per_arm'] == 920
    assert inference['protocol_sha256'] in {sha(CONFIG), read(CONFIG)['upstream_visual_verification_protocol_sha256']}
    for key, name in [('frozen_sha256', 'FROZEN100_HELDOUT.json'), ('finetuned_sha256', 'FINETUNED100_HELDOUT.json')]:
        assert sha(ROOT/'04_training_side_predictions'/name) == inference[key]
    lock = read(ROOT/'05_fusion_models/FUSION_FIT_LOCK.json')
    assert lock['locked_before_new_outer_metrics'] and lock['protocol_identity']['sha256'] == sha(CONFIG)
    assert not lock['new_outer_model_metrics_seen_before_this_receipt']
    assert sha(REPO/lock['evaluation_source_identity']['path']) == lock['evaluation_source_identity']['sha256']
    models = {}
    for arm, receipt in lock['models'].items():
        assert sha(REPO/receipt['path']) == receipt['sha256']
        models[arm] = read(REPO/receipt['path'])
        assert not models[arm]['outer_test_labels_used'] and not models[arm]['outer_test_probabilities_used']
    saved = read(ROOT/'06_held_out_predictions/ALL_MODELS_IDENTICAL_OUTER_IDS.json')
    train = read(ROOT/'04_training_side_predictions/EXACT_F2_INPUT_PROBABILITIES.json')
    rows, selected = cohort(), job()
    assert len(saved) == len({r['sample_id'] for r in saved}) == 753
    assert [r['sample_id'] for r in saved] == [rows[i]['sample_id'] for i in selected['predict']]
    assert len(train) == len({r['sample_id'] for r in train}) == 920
    assert not {r['recording_id'] for r in saved} & {r['recording_id'] for r in train}
    assert not {r['sample_id'] for r in saved} & {r['sample_id'] for r in train}
    for role in ['training', 'validation', 'C']:
        assert not {r['recording_id'] for r in train} & {rows[i]['recording_id'] for i in selected[role]}
    canonical = read(ROOT/'03_static_sensor_evidence/CANONICAL_SENSOR_VERIFICATION.json')
    assert canonical['passed']
    for fit in canonical['recipes']:
        for key in ['model', 'predictions', 'original_source']:
            assert sha(REPO/fit[key]['path']) == fit[key]['sha256']
    sensor_test = read(ROOT/'03_static_sensor_evidence/CANONICAL_OUTER_TEST_PREDICTIONS.json')['data']
    assert [r['p_sensor'] for r in sensor_test] == [r['M3_sensor'] for r in saved]
    for arm, visual, fused in [('frozen', 'M1_frozen100', 'M4_F2_frozen'),
                              ('finetuned', 'M2_finetuned100', 'M5_F2_finetuned')]:
        model = models[arm]['model']
        p = expit(np.array([[r[visual], r['M3_sensor']] for r in saved])@np.array(model['coefficient'])+model['intercept'])
        assert np.max(abs(p-np.array([r[fused] for r in saved]))) < 1e-12
    assert np.allclose([r['M6_average_frozen'] for r in saved], [(r['M1_frozen100']+r['M3_sensor'])/2 for r in saved], rtol=0, atol=1e-15)
    assert np.allclose([r['M7_average_finetuned'] for r in saved], [(r['M2_finetuned100']+r['M3_sensor'])/2 for r in saved], rtol=0, atol=1e-15)
    y = np.array([r['failure'] for r in saved])
    assert y.sum() == 77 and len({r['recording_id'] for r in saved}) == 26
    scores = read(ROOT/'07_evaluation_results/ALL_MODEL_METRICS.json')
    for name in NAMES:
        actual = independent_metrics(y, [r[name] for r in saved])
        assert max(abs(value-scores[name][key]) for key, value in actual.items()) < 1e-12
    native_scores = read(ROOT/'07_evaluation_results/ORIGINAL_NATIVE_THRESHOLD_METRICS.json')
    for name in NAMES:
        actual = independent_metrics(y, [r[name] for r in saved], native_scores[name]['threshold'])
        assert max(abs(value-native_scores[name][key]) for key,value in actual.items()) < 1e-12
    assert native_scores['M4_F2_frozen']['threshold'] == models['frozen']['threshold']
    assert native_scores['M5_F2_finetuned']['threshold'] == models['finetuned']['threshold']
    paired = read(ROOT/'07_evaluation_results/PAIRED_RECORDING_BOOTSTRAP.json')
    draws = read(ROOT/'07_evaluation_results/BOOTSTRAP_METRIC_DRAWS.json')
    for value in paired['differences'].values():
        for metric in ['AP', 'AUROC']:
            x = np.array(draws[value['treatment']][metric])-np.array(draws[value['control']][metric])
            lo, hi = np.quantile(x, [.025, .975])
            assert abs(lo-value[metric]['lower95']) < 1e-12 and abs(hi-value[metric]['upper95']) < 1e-12
    assert all((ROOT/'10_final_research_report'/name).is_file() for name in REQUIRED)
    assert read(ROOT/'07_evaluation_results/HISTORICAL_COMPARABILITY.json')['directly_controlled_comparison'] is False
    figures = read(ROOT/'07_evaluation_results/FIGURE_SOURCE_MANIFEST.json')
    for figure in figures:
        assert sha(REPO/figure['path']) == figure['sha256']
        with Image.open(REPO/figure['path']) as image:image.verify()
        for source in figure['sources']:assert sha(REPO/source['path']) == source['sha256']
    examples = read(ROOT/'08_visual_diagnostics/HELDOUT_DISAGREEMENT_EXAMPLES.json')
    for example in examples:
        assert example['sample_id'] in {r['sample_id'] for r in saved}
        assert len(example['frame_receipts']) == 16
        assert len({r['frame_index'] for r in example['frame_receipts']}) == 16
        for frame in example['frame_receipts']:
            assert sha(REPO/frame['path']) == frame['sha256']
            with Image.open(REPO/frame['path']) as image:image.verify()
        assert sha(REPO/example['contact_sheet']) == example['contact_sheet_sha256']
    for path in (ROOT/'src').glob('*.py'):
        ast.parse(path.read_text(), filename=str(path))
    checks = {}
    commands = [(['git', 'diff', '--check'], 'git_diff_check'),
                ([str(REPO/'ma_thesis_env/bin/python'), '-B', '-m', 'pip', 'check'], 'pip_check'),
                ([str(REPO/'ma_thesis_env/bin/python'), '-B', '-m', 'pytest', '-q', '-p', 'no:cacheprovider', str(ROOT/'tests')], 'regression_tests')]
    for command, label in commands:
        process = subprocess.run(command, cwd=REPO, text=True, capture_output=True)
        assert process.returncode == 0, (label, process.stdout, process.stderr)
        checks[label] = process.stdout.strip() or 'PASS'
    subprocess.run(['git', 'status', '--short', '--branch', '--untracked-files=all'], cwd=REPO, text=True, capture_output=True, check=True)
    receipt = {'utc': utc(), 'passed': True, 'required_reports': len(REQUIRED), 'controlled_models': 7,
               'separate_historical_reference': True, 'all_original_input_hashes_unchanged': len(sources),
               'same753_unique_test_ids': True, 'same_sensor_test_probabilities_across_F2_arms': True,
               'training_test_recording_overlap': 0, 'strict_checkpoint_loading_and_calibration_checks_passed': True,
               'full_CPU_forward_controls_verified': True, 'independent_metric_tolerance': 1e-12,
               'all4530_static_feature_rows_match_original148_recording_blocks': True,
               'original_sensor_fits_replayed_without_replacing_models': True,
               'saved_original_all_CNN_scope_gradient_evidence_verified': True,
               'paired_bootstrap_intervals_reproduced_from_saved_draws': True,
               'source_backed_figures_verified': len(figures), 'real_diagnostic_examples_verified': len(examples),
               'checks': checks, 'new_CNN_fits': 0, 'training_GPUTask_interrupted': False,
               'scientific_limitations': ['one previously inspected test fold and seed', 'selected original fit3',
                 'one genuine base-model holdout bank; not complete4-fold nested100-epoch OOF',
                 'conditional group-bootstrap intervals; no independent confirmation', 'sparse-bin ECE descriptive only']}
    write(RUN/'validation.json', receipt)
    write(ROOT/'09_reproducibility/FINAL_VALIDATION.json', receipt)
    status('COMPLETE', completed_utc=utc(), models_evaluated=7, required_reports=8,
           original_CNNs_and_sensor_models_reused=True, new_CNN_fits=0, independent_verification_passed=True,
           inference_device='CPU; existing GPU study untouched', complete_nested100_epoch_OOF_reproduction=False)
    output = RUN/'manifests/OUTPUT_MANIFEST.json'
    payload = []
    for path in sorted(ROOT.rglob('*')):
        if path.is_file() and path != output and not path.name.endswith('.writing'):
            payload.append(identity(path))
    write(output, {'created_utc': utc(), 'files': payload, 'total_bytes': sum(p['bytes'] for p in payload),
                   'self_excluded': True, 'raw_datasets_and_original_large_checkpoints_not_duplicated': True})
    print('FINAL_VALIDATION_PASSED', len(payload), 'files', flush=True)


if __name__ == '__main__':main()
