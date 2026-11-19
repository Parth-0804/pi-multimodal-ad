"""Compose existing REASSEMBLE/MSM heads and OOF fusion; no framework copy."""
import json
import sys
import time
from pathlib import Path
import joblib
import numpy as np
import torch
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.utils.class_weight import compute_sample_weight

sys.path[:0]=['src','MSM/99_preserved_previous_work/MILLING_DATASET/source']
from msm.models import (fit_visual,predict_visual,SensorClassifier,StaticF2,MillingVisual)
from reassemble.section1_models import Standardizer
from reassemble.section2_models import DecisionGate,logit
from external_eval.io import write_json,sha,utc
from external_eval.data import TRAIN_VIEWS


def restore_logistic(state):
    model=LogisticRegression(C=1,solver='lbfgs',max_iter=2000)
    model.coef_=np.asarray(state['coef'],float);model.intercept_=np.asarray(state['intercept'],float)
    model.classes_=np.array([0,1]);model.n_features_in_=model.coef_.shape[1]
    return model


class BaseFit:
    def __init__(self,visual,scaler,sensor,strong,train,metadata):
        self.visual=visual;self.scaler=scaler;self.sensor=sensor;self.strong=strong;self.train=np.asarray(train,int);self.metadata=metadata
    def probabilities(self,view):
        n=len(view['visual']);p=np.full((n,2),np.nan)
        if np.all(view['availability'][:,0]):p[:,0]=predict_visual(self.visual,self.scaler,view['visual'])
        if np.all(view['availability'][:,1]):p[:,1]=self.sensor.predict(view['sensor'])
        return p
    def stronger(self,view):
        if not np.all(view['availability'][:,1]):return np.full(len(view['sensor']),np.nan)
        return self.strong.predict_proba(self.sensor.scaler.transform(view['sensor']))[:,1]


def load_base(receipt):
    info=json.loads(Path(receipt).read_text());state_path=Path(info['visual_checkpoint'])
    if sha(state_path)!=info['visual_sha256'] or (info['classical_checkpoint'] and sha(info['classical_checkpoint'])!=info['classical_sha256']):raise ValueError('Own checkpoint hash mismatch')
    saved=torch.load(state_path,map_location='cpu',weights_only=True)
    model=MillingVisual();model.load_state_dict(saved['visual']);model.eval()
    scaler=Standardizer();scaler.mean=saved['visual_mean'].numpy();scaler.std=saved['visual_std'].numpy()
    sensor=SensorClassifier();sensor.scaler.mean=saved['sensor_mean'].numpy();sensor.scaler.std=saved['sensor_std'].numpy()
    sensor.model=restore_logistic(info['sensor_logistic'])
    strong=joblib.load(info['classical_checkpoint']) if info['classical_checkpoint'] else None
    return BaseFit(model,scaler,sensor,strong,np.array(info['train_rows']),info)


def fit_base(store,train,config,seed,key,role,include_strong=True):
    train=np.asarray(train,int);root=store.root
    marker=root/'05_trained_models/visual_only'/key/role/'FIT_COMPLETE.json'
    if marker.exists():return load_base(marker)
    start=time.perf_counter();y=store.frame.target.to_numpy(int)
    if set(y[train])!={0,1}:raise ValueError('Both training classes required')
    visual,scaler,log=fit_visual(store.visual['clean'][train],y[train],config['visual'],seed)
    sensor=SensorClassifier().fit(store.sensor[train],y[train])
    options=dict(config['strong_sensor']);options.pop('kind');options.pop('sample_weight')
    strong=HistGradientBoostingClassifier(**options,random_state=seed) if include_strong else None
    if include_strong:strong.fit(sensor.scaler.transform(store.sensor[train]),y[train],sample_weight=compute_sample_weight('balanced',y[train]))
    stamp=utc().replace(':','').replace('+','').replace('.','')
    vf=root/'05_trained_models/visual_only'/key/role/stamp;sf=root/'05_trained_models/sensor_only'/key/role/stamp
    vf.mkdir(parents=True);sf.mkdir(parents=True)
    vp=vf/'visual.pt';sp=sf/'histgradient.joblib'
    torch.save({'visual':visual.state_dict(),'visual_mean':torch.tensor(scaler.mean),'visual_std':torch.tensor(scaler.std),
        'sensor_mean':torch.tensor(sensor.scaler.mean),'sensor_std':torch.tensor(sensor.scaler.std)},vp)
    if include_strong:joblib.dump(strong,sp)
    info={'nominal_case':key,'role':role,'actual_seed':seed,'train_rows':train.tolist(),
        'train_sample_ids':store.frame.iloc[train].sample_id.tolist(),'train_positive':int(y[train].sum()),
        'visual_checkpoint':str(vp),'visual_sha256':sha(vp),'classical_checkpoint':str(sp) if include_strong else None,'classical_sha256':sha(sp) if include_strong else None,
        'sensor_logistic':{'coef':sensor.model.coef_.tolist(),'intercept':sensor.model.intercept_.tolist()},
        'sensor_n_iter':sensor.model.n_iter_.tolist(),'feature_cache_signature':store.cache_identity['signature'],
        'log':log,'wall_seconds':time.perf_counter()-start,'utc':utc()}
    # Exact save/reload is assessed on deterministic TRAIN features, not test-selected examples.
    probe=train[:min(16,len(train))];view=store.view('clean',probe,train)
    direct=BaseFit(visual,scaler,sensor,strong,train,info)
    temp=vf/'fit_receipt.json';write_json(temp,info);loaded=load_base(temp)
    diff=float(np.max(abs(direct.probabilities(view)-loaded.probabilities(view))))
    tree_diff=float(np.max(abs(direct.stronger(view)-loaded.stronger(view)))) if include_strong else 0.
    if diff!=0 or tree_diff!=0:raise ValueError('Own checkpoint reload changed predictions')
    info['reload_max_abs_difference']=diff;info['strong_reload_max_abs_difference']=tree_diff
    write_json(marker,info);return direct


class QualityFit:
    def __init__(self,model,mean,std,metadata):self.model=model;self.mean=mean;self.std=std;self.metadata=metadata
    def predict(self,p,q,availability):
        # Missing branches are masked explicitly by the existing DecisionGate.
        context=np.concatenate([(q-self.mean)/self.std,availability],axis=1).astype(np.float32)
        pp=np.where(availability.astype(bool),p,.5)
        with torch.inference_mode():
            raw,weights=self.model(torch.tensor(context),torch.tensor(logit(pp)),torch.tensor(availability))
        return torch.sigmoid(raw).numpy(),weights.numpy()


def fit_quality(probabilities,qualities,y,config,seed,augmented,path):
    """Exactly one sampled corruption view/native example/epoch; fixed budget."""
    start=time.perf_counter();settings=config['quality_gate'];n=len(y)
    weights=np.array([.5]+[.5/(len(TRAIN_VIEWS)-1)]*(len(TRAIN_VIEWS)-1)) if augmented else np.r_[1.,np.zeros(len(TRAIN_VIEWS)-1)]
    q=qualities.astype(np.float64);mean=(q*weights[:,None,None]).sum((0,1))/n
    std=np.sqrt(((q-mean)**2*weights[:,None,None]).sum((0,1))/n);std=np.where(std>1e-6,std,1)
    qq=np.concatenate([((q-mean)/std).astype(np.float32),np.ones((*q.shape[:2],2),np.float32)],axis=2)
    torch.manual_seed(seed);torch.set_num_threads(1)
    model=DecisionGate(qq.shape[-1],settings['hidden'])
    opt=torch.optim.AdamW(model.parameters(),lr=settings['learning_rate'],weight_decay=settings['weight_decay'])
    p=torch.tensor(logit(probabilities));u=torch.tensor(qq);target=torch.tensor(y,dtype=torch.float32)
    rng=torch.Generator().manual_seed(seed);history=[]
    for epoch in range(settings['epochs']):
        model.train();order=torch.randperm(n,generator=rng)
        choices=torch.multinomial(torch.tensor(weights),n,replacement=True,generator=rng)
        total=0.
        for indices in order.split(settings['batch_size']):
            opt.zero_grad(set_to_none=True);context=u[choices[indices],indices]
            raw,_=model(context,p[choices[indices],indices],context[:,-2:])
            loss=torch.nn.functional.binary_cross_entropy_with_logits(raw,target[indices])
            if not torch.isfinite(loss):raise ValueError('Nonfinite quality-gate loss')
            loss.backward()
            if any(v.grad is None or not torch.isfinite(v.grad).all() for v in model.parameters()):raise ValueError('Gate gradient failure')
            torch.nn.utils.clip_grad_norm_(model.parameters(),1.);opt.step();total+=float(loss.detach())*len(indices)
        history.append(total/n)
    model.eval();path.parent.mkdir(parents=True,exist_ok=True)
    torch.save({'state':model.state_dict(),'mean':torch.tensor(mean,dtype=torch.float32),'std':torch.tensor(std,dtype=torch.float32),
        'context_width':qq.shape[-1],'hidden':settings['hidden'],'seed':seed},path)
    fit=QualityFit(model,mean.astype(np.float32),std.astype(np.float32),{'seed':seed,'augmented':augmented,'loss_by_epoch':history,
        'wall_seconds':time.perf_counter()-start,'checkpoint':str(path),'sha256':sha(path)})
    saved=torch.load(path,map_location='cpu',weights_only=True);restored=DecisionGate(saved['context_width'],saved['hidden']);restored.load_state_dict(saved['state']);restored.eval()
    other=QualityFit(restored,saved['mean'].numpy(),saved['std'].numpy(),{})
    available=np.ones((min(16,n),2),np.float32)
    a=fit.predict(probabilities[0,:len(available)],qualities[0,:len(available)],available)[0]
    b=other.predict(probabilities[0,:len(available)],qualities[0,:len(available)],available)[0]
    if not np.array_equal(a,b):raise ValueError('Quality checkpoint reload mismatch')
    fit.metadata['reload_max_abs_difference']=float(np.max(abs(a-b)))
    return fit


def fit_fusions(frame,bank,qualities,train,provenance,config,seed,root):
    y=frame.target.to_numpy(int);ids=frame.iloc[train].sample_id.tolist();groups=frame.iloc[train].group_id.tolist()
    if bank.shape!=(len(TRAIN_VIEWS),len(frame),2) or not np.isfinite(bank[:,train]).all():raise ValueError('OOF bank incomplete')
    if np.any((bank[:,train]<0)|(bank[:,train]>1)) or not np.isfinite(qualities[:,train]).all():raise ValueError('Invalid OOF probability/quality values')
    outside=np.setdiff1d(np.arange(len(frame)),train)
    if np.isfinite(bank[:,outside]).any():raise ValueError('Outer rows entered stacking bank')
    result={}
    result['F2']=StaticF2().fit(bank[0,train],y[train],ids,groups,provenance)
    # Original F2 is unchanged. This explicitly named control uses the same extra
    # corruption exposure as QG_aug, with total weight one per native example.
    pp=bank[:,train].reshape(-1,2);yy=np.tile(y[train],len(TRAIN_VIEWS))
    weights=np.repeat(np.array([.5]+[.5/(len(TRAIN_VIEWS)-1)]*(len(TRAIN_VIEWS)-1)),len(train))
    augmented=StaticF2();augmented.model=LogisticRegression(C=1,class_weight=None,solver='lbfgs',max_iter=2000,random_state=0).fit(pp,yy,sample_weight=weights)
    result['F2_aug']=augmented
    for name in ['F2','F2_aug']:
        write_json(root/(name+'.json'),{'model':name,'coef':result[name].model.coef_.tolist(),'intercept':result[name].model.intercept_.tolist(),
            'native_train_ids':ids,'source':'group-OOF only','newly_fitted':True,'sample_weights':weights.tolist() if name.endswith('aug') else None})
    for name,aug in [('QG_clean',False),('QG_aug',True)]:
        fit=fit_quality(bank[:,train],qualities[:,train],y[train],config,seed,aug,root/(name+'.pt'))
        result[name]=fit;write_json(root/(name+'.json'),fit.metadata)
    return result


def predictions(fit,fusions,view,prevalence):
    p=fit.probabilities(view);avail=view['availability'];n=len(p)
    results={'prevalence':np.full(n,prevalence),'sensor_logistic':p[:,1],'sensor_histgradient':fit.stronger(view),'visual':p[:,0]}
    both=np.all(avail==1,axis=1);one=~both
    average=np.empty(n)
    if both.any():average[both]=p[both].mean(1)
    if one.any():average[one]=np.nansum(p[one],axis=1)
    results['averaging']=average
    for name,model in fusions.items():
        values=np.empty(n)
        if both.any():
            if name.startswith('F2'):values[both]=model.predict(p[both])
            else:values[both]=model.predict(p[both],view['quality'][both],avail[both])[0]
        # Explicit available-branch fallback, separately identified in prediction
        # records. Static F2 never sees an invented missing-branch probability.
        if one.any():values[one]=np.nansum(p[one],axis=1)
        results[name]=values
    return results,p
