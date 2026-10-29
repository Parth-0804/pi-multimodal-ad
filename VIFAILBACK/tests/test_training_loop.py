"""Exercise the actual100-epoch orchestration using tiny synthetic feature rows."""
import numpy as np
import torch
import pytest
from vifailback import common,training
from vifailback.reference import primitives


@pytest.mark.parametrize('condition',['V1','V1_high_only'])
def test_executed_epochs_validation_selection_final_and_resume(tmp_path,monkeypatch,condition):
    c=common.config();c['run_id']='synthetic'
    monkeypatch.setattr(common,'PROJECT',tmp_path);monkeypatch.setattr(training,'PROJECT',tmp_path)
    rows=[{'episode_index':i,'canonical_task_id':i//2,'label':i%2} for i in range(24)]
    job={'id':'synthetic','outer':0,'inner':-1,'ids':{'T':list(range(12)),'V':list(range(12,16)),
         'C':list(range(16,20)),'A':list(range(20,24))},'groups':{}}
    rng=np.random.default_rng(42);bank=rng.normal(size=(24,896)).astype('float32')
    monkeypatch.setattr(training,'finalize',lambda c:rows)
    monkeypatch.setattr(training,'pooled_bank',lambda c,condition:(bank,{'sha256':'synthetic'}))
    monkeypatch.setattr(training,'make',lambda c,condition,mean,std,seed,device:
                        primitives()['PhaseVisual'](None,896,mean,std,False))
    monkeypatch.setattr(training,'disk_reserve',lambda *args:10**12)
    receipt=training.fit(c,condition,job,42,'cpu')
    branch='visual_frozen' if condition=='V1' else 'visual_frozen_high_only'
    root=tmp_path/f'06_training_experiments/{branch}/runs/synthetic/seed42/synthetic'
    assert receipt['executed_epochs']==100
    history=common.read(root/'HISTORY.json');assert [r['epoch'] for r in history]==list(range(1,101))
    assert receipt['selected_epoch']==1+int(np.argmax([r['V_macro_AP'] for r in history]))
    assert (root/'FINAL_EPOCH100.pt').stat().st_ino==(root/'RECOVERY.pt').stat().st_ino
    final=torch.load(root/'FINAL_EPOCH100.pt',weights_only=True);assert final['completed_epochs']==100
    assert len(common.read(root/'predictions.json'))==4
    assert training.fit(c,condition,job,42,'cpu')==receipt
