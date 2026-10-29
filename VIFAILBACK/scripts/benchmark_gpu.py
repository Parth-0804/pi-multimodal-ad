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
from vifailback.training import Episodes
from vifailback.visual import make,pixels,chunked_backward,gradient_evidence


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
    for chunk in [4,8]:
        model=make(c,'V2',np.zeros(896),np.ones(896),42,'cuda');opt=torch.optim.AdamW(model.parameters(),lr=1e-5)
        torch.cuda.reset_peak_memory_stats();timings=[]
        for step in range(3):
            torch.cuda.synchronize();started=time.perf_counter();opt.zero_grad(set_to_none=True)
            loss,_=chunked_backward(model,x,torch.tensor([float(chosen[0]['label'])],device='cuda'),torch.tensor(.2,device='cuda'),chunk=chunk)
            assert torch.isfinite(loss);gradients=gradient_evidence(model);torch.nn.utils.clip_grad_norm_(model.parameters(),1);opt.step()
            torch.cuda.synchronize();timings.append(time.perf_counter()-started)
        bench.append({'CNN_frame_chunk':chunk,'step_seconds':timings,'warm_steps_episode_per_second':2/sum(timings[1:]),
                      'peak_GPU_bytes':torch.cuda.max_memory_allocated(),'finite_gradient_tensors':len(gradients),'nonfinite_loss':False})
        del model,opt;torch.cuda.empty_cache()
    write(out,{'GPU':subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total,driver_version','--format=csv,noheader'],text=True).strip(),
               'input_shape':list(x.shape),'loading':loading,'selected_loader_workers':selected,'CNN_benchmarks':bench,
               'primary_CNN_frame_chunk':4,'training_precision':'float32','claim':'diagnostic disposable updates only; no held-out performance evidence'})


if __name__=='__main__':main()
