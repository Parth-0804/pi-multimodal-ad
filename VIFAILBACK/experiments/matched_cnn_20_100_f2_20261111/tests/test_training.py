"""Synthetic numerical and crash-boundary checks; no real CNN fitting or GPU use."""
from copy import deepcopy
from types import SimpleNamespace
import random
import numpy as np
import pytest
import torch
from torch import nn
from matched_vifailback import common,model_runtime as mr,training as tr


class TinyCNN(nn.Module):
    def __init__(self):super().__init__();self.conv=nn.Conv2d(3,4,3,padding=1)
    def forward(self,x):return SimpleNamespace(feature_maps=[torch.relu(self.conv(x))])


class TinyHead(nn.Module):
    def __init__(self):super().__init__();self.layers=nn.Sequential(nn.Linear(4,5),nn.ReLU(),nn.Dropout(.1),nn.Linear(5,1));self.calls=0
    def forward(self,x):self.calls+=1;return self.layers(x).squeeze(-1)


def model(full=True):
    return mr.EpisodeModel(TinyCNN() if full else None,TinyHead(),np.array([.1,.2,.3,.4],dtype='float32'),np.array([1.,2.,.5,.8],dtype='float32'))


def test_two_pass_all48_camera_frames_same_episode_loss_and_minibatch_dropout():
    torch.set_num_threads(2);torch.manual_seed(42)
    a=model();b=deepcopy(a);xs=[torch.rand(3,16,3,8,8) for _ in range(3)];y=torch.tensor([0.,1.,1.]);w=torch.tensor(.144)
    torch.manual_seed(123);z=torch.stack([mr.episode_features(a.backbone,x,4,grad=True) for x in xs]);loss=nn.functional.binary_cross_entropy_with_logits(a.classify(z),y,pos_weight=w);loss.backward()
    torch.manual_seed(123);other,_=mr.full_batch_backward(b,xs,y,w)
    assert a.head.calls==b.head.calls==1
    assert torch.allclose(loss,other,atol=1e-7,rtol=1e-6)
    for (n,p),(m,q) in zip(a.named_parameters(),b.named_parameters()):
        assert n==m and torch.allclose(p.grad,q.grad,atol=2e-7,rtol=2e-5),n


def test_global_clipping_matches_single_device_reference():
    torch.manual_seed(42);a=model();b=deepcopy(a)
    for p,q in zip(a.parameters(),b.parameters()):p.grad=torch.randn_like(p)*2;q.grad=p.grad.clone()
    expected=nn.utils.clip_grad_norm_(a.parameters(),1.);actual=mr.global_clip(b,1.)
    assert np.isclose(float(expected),actual,rtol=1e-6)
    assert all(torch.allclose(p.grad,q.grad,atol=1e-7,rtol=1e-6) for p,q in zip(a.parameters(),b.parameters()))


@pytest.mark.parametrize('epochs,horizon',[(20,50),(100,100)])
def test_complete_schedule_does_not_shorten_to_selected_epoch(epochs,horizon):
    m=model(False);opt=mr.optimizer_for(m);scheduler=tr.scheduler_for(opt,horizon);observed=[];best=None
    for e in range(1,epochs+1):
        observed.append(opt.param_groups[0]['lr']);row={'epoch':e,'V_macro_AP':1./e,'V_weighted_BCE_same_T_positive_weight':1.}
        if tr.better(row,best):best=row
        opt.step();scheduler.step()
    assert len(observed)==epochs and best['epoch']==1
    assert np.allclose(observed,[.001*(.1+.9*.5*(1+np.cos(np.pi*t/horizon))) for t in range(epochs)],rtol=0,atol=1e-16)
    assert opt.param_groups[0]['betas']==(.9,.999) and opt.param_groups[0]['eps']==1e-8


def test_macro_selection_then_lower_weighted_bce_then_earliest():
    base={'epoch':3,'V_macro_AP':.7,'V_weighted_BCE_same_T_positive_weight':.8}
    assert tr.better(dict(base,epoch=4,V_weighted_BCE_same_T_positive_weight=.7),base)
    assert not tr.better(dict(base,epoch=4),base)
    assert not tr.better(dict(base,V_macro_AP=.69,V_weighted_BCE_same_T_positive_weight=.1),base)


def test_recovery_rolls_back_uncommitted_future_best_and_exact_next_update(tmp_path,monkeypatch):
    cfg=common.protocol();monkeypatch.setattr(mr,'protocol',lambda:cfg)
    monkeypatch.setattr(common,'STUDY',tmp_path)
    torch.manual_seed(42);random.seed(42);np.random.seed(42)
    m=model(False);opt=mr.optimizer_for(m);scheduler=tr.scheduler_for(opt,50);x=torch.randn(3,4);target=torch.tensor([0.,1.,1.])
    def step():
        opt.zero_grad();loss=nn.functional.binary_cross_entropy_with_logits(m.classify(x),target);loss.backward();mr.global_clip(m);opt.step();return loss.detach()
    step();scheduler.step();recover=tr.EpochRecovery(tmp_path,'synthetic')
    payload={'model':tr.cpu_tree(m.state_dict()),'selected_epoch':1}
    recover.save({'model':m.state_dict(),'optimizer':opt.state_dict(),'scheduler':scheduler.state_dict(),'rng':tr.rng_state(),
                  'completed_epochs':1,'best_payload':payload,'history':[{'epoch':1}]})
    expected=step();expected_state=mr.snapshot(m)
    tr.atomic_checkpoint(tmp_path/'BEST_MODEL.pt',{'model':m.state_dict(),'selected_epoch':999})
    state=recover.load();assert torch.load(tmp_path/'BEST_MODEL.pt',weights_only=True)['selected_epoch']==1
    m.load_state_dict(state['model']);opt.load_state_dict(state['optimizer']);scheduler.load_state_dict(state['scheduler']);tr.restore_rng(state['rng'])
    assert torch.equal(step(),expected) and mr.snapshot(m)==expected_state
    final=recover.final(1);pointer=common.read_json(tmp_path/'RECOVERY_POINTER.json')
    assert final.stat().st_ino==(tmp_path/pointer['slot']).stat().st_ino


@pytest.mark.parametrize('epochs',[20,100])
def test_actual_trainer_all_epochs_final_checkpoint_and_completed_resume(tmp_path,monkeypatch,epochs):
    condition='FROZEN20' if epochs==20 else 'DONOR100'
    cfg=common.protocol();cfg['epochs'][condition]=epochs
    monkeypatch.setattr(common,'STUDY',tmp_path)
    monkeypatch.setattr(tr,'STUDY',tmp_path)
    monkeypatch.setattr(tr,'protocol',lambda:cfg)
    monkeypatch.setattr(mr,'protocol',lambda:cfg)
    monkeypatch.setattr(tr,'fit_root',lambda *args:tmp_path/condition)
    monkeypatch.setattr(tr,'check_storage',lambda *args:None)
    monkeypatch.setattr(tr,'_source_identity',lambda:{'synthetic':'v1'})
    monkeypatch.setattr(tr,'make_model',lambda mean,std,seed,full,device:mr.EpisodeModel(None,TinyHead(),mean,std))
    import matched_vifailback.data as data
    rows=[{'episode_index':i,'label':i%2} for i in range(18)]
    job={'id':'outer0_inner0','outer':0,'inner':0,'ids':{'T':list(range(8)),'V':list(range(8,12)),'C':list(range(12,14)),'A':list(range(14,16))},'groups':{}}
    ctx={'config':{},'lookup':{r['episode_index']:r for r in rows},'index':{i:i for i in range(18)},'original':np.random.default_rng(5).normal(size=(18,4)).astype('float32')}
    ctx['donor']=ctx['original'];monkeypatch.setattr(data,'get_job',lambda ctx,name:job);monkeypatch.setattr(data,'pilot_outer_ids',lambda ctx:[16,17])
    result=tr.fit(condition,42,'outer0_inner0',context=ctx)
    assert result['executed_epochs']==epochs
    root=tmp_path/condition;history=common.read_json(root/'HISTORY.json');assert [h['epoch'] for h in history]==list(range(1,epochs+1))
    assert torch.load(root/f'FINAL_EPOCH{epochs}.pt',weights_only=True)['completed_epochs']==epochs
    assert result['selected_epoch']==max(history,key=lambda h:(h['V_macro_AP'],-h['V_weighted_BCE_same_T_positive_weight'],-h['epoch']))['epoch']
    assert len(common.read_json(root/'predictions.json'))==2
    assert tr.fit(condition,42,'outer0_inner0',context=ctx)==result
