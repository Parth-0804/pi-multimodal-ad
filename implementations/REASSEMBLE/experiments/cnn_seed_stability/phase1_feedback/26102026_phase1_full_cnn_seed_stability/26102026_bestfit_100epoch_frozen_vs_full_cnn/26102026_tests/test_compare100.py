"""Budget, selection isolation, and exact stochastic checkpoint continuation."""
from pathlib import Path
import hashlib
import random
import sys
import tempfile

import numpy as np
import pytest
import torch

DETOUR=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(DETOUR/'26102026_source'))
from compare100_common import BASE,REPO,RUN,JOB,EVIDENCE,read,sha,configuration,scheduler100,folder_for,fit_identity
from compare100_common import fixed_stop,effective_configuration
from compare100_controller import main_sources_ok,own_stop,resume_command
from phase_checkpoint import EpochRecovery,restore_rng,rng_state,cpu_tree
from phase_training import tensor_equal_tree,run_identity,folder_for as original_folder


def test_validation_selection_and_disjoint_recordings():
    selection=read(DETOUR/'26102026_evidence/PHASE1_FIT_SELECTION.json')
    candidates=selection['candidate_snapshot']
    chosen=min(candidates,key=lambda r:(-r['validation_AP'],r['validation_loss'],r['seed'],r['job_index']))
    assert selection['chosen']==chosen and chosen['job_index']==2 and chosen['seed']==42
    cohort=read(EVIDENCE/'PHASE1_INPUT_IDENTITY_MANIFEST.json')
    plan=read(EVIDENCE/'PHASE1_FIT_PLAN.json')
    job=read(JOB)
    original=next(j for j in plan if j['job_index']==chosen['job_index'])
    for role in ['training','validation','C','G']:assert job[role]==original[role]
    roles=[{cohort[i]['recording_id'] for i in job[role]} for role in ['training','validation','C','predict']]
    for i,a in enumerate(roles):
        for b in roles[i+1:]:assert a.isdisjoint(b)
    for candidate in candidates:
        assert candidate['executed_epochs']==20
        j=next(j for j in plan if j['job_index']==candidate['job_index'])
        for role in ['training','validation','C','predict']:
            assert roles[-1].isdisjoint({cohort[i]['recording_id'] for i in j[role]})
    assert len(job['predict'])==753 and selection['assessment_labels_or_metrics_read_for_selection'] is False


def test_100_budget_matched_cosine_and_separate_identity():
    a=torch.nn.Parameter(torch.tensor(1.));b=torch.nn.Parameter(torch.tensor(2.))
    optimizer=torch.optim.AdamW([{'params':[a],'lr':1e-3},{'params':[b],'lr':1e-5}])
    scheduler=scheduler100(optimizer)
    for epoch in range(101):
        if epoch in [0,50,100]:
            expected={0:1.,50:.55,100:.1}[epoch]
            assert optimizer.param_groups[0]['lr']==pytest.approx(1e-3*expected)
            assert optimizer.param_groups[1]['lr']==pytest.approx(1e-5*expected)
        if epoch<100:optimizer.step();scheduler.step()
        assert fixed_stop(epoch,1)==(epoch>=100)
    assert effective_configuration()['max_epochs']==100
    job=read(JOB)
    for arm in configuration()['arms']:
        assert folder_for(arm,42,job).is_relative_to(DETOUR)
        assert folder_for(arm,42,job)!=original_folder(arm,42,job)
        assert fit_identity(arm,42,job)!=run_identity(arm,42,job)
    main_sources_ok()
    assert resume_command()[-1].endswith('26102026_source/c20_controller.py')
    c20=read(BASE/'26102026_c_only_20epoch_revision_01/26102026_configuration/PHASE1_C_ONLY_CONFIG.json')
    assert c20['epochs']==20 and c20['arms']==['C_full_finetuned16']


def test_resume100_restores_stochastic_optimizer_and_scheduler_exactly():
    def initial():
        random.seed(197);np.random.seed(197);torch.manual_seed(197)
        model=torch.nn.Sequential(torch.nn.Linear(3,4),torch.nn.Dropout(.2),torch.nn.Linear(4,1))
        opt=torch.optim.AdamW(model.parameters(),lr=1e-3)
        return model,opt,scheduler100(opt)
    def advance(model,opt,scheduler,start,end):
        for _ in range(start,end+1):
            x=torch.randn(7,3)*(random.random()+np.random.uniform())
            loss=model(x).square().mean();opt.zero_grad();loss.backward();opt.step();scheduler.step()
    model,opt,scheduler=initial();advance(model,opt,scheduler,1,100)
    expected=cpu_tree({'model':model.state_dict(),'optimizer':opt.state_dict(),'scheduler':scheduler.state_dict(),'rng':rng_state()})
    model,opt,scheduler=initial();advance(model,opt,scheduler,1,37)
    with tempfile.TemporaryDirectory(prefix='26102026_synthetic_recovery_',dir=RUN) as tmp:
        recovery=EpochRecovery(Path(tmp),'synthetic100')
        recovery.save({'completed_epoch':37,'model':model.state_dict(),'optimizer':opt.state_dict(),'scheduler':scheduler.state_dict()})
        torch.rand(13);random.random();np.random.rand(5)
        state=recovery.load();assert state['completed_epoch']==37
        model,opt,scheduler=initial()
        model.load_state_dict(state['model']);opt.load_state_dict(state['optimizer']);scheduler.load_state_dict(state['scheduler'])
        restore_rng(state['random']);advance(model,opt,scheduler,38,100)
        actual=cpu_tree({'model':model.state_dict(),'optimizer':opt.state_dict(),'scheduler':scheduler.state_dict(),'rng':rng_state()})
        assert tensor_equal_tree(expected,actual)


def test_different_stop_request_is_never_consumed():
    with tempfile.TemporaryDirectory(prefix='26102026_synthetic_control_',dir=RUN) as tmp:
        marker=Path(tmp)/'stop.json';marker.write_text('{"request_id":"new-user-stop"}')
        with pytest.raises(AssertionError,match='DIFFERENT_STOP_REQUEST'):
            own_stop(marker,{'request_id':'old-pause'})
        assert marker.exists()
