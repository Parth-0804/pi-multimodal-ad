"""Strict-partition static-anchored models on the original branch information."""
from pathlib import Path
import argparse
import time
import hashlib
import json
import numpy as np
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score,roc_auc_score
from threadpoolctl import threadpool_limits
from reassemble.section1_models import Standardizer,sigmoid
from reassemble.section1_features import cohort,sha
from reassemble.section1b import choose_threshold,guard_partition,index_plan
from reassemble.section2_data import quality_features
from .models import AnchoredAdjustment
from .common import config,read,write,progress,storage,identity
from .reporting import comparison

def anchor(p,y):
    with threadpool_limits(limits=16):
        m=LogisticRegression(C=1,class_weight=None,solver='lbfgs',max_iter=2000,random_state=0).fit(p,y)
    return m.coef_[0],float(m.intercept_[0])

def fit(path,p,y,u,train,valid,adaptive,penalty,seed,epochs=None,anchor_values=None):
    path=Path(path);path=path.parent/path.name.replace('.', 'p');path.parent.mkdir(parents=True,exist_ok=True)
    c=config();options=c['adaptation']; signature=hashlib.sha256(json.dumps(dict(source=sha(__file__),models=sha(Path(__file__).with_name('models.py')),train=train.tolist(),valid=valid.tolist(),adaptive=adaptive,penalty=penalty,seed=seed,epochs=epochs,options=options),sort_keys=True).encode()).hexdigest()
    if path.with_suffix('.json').exists():
        info=read(path.with_suffix('.json'));assert info['signature']==signature
        with np.load(path.with_suffix('.npz')) as z:return {k:z[k] for k in z.files},info
    storage();started=time.perf_counter();torch.manual_seed(seed)
    a,b=anchor(p[train],y[train]) if anchor_values is None else anchor_values
    normalizer=Standardizer().fit(u[train,4:40]);context=u.copy();context[:,4:40]=normalizer.transform(u[:,4:40])
    model=AnchoredAdjustment(a,b,adaptive);optimizer=torch.optim.AdamW(model.parameters(),lr=options['lr'],weight_decay=options['weight_decay'])
    tp=torch.tensor(p,dtype=torch.float32);tu=torch.tensor(context,dtype=torch.float32);ty=torch.tensor(y,dtype=torch.float32)
    with torch.no_grad():
        parity=float(np.max(abs(torch.sigmoid(model(tp[valid],tu[valid])[0]).numpy()-sigmoid(b+p[valid]@a))))
    assert parity<1e-6
    rng=torch.Generator().manual_seed(seed);best=-np.inf;best_epoch=0;history=[];best_state=None;best_raw=None
    maximum=epochs or options['max_epochs']
    for epoch in range(1,maximum+1):
        model.train();loss_sum=0.
        order=torch.as_tensor(train)[torch.randperm(len(train),generator=rng)]
        for ids in order.split(options['batch_size']):
            optimizer.zero_grad();raw,delta,_=model(tp[ids],tu[ids])
            loss=torch.nn.functional.binary_cross_entropy_with_logits(raw,ty[ids])+penalty*delta.square().mean()
            loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),options['gradient_clip']);optimizer.step();loss_sum+=loss.item()*len(ids)
        model.eval()
        with torch.no_grad(): raw,delta,effective=model(tp[valid],tu[valid]);raw=raw.numpy()
        ap=float(average_precision_score(y[valid],sigmoid(raw))) if epochs is None else None
        auc=float(roc_auc_score(y[valid],raw)) if epochs is None else None
        history.append(dict(epoch=epoch,train_loss=loss_sum/len(train),validation_AP=ap,validation_AUROC=auc))
        if epochs is not None or ap>best:
            if ap is not None:best=ap
            best_epoch=epoch;best_raw=raw.copy();best_state={k:v.detach().clone() for k,v in model.state_dict().items()}
        if epochs is None and epoch>=options['minimum_epochs'] and epoch-best_epoch>=options['patience']:break
    model.load_state_dict(best_state);model.eval()
    with torch.no_grad():
        raw,delta,effective=model(tp[valid],tu[valid]);neutral=tu[valid].clone();neutral[:,4:40]=0
        pn=torch.sigmoid(model(tp[valid],neutral)[0]).numpy()
        perm=tu[valid].clone();order=np.random.default_rng(seed+991).permutation(len(valid));perm[:,:4]=tu[valid][order,:4]
        pp=torch.sigmoid(model(tp[valid],perm)[0]).numpy()
    result=dict(p=sigmoid(raw.numpy()),effective=effective.numpy(),delta=delta.numpy(),neutral_quality=pn,permuted_action=pp)
    np.savez_compressed(path.with_suffix('.npz'),**result)
    torch.save(dict(state_dict=best_state,coefficient=torch.tensor(a),intercept=b,adaptive=adaptive,mean=torch.tensor(normalizer.mean),std=torch.tensor(normalizer.std),epoch=best_epoch),path.with_suffix('.pt'))
    info=dict(signature=signature,train_rows=train.tolist(),assessment_rows=valid.tolist(),seed=seed,penalty=penalty,best_epoch=best_epoch,stopped_epoch=epoch,cap_reached=epoch==maximum,
              history=history,anchor_coefficient=a.tolist(),anchor_intercept=b,initialization_max_abs=parity,trainable_parameters=sum(x.numel() for x in model.parameters()),seconds=time.perf_counter()-started,
              checkpoint=identity(path.with_suffix('.pt')),predictions=identity(path.with_suffix('.npz')))
    write(path.with_suffix('.json'),info);return result,info

def main():
    c=config();base=read(c['section1_config']);c2=read(c['section2_config']);root=Path(c['run_dir'])/'03_static_anchored_adaptation';root.mkdir(exist_ok=True)
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    frame=cohort(base);y=frame.failure.to_numpy(int);n=len(y);splits=read(base['splits'])
    quality, names, sources=quality_features(frame,base,c2)
    actions=np.asarray([[float(a==name) for name in c2['actions']] for a in frame.action],dtype=np.float32)
    u=np.concatenate([actions,quality,np.ones((n,2),np.float32)],axis=1)
    write(root/'input_identities.json',dict(quality_names=names,quality_sources=sources,strict_inputs=sorted(str(p) for p in (Path(c2['run_dir'])/'inputs').glob('outer*_inner?.npz'))))
    predictions={name:dict(p=np.full(n,np.nan),hard=np.zeros(n,int),seed_p=np.full((3,n),np.nan),seed_hard=np.zeros((3,n),int)) for name in ['A0','A-CONSTANT','A-ADAPTIVE']};fold=np.full(n,-1)
    foldinfo=[]
    for outer in splits['folds']:
        k=outer['fold'];plan=index_plan(frame,outer)
        src=Path(c2['section1b_run'])/'stacking'/f'outer{k}.npz'
        with np.load(src) as z:tr=z['train_rows'];te=z['test_rows'];ptr=z['training_branch_oof'];pte=z['test_branch_probabilities'];original=z['p']
        guard_partition(frame,tr,te,plan);fold[te]=k
        p=np.full((n,2),np.nan);p[tr]=ptr;p[te]=pte
        coefficient,intercept=anchor(ptr,y[tr]);a0=sigmoid(intercept+pte@coefficient)
        assert np.max(abs(a0-original))<1e-8
        inner_a0=np.full(n,np.nan);inners=[]
        for j,(it,iv) in enumerate(plan):
            z=np.load(Path(c2['run_dir'])/'inputs'/f'outer{k}_inner{j}.npz')
            assert np.array_equal(z['train_rows'],it) and np.array_equal(z['validation_rows'],iv)
            ip=np.full((n,2),np.nan);ip[it]=z['train_probabilities'];ip[iv]=z['validation_probabilities'];z.close()
            a,b=anchor(ip[it],y[it]);inner_a0[iv]=sigmoid(b+ip[iv]@a);inners.append(ip)
        threshold=choose_threshold(y[tr],inner_a0[tr]);predictions['A0']['p'][te]=a0;predictions['A0']['hard'][te]=a0>=threshold
        predictions['A0']['seed_p'][:,te]=a0;predictions['A0']['seed_hard'][:,te]=a0>=threshold
        summary=dict(fold=k,anchor_coefficient=coefficient.tolist(),anchor_intercept=intercept,anchor_threshold=threshold,models={})
        for name,adaptive in [('A-CONSTANT',False),('A-ADAPTIVE',True)]:
            candidates=[]
            for penalty in c['adaptation']['lambdas']:
                raw=np.full((3,n),np.nan);durations=np.zeros((3,4),int)
                for j,(it,iv) in enumerate(plan):
                    for s,seed in enumerate(c['seeds']):
                        res,info=fit(root/'fits'/f'outer{k}_{name}_lambda{penalty}_inner{j}_seed{seed}',inners[j],y,u,it,iv,adaptive,penalty,seed)
                        raw[s,iv]=res['p'];durations[s,j]=info['best_epoch']
                score=float(np.mean([average_precision_score(y[iv],raw[:,iv].mean(0)) for _,iv in plan]))
                candidates.append(dict(penalty=penalty,score=score,probabilities=raw,epochs=durations))
                progress(3,f'Outer {k+1}/5 {name} penalty {penalty} inner fits complete')
            selected=max(candidates,key=lambda x:x['score']);threshold=choose_threshold(y[tr],selected['probabilities'][:,tr].mean(0))
            refits=[]
            for s,seed in enumerate(c['seeds']):
                epochs=int(np.floor(np.median(selected['epochs'][s])+.5))
                res,info=fit(root/'fits'/f'outer{k}_{name}_refit_seed{seed}',p,y,u,tr,te,adaptive,selected['penalty'],seed,epochs)
                predictions[name]['seed_p'][s,te]=res['p'];predictions[name]['seed_hard'][s,te]=res['p']>=choose_threshold(y[tr],selected['probabilities'][s,tr]);refits.append(info)
            predictions[name]['p'][te]=predictions[name]['seed_p'][:,te].mean(0);predictions[name]['hard'][te]=predictions[name]['p'][te]>=threshold
            summary['models'][name]=dict(selected_penalty=selected['penalty'],inner_scores=[dict(penalty=x['penalty'],AP=x['score']) for x in candidates],threshold=threshold,refits=refits)
        foldinfo.append(summary);write(root/f'outer{k}.json',summary)
        progress(3,f'Outer {k+1}/5 complete')
    out=root/'predictions.npz';np.savez_compressed(out,y=y,fold=fold,**{f'{m}_{key}':value for m,values in predictions.items() for key,value in values.items()})
    result=comparison(frame,fold,predictions,[('A-ADAPTIVE','A0'),('A-ADAPTIVE','A-CONSTANT'),('A-CONSTANT','A0')],root/'comparison')
    write(root/'execution.json',dict(folds=foldinfo,predictions=identity(out)))
    progress(3,'All static-anchored clean fits and comparisons complete; final report pending')

if __name__=='__main__':main()
