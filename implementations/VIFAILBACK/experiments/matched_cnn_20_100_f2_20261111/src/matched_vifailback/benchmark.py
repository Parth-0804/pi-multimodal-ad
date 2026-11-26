"""Bounded real48-frame equivalence, memory, update and recovery admission checks."""
from __future__ import annotations
import copy
import gc
import math
import time
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.utils.checkpoint import checkpoint
from .common import STUDY,protocol,write_json,sha256,relative,signature
from .model_runtime import make_model,episode_features,frame_features,full_batch_backward,global_clip,optimizer_for,snapshot,gradients,validate_donor
from .training import cpu_tree,atomic_checkpoint,rng_state,restore_rng,scheduler_for,EpochRecovery,Telemetry,train_epoch,predict,_source_identity
from vifailback.reference import primitives
from vifailback.visual import pixels


def _reference(model,example,y,weight,chunk=4):
    """Ordinary autograd through all48 frames, checkpoint each CNN chunk only."""
    flat=example.flatten(0,1);outputs=[]
    for part in flat.split(chunk):
        part=part.cuda()
        outputs.append(checkpoint(lambda value:frame_features(model.backbone,value),part,use_reentrant=False))
    pooled=torch.cat(outputs).mean(0,keepdim=True).cpu()
    loss=nn.functional.binary_cross_entropy_with_logits(model.classify(pooled),y,pos_weight=weight)
    loss.backward();return loss.detach()


def run(context=None):
    from .data import load_context,get_job
    ctx=context or load_context(verify=True);p=protocol();root=STUDY/'13_reproducibility/bounded_validation'
    root.mkdir(parents=True,exist_ok=True)
    assert torch.cuda.is_available(),'CUDA_REQUIRED_FOR_FULL_CNN_ADMISSION'
    torch.set_num_threads(p['resources']['CPU_threads'])
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True;torch.use_deterministic_algorithms(True)
    job=get_job(ctx,p['pilot']['base_job_id']);eid=job['ids']['T'][0];row=ctx['lookup'][eid]
    bank=ctx['original'];mean,std=primitives()['standardizer'](bank[[ctx['index'][e] for e in job['ids']['T']]])
    start=time.perf_counter();x=pixels(ctx['config'],row);decode=time.perf_counter()-start
    assert x.shape==(3,16,3,640,640) and x.dtype==torch.float32
    y=torch.tensor([row['label']],dtype=torch.float32)
    ty=np.asarray([ctx['lookup'][e]['label'] for e in job['ids']['T']]);weight=torch.tensor((len(ty)-ty.sum())/ty.sum(),dtype=torch.float32)
    a=make_model(mean,std,42,True,'cuda');b=make_model(mean,std,42,True,'cuda');frozen=make_model(mean,std,42,False,'cpu')
    assert all(torch.equal(v,b.head.state_dict()[k]) and torch.equal(v,frozen.head.state_dict()[k]) for k,v in a.head.state_dict().items())
    initial=snapshot(b);a.train();b.train();torch.cuda.reset_peak_memory_stats()
    rng=rng_state();start=time.perf_counter();ref=_reference(a,x,y,weight);torch.cuda.synchronize();reference_seconds=time.perf_counter()-start
    restore_rng(rng);start=time.perf_counter()
    with Telemetry(True) as telemetry:other,_=full_batch_backward(b,[x],y,weight)
    torch.cuda.synchronize();recompute_seconds=time.perf_counter()-start
    checks={'48_frame_tensor':True,'matched_initial_head':True,'episode_level_loss':True,'checkpointed_reference_agrees':bool(torch.allclose(ref,other,rtol=1e-6,atol=1e-6))}
    comparisons=[]
    for (name,left),(name2,right) in zip(a.named_parameters(),b.named_parameters()):
        assert name==name2 and left.grad is not None and right.grad is not None
        error=float((left.grad.detach().cpu()-right.grad.detach().cpu()).abs().max())
        agrees=bool(torch.allclose(left.grad,right.grad,rtol=5e-4,atol=2e-6))
        comparisons.append({'parameter':name,'maximum_absolute_gradient_difference':error,'agrees':agrees})
    checks['all_gradients_match_reference']=all(v['agrees'] for v in comparisons)
    assert all(checks.values()),checks
    evidence=gradients(b);opt=optimizer_for(b);global_clip(b);opt.step();after=snapshot(b)
    changed=[n for n in initial if initial[n]!=after[n]]
    checks['all_stages_updated']=all(any(n.startswith(pre) for n in changed) for pre in ['backbone.embedder.']+[f'backbone.encoder.stages.{i}.' for i in range(4)])
    checks['running_moments_fixed']=not any('running_' in n for n in changed)
    checks['CNN_parameters']=sum(q.numel() for q in b.backbone.parameters())==11199968
    checks['head_parameters']=sum(q.numel() for q in b.head.parameters())==114945
    groups=[{k:v for k,v in g.items() if k!='params'}|{'elements':sum(q.numel() for q in g['params'])} for g in opt.param_groups]
    checks['optimizer_groups']=groups[0]['lr']==.001 and groups[1]['lr']==.00001
    # Frozen optimizer never owns or changes any CNN tensor; CPU head does change.
    a_before=snapshot(a);head_before=snapshot(frozen);fo=optimizer_for(frozen);fo.zero_grad()
    ff=torch.from_numpy(bank[[ctx['index'][eid]]]);frozen.train()
    fl=nn.functional.binary_cross_entropy_with_logits(frozen.classify(ff),y,pos_weight=weight);fl.backward();global_clip(frozen);fo.step()
    checks['frozen_CNN_unchanged']=snapshot(a)==a_before and not any(n.startswith('backbone.') for n,_ in frozen.named_parameters())
    checks['frozen_head_updated']=snapshot(frozen)!=head_before
    # Full model + optimizer + scheduler + RNG safe-load and exact next update.
    scheduler=scheduler_for(opt,100);scheduler.step();saved_rng=rng_state()
    saved={'model':cpu_tree(b.state_dict()),'optimizer':cpu_tree(opt.state_dict()),'scheduler':scheduler.state_dict(),'rng':saved_rng}
    path=root/'DISPOSABLE_RESUME.pt';atomic_checkpoint(path,saved);reloaded=torch.load(path,map_location='cpu',weights_only=True)
    restore_rng(saved_rng);opt.zero_grad(set_to_none=True);full_batch_backward(b,[x],y,weight);global_clip(b);opt.step();expected=snapshot(b);expected_rng=rng_state()
    b.load_state_dict(reloaded['model']);opt.load_state_dict(reloaded['optimizer']);scheduler.load_state_dict(reloaded['scheduler']);restore_rng(reloaded['rng'])
    opt.zero_grad(set_to_none=True);full_batch_backward(b,[x],y,weight);global_clip(b);opt.step()
    checks['resume_exact_next_update']=snapshot(b)==expected and torch.equal(rng_state()['torch'],expected_rng['torch'])
    checks['loss_finite']=bool(torch.isfinite(other))
    torch.cuda.synchronize();b.eval();start=time.perf_counter()
    with torch.inference_mode():z=episode_features(b.backbone,x).cpu().unsqueeze(0);before=b.classify(z)
    torch.cuda.synchronize();inference=time.perf_counter()-start
    state=cpu_tree(b.state_dict());b.load_state_dict(state,strict=True)
    with torch.inference_mode():again=b.classify(episode_features(b.backbone,x).cpu().unsqueeze(0))
    checks['selected_reload_exact']=torch.equal(before,again)
    # Compare original feature geometry to saved CPU bank; preserve numerical device distinction.
    a.eval()
    with torch.inference_mode():original=episode_features(a.backbone,x).cpu().numpy()
    cached=bank[ctx['index'][eid]];feature_error=float(np.max(np.abs(original-cached)))
    checks['saved_CPU_vs_GPU_feature_equivalence']=bool(np.allclose(original,cached,rtol=5e-4,atol=2e-4))
    peak=torch.cuda.max_memory_allocated()
    # Quantify actual storage with real model/optimizer plus selected weights, not raw caches.
    storage_payload=dict(saved,best_payload={'model':saved['model'],'selected_epoch':1},completed_epochs=1,history=[],best=None,initial=initial)
    # Clone the selected state to represent separately stored current and best tensor storages.
    storage_payload['best_payload']['model']=cpu_tree(saved['model'])
    storage_path=root/'DISPOSABLE_STORAGE.pt';atomic_checkpoint(storage_path,storage_payload)
    best_path=root/'DISPOSABLE_BEST.pt';atomic_checkpoint(best_path,{'model':saved['model'],'selected_epoch':1})
    persistent=storage_path.stat().st_size+best_path.stat().st_size
    checks['donor_lineage']=True;donor=validate_donor()
    result={'status':'PASS' if all(checks.values()) else 'FAIL','utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
            'episode_index':eid,'role':'pilot gradient-training T; no held-out label or score selection','checks':checks,
            'gradient_comparisons':comparisons,'gradient_evidence':evidence,'updated_state_names':changed,'optimizer_groups':groups,
            'training_seconds_per_episode':recompute_seconds,'reference_training_seconds_per_episode':reference_seconds,
            'inference_seconds_per_episode':inference,'decode_seconds_per_episode':decode,'peak_GPU_bytes':peak,
            'CPU_vs_GPU_original_feature_max_abs':feature_error,'GPU':torch.cuda.get_device_name(0),
            'GPU_utilization_percent':float(np.mean([r['GPU_utilization_percent'] for r in telemetry.rows])) if telemetry.rows else None,
            'full_fit_checkpoint_bytes_estimate':persistent,'active_fit_checkpoint_peak_bytes_estimate':3*storage_path.stat().st_size+best_path.stat().st_size,
            'storage_measurement':'Actual serialized selected+recovery payload with separate current/selected tensor storages; history growth additional',
            'resume_checkpoint_sha256':sha256(path),'donor':donor,'disposable_optimizer_updates':4,
            'compute_estimate_scope':'Single training-T episode, no campaign-time guarantee; decoder and validation overhead separate',
            'CPU_head':'One batched CPU head per actual up-to8episode update; matched initial weights and RNG; GPU CNN only'}
    write_json(STUDY/'13_reproducibility/BOUNDED_GPU_BENCHMARK.json',result)
    assert result['status']=='PASS',checks
    del a,b,frozen,opt,fo,scheduler,saved,reloaded,storage_payload,state;gc.collect();torch.cuda.empty_cache()
    return result


def run_batch8(context=None):
    """One production minibatch and inference on the same eight training episodes."""
    from .data import load_context,get_job
    ctx=context or load_context(verify=True);p=protocol()
    assert torch.cuda.is_available(),'CUDA_REQUIRED_FOR_BATCH8_ADMISSION'
    output=STUDY/'13_reproducibility/BOUNDED_BATCH8_THROUGHPUT.json'
    assert not output.exists(),'PRESERVE_EXISTING_BATCH8_RECEIPT'
    job=get_job(ctx,p['pilot']['base_job_id']);ids=[int(e) for e in job['ids']['T'][:8]]
    assert len(ids)==len(set(ids))==8
    bank=ctx['original'];mean,std=primitives()['standardizer'](bank[[ctx['index'][int(e)] for e in job['ids']['T']]])
    labels=np.asarray([ctx['lookup'][int(e)]['label'] for e in job['ids']['T']])
    weight=torch.tensor((len(labels)-labels.sum())/labels.sum(),dtype=torch.float32)
    model=make_model(mean,std,p['pilot']['seed'],True,'cuda');optimizer=optimizer_for(model)
    initial=snapshot(model);calls=[]
    hook=model.head.register_forward_pre_hook(lambda module,args:calls.append(tuple(args[0].shape)))
    torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();started=time.perf_counter()
    try:
        with Telemetry(True) as telemetry:
            epoch=train_epoch(model,optimizer,ctx,ids,bank,weight,evidence=True)
        torch.cuda.synchronize();training_seconds=time.perf_counter()-started
    finally:hook.remove()
    after=snapshot(model);changed=[name for name in initial if initial[name]!=after[name]]
    parameter_steps=[int(state['step'].item()) for state in optimizer.state.values()]
    training_peak=torch.cuda.max_memory_allocated()
    torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();started=time.perf_counter()
    raw=predict(model,ctx,ids,bank);torch.cuda.synchronize();inference_seconds=time.perf_counter()-started
    inference_peak=torch.cuda.max_memory_allocated()
    checks={
        'eight_distinct_training_episodes':len(ids)==len(set(ids))==8,
        'production_two_spawn_workers':p['resources']['loader_workers']==2 and p['resources']['loader_prefetch']==1,
        'single_CPU_head_batch8':calls==[(8,896)] and next(model.head.parameters()).device.type=='cpu',
        'single_optimizer_update':epoch['optimizer_updates']==1 and parameter_steps and all(step==1 for step in parameter_steps),
        'eight_episode_loss':epoch['training_episodes']==8 and math.isfinite(epoch['training_loss']),
        'all_stages_updated':all(any(name.startswith(prefix) for name in changed) for prefix in ['backbone.embedder.']+[f'backbone.encoder.stages.{i}.' for i in range(4)]),
        'running_moments_fixed':not any('running_' in name for name in changed),
        'head_updated':any(name.startswith('head.') for name in changed),
        'CNN_parameter_count':sum(value.numel() for value in model.backbone.parameters())==11199968,
        'head_parameter_count':sum(value.numel() for value in model.head.parameters())==114945,
        'eight_finite_inferences':raw.shape==(8,) and bool(np.isfinite(raw).all()),
    }
    result={
        'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,
        'utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
        'episode_indices':ids,'role':'First eight distinct pilot gradient-training T episodes only',
        'training_seconds':training_seconds,'training_seconds_per_episode':training_seconds/8,
        'inference_seconds':inference_seconds,'inference_seconds_per_episode':inference_seconds/8,
        'timing_scope':'End-to-end actual production train_epoch/predict, including spawned worker startup, all eight video decodes, CNN, CPU head and worker shutdown; no extra decoder time should be added',
        'peak_GPU_bytes':max(training_peak,inference_peak),'training_peak_GPU_bytes':training_peak,
        'inference_peak_GPU_bytes':inference_peak,'GPU':torch.cuda.get_device_name(0),
        'GPU_utilization_percent':float(np.mean([row['GPU_utilization_percent'] for row in telemetry.rows])) if telemetry.rows else None,
        'training':epoch,'head_call_shapes':calls,'optimizer_parameter_steps':sorted(set(parameter_steps)),
        'updated_state_names':changed,'disposable_optimizer_updates':1,'implementation':_source_identity(),
        'compute_estimate_scope':'Bounded batch8 includes worker startup on only eight episodes; larger-epoch throughput may differ. No campaign-time guarantee.',
    }
    write_json(output,result)
    assert result['status']=='PASS',checks
    del model,optimizer;gc.collect();torch.cuda.empty_cache()
    return result
