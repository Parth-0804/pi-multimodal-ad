"""Load original project primitives directly; do not copy the framework."""
from __future__ import annotations

from functools import lru_cache
import importlib.util
import sys

from .common import REPO, read, sha, signature

STUDY = REPO / 'parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01'
PHASE = REPO / '26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_source'


@lru_cache(maxsize=1)
def primitives():
    # These inspected modules define models/functions; no entry-point main runs.
    # All training/configuration and output locations remain owned by ViFailback.
    sys.path.insert(0, str(REPO / 'src'))
    sys.path.insert(0, str(PHASE))
    sys.path.insert(0, str(STUDY / 'source'))
    from phase_model import PhaseVisual, promote_normalization_affine
    from visual_model import pooled, Head
    from fusion import sensor_fit, sensor_predict, calibrate, calibrated, stacker, fused, standardizer
    from reassemble.section1_features import statistics
    from reassemble.section2_models import DecisionGate
    return dict(PhaseVisual=PhaseVisual, promote_normalization_affine=promote_normalization_affine,
                pooled=pooled, Head=Head, sensor_fit=sensor_fit, sensor_predict=sensor_predict,
                calibrate=calibrate, calibrated=calibrated, stacker=stacker, fused=fused,
                standardizer=standardizer, statistics=statistics, DecisionGate=DecisionGate)


def identities():
    paths = [PHASE / 'phase_model.py', STUDY / 'source/visual_model.py', STUDY / 'source/fusion.py',
             REPO / 'src/reassemble/section1_features.py', REPO / 'src/reassemble/section2_models.py']
    return {str(path.relative_to(REPO)): sha(path) for path in paths}
