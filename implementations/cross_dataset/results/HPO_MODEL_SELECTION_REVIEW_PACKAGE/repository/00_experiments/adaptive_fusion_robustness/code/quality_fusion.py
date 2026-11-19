"""Eight observable quality features and three fixed, augmentation-matched heads."""
import hashlib,json,warnings
import numpy as np
from scipy.special import expit
from sklearn.linear_model import LogisticRegression
from sklearn.exceptions import ConvergenceWarning
NAMES=['image_gradient','image_clipping','image_contrast','unique_frame_fraction','sensor_finite_fraction','available_channel_fraction','sensor_max_gap_fraction','sensor_relative_variation']
TRAIN_SEED=50101
ASSESS_SEEDS=(60101,60102,60103)
DEFINITIONS={
 'image_gradient':'Mean across available native RGB frames of the mean absolute horizontal/vertical neighbor difference of luminance 0.299R+0.587G+0.114B, RGB/255; equal axis weight.',
 'image_clipping':'Mean fraction of native RGB channel values <=1/255 or >=254/255 across available frames.',
 'image_contrast':'Mean population SD of native luminance per frame.',
 'unique_frame_fraction':'Number of actually received distinct frame IDs divided by 16; clipped to [0,1].',
 'sensor_finite_fraction':'Finite raw values divided by all expected raw values in each action interval, pooled over five native streams and 22 channels; missing samples/channels are NaN.',
 'available_channel_fraction':'Fraction of the 22 channels with at least two finite in-interval raw samples.',
 'sensor_max_gap_fraction':'Mean over channels of largest gap between finite native timestamps including action boundaries, divided by action duration; no finite samples gives 1.',
 'sensor_relative_variation':'log1p of mean per-channel finite population SD divided by that branch G-only raw-channel SD; each ratio capped at 1000; zero/undefined G scales omitted, unavailable channels contribute 0; no usable scales gives 0.',
 'normalization':'Weighted mean and population SD from only that outer fold fusion-training variants; sample weights 0.5/0.25/0.25. SD<=1e-6 replaced by 1; standardized q clipped to [-10,10]. p probabilities unstandardized; interactions use this q.',
 'image_missing':'All four image descriptors set 0 if no received frames; explicit absence routes to the surviving branch, never a fitted head.',
 'quality_missing':'Defined finite sentinel behavior as above; no pristine input, identity, fault name, severity, seed, label or correctness enters quality.'}
def image_quality(images,frame_ids):
 if not images:return np.zeros(4,dtype=float)
 values=[]
 for im in images:
  x=np.asarray(im,dtype=np.float32)/np.float32(255);y=.299*x[...,0]+.587*x[...,1]+.114*x[...,2]
  gradient=(np.abs(np.diff(y,axis=0)).mean()+np.abs(np.diff(y,axis=1)).mean())/2
  values.append([gradient,((x<=1/255)|(x>=254/255)).mean(),y.std()])
 return np.r_[np.mean(values,axis=0),min(1,len(set(frame_ids))/16)]
def sensor_quality(streams,start,end,scales):
 total=finite=0;available=[];gaps=[];variations=[];offset=0
 for _,t,x in streams:
  inside=(t>=start)&(t<=end);tt=t[inside];xx=x[inside]
  for col in range(x.shape[1]):
   z=xx[:,col];valid=np.isfinite(z);total+=len(z);finite+=int(valid.sum());available.append(valid.sum()>=2)
   points=np.r_[start,tt[valid],end];gaps.append(float(np.diff(points).max()/(end-start)))
   sd=scales[offset+col]
   if np.isfinite(sd) and sd>0:variations.append(min(1000,float(np.std(z[valid]))/sd) if valid.sum()>=2 else 0.)
  offset+=x.shape[1]
 return np.array([finite/max(1,total),np.mean(available),np.mean(gaps),np.log1p(np.mean(variations)) if variations else 0.])
def normalize_fit(q,weights):
 q=np.asarray(q,float);weights=np.asarray(weights,float);assert q.shape[1]==8 and np.isfinite(q).all() and (weights>0).all()
 mean=np.average(q,axis=0,weights=weights);std=np.sqrt(np.average((q-mean)**2,axis=0,weights=weights));std=np.where(std>1e-6,std,1.)
 return {'mean':mean.tolist(),'std':std.tolist(),'clip':10.}
def design(p,q,condition,normalizer):
 p=np.asarray(p,float);q=np.asarray(q,float);assert p.shape==(len(q),2) and np.isfinite(p).all() and ((p>=0)&(p<=1)).all()
 if condition=='static_augmented':return p
 z=np.clip((q-np.asarray(normalizer['mean']))/np.asarray(normalizer['std']),-10,10)
 if condition=='quality_additive':return np.c_[p,z]
 assert condition=='quality_interaction';return np.c_[p,z,p[:,0,None]*z,p[:,1,None]*z]
def fit_all(p,q,y,weights,parent_ids):
 y=np.asarray(y,int);weights=np.asarray(weights,float);assert set(np.unique(y))=={0,1};assert len(y)==len(p)==len(q)==len(parent_ids)
 for key in set(parent_ids):
  ix=np.asarray(parent_ids)==key;assert ix.sum()==3 and np.allclose(np.sort(weights[ix]),[.25,.25,.5]) and weights[ix].sum()==1
 normalizer=normalize_fit(q,weights);out={}
 for condition in ['static_augmented','quality_additive','quality_interaction']:
  x=design(p,q,condition,normalizer)
  with warnings.catch_warnings():
   warnings.simplefilter('error',ConvergenceWarning)
   model=LogisticRegression(C=1,class_weight=None,solver='lbfgs',max_iter=2000,tol=1e-4,random_state=42).fit(x,y,sample_weight=weights)
  out[condition]={'coefficient':model.coef_[0].tolist(),'intercept':float(model.intercept_[0]),'iterations':model.n_iter_.tolist(),'normalizer':normalizer,'condition':condition,'C':1,'solver':'lbfgs','max_iter':2000,'tol':1e-4,'class_weight':None,'threshold':.5,'fused_calibrator':None}
 return out
def predict(p,q,component):return expit(design(p,q,component['condition'],component['normalizer'])@np.asarray(component['coefficient'])+component['intercept'])
def route(p_visual,p_sensor,available_visual,available_sensor,fused):
 if available_visual and available_sensor:return fused,'fusion'
 if available_visual:return p_visual,'visual_only_fallback'
 if available_sensor:return p_sensor,'sensor_only_fallback'
 return None,'unavailable_both_absent'
def training_variant(sample_id,modality):
 token=json.dumps([TRAIN_SEED,str(sample_id),modality],separators=(',',':'));rng=np.random.default_rng(int.from_bytes(hashlib.sha256(token.encode()).digest()[:8],'little'))
 family=('image_noise','frame_loss') if modality=='image' else ('sensor_noise','sensor_channel_loss')
 name=family[int(rng.integers(2))];levels={'image_noise':[.02,.05,.10],'frame_loss':[.1,.3,.5],'sensor_noise':[.1,.5,1.],'sensor_channel_loss':[.1,.3,.5]}
 return {'family':name,'severity':levels[name][int(rng.integers(3))],'seed':TRAIN_SEED}
