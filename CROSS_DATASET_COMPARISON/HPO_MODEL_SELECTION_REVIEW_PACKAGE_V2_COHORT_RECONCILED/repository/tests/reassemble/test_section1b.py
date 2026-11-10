import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from reassemble.section1b import guard_partition,fit_stacker
from reassemble.section1b_report import complement,decide


def test_partition_rejects_shared_recording_even_with_distinct_rows():
    f=pd.DataFrame({'recording_id':['a','a','b','c']})
    with pytest.raises(AssertionError):guard_partition(f,np.array([0,2,3]),np.array([1]),[(np.array([0,2]),np.array([3])),(np.array([3]),np.array([0,2]))])


def test_stacker_never_uses_outer_test_labels():
    rng=np.random.default_rng(1);meta=rng.uniform(size=(80,2));y=(meta[:,1]>.5).astype(int)
    train=np.arange(60);test=np.arange(60,80);plan=[(train[train%3!=i],train[train%3==i]) for i in range(3)]
    settings={'C':1.,'solver':'lbfgs','max_iter':2000}
    a=fit_stacker(meta,y,train,plan,meta[test],settings)
    poisoned=y.copy();poisoned[test]=1-poisoned[test]
    b=fit_stacker(meta,poisoned,train,plan,meta[test],settings)
    np.testing.assert_array_equal(a[0],b[0]);assert a[2]==b[2]


def test_complementarity_cells_and_oracle_are_label_dependent_diagnostic():
    y=np.array([0,1,1,0]);v={'hard':np.array([0,1,0,1]),'p':np.array([.1,.8,.3,.7])};s={'hard':np.array([0,0,1,1]),'p':np.array([.2,.3,.9,.8])}
    r=complement(y,v,s,np.ones(4,bool))
    assert [r[k] for k in ['both_correct','both_wrong','visual_only_correct','sensor_only_correct']]==[1,1,1,1]
    assert r['oracle_correct']==3
    failures=complement(y,v,s,y==1);assert failures['oracle_correct']==2 and failures['both_correct']==0


def test_incremental_gate_does_not_require_standalone_visual_gate():
    c=json.loads(Path('configs/reassemble/section1b.json').read_text())
    delta={'AUPRC':{'estimate':.02,'lower_95':.003,'upper_95':.04},'AUROC':{'estimate':0.,'lower_95':-.005,'upper_95':.01}}
    folds=[{'AUPRC':.01}]*5
    g=decide(c,delta,folds,folds,10,.01,.05)
    assert g['decision']=='FUSION GO' and not g['old_unimodal_intersection_union_gate_applied']
    delta['AUPRC']['lower_95']=-.01
    assert decide(c,delta,folds,folds,10,.01,.05)['decision']=='FUSION CONDITIONAL'
    assert decide(c,delta,folds,folds,0,0,.05)['decision']=='FUSION NO-GO'


def test_material_auc_uncertainty_blocks_go_even_with_positive_AP():
    c=json.loads(Path('configs/reassemble/section1b.json').read_text())
    d={'AUPRC':{'estimate':.02,'lower_95':.01,'upper_95':.03},'AUROC':{'estimate':-.02,'lower_95':-.04,'upper_95':0.}}
    assert decide(c,d,[{'AUPRC':.02}]*5,[{'AUPRC':.02}]*5,10,.1,.05)['decision']=='FUSION CONDITIONAL'


def test_full_admissibility_report_synthetic_run(tmp_path,monkeypatch):
    import copy
    from reassemble.section1b_report import assess
    c=json.loads(Path('configs/reassemble/section1b.json').read_text())
    monkeypatch.chdir(tmp_path);c=copy.deepcopy(c);c.update(run_dir='run',section1_run='old',bootstrap_replicates=20)
    for p in ['run/stacking','run/sensor_controls/predictions','old/predictions','artifacts/reassemble/reports','docs/reassemble']:Path(p).mkdir(parents=True,exist_ok=True)
    y=np.tile([0,0,0,0,1,1,1,1],20);n=len(y);fold=np.arange(n)%5
    frame=pd.DataFrame({'failure':y,'recording_id':np.repeat([str(i) for i in range(n//4)],4),'action':['pick','insert','remove','place']*(n//4)})
    sensor=np.where(y,.8,.2);sensor[np.arange(n)%11==0]=1-sensor[np.arange(n)%11==0]
    visual=np.where(y,.75,.25);visual[np.arange(n)%13==0]=1-visual[np.arange(n)%13==0]
    for name,p in [('sensor_statistics',sensor),('rtdetr',visual)]:np.savez('old/predictions/'+name+'_perm00.npz',p=p,hard=p>=.5,y=y,fold=fold)
    p=np.where(y,.9,.1);np.savez('run/stacking/oof.npz',p=p,hard=p>=.5,y=y,fold=fold)
    for i in range(5):Path(f'run/stacking/outer{i}.json').write_text(json.dumps({'stacker':{'coefficient':[1,1]}}))
    for i in range(1,20):Path(f'run/sensor_controls/predictions/sensor_statistics_perm{i:02d}.json').write_text(json.dumps({'permutation':i,'AUROC':.5,'AP':.5,'changed_labels':40}))
    assess(c,frame)
    text=Path('artifacts/reassemble/reports/SECTION_1B_FUSION_ADMISSIBILITY_HANDOFF.md').read_text()
    assert all('## '+str(i)+'.' in text for i in range(1,14))
    r=json.loads(Path('run/assessment/results.json').read_text())
    assert r['complementarity']['failures']['segments']==int(y.sum())
    assert not r['gate']['old_unimodal_intersection_union_gate_applied']
