"""Nested unimodal fits. No outer outcomes participate in fitting decisions."""
import os
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG',':4096:8')
import argparse
import json
import time
import subprocess
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from torch import nn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, balanced_accuracy_score, roc_auc_score
from transformers import PatchTSTConfig, PatchTSTModel
from .section1_features import cohort, sha


class Standardizer:
    def fit(self,x):
        axis=(0,1) if x.ndim==3 else 0
        self.mean=np.nanmean(x,axis=axis).astype('float32')
        self.std=np.nanstd(x,axis=axis).astype('float32')
        self.mean=np.nan_to_num(self.mean,nan=0)
        self.std=np.where(np.isfinite(self.std)&(self.std>1e-6),self.std,1).astype('float32')
        return self
    def transform(self,x):
        return np.nan_to_num((x-self.mean)/self.std,nan=0,posinf=0,neginf=0).astype('float32')


class VisualHead(nn.Module):
    def __init__(self,width,config):
        super().__init__();self.projection=nn.Sequential(nn.Linear(width,128),nn.ReLU(),nn.Dropout(.1));self.classifier=nn.Linear(128,1)
    def forward(self,x,mask=None):
        z=self.projection(x);return self.classifier(z).squeeze(-1),z


class SensorHead(nn.Module):
    def __init__(self,width,config):
        super().__init__();c=config['sensor']
        self.encoder=PatchTSTModel(PatchTSTConfig(num_input_channels=width,context_length=512,patch_length=c['patch_length'],patch_stride=c['patch_stride'],d_model=c['d_model'],num_hidden_layers=c['layers'],num_attention_heads=c['heads'],ffn_dim=c['ffn_dim'],scaling=None,norm_type='layernorm',do_mask_input=False,attention_dropout=c['dropout'],ff_dropout=c['dropout'],path_dropout=c['dropout'],positional_dropout=c['dropout']))
        self.projection=nn.Sequential(nn.Linear(width*c['d_model'],128),nn.ReLU(),nn.Dropout(c['dropout']));self.classifier=nn.Linear(128,1)
    def forward(self,x,mask=None):
        h=self.encoder(past_values=x,past_observed_mask=mask).last_hidden_state
        z=self.projection(h.mean(dim=2).flatten(1));return self.classifier(z).squeeze(-1),z


def verify_splits(frame,splits):
    """Validate exact frozen assignment and full coverage before any fitting."""
    import hashlib
    unsigned={k:v for k,v in splits.items() if k!='sha256'}
    assert hashlib.sha256(json.dumps(unsigned,sort_keys=True).encode()).hexdigest()==splits['sha256']
    groups=set(frame.recording_id);seen=set()
    for f in splits['folds']:
        tr,te=set(f['train_recordings']),set(f['test_recordings'])
        assert not tr&te and tr|te==groups and not seen&te;seen|=te
        ivseen=set()
        for i in f['inner']:
            it,iv=set(i['train_recordings']),set(i['validation_recordings'])
            assert not it&iv and it|iv==tr and not ivseen&iv;ivseen|=iv
            for g in [it,iv]:assert frame.loc[frame.recording_id.isin(g),'failure'].nunique()==2
        assert ivseen==tr
    assert seen==groups


def permute_labels(frame,seed):
    rng=np.random.default_rng(seed);y=frame.failure.to_numpy(dtype=int).copy()
    for _,rows in frame.groupby(['recording_id','action'],sort=True):
        ix=rows.sort_values(['start','segment_id']).index.to_numpy()
        y[ix]=np.roll(y[ix],int(rng.integers(len(ix))))
    return y


def sigmoid(x):return 1/(1+np.exp(-np.clip(x,-40,40)))


def calibrate(inner_logits,y,test_logits):
    cal=LogisticRegression(C=1.0,max_iter=1000).fit(np.asarray(inner_logits)[:,None],y)
    p=cal.predict_proba(np.asarray(inner_logits)[:,None])[:,1]
    thresholds=np.arange(.01,1,.01)
    scores=np.array([balanced_accuracy_score(y,p>=t) for t in thresholds])
    tied=thresholds[np.isclose(scores,scores.max(),rtol=0,atol=1e-12)]
    threshold=float(tied[np.argmin(abs(tied-.5))])
    return cal.predict_proba(np.asarray(test_logits)[:,None])[:,1],threshold,{'coefficient':float(cal.coef_[0,0]),'intercept':float(cal.intercept_[0]),'threshold':threshold}


def neural_fit(kind,x,y,train,predict,candidates,config,seed,save=None):
    torch.manual_seed(seed);np.random.seed(seed)
    normalizer=Standardizer().fit(x[train]);values=torch.from_numpy(normalizer.transform(x)).cuda()
    mask=torch.from_numpy(np.isfinite(x)).cuda() if kind=='patchtst' else None
    labels=torch.tensor(y,dtype=torch.float32,device='cuda')
    model=(SensorHead if kind=='patchtst' else VisualHead)(x.shape[-1],config).cuda()
    c=config['sensor' if kind=='patchtst' else 'visual'];opt=torch.optim.AdamW(model.parameters(),lr=c['learning_rate'],weight_decay=c['weight_decay'])
    ratio=float((len(train)-y[train].sum())/y[train].sum());criterion=nn.BCEWithLogitsLoss(pos_weight=torch.tensor(ratio,device='cuda'))
    generator=torch.Generator(device='cuda').manual_seed(seed)
    indices=torch.tensor(train,device='cuda');outputs={};losses=[]
    for epoch in range(1,max(candidates)+1):
        model.train();order=indices[torch.randperm(len(indices),generator=generator,device='cuda')];total=0
        for batch in order.split(c['batch_size']):
            opt.zero_grad(set_to_none=True)
            logits,_=model(values[batch],mask[batch] if mask is not None else None)
            loss=criterion(logits,labels[batch]);assert torch.isfinite(loss),'Nonfinite training loss'
            loss.backward();nn.utils.clip_grad_norm_(model.parameters(),1.0);opt.step();total+=float(loss.detach())*len(batch)
        losses.append(total/len(train))
        if epoch in candidates:
            model.eval();scores=[];zs=[]
            with torch.inference_mode():
                for b in np.array_split(predict,max(1,int(np.ceil(len(predict)/256)))):
                    logits,z=model(values[b],mask[b] if mask is not None else None);scores.append(logits.cpu().numpy());zs.append(z.cpu().numpy())
            outputs[epoch]=(np.concatenate(scores),np.concatenate(zs))
    if save is not None:
        torch.save({'state_dict':model.cpu().state_dict(),'kind':kind,'width':x.shape[-1],'config':config,'normalizer_mean':torch.tensor(normalizer.mean),'normalizer_std':torch.tensor(normalizer.std),'epochs':max(candidates)},save)
    info={'loss_by_epoch':losses,'parameters':sum(p.numel() for p in model.parameters()),'seed':seed}
    del model,values,mask,opt
    return outputs,info


def logistic_fit(x,y,train,predict,c):
    scaler=Standardizer().fit(x[train]);model=LogisticRegression(C=c,class_weight='balanced',max_iter=2000,random_state=0).fit(scaler.transform(x[train]),y[train])
    return model.decision_function(scaler.transform(x[predict])),{'iterations':model.n_iter_.tolist()}


def load_features(config):
    f=cohort(config);run=Path(config['run_dir']);blocks=[]
    for p in sorted((run/'features').glob('*.npz')):
        assert sha(p)==json.loads(p.with_suffix('.json').read_text())['feature_sha256']
        with np.load(p) as z:blocks.append({k:z[k] for k in ['row_index','visual','sensor','statistics']})
    ix=np.concatenate([b['row_index'] for b in blocks]);assert sorted(ix)==list(range(len(f)))
    order=np.argsort(ix);arrays={k:np.concatenate([b[k] for b in blocks])[order] for k in ['visual','sensor','statistics']}
    arrays['action']=np.stack([(f.action==a).to_numpy(dtype='float32') for a in ['pick','insert','remove','place']],axis=1)
    return f,arrays


def evaluate_model(kind,frame,arrays,y,config,splits,permutation):
    run=Path(config['run_dir']);out=run/'predictions';out.mkdir(exist_ok=True)
    target=out/f'{kind}_perm{permutation:02d}.npz';details=target.with_suffix('.json')
    if target.exists():
        with np.load(target) as z:assert np.array_equal(z['y'],y)
        print('REUSED MODEL',kind,permutation,flush=True);return
    x=arrays.get({'rtdetr':'visual','patchtst':'sensor','sensor_statistics':'statistics','action_only':'action'}.get(kind,''))
    n=len(y);p=np.full(n,np.nan);raw=np.full(n,np.nan);hard=np.zeros(n,dtype=int);fold_id=np.full(n,-1);embedding=np.full((n,128),np.nan,dtype='float32');logs=[]
    for outer in splits['folds']:
        fold=outer['fold'];folder=out/f'{kind}_perm{permutation:02d}_fold{fold}'
        checkpoint=folder.with_suffix('.npz');logpath=folder.with_suffix('.json')
        tr=np.flatnonzero(frame.recording_id.isin(outer['train_recordings']));te=np.flatnonzero(frame.recording_id.isin(outer['test_recordings']))
        if checkpoint.exists():
            with np.load(checkpoint) as z:p[te]=z['p'];raw[te]=z['raw'];hard[te]=z['hard'];embedding[te]=z['embedding']
            logs.append(json.loads(logpath.read_text()));fold_id[te]=fold;continue
        started=time.time();log={'fold':fold,'kind':kind,'permutation':permutation,'inner':[]}
        if kind in ['prior','majority']:
            prior=float(y[tr].mean());p[te]=prior if kind=='prior' else float(prior>=.5);raw[te]=p[te];hard[te]=(p[te]>=.5).astype(int);log['training_prior']=prior
        else:
            neural=kind in ['rtdetr','patchtst']
            candidates=config['sensor' if kind=='patchtst' else 'visual']['epochs'] if neural else config['logistic_C']
            inner={c:np.full(n,np.nan) for c in candidates};scores={c:[] for c in candidates}
            for part in outer['inner']:
                it=np.flatnonzero(frame.recording_id.isin(part['train_recordings']));iv=np.flatnonzero(frame.recording_id.isin(part['validation_recordings']))
                seed=config['seed']+100*fold+part['fold']
                if neural:outs,info=neural_fit(kind,x,y,it,iv,candidates,config,seed)
                else:outs={c:(logistic_fit(x,y,it,iv,c)[0],None) for c in candidates};info={}
                for c in candidates:
                    inner[c][iv]=outs[c][0];scores[c].append(float(average_precision_score(y[iv],sigmoid(outs[c][0]))))
                log['inner'].append({'fold':part['fold'],'training':info})
            best=max(candidates,key=lambda c:np.mean(scores[c]));assert np.isfinite(inner[best][tr]).all()
            log.update(selected=best,inner_AP=scores)
            if neural:
                save=None
                if permutation==0:
                    weights=run/'checkpoints';weights.mkdir(exist_ok=True);save=weights/f'{kind}_fold{fold}.pt'
                outs,info=neural_fit(kind,x,y,tr,te,[best],config,config['seed']+100*fold+99,save)
                raw[te]=outs[best][0];embedding[te]=outs[best][1];log['refit']=info
            else:raw[te],log['refit']=logistic_fit(x,y,tr,te,best)
            p[te],threshold,cal=calibrate(inner[best][tr],y[tr],raw[te]);hard[te]=(p[te]>=threshold).astype(int);log['calibration']=cal
        fold_id[te]=fold;log['seconds']=time.time()-started
        logpath.write_text(json.dumps(log,indent=2)+'\n')
        np.savez_compressed(checkpoint,p=p[te],raw=raw[te],hard=hard[te],embedding=embedding[te])
        logs.append(log);print('FOLD COMPLETE',kind,'perm',permutation,'fold',fold,'seconds',round(log['seconds'],1),flush=True)
    assert np.isfinite(p).all() and np.all(fold_id>=0)
    np.savez_compressed(target,p=p,raw=raw,hard=hard,y=y,fold=fold_id,embedding=embedding)
    summary={'model':kind,'permutation':permutation,'AP':float(average_precision_score(y,p)),'AUROC':float(roc_auc_score(y,p)),'changed_labels':int((y!=frame.failure.to_numpy()).sum()),'folds':logs}
    details.write_text(json.dumps(summary,indent=2)+'\n')
    print('MODEL COMPLETE',kind,'perm',permutation,'AP',round(summary['AP'],5),'AUROC',round(summary['AUROC'],5),flush=True)


def main():
    a=argparse.ArgumentParser();a.add_argument('--config',default='configs/reassemble/section1.json');args=a.parse_args();config=json.loads(Path(args.config).read_text())
    torch.set_num_threads(config['threads']);torch.use_deterministic_algorithms(True);torch.backends.cudnn.benchmark=False
    frame,arrays=load_features(config);splits=json.loads(Path(config['splits']).read_text());verify_splits(frame,splits)
    run=Path(config['run_dir']);assert config==json.loads((run/'config.json').read_text()),'Frozen config changed';assert sha(config['splits'])==sha(run/'nested_splits.json'),'Frozen split file changed'
    prov={'source_sha256':{str(p):sha(p) for p in sorted(Path('src/reassemble').glob('section1_*.py'))},'config_sha256':sha(run/'config.json'),'split_sha256':splits['sha256'],'device':torch.cuda.get_device_name(0),'torch':torch.__version__,'implementation_git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()}
    fp=run/'training_implementation.json'
    if fp.exists():assert json.loads(fp.read_text())==prov,'Changed implementation; do not silently resume'
    else:fp.write_text(json.dumps(prov,indent=2)+'\n')
    for kind in ['prior','majority','action_only','sensor_statistics','rtdetr','patchtst']:
        evaluate_model(kind,frame,arrays,frame.failure.to_numpy(dtype=int),config,splits,0)
    for permutation in range(1,config['permutations']+1):
        y=permute_labels(frame,config['seed']+10000+permutation)
        for kind in ['rtdetr','patchtst']:evaluate_model(kind,frame,arrays,y,config,splits,permutation)
    print('SECTION 1 TRAINING COMPLETE',flush=True)

if __name__=='__main__':main()
