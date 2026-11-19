"""Explicit unchanged-artifact reuse and bounded optimized inference."""
import shutil,time
from pathlib import Path
import numpy as np,torch
from common import ROOT,REPO,config,read,write,sha,event
from fast_input import ordered_pixels
from budget import guard

def legacy_identity():return read(REPO/config()['original_run']/'provenance/scientific_fit_lock.json')

def stage_reuse(identity):
 old=REPO/config()['original_run'];records=[]
 # Validate all shared data identities and frozen training hyperparameters first.
 legacy=legacy_identity()
 for key in ['cohort','partitions','sensor_statistics','feature_metadata','original_pretrained_identity','runtime_identity']:assert identity[key]==legacy[key],('REUSE_INPUT_MISMATCH',key)
 original=read(old/'config/resolved_config.json');current=config()
 allowed={'amendment_id','epoch_budgets','scheduler','original_run','prediction_batch_segments_finetuned','loader_workers','wall_seconds','scientific_authority'}
 assert {k:v for k,v in current.items() if k not in allowed}=={k:v for k,v in original.items() if k not in allowed},'FROZEN_POLICY_CHANGED'
 for condition in ['frozen_16_frames','frozen_32_frames']:
  for done in (old/condition).glob('fold_*/condition_complete.json'):
   d=read(done);folder=done.parent;assert d['inputs']==legacy and sha(folder/'assessment_predictions.csv')==d['assessment_sha256']
   for p in folder.glob('**/visual_fit/complete.json'):
    f=read(p);assert f['epochs_complete']==5 and f['identities']==legacy and sha(p.parent/'model.pt')==f['model_sha256'] and sha(p.parent/'identified_branch_predictions.csv')==f['predictions_sha256']
   target=ROOT/condition/folder.name
   if not target.exists():shutil.copytree(folder,target)
   nd=read(target/'condition_complete.json')
   if nd['inputs']==legacy or nd.get('reused_unchanged_original',{}).get('original_inputs')==legacy:
    nd.update(inputs=identity,reused_unchanged_original={'directory':str(folder.resolve()),'original_condition_complete_sha256':sha(done),'original_inputs':legacy,'assessment_byte_identical':True})
    write(target/'condition_complete.json',nd)
   assert sha(target/'assessment_predictions.csv')==d['assessment_sha256']
   records.append({'condition':condition,'fold':folder.name,'path':str(folder.resolve()),'assessment_sha256':d['assessment_sha256'],'epochs':5,'reuse':'entire unchanged frozen condition'})
 for done in (old/'sensor_reference').glob('fold_*/*/complete.json'):
  d=read(done);assert d['identities']==legacy and sha(done.parent/'identified_branch_predictions.csv')==d['predictions_sha256']
  target=ROOT/'sensor_reference'/done.parent.parent.name/done.parent.name
  if not target.exists():shutil.copytree(done.parent,target)
 write(ROOT/'provenance/reused_unchanged_artifacts.json',records)
 completed=[{'condition':r['condition'],'fold':r['fold'],'assessment_predictions':f"{r['condition']}/{r['fold']}/assessment_predictions.csv"} for r in records]
 # Retain later already completed amendment conditions on resume.
 prior=read(ROOT/'progress.json')['completed_jobs']
 for row in prior:
  if row not in completed:completed.append(row)
 event('COMPATIBLE_ARTIFACTS_REUSED',completed_jobs=completed)

def predict_fast(model,frame,rows,frames,features,baseline):
 if not model.adapted:return baseline(model,frame,rows,frames,True,features)
 model.eval();batch=config()['prediction_batch_segments_finetuned'];out=[];start=time.perf_counter();load_seconds=0.;h2d_seconds=0.;compute_seconds=0.;pending=[]
 torch.cuda.synchronize()
 with torch.inference_mode():
  iterator=iter(ordered_pixels(frame,rows,frames));consumed=[]
  for offset in range(0,len(rows),batch):
   guard();expected=list(map(int,rows[offset:offset+batch]));t=time.perf_counter();items=[next(iterator) for _ in expected];load_seconds+=time.perf_counter()-t
   assert [r for r,_ in items]==expected;consumed.extend(expected);t=time.perf_counter();x=torch.stack([v for _,v in items]).cuda();torch.cuda.synchronize();h2d_seconds+=time.perf_counter()-t;t=time.perf_counter();out.extend(model(x).cpu().numpy().tolist());torch.cuda.synchronize();compute_seconds+=time.perf_counter()-t
  assert consumed==list(map(int,rows))
 return np.array(out),{'seconds':time.perf_counter()-start,'segments':len(rows),'batch_segments':batch,'loader_workers':config()['loader_workers'],'loader_wait_seconds':load_seconds,'H2D_seconds':h2d_seconds,'forward_D2H_seconds':compute_seconds,'includes_pixel_decode_on_cache_miss':True,'CNN_input_frames':frames,'pixel_cache_support_frames':32,'timing_protocol':'Bounded ordered two-worker option; no-grad/eval; FP32; same exact pixels; wait excludes overlapped loader work'}
