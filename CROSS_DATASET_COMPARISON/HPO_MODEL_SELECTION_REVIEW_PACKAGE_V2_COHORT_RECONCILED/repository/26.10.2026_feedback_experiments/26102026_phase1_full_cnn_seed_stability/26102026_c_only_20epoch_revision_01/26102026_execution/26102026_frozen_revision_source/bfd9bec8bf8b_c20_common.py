"""Explicit schedule/budget amendment around the unchanged Phase 1 primitives."""
from pathlib import Path
import sys

REVISION = Path(__file__).resolve().parents[1]
BASE = REVISION.parent
sys.path.insert(0, str(BASE/'26102026_source'))
from phase_common import REPO, ROOT, EXEC, EVIDENCE, CONFIG, read, write, sha, utc, signature, host_resources
from phase_common import config as base_config

ARM = 'C_full_finetuned16'
RUN = REVISION/'26102026_execution'
REPORTS = REVISION/'26102026_reports'
REV_CONFIG = REVISION/'26102026_configuration/PHASE1_C_ONLY_CONFIG.json'


def configuration():
    return read(REV_CONFIG)


def schedule():
    c = configuration()
    assert c['arms'] == [ARM] and c['epochs'] == 20
    return [(seed, job) for seed in c['seeds'] for job in read(EVIDENCE/'PHASE1_FIT_PLAN.json')]


def effective_training_configuration():
    # Keep initialization, optimizer, input path and the original cosine-50
    # learning-rate prefix. Only the execution horizon/stop rule change.
    c = base_config()
    c.update(arms=[ARM], min_epochs=20, max_epochs=20,
             stopping='Exactly20 completed epochs unless unsafe or explicitly interrupted')
    return c


def fixed_stop(epoch, best_epoch, *args, **kwargs):
    return epoch >= 20


def receipt_for(seed, job):
    return RUN/f'PHASE1_C_ONLY_COMPLETE_SEED{seed}_JOB{job["job_index"]:02d}.json'


def remaining_estimate():
    from phase_training import folder_for
    speed = read(EVIDENCE/'PHASE1_FULL_CNN_BENCHMARK.json')['actions_per_second']
    presentations = 0
    complete = 0
    for seed, job in schedule():
        folder = folder_for(ARM, seed, job)
        if receipt_for(seed, job).exists():
            complete += 1
            continue
        pointer = folder/'PHASE1_LATEST_EPOCH.json'
        epoch = read(pointer)['completed_epoch'] if pointer.exists() else 0
        assert epoch <= 20, 'C20_BUDGET_INCOMPATIBLE_WITH_EXISTING_EXPOSURE'
        presentations += len(job['training'])*(20-epoch)
    hours = presentations/speed/3600
    return {'completed_C_fits': complete, 'required_C_fits': 75,
            'remaining_CNN_training_hours': hours,
            'remaining_planning_GPU_job_hours': [hours*1.2, hours*1.4],
            'remaining_planning_days_exclusive_GPU': [hours*1.2/24, hours*1.4/24]}


def status(stage, **extra):
    value = {'utc': utc(), 'stage': stage, 'status': 'RUNNING', 'arm': ARM,
             'epoch_budget': 20, 'pending_B_fits': 0, **remaining_estimate(),
             'host_resources': host_resources(), **extra}
    write(RUN/'PHASE1_C_ONLY_STATUS.json', value)
    return value
