#!/usr/bin/env python3
"""Disposable real48-image gradient/reload check; no held-out performance claim."""
from pathlib import Path
import sys,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import torch
from vifailback.common import PROJECT,config,core,read,sha,write
from vifailback.splits import plans
from vifailback.visual import make,pixels,chunked_backward,gradient_evidence,snapshot,backbone
from vifailback.training import atomic_checkpoint,rng_state,restore_rng


def main():
    c=config();out=PROJECT/'05_model_implementations/visual_models'/c['run_id'];done=out/'CPU_PREFLIGHT.json'
    if done.exists():return
    torch.set_num_threads(c['cpu_threads']);rows=core(c);job=plans(rows,c['split_seed'])[0]
    row=next(r for r in rows if r['episode_index']==job['ids']['T'][0])
    qc=PROJECT/'02_dataset_verification/video_audit/runs'/c['run_id']/'per_camera'
    assert all(read(qc/f'{row["episode_index"]:06d}_{cam}.json')['technical_valid'] for cam in c['cameras'])
    started=time.perf_counter();x=pixels(c,row);pixel_seconds=time.perf_counter()-started
    model=make(c,'V2',np.zeros(896),np.ones(896),42,'cpu');torch.set_num_threads(c['cpu_threads'])
    opt=torch.optim.AdamW(model.parameters(),lr=1e-5);before=snapshot(model);timings=[]
    def step():
        started=time.perf_counter();model.train();opt.zero_grad(set_to_none=True)
        loss,raw=chunked_backward(model,x,torch.tensor([float(row['label'])]),torch.tensor(.2),chunk=4)
        gradients=gradient_evidence(model);torch.nn.utils.clip_grad_norm_(model.parameters(),1);opt.step()
        timings.append(time.perf_counter()-started);return float(loss),gradients
    loss,grads=step()
    checkpoint=out/'DISPOSABLE_PREFLIGHT.pt'
    atomic_checkpoint(checkpoint,{'model':model.state_dict(),'optimizer':opt.state_dict(),'rng':rng_state()})
    second,_=step();expected=snapshot(model)
    saved=torch.load(checkpoint,map_location='cpu',weights_only=True)
    model.load_state_dict(saved['model']);opt.load_state_dict(saved['optimizer']);restore_rng(saved['rng'])
    replay,_=step();assert second==replay and snapshot(model)==expected
    changed=[n for n in before if before[n]!=expected[n]]
    assert not any('running_' in n for n in changed)
    donor=backbone(c,'V3','cpu');donor_identity=snapshot(donor)
    write(done,{'passed':True,'episode_index':row['episode_index'],'temporary_reference_T_task':row['canonical_task_id'],
                'input_shape':list(x.shape),'decode_preprocess_seconds':pixel_seconds,'step_seconds':timings,
                'gradient_evidence':grads,'changed_tensors':changed,'unchanged_FrozenBN_moments':True,
                'exact_reloaded_second_update':True,'checkpoint_sha256':sha(checkpoint),
                'donor_checkpoint_sha256':c['donor_sha256'],'donor_backbone_tensors':len(donor_identity),
                'interpretation':'CPU disposable pipeline check only; not GPU benchmark or held-out evidence'})


if __name__=='__main__':main()
