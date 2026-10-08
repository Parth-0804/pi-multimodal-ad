from datetime import datetime,timezone
import numpy as np
import pytest
import torch
from reassemble.additional_improvements.training_recovery import Recovery,random_state,restore_random


@pytest.mark.parametrize('device',['cpu','cuda'])
def test_interrupted_training_matches_uninterrupted(tmp_path,device):
    if device=='cuda' and not torch.cuda.is_available():pytest.skip('CUDA unavailable')
    torch.set_num_threads(1);torch.manual_seed(7)
    model=torch.nn.Sequential(torch.nn.Linear(3,5),torch.nn.Dropout(.25),torch.nn.Linear(5,1)).to(device)
    opt=torch.optim.AdamW(model.parameters(),lr=.001)
    amp=torch.amp.GradScaler('cuda',enabled=device=='cuda')
    rng=np.random.default_rng(9);x=torch.arange(24,dtype=torch.float32,device=device).reshape(8,3)/20
    def step(m,o,a,g):
        indices=g.permutation(8);o.zero_grad(set_to_none=True)
        with torch.autocast(device_type=device,enabled=device=='cuda',dtype=torch.float16):loss=m(x[indices]).square().mean()
        a.scale(loss).backward();a.step(o);a.update()
        return loss.detach().cpu()
    step(model,opt,amp,rng)
    recovery=Recovery(tmp_path,'fixed-test-signature')
    recovery.save(dict(model=model.state_dict(),optimizer=opt.state_dict(),amp=amp.state_dict(),random=random_state(rng),offset=128))
    expected=[step(model,opt,amp,rng) for _ in range(3)]
    state=recovery.load()
    replacement=torch.nn.Sequential(torch.nn.Linear(3,5),torch.nn.Dropout(.25),torch.nn.Linear(5,1)).to(device)
    optimizer=torch.optim.AdamW(replacement.parameters(),lr=.001);scaler=torch.amp.GradScaler('cuda',enabled=device=='cuda')
    replacement.load_state_dict(state['model']);optimizer.load_state_dict(state['optimizer']);scaler.load_state_dict(state['amp'])
    generator=np.random.default_rng();restore_random(state['random'],generator)
    actual=[step(replacement,optimizer,scaler,generator) for _ in range(3)]
    assert all(torch.equal(a,b) for a,b in zip(expected,actual))
    assert all(torch.equal(v,replacement.state_dict()[k]) for k,v in model.state_dict().items())
    assert state['offset']==128 and amp.state_dict()==scaler.state_dict()
    for key,values in opt.state_dict()['state'].items():
        for field,value in values.items():
            other=optimizer.state_dict()['state'][key][field]
            assert torch.equal(value,other) if torch.is_tensor(value) else value==other


def test_partial_write_and_signature_guard(tmp_path):
    r=Recovery(tmp_path,'a');assert r.due();r.save({'value':torch.tensor([1])});assert not r.due()
    (tmp_path/'slot1.pending.interrupted').write_bytes(b'not committed')
    assert r.load()['value'].item()==1
    r.save({'value':torch.tensor([2])});r.save({'value':torch.tensor([3])})
    assert r.load()['value'].item()==3 and len(list(tmp_path.glob('slot*.pt')))==2
    with pytest.raises(ValueError,match='signature'):Recovery(tmp_path,'changed').load()
    (tmp_path/'slot0.pt').write_bytes(b'damaged')
    with pytest.raises(ValueError,match='hash'):r.load()


@pytest.mark.skipif(not torch.cuda.is_available(),reason='CUDA unavailable')
def test_actual_finetune_loop_resumes_same_selection_and_predictions(tmp_path,monkeypatch):
    from pathlib import Path
    from reassemble.additional_improvements import finetune as ft,prefix_cache
    from reassemble.additional_improvements.training_recovery import TrainingPaused
    torch.set_num_threads(1)
    class Backbone(torch.nn.Module):
        def __init__(self):
            super().__init__();self.encoder=torch.nn.Module()
            self.encoder.stages=torch.nn.ModuleList([torch.nn.Identity() for _ in range(3)]+[torch.nn.Linear(4,4)])
    class Model(torch.nn.Module):
        def __init__(self,backbone,checkpoint):
            super().__init__();self.backbone=backbone
            self.head=torch.nn.Sequential(torch.nn.Dropout(.2),torch.nn.Linear(4,1))
            self.register_buffer('mean',torch.zeros(4));self.register_buffer('std',torch.ones(4))
        def forward(self,x):return self.head(self.backbone.encoder.stages[3](x).mean(1)).squeeze(-1)
    class Source:
        def values(self,rows):return x[rows]
    x=torch.arange(16*16*4,dtype=torch.float32,device='cuda').reshape(16,16,4)/1000
    config={'run_dir':str(tmp_path),'finetune':dict(head_lr=.001,pretrained_lr=.0001,weight_decay=.001,batch_size=4,max_epochs=3,patience=5)}
    monkeypatch.setattr(ft,'config',lambda:config);monkeypatch.setattr(ft,'storage',lambda:None)
    monkeypatch.setattr(ft,'load_visual',lambda base:(None,Backbone(),None))
    monkeypatch.setattr(prefix_cache,'CachedFineTunedVisual',Model)
    monkeypatch.setattr(Recovery,'due',lambda self:True)
    monkeypatch.setattr(ft,'should_pause',lambda:False)
    initial=tmp_path/'initial.pt';torch.save({},initial)
    parent=tmp_path/'01_temporal_visual/fits/V-FT';parent.mkdir(parents=True)
    args=(Source(),None,{},initial,np.arange(16)%2,np.arange(12),np.arange(12,16),7,None,2,'test-signature')
    expected,detail=ft._fit(parent/'reference',*args)
    monkeypatch.setattr(ft,'should_pause',lambda:True)
    with pytest.raises(TrainingPaused):ft._fit(parent/'resumed',*args)
    monkeypatch.setattr(ft,'should_pause',lambda:False)
    actual,resumed=ft._fit(parent/'resumed',*args)
    assert all(np.array_equal(expected[k],actual[k]) for k in expected)
    assert detail['best_epoch']==resumed['best_epoch'] and detail['stopped_epoch']==resumed['stopped_epoch']
    for a,b in zip(detail['history'],resumed['history']):
        assert {k:v for k,v in a.items() if k!='elapsed_seconds'}=={k:v for k,v in b.items() if k!='elapsed_seconds'}


def test_final_publication_reuses_equal_files_and_rejects_changed(tmp_path):
    from reassemble.additional_improvements.training_recovery import publish_predictions,publish_selected
    pred=tmp_path/'p.npz';values={'p':np.array([.1,.9])};publish_predictions(pred,values)
    before=pred.read_bytes();mtime=pred.stat().st_mtime_ns
    publish_predictions(pred,values);assert pred.read_bytes()==before and pred.stat().st_mtime_ns==mtime
    with pytest.raises(ValueError):publish_predictions(pred,{'p':np.array([.2,.9])})
    checkpoint=tmp_path/'selected.pt';state=dict(state_dict={'w':torch.tensor([1.])},epoch=2,seed=7,initial={})
    publish_selected(checkpoint,state);before=checkpoint.read_bytes();mtime=checkpoint.stat().st_mtime_ns
    publish_selected(checkpoint,state);assert checkpoint.read_bytes()==before and checkpoint.stat().st_mtime_ns==mtime
    with pytest.raises(ValueError):publish_selected(checkpoint,{**state,'epoch':3})
