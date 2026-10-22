"""Reproducible synthetic exact-equivalence check; no scientific inference."""
import importlib.util
from pathlib import Path
root=Path(__file__).resolve().parents[3]
sp=importlib.util.spec_from_file_location('versioned',root/'run_after_encoder.py');module=importlib.util.module_from_spec(sp);sp.loader.exec_module(module)
import numpy as np,time
from run02_input_adapter import resample,_original_resample
from common import RUN,write
rng=np.random.default_rng(42);cases=0;timings={'original_seconds':0.,'vectorized_seconds':0.}
for n in [25,121,5001]:
 t=np.cumsum(rng.uniform(.001,.003,n));x=rng.normal(size=(n,3));start,end=t[2],t[-3]
 for mask_kind in ['none','random','channel','time']:
  mask=np.zeros(x.shape,bool)
  if mask_kind=='random':mask=rng.random(x.shape)<.3
  if mask_kind=='channel':mask[:,1]=True
  if mask_kind=='time':mask[n//3:2*n//3,:]=True
  altered=x.copy();altered[mask]=np.nan;altered[n//4,2]=np.nan
  for time_block in [None,(t[n//3],t[2*n//3])]:
   a=time.perf_counter();old=_original_resample(t,altered,start,end,512,mask,time_block);timings['original_seconds']+=time.perf_counter()-a
   a=time.perf_counter();new=resample(t,altered,start,end,512,mask,time_block);timings['vectorized_seconds']+=time.perf_counter()-a
   np.testing.assert_array_equal(new,old);cases+=1
write(RUN/'checks/vectorized_mask_equivalence.json',{'passed':True,'cases':cases,'comparison':'Exact array equality including NaN locations against original implementation','scope':'Synthetic timestamps/signals only; no assessment outcomes or predictor changes',**timings})
print({'passed':True,'cases':cases,**timings})

# Cache serialization must reproduce the live vectors exactly before frame-loss reuse.
import tempfile
from inference import cache_frames
from common import read
with tempfile.TemporaryDirectory(dir=RUN/'cache',prefix='synthetic_frame_cache_') as directory:
 path=Path(directory)/'frames.npy';features=np.arange(128,dtype='float32').reshape(16,8)
 cache_frames(path,features,{'scope':'synthetic check'})
 assert read(path.with_suffix('.json'))['live_cache_bitwise_equal']
 np.testing.assert_array_equal(np.load(path,allow_pickle=False),features)
write(RUN/'checks/live_frame_cache_serialization.json',{'passed':True,'scope':'Synthetic float32 per-frame vectors; real clean caches additionally assert bitwise equality at every write'})
