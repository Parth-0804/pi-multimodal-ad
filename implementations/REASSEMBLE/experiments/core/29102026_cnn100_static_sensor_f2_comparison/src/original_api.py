"""Load historical definitions with their original module-resolution context."""
import importlib.util
import sys
from pathlib import Path


def load():
    root = Path(__file__).resolve().parents[1]
    repo = root.parents[2]
    base = repo/'26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability'
    study = repo/'parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01'
    # Give the legacy "common" name to the legacy module only while importing
    # historical functions. Their already-bound globals keep that context.
    current = sys.modules.pop('common', None)
    old_path = list(sys.path)
    try:
        sys.path.insert(0, str(study/'source'))
        spec = importlib.util.spec_from_file_location('common', study/'source/common.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules['common'] = module
        spec.loader.exec_module(module)
        import fusion
        sys.path.insert(0, str(base/'26102026_source'))
        import phase_model
        return fusion, phase_model
    finally:
        sys.path[:] = old_path
        if current is not None:
            sys.modules['common'] = current
        else:
            sys.modules.pop('common', None)
