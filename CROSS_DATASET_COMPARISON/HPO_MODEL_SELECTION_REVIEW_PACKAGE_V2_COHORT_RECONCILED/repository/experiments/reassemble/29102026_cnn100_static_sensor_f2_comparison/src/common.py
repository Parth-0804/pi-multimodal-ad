"""Paths and immutable identities for this isolated REASSEMBLE comparison."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
BASE = REPO / '26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability'
COMPARISON = BASE / '26102026_bestfit_100epoch_frozen_vs_full_cnn'
STUDY = REPO / 'parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01'
EVIDENCE = BASE / '26102026_evidence'
RUN = REPO / json.loads((ROOT/'01_experiment_definition/ACTIVE_RUN.json').read_text())['run']
CONFIG = ROOT/'01_experiment_definition/LOCKED_PROTOCOL_03.json'
ARMS = {'frozen': '26102026_B_frozen100_seed42_selectedjob02',
        'finetuned': '26102026_C_full_finetuned16_seed42_selectedjob02'}


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8*1024**2), b''):
            h.update(block)
    return h.hexdigest()


def relative(path):
    return Path(path).relative_to(REPO).as_posix()


def write(path, value):
    path = Path(path)
    assert path.resolve().is_relative_to(ROOT.resolve()), 'Existing studies must remain unchanged'
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name+'.writing')
    temp.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
    temp.replace(path)


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def cohort():
    return read(EVIDENCE/'PHASE1_INPUT_IDENTITY_MANIFEST.json')


def job():
    return read(COMPARISON/'26102026_configuration/PHASE1_SELECTED_JOB.json')


def arm_folder(arm):
    return COMPARISON/'26102026_execution'/ARMS[arm]


def load_original_modules():
    # Historical modules also use the name "common". Load their package paths
    # only in a separate child process (see original_api.py), not by shadowing
    # this task's common module.
    raise RuntimeError('Use original_api; preserve original import resolution')


def identity(path):
    return {'path': relative(path), 'bytes': Path(path).stat().st_size, 'sha256': sha(path)}


def status(stage, **extra):
    write(ROOT/'STATUS.json', {'utc': utc(), 'stage': stage, **extra})
