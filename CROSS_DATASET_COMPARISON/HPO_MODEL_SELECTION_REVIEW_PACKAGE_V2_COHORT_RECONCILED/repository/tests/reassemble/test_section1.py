import copy
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import torch
from reassemble.section1_features import statistics,cohort
from reassemble.section1_models import Standardizer,permute_labels,verify_splits,calibrate,SensorHead,VisualHead


def test_holdout_extremes_cannot_change_training_scaler():
    train=np.array([[[1.,np.nan],[3.,4.]],[[5.,6.],[7.,8.]]])
    scaler=Standardizer().fit(train);before=scaler.mean.copy()
    held=np.full((1,2,2),1e9);scaler.transform(held)
    np.testing.assert_array_equal(scaler.mean,before)
    assert scaler.mean.tolist()==[4.,6.]
    assert np.isfinite(scaler.transform(train)).all()
    assert scaler.transform(train)[0,0,1]==0


def test_statistics_linear_ramp_slope_and_constant():
    x=np.stack([np.linspace(2,5,512),np.ones(512)],axis=1)
    a=statistics(x).reshape(10,2)
    np.testing.assert_allclose(a[-1],[3,0],atol=1e-5)
    np.testing.assert_allclose(a[7],[3,0],atol=1e-5)


def test_permutation_preserves_recording_action_prevalence_and_is_reproducible():
    f=pd.DataFrame({'recording_id':['a']*8+['b']*8,'action':['pick']*4+['insert']*4+['pick']*4+['insert']*4,'start':np.arange(16),'segment_id':list(map(str,range(16))),'failure':[0,0,0,1]*4})
    y=permute_labels(f,15);np.testing.assert_array_equal(y,permute_labels(f,15))
    assert np.any(y!=f.failure)
    for _,r in f.groupby(['recording_id','action']):assert y[r.index].sum()==r.failure.sum()


def test_frozen_split_and_cohort_reject_recording_leakage():
    config=json.loads(Path('configs/reassemble/section1.json').read_text())
    f=cohort(config);s=json.loads(Path(config['splits']).read_text());verify_splits(f,s)
    broken=copy.deepcopy(s);broken['folds'][0]['test_recordings'].append(broken['folds'][0]['train_recordings'][0])
    with pytest.raises(AssertionError):verify_splits(f,broken)


def test_calibration_predicts_without_assessment_targets():
    logits=np.r_[np.linspace(-3,-1,20),np.linspace(1,3,20)];y=np.r_[np.zeros(20),np.ones(20)]
    p,t,meta=calibrate(logits,y,np.array([-2.,2.]))
    assert p[0]<t<p[1] and meta['coefficient']>0


def test_patchtst_and_visual_expose_128_embeddings_and_gradients():
    torch.set_num_threads(2)
    config=json.loads(Path('configs/reassemble/section1.json').read_text())
    for model,x in [(SensorHead(2,config),torch.zeros(2,512,2)),(VisualHead(8,config),torch.zeros(2,8))]:
        score,z=model(x,torch.ones_like(x,dtype=torch.bool));assert z.shape==(2,128) and score.shape==(2,)
        score.sum().backward();assert model.classifier.weight.grad is not None


def test_cluster_weights_equal_explicit_recording_replication():
    from reassemble.section1_report import metrics
    y=np.array([0,1,1,0,0,1]);p=np.array([.1,.6,.3,.4,.2,.9]);h=(p>=.5).astype(int)
    w=np.array([2,2,0,0,3,3]);ix=np.repeat(np.arange(6),w)
    np.testing.assert_allclose(metrics(y,p,h,w),metrics(y[ix],p[ix],h[ix]))


def test_metrics_match_sklearn_secondary_definitions():
    from reassemble.section1_report import metrics
    from sklearn.metrics import f1_score,balanced_accuracy_score,brier_score_loss,precision_score,recall_score
    y=np.array([0,0,0,1,1,1]);p=np.array([.2,.6,.1,.8,.7,.3]);h=(p>=.5).astype(int)
    m=metrics(y,p,h)
    np.testing.assert_allclose(m[2:7],[balanced_accuracy_score(y,h),f1_score(y,h,average='macro'),recall_score(y,h),precision_score(y,h),brier_score_loss(y,p)])


def test_report_end_to_end_positive_control_and_constant_error_correlation(tmp_path,monkeypatch):
    from reassemble import section1_report as report
    monkeypatch.chdir(tmp_path)
    run=Path('run');(run/'predictions').mkdir(parents=True);(run/'features').mkdir()
    Path('artifacts/reassemble/reports').mkdir(parents=True)
    y=np.tile([0,0,0,0,1,1,1,1],10)
    f=pd.DataFrame({'recording_id':np.repeat([str(i) for i in range(20)],4),'action':['pick','insert','remove','place']*20,'failure':y})
    monkeypatch.setattr(report,'cohort',lambda config:f)
    (run/'pretrained_model.json').write_text('{}')
    (run/'features/a.json').write_text(json.dumps({'channel_names':['synthetic:0']}))
    for name in report.MODELS:
        p=np.where(y,.9,.1) if name in ['rtdetr','patchtst','sensor_statistics'] else np.full(80,.5)
        np.savez(run/'predictions'/f'{name}_perm00.npz',y=y,p=p,hard=p>.5,fold=np.arange(80)%5)
        (run/'predictions'/f'{name}_perm00.json').write_text(json.dumps({'folds':[{'fold':i} for i in range(5)]}))
        if name in ['rtdetr','patchtst']:
            for i in range(1,20):(run/'predictions'/f'{name}_perm{i:02d}.json').write_text(json.dumps({'permutation':i,'AP':.5,'AUROC':.5,'changed_labels':40}))
    report.assess({'run_dir':str(run),'seed':12,'bootstrap_replicates':20,'permutations':19,'permutation_scheme':'synthetic test'})
    r=json.loads((run/'assessment/results.json').read_text())
    assert r['modality_gates']=={'rtdetr':'PASS','patchtst':'PASS'}
    assert r['complementarity']['all']['error_correlation'] is None
    text=Path('artifacts/reassemble/reports/SECTION_1_UNIMODAL_HANDOFF.md').read_text()
    assert text.rstrip().endswith('FUSION GO — VISUAL AND SENSOR MODALITIES BOTH DEMONSTRATE SIGNAL')
    assert all('## '+letter+'.' in text for letter in 'ABCDEFGHIJKLMN')
