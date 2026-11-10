"""Optional FP32 inference compiler check on one fixed calibration control."""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '4'
import sys
import time
import warnings
import hashlib
import numpy as np
import torch
from common import ROOT, REPO, STUDY, RUN, read, write, job, cohort, arm_folder
from original_api import load


def main():
    _, models = load()
    selected = job();row = cohort()[selected['C'][0]]
    model = models.make_model('C_full_finetuned16', selected['training'], 42, device='cpu')
    payload = torch.load(arm_folder('finetuned')/'PHASE1_BEST_MODEL.pt', map_location='cpu', weights_only=True)
    model.load_state_dict(payload['model'], strict=True);model.requires_grad_(False);model.eval()
    torch.set_num_threads(4)
    sys.path.insert(0, str(REPO/'26.10.2026_feedback_experiments/source'))
    from isolated_decode import IsolatedDecoder
    c = read(STUDY/'config/resolved_config.json')
    pixels = IsolatedDecoder(REPO, c['weights_dir'], c['rescale_factor'], decoder_threads=1)(dict(row, frames32=row['frames16']))
    assert hashlib.sha256(pixels.tobytes()).hexdigest() == row['selected16_sha256']
    x = torch.from_numpy(pixels.astype('float32')*np.float32(1/255)).unsqueeze(0)
    receipt = {'sample_id': row['sample_id'], 'labels_used': False, 'threads': 4,
               'checkpoint_identity': payload['fit_identity'], 'precision': 'float32'}
    try:
        with torch.inference_mode():
            start = time.monotonic();reference = float(model(x)[0]);receipt['eager_seconds'] = time.monotonic()-start
            print('EAGER', receipt['eager_seconds'], reference, flush=True)
            start = time.monotonic()
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                traced = torch.jit.trace(model, x, check_trace=False, strict=False)
                optimized = torch.jit.optimize_for_inference(torch.jit.freeze(traced.eval()))
            receipt['compiler_seconds'] = time.monotonic()-start
            receipt['compiler_warning_types'] = sorted({type(w.message).__name__ for w in caught})
            values = []
            for _ in range(2):
                start = time.monotonic();p = float(optimized(x)[0]);seconds = time.monotonic()-start
                values.append({'raw_logit': p, 'seconds': seconds, 'absolute_eager_difference': abs(p-reference)})
                print('OPTIMIZED', values[-1], flush=True)
            assert all(v['absolute_eager_difference'] < 1e-3 for v in values)
            receipt.update(passed=True, optimized=values, model_choice_changed=False,
                           shape_contract='Fixed1 action,16 frames,3 RGB channels,640x640; no dynamic input shape')
    except Exception as error:
        receipt.update(passed=False, error_type=type(error).__name__, error=str(error)[:2000])
        print('OPTIONAL_COMPILER_UNAVAILABLE', receipt['error_type'], flush=True)
    write(RUN/'manifests/OPTIONAL_FP32_CPU_COMPILER_BENCHMARK.json', receipt)


if __name__ == '__main__':main()
