"""Synthetic regression checks; no raw data are copied into fixtures."""
import copy
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import torch

sys.path[:0]=['src','MSM/99_preserved_previous_work/MILLING_DATASET/source','CROSS_DATASET_COMPARISON/src']
from external_eval.data import statistics,sensor_quality,rng_for,TRAIN_VIEWS
from external_eval.features import altered,quality
from external_eval.evaluate import metrics
from external_eval.evaluate import execute_case
from external_eval.models import fit_base,predictions,fit_quality,fit_fusions
from external_eval.protocol import core
from external_eval.io import write_json,sha,extract_verified


def test_fixed_statistics_channel_major_and_finite_gate():
    x=np.array([[1.,4.],[2.,5.],[3.,6.]])
    v=statistics(x)
    assert v.shape==(12,) and v[0]==2 and v[1]==pytest.approx(np.sqrt(2/3)) and v[5]==2 and v[6]==5
    with pytest.raises(ValueError):statistics(np.array([[float('nan')]]))
    assert sensor_quality(v[None]).shape==(1,4)


def test_pixel_corruption_preserves_padding_and_does_not_modify_source():
    rng=np.random.default_rng(42);x=np.zeros((30,30,3),np.uint8);x[5:25,7:23]=rng.integers(0,256,(20,16,3),dtype=np.uint8)
    before=x.copy();box=(7,5,16,20)
    for kind,value in [('gaussian_blur',2),('brightness_contrast',[.5,.5]),('partial_occlusion',.25)]:
        changed=altered(x,box,kind,value)
        assert np.array_equal(x,before) and not np.array_equal(changed,x)
        assert not changed[:5].any() and not changed[25:].any() and not changed[:,:7].any()
        assert np.isfinite(quality(changed,box)).all()


def test_corruption_randomness_deterministic_and_severity_nested():
    a=rng_for(42,'frame_dropout','unitA').permutation(16);b=rng_for(42,'frame_dropout','unitA').permutation(16)
    assert np.array_equal(a,b) and set(a[12:])<=set(a[8:])<=set(a[4:])
    assert not np.array_equal(a,rng_for(42,'frame_dropout','unitB').permutation(16))


def test_metric_known_values_and_undefined_class_handling():
    m=metrics([0,1,0,1],[.1,.4,.35,.8])
    assert m['AP']==1 and m['AUROC']==1 and (m['TN'],m['FP'],m['FN'],m['TP'])==(2,0,1,1)
    assert m['specificity']==1 and m['recall']==.5
    assert metrics([0,0],[.1,.2])['AUROC'] is None
    with pytest.raises(ValueError):metrics([0,1],[.1,np.nan])


def test_atomic_json_idempotence_and_mismatch_protection(tmp_path):
    p=tmp_path/'proof.json';write_json(p,{'a':1});before=sha(p);write_json(p,{'a':1})
    assert sha(p)==before
    with pytest.raises(ValueError):write_json(p,{'a':2})


class FakeStore:
    def __init__(self,root):
        self.root=root;self.config=core();self.config['visual']['epochs']=2;self.config['strong_sensor']['max_iter']=3
        rng=np.random.default_rng(41);n=24
        self.frame=pd.DataFrame({'sample_id':[f'id{i}' for i in range(n)],'interval_id':[f'id{i}' for i in range(n)],
            'target':np.arange(n)%2,'group_id':np.repeat([f'g{k}' for k in range(6)],4)})
        self.index={s:i for i,s in enumerate(self.frame.sample_id)}
        self.sensor=rng.normal(size=(n,12)).astype(np.float32);self.visual={'clean':rng.normal(size=(n,896)).astype(np.float32)}
        self.cache_identity={'signature':'tiny-synthetic'}
    def view(self,name,rows,train):
        return {'visual':self.visual['clean'][rows],'sensor':self.sensor[rows],
            'availability':np.ones((len(rows),2),np.float32),'quality':np.zeros((len(rows),10),np.float32)}


def test_real_head_gradients_reload_and_unimodal_missing_fallback(tmp_path):
    torch.set_num_threads(1);s=FakeStore(tmp_path);train=np.arange(16)
    fit=fit_base(s,train,s.config,42,'synthetic','refit')
    assert fit.metadata['log']['all_head_parameters_nonzero_gradient']
    assert fit.metadata['reload_max_abs_difference']==0 and fit.metadata['strong_reload_max_abs_difference']==0
    view=s.view('clean',np.arange(16,24),train);view['availability'][:,0]=0
    values,p=predictions(fit,{},view,.5)
    assert np.isnan(values['visual']).all() and np.array_equal(values['averaging'],values['sensor_logistic'])
    assert np.isnan(p[:,0]).all() # no fabricated visual probability


def test_outer_labels_cannot_change_fitted_base_or_probabilities(tmp_path):
    s=FakeStore(tmp_path/'a');a=fit_base(s,np.arange(16),s.config,42,'fit','final')
    z=FakeStore(tmp_path/'b');z.frame.loc[16:,'target']=1-z.frame.loc[16:,'target']
    b=fit_base(z,np.arange(16),z.config,42,'fit','final')
    view=s.view('clean',np.arange(16,24),np.arange(16))
    assert np.array_equal(a.probabilities(view),b.probabilities(view))


def test_gate_exact_reload_and_single_available_branch(tmp_path):
    cfg=core();cfg['quality_gate']['epochs']=2
    rng=np.random.default_rng(62);p=rng.uniform(.1,.9,(8,12,2));q=rng.normal(size=(8,12,10)).astype(np.float32);y=np.arange(12)%2
    gate=fit_quality(p,q,y,cfg,42,True,tmp_path/'gate.pt')
    availability=np.tile([0.,1.],(12,1)).astype(np.float32);masked=p[0].copy();masked[:,0]=np.nan
    values,weights=gate.predict(masked,q[0],availability)
    assert np.all(weights[:,0]==0) and np.all(weights[:,1]==1)
    assert np.allclose(values,p[0,:,1],atol=1e-7) and gate.metadata['reload_max_abs_difference']==0


def test_fusion_rejects_assessment_bank_rows_before_training(tmp_path):
    n=12;f=pd.DataFrame({'sample_id':[f'x{i}' for i in range(n)],'target':np.arange(n)%2,'group_id':[f'g{i//2}' for i in range(n)]})
    bank=np.full((8,n,2),.5);q=np.zeros((8,n,10),np.float32)
    with pytest.raises(ValueError,match='Outer rows'):
        fit_fusions(f,bank,q,np.arange(8),{},core(),42,tmp_path)


def test_archive_traversal_and_links_rejected(tmp_path):
    import io,tarfile
    archive=tmp_path/'bad.tar.gz'
    with tarfile.open(archive,'w:gz') as t:
        member=tarfile.TarInfo('../escape');member.size=1;t.addfile(member,io.BytesIO(b'x'))
    with pytest.raises(ValueError,match='Unsafe'):
        extract_verified(archive,tmp_path/'out')


def test_complete_synthetic_outer_case_runs_all_models_and_resumes(tmp_path):
    s=FakeStore(tmp_path);s.dataset='MSM';s.condition='P';s.channels=['c0','c1'];s.adapter_identity={'sha256':'synthetic'}
    s.config['quality_gate']['epochs']=2
    s.frame['native_label']=s.frame.target;s.frame['direction']=np.where(s.frame.target==1,'UP','DOWN')
    (tmp_path/'06_evaluation_results/metrics').mkdir(parents=True)
    definition={'sample_ids':s.frame.sample_id.tolist(),'grouping':'group_id'}
    fold={'train':list(range(16)),'test':list(range(16,24)),
          'inner':[(list(range(8)),list(range(8,16))),(list(range(8,16)),list(range(8)))]}
    first=execute_case(s,'synthetic',definition,0,fold,42)
    assert first['status']=='COMPLETE' and len(first['models'])==9
    second=execute_case(s,'synthetic',definition,0,fold,42)
    assert first==second
    predictions=pd.read_csv(first['predictions'])
    clean=predictions[predictions.corruption=='clean']
    assert clean.groupby('model').sample_id.nunique().eq(8).all()
    assert not clean.sample_id.isin(s.frame.iloc[:16].sample_id).any()
