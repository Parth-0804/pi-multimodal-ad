"""Exercise saved-model stress evaluation/abstention with tiny synthetic inputs."""
from copy import deepcopy
from types import SimpleNamespace
import joblib
import numpy as np
import torch
from sklearn.dummy import DummyClassifier
from vifailback import common,fusion,robustness,training
from vifailback.reference import primitives


class SyntheticCNN(torch.nn.Module):
    def forward(self,x):return SimpleNamespace(feature_maps=[x.mean((1,2,3),keepdim=True).expand(len(x),896,1,1)])


def test_saved_models_stresses_same_examples_and_both_missing_abstains(tmp_path,monkeypatch):
    c=common.config();c['run_id']='synthetic';c['seeds']=[42];c['outer_folds']=1
    for module in [common,fusion,robustness,training]:monkeypatch.setattr(module,'PROJECT',tmp_path)
    rows=[{'episode_index':i,'canonical_task_id':i,'label':i%2,'frame_count':32,'data':f'synthetic{i}'} for i in range(4)]
    job={'id':'outer0_final','outer':0,'inner':-1,'ids':{'T':[2,3],'A':[0,1]}}
    monkeypatch.setattr(robustness,'finalize',lambda c:rows);monkeypatch.setattr(robustness,'prepare',lambda c:[job])
    monkeypatch.setattr(robustness,'sensor_sources',lambda c:{})
    monkeypatch.setattr(robustness,'load_episode',lambda *a:(np.tile(np.linspace(0,1,32,dtype='float32')[:,None],(1,28)),np.arange(32)/25))
    monkeypatch.setattr(robustness,'training_scale',lambda *a:np.ones(28,dtype='float32'))
    monkeypatch.setattr(robustness,'pixels',lambda c,row:torch.ones(3,16,3,8,8)*.5)
    model=primitives()['PhaseVisual'](None,896,np.zeros(896),np.ones(896),False)
    monkeypatch.setattr(robustness,'make',lambda *a:deepcopy(model));monkeypatch.setattr(robustness,'backbone',lambda *a:SyntheticCNN())
    scenarios=[s for s in robustness.SCENARIOS if s['name'] in ['clean','missing_channels_0.5','visual_missing','both_missing']]
    monkeypatch.setattr(robustness,'SCENARIOS',scenarios)
    vr=fusion.visual_root(c,'V1',42,job);vr.mkdir(parents=True)
    training.atomic_checkpoint(vr/'BEST_MODEL.pt',{'model':model.state_dict()})
    common.write(vr/'COMPLETE.json',{'best_checkpoint_sha256':common.sha(vr/'BEST_MODEL.pt')})
    calibrator={'coefficient':[0.],'intercept':0.};common.write(vr/'CALIBRATOR.json',calibrator)
    sr=tmp_path/'06_training_experiments/sensor_baselines/runs/synthetic/seed42/outer0_final';sr.mkdir(parents=True)
    s3={'mean':[0.]*280,'std':[1.]*280,'raw':{'coefficient':[0.]*280,'intercept':0.},'calibrator':calibrator}
    common.write(sr/'S3_MODEL.json',s3)
    dummy=DummyClassifier(strategy='prior').fit(np.zeros((2,280)),[0,1]);joblib.dump(dummy,sr/'S2_MODEL.joblib')
    common.write(sr/'S2_SELECTION_AND_CALIBRATION.json',{'calibrator':calibrator})
    common.write(sr/'COMPLETE.json',{'S3_checkpoint_sha256':common.sha(sr/'S3_MODEL.json'),'S2_checkpoint_sha256':common.sha(sr/'S2_MODEL.joblib')})
    fr=tmp_path/'06_training_experiments/fusion_experiments/runs/synthetic/V1/seed42/outer0';fr.mkdir(parents=True)
    common.write(fr/'F2_COEFFICIENTS.json',{'coefficient':[0.,0.],'intercept':0.})
    gate=fusion.fit_gate(np.ones((2,2),dtype='float32')*.5,np.zeros((2,11),dtype='float32'),np.asarray([0,1]),42,epochs=2)
    for name in ['QUALITY_GATE.pt','QUALITY_NEUTRAL_GATE.pt']:training.atomic_checkpoint(fr/name,gate)
    common.write(fr/'COMPLETE.json',{'f2_sha256':common.sha(fr/'F2_COEFFICIENTS.json'),'gate_sha256':common.sha(fr/'QUALITY_GATE.pt'),'gate_static_sha256':common.sha(fr/'QUALITY_NEUTRAL_GATE.pt')})
    common.write(fr/'predictions.json',[{'episode_index':i,'visual_probability':.5,'sensor_probability':.5,'F2_probability':.5,'gate_probability':.5,'gate_static_probability':.5} for i in [0,1]])
    robustness.run(c,('V1',),device='cpu')
    root=tmp_path/'07_robustness_experiments/combined_corruption/runs/synthetic/V1/seed42/outer0'
    reports=common.read(root/'metrics.json');assert reports['both_missing']=={'eligible':2,'scored':0,'abstained':2}
    assert reports['visual_missing']['hardcoded_fallback_examples']==2
    assert reports['clean']['visual_probability']['episodes']==2
    predictions=common.read(root/'predictions.json');assert len(predictions)==len(scenarios)*2
    robustness.run(c,('V1',),device='cpu')  # Complete results are verified and reused.
