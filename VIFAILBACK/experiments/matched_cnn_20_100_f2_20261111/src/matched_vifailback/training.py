"""Matched20/100 fitting with committed epoch recovery and CPU minibatch heads."""
from __future__ import annotations
import gc
import math
import os
import random
import shutil
import subprocess
import threading
import time
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.utils.data import Dataset,DataLoader
from scipy.special import expit
from . import common
from .common import STUDY,PROJECT,REPO,protocol,legacy_config,read_json,write_json,sha256,signature,relative,resolve,fit_root,immutable_json,exclusive_lock,utc
from .model_runtime import make_model,episode_features,full_batch_backward,global_clip,optimizer_for,snapshot,gradients
from vifailback.reference import primitives,identities
from vifailback.metrics import metrics,independent_check
from vifailback.visual import pixels
from vifailback.training import rng_state,restore_rng
from vifailback.common import code_identity as legacy_code_identity


def cpu_tree(value):
    if torch.is_tensor(value): return value.detach().cpu().clone()
    if isinstance(value,dict): return {k:cpu_tree(v) for k,v in value.items()}
    if isinstance(value,list): return [cpu_tree(v) for v in value]
    if isinstance(value,tuple): return tuple(cpu_tree(v) for v in value)
    return value


def atomic_checkpoint(path,value):
    path=common.destination(path);path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name(path.name+f'.writing.{os.getpid()}')
    with temporary.open('wb') as f:
        torch.save(value,f);f.flush();os.fsync(f.fileno())
    os.replace(temporary,path)
    fd=os.open(path.parent,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)


class EpochRecovery:
    """Pointer commits last+selected state together; selected files are materializations."""
    def __init__(self,root,identity):self.root=Path(root);self.identity=identity
    def save(self,state):
        epoch=state['completed_epochs'];slot=self.root/f'RECOVERY_SLOT_{epoch%2}.pt'
        value=cpu_tree(dict(state,identity=self.identity));atomic_checkpoint(slot,value)
        write_json(self.root/'RECOVERY_POINTER.json',{'slot':slot.name,'sha256':sha256(slot),'completed_epochs':epoch,'identity':self.identity})
        self.publish_best(value)
        return slot
    def publish_best(self,state):
        if state.get('best_payload') is not None:
            atomic_checkpoint(self.root/'BEST_MODEL.pt',state['best_payload'])
    def load(self):
        p=self.root/'RECOVERY_POINTER.json'
        if not p.exists():return None
        pointer=read_json(p);assert pointer['identity']==self.identity
        slot=self.root/pointer['slot'];assert sha256(slot)==pointer['sha256'],'RECOVERY_HASH_MISMATCH'
        state=torch.load(slot,map_location='cpu',weights_only=True)
        assert state['identity']==self.identity and state['completed_epochs']==pointer['completed_epochs']
        self.publish_best(state)
        return state
    def final(self,epoch):
        pointer=read_json(self.root/'RECOVERY_POINTER.json');assert pointer['completed_epochs']==epoch
        slot=self.root/pointer['slot'];dest=self.root/f'FINAL_EPOCH{epoch}.pt'
        if dest.exists():assert sha256(dest)==pointer['sha256']
        else:os.link(slot,dest)
        return dest
    def release_previous(self):
        # Only the unreferenced rolling generation created by this fitter.
        pointer=read_json(self.root/'RECOVERY_POINTER.json');removed=[]
        for path in self.root.glob('RECOVERY_SLOT_[01].pt'):
            if path.name!=pointer['slot']:
                assert path.resolve().parent==self.root.resolve() and not path.is_symlink()
                removed.append({'path':relative(path),'sha256':sha256(path),'bytes':path.stat().st_size});path.unlink()
        return removed


def better(candidate,best):
    if best is None:return True
    return (candidate['V_macro_AP'],-candidate['V_weighted_BCE_same_T_positive_weight'],-candidate['epoch'])>(best['V_macro_AP'],-best['V_weighted_BCE_same_T_positive_weight'],-best['epoch'])


def scheduler_for(optimizer,horizon):
    return torch.optim.lr_scheduler.LambdaLR(optimizer,lambda epoch:.1+.9*.5*(1+math.cos(math.pi*epoch/horizon)))


class Episodes(Dataset):
    def __init__(self,c,rows):self.c=c;self.rows=rows
    def __len__(self):return len(self.rows)
    def __getitem__(self,index):
        row=self.rows[index];return int(row['episode_index']),pixels(self.c,row)


def episode_loader(ctx,ids):
    p=protocol();workers=p['resources']['loader_workers']
    kwargs={'prefetch_factor':p['resources']['loader_prefetch'],'persistent_workers':False,'multiprocessing_context':'spawn'} if workers else {}
    # Separate generator keeps worker-seeding draws out of the CPU dropout RNG.
    return DataLoader(Episodes(ctx['config'],[ctx['lookup'][int(e)] for e in ids]),batch_size=None,num_workers=workers,
                      pin_memory=True,generator=torch.Generator().manual_seed(314159),**kwargs)


class Telemetry:
    def __init__(self,enabled):self.enabled=enabled;self.rows=[];self.stop=threading.Event();self.thread=None
    def _run(self):
        while not self.stop.is_set():
            try:
                result=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.used,power.draw','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=5)
                if result.returncode==0:
                    values=[float(v.strip()) for v in result.stdout.splitlines()[0].split(',')]
                    self.rows.append({'elapsed':time.perf_counter()-self.started,'GPU_utilization_percent':values[0],'driver_memory_MiB':values[1],'power_W':values[2]})
            except (OSError,ValueError,subprocess.TimeoutExpired):pass
            self.stop.wait(2.)
    def __enter__(self):
        self.started=time.perf_counter()
        if self.enabled:self.thread=threading.Thread(target=self._run,daemon=True);self.thread.start()
        return self
    def __exit__(self,*args):
        self.stop.set()
        if self.thread:self.thread.join(timeout=6)


def predict(model,ctx,ids,bank,chunk=4):
    model.eval();values=[]
    with torch.inference_mode():
        if model.full:
            for eid,x in episode_loader(ctx,ids):
                z=episode_features(model.backbone,x,chunk).cpu().unsqueeze(0)
                values.append(float(model.classify(z)[0]))
        else:
            for start in range(0,len(ids),128):
                batch=ids[start:start+128];x=torch.from_numpy(bank[[ctx['index'][int(e)] for e in batch]])
                values.extend(model.classify(x).numpy().tolist())
    result=np.asarray(values,dtype=np.float32);assert result.shape==(len(ids),) and np.isfinite(result).all()
    return result


def train_epoch(model,optimizer,ctx,ids,bank,positive_weight,*,evidence=False,progress=None):
    model.train();loss_sum=0.;count=0;first=None;updates=0
    if model.full:
        iterator=iter(episode_loader(ctx,ids))
        for offset in range(0,len(ids),8):
            batch=ids[offset:offset+8];examples=[]
            for expected in batch:
                eid,x=next(iterator);assert int(eid)==int(expected),'TRAINING_ORDER_DRIFT';examples.append(x)
            y=torch.tensor([ctx['lookup'][int(e)]['label'] for e in batch],dtype=torch.float32)
            optimizer.zero_grad(set_to_none=True)
            loss,_=full_batch_backward(model,examples,y,positive_weight)
            if evidence and first is None:first=gradients(model)
            global_clip(model,1.);optimizer.step();loss_sum+=float(loss)*len(batch);count+=len(batch);updates+=1
            del examples,x
            if progress and updates%10==0:progress(count,updates)
        try:next(iterator);raise AssertionError('Extra episodes in loader')
        except StopIteration:pass
    else:
        for offset in range(0,len(ids),8):
            batch=ids[offset:offset+8];optimizer.zero_grad(set_to_none=True)
            x=torch.from_numpy(bank[[ctx['index'][int(e)] for e in batch]])
            y=torch.tensor([ctx['lookup'][int(e)]['label'] for e in batch],dtype=torch.float32)
            loss=nn.functional.binary_cross_entropy_with_logits(model.classify(x),y,pos_weight=positive_weight)
            assert torch.isfinite(loss);loss.backward()
            if evidence and first is None:first=gradients(model)
            # Source-exact CPU clipping for the cached-feature arm.
            nn.utils.clip_grad_norm_(model.parameters(),1.,error_if_nonfinite=True);optimizer.step()
            loss_sum+=float(loss.detach())*len(batch);count+=len(batch);updates+=1
    assert count==len(ids)
    return {'training_loss':loss_sum/count,'training_episodes':count,'optimizer_updates':updates,'first_gradients':first}


def check_storage(future=600*1024**2):
    p=protocol();free=shutil.disk_usage(STUDY).free
    if free-future < p['resources']['minimum_free_GiB']*1024**3:raise RuntimeError('STORAGE_RESERVE_BLOCKER')


def _source_identity():
    paths=[Path(__file__),Path(__file__).with_name('model_runtime.py'),Path(__file__).with_name('data.py'),Path(__file__).with_name('common.py')]
    return legacy_code_identity()|{relative(p):sha256(p) for p in paths}|identities()


def _configuration(condition,seed,job,ctx):
    p=protocol();bank='donor' if condition.startswith('DONOR') else 'original'
    return {'protocol_sha256':common.PROTOCOL_SHA256,'condition':condition,'seed':int(seed),'job':job,
            'epochs':p['epochs'][condition],'cosine_horizon':p['cosine_horizon'][condition],
            'optimizer':p['optimizer'],'selection':p['selection'],'CNN_full_trainable':condition.startswith('FULL'),
            'feature_bank':bank,'feature_moments':'Proper gradient-training T only; fixed',
            'initialization':'original pretrained' if bank=='original' else 'verified Full100 epoch47 CNN only',
            'implementation':_source_identity(),'cohort_sha256':p['cohort_sha256'],'splits_sha256':p['splits_sha256']}


def _records(raw,probabilities,ctx,ids,condition,seed,job):
    return [{'episode_index':int(e),'label':int(ctx['lookup'][int(e)]['label']),'raw':float(r),'probability':float(p),
             'condition':condition,'seed':int(seed),'fit_id':job['id'],'outer':job['outer'],'inner':job['inner']}
            for e,r,p in zip(ids,raw,probabilities)]


def _postfit(model,ctx,job,bank,root,condition,seed,calibrator=None):
    source=primitives();started=time.perf_counter()
    target=lambda ids:np.asarray([ctx['lookup'][int(e)]['label'] for e in ids],dtype=int)
    if calibrator is None:
        raw=predict(model,ctx,job['ids']['C'],bank)
        calibrator=source['calibrate'](raw,target(job['ids']['C']))
        write_json(root/'CALIBRATION_PREDICTIONS.json',[{'episode_index':int(e),'label':int(y),'raw':float(r)} for e,y,r in zip(job['ids']['C'],target(job['ids']['C']),raw)])
    write_json(root/'CALIBRATOR.json',calibrator)
    outputs={};roles=[('predictions.json',job['ids']['A'])]
    if condition.endswith('100'):
        from .data import pilot_outer_ids
        roles.append(('OUTER_PREDICTIONS.json',pilot_outer_ids(ctx)))
    for filename,ids in roles:
        raw=predict(model,ctx,ids,bank);p=source['calibrated'](raw,calibrator)
        write_json(root/filename,_records(raw,p,ctx,ids,condition,seed,job))
        report=metrics(target(ids),p);independent_check(target(ids),p,report)
        write_json(root/('OUTER_METRICS.json' if filename.startswith('OUTER') else 'metrics.json'),report)
        outputs['outer_prediction_sha256' if filename.startswith('OUTER') else 'prediction_sha256']=sha256(root/filename)
    outputs['postfit_inference_seconds']=time.perf_counter()-started
    return outputs


def _reuse_frozen100(ctx,job,seed,root,configuration):
    old=PROJECT/'06_training_experiments/visual_frozen/runs'/ctx['config']['run_id']/f'seed{seed}'/job['id']
    receipt=read_json(old/'COMPLETE.json');history=read_json(old/'HISTORY.json')
    assert [x['epoch'] for x in history]==list(range(1,101))
    selected=None
    for row in history:
        if better(row,selected):selected=row
    assert selected['epoch']==receipt['selected_epoch']==11
    for n,k in [('BEST_MODEL.pt','best_checkpoint_sha256'),('FINAL_EPOCH100.pt','final_checkpoint_sha256'),('predictions.json','prediction_sha256')]:
        assert sha256(old/n)==receipt[k]
    payload=torch.load(old/'BEST_MODEL.pt',map_location='cpu',weights_only=True)
    bank=ctx['original'];mean,std=primitives()['standardizer'](bank[[ctx['index'][int(e)] for e in job['ids']['T']]])
    assert np.array_equal(mean,payload['model']['mean'].numpy()) and np.array_equal(std,payload['model']['std'].numpy())
    assert payload['job']==job and payload['seed']==seed
    model=make_model(mean,std,seed,False,'cpu');model.load_state_dict(payload['model'],strict=True)
    model.eval();old_rows=read_json(old/'predictions.json');old_ids=[int(r['episode_index']) for r in old_rows]
    assert old_ids==job['ids']['A']
    # Reuse original calibrated inner bank exactly. Only new outer inference is needed.
    write_json(root/'predictions.json',[dict(r,condition='FROZEN100') for r in old_rows])
    calibrator=read_json(old/'CALIBRATOR.json');write_json(root/'CALIBRATOR.json',calibrator)
    write_json(root/'CALIBRATION_PREDICTIONS_REFERENCE.json',{'path':relative(old/'CALIBRATION_PREDICTIONS.json'),'sha256':sha256(old/'CALIBRATION_PREDICTIONS.json')})
    from .data import pilot_outer_ids
    ids=pilot_outer_ids(ctx);started=time.perf_counter();raw=predict(model,ctx,ids,bank);prob=primitives()['calibrated'](raw,calibrator)
    write_json(root/'OUTER_PREDICTIONS.json',_records(raw,prob,ctx,ids,'FROZEN100',seed,job))
    for name,values in [('metrics.json',read_json(root/'predictions.json')),('OUTER_METRICS.json',read_json(root/'OUTER_PREDICTIONS.json'))]:
        y=np.asarray([r['label'] for r in values]);p=np.asarray([r['probability'] for r in values]);m=metrics(y,p);independent_check(y,p,m);write_json(root/name,m)
    write_json(root/'HISTORY.json',history)
    write_json(root/'BEST_MODEL_REFERENCE.json',{'path':relative(old/'BEST_MODEL.pt'),'sha256':receipt['best_checkpoint_sha256']})
    write_json(root/'FINAL_MODEL_REFERENCE.json',{'path':relative(old/'FINAL_EPOCH100.pt'),'sha256':receipt['final_checkpoint_sha256']})
    done={'condition':'FROZEN100','seed':seed,'fit_id':job['id'],'outer':job['outer'],'inner':job['inner'],
          'executed_epochs':100,'selected_epoch':11,'reused':True,'new_training_seconds':0.,'training_seconds':0.,'validation_seconds':0.,
          'historical_training_and_validation_seconds':receipt['training_and_validation_seconds'],
          'best_checkpoint_path':relative(old/'BEST_MODEL.pt'),'final_checkpoint_path':relative(old/'FINAL_EPOCH100.pt'),
          'best_checkpoint_sha256':receipt['best_checkpoint_sha256'],'final_checkpoint_sha256':receipt['final_checkpoint_sha256'],
          'prediction_sha256':sha256(root/'predictions.json'),'outer_prediction_sha256':sha256(root/'OUTER_PREDICTIONS.json'),
          'history_sha256':sha256(root/'HISTORY.json'),'configuration_sha256':signature(configuration),
          'identity':signature(configuration),'postfit_inference_seconds':time.perf_counter()-started,
          'reuse_source_receipt':relative(old/'COMPLETE.json'),'reuse_source_receipt_sha256':sha256(old/'COMPLETE.json'),'completed_utc':utc()}
    write_json(root/'COMPLETE.json',done);return done


def fit(condition,seed,job_id,context=None):
    from .data import load_context,get_job
    p=protocol();ctx=context or load_context(verify=True);job=get_job(ctx,job_id)
    assert condition in p['epochs'] and seed in p['seeds']
    if condition.endswith('100'):
        assert seed==p['pilot']['seed'] and job_id==p['pilot']['base_job_id']
    root=fit_root(condition,seed,job_id);root.mkdir(parents=True,exist_ok=True)
    with exclusive_lock(root/'FIT.lock'):
        configuration=_configuration(condition,seed,job,ctx);identity=signature(configuration)
        immutable_json(root/'CONFIG.json',configuration)
        if (root/'COMPLETE.json').exists():
            done=read_json(root/'COMPLETE.json');assert done['configuration_sha256']==signature(configuration)
            for name,key in [('predictions.json','prediction_sha256'),('HISTORY.json','history_sha256')]:assert sha256(root/name)==done[key]
            if 'outer_prediction_sha256' in done:assert sha256(root/'OUTER_PREDICTIONS.json')==done['outer_prediction_sha256']
            for key in ['best','final']:
                path=resolve(done[f'{key}_checkpoint_path']);assert sha256(path)==done[f'{key}_checkpoint_sha256']
            return done
        if condition=='FROZEN100':return _reuse_frozen100(ctx,job,seed,root,configuration)
        full=condition.startswith('FULL');bank=ctx['donor' if condition.startswith('DONOR') else 'original']
        if full:
            gate=STUDY/'13_reproducibility/BOUNDED_GPU_BENCHMARK.json'
            assert gate.exists() and read_json(gate)['status']=='PASS','FULL_CNN_BENCHMARK_NOT_PASSED'
        check_storage();mean,std=primitives()['standardizer'](bank[[ctx['index'][int(e)] for e in job['ids']['T']]])
        random.seed(seed);np.random.seed(seed)
        model=make_model(mean,std,seed,full,'cuda' if full else 'cpu');optimizer=optimizer_for(model)
        scheduler=scheduler_for(optimizer,p['cosine_horizon'][condition]);recovery=EpochRecovery(root,identity)
        state=recovery.load();history=[];best=None;best_payload=None;start=0;initial=snapshot(model)
        if state:
            model.load_state_dict(state['model']);optimizer.load_state_dict(state['optimizer']);scheduler.load_state_dict(state['scheduler'])
            history=state['history'];best=state['best'];best_payload=state['best_payload'];start=state['completed_epochs'];initial=state['initial'];restore_rng(state['rng'])
            write_json(root/'RESUMPTION.json',{'completed_epochs':start,'next_epoch':start+1,'identity':identity,'policy':'Restore committed best+last+optimizer+scheduler+RNG; replay incomplete epoch'})
        target=lambda ids:np.asarray([ctx['lookup'][int(e)]['label'] for e in ids],dtype=int)
        ty=target(job['ids']['T']);positive_weight=torch.tensor((len(ty)-ty.sum())/ty.sum(),dtype=torch.float32)
        def boundary(epoch):
            return {'model':model.state_dict(),'optimizer':optimizer.state_dict(),'scheduler':scheduler.state_dict(),'rng':rng_state(),
                    'completed_epochs':epoch,'history':history,'best':best,'best_payload':best_payload,'initial':initial,
                    'condition':condition,'seed':seed,'job':job}
        if state is None:recovery.save(boundary(0))
        del state
        for epoch in range(start,p['epochs'][condition]):
            check_storage();ids=np.asarray(job['ids']['T'])[np.random.default_rng(seed+epoch*100003).permutation(len(job['ids']['T']))].tolist()
            if full:torch.cuda.reset_peak_memory_stats();torch.cuda.synchronize()
            started=time.perf_counter()
            def progress(count,updates):write_json(root/'BATCH_PROGRESS.json',{'epoch':epoch+1,'completed_epochs':epoch,'episodes':count,'total':len(ids),'optimizer_updates':updates,'utc':utc()})
            with Telemetry(full) as telemetry:
                result=train_epoch(model,optimizer,ctx,ids,bank,positive_weight,evidence=epoch==0,progress=progress)
                if full:torch.cuda.synchronize()
            train_seconds=time.perf_counter()-started
            valid_started=time.perf_counter();raw=predict(model,ctx,job['ids']['V'],bank);vy=target(job['ids']['V'])
            m=metrics(vy,expit(raw));weight=float(positive_weight)
            vloss=float(np.mean((1-vy)*np.logaddexp(0,raw.astype(float))+weight*vy*np.logaddexp(0,-raw.astype(float))))
            valid_seconds=time.perf_counter()-valid_started
            row={'epoch':epoch+1,'T_weighted_BCE':result['training_loss'],'V_macro_AP':m['macro_AP'],'V_AP_failure':m['AP_failure'],
                 'V_AP_success':m['AP_success'],'V_AUROC':m['AUROC'],'V_weighted_BCE_same_T_positive_weight':vloss,
                 'learning_rates':[g['lr'] for g in optimizer.param_groups],'training_seconds':train_seconds,'validation_seconds':valid_seconds,
                 'epoch_seconds':train_seconds+valid_seconds,'training_episodes':len(ids),'training_episodes_per_second':len(ids)/train_seconds,
                 'optimizer_updates':result['optimizer_updates'],'peak_GPU_bytes':torch.cuda.max_memory_allocated() if full else 0,
                 'GPU_utilization_percent':float(np.mean([x['GPU_utilization_percent'] for x in telemetry.rows])) if telemetry.rows else None,
                 'precision':'float32','validation_probability_scope':'raw sigmoid before C calibration'}
            if result['first_gradients']:write_json(root/'GRADIENT_EVIDENCE.json',result['first_gradients'])
            history.append(row)
            if better(row,best):
                best=row.copy();best_payload={'model':cpu_tree(model.state_dict()),'selected_epoch':epoch+1,'identity':identity,'condition':condition,'seed':seed,'job':job}
            scheduler.step();checkpoint_started=time.perf_counter();recovery.save(boundary(epoch+1))
            write_json(root/'HISTORY.json',history)
            write_json(root/f'TIMING_EPOCH_{epoch+1:03d}.json',{'training_seconds':train_seconds,'validation_seconds':valid_seconds,'checkpoint_seconds':time.perf_counter()-checkpoint_started})
            if full:write_json(root/f'GPU_TELEMETRY_EPOCH_{epoch+1:03d}.json',telemetry.rows)
            print(f'{utc()} {condition} seed{seed} {job_id} epoch{epoch+1}/{p["epochs"][condition]} V_macro_AP={m["macro_AP"]:.6f}',flush=True)
        assert [h['epoch'] for h in history]==list(range(1,p['epochs'][condition]+1))
        final=recovery.final(p['epochs'][condition]);after=snapshot(model);changed=[n for n in initial if initial[n]!=after[n]]
        assert any(n.startswith('head.') for n in changed)
        if full:
            for prefix in ['backbone.embedder.']+[f'backbone.encoder.stages.{i}.' for i in range(4)]:assert any(n.startswith(prefix) for n in changed),prefix
            assert not any('running_' in n for n in changed)
        write_json(root/'WEIGHT_UPDATE_EVIDENCE.json',{'initial':initial,'final':after,'changed_tensors':changed,'full_CNN':full,'running_moments_unchanged':True})
        selected=torch.load(root/'BEST_MODEL.pt',map_location='cpu',weights_only=True);assert selected['identity']==identity
        model.load_state_dict(selected['model']);post=_postfit(model,ctx,job,bank,root,condition,seed)
        done={'condition':condition,'seed':seed,'fit_id':job_id,'outer':job['outer'],'inner':job['inner'],'identity':identity,
              'executed_epochs':len(history),'selected_epoch':best['epoch'],'reused':False,'configuration_sha256':signature(configuration),
              'training_seconds':sum(r['training_seconds'] for r in history),'validation_seconds':sum(r['validation_seconds'] for r in history),
              'best_checkpoint_path':relative(root/'BEST_MODEL.pt'),'final_checkpoint_path':relative(final),
              'best_checkpoint_sha256':sha256(root/'BEST_MODEL.pt'),'final_checkpoint_sha256':sha256(final),'history_sha256':sha256(root/'HISTORY.json'),
              'completed_utc':utc(),**post}
        # Release only previous rolling generation; selected and final remain permanent.
        done['released_unreferenced_rolling_generation']=recovery.release_previous()
        write_json(root/'COMPLETE.json',done)
        del model,optimizer,scheduler,best_payload,selected;gc.collect()
        if full:torch.cuda.empty_cache()
        return done
