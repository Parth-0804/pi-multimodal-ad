"""CPU-only, exact16-frame held-out inference; no training or GPU context."""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['OMP_NUM_THREADS'] = '2'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '2'

import fcntl
import hashlib
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import torch

from common import ROOT, REPO, BASE, STUDY, EVIDENCE, RUN, CONFIG
from common import read, write, sha, relative, cohort, job, arm_folder, status, utc
from original_api import load


def runtime_path():
    stable = ROOT/'01_experiment_definition/CPU_RUNTIME_03.json'
    if stable.exists():
        return stable
    preferred = ROOT/'01_experiment_definition/CPU_RUNTIME_02.json'
    return preferred if preferred.exists() else ROOT/'01_experiment_definition/CPU_RUNTIME.json'


def cpu_threads():
    runtime = runtime_path()
    return read(runtime)['torch_threads'] if runtime.exists() else read(CONFIG)['torch_CPU_threads']


def main():
    assert read(ROOT/'02_checkpoint_verification/VERIFICATION.json')['passed']
    assert CONFIG.exists()
    lock = (RUN/'CPU_INFERENCE.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    fusion, models = load()
    torch.set_num_threads(cpu_threads())
    assert not torch.cuda.is_available(), 'This task must not contend with main GPU study'
    rows, selected = cohort(), job()
    indices = selected['original_inner_prediction_indices']
    expected = [rows[i]['sample_id'] for i in indices]
    features = np.load(STUDY/'shared_cache/original_features_16.npy', allow_pickle=False)
    frozen_folder = arm_folder('frozen')
    frozen = models.make_model('B_frozen100', selected['training'], 42, device='cpu')
    state = torch.load(frozen_folder/'PHASE1_BEST_MODEL.pt', map_location='cpu', weights_only=True)
    assert sha(frozen_folder/'PHASE1_BEST_MODEL.pt') == read(frozen_folder/'PHASE1_FIT_COMPLETE.json')['selected_model_sha256']
    frozen.load_state_dict(state['model'], strict=True)
    frozen.eval()
    with torch.inference_mode():
        raw = frozen(torch.from_numpy(features[indices])).numpy().astype(float)
    cal = read(frozen_folder/'PHASE1_CALIBRATOR.json')['calibrator']
    p = fusion.calibrated(raw, cal)
    bank = [dict(sample_id=rows[i]['sample_id'], recording_id=rows[i]['recording_id'],
                 segment_id=rows[i]['segment_id'], failure=rows[i]['failure'],
                 raw_visual_logit=float(z), p_visual=float(q), checkpoint_identity=state['fit_identity'],
                 prediction_role='selected_inner_fold3_base_model_holdout')
            for i, z, q in zip(indices, raw, p)]
    write(ROOT/'04_training_side_predictions/FROZEN100_HELDOUT.json', bank)
    del frozen, state
    sensor_root = BASE/'26102026_execution/26102026_main_run_01'
    for role, name in [('training_bank', '26102026_sensor_outer1_inner_fold_03'),
                       ('outer_test', '26102026_sensor_outer1_outer_assessment')]:
        for source_name, suffix in [('PHASE1_SENSOR_MODEL.json', 'MODEL'), ('PHASE1_SENSOR_PREDICTIONS.json', 'PREDICTIONS')]:
            source = sensor_root/name/source_name
            data = read(source)
            write(ROOT/f'03_static_sensor_evidence/{role.upper()}_{suffix}.json',
                  {'source_path': relative(source), 'source_sha256': sha(source), 'data': data})
    full_folder = arm_folder('finetuned')
    assert sha(full_folder/'PHASE1_BEST_MODEL.pt') == read(full_folder/'PHASE1_FIT_COMPLETE.json')['selected_model_sha256']
    model = models.make_model('C_full_finetuned16', selected['training'], 42, device='cpu')
    state = torch.load(full_folder/'PHASE1_BEST_MODEL.pt', map_location='cpu', weights_only=True)
    model.load_state_dict(state['model'], strict=True)
    model.requires_grad_(False)
    model.eval()
    torch.set_num_threads(cpu_threads())
    sys.path.insert(0, str(REPO/'26.10.2026_feedback_experiments/source'))
    from isolated_decode import IsolatedDecoder
    original = read(STUDY/'config/resolved_config.json')
    decoder = IsolatedDecoder(REPO, original['weights_dir'], original['rescale_factor'], decoder_threads=1)
    backend = read(runtime_path()).get('backend', 'eager')
    if backend == 'torchscript_frozen_FP32':
        warm = rows[selected['C'][0]]
        pixels = decoder(dict(warm, frames32=warm['frames16']))
        assert hashlib.sha256(pixels.tobytes()).hexdigest() == warm['selected16_sha256']
        x = torch.from_numpy(pixels.astype('float32')*np.float32(1/255)).unsqueeze(0)
        start = time.monotonic()
        with torch.inference_mode(), warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            traced = torch.jit.trace(model, x, check_trace=False, strict=False)
            model = torch.jit.optimize_for_inference(torch.jit.freeze(traced.eval()))
        write(RUN/'manifests/ACTIVE_CPU_INFERENCE_COMPILER.json',
              {'backend': backend, 'compile_seconds': time.monotonic()-start,
               'shape_contract': '1 action,16 RGB frames,640x640', 'precision': 'float32',
               'operator_names': torch.jit.export_opnames(model),
               'source_checkpoint_sha256': sha(full_folder/'PHASE1_BEST_MODEL.pt'),
               'runtime_identity': {'path': relative(runtime_path()), 'sha256': sha(runtime_path())},
               'compiler_warning_types': sorted({type(w.message).__name__ for w in caught}),
               'checkpoint_parameters_learned_or_modified': False})

    def predict(index):
        row = rows[index]
        start = time.monotonic()
        pixels = decoder(dict(row, frames32=row['frames16']))
        digest = hashlib.sha256(pixels.tobytes()).hexdigest()
        assert digest == row['selected16_sha256'], ('PIXEL_DRIFT', row['sample_id'])
        assert pixels.shape == (16, 3, 640, 640) and len(set(row['frames16'])) == 16
        x = torch.from_numpy(pixels.astype('float32')*np.float32(1/255)).unsqueeze(0)
        with torch.inference_mode():
            logit = float(model(x)[0])
        assert np.isfinite(logit)
        return logit, time.monotonic()-start, digest

    # Verify numeric equivalence against saved GPU logits; no control label
    # enters fitting, calibration or any configurable choice.
    control_path = ROOT/f'02_checkpoint_verification/FULL_CNN_CPU_FORWARD_PARITY_THREADS{cpu_threads()}_{backend}.json'
    if not control_path.exists():
        outer = read(full_folder/'PHASE1_PREDICTIONS.json')
        calibrator = read(full_folder/'PHASE1_CALIBRATOR.json')
        targets = [(selected['predict'][k], outer[k]['raw_visual_logit'], 'saved_outer_logit') for k in [0, len(outer)//2, len(outer)-1]]
        targets += [(selected['C'][k], calibrator['raw_calibration_logits'][k], 'saved_calibration_logit') for k in [0, len(selected['C'])//2, len(selected['C'])-1]]
        controls = []
        for index, expected_logit, role in targets:
            actual, seconds, digest = predict(index)
            difference = abs(actual-expected_logit)
            assert difference <= 1e-3, ('CPU_GPU_NUMERIC_PARITY_FAILURE', difference)
            controls.append({'sample_id': rows[index]['sample_id'], 'role': role,
                             'expected_GPU_logit': expected_logit, 'CPU_logit': actual,
                             'absolute_difference': difference, 'seconds': seconds, 'pixels_sha256': digest})
            print('CONTROL', rows[index]['sample_id'], 'difference', difference, 'seconds', seconds, flush=True)
        write(control_path, {'passed': True, 'absolute_raw_logit_tolerance': 1e-3,
                            'GPU_vs_CPU_float32_backend_difference_only': True, 'controls': controls,
                            'full_state_loaded_strictly': True, 'GPU_allocations_by_this_process': 0})
    else:
        assert read(control_path)['passed']
    write(ROOT/'02_checkpoint_verification/FULL_CNN_CPU_FORWARD_PARITY_ACTIVE.json',
          {'path': relative(control_path), 'sha256': sha(control_path), 'CPU_threads': cpu_threads(), 'passed': True})
    cache = ROOT/'04_training_side_predictions/FINETUNED100_RAW_CPU.jsonl'
    completed = [json.loads(line) for line in cache.read_text().splitlines()] if cache.exists() else []
    assert [r['sample_id'] for r in completed] == expected[:len(completed)]
    assert all(r['checkpoint_identity'] == state['fit_identity'] for r in completed)
    started = time.monotonic()
    with cache.open('a') as stream:
        for index in indices[len(completed):]:
            raw_logit, seconds, digest = predict(index)
            row = rows[index]
            entry = {'sample_id': row['sample_id'], 'recording_id': row['recording_id'],
                     'segment_id': row['segment_id'], 'failure': row['failure'],
                     'raw_visual_logit': raw_logit, 'pixels_sha256': digest,
                     'frames16': row['frames16'], 'seconds': seconds,
                     'checkpoint_identity': state['fit_identity'], 'device': 'cpu', 'precision': 'float32',
                     'torch_CPU_threads': cpu_threads(), 'CPU_backend': backend}
            stream.write(json.dumps(entry, allow_nan=False)+'\n')
            stream.flush()
            completed.append(entry)
            if len(completed)%5 == 0 or len(completed) == len(indices):
                recent = float(np.mean([r['seconds'] for r in completed[-20:]]))
                status('CPU_HELDOUT_INFERENCE', completed=len(completed), required=len(indices),
                       recent_seconds_per_action=recent, estimated_remaining_seconds=(len(indices)-len(completed))*recent,
                       existing_GPU_study_unchanged=True)
                print(utc(), 'CPU_ACTIONS', len(completed), '/', len(indices), 'seconds_per_action', recent, flush=True)
    cal = read(full_folder/'PHASE1_CALIBRATOR.json')['calibrator']
    probabilities = fusion.calibrated(np.array([r['raw_visual_logit'] for r in completed]), cal)
    final = [dict(r, p_visual=float(p), prediction_role='selected_inner_fold3_base_model_holdout')
             for r, p in zip(completed, probabilities)]
    write(ROOT/'04_training_side_predictions/FINETUNED100_HELDOUT.json', final)
    write(ROOT/'04_training_side_predictions/INFERENCE_RECEIPT.json',
          {'completed_utc': utc(), 'actions_per_arm': 920, 'training_side_recordings': 28,
           'calibrator_refitted_for_this_bank': False, 'in_sample_base_predictions_used': False,
           'new_CNN_fits': 0, 'CPU_only': True, 'torch_threads': torch.get_num_threads(),
           'FFmpeg_decoder_threads': 1, 'elapsed_this_invocation_seconds': time.monotonic()-started,
           'raw_CPU_forward_seconds': sum(r['seconds'] for r in completed),
           'frozen_sha256': sha(ROOT/'04_training_side_predictions/FROZEN100_HELDOUT.json'),
           'finetuned_sha256': sha(ROOT/'04_training_side_predictions/FINETUNED100_HELDOUT.json'),
           'CPU_runtime_override_identity': {'path': relative(runtime_path()), 'sha256': sha(runtime_path())},
           'protocol_sha256': sha(CONFIG)})
    status('CPU_HELDOUT_INFERENCE_COMPLETE', completed=920, required=920, new_CNN_fits=0)
    print('HELDOUT_INFERENCE_COMPLETE', flush=True)


if __name__ == '__main__':
    main()
