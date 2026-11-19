"""Matched FP32 end-to-end inference cost, separate from cached-head timing."""
import time
import gc

import numpy as np
import torch

from phase_common import EXEC, EVIDENCE, config, read, write
from phase_loader import EpochLoader
from phase_model import make_model
from phase_training import folder_for, predict


def benchmark_inference():
    job = next(j for j in read(EVIDENCE/'PHASE1_FIT_PLAN.json') if j['role'] == 'outer_assessment')
    seed = config()['seeds'][0]
    indices = np.asarray(job['training'][:24])
    # No labels are used for timing or for model selection.
    labels = torch.zeros(4530, device='cuda')
    results = []
    folder = EXEC/'26102026_matched_inference_benchmark'
    folder.mkdir(exist_ok=True)
    for arm in config()['arms']:
        model = make_model('C_full_finetuned16', job['training'], seed)
        checkpoint = torch.load(folder_for(arm, seed, job)/'PHASE1_BEST_MODEL.pt', map_location='cpu', weights_only=True)
        missing = model.load_state_dict(checkpoint['model'], strict=False)
        assert not missing.unexpected_keys
        assert not missing.missing_keys if arm.startswith('C_') else all(n.startswith('backbone.') for n in missing.missing_keys)
        model.requires_grad_(False)
        with EpochLoader(indices, folder, arm) as loader:
            predict(model, indices, labels, None, loader)
            for repetition in range(2):
                torch.cuda.synchronize()
                start = time.monotonic()
                predict(model, indices, labels, None, loader)
                torch.cuda.synchronize()
                seconds = time.monotonic()-start
                results.append({'arm': arm, 'repetition': repetition, 'seconds': seconds,
                    'actions': len(indices), 'actions_per_second': len(indices)/seconds,
                    'cached_feature_shortcut_used': False, 'precision': 'float32'})
        del model
        gc.collect()
        torch.cuda.empty_cache()
    write(EXEC/'PHASE1_MATCHED_INFERENCE_BENCHMARK.json', {'windows': results,
        'scope': 'Representative first-seed outer-assessment checkpoints; 24 training-side actions; identical live16 pipeline',
        'worker_startup_and_model_loading_excluded': True})
