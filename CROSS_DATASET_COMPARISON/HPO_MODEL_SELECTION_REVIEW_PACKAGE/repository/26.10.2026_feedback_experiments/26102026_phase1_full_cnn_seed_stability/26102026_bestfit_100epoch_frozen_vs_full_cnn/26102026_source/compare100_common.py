"""Separate two-fit100-epoch experiment; the paused study stays immutable."""
from pathlib import Path
import math
import sys

DETOUR = Path(__file__).resolve().parents[1]
BASE = DETOUR.parent
MAIN_REVISION = BASE/'26102026_c_only_20epoch_revision_01'
sys.path.insert(0,str(BASE/'26102026_source'))
from phase_common import REPO, EVIDENCE, STUDY, read, write, sha, signature, utc, environment, host_resources
from phase_common import config as original_configuration
from phase_common import EXEC as MAIN_EXEC

RUN=DETOUR/'26102026_execution'
REPORTS=DETOUR/'26102026_reports'
CONFIG=DETOUR/'26102026_configuration/PHASE1_COMPARISON_CONFIG.json'
JOB=DETOUR/'26102026_configuration/PHASE1_SELECTED_JOB.json'


def configuration():
    return read(CONFIG)


def effective_configuration():
    c=original_configuration()
    c.update(min_epochs=100,max_epochs=100,arms=configuration()['arms'],
             stopping='Exactly100 epochs unless unsafe or explicitly interrupted')
    return c


def fixed_stop(epoch,best_epoch,*args,**kwargs):
    return epoch>=100


def scheduler100(optimizer):
    import torch
    return torch.optim.lr_scheduler.LambdaLR(optimizer,lambda epoch:.1+.9*.5*(1+math.cos(math.pi*epoch/100)))


def folder_for(arm,seed,job):
    assert arm in configuration()['arms']
    return RUN/f'26102026_{arm}_seed{seed}_selectedjob{job["job_index"]:02d}'


def fit_identity(arm,seed,job):
    return signature({'arm':arm,'seed':seed,'selected_job':job,'configuration_sha256':sha(CONFIG),
        'inputs':sha(EVIDENCE/'PHASE1_INPUT_IDENTITY_MANIFEST.json'),
        'pretrained':sha(STUDY/'provenance/original_pretrained_identity.json')})


def status(stage,**extra):
    value={'utc':utc(),'stage':stage,'status':'RUNNING','epochs_per_arm':100,'arms':configuration()['arms'],
           'main_study':'Temporarily paused at completed epoch; automatic continuation scheduled',
           'host_resources':host_resources(),**extra}
    write(RUN/'PHASE1_COMPARISON_STATUS.json',value)
    return value
