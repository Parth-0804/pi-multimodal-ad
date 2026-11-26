"""Native keyed cohort and deterministic nested sampling. Pure formulas attributed
to snapshots of section1_features.statistics and alignment.py; no old loader called."""
from pathlib import Path
import math, os, time
import cv2,h5py,numpy as np,pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from common import ROOT,REPO,config,read,write,sha,signature,event,resources,save_csv,CONDITIONS
cv2.setNumThreads(1)

def times(values):
 x=np.asarray(values,dtype=np.float64)
 if x.ndim==2:
  if not x.shape[1] or not np.allclose(x,x[:,:1],rtol=0,atol=1e-9,equal_nan=True):raise ValueError('Per-channel timestamps differ')
  x=x[:,0]
 if x.ndim!=1 or not np.isfinite(x).all() or np.any(np.diff(x)<=0):raise ValueError('Invalid timestamps')
 return x
def resample(t,x,start,end,positions=512):
 t=times(t);x=np.asarray(x,float)
 if x.ndim==1:x=x[:,None]
 indices=np.flatnonzero((t>=start)&(t<=end));grid=np.linspace(start,end,positions);out=np.full((positions,x.shape[1]),np.nan)
 native=np.median(np.diff(t)) if len(t)>1 else 0
 for j in range(x.shape[1]):
  valid=indices[np.isfinite(x[indices,j])]
  if len(valid)<2:continue
  tv=t[valid];v=np.interp(grid,tv,x[valid,j],left=np.nan,right=np.nan);right=np.searchsorted(tv,grid,side='left')
  slots=np.flatnonzero((right>0)&(right<len(tv)));rr=right[slots];gap=(tv[rr]-tv[rr-1]>5*native)&(grid[slots]!=tv[rr]);v[slots[gap]]=np.nan;out[:,j]=v
 return out
def statistics(x):
 q=np.nanquantile(x,[.25,.5,.75],axis=0);lo,hi=np.nanmin(x,axis=0),np.nanmax(x,axis=0)
 t=np.linspace(0,1,len(x))[:,None];valid=np.isfinite(x);n=valid.sum(0);tx=np.where(valid,t,0).sum(0)/np.maximum(n,1)
 xm=np.nanmean(x,axis=0);tc=t-tx;slope=np.nansum(tc*(x-xm),0)/np.maximum(np.where(valid,tc**2,0).sum(0),1e-12)
 return np.concatenate([xm,np.nanstd(x,axis=0),q[1],lo,hi,q[0],q[2],hi-lo,np.sqrt(np.nanmean(x*x,0)),slope]).astype('float32')
def selection(indices,ts):
 indices=np.asarray(indices,int)
 if len(indices)<32:raise ValueError('Fewer than32 distinct interval frames')
 old=indices[np.linspace(0,len(indices)-1,16).round().astype(int)]
 assert len(np.unique(old))==16
 selected=set(old.tolist())
 # Maximize distance in timestamp to closest selected frame; includes end gaps.
 # Ties: smaller timestamp/index wins. Original16 are exactly preserved.
 while len(selected)<32:
  candidates=np.array([i for i in indices if int(i) not in selected]);chosen=np.array(sorted(selected));distance=np.min(abs(ts[candidates,None]-ts[chosen][None,:]),axis=1)
  selected.add(int(candidates[np.argmax(distance)]))
 new=np.array(sorted(selected));assert set(old)<=set(new)
 return old,new
def role_seed(outer,role):return int(signature({'base':42,'outer':outer,'role':role})[:8],16)%(2**31-1)
def memberships(frame,splits):
 groups=set(frame.recording_id);jobs=[];seen=set()
 for outer in splits['folds']:
  k=outer['fold'];T=sorted(set(outer['train_recordings'])&groups);E=sorted(set(outer['test_recordings'])&groups)
  assert not set(T)&set(E) and set(T)|set(E)==groups and not seen&set(E);seen|=set(E)
  inner_seen=set()
  for original in outer['inner']:
   role='inner_fold_%02d'%(original['fold']+1);A=sorted(set(original['train_recordings'])&groups);V=sorted(set(original['validation_recordings'])&groups)
   assert not set(A)&set(V) and set(A)|set(V)==set(T) and not inner_seen&set(V);inner_seen|=set(V)
   jobs.append(make_job(frame,k,role,A,V,T,E))
  assert inner_seen==set(T)
  jobs.append(make_job(frame,k,'outer_assessment',T,E,T,E))
 assert seen==groups
 assert len(splits['folds'])==5 and all(len(o['inner'])==4 for o in splits['folds'])
 return jobs
def make_job(frame,k,role,A,V,T,E):
 seed=role_seed(k,role);ix=np.flatnonzero(frame.recording_id.isin(A))
 raw,cal=next(GroupShuffleSplit(n_splits=1,test_size=.20,random_state=seed).split(ix,groups=frame.iloc[ix].recording_id))
 G=ix[raw];C=ix[cal];assessment=np.flatnonzero(frame.recording_id.isin(V));train=np.flatnonzero(frame.recording_id.isin(T))
 for label,rows in [('G',G),('C',C),('predict',assessment)]:
  if not len(rows) or frame.iloc[rows].failure.nunique()!=2:raise ValueError('CLASS_SUPPORT_BLOCKER '+str((k,role,label)))
 assert not set(frame.iloc[G].recording_id)&set(frame.iloc[C].recording_id)
 assert not (set(frame.iloc[G].recording_id)|set(frame.iloc[C].recording_id))&set(V)
 return {'outer_fold_original':k,'fold_name':'fold_%02d'%(k+1),'role':role,'seed':seed,'G':G.tolist(),'C':C.tolist(),'predict':assessment.tolist(),'T':train.tolist(),'A_recordings':A,'G_recordings':sorted(set(frame.iloc[G].recording_id)),'C_recordings':sorted(set(frame.iloc[C].recording_id)),'prediction_recordings':V,'outer_E_recordings':E}
def prepare():
 c=config();base=read(REPO/c['base_config']);data=(REPO/base['data_root']).resolve()
 inventory=REPO/base['audit_run'];allrows=pd.read_parquet(inventory/'tables_v2/cohort.parquet');frame=allrows.loc[allrows.primary_task & allrows.dual_complete].copy().reset_index(drop=True)
 recordings=pd.read_parquet(inventory/'recordings.parquet').set_index('recording_id')
 processor=processor_only()
 manifests=[];excluded=[];sensor=[];sources=[];started=time.monotonic();processed=0
 for rid,rows in frame.groupby('recording_id',sort=True):
  checkpoint=ROOT/'shared_cache/preparation'/str(rid);checkpoint.mkdir(parents=True,exist_ok=True)
  done=checkpoint/'complete_v2.json'
  if done.exists():
   d=read(done);assert d['source']==sha(ROOT/'source/data.py')
   manifests+=d['samples'];excluded+=d['excluded'];sensor.extend(np.load(checkpoint/'statistics.npy',allow_pickle=False));sources.append(d['input']);continue
  source=data/'raw/data'/str(recordings.loc[rid,'filename']);st=source.stat()
  assert st.st_size==int(recordings.loc[rid,'size_bytes']) and st.st_mtime_ns==int(recordings.loc[rid,'mtime_ns'])
  video=data/'cache/encoded_media'/str(recordings.loc[rid,'sha256'])/'hand.mp4';assert video.is_file(),'EXISTING_VIDEO_CACHE_MISSING '+str(video)
  cap=cv2.VideoCapture(str(video));assert cap.isOpened();local=[];bad=[];stats=[]
  with h5py.File(source,'r') as h:
   vt=times(h['timestamps/hand'][()]);assert len(vt)==int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
   streams={name:(times(h['timestamps'][name][()]),np.asarray(h['robot_state'][name][()],float)) for name in base['sensor']['channels']}
   for row in rows.sort_values('start').itertuples():
    native=h['segments_info'][str(row.segment_id)]
    scalar=lambda n:np.asarray(native[n][()]).item()
    assert float(scalar('start'))==row.start and float(scalar('end'))==row.end and int(not scalar('success'))==int(row.failure),'NATIVE_LABEL_OR_INTERVAL_DRIFT'
    ii=np.flatnonzero((vt>=row.start)&(vt<=row.end))
    if len(ii)<32:bad.append({'recording_id':str(rid),'segment_id':str(row.segment_id),'failure':int(row.failure),'reason':'fewer_than32_distinct_in_interval_frames'});continue
    chosen16,chosen32=selection(ii,vt);images=[];failure=None
    for index in chosen32:
     current=int(cap.get(cv2.CAP_PROP_POS_FRAMES))
     if int(index)<current or int(index)-current>64:cap.set(cv2.CAP_PROP_POS_FRAMES,int(index))
     else:
      for _ in range(int(index)-current):cap.grab()
     ok,img=cap.read()
     if not ok:failure='selected_frame_decode_failure';break
     images.append(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
    if failure:bad.append({'recording_id':str(rid),'segment_id':str(row.segment_id),'failure':int(row.failure),'reason':failure});continue
    # Exact uint8 inverse of this no-normalization processor; equivalence asserted.
    pixels=processor(images=images,return_tensors='np')['pixel_values'];u=np.rint(pixels/c['rescale_factor']).astype('uint8')
    assert np.array_equal(u.astype('float32')*np.float32(c['rescale_factor']),pixels),'PROCESSOR_CACHE_EQUIVALENCE_BLOCKER'
    sample_id=signature({'recording_id':str(rid),'segment_id':str(row.segment_id)})[:24];dest=ROOT/'shared_cache/pixels'/str(rid)/(sample_id+'.npz');dest.parent.mkdir(parents=True,exist_ok=True)
    resources(u.nbytes+256*1024**2)
    if not dest.exists():
     tmp=dest.with_suffix('.writing.npz');np.savez_compressed(tmp,pixels=u);os.replace(tmp,dest)
    x=np.concatenate([resample(t,a,row.start,row.end) for t,a in streams.values()],axis=1).astype('float32')
    assert np.isfinite(x).mean(axis=0).min()>=.89
    stats.append(statistics(x));record={'sample_id':sample_id,'recording_id':str(rid),'segment_id':str(row.segment_id),'failure':int(row.failure),'action':str(row.action),'start':float(row.start),'end':float(row.end),'original_cohort_row':int(row.Index),'frames16':chosen16.tolist(),'frames32':chosen32.tolist(),'timestamps16':vt[chosen16].tolist(),'timestamps32':vt[chosen32].tolist(),'positions16_in32':np.searchsorted(chosen32,chosen16).tolist(),'pixel_cache':str(dest.relative_to(ROOT)),'pixel_content_sha256':__import__('hashlib').sha256(u.tobytes()).hexdigest(),'source_path':os.path.relpath(source,REPO),'source_recorded_sha256':str(recordings.loc[rid,'sha256']),'source_bytes':st.st_size,'source_mtime_ns':st.st_mtime_ns,'video_path':os.path.relpath(video,REPO),'video_bytes':video.stat().st_size,'video_mtime_ns':video.stat().st_mtime_ns};local.append(record)
    evict_pixel_cache()
    processed+=1
    if processed%25==0:event('PREPARING_COMMON_COHORT',selected=processed,recording=str(rid),elapsed_seconds=time.monotonic()-started,storage=resources())
   # Bound pixel-cache growth using observed per-segment bytes without labels.
  cap.release();np.save(checkpoint/'statistics.npy',np.asarray(stats,dtype='float32'),allow_pickle=False)
  source_info={'recording_id':str(rid),'source_path':os.path.relpath(source,REPO),'bytes':st.st_size,'mtime_ns':st.st_mtime_ns,'stored_sha256':str(recordings.loc[rid,'sha256'])}
  write(done,{'source':sha(ROOT/'source/data.py'),'samples':local,'excluded':bad,'input':source_info})
  manifests+=local;excluded+=bad;sensor.extend(stats);sources.append(source_info)
  cache_bytes=sum(p.stat().st_size for p in (ROOT/'shared_cache/pixels').rglob('*.npz'))
  estimate=cache_bytes/max(1,len(manifests))*len(frame)
  write(ROOT/'checks/pixel_cache_estimate.json',{'observed_segments':len(manifests),'observed_bytes':cache_bytes,'estimated_full_pixel_bytes':estimate,'head_and_stage_checkpoint_reserve_bytes':8*2**30,'ceiling_bytes':c['new_storage_cap_bytes']})
  # Full cache rejected before fits. Fixed bounded cache with exact re-decoding.
  resources()
 samples=pd.DataFrame(manifests).sort_values(['original_cohort_row']).reset_index(drop=True)
 # Sensor append order is recording-group order; reorder explicitly by original row.
 unsorted=pd.DataFrame(manifests);order=np.argsort(unsorted.original_cohort_row.to_numpy());stats=np.asarray(sensor,dtype='float32')[order]
 assert not samples.duplicated(['recording_id','segment_id']).any()
 samples.to_json(ROOT/'data_manifests/cohort_and_frames.json',orient='records',indent=2)
 save_csv(ROOT/'data_manifests/cohort.csv',samples[['sample_id','recording_id','segment_id','failure','action','start','end','original_cohort_row']])
 save_csv(ROOT/'data_manifests/exclusions.csv',pd.DataFrame(excluded,columns=['recording_id','segment_id','failure','reason']))
 np.save(ROOT/'shared_cache/sensor_statistics.npy',stats,allow_pickle=False)
 splits=read(REPO/base['splits']);jobs=memberships(samples,splits);write(ROOT/'data_manifests/fit_partitions.json',jobs)
 write(ROOT/'data_manifests/input_manifest.json',sources)
 coverage=[]
 for o in splits['folds']:
  for phase,recs in [('train',o['train_recordings']),('assessment',o['test_recordings'])]:
   before=frame.loc[frame.recording_id.isin(recs)];after=samples.loc[samples.recording_id.isin(recs)]
   coverage.append({'fold':o['fold']+1,'phase':phase,'rows_before':len(before),'rows_after':len(after),'failures_before':int(before.failure.sum()),'failures_after':int(after.failure.sum()),'recordings_after':int(after.recording_id.nunique())})
 save_csv(ROOT/'data_manifests/cohort_coverage.csv',pd.DataFrame(coverage))
 write(ROOT/'data_manifests/cohort_lock.json',{'source':sha(ROOT/'source/data.py'),'config':sha(ROOT/'config/resolved_config.json'),'cohort_sha256':sha(ROOT/'data_manifests/cohort_and_frames.json'),'partitions_sha256':sha(ROOT/'data_manifests/fit_partitions.json'),'samples':len(samples),'failures':int(samples.failure.sum()),'recordings':int(samples.recording_id.nunique()),'planned_visual_fits':len(jobs)*4,'sensor_fits':len(jobs),'no_scores_seen':True})
 event('COMMON_COHORT_LOCKED',samples=len(samples),exclusions=len(excluded),visual_fits=len(jobs)*4)
def processor_only():
 from transformers import RTDetrImageProcessor
 return RTDetrImageProcessor.from_pretrained(REPO/config()['weights_dir'],local_files_only=True)
def load_cohort():return pd.DataFrame(read(ROOT/'data_manifests/cohort_and_frames.json'))
def evict_pixel_cache():
 cap=config()['pixel_cache_cap_bytes'];paths=list((ROOT/'shared_cache/pixels').rglob('*.npz'));used=sum(p.stat().st_size for p in paths)
 for p in sorted(paths,key=lambda p:p.stat().st_mtime_ns):
  if used<=cap:break
  size=p.stat().st_size
  assert p.resolve().is_relative_to((ROOT/'shared_cache/pixels').resolve()) and not p.is_symlink()
  p.unlink();used-=size # Own regenerable cache only; no historical/raw artifacts.

def pixels(sample,frames):
 import torch,hashlib
 path=ROOT/sample['pixel_cache']
 if path.exists():
  with np.load(path,allow_pickle=False) as z:u=z['pixels']
 else:
  cap=cv2.VideoCapture(str(REPO/sample['video_path']));assert cap.isOpened();images=[]
  for index in sample['frames32']:
   current=int(cap.get(cv2.CAP_PROP_POS_FRAMES))
   if int(index)<current or int(index)-current>64:cap.set(cv2.CAP_PROP_POS_FRAMES,int(index))
   else:
    for _ in range(int(index)-current):cap.grab()
   ok,img=cap.read();assert ok,('LOCKED_FRAME_DECODE_FAILURE',sample['sample_id'],index)
   images.append(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
  cap.release();v=processor_only()(images=images,return_tensors='np')['pixel_values'];u=np.rint(v/config()['rescale_factor']).astype('uint8')
  assert np.array_equal(u.astype('float32')*np.float32(config()['rescale_factor']),v)
  path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix('.writing.npz');np.savez_compressed(tmp,pixels=u);os.replace(tmp,path);evict_pixel_cache()
 assert hashlib.sha256(u.tobytes()).hexdigest()==sample['pixel_content_sha256'],'DECODED_PIXEL_IDENTITY_DRIFT'
 if frames==16:u=u[sample['positions16_in32']]
 return torch.from_numpy(u.astype('float32')*np.float32(config()['rescale_factor']))
