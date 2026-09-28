"""Exposure-matched frozen-branch fusion; training and assessment banks are separate."""
from pathlib import Path
import json
import hashlib
import time
import numpy as np
import torch
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score,roc_auc_score
from threadpoolctl import threadpool_limits
from reassemble.section1_features import cohort,sha
from reassemble.section1b import index_plan,choose_threshold
from reassemble.section1_models import sigmoid
from reassemble.section2_data import quality_features
from reassemble.section2_models import DecisionGate,logit
from .models import AnchoredAdjustment,modality_fallback
from .anchored import anchor
from .common import config,read,write,storage,progress,identity

VIEW_WEIGHTS=np.array([.5]+[.0625]*8)

def pack(c,frame,quality,actions,name,split):
    root=Path(c['run_dir'])/'04_corruption_training';meta=read(root/'branches'/(name+'.json'));rows=np.array(meta['test_rows'])
    c2=read(c['section2_config']);original=Path(c2['section1b_run'])/'stacking'
    if '_sub' in name:
        with np.load(Path(c2['run_dir'])/'inputs'/(name+'.npz')) as z:clean=z['probabilities']
    elif '_inner' in name:
        with np.load(original/(name+'.npz')) as z:clean=z['probabilities']
    else:
        with np.load(original/(name+'.npz')) as z:clean=z['test_branch_probabilities']
    probabilities=[clean];contexts=[np.concatenate([actions[rows],quality[rows],np.ones((len(rows),2))],axis=1)];names=['clean']
    for modality,folder,offset in [(0,'visual_probabilities',4),(1,'sensor_bank',10)]:
        with np.load(root/folder/(name+'.npz')) as z:
            assert np.array_equal(z['rows'],rows)
            for i,key in enumerate(z['names']):
                if not key.startswith(split+'_'):continue
                values=clean.copy();values[:,modality]=z['p'][i];context=contexts[0].copy();context[:,offset:offset+z['quality'].shape[-1]]=z['quality'][i]
                probabilities.append(values);contexts.append(context);names.append(str(key))
    if split=='test':
        for missing,label in [(0,'test_missing_visual'),(1,'test_missing_sensor')]:
            values=clean.copy();values[:,missing]=0;context=contexts[0].copy();context[:,40+missing]=0
            context[:,4:10] = np.nan if missing==0 else context[:,4:10]
            context[:,10:40] = np.nan if missing==1 else context[:,10:40]
            probabilities.append(values);contexts.append(context);names.append(label)
    else:assert len(names)==9,names
    thresholds=np.array([meta['visual_calibration']['threshold'],meta['sensor_calibration']['threshold']])
    return dict(rows=rows,p=np.stack(probabilities).astype(np.float64),u=np.stack(contexts).astype(np.float32),names=np.array(names),branch_thresholds=np.broadcast_to(thresholds,(len(rows),2)).copy())

def join(packs):
    names=packs[0]['names'];assert all(np.array_equal(p['names'],names) for p in packs)
    rows=np.concatenate([p['rows'] for p in packs]);assert len(np.unique(rows))==len(rows);order=np.argsort(rows)
    return dict(rows=rows[order],p=np.concatenate([p['p'] for p in packs],axis=1)[:,order],u=np.concatenate([p['u'] for p in packs],axis=1)[:,order],names=names,branch_thresholds=np.concatenate([p['branch_thresholds'] for p in packs])[order])

def normalize(train,assessment,augmented):
    quality=train['u'][:,:,4:40].astype(float);weights=VIEW_WEIGHTS[:,None,None] if augmented else np.eye(9)[0,:,None,None]
    valid=np.isfinite(quality);mass=(valid*weights).sum((0,1));mean=np.nansum(quality*weights,axis=(0,1))/np.maximum(mass,1)
    std=np.sqrt(np.nansum((quality-mean)**2*weights,axis=(0,1))/np.maximum(mass,1));std=np.where(np.isfinite(std)&(std>1e-6),std,1)
    def transform(pack):
        u=pack['u'].copy();u[:,:,4:40]=np.nan_to_num((u[:,:,4:40]-mean)/std,nan=0,posinf=0,neginf=0)
        for col,slice_ in [(0,slice(4,10)),(1,slice(10,40))]:
            missing=u[:,:,40+col]==0;u[:,:,slice_][missing]=0
        return u
    return transform(train),transform(assessment),mean.astype(np.float32),std.astype(np.float32)

def selection_score(labels,probability):
    scores=np.array([average_precision_score(labels,p) for p in probability]);assert len(scores)==9
    return float(.5*scores[0]+.25*scores[1:5].mean()+.25*scores[5:9].mean())

def fit(path,kind,augmented,train,test,y,seed,penalty=0.,epochs=None):
    path=Path(path);path=path.parent/path.name.replace('.','p');path.parent.mkdir(parents=True,exist_ok=True)
    c=config();options=c['adaptation'];signature=hashlib.sha256(json.dumps(dict(code=sha(__file__),models=sha(Path(__file__).with_name('models.py')),train=train['rows'].tolist(),test=test['rows'].tolist(),kind=kind,augmented=augmented,seed=seed,penalty=penalty,epochs=epochs,configuration=c),sort_keys=True).encode()).hexdigest()
    if path.with_suffix('.json').exists():
        info=read(path.with_suffix('.json'));assert info['signature']==signature
        with np.load(path.with_suffix('.npz')) as z:return {k:z[k] for k in z.files},info
    storage();start=time.perf_counter();torch.manual_seed(seed)
    assert not set(train['rows'])&set(test['rows'])
    yt=y[train['rows']];yv=y[test['rows']]
    if kind=='F2':
        pp=train['p'].reshape(-1,2) if augmented else train['p'][0];yy=np.tile(yt,9) if augmented else yt
        ww=np.repeat(VIEW_WEIGHTS,len(yt)) if augmented else np.ones(len(yt))
        assert np.allclose(ww.reshape(-1,len(yt)).sum(0),1)
        with threadpool_limits(limits=16):model=LogisticRegression(C=1,solver='lbfgs',max_iter=2000,random_state=0).fit(pp,yy,sample_weight=ww)
        probabilities=model.predict_proba(test['p'].reshape(-1,2))[:,1].reshape(test['p'].shape[:2]);weights=np.broadcast_to(model.coef_[0],(*probabilities.shape,2)).copy()
        joblib.dump(model,path.with_suffix('.joblib'))
        info=dict(signature=signature,kind=kind,augmented=augmented,seed=seed,best_epoch=None,history=[],coefficient=model.coef_[0].tolist(),intercept=float(model.intercept_[0]),seconds=time.perf_counter()-start,checkpoint=identity(path.with_suffix('.joblib')))
    else:
        tr_u,te_u,mean,std=normalize(train,test,augmented);tp=torch.tensor(train['p'],dtype=torch.float32);tu=torch.tensor(tr_u);vp=torch.tensor(test['p'],dtype=torch.float32);vu=torch.tensor(te_u);target=torch.tensor(yt,dtype=torch.float32)
        if kind=='F6':model=DecisionGate(42,16);maximum=epochs or 40;a=b=None
        else:a,b=anchor(train['p'][0],yt);model=AnchoredAdjustment(a,b);maximum=epochs or 100
        optimizer=torch.optim.AdamW(model.parameters(),lr=.003,weight_decay=.001);generator=torch.Generator().manual_seed(seed)
        def forward(probabilities,context):
            if kind=='F6':
                raw,weights=model(context,torch.logit(probabilities.clamp(1e-6,1-1e-6)),context[:,-2:]);return raw,weights,torch.tensor(0.)
            raw,delta,effective=model(probabilities,context);return raw,effective,delta.square().mean()
        def predict():
            model.eval();ps=[];ws=[]
            with torch.no_grad():
                for i in range(len(vp)):
                    raw,weights,_=forward(vp[i],vu[i]);ps.append(torch.sigmoid(raw).numpy());ws.append(weights.numpy())
            return np.stack(ps),np.stack(ws)
        best=-np.inf;best_epoch=0;history=[];best_state=None
        for epoch in range(1,maximum+1):
            model.train();order=torch.randperm(len(yt),generator=generator);choices=torch.multinomial(torch.tensor(VIEW_WEIGHTS),len(yt),replacement=True,generator=generator)
            if not augmented:choices.zero_()
            total=0.
            for ids in order.split(128):
                optimizer.zero_grad();raw,_,regularizer=forward(tp[choices[ids],ids],tu[choices[ids],ids]);loss=torch.nn.functional.binary_cross_entropy_with_logits(raw,target[ids])+penalty*regularizer
                assert torch.isfinite(loss);loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1);optimizer.step();total+=float(loss.detach())*len(ids)
            probabilities,weights=predict() if epochs is None or epoch==maximum else (None,None)
            objective=selection_score(yv,probabilities) if epochs is None else None
            history.append(dict(epoch=epoch,train_loss=total/len(yt),validation_objective=objective,validation_clean_AP=float(average_precision_score(yv,probabilities[0])) if epochs is None else None,
                validation_clean_AUROC=float(roc_auc_score(yv,probabilities[0])) if epochs is None else None))
            if (epochs is not None and epoch==maximum) or (epochs is None and objective>best):
                if objective is not None:best=objective
                best_epoch=epoch;best_state={k:v.detach().clone() for k,v in model.state_dict().items()}
            if epochs is None and epoch>=10 and epoch-best_epoch>=12:break
        model.load_state_dict(best_state);probabilities,weights=predict()
        torch.save(dict(kind=kind,augmented=augmented,state_dict=best_state,normalizer_mean=torch.tensor(mean),normalizer_std=torch.tensor(std),coefficient=torch.tensor(a) if a is not None else None,intercept=b,epoch=best_epoch,seed=seed),path.with_suffix('.pt'))
        info=dict(signature=signature,kind=kind,augmented=augmented,seed=seed,penalty=penalty,best_epoch=best_epoch,stopped_epoch=epoch,cap_reached=epoch==maximum,history=history,normalizer_mean=mean.tolist(),normalizer_std=std.tolist(),seconds=time.perf_counter()-start,checkpoint=identity(path.with_suffix('.pt')))
    result=dict(p=probabilities,weights=weights)
    np.savez_compressed(path.with_suffix('.npz'),**result);info.update(predictions=identity(path.with_suffix('.npz')),training_rows=train['rows'].tolist(),assessment_rows=test['rows'].tolist())
    write(path.with_suffix('.json'),info);return result,info

def main():
    c=config();torch.set_num_threads(1);torch.use_deterministic_algorithms(True);base=read(c['section1_config']);c2=read(c['section2_config']);root=Path(c['run_dir'])/'04_corruption_training';frame=cohort(base);y=frame.failure.to_numpy(int);splits=read(base['splits'])
    quality,names,sources=quality_features(frame,base,c2);actions=np.stack([(frame.action==a).to_numpy(np.float32) for a in c2['actions']],axis=1)
    for outer in splits['folds']:
        k=outer['fold'];plan=index_plan(frame,outer)
        finaltrain=join([pack(c,frame,quality,actions,f'outer{k}_inner{j}','train') for j in range(4)]);test=pack(c,frame,quality,actions,f'outer{k}','test')
        inner=[]
        for j,(it,iv) in enumerate(plan):
            tr=join([pack(c,frame,quality,actions,f'outer{k}_inner{j}_sub{t}','train') for t in range(4)]);va=pack(c,frame,quality,actions,f'outer{k}_inner{j}','validation')
            assert np.array_equal(tr['rows'],it) and np.array_equal(va['rows'],iv)
            assert not set(frame.recording_id.iloc[tr['rows']])&set(frame.recording_id.iloc[va['rows']]);inner.append((tr,va))
        for kind in ['F2','F6','A-ADAPTIVE']:
            for augmented in [False,True]:
                label=('augmented_' if augmented else 'clean_')+kind;seeds=c['seeds'] if kind!='F2' else [c['seeds'][0]]
                penalties=c['adaptation']['lambdas'] if kind=='A-ADAPTIVE' else [0.];candidates=[]
                for penalty in penalties:
                    oof=np.full((len(seeds),len(y)),np.nan);scores=[];durations=np.zeros((len(seeds),4),int)
                    for j,(tr,va) in enumerate(inner):
                        seedpred=[]
                        for s,seed in enumerate(seeds):
                            result,info=fit(root/'fits'/f'outer{k}_{label}_lambda{penalty}_inner{j}_seed{seed}',kind,augmented,tr,va,y,seed,penalty)
                            seedpred.append(result['p']);oof[s,va['rows']]=result['p'][0];durations[s,j]=info['best_epoch'] or 0
                        scores.append(selection_score(y[va['rows']],np.mean(seedpred,axis=0)))
                    candidates.append(dict(penalty=penalty,score=float(np.mean(scores)),oof=oof,epochs=durations))
                selected=max(candidates,key=lambda v:v['score']);threshold=choose_threshold(y[finaltrain['rows']],selected['oof'][:,finaltrain['rows']].mean(0));pred=[];weights=[];refits=[];seedhard=[]
                for s,seed in enumerate(seeds):
                    duration=int(np.floor(np.median(selected['epochs'][s])+.5)) if kind!='F2' else None
                    result,info=fit(root/'fits'/f'outer{k}_{label}_refit_seed{seed}',kind,augmented,finaltrain,test,y,seed,selected['penalty'],duration)
                    sp=result['p'].astype(float);hard=(sp>=choose_threshold(y[finaltrain['rows']],selected['oof'][s,finaltrain['rows']])).astype(float)
                    for i in range(len(sp)):sp[i],hard[i]=modality_fallback(sp[i],hard[i],test['p'][i],test['branch_thresholds'],test['u'][i,:,-2:])
                    pred.append(sp);weights.append(result['weights']);refits.append(info);seedhard.append(hard)
                probability=np.mean(pred,axis=0);hard=(probability>=threshold).astype(float)
                for i in range(len(probability)):probability[i],hard[i]=modality_fallback(probability[i],hard[i],test['p'][i],test['branch_thresholds'],test['u'][i,:,-2:])
                out=root/f'outer{k}_{label}.npz';np.savez_compressed(out,rows=test['rows'],names=test['names'],p=probability,hard=hard,seed_p=np.stack(pred),seed_hard=np.stack(seedhard),weights=np.mean(weights,axis=0),seed_weights=np.stack(weights),branch_p=test['p'],branch_thresholds=test['branch_thresholds'])
                write(out.with_suffix('.json'),dict(label=label,fold=k,threshold=threshold,selected_penalty=selected['penalty'],inner_scores=[dict(penalty=v['penalty'],objective=v['score']) for v in candidates],refits=refits,output=identity(out)))
                progress(4,f'Matched robustness {label} outer{k+1}/5 complete')
    progress(4,'All matched fusion refits complete; hierarchical paired evaluation pending')

if __name__=='__main__':main()
