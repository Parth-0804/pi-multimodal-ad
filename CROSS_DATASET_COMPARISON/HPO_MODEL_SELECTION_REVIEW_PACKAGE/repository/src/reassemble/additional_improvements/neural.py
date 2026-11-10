"""Bounded unimodal neural training; outer assessment labels never select epochs."""
from pathlib import Path
import hashlib
import json
import time
import numpy as np
import torch
from sklearn.metrics import average_precision_score,roc_auc_score
from reassemble.section1_models import Standardizer,VisualHead,SensorHead,calibrate,sigmoid
from reassemble.section1b import choose_threshold,guard_partition
from reassemble.section1_features import sha
from .models import TemporalHead
from .common import config,read,write,storage,identity

def make_model(kind,width,base):
    if kind=='V-MEAN':return VisualHead(width,base)
    if kind in ['V-TEMP','V-NOPOS']:return TemporalHead(width,kind=='V-TEMP')
    if kind in ['S-6','S-LONG']:return SensorHead(width,base)
    raise ValueError(kind)

def _fit(path,kind,x,y,train,valid,base,seed,epochs,microbatch):
    c=config();optconf=c['neural'];maximum=epochs or (6 if kind=='S-6' else optconf['max_epochs'])
    torch.manual_seed(seed);np.random.seed(seed);t0=time.perf_counter()
    scale_input=x[train].mean(1) if kind in ['V-TEMP','V-NOPOS'] else x[train]
    scaler=Standardizer().fit(scale_input)
    values=torch.tensor(scaler.transform(x),device='cuda');labels=torch.tensor(y,dtype=torch.float32,device='cuda')
    mask=torch.tensor(np.isfinite(x),device='cuda') if kind.startswith('S-') else None
    model=make_model(kind,x.shape[-1],base).cuda()
    optimizer=torch.optim.AdamW(model.parameters(),lr=optconf['lr'],weight_decay=optconf['weight_decay'])
    pos=float((len(train)-y[train].sum())/y[train].sum())
    criterion=torch.nn.BCEWithLogitsLoss(pos_weight=torch.tensor(pos,device='cuda'))
    generator=torch.Generator(device='cuda').manual_seed(seed);indices=torch.tensor(train,device='cuda')
    history=[];best=-np.inf;best_epoch=0;best_state=None;out={}
    def predict(indices):
        model.eval()
        with torch.inference_mode():
            return np.concatenate([model(values[ix],mask[ix] if mask is not None else None)[0].cpu().numpy() for ix in np.array_split(indices,max(1,int(np.ceil(len(indices)/128))))])
    for epoch in range(1,maximum+1):
        model.train();order=indices[torch.randperm(len(indices),generator=generator,device='cuda')];total=0.
        for effective in order.split(optconf['batch_size']):
            optimizer.zero_grad(set_to_none=True)
            for batch in effective.split(microbatch):
                raw,_=model(values[batch],mask[batch] if mask is not None else None)
                loss=criterion(raw,labels[batch]);assert torch.isfinite(loss)
                (loss*len(batch)/len(effective)).backward();total+=float(loss.detach())*len(batch)
            torch.nn.utils.clip_grad_norm_(model.parameters(),optconf['gradient_clip']);optimizer.step()
        raw=predict(valid) if epochs is None or epoch==maximum else None
        ap=float(average_precision_score(y[valid],sigmoid(raw))) if epochs is None else None
        auc=float(roc_auc_score(y[valid],raw)) if epochs is None else None
        history.append(dict(epoch=epoch,train_loss=total/len(train),validation_AP=ap,validation_AUROC=auc))
        if epochs is None and kind=='S-6' and epoch in [3,6]:out[f'raw_epoch{epoch}']=raw.copy()
        if (epochs is not None and epoch==maximum) or (epochs is None and ap>best):
            if ap is not None:best=ap
            best_epoch=epoch;out['raw']=raw.copy();best_state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}
        if epochs is None and kind!='S-6' and epoch>=optconf['minimum_epochs'] and epoch-best_epoch>=optconf['patience']:break
    model.load_state_dict(best_state);model.eval()
    if kind.startswith('V-'):
        # Only held-out assessment rows are changed; trained weights stay fixed.
        with torch.inference_mode():
            for name in ['reverse','permute']:
                if x.ndim==2:
                    out[name]=predict(valid)
                else:
                    order=np.arange(16)[::-1].copy() if name=='reverse' else np.random.default_rng(seed+991).permutation(16)
                    out[name]=np.concatenate([model(values[ix][:,order])[0].cpu().numpy() for ix in np.array_split(valid,max(1,int(np.ceil(len(valid)/128))))])
        if kind in ['V-MEAN','V-NOPOS']:
            assert max(float(np.max(abs(out[name]-out['raw']))) for name in ['reverse','permute'])<=1e-5
    torch.save(dict(state_dict=best_state,kind=kind,width=x.shape[-1],base=base,normalizer_mean=torch.tensor(scaler.mean),normalizer_std=torch.tensor(scaler.std),epochs=best_epoch,seed=seed),path.with_suffix('.pt'))
    np.savez_compressed(path.with_suffix('.npz'),**out)
    info=dict(kind=kind,seed=seed,train_rows=train.tolist(),assessment_rows=valid.tolist(),best_epoch=best_epoch,stopped_epoch=epoch,cap_reached=epoch==maximum,
              history=history,parameters=sum(p.numel() for p in model.parameters()),seconds=time.perf_counter()-t0,microbatch=microbatch,effective_batch=optconf['batch_size'],
              checkpoint=identity(path.with_suffix('.pt')),predictions=identity(path.with_suffix('.npz')))
    del model,optimizer,values,labels,mask;torch.cuda.empty_cache()
    return out,info

def fit(path,kind,x,y,train,valid,base,seed,epochs=None):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    signature=hashlib.sha256(json.dumps(dict(code=sha(__file__),models=sha(Path(__file__).with_name('models.py')),config=config(),kind=kind,train=train.tolist(),valid=valid.tolist(),seed=seed,epochs=epochs),sort_keys=True).encode()).hexdigest()
    if path.with_suffix('.json').exists():
        info=read(path.with_suffix('.json'));assert info['signature']==signature
        assert sha(path.with_suffix('.pt'))==info['checkpoint']['sha256']
        with np.load(path.with_suffix('.npz')) as z:return {k:z[k] for k in z.files},info
    storage()
    for attempt,micro in enumerate([128,64,32]):
        try:
            out,info=_fit(path,kind,x,y,train,valid,base,seed,epochs,micro)
            info['signature']=signature;write(path.with_suffix('.json'),info);return out,info
        except torch.cuda.OutOfMemoryError as exc:
            write(path.parent/(path.name+f'_oom_attempt{attempt}.json'),dict(error=str(exc),microbatch=micro,effective_batch=128))
            torch.cuda.empty_cache()
            if attempt==2:raise

def branch(folder,kind,x,y,frame,train,test,plan,base):
    """A complete selected/calibrated branch; assess=test is excluded at every level."""
    guard_partition(frame,train,test,plan);folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    final=folder/'branch.json'
    if final.exists():
        info=read(final)
        assert info['train_rows']==train.tolist() and info['test_rows']==test.tolist()
        with np.load(folder/'branch.npz') as z:return {k:z[k] for k in z.files},info
    c=config();seed_p=[];seed_inner=[];reports=[];seed_reverse=[];seed_permute=[]
    for seed in c['seeds']:
        raw=np.full(len(y),np.nan);epochs=[];fits=[];short={3:np.full(len(y),np.nan),6:np.full(len(y),np.nan)}
        for j,(it,iv) in enumerate(plan):
            output,info=fit(folder/f'inner{j}_seed{seed}',kind,x,y,it,iv,base,seed)
            raw[iv]=output['raw'];epochs.append(info['best_epoch']);fits.append(info)
            if kind=='S-6':
                for e in [3,6]:short[e][iv]=output[f'raw_epoch{e}']
        if kind=='S-6':
            duration=max([3,6],key=lambda e:np.mean([average_precision_score(y[iv],short[e][iv]) for _,iv in plan]));raw=short[duration]
        else:duration=int(np.floor(np.median(epochs)+.5))
        output,refit=fit(folder/f'refit_seed{seed}',kind,x,y,train,test,base,seed,duration)
        p,_,cal=calibrate(raw[train],y[train],output['raw'])
        inner=sigmoid(cal['coefficient']*raw[train]+cal['intercept'])
        seed_p.append(p);seed_inner.append(inner)
        if kind.startswith('V-'):
            seed_reverse.append(sigmoid(cal['coefficient']*output['reverse']+cal['intercept']))
            seed_permute.append(sigmoid(cal['coefficient']*output['permute']+cal['intercept']))
        reports.append(dict(seed=seed,calibration=cal,selected_epochs=epochs,refit_epochs=duration,inner_fits=fits,refit=refit))
    seed_p=np.stack(seed_p);seed_inner=np.stack(seed_inner);p=seed_p.mean(0);threshold=choose_threshold(y[train],seed_inner.mean(0))
    output=dict(p=p,hard=(p>=threshold).astype(int),seed_p=seed_p,inner_seed_p=seed_inner,
                seed_hard=np.stack([seed_p[s]>=choose_threshold(y[train],seed_inner[s]) for s in range(3)]).astype(int))
    if kind.startswith('V-'):output.update(reverse=np.mean(seed_reverse,axis=0),permute=np.mean(seed_permute,axis=0))
    np.savez_compressed(folder/'branch.npz',**output)
    info=dict(kind=kind,train_rows=train.tolist(),test_rows=test.tolist(),seeds=reports,threshold=threshold,predictions=identity(folder/'branch.npz'))
    write(final,info);return output,info
