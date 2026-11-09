"""New two-epoch orchestration using the unchanged visual/optimizer/calibration primitives."""
import gc
import math
import os
import random
import signal
import time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from common import *
install_prior_primitives()
from visual_model import original,Visual,optimizer,model_state,restore_model,snapshot_named
from fusion import standardizer,calibrate,calibrated
from fast_input import ordered_pixels
from data import load_cohort

STOP=False
def request_stop(*args):
    global STOP
    STOP=True
def training_guard():
    if STOP:raise StopStudy('SIGNAL_STOP')
    guard();resources(160*1024**2)
def seed_all(seed):
    random.seed(seed);np.random.seed(seed);torch.manual_seed(seed);torch.cuda.manual_seed_all(seed)
def fit_folder(seed,condition,job):return ROOT/f'seed_{seed}'/condition/job['fold_name']/job['role']
def old_fit_folder(job):
    return PRIOR/'fine_tuned_32_frames'/job['fold_name']/('outer_assessment' if job['role']=='outer_assessment' else 'fusion_training/'+job['role'])/'visual_fit'
def fit_identity(seed,condition,job):
    return {'seed_family':seed,'training_role_seed':role_seed(seed,job),'condition':condition,'job':job,
        'config':sha(STUDY/'resolved_config.json'),'cohort':sha(STUDY/'data_manifests/cohort_and_frames.json'),
        'partitions':sha(STUDY/'data_manifests/fit_partitions.json'),
        'training_sources':{n:sha(STUDY/'code'/n) for n in ['common.py','data.py','branch_fit.py','pipeline.py']},
        'prior_model_source':sha(PRIOR/'source/visual_model.py'),'prior_pixel_source':sha(PRIOR/'source/pixel_access.py'),
        'prior_primitives':{n:sha(PRIOR/'source'/n) for n in ['visual_model.py','fusion.py','pixel_access.py','fast_input.py']},
        'feature_sha256':read(PRIOR/'shared_cache/frozen_features_complete.json')['hashes']['shared_cache/original_features_32.npy']}

def predict(model,frame,rows,features,pixels=False):
    start=time.monotonic();model.eval();answer=[]
    with torch.inference_mode():
        if pixels:
            batch=config()['prediction_batch_segments_finetuned'];iterator=iter(ordered_pixels(frame,rows,32))
            for offset in range(0,len(rows),batch):
                training_guard();items=[next(iterator) for _ in rows[offset:offset+batch]]
                assert [x[0] for x in items]==list(map(int,rows[offset:offset+batch]))
                x=torch.stack([x[1] for x in items]).cuda();answer.extend(model(x).cpu().numpy().tolist())
        else:
            for offset in range(0,len(rows),256):
                training_guard();x=torch.from_numpy(np.asarray(features[rows[offset:offset+256]]).copy()).cuda()
                answer.extend(model(x).cpu().numpy().tolist())
    torch.cuda.synchronize();return np.asarray(answer),time.monotonic()-start

def reuse_finetuned42(job):
    old=old_fit_folder(job);done=read(old/'complete.json');folder=fit_folder(42,'finetuned32_two_epochs',job)
    folder.mkdir(parents=True,exist_ok=True)
    pred=csv(old/'identified_branch_predictions.csv')
    assert sha(old/'model.pt')==done['model_sha256'] and sha(old/'identified_branch_predictions.csv')==done['predictions_sha256']
    for name in ['calibrator.json','learning_curve.csv','full_fit_weight_checks.json','calibration_holdout_logits.csv']:
        target=folder/name
        if not target.exists():target.write_bytes((old/name).read_bytes())
    out=folder/'identified_branch_predictions.csv'
    if not out.exists():out.write_bytes((old/'identified_branch_predictions.csv').read_bytes())
    manifest={'status':'COMPLETE','reused':True,'seed_family':42,'training_role_seed':job['seed'],'job':job,'epochs':2,
        'fit_id':done['fit_id'],'model_reference':str((old/'model.pt').relative_to(REPO)),
        'model_sha256':done['model_sha256'],'source_complete_manifest':str((old/'complete.json').relative_to(REPO)),
        'source_complete_sha256':sha(old/'complete.json'),'prediction_sha256':sha(out),
        'source_gradient_and_replay_checks':'Reused unchanged; not re-executed','sensor_artifact':str((PRIOR/'sensor_reference'/job['fold_name']/job['role']/'complete.json').relative_to(REPO))}
    write(folder/'complete.json',manifest)
    return pred,manifest

def visual_fit(seed,condition,job,frame,features):
    if seed==42 and condition=='finetuned32_two_epochs':return reuse_finetuned42(job)
    folder=fit_folder(seed,condition,job);folder.mkdir(parents=True,exist_ok=True)
    identity=fit_identity(seed,condition,job);fid=signature(identity);complete=folder/'complete.json'
    if complete.exists():
        done=read(complete);assert done['fit_id']==fid and sha(folder/'identified_branch_predictions.csv')==done['prediction_sha256']
        return csv(folder/'identified_branch_predictions.csv'),done
    adapted=condition=='finetuned32_two_epochs';seed_value=role_seed(seed,job);c=config()
    G,C,V=[np.array(job[k],int) for k in ['G','C','predict']]
    mean,std=standardizer(np.asarray(features[G]));seed_all(seed_value)
    b=original() if adapted else None;torch.manual_seed(seed_value);torch.cuda.manual_seed_all(seed_value)
    model=Visual(b,features.shape[1],mean,std,adapted).cuda();opt=optimizer(model)
    yG=torch.tensor(frame.iloc[G].failure.to_numpy(float),dtype=torch.float32,device='cuda')
    ratio=float((len(G)-yG.sum().item())/yG.sum().item());criterion=torch.nn.BCEWithLogitsLoss(pos_weight=torch.tensor(ratio,device='cuda'))
    original_backbone=snapshot_named(b) if adapted else {};original_head=snapshot_named(model.head)
    cp=folder/'optimizer_checkpoint.pt';epoch0=0;offset0=0;curves=[];updates=0;rows_seen=0;elapsed_prior=0.;loss_sum=0.;epoch_rows=0
    if cp.exists():
        saved=torch.load(cp,map_location='cpu',weights_only=True);assert saved['fit_id']==fid and saved['epoch']<=2
        model.head.load_state_dict(saved['model']['head'])
        if adapted:model.backbone.encoder.stages[-1].load_state_dict(saved['model']['stage'])
        assert np.array_equal(saved['model']['mean'].numpy(),mean) and np.array_equal(saved['model']['std'].numpy(),std)
        opt.load_state_dict(saved['optimizer']);epoch0=saved['epoch'];offset0=saved['offset'];curves=saved['curves'];updates=saved['updates'];rows_seen=saved['rows_seen']
        elapsed_prior=saved['elapsed'];loss_sum=saved['loss_sum'];epoch_rows=saved['epoch_rows']
        torch.set_rng_state(saved['torch_rng']);torch.cuda.set_rng_state_all(saved['cuda_rng']);random.setstate(saved['python_rng'])
    started=time.monotonic();last_event=0.;gradient_record=None;torch.cuda.reset_peak_memory_stats()
    def checkpoint(epoch,offset):
        resources(160*1024**2)
        saved={'fit_id':fid,'model':model_state(model),'optimizer':opt.state_dict(),'epoch':epoch,'offset':offset,'curves':curves,
            'updates':updates,'rows_seen':rows_seen,'elapsed':elapsed_prior+time.monotonic()-started,'loss_sum':loss_sum,'epoch_rows':epoch_rows,
            'torch_rng':torch.get_rng_state(),'cuda_rng':torch.cuda.get_rng_state_all(),'python_rng':random.getstate(),
            'seed':seed_value,'precision':'float32','order':'default_rng(role_seed+epoch).permutation; full optimizer-batch offset'}
        temp=cp.with_suffix('.writing.pt');torch.save(saved,temp);os.replace(temp,cp)
    event('FITTING',active_fit={'seed':seed,'condition':condition,'fold':job['fold_name'],'role':job['role'],'fit_id':fid})
    for epoch in range(epoch0,2):
        order=np.random.default_rng(seed_value+epoch).permutation(len(G));start_offset=offset0 if epoch==epoch0 else 0
        model.train();assert model.head.training
        if adapted:assert all(not module.training for module in model.backbone.modules())
        iterator=iter(ordered_pixels(frame,G[order[start_offset:]],32)) if adapted else None
        for offset in range(start_offset,len(G),c['effective_batch_segments']):
            try:training_guard()
            except StopStudy:checkpoint(epoch,offset);raise
            positions=order[offset:offset+c['effective_batch_segments']];actual=len(positions);opt.zero_grad(set_to_none=True);batch_loss=0.
            for pos in positions:
                row=int(G[pos])
                if adapted:
                    loaded,x=next(iterator);assert loaded==row;x=x.unsqueeze(0).cuda()
                else:x=torch.from_numpy(np.asarray(features[np.array([row])]).copy()).cuda()
                logit=model(x);value=criterion(logit,yG[pos:pos+1]);assert torch.isfinite(value)
                (value/actual).backward();batch_loss+=float(value.detach())
            norm=torch.nn.utils.clip_grad_norm_(model.parameters(),c['gradient_clip']);assert torch.isfinite(norm)
            if gradient_record is None:
                gradient_record={n:{'finite':bool(torch.isfinite(p.grad).all()),'nonzero':bool(torch.count_nonzero(p.grad))} for n,p in model.named_parameters() if p.grad is not None}
                assert all(n.startswith('head.') or (adapted and n.startswith('backbone.encoder.stages.3.')) for n in gradient_record)
                assert all(v['finite'] for v in gradient_record.values())
                if adapted:assert any(v['nonzero'] for n,v in gradient_record.items() if n.startswith('backbone.'))
                write(folder/'first_update_checks.json',{'gradients':gradient_record,'all_backbone_modules_eval':not adapted or all(not x.training for x in model.backbone.modules()),'effective_batch':8,'microbatch':1})
            opt.step();torch.cuda.synchronize();updates+=1;rows_seen+=actual;loss_sum+=batch_loss;epoch_rows+=actual
            if updates%100==0 or time.monotonic()-last_event>=60:
                checkpoint(epoch,offset+actual);last_event=time.monotonic()
                event('FITTING',active_fit={'seed':seed,'condition':condition,'fold':job['fold_name'],'role':job['role'],'epoch':epoch+1,'segments':epoch_rows,'G_samples':len(G),'updates':updates})
        assert epoch_rows==len(G)
        curves.append({'epoch':epoch+1,'training_BCE_mean':loss_sum/epoch_rows,'gradient_training_segments':epoch_rows,'optimizer_updates_cumulative':updates,'training_elapsed_seconds':elapsed_prior+time.monotonic()-started})
        loss_sum=0.;epoch_rows=0;offset0=0;checkpoint(epoch+1,0);save_csv(folder/'learning_curve.csv',pd.DataFrame(curves))
    assert len(curves)==2 and rows_seen==2*len(G) and updates==2*math.ceil(len(G)/8)
    if seed==42 and not adapted:
        old=PRIOR/'frozen_32_frames'/job['fold_name']/('outer_assessment' if job['role']=='outer_assessment' else 'fusion_training/'+job['role'])/'visual_fit/learning_curve.csv'
        prefix=csv(old).iloc[:2].training_BCE_mean.to_numpy();diff=float(np.max(np.abs(prefix-np.array([r['training_BCE_mean'] for r in curves]))))
        write(folder/'frozen_training_prefix_check.json',{'passed':diff<1e-6,'max_abs_BCE_difference':diff,'source':str(old.relative_to(REPO))})
        assert diff<1e-6,'FROZEN_TWO_EPOCH_PREFIX_DIFFERS_FROM_ORIGINAL'
    changed=[]
    if adapted:
        after=snapshot_named(model.backbone);changed=[n for n,h in original_backbone.items() if h!=after[n]]
        assert len(changed)==5 and all(n.startswith('encoder.stages.3.') for n in changed)
    assert original_head!=snapshot_named(model.head)
    write(folder/'weight_update_checks.json',{'passed':True,'head_changed':True,'changed_backbone_tensors':changed,'earlier_CNN_and_running_buffers_unchanged':True,
        'frozen_CNN_proof':'Original hash-checked feature bank; no CNN in optimizer' if not adapted else None})
    training_seconds=elapsed_prior+time.monotonic()-started;torch.save(model_state(model),folder/'model.pt')
    rawC,timeC=predict(model,frame,C,features,adapted);cal=calibrate(rawC,frame.iloc[C].failure.to_numpy(int));write(folder/'calibrator.json',cal)
    caldata=frame.iloc[C][['sample_id','recording_id','segment_id','failure']].copy();caldata['raw_logit']=rawC;save_csv(folder/'calibration_holdout_logits.csv',caldata)
    rawV,timeV=predict(model,frame,V,features,adapted);prob=calibrated(rawV,cal)
    pred=frame.iloc[V][['sample_id','recording_id','segment_id','failure','action','start','end']].copy();pred['raw_visual_logit']=rawV;pred['p_visual']=prob;pred['visual_fit_id']=fid
    save_csv(folder/'identified_branch_predictions.csv',pred)
    del model,opt,b;gc.collect();torch.cuda.empty_cache()
    saved=torch.load(folder/'model.pt',map_location='cpu',weights_only=True);replayed=restore_model(saved,features.shape[1],adapted,seed_value)
    if not adapted:replayed.backbone=original()
    raw_replay,replay_seconds=predict(replayed,frame,V[:3],features,True)
    error=float(np.max(np.abs(calibrated(raw_replay,cal)-prob[:3])));assert error<=c['probability_replay_tolerance']
    manifest={'status':'COMPLETE','reused':False,'fit_id':fid,'identity':identity,'seed_family':seed,'training_role_seed':seed_value,'job':job,'epochs':2,
        'updates':updates,'training_segments_presentations':rows_seen,'training_seconds':training_seconds,'C_prediction_seconds':timeC,'V_prediction_seconds':timeV,
        'replay_seconds':replay_seconds,'saved_pixel_replay':{'passed':True,'max_abs_error':error,'sample_ids':frame.iloc[V[:3]].sample_id.tolist()},
        'model_reference':str((folder/'model.pt').relative_to(REPO)),'model_sha256':sha(folder/'model.pt'),
        'optimizer_checkpoint_sha256':sha(cp),'prediction_sha256':sha(folder/'identified_branch_predictions.csv'),
        'calibrator_sha256':sha(folder/'calibrator.json'),'peak_cuda_bytes':torch.cuda.max_memory_allocated(),
        'sensor_artifact':str((PRIOR/'sensor_reference'/job['fold_name']/job['role']/'complete.json').relative_to(REPO))}
    write(complete,manifest);del replayed,saved;gc.collect();torch.cuda.empty_cache()
    state=read(STUDY/'STATE.json');event('FIT_COMPLETE',new_fits_completed=state.get('new_fits_completed',0)+1,active_fit=None,last_fit={'seed':seed,'condition':condition,'fold':job['fold_name'],'role':job['role']})
    return csv(folder/'identified_branch_predictions.csv'),manifest

