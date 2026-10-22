"""Frozen input-level inference with fit-bound native scales and content caches."""
import time,warnings
import cv2,h5py,numpy as np,torch
from scipy.special import expit
from common import *
from quality_fusion import image_quality,sensor_quality
from native import times
import corruptions as faults
cv2.setNumThreads(1)

def resample_masked(t,x,start,end,positions=512,explicit_mask=None,time_block=None):
 # Exact vectorization of the prior no-bridge mask rule; same clean path.
 if explicit_mask is None or not np.asarray(explicit_mask).any():return original_resample(t,x,start,end,positions,explicit_mask,time_block)
 t=np.asarray(t,dtype='float64');x=np.asarray(x,float);indices=np.flatnonzero((t>=start)&(t<=end));grid=np.linspace(start,end,positions);out=np.full((positions,x.shape[1]),np.nan);native=np.median(np.diff(t))
 for col in range(x.shape[1]):
  valid=indices[np.isfinite(x[indices,col])]
  if len(valid)<2:continue
  tv=t[valid];v=np.interp(grid,tv,x[valid,col],left=np.nan,right=np.nan);right=np.searchsorted(tv,grid,side='left');slots=np.flatnonzero((right>0)&(right<len(tv)));rr=right[slots];gap=(tv[rr]-tv[rr-1]>5*native)&(grid[slots]!=tv[rr]);v[slots[gap]]=np.nan
  mt=t[np.asarray(explicit_mask)[:,col]]
  if len(mt):
   forbidden=np.searchsorted(mt,tv[1:],side='left')>np.searchsorted(mt,tv[:-1],side='right');inside=(grid[slots]>tv[rr-1])&(grid[slots]<tv[rr]);v[slots[forbidden[rr-1]&inside]]=np.nan
  if time_block is not None:v[(grid>=time_block[0])&(grid<=time_block[1])]=np.nan
  out[:,col]=v
 return out
original_resample=faults.resample
faults.resample=resample_masked

class Head(torch.nn.Module):
 def __init__(self,w):
  super().__init__();self.projection=torch.nn.Sequential(torch.nn.Linear(w,128),torch.nn.ReLU(),torch.nn.Dropout(.1));self.classifier=torch.nn.Linear(128,1)
 def forward(self,x):return self.classifier(self.projection(x)).squeeze(-1)
def linear(x,m):return np.asarray(x)@np.asarray(m['coefficient'])+m['intercept']
def calibrated(x,m):return expit(linear(np.asarray(x).reshape(-1,1),m))
class Branch:
 def __init__(self,job):
  self.job=job;v=folder('cnn_only',job);s=folder('sensor_reference',job);self.visual_complete=read(v/'complete.json');self.sensor_complete=read(s/'complete.json')
  for path,done in [(v,self.visual_complete),(s,self.sensor_complete)]:
   assert done['job']==job
   for n,h in done['outputs'].items():assert sha(path/n)==h
  state=torch.load(v/'model.pt',map_location='cpu',weights_only=True);assert state.get('stage') is None
  self.mean=state['mean'].numpy();self.std=state['std'].numpy();self.head=Head(len(self.mean));self.head.load_state_dict(state['head']);self.head.eval().requires_grad_(False);self.cal=read(v/'calibrator.json');self.sensor=read(s/'model_and_calibrator.json')
 def visual(self,mean):
  z=np.nan_to_num((np.asarray(mean,dtype='float32')-self.mean)/self.std,nan=0,posinf=0,neginf=0).astype('float32')
  with torch.inference_mode():raw=float(self.head(torch.from_numpy(z[None,:]))[0])
  return raw,float(calibrated([raw],self.cal)[0])
 def sensory(self,x):
  z=np.nan_to_num((np.asarray(x,dtype='float32')-np.asarray(self.sensor['mean'],dtype='float32'))/np.asarray(self.sensor['std'],dtype='float32'),nan=0,posinf=0,neginf=0).astype('float32');raw=float(linear(z,self.sensor['raw']));return raw,float(calibrated([raw],self.sensor['calibrator'])[0])

class Bank:
 def __init__(self,extract=True):
  from transformers import RTDetrImageProcessor
  self.c=config();self.processor=RTDetrImageProcessor.from_pretrained(REPO/self.c['weights_dir'],local_files_only=True);self.model=None
  if extract:
   from prefix import original
   self.model=original('cpu');self.initial=self.model.active_state()
  self.weights=sha(REPO/self.c['weights_dir']/'model.safetensors');self.processor_hash=sha(REPO/self.c['weights_dir']/'preprocessor_config.json');self.source=None;self.h5=None;self.cached_streams=None;self.video=None;self.cap=None;self.image_sample=None;self.image_data=None
  self.channels=read(REPO/'configs/reassemble/section1.json')['sensor']['channels'];self.cohort=read(ENC/'data/cohort_and_frames.json');self.clean_vectors=np.load(ENC/'cache/cnn_only.npy',mmap_mode='r');self.clean_statistics=np.load(ENC/'cache/sensor_statistics.npy',mmap_mode='r')
 def images(self,s):
  if self.image_sample==s['sample_id']:return self.image_data
  p=REPO/s['video_path'];st=p.stat();assert (st.st_size,st.st_mtime_ns)==(s['video_bytes'],s['video_mtime_ns'])
  if self.video!=str(p):
   if self.cap:self.cap.release()
   self.cap=cv2.VideoCapture(str(p));assert self.cap.isOpened();self.video=str(p)
  imgs=[]
  for idx in s['frames16']:
   pos=int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
   if idx<pos or idx-pos>64:self.cap.set(cv2.CAP_PROP_POS_FRAMES,idx)
   else:
    for _ in range(idx-pos):self.cap.grab()
   ok,b=self.cap.read();assert ok;imgs.append(cv2.cvtColor(b,cv2.COLOR_BGR2RGB))
  self.image_sample=s['sample_id'];self.image_data=imgs;return imgs
 def streams(self,s):
  p=REPO/s['source_path'];st=p.stat();assert (st.st_size,st.st_mtime_ns)==(s['source_bytes'],s['source_mtime_ns'])
  if self.source!=str(p):
   if self.h5:self.h5.close()
   self.h5=h5py.File(p,'r');self.source=str(p);self.cached_streams=[]
   for name in self.channels:
    t=times(self.h5['timestamps'][name][()]);x=np.asarray(self.h5['robot_state'][name][()],float);assert len(t)==len(x);self.cached_streams.append((name,t,x))
  return self.cached_streams
 def moments(self,s):
  identity={'sample':s['sample_id'],'source':s['source_recorded_sha256'],'start':s['start'],'end':s['end'],'channels':self.channels};p=RUN/'cache/moments'/(signature(identity)+'.json')
  if p.exists():return read(p)
  means=[];counts=[];m2=[]
  for _,t,x in self.streams(s):
   mask=(t>=s['start'])&(t<=s['end'])
   for col in range(x.shape[1]):
    z=x[mask,col];z=z[np.isfinite(z)];assert len(z)>0;counts.append(len(z));means.append(float(z.mean()));m2.append(float(np.sum((z-z.mean())**2)))
  d={'identity':identity,'counts':counts,'means':means,'m2':m2};write(p,d);return d
 def scales(self,job):
  identity={'G_sample_ids':[self.cohort[i]['sample_id'] for i in job['G']],'cohort':sha(ENC/'data/cohort_and_frames.json'),'channels':self.channels,'method':'Population SD; combine per-action native finite count/mean/M2; each G interval contributes once, no C/V/E values.'};p=RUN/'scales'/job['fold_name']/(job['role']+'.json')
  if p.exists():
   d=read(p);assert d['identity']==identity;return np.asarray(d['SD']),sha(p)
  count=np.zeros(22);mean=np.zeros(22);m2=np.zeros(22)
  for k,i in enumerate(job['G']):
   if k%100==0:guard()
   d=self.moments(self.cohort[i]);n=np.asarray(d['counts']);mu=np.asarray(d['means']);total=count+n;delta=mu-mean;m2+=np.asarray(d['m2'])+delta**2*count*n/total;mean+=delta*n/total;count=total
  sd=np.sqrt(m2/count);assert np.isfinite(sd).all();write(p,{'identity':identity,'SD':sd.tolist(),'finite_counts':count.astype(int).tolist(),'zero_scale_channels':np.flatnonzero(sd==0).tolist()});return sd,sha(p)
 def image_features(self,index,job):
  s=self.cohort[index];identity={'sample':s['sample_id'],'raw':s['source_recorded_sha256'],'frames':s['frames16'],'pixel_hash':s['pixel_content_sha256'],'weights':self.weights,'processor':self.processor_hash,'inference_source':sha(__file__),'prefix_source':sha(Path(__file__).with_name('prefix.py')),'quality_source':sha(Path(__file__).with_name('quality_fusion.py')),'fault_source':sha(Path(__file__).with_name('corruptions.py')),'job':job,'precision':'float32 CPU'};p=RUN/'cache/images'/(signature(identity)+'.npz')
  if p.exists():
   meta=read(p.with_suffix('.json'));assert meta['identity']==identity and meta['sha256']==sha(p);d=np.load(p,allow_pickle=False);return d['mean'],d['quality']
  images=self.images(s);ids=s['frames16'];family=job['family'];severity=job.get('severity',0);seed=job.get('seed') or 0
  if family=='frame_loss':
   keep,_=faults.survivors(16,severity,seed,(s['recording_id'],s['segment_id']),family);images=[images[k] for k in keep];ids=[ids[k] for k in keep]
  elif family in ['image_noise','image_blur']:
   images=[np.rint(faults.image_fault(im,family,severity,seed,(s['recording_id'],s['segment_id']),frame_id)[0]*255).astype('uint8') for im,frame_id in zip(images,ids)]
  assert images;quality=image_quality(images,ids)
  if family=='clean':mean=np.array(self.clean_vectors[index])
  else:
   assert self.model is not None,'EXTRACTION_NOT_INITIALIZED';x=self.processor(images=images,return_tensors='pt')['pixel_values'];values=[]
   with torch.inference_mode():
    for k in range(0,len(x),self.c['image_batch_frames']):values.append(self.model(x[k:k+self.c['image_batch_frames']],'cnn_only'))
   mean=torch.cat(values).mean(0).numpy()
  guard(mean.nbytes+quality.nbytes);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix('.writing.npz');np.savez(tmp,mean=mean,quality=quality);os.replace(tmp,p);write(p.with_suffix('.json'),{'identity':identity,'sha256':sha(p)})
  return mean,quality
 def sensor_features(self,index,job,scales,scale_hash):
  s=self.cohort[index];identity={'sample':s['sample_id'],'raw':s['source_recorded_sha256'],'interval':[s['start'],s['end']],'scales':scale_hash,'job':job,'engine_source':sha(__file__),'fault_source':sha(Path(__file__).with_name('corruptions.py')),'quality_source':sha(Path(__file__).with_name('quality_fusion.py'))};p=RUN/'cache/sensors'/(signature(identity)+'.npz')
  if p.exists():
   meta=read(p.with_suffix('.json'));assert meta['identity']==identity and meta['sha256']==sha(p);d=np.load(p,allow_pickle=False);return d['statistics'],d['quality']
  streams=self.streams(s);family=job['family'];names=[f'{name}[{i}]' for name,_,x in streams for i in range(x.shape[1])]
  if family=='clean':statistics=np.array(self.clean_statistics[index]);received=streams
  else:
   changed,meta=faults.sensor_fault(streams,names,family,job['severity'],job['seed'],(s['recording_id'],s['segment_id']),s['start'],s['end'],scales)
   with warnings.catch_warnings():
    warnings.simplefilter('ignore',RuntimeWarning);statistics=faults.statistics_for(changed,s['start'],s['end'],meta['time_bounds'])
   received=[(name,t,x) for name,t,x,_ in changed]
  quality=sensor_quality(received,s['start'],s['end'],scales);assert np.isfinite(quality).all()
  p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix('.writing.npz');np.savez(tmp,statistics=statistics,quality=quality);os.replace(tmp,p);write(p.with_suffix('.json'),{'identity':identity,'sha256':sha(p)})
  return statistics,quality
 def verify_frozen(self):
  if self.model:
   assert self.initial==self.model.active_state();assert all(not m.training for m in self.model.modules());assert all(k.startswith('backbone') for k,v in self.model.trace.items() if v)
 def close(self):
  if self.cap:self.cap.release()
  if self.h5:self.h5.close()
