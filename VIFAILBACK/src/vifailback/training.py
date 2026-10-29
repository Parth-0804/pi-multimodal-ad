"""100 executed epochs, validation-only selection, epoch-boundary exact resume."""
import gc
import math
import os
import random
import time
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader,Dataset

from .common import PROJECT,config,disk_reserve,event,read,sha,signature,write,code_identity
from .cohort import finalize
from .feature_bank import pooled_bank
from .metrics import metrics,independent_check
from .reference import primitives,identities
from .splits import prepare
from .visual import make,pixels,features,chunked_backward,gradient_evidence,snapshot


def atomic_checkpoint(path,value):
    path=Path(path);assert path.resolve().is_relative_to(PROJECT.resolve())
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+f'.writing.{os.getpid()}')
    with temp.open('wb') as f:
        torch.save(value,f);f.flush();os.fsync(f.fileno())
    os.replace(temp,path)


def rng_state():
    ns=np.random.get_state()
    return {'python':random.getstate(),'numpy':[ns[0],ns[1].tolist(),ns[2],ns[3],ns[4]],
            'torch':torch.get_rng_state(),'cuda':torch.cuda.get_rng_state_all() if torch.cuda.is_initialized() else []}


def restore_rng(value):
    random.setstate(value['python']);ns=value['numpy']
    np.random.set_state((ns[0],np.asarray(ns[1],dtype='uint32'),ns[2],ns[3],ns[4]))
    torch.set_rng_state(value['torch'])
    if value['cuda']:torch.cuda.set_rng_state_all(value['cuda'])


class Episodes(Dataset):
    def __init__(self,c,rows):self.c=c;self.rows=rows
    def __len__(self):return len(self.rows)
    def __getitem__(self,i):return self.rows[i]['episode_index'],pixels(self.c,self.rows[i])


def loader(c,rows):
    # CPU decode workers are isolated; a single episode limits host/GPU memory.
    policy=PROJECT/'05_model_implementations/visual_models'/c['run_id']/'GPU_BENCHMARK.json'
    workers=read(policy)['selected_loader_workers'] if policy.exists() else 2
    settings={'prefetch_factor':1,'persistent_workers':False} if workers else {}
    return DataLoader(Episodes(c,rows),batch_size=None,num_workers=workers,pin_memory=True,**settings)


def predict(model,c,ids,lookup,bank,bank_index,device):
    model.eval();out=[]
    with torch.inference_mode():
        if model.backbone is None:
            for batch in np.array_split(np.asarray(ids),max(1,math.ceil(len(ids)/128))):
                z=torch.as_tensor(bank[[bank_index[int(e)] for e in batch]],device=device)
                out.extend(model(z).cpu().numpy().tolist())
        else:
            for eid,x in loader(c,[lookup[e] for e in ids]):
                z=features(model.backbone,x.to(device),c['cnn_frame_chunk']).mean(0,keepdim=True)
                raw=model.head(torch.nan_to_num((z-model.mean)/model.std,nan=0,posinf=0,neginf=0))
                out.append(float(raw[0].cpu()))
    assert len(out)==len(ids)
    return np.asarray(out,dtype='float32')


def fit(c,condition,job,seed,device):
    assert c['epochs']==100,'Required full schedule must remain100'
    root=PROJECT/'06_training_experiments'/dict(V1='visual_frozen',V2='visual_finetuned100',V3='reassemble_transfer')[condition]/'runs'/c['run_id']/f'seed{seed}'/job['id']
    done=root/'COMPLETE.json'
    if done.exists():
        receipt=read(done);assert sha(root/'predictions.json')==receipt['prediction_sha256']
        assert sha(root/'BEST_MODEL.pt')==receipt['best_checkpoint_sha256']
        assert sha(root/'FINAL_EPOCH100.pt')==receipt['final_checkpoint_sha256']
        return receipt
    disk_reserve(c,300*1024**2)
    if str(device).startswith('cuda'):
        from .resources import wait_for_gpu
        wait_for_gpu(c)
    root.mkdir(parents=True,exist_ok=True)
    rows=finalize(c);lookup={r['episode_index']:r for r in rows};index={r['episode_index']:i for i,r in enumerate(rows)}
    bank,bank_receipt=pooled_bank(c,'V3' if condition=='V3' else 'V1')
    source=primitives();torch.set_num_threads(c['cpu_threads'])
    mean,std=source['standardizer'](bank[[index[e] for e in job['ids']['T']]])
    random.seed(seed);np.random.seed(seed);torch.manual_seed(seed)
    model=make(c,condition,mean,std,seed,device)
    groups=[{'params':list(model.head.parameters()),'lr':c['head_lr'],'name':'new_classifier'}]
    if model.full:groups.append({'params':list(model.backbone.parameters()),'lr':c['backbone_lr'],'name':'all_CNN_conv_and_affine'})
    optimizer=torch.optim.AdamW(groups,weight_decay=c['weight_decay'])
    scheduler=torch.optim.lr_scheduler.LambdaLR(optimizer,lambda ep:.1+.9*.5*(1+math.cos(math.pi*ep/100)))
    runtime=PROJECT/'05_model_implementations/visual_models'/c['run_id']/'GPU_BENCHMARK.json'
    identity=signature({'config':c,'job':job,'seed':seed,'condition':condition,'feature_sha256':bank_receipt['sha256'],
                        'source':identities(),'implementation':code_identity(),'runtime_benchmark_sha256':sha(runtime) if runtime.exists() else None})
    initial=snapshot(model);history=[];best=-float('inf');best_epoch=None;start_epoch=0
    live=root/'RECOVERY.pt'
    if live.exists():
        saved=torch.load(live,map_location='cpu',weights_only=True);assert saved['identity']==identity
        model.load_state_dict(saved['model']);optimizer.load_state_dict(saved['optimizer']);scheduler.load_state_dict(saved['scheduler'])
        history=saved['history'];best=saved['best'];best_epoch=saved['best_epoch'];start_epoch=saved['completed_epochs'];initial=saved['initial']
        restore_rng(saved['rng'])
    target=lambda ids:np.asarray([lookup[e]['label'] for e in ids])
    t_y=target(job['ids']['T']);positive_weight=torch.tensor((len(t_y)-t_y.sum())/t_y.sum(),device=device,dtype=torch.float32)
    total_seconds=sum(h['epoch_seconds'] for h in history)
    for epoch in range(start_epoch,100):
        disk_reserve(c,200*1024**2);model.train()
        if str(device).startswith('cuda'):torch.cuda.reset_peak_memory_stats()
        started=time.perf_counter();loss_sum=0;count=0
        train_ids=np.asarray(job['ids']['T'])[np.random.default_rng(seed+epoch*100003).permutation(len(job['ids']['T']))].tolist()
        if condition=='V1':
            batch=c['gradient_accumulation']
            batches=[train_ids[i:i+batch] for i in range(0,len(train_ids),batch)]
            for ids in batches:
                optimizer.zero_grad(set_to_none=True)
                x=torch.as_tensor(bank[[index[e] for e in ids]],device=device)
                y=torch.as_tensor(target(ids),device=device,dtype=torch.float32)
                loss=nn.functional.binary_cross_entropy_with_logits(model(x),y,pos_weight=positive_weight)
                assert torch.isfinite(loss);loss.backward()
                if epoch==0 and not count:write(root/'GRADIENT_EVIDENCE.json',gradient_evidence(model))
                nn.utils.clip_grad_norm_(model.parameters(),c['gradient_clip']);optimizer.step()
                loss_sum+=float(loss.detach())*len(ids);count+=len(ids)
        else:
            optimizer.zero_grad(set_to_none=True)
            for number,(eid,x) in enumerate(loader(c,[lookup[e] for e in train_ids])):
                position=number%c['gradient_accumulation']
                divisor=min(c['gradient_accumulation'],len(train_ids)-(number-position))
                y=torch.tensor([lookup[eid]['label']],device=device,dtype=torch.float32)
                loss,raw=chunked_backward(model,x.to(device),y,positive_weight,divisor,c['cnn_frame_chunk'])
                assert torch.isfinite(loss);loss_sum+=float(loss);count+=1
                if epoch==0 and number==0:write(root/'GRADIENT_EVIDENCE.json',gradient_evidence(model))
                if position==c['gradient_accumulation']-1 or number==len(train_ids)-1:
                    nn.utils.clip_grad_norm_(model.parameters(),c['gradient_clip']);optimizer.step();optimizer.zero_grad(set_to_none=True)
                if (number+1)%100==0:
                    write(root/'BATCH_PROGRESS.json',{'epoch':epoch+1,'episodes':number+1,'total':len(train_ids),'recovery':'epoch boundary; interrupted epoch replays from saved RNG'})
        raw= predict(model,c,job['ids']['V'],lookup,bank,index,device)
        from scipy.special import expit
        score=metrics(target(job['ids']['V']),expit(raw))['macro_AP']
        elapsed=time.perf_counter()-started;total_seconds+=elapsed
        record={'epoch':epoch+1,'T_weighted_BCE':loss_sum/count,'V_macro_AP':score,
                'learning_rates':[g['lr'] for g in optimizer.param_groups],
                'epoch_seconds':elapsed,'training_episodes_per_train_plus_validation_second':count/elapsed,
                'peak_GPU_bytes':torch.cuda.max_memory_allocated() if str(device).startswith('cuda') else 0,
                'precision':'float32'}
        history.append(record)
        if score>best:
            best=score;best_epoch=epoch+1
            atomic_checkpoint(root/'BEST_MODEL.pt',{'model':model.state_dict(),'selected_epoch':best_epoch,'identity':identity,
                              'condition':condition,'seed':seed,'job':job,'mean_source':'T only','bank_sha256':bank_receipt['sha256']})
            write(root/'BEST_VALIDATION_PREDICTIONS.json',[{'episode_index':e,'label':lookup[e]['label'],'raw':float(r),'epoch':best_epoch}
                  for e,r in zip(job['ids']['V'],raw)])
        scheduler.step()
        state={'model':model.state_dict(),'optimizer':optimizer.state_dict(),'scheduler':scheduler.state_dict(),
               'rng':rng_state(),'history':history,'best':best,'best_epoch':best_epoch,'completed_epochs':epoch+1,
               'identity':identity,'initial':initial,'condition':condition,'seed':seed,'job':job}
        atomic_checkpoint(live,state);write(root/'HISTORY.json',history)
        event(c,'VISUAL_EPOCH_COMPLETE',condition=condition,seed=seed,fit_id=job['id'],**record)
    assert len(history)==100 and history[-1]['epoch']==100
    final=root/'FINAL_EPOCH100.pt'
    # Same immutable final recovery bytes, two names, no duplicated135MB payload.
    if not final.exists():os.link(live,final)
    after=snapshot(model);changed=[n for n in initial if initial[n]!=after[n]]
    assert any(n.startswith('head.') for n in changed)
    if condition!='V1':
        for prefix in ['backbone.embedder.']+[f'backbone.encoder.stages.{i}.' for i in range(4)]:
            assert any(n.startswith(prefix) for n in changed),('CNN_NOT_UPDATED',prefix)
        assert not any('running_' in n for n in changed),'FROZEN_BN_MOMENTS_CHANGED'
    write(root/'WEIGHT_UPDATE_EVIDENCE.json',{'changed_tensors':changed,'initial':initial,'final':after,
                                            'full_100_epochs_executed':True,'selected_epoch':best_epoch})
    selected=torch.load(root/'BEST_MODEL.pt',map_location='cpu',weights_only=True);assert selected['identity']==identity
    model.load_state_dict(selected['model']);model.eval()
    rawC=predict(model,c,job['ids']['C'],lookup,bank,index,device)
    calibrator=source['calibrate'](rawC,target(job['ids']['C']))
    write(root/'CALIBRATION_PREDICTIONS.json',[{'episode_index':e,'label':lookup[e]['label'],'raw':float(r)} for e,r in zip(job['ids']['C'],rawC)])
    rawA=predict(model,c,job['ids']['A'],lookup,bank,index,device);p=source['calibrated'](rawA,calibrator)
    predictions=[{'episode_index':e,'fit_id':job['id'],'outer':job['outer'],'inner':job['inner'],'seed':seed,
                  'condition':condition,'label':lookup[e]['label'],'raw':float(r),'probability':float(prob)} for e,r,prob in zip(job['ids']['A'],rawA,p)]
    write(root/'CALIBRATOR.json',calibrator);write(root/'predictions.json',predictions)
    report=metrics(target(job['ids']['A']),p);independent_check(target(job['ids']['A']),p,report);write(root/'metrics.json',report)
    receipt={'condition':condition,'seed':seed,'fit_id':job['id'],'identity':identity,'executed_epochs':100,
             'selected_epoch':best_epoch,'training_and_validation_seconds':total_seconds,
             'prediction_sha256':sha(root/'predictions.json'),'best_checkpoint_sha256':sha(root/'BEST_MODEL.pt'),
             'final_checkpoint_sha256':sha(final),'source':identities()}
    write(done,receipt);del model,optimizer;gc.collect()
    if str(device).startswith('cuda'):torch.cuda.empty_cache()
    return receipt


def run(c=None,conditions=('V1',),device='cpu'):
    c=c or config();jobs=prepare(c)
    return [fit(c,condition,job,seed,device) for condition in conditions for seed in c['seeds'] for job in jobs]
