import sys
from pathlib import Path
import uuid

import torch
from torch import nn

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'26102026_source'))
from c20_common import ARM, RUN, schedule, effective_training_configuration, fixed_stop
from phase_model import make_scheduler
from phase_checkpoint import EpochRecovery, restore_rng
from phase_training import tensor_equal_tree


def test_schedule_contains_only_C_and_retains_all_seed_fold_roles():
    jobs=schedule()
    assert len(jobs)==75 and len({(seed,j['job_index']) for seed,j in jobs})==75
    assert {seed for seed,_ in jobs}=={42,123,20261023}
    for seed in [42,123,20261023]:
        subset=[job for s,job in jobs if s==seed]
        assert len(subset)==25
        for outer in range(5):
            assert len([j for j in subset if j['outer_fold_original']==outer])==5
    assert effective_training_configuration()['arms']==[ARM]


def test_twenty_epoch_cap_preserves_original_scheduler_and_checkpoint_prefix():
    folder=RUN/('26102026_revision_test_'+uuid.uuid4().hex[:8])
    folder.mkdir(parents=True)
    torch.manual_seed(42)
    model=nn.Sequential(nn.Linear(3,4),nn.Dropout(.1),nn.Linear(4,1))
    optimizer=torch.optim.AdamW(model.parameters(),lr=.001)
    scheduler=make_scheduler(optimizer)
    x=torch.arange(24).reshape(8,3).float()/10
    y=(torch.arange(8)%2).float()
    def step():
        optimizer.zero_grad(set_to_none=True)
        nn.functional.binary_cross_entropy_with_logits(model(x).flatten(),y).backward()
        optimizer.step();scheduler.step()
    for _ in range(8):step()
    recovery=EpochRecovery(folder,'c20-compatible-prefix')
    recovery.save({'completed_epoch':8,'model':model.state_dict(),'optimizer':optimizer.state_dict(),'scheduler':scheduler.state_dict()})
    for _ in range(8,20):step()
    reference={k:v.clone() for k,v in model.state_dict().items()}
    reference_opt=optimizer.state_dict()
    reference_sched=scheduler.state_dict()
    reference_rng=torch.get_rng_state()
    saved=recovery.load()
    model.load_state_dict(saved['model'])
    optimizer=torch.optim.AdamW(model.parameters(),lr=.001)
    scheduler=make_scheduler(optimizer)
    optimizer.load_state_dict(saved['optimizer']);scheduler.load_state_dict(saved['scheduler'])
    restore_rng(saved['random'])
    c=effective_training_configuration()
    executed=saved['completed_epoch']
    while not fixed_stop(executed,1):
        step();executed+=1
    assert executed==c['max_epochs']==c['min_epochs']==20
    assert tensor_equal_tree(reference,model.state_dict())
    assert tensor_equal_tree(reference_opt,optimizer.state_dict())
    assert tensor_equal_tree(reference_sched,scheduler.state_dict())
    assert torch.equal(reference_rng,torch.get_rng_state())
    assert scheduler.get_last_lr()[0] > .0006  # cosine50 prefix, not cosine20 endpoint
