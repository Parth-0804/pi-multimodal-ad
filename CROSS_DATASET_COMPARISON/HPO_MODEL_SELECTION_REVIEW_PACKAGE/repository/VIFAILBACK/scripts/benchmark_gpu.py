#!/usr/bin/env python3
"""Disposable real-input benchmark after the unrelated study releases the GPU."""
from pathlib import Path
import sys,time,subprocess
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import torch
from torch.utils.data import DataLoader
from vifailback.common import PROJECT,config,read,write
from vifailback.cohort import finalize
from vifailback.resources import wait_for_gpu
from vifailback.splits import prepare
from vifailback.training import Episodes,optimizer_for,atomic_checkpoint,rng_state,restore_rng
from vifailback.feature_bank import pooled_bank
from vifailback.reference import primitives
from vifailback.visual import make,pixels,chunked_backward,gradient_evidence,snapshot


def main():
    c=config();out=PROJECT/'05_model_implementations/visual_models'/c['run_id']/'GPU_BENCHMARK.json'
    if out.exists():return
    wait_for_gpu(c);rows=finalize(c);lookup={r['episode_index']:r for r in rows};job=next(j for j in prepare(c) if j['inner']==-1)
    chosen=[lookup[e] for e in job['ids']['T'][:8]];loading=[]
    for workers in [0,2,4]:
        settings={'prefetch_factor':1} if workers else {}
        loader=DataLoader(Episodes(c,chosen),batch_size=None,num_workers=workers,**settings)
        started=time.perf_counter();count=0
        for e,x in loader:
            assert x.shape==(3,16,3,640,640);count+=1
        elapsed=time.perf_counter()-started
        loading.append({'workers':workers,'episodes':count,'seconds':elapsed,'episodes_per_second':count/elapsed,'worker_stability':'PASS'})
    fastest=max(r['episodes_per_second'] for r in loading)
    selected=min(r['workers'] for r in loading if r['episodes_per_second']>=.95*fastest)
    x=pixels(c,chosen[0]).cuda();bench=[]
    bank,bank_receipt=pooled_bank(c,'V1');index={r['episode_index']:i for i,r in enumerate(rows)}
    mean,std=primitives()['standardizer'](bank[[index[e] for e in job['ids']['T']]])
    positive=sum(lookup[e]['label'] for e in job['ids']['T']);weight=torch.tensor((len(job['ids']['T'])-positive)/positive,device='cuda',dtype=torch.float32)
    for chunk in [4,8]:
        model=make(c,'V2',mean,std,42,'cuda');opt=optimizer_for(c,model)
        torch.cuda.reset_peak_memory_stats();timings=[]
        recovery=out.with_name('GPU_DISPOSABLE_RECOVERY.pt');expected=None;replay_passed=False
        for step in range(3):
            if chunk==4 and step==2:
                saved=torch.load(recovery,map_location='cpu',weights_only=True);model.load_state_dict(saved['model']);opt.load_state_dict(saved['optimizer']);restore_rng(saved['rng'])
            torch.cuda.synchronize();started=time.perf_counter();opt.zero_grad(set_to_none=True)
            loss,_=chunked_backward(model,x,torch.tensor([float(chosen[0]['label'])],device='cuda'),weight,chunk=chunk)
            assert torch.isfinite(loss);gradients=gradient_evidence(model);torch.nn.utils.clip_grad_norm_(model.parameters(),1);opt.step()
            torch.cuda.synchronize();timings.append(time.perf_counter()-started)
            if chunk==4 and step==0:atomic_checkpoint(recovery,{'model':model.state_dict(),'optimizer':opt.state_dict(),'rng':rng_state()})
            if chunk==4 and step==1:expected={'loss':float(loss),'model':snapshot(model),'rng':rng_state()}
            if chunk==4 and step==2:
                assert float(loss)==expected['loss'] and snapshot(model)==expected['model'],'GPU_RESUME_REPLAY_MISMATCH'
                assert torch.equal(torch.get_rng_state(),expected['rng']['torch'])
                assert all(torch.equal(a,b) for a,b in zip(torch.cuda.get_rng_state_all(),expected['rng']['cuda']))
                replay_passed=True
        bench.append({'CNN_frame_chunk':chunk,'step_seconds':timings,'warm_steps_episode_per_second':2/sum(timings[1:]),
                      'peak_GPU_bytes':torch.cuda.max_memory_allocated(),'finite_gradient_tensors':len(gradients),'nonfinite_loss':False,
                      'exact_full_CNN_optimizer_CUDA_RNG_replay':replay_passed if chunk==4 else 'tested with primary_chunk4'})
        del model,opt;torch.cuda.empty_cache()
    write(out,{'GPU':subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total,driver_version','--format=csv,noheader'],text=True).strip(),
               'input_shape':list(x.shape),'loading':loading,'selected_loader_workers':selected,'CNN_benchmarks':bench,
               'primary_CNN_frame_chunk':4,'training_precision':'float32','claim':'diagnostic disposable updates only; no held-out performance evidence'})


if __name__=='__main__':main()
