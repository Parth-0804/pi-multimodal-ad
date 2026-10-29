"""Matched meta augmentation must use genuine inner-held-out checkpoints/IDs."""
from copy import deepcopy
from types import SimpleNamespace
import numpy as np
import torch
from vifailback import augmentation,common,fusion,training
from vifailback.reference import primitives
from vifailback.splits import plans


class SyntheticCNN(torch.nn.Module):
    def forward(self,x):return SimpleNamespace(feature_maps=[x.mean((1,2,3),keepdim=True).expand(len(x),896,1,1)])


def test_augmented_meta_rows_are_not_new_independent_examples(tmp_path,monkeypatch):
    c=common.config();c['run_id']='synthetic';c['seeds']=[42];c['outer_folds']=1
    for module in [common,fusion,augmentation,training]:monkeypatch.setattr(module,'PROJECT',tmp_path)
    rows=[{'episode_index':2*g+y,'canonical_task_id':g,'label':y,'frame_count':32,'data':f'synthetic{2*g+y}'} for g in range(33) for y in [0,1]]
    jobs=plans(rows,42);lookup={r['episode_index']:r for r in rows}
    monkeypatch.setattr(augmentation,'finalize',lambda c:rows);monkeypatch.setattr(augmentation,'prepare',lambda c:jobs)
    monkeypatch.setattr(augmentation,'quality_matrix',lambda *a:{r['episode_index']:np.zeros(11,dtype='float32') for r in rows})
    monkeypatch.setattr(augmentation,'sensor_sources',lambda c:{})
    monkeypatch.setattr(augmentation,'load_episode',lambda *a:(np.tile(np.linspace(0,1,32,dtype='float32')[:,None],(1,28)),np.arange(32)/25))
    monkeypatch.setattr(augmentation,'training_scale',lambda *a:np.ones(28,dtype='float32'))
    monkeypatch.setattr(augmentation,'pixels',lambda *a:torch.ones(3,16,3,8,8)*.5)
    model=primitives()['PhaseVisual'](None,896,np.zeros(896),np.ones(896),False)
    monkeypatch.setattr(augmentation,'make',lambda *a:deepcopy(model));monkeypatch.setattr(augmentation,'backbone',lambda *a:SyntheticCNN())
    clean=[];cal={'coefficient':[0.],'intercept':0.}
    for job in [j for j in jobs if j['outer']==0 and j['inner']>=0]:
        vr=fusion.visual_root(c,'V1',42,job);vr.mkdir(parents=True)
        training.atomic_checkpoint(vr/'BEST_MODEL.pt',{'model':model.state_dict()});common.write(vr/'CALIBRATOR.json',cal)
        common.write(vr/'COMPLETE.json',{'best_checkpoint_sha256':common.sha(vr/'BEST_MODEL.pt')})
        sr=tmp_path/'06_training_experiments/sensor_baselines/runs/synthetic/seed42'/job['id'];sr.mkdir(parents=True)
        common.write(sr/'S3_MODEL.json',{'mean':[0.]*280,'std':[1.]*280,'raw':{'coefficient':[0.]*280,'intercept':0.},'calibrator':cal})
        common.write(sr/'COMPLETE.json',{'S3_checkpoint_sha256':common.sha(sr/'S3_MODEL.json')})
        clean += [{'episode_index':e,'fit_id':job['id'],'label':lookup[e]['label'],'visual_probability':.5,'sensor_probability':.5} for e in job['ids']['A']]
    final=next(j for j in jobs if j['outer']==0 and j['inner']==-1)
    fr=tmp_path/'06_training_experiments/fusion_experiments/runs/synthetic/V1/seed42/outer0';fr.mkdir(parents=True)
    common.write(fr/'META_TRAINING_PREDICTIONS.json',clean)
    common.write(fr/'predictions.json',[{'episode_index':e,'fit_id':final['id'],'label':lookup[e]['label'],'visual_probability':.5,'sensor_probability':.5,'seed':42,'outer':0,'condition':'V1'} for e in final['ids']['A']])
    common.write(fr/'COMPLETE.json',{'meta_training_sha256':common.sha(fr/'META_TRAINING_PREDICTIONS.json'),'prediction_sha256':common.sha(fr/'predictions.json')})
    augmentation.run(c,'V1',device='cpu')
    out=fusion.augmentation_root(c,'V1',42,0);receipt=common.read(out/'COMPLETE.json')
    assert receipt['independent_native_meta_episodes']==44 and receipt['clean_and_augmented_meta_records']==88
    assert receipt['gate_epochs']==20 and len(common.read(out/'predictions.json'))==22
    assert len(common.read(out/'AUGMENTED_OOF_RECORDS.json'))==44
    augmentation.run(c,'V1',device='cpu')
