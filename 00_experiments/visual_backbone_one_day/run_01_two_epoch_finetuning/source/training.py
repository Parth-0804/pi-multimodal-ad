"""Fixed five frozen / two adapted epoch independent fits; actual group calibration; no score selection."""
import gc,json,os,random,signal,time,importlib.metadata,shutil
from pathlib import Path
import numpy as np,pandas as pd,torch
from common import ROOT,REPO,config,read,write,sha,signature,event,resources,save_csv,CONDITIONS,check_originals
from data import load_cohort
from pixel_access import input_pixels as pixels
from fusion import standardizer,sensor_fit,sensor_predict,calibrate,calibrated,stacker,fused
from visual_model import original,Visual,optimizer,model_state,restore_model,snapshot_named
from budget import guard,admit,cost_estimate,BudgetStop
from fast_input import ordered_pixels
from amend_training_support import stage_reuse,legacy_identity,predict_fast
STOP=False
CACHE_FULL_SCAN_AT=0.
def cache_spill_budget(extra=0):
 """Bounded cache already enforces24 GiB; avoid a tree scan every promotion.

 Free reserve is checked every spill. Full study accounting remains before
 model/checkpoint writes, every100 updates and at least once per minute here.
 The predeclared4 GiB non-cache reserve leaves2 GiB additional ceiling slack.
 """
 global CACHE_FULL_SCAN_AT
 if shutil.disk_usage(ROOT).free-extra<config()['minimum_free_bytes']:raise RuntimeError('DISK_FREE_RESERVE_BLOCKER')
 now=time.monotonic()
 if now-CACHE_FULL_SCAN_AT>=60:resources(extra);CACHE_FULL_SCAN_AT=now
def memory_check():
 values={}
 for line in Path('/proc/self/status').read_text().splitlines():
  if line.startswith(('VmRSS:','VmHWM:')):values[line.split(':')[0]]=int(line.split()[1])*1024
 assert values.get('VmRSS',0)<=config()['host_memory_ceiling_bytes'],'HOST_RSS_CEILING_BLOCKER'
 return {'method':'monitored process RSS; OS CPU affinity separately enforced; no claimed OS memory hard limit',**values}

def request_stop(*args):
 global STOP
 STOP=True
def stop_requested():return STOP or (ROOT/'STOP.json').exists()
def check_locked_inputs(frame):
 for source in read(ROOT/'data_manifests/input_manifest.json'):
  st=(REPO/source['source_path']).stat();assert st.st_size==source['bytes'] and st.st_mtime_ns==source['mtime_ns'],'RAW_INPUT_STAT_DRIFT'
 for row in frame.drop_duplicates('video_path').itertuples():
  st=(REPO/row.video_path).stat();assert st.st_size==row.video_bytes and st.st_mtime_ns==row.video_mtime_ns,'VIDEO_INPUT_STAT_DRIFT'
def runtime_guard():
 recorded=read(ROOT/'provenance/runtime_environment.json')
 for name,version in recorded['packages'].items():assert importlib.metadata.version(name)==version,'SOFTWARE_VERSION_DRIFT '+name
 assert torch.version.cuda==recorded['torch_cuda'] and torch.backends.cudnn.version()==recorded['cudnn_version'],'CUDA_LIBRARY_VERSION_DRIFT'
 assert os.environ.get('CUBLAS_WORKSPACE_CONFIG')==recorded['CUBLAS_WORKSPACE_CONFIG'],'CUBLAS_DETERMINISM_CONFIGURATION_DRIFT'
def fit_code_identity():return {n:sha(ROOT/'source'/n) for n in ['common.py','data.py','fusion.py','visual_model.py','pixel_access.py','training.py','study.sh','budget.py','fast_input.py','amend_training_support.py']}
def input_identity():
 return {'amendment_deadline':sha(ROOT.parent/'efficient_finetuning_two_epochs_24h_v1_deadline.json'),'cohort':sha(ROOT/'data_manifests/cohort_and_frames.json'),'partitions':sha(ROOT/'data_manifests/fit_partitions.json'),'sensor_statistics':sha(ROOT/'shared_cache/sensor_statistics.npy'),'feature_metadata':sha(ROOT/'shared_cache/frozen_features_complete.json'),'original_pretrained_identity':sha(ROOT/'provenance/original_pretrained_identity.json'),'runtime_identity':sha(ROOT/'provenance/runtime_environment.json'),'config':sha(ROOT/'config/resolved_config.json'),'sources':fit_code_identity()}
def fit_signature(job,condition,identity):return signature({'job':job,'condition':condition,'inputs':identity})
def job_folder(job,condition):
 base=ROOT/condition/job['fold_name']
 return base/('outer_assessment' if job['role']=='outer_assessment' else 'fusion_training/'+job['role'])
def membership_check(frame,job):
 G,C,V=[np.array(job[k],int) for k in ['G','C','predict']]
 gs,cs,vs=[set(frame.iloc[ix].recording_id) for ix in [G,C,V]]
 assert not gs&cs and not (gs|cs)&vs
 assert gs|cs==set(job['A_recordings'])
 for rows in [G,C,V]:assert frame.iloc[rows].failure.nunique()==2
 return {'G_sample_ids':frame.iloc[G].sample_id.tolist(),'C_sample_ids':frame.iloc[C].sample_id.tolist(),'prediction_sample_ids':frame.iloc[V].sample_id.tolist(),'G_recordings':sorted(gs),'C_recordings':sorted(cs),'prediction_recordings':sorted(vs),'recording_disjoint':True,'class_support':True}
def tensors_for_rows(frame,rows,frames,adapted,features):
 if adapted:return pixels(frame.iloc[int(rows[0])].to_dict(),frames).unsqueeze(0).cuda()
 return torch.from_numpy(np.asarray(features[rows]).copy()).cuda()
def baseline_predict(model,frame,rows,frames,adapted,features):
 model.eval();out=[];start=time.perf_counter();torch.cuda.synchronize()
 with torch.inference_mode():
  for offset in range(0,len(rows),1 if adapted else 256):
   guard();ix=np.array(rows[offset:offset+(1 if adapted else 256)],int)
   x=tensors_for_rows(frame,ix,frames,adapted,features);out.extend(model(x).cpu().numpy().tolist())
   if offset%25==0:memory_check()
 torch.cuda.synchronize();return np.array(out),{'seconds':time.perf_counter()-start,'segments':len(rows),'batch_segments':1 if adapted else 256,'includes_pixel_decode_on_cache_miss':adapted,'CNN_input_frames':frames if adapted else 0,'pixel_cache_support_frames':32 if adapted else None,'timing_protocol':'Pixel access/validation uses shared32-frame lossless cache; CNN consumes only selected16/32. Cached-feature head timing excludes CNN extraction.'}
def predict(model,frame,rows,frames,adapted,features):
 if adapted:return predict_fast(model,frame,rows,frames,features,baseline_predict)
 return baseline_predict(model,frame,rows,frames,False,features)
def compact_load(path,width,adapted,seed):
 d=torch.load(path,map_location='cpu',weights_only=True);return restore_model(d,width,adapted,seed)
def visual_fit(frame,job,condition,features,identity):
 assert input_identity()==identity,'FIT_INPUT_OR_SOURCE_DRIFT'
 c=config();folder=job_folder(job,condition)/'visual_fit';folder.mkdir(parents=True,exist_ok=True);fit_id=fit_signature(job,condition,identity);done=folder/'complete.json';out=folder/'identified_branch_predictions.csv'
 if done.exists():
  info=read(done);assert info['fit_id']==fit_id and sha(out)==info['predictions_sha256'] and sha(folder/'model.pt')==info['model_sha256'];return pd.read_csv(out,dtype={'recording_id':str,'segment_id':str}),info
 guard()
 if condition.startswith('fine_tuned'):
  estimate=cost_estimate(job,32 if '32' in condition else 16)
  if not admit(estimate['seconds'],f"fit {condition} {job['fold_name']} {job['role']}"):raise BudgetStop('FIT_NOT_ADMITTED_BEFORE_REPORTING_RESERVE')
 membership=membership_check(frame,job);write(folder/'memberships.json',membership)
 progress=read(ROOT/'progress.json');count=progress['full_visual_fits_started'];assert count<c['full_visual_fit_cap'],'FULL_FIT_CAP'
 event('FITTING_VISUAL',active_job={'condition':condition,'fold':job['fold_name'],'role':job['role'],'fit_id':fit_id},full_visual_fits_started=count+(0 if (folder/'in_progress.pt').exists() else 1))
 G=np.array(job['G'],int);C=np.array(job['C'],int);V=np.array(job['predict'],int);frames=32 if '32' in condition else 16;adapted=condition.startswith('fine_tuned');width=features.shape[1];seed=job['seed'];mean,std=standardizer(np.asarray(features[G]))
 # Helpers receive only G labels during gradient fitting. C labels arrive only below.
 yG=torch.tensor(frame.iloc[G].failure.to_numpy(float),dtype=torch.float32,device='cuda');ratio=float((len(G)-yG.sum().item())/yG.sum().item())
 random.seed(seed);np.random.seed(seed);torch.manual_seed(seed);torch.cuda.manual_seed_all(seed)
 b=original() if adapted else None
 torch.manual_seed(seed);torch.cuda.manual_seed_all(seed)
 model=Visual(b,width,mean,std,adapted).cuda();opt=optimizer(model);criterion=torch.nn.BCEWithLogitsLoss(pos_weight=torch.tensor(ratio,device='cuda'));backbone_initial=snapshot_named(b) if adapted else None;head_initial=snapshot_named(model.head);gradient_evidence=None
 loader_wait_seconds=0.;H2D_seconds=0.
 checkpoint=folder/'in_progress.pt';epoch0=0;next_batch=0;curves=[];updates=0;elapsed_prior=0.;rows_seen=0
 if checkpoint.exists():
  d=torch.load(checkpoint,map_location='cpu',weights_only=True);assert d['fit_id']==fit_id and d['precision']=='float32'
  assert d['order_seed']==seed and d['effective_batch_segments']==c['effective_batch_segments'] and d['microbatch_segments']==c['microbatch_segments'] and d['frames']==frames
  model.head.load_state_dict(d['model']['head'])
  if adapted:model.backbone.encoder.stages[-1].load_state_dict(d['model']['stage'])
  assert np.array_equal(d['model']['mean'].numpy(),mean) and np.array_equal(d['model']['std'].numpy(),std)
  loader_wait_seconds=d.get('loader_wait_seconds',0.);H2D_seconds=d.get('H2D_seconds',0.)
  opt.load_state_dict(d['optimizer']);epoch0=d['epoch'];next_batch=d['next_batch'];curves=d['curves'];updates=d['updates'];elapsed_prior=d['elapsed_seconds'];rows_seen=d['rows_seen']
  torch.set_rng_state(d['torch_rng']);torch.cuda.set_rng_state_all(d['cuda_rng']);random.setstate(d['python_rng'])
 torch.cuda.reset_peak_memory_stats();started=time.perf_counter();gpu_ms=0.;gpu_compute_ms=0.;loss_sum=0.;epoch_rows=0
 if checkpoint.exists():
  loss_sum=d['epoch_loss_sum'];epoch_rows=d['epoch_rows'];gpu_ms=d.get('gpu_ms',0.);gpu_compute_ms=d.get('gpu_compute_ms',0.)
 def save_checkpoint(epoch,batch):
  assert sha(ROOT/'config/resolved_config.json')==identity['config'],'FIXED_CONFIGURATION_DRIFT'
  resources(256*1024**2)
  value={'fit_id':fit_id,'model':model_state(model),'optimizer':opt.state_dict(),'epoch':epoch,'next_batch':batch,'curves':curves,'updates':updates,'rows_seen':rows_seen,'elapsed_seconds':elapsed_prior+time.perf_counter()-started,'epoch_loss_sum':loss_sum,'epoch_rows':epoch_rows,'torch_rng':torch.get_rng_state(),'cuda_rng':torch.cuda.get_rng_state_all(),'python_rng':random.getstate(),'precision':'float32','gpu_ms':gpu_ms,'order_seed':seed,'frames':frames,'effective_batch_segments':c['effective_batch_segments'],'microbatch_segments':c['microbatch_segments'],'order_policy':'numpy default_rng(role_seed+epoch) permutation; saved next full optimizer batch'}
  value['gpu_compute_ms']=gpu_compute_ms;value['loader_wait_seconds']=loader_wait_seconds;value['H2D_seconds']=H2D_seconds
  tmp=checkpoint.with_suffix('.writing.pt');torch.save(value,tmp);os.replace(tmp,checkpoint)
 target_epochs=c['epoch_budgets'][condition]
 assert epoch0<=target_epochs,'INCOMPATIBLE_LATE_EPOCH_CHECKPOINT'
 for epoch in range(epoch0,target_epochs):
  order=np.random.default_rng(seed+epoch).permutation(len(G));start_batch=next_batch if epoch==epoch0 else 0
  model.train();assert model.head.training
  if adapted:assert all(not module.training for module in model.backbone.modules())
  loader=iter(ordered_pixels(frame,G[order[start_batch:]],frames)) if adapted else None
  for offset in range(start_batch,len(G),c['effective_batch_segments']):
   if stop_requested():save_checkpoint(epoch,offset);raise BudgetStop('OWNED_AMENDMENT_STOP_CHECKPOINT_SAVED')
   try:guard()
   except BudgetStop:save_checkpoint(epoch,offset);raise
   batch_positions=order[offset:offset+c['effective_batch_segments']];batch_rows=G[batch_positions];actual=len(batch_rows);opt.zero_grad(set_to_none=True);batch_loss=0.
   begin=torch.cuda.Event(enable_timing=True);end=torch.cuda.Event(enable_timing=True);begin.record();segment_events=[]
   for pos,row in zip(batch_positions,batch_rows):
    if adapted:
     load_started=time.perf_counter();loaded_row,cpu_x=next(loader);loader_wait_seconds+=time.perf_counter()-load_started;assert loaded_row==row;transfer_started=time.perf_counter();x=cpu_x.unsqueeze(0).cuda();H2D_seconds+=time.perf_counter()-transfer_started
    else:x=tensors_for_rows(frame,np.array([row]),frames,adapted,features)
    compute_begin=torch.cuda.Event(enable_timing=True);compute_end=torch.cuda.Event(enable_timing=True);compute_begin.record();logit=model(x);loss=criterion(logit,yG[pos:pos+1]);assert torch.isfinite(loss),'NONFINITE_TRAINING_LOSS'
    (loss/actual).backward();compute_end.record();segment_events.append((compute_begin,compute_end));batch_loss+=float(loss.detach())
   optimizer_begin=torch.cuda.Event(enable_timing=True);optimizer_end=torch.cuda.Event(enable_timing=True);optimizer_begin.record()
   norm=torch.nn.utils.clip_grad_norm_(model.parameters(),c['gradient_clip']);assert torch.isfinite(norm),'NONFINITE_GRADIENT'
   if gradient_evidence is None:
    gradient_evidence={n:{'finite':bool(torch.isfinite(p.grad).all()),'nonzero':bool(torch.count_nonzero(p.grad))} for n,p in model.named_parameters() if p.grad is not None}
    assert all(n.startswith('head.') or (adapted and n.startswith('backbone.encoder.stages.3.')) for n in gradient_evidence)
    assert all(v['finite'] for v in gradient_evidence.values())
    if adapted:assert any(v['nonzero'] for n,v in gradient_evidence.items() if n.startswith('backbone.encoder.stages.3.'))
   opt.step();optimizer_end.record();end.record();torch.cuda.synchronize();gpu_ms+=begin.elapsed_time(end);gpu_compute_ms+=sum(a.elapsed_time(b) for a,b in segment_events)+optimizer_begin.elapsed_time(optimizer_end);updates+=1;rows_seen+=actual;loss_sum+=batch_loss;epoch_rows+=actual;memory_check()
   if updates==1:write(folder/'first_real_update_checks.json',{'fit_id':fit_id,'gradients':gradient_evidence,'head_nonzero':any(v['nonzero'] for n,v in gradient_evidence.items() if n.startswith('head.')),'all_backbone_modules_eval':all(not module.training for module in model.backbone.modules()) if adapted else True,'learning_rates':[g['lr'] for g in opt.param_groups],'target_epochs':target_epochs,'physical_batch_segments':c['microbatch_segments'],'effective_batch_segments':c['effective_batch_segments'],'disposable_optimizer_steps_added':0,'loader_wait_seconds_so_far':loader_wait_seconds,'H2D_seconds_so_far':H2D_seconds,'forward_backward_optimizer_CUDA_seconds_so_far':gpu_compute_ms/1000})
   if updates%100==0:
    save_checkpoint(epoch,offset+actual);event('FITTING_VISUAL',active_job={'condition':condition,'fold':job['fold_name'],'role':job['role'],'epoch':epoch+1,'segments_in_epoch':offset+actual,'G_segments':len(G),'optimizer_updates':updates,'fit_id':fit_id},storage=resources())
   if stop_requested():save_checkpoint(epoch,offset+actual);raise InterruptedError('OWNED_STUDY_STOP_REQUESTED_CHECKPOINT_SAVED')
  assert epoch_rows==len(G),'INCOMPLETE_OR_DUPLICATED_EPOCH_COVERAGE'
  curves.append({'epoch':epoch+1,'training_BCE_mean':loss_sum/max(1,epoch_rows),'gradient_training_segments':epoch_rows,'optimizer_updates_cumulative':updates,'training_elapsed_seconds':elapsed_prior+time.perf_counter()-started})
  next_batch=0;loss_sum=0.;epoch_rows=0;save_checkpoint(epoch+1,0);save_csv(folder/'learning_curve.csv',pd.DataFrame(curves));event('VISUAL_EPOCH_COMPLETE',condition=condition,fold=job['fold_name'],role=job['role'],epoch=epoch+1,optimizer_updates=updates)
 assert rows_seen==target_epochs*len(G) and len(curves)==target_epochs,'FINAL_EPOCH_OR_COVERAGE_MISMATCH'
 training_seconds=elapsed_prior+time.perf_counter()-started
 changed=[]
 if adapted:
  after=snapshot_named(model.backbone);changed=[n for n,h in backbone_initial.items() if h!=after[n]]
  assert changed and all(n.startswith('encoder.stages.3.') for n in changed) and not any('running_' in n for n in changed),'TRAINED_BACKBONE_SCOPE_VIOLATION'
 assert head_initial!=snapshot_named(model.head),'HEAD_DID_NOT_CHANGE'
 write(folder/'full_fit_weight_checks.json',{'fit_id':fit_id,'head_changed':True,'changed_backbone_tensor_names':changed,'earlier_backbone_and_running_buffers_unchanged':True,'frozen_CNN_used_as_hash_bound_original_feature_cache':not adapted,'first_observed_post_resume_gradient_parameters':gradient_evidence,'trainable_parameter_names':[n for n,p in model.named_parameters() if p.requires_grad],'resumed_from_saved_optimizer':checkpoint.exists() and epoch0>0,'final_epoch':target_epochs,'scheduler':'none; constant original learning-rate prefix','learning_rates':[g['lr'] for g in opt.param_groups]})
 resources(256*1024**2);model_tmp=folder/'model.writing.pt';torch.save(model_state(model),model_tmp);os.replace(model_tmp,folder/'model.pt');rawC,costC=predict(model,frame,C,frames,adapted,features)
 calibration_started=time.perf_counter();cal=calibrate(rawC,frame.iloc[C].failure.to_numpy(int));calibration_seconds=time.perf_counter()-calibration_started;write(folder/'calibrator.json',cal)
 rawV,costV=predict(model,frame,V,frames,adapted,features);prob=calibrated(rawV,cal)
 pred=frame.iloc[V][['sample_id','recording_id','segment_id','failure','action','start','end']].copy();pred['raw_visual_logit']=rawV;pred['p_visual']=prob;pred['visual_fit_id']=fit_id;save_csv(out,pred)
 calibration=frame.iloc[C][['sample_id','recording_id','segment_id','failure']].copy();calibration['raw_logit']=rawC;save_csv(folder/'calibration_holdout_logits.csv',calibration)
 # Replay first3 deterministic assessment samples with saved compact state/calibrator.
 replay_ix=V[:3];expected=rawV[:len(replay_ix)]
 del model,opt,b;gc.collect();torch.cuda.empty_cache();replayed=compact_load(folder/'model.pt',width,adapted,seed)
 if not adapted:replayed.backbone=original()
 # Replay the complete pixel -> CNN -> head -> calibrator path, also for frozen
 # fits. This independently verifies cached features against the live original.
 rawReplay,replayCost=predict(replayed,frame,replay_ix,frames,True,features)
 prob_error=float(np.max(abs(calibrated(rawReplay,cal)-prob[:len(replay_ix)])));assert prob_error<=c['probability_replay_tolerance'],'SAVED_MODEL_REPLAY_BLOCKER'
 info={'fit_id':fit_id,'condition':condition,'job':job,'identities':identity,'seed':seed,'frames':frames,'final_stage_trainable':adapted,'final_stage_name':'backbone.encoder.stages.3' if adapted else None,'normalizer_training_sample_ids':membership['G_sample_ids'],'normalizer_fixed':True,'positive_weight_from_G':ratio,'epochs_complete':target_epochs,'scheduler_horizon_epochs':5,'scheduler_kind':'none','optimizer_updates':updates,'training_segments_presentations':rows_seen,'training_wall_seconds':training_seconds,'cuda_event_seconds_including_host_gaps':gpu_ms/1000,'peak_cuda_bytes':torch.cuda.max_memory_allocated(),'raw_prediction_cost_C':costC,'raw_prediction_cost_V':costV,'replay':{'sample_ids':frame.iloc[replay_ix].sample_id.tolist(),'probability_max_abs':prob_error,'tolerance':c['probability_replay_tolerance'],'passed':True},'head_parameters':sum(p.numel() for p in replayed.head.parameters()),'loaded_backbone_parameters':read(ROOT/'shared_cache/frozen_features_complete.json')['CNN_parameters'],'trainable_backbone_parameters':sum(p.numel() for p in replayed.backbone.encoder.stages[-1].parameters()) if adapted else 0,'predictions_sha256':sha(out),'model_sha256':sha(folder/'model.pt'),'model_excluded_from_review_archive':True,'calibrator':cal}
 info['replay']['full_pixel_to_probability_path']=True;info['replay']['inference_cost']=replayCost;info['calibrator_fit_seconds']=calibration_seconds
 info['training_loader_wait_seconds']=loader_wait_seconds;info['training_H2D_seconds']=H2D_seconds;info['input_timing_scope']='Loader wait includes only non-overlapped delay; H2D uses blocking FP32 tensor transfer; model compute CUDA intervals unchanged'
 info['host_memory_observation']=memory_check();info['peak_cuda_scope']='Allocated tensors from fitting reset through C/V prediction and compact-model full pixel replay; not driver total/reserved memory';info['cuda_model_optimizer_seconds_excluding_pixel_load']=gpu_compute_ms/1000;info['CUDA_timing_policy']='Sum of CUDA-event model-forward/backward and clip/optimizer intervals, recorded after pixel load; includes dispatch/synchronization gaps within those intervals, excludes pixel decode/cache/transfer and checkpoint I/O'
 write(done,info)
 # Only this study's regenerable optimizer checkpoint is released after a verified
 # complete prediction-producing compact model exists. No historical file touched.
 if checkpoint.exists():
  write(folder/'completed_optimizer_checkpoint_receipt.json',{'fit_id':fit_id,'completed_epochs':target_epochs,'optimizer_updates':updates,'order_seed':seed,'precision':'float32','checkpoint_sha256_before_release':sha(checkpoint),'checkpoint_bytes_released':checkpoint.stat().st_size,'reason':'Completed fit; compact model/normalizer/calibrator retained for prediction replay; no continuation of a complete fit'})
  checkpoint.unlink()
 del replayed;gc.collect();torch.cuda.empty_cache()
 completed=sum(len(list((ROOT/name).glob('fold_*/**/visual_fit/complete.json'))) for name in CONDITIONS)
 event('VISUAL_FIT_COMPLETE',condition=condition,fold=job['fold_name'],role=job['role'],fit_id=fit_id,full_visual_fits_completed=completed)
 return pred,info

def sensor_job(frame,job,stats,identity):
 assert input_identity()==identity,'SENSOR_INPUT_OR_SOURCE_DRIFT'
 folder=ROOT/'sensor_reference'/job['fold_name']/job['role'];folder.mkdir(parents=True,exist_ok=True);fid=signature({'job':job,'sensor':'fixed_C1_balanced','inputs':identity});done=folder/'complete.json';out=folder/'identified_branch_predictions.csv'
 if done.exists():
  d=read(done);assert (d['fit_id']==fid or d['identities']==legacy_identity()) and sha(out)==d['predictions_sha256'];return pd.read_csv(out,dtype={'recording_id':str,'segment_id':str}),d
 membership=membership_check(frame,job);write(folder/'memberships.json',membership);G,C,V=[np.array(job[k],int) for k in ['G','C','predict']];start=time.perf_counter()
 m=sensor_fit(stats[G],frame.iloc[G].failure.to_numpy(int),stats[C],frame.iloc[C].failure.to_numpy(int));raw,p=sensor_predict(stats[V],m)
 rawC,_=sensor_predict(stats[C],m);calibration=frame.iloc[C][['sample_id','recording_id','segment_id','failure']].copy();calibration['raw_sensor_logit']=rawC;save_csv(folder/'calibration_holdout_logits.csv',calibration)
 pred=frame.iloc[V][['sample_id','recording_id','segment_id','failure']].copy();pred['raw_sensor_logit']=raw;pred['p_sensor']=p;pred['sensor_fit_id']=fid;save_csv(out,pred);write(folder/'model_and_calibrator.json',m)
 d={'fit_id':fid,'job':job,'identities':identity,'model':m,'seconds':time.perf_counter()-start,'predictions_sha256':sha(out),'fit_local_labels_only':True};write(done,d);event('SENSOR_FIT_COMPLETE',fold=job['fold_name'],role=job['role'],fit_id=fid);return pred,d

def run(resume=False):
 global STOP
 signal.signal(signal.SIGTERM,request_stop);signal.signal(signal.SIGINT,request_stop)
 c=config();assert read(ROOT/'checks/focused_checks.json')['passed'];assert read(ROOT/'checks/inherited_gradient_preflight.json')['passed'];assert read(ROOT/'checks/inherited_checkpoint_resume_preflight.json')['passed'];guard()
 assert not (ROOT/'STOP.json').exists(),'STOP_MARKER_PRESENT: preserve and explicitly clear under new resume instruction'
 check_originals();runtime_guard();frame=load_cohort();check_locked_inputs(frame);jobs=read(ROOT/'data_manifests/fit_partitions.json');identity=input_identity()
 lock=ROOT/'provenance/scientific_fit_lock.json'
 if lock.exists():assert read(lock)==identity,'FIT_SOURCE_OR_INPUT_DRIFT'
 else:write(lock,identity)
 features={n:np.load(ROOT/f'shared_cache/original_features_{n}.npy',mmap_mode='r',allow_pickle=False) for n in [16,32]};stats=np.load(ROOT/'shared_cache/sensor_statistics.npy',allow_pickle=False)
 stage_reuse(identity)
 event('AMENDMENT_CONFIG_LOADED',epoch_budgets=c['epoch_budgets'],scheduler=c['scheduler'],loader_workers=c['loader_workers'],prediction_batch_segments=c['prediction_batch_segments_finetuned'],precision=c['precision'],effective_batch_segments=c['effective_batch_segments'],microbatch_segments=c['microbatch_segments'],deadline=__import__('budget').clock(),pid=os.getpid(),input_identity=identity)
 import pixel_access
 pixel_access.resources=cache_spill_budget
 for outer in range(5):
  check_locked_inputs(frame)
  foldjobs=[j for j in jobs if j['outer_fold_original']==outer];outerjob=next(j for j in foldjobs if j['role']=='outer_assessment');inner=[j for j in foldjobs if j['role']!='outer_assessment'];sensors={}
  guard()
  if stop_requested():raise BudgetStop('STUDY_STOP_REQUESTED')
  pending=[(n,j) for n in CONDITIONS for j in foldjobs if not (job_folder(j,n)/'visual_fit/complete.json').exists()]
  projected=sum(cost_estimate(j,32 if '32' in n else 16)['seconds'] if n.startswith('fine_tuned') else 90 for n,j in pending)
  if pending and not admit(projected,f"complete outer cycle {outerjob['fold_name']}"):raise BudgetStop('COMPLETE_OUTER_CYCLE_NOT_ADMITTED')
  for j in foldjobs:sensors[j['role']]=sensor_job(frame,j,stats,identity)
  for condition in CONDITIONS:
   destination=ROOT/condition/outerjob['fold_name'];done=destination/'condition_complete.json'
   if done.exists():
    d=read(done);assert d['inputs']==identity and sha(destination/'assessment_predictions.csv')==d['assessment_sha256'];continue
   parts=[];lineage=[]
   for j in inner:
    pred,info=visual_fit(frame,j,condition,features[32 if '32' in condition else 16],identity);s,si=sensors[j['role']]
    z=pred.merge(s[['sample_id','raw_sensor_logit','p_sensor','sensor_fit_id']],on='sample_id',validate='one_to_one');assert len(z)==len(j['predict']);parts.append(z);lineage.append({'visual':info['fit_id'],'sensor':si['fit_id'],'role':j['role']})
   oof=pd.concat(parts,ignore_index=True);expected=set(frame.iloc[outerjob['T']].sample_id);assert set(oof.sample_id)==expected and not oof.sample_id.duplicated().any()
   stack_started=time.perf_counter();f2=stacker(oof[['p_visual','p_sensor']].to_numpy(),oof.failure.to_numpy(int));stack_seconds=time.perf_counter()-stack_started;stack_id=signature({'condition':condition,'outer':outer,'memberships':outerjob,'lineage':lineage,'inputs':identity,'parameters':f2});write(destination/'F2_stacker.json',{'fit_id':stack_id,'model':f2,'training_sample_ids':oof.sample_id.tolist(),'no_fusion_calibrator':True,'feature_columns':['p_visual','p_sensor'],'lineage':lineage,'fit_seconds':stack_seconds})
   save_csv(destination/'fusion_training/identified_oof_branch_probabilities.csv',oof)
   pred,info=visual_fit(frame,outerjob,condition,features[32 if '32' in condition else 16],identity);s,si=sensors['outer_assessment']
   out=pred.merge(s[['sample_id','raw_sensor_logit','p_sensor','sensor_fit_id']],on='sample_id',validate='one_to_one');out['p_fused']=fused(out[['p_visual','p_sensor']].to_numpy(),f2)
   out['threshold']=.5
   for name in ['visual','sensor','fused']:out['decision_'+name]=(out['p_'+name]>=.5).astype(int)
   out['condition']=condition;out['model_epochs']=c['epoch_budgets'][condition];out['outer_fold_original']=outer;out['fold_name']=outerjob['fold_name'];out['stacker_fit_id']=stack_id;out['config_sha256']=identity['config'];out['cohort_sha256']=identity['cohort'];out['G_membership_sha256']=signature(outerjob['G']);out['C_membership_sha256']=signature(outerjob['C']);out['branch_fit_manifest']=str((job_folder(outerjob,condition)/'visual_fit/complete.json').relative_to(ROOT));save_csv(destination/'assessment_predictions.csv',out)
   # Replay F2 arithmetic from saved keyed branch predictions and saved coefficients.
   loaded=pd.read_csv(destination/'assessment_predictions.csv');error=float(np.max(abs(fused(loaded[['p_visual','p_sensor']].to_numpy(),f2)-loaded.p_fused)))
   assert error<=1e-12
   write(done,{'condition':condition,'fold':outerjob['fold_name'],'inputs':identity,'rows':len(out),'assessment_sha256':sha(destination/'assessment_predictions.csv'),'stacker_fit_id':stack_id,'visual_fit_id':info['fit_id'],'sensor_fit_id':si['fit_id'],'F2_replay_max_abs':error,'all_inner_OOF_membership_checks':True,'new_scores_not_used_for_selection':True})
   state=read(ROOT/'progress.json');completed=state['completed_jobs'];completed.append({'condition':condition,'fold':outerjob['fold_name'],'assessment_predictions':str((destination/'assessment_predictions.csv').relative_to(ROOT))});event('CONDITION_COMPLETE',completed_jobs=completed,condition=condition,fold=outerjob['fold_name'])
  assert all((ROOT/n/outerjob['fold_name']/'condition_complete.json').exists() for n in CONDITIONS)
  event('PAIRED_OUTER_FOLD_COMPLETE',fold=outerjob['fold_name'])
 event('TRAINING_COMPLETE',active_job=None,completed_outer_folds=5)
