"""Exact probability-logistic F2 and original quality-only DecisionGate."""
import time
import numpy as np
import torch
from torch import nn

from .common import PROJECT,config,read,resolve,sha,signature,write
from .cohort import finalize
from .reference import primitives,identities
from .sensors import prepare as sensor_features
from .splits import prepare,require_oof
from .metrics import metrics,independent_check
from .training import atomic_checkpoint

QUALITY_NAMES=['mean_brightness','mean_contrast','black_fraction','laplacian_variance','adjacent_identical_fraction',
               'mean_adjacent_pixel_delta','sensor_finite_fraction','sensor_observed_channel_fraction',
               'sensor_constant_channel_fraction','sensor_large_value_fraction','sensor_adjacent_delta']


def quality_matrix(c,rows):
    bank=PROJECT/'03_preprocessing/visual_preprocessing/features'/c['run_id']/'V1'
    identity=read(bank/'COMPLETE.json');assert sha(bank/'quality.npy')==identity['quality_sha256']
    visual=np.load(bank/'quality.npy',allow_pickle=False);assert len(visual)==len(rows)
    receipt=sensor_features(c);data=np.load(resolve(receipt['path']),allow_pickle=False)
    sensors={int(e):q for e,q in zip(data['episode_ids'],data['quality'])}
    result={}
    for i,row in enumerate(rows):
        e=row['episode_index'];result[e]=np.r_[visual[i],sensors[e]].astype('float32')
    return result


def fit_gate(probabilities,quality,labels,seed,epochs=40):
    source=primitives();torch.manual_seed(seed);torch.set_num_threads(2)
    mean,std=source['standardizer'](quality)
    context=np.c_[(quality-mean)/std,np.ones((len(quality),2))].astype('float32')
    logits=np.log(np.clip(probabilities,1e-6,1-1e-6)/np.clip(1-probabilities,1e-6,1-1e-6)).astype('float32')
    model=source['DecisionGate'](context.shape[1],16)
    optimizer=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.001)
    cx=torch.from_numpy(context);lg=torch.from_numpy(logits);av=torch.ones_like(lg);y=torch.as_tensor(labels,dtype=torch.float32)
    losses=[];rng=np.random.default_rng(seed)
    for epoch in range(epochs):
        total=0
        for ix in np.array_split(rng.permutation(len(y)),max(1,int(np.ceil(len(y)/64)))):
            optimizer.zero_grad(set_to_none=True);raw,_=model(cx[ix],lg[ix],av[ix])
            loss=nn.functional.binary_cross_entropy_with_logits(raw,y[ix]);assert torch.isfinite(loss)
            loss.backward();nn.utils.clip_grad_norm_(model.parameters(),1);optimizer.step();total+=float(loss.detach())*len(ix)
        losses.append(total/len(y))
    return {'state_dict':model.state_dict(),'mean':mean.tolist(),'std':std.tolist(),'hidden':16,'width':context.shape[1],
            'epochs':epochs,'seed':seed,'loss_by_epoch':losses,'quality_names':QUALITY_NAMES,
            'source':'reassemble.section2_models.DecisionGate; F5 quality plus availability; no task/action identity',
            'augmentation_training':False}


def gate_predict(model_data,probabilities,quality,availability=None):
    source=primitives();p=np.asarray(probabilities);av=np.ones_like(p) if availability is None else np.asarray(availability)
    assert av.any(axis=1).all(),'BOTH_MODALITIES_MISSING_REQUIRES_ABSTENTION'
    mean=np.asarray(model_data['mean']);std=np.asarray(model_data['std'])
    context=np.c_[np.nan_to_num((quality-mean)/std),av].astype('float32')
    logits=np.log(np.clip(p,1e-6,1-1e-6)/np.clip(1-p,1e-6,1-1e-6)).astype('float32')
    model=source['DecisionGate'](model_data['width'],model_data['hidden']);model.load_state_dict(model_data['state_dict']);model.eval()
    with torch.inference_mode():
        raw,weights=model(torch.from_numpy(context),torch.from_numpy(logits),torch.as_tensor(av,dtype=torch.float32))
    return torch.sigmoid(raw).numpy(),weights.numpy()


def visual_root(c,condition,seed,job):
    return PROJECT/'06_training_experiments'/dict(V1='visual_frozen',V2='visual_finetuned100',V3='reassemble_transfer')[condition]/'runs'/c['run_id']/f'seed{seed}'/job['id']


def augmentation_root(c,condition,seed,outer):
    return PROJECT/'06_training_experiments/fusion_experiments/augmentation/runs'/c['run_id']/condition/f'seed{seed}'/f'outer{outer}'


def paired_records(c,condition,seed,job):
    vr=visual_root(c,condition,seed,job)
    sr=PROJECT/'06_training_experiments/sensor_baselines/runs'/c['run_id']/f'seed{seed}'/job['id']
    vi=read(vr/'COMPLETE.json');si=read(sr/'COMPLETE.json')
    assert sha(vr/'predictions.json')==vi['prediction_sha256'] and sha(sr/'predictions.json')==si['prediction_sha256']
    visual=read(vr/'predictions.json');sensor=read(sr/'predictions.json')
    assert [r['episode_index'] for r in visual]==[r['episode_index'] for r in sensor]==job['ids']['A']
    result=[]
    for v,s in zip(visual,sensor):
        assert v['label']==s['label'] and v['fit_id']==s['fit_id']==job['id']
        result.append({'episode_index':v['episode_index'],'fit_id':job['id'],'label':v['label'],
                       'visual_probability':v['probability'],'sensor_probability':s['S3_probability']})
    return result,{'visual':vi['prediction_sha256'],'sensor':si['prediction_sha256']}


def run(c=None,conditions=('V1','V2','V3')):
    c=c or config();rows=finalize(c);jobs=prepare(c);quality=quality_matrix(c,rows);source=primitives();all_receipts=[]
    for condition in conditions:
        for seed in c['seeds']:
            for outer in range(c['outer_folds']):
                root=PROJECT/'06_training_experiments/fusion_experiments/runs'/c['run_id']/condition/f'seed{seed}'/f'outer{outer}'
                if (root/'COMPLETE.json').exists():
                    receipt=read(root/'COMPLETE.json');assert sha(root/'predictions.json')==receipt['prediction_sha256']
                    all_receipts.append(receipt);continue
                train=[];lineage={};started=time.perf_counter()
                for job in jobs:
                    if job['outer']==outer and job['inner']>=0:
                        records,identity=paired_records(c,condition,seed,job);train.extend(records);lineage[job['id']]=identity
                require_oof(jobs,outer,train)
                final=next(j for j in jobs if j['outer']==outer and j['inner']==-1)
                test,testidentity=paired_records(c,condition,seed,final)
                def arrays(records):
                    return (np.asarray([[r['visual_probability'],r['sensor_probability']] for r in records],dtype='float32'),
                            np.asarray([r['label'] for r in records]),np.stack([quality[r['episode_index']] for r in records]))
                p,y,q=arrays(train);pt,yt,qt=arrays(test)
                f2=source['stacker'](p,y);gate=fit_gate(p,q,y,seed)
                neutral=fit_gate(p,np.zeros_like(q),y,seed);neutral['context_policy']='trained availability-only control; quality always zero'
                pf2=source['fused'](pt,f2);pg,weights=gate_predict(gate,pt,qt);pn,_=gate_predict(neutral,pt,np.zeros_like(qt));avg=pt.mean(1)
                root.mkdir(parents=True,exist_ok=True)
                write(root/'F2_COEFFICIENTS.json',f2);atomic_checkpoint(root/'QUALITY_GATE.pt',gate)
                atomic_checkpoint(root/'QUALITY_NEUTRAL_GATE.pt',neutral)
                write(root/'META_TRAINING_PREDICTIONS.json',train)
                predictions=[{**row,'condition':condition,'seed':seed,'outer':outer,'F1_average':float(a),
                              'F2_probability':float(b),'gate_probability':float(d),'gate_static_probability':float(n),'gate_visual_weight':float(w[0])}
                             for row,a,b,d,n,w in zip(test,avg,pf2,pg,pn,weights)]
                write(root/'predictions.json',predictions)
                reports={name:metrics(yt,pred) for name,pred in [('F1_average',avg),('F2',pf2),('quality_gate',pg),('gate_static',pn)]}
                for name,pred in [('F1_average',avg),('F2',pf2),('quality_gate',pg),('gate_static',pn)]:independent_check(yt,pred,reports[name])
                write(root/'metrics.json',reports)
                receipt={'condition':condition,'seed':seed,'outer':outer,'meta_rows':len(train),'outer_rows':len(test),
                         'group_safe_OOF_verified':True,'inner_prediction_sha256':lineage,'outer_prediction_sha256':testidentity,
                         'meta_training_sha256':sha(root/'META_TRAINING_PREDICTIONS.json'),'f2_sha256':sha(root/'F2_COEFFICIENTS.json'),
                         'gate_sha256':sha(root/'QUALITY_GATE.pt'),'prediction_sha256':sha(root/'predictions.json'),
                         'gate_static_sha256':sha(root/'QUALITY_NEUTRAL_GATE.pt'),
                         'seconds':time.perf_counter()-started,'source':identities()}
                write(root/'COMPLETE.json',receipt);all_receipts.append(receipt)
    return all_receipts
