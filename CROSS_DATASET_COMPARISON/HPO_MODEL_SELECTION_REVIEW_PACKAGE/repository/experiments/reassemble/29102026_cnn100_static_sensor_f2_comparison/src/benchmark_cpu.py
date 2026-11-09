"""Measure CPU inference throughput only; never inspect labels or choose models."""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '2'
import sys
import time
import hashlib
import numpy as np
import torch
from common import ROOT, REPO, STUDY, RUN, read, write, job, cohort, arm_folder
from original_api import load


def main():
    _, models = load()
    selected = job()
    index = selected['C'][0]  # Predefined calibration control; labels unused.
    row = cohort()[index]
    model = models.make_model('C_full_finetuned16', selected['training'], 42, device='cpu')
    payload = torch.load(arm_folder('finetuned')/'PHASE1_BEST_MODEL.pt', map_location='cpu', weights_only=True)
    model.load_state_dict(payload['model'], strict=True)
    model.requires_grad_(False);model.eval()
    sys.path.insert(0, str(REPO/'26.10.2026_feedback_experiments/source'))
    from isolated_decode import IsolatedDecoder
    config = read(STUDY/'config/resolved_config.json')
    pixels = IsolatedDecoder(REPO, config['weights_dir'], config['rescale_factor'], decoder_threads=1)(dict(row, frames32=row['frames16']))
    assert hashlib.sha256(pixels.tobytes()).hexdigest() == row['selected16_sha256']
    x = torch.from_numpy(pixels.astype('float32')*np.float32(1/255)).unsqueeze(0)
    evidence = []
    with torch.inference_mode():
        for threads in [2, 4, 8]:
            torch.set_num_threads(threads)
            start = time.monotonic();p = float(model(x)[0]);seconds = time.monotonic()-start
            evidence.append({'threads': threads, 'seconds': seconds, 'raw_logit': p})
            print('CPU_BENCHMARK', evidence[-1], flush=True)
    assert max(r['raw_logit'] for r in evidence)-min(r['raw_logit'] for r in evidence) < 1e-3
    write(RUN/'manifests/CPU_THREAD_THROUGHPUT.json', {'sample_id': row['sample_id'],
        'labels_used': False, 'model_choice_changed': False, 'FP32': True,
        '16_frames_unchanged': True, 'cpu_affinity_available': len(os.sched_getaffinity(0)),
        'benchmark': evidence, 'selection': min(evidence, key=lambda r:r['seconds'])['threads']})


if __name__ == '__main__':main()
