"""Targeted study tests only. Tiny synthetic records; no repository discovery."""
from pathlib import Path
import sys,unittest,json
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source'))
from data import selection,memberships,resample,statistics
from fusion import standardizer,transform,sensor_fit,sensor_predict,stacker,fused,linear,sigmoid
class Tests(unittest.TestCase):
 def test_nested_frames_and_edges(self):
  for n in [32,33,100,1001]:
   t=np.cumsum(np.linspace(.01,.06,n));a,b=selection(np.arange(n),t)
   self.assertEqual(len(set(a)),16);self.assertEqual(len(set(b)),32);self.assertTrue(set(a)<=set(b));self.assertEqual(b[0],0);self.assertEqual(b[-1],n-1);self.assertTrue((np.diff(b)>0).all())
   self.assertTrue(np.array_equal(a,np.arange(n)[np.linspace(0,n-1,16).round().astype(int)]))
  with self.assertRaises(ValueError):selection(np.arange(31),np.arange(31))
 def test_fixed_group_partitions_and_graph(self):
  f=pd.DataFrame([{'recording_id':str(i),'failure':y} for i in range(40) for y in [0,1]])
  outer=[]
  for k in range(5):
   E={str(i) for i in range(40) if i%5==k};T=set(f.recording_id)-E;order=sorted(T);parts=[]
   for j in range(4):
    V=set(order[j::4]);parts.append({'fold':j,'train_recordings':sorted(T-V),'validation_recordings':sorted(V)})
   outer.append({'fold':k,'train_recordings':sorted(T),'test_recordings':sorted(E),'inner':parts})
  a=memberships(f,{'folds':outer});b=memberships(f,{'folds':outer});self.assertEqual(a,b);self.assertEqual(len(a)*4,100)
  for job in a:
   self.assertFalse(set(job['G'])&set(job['C']));self.assertFalse((set(job['G'])|set(job['C']))&set(job['predict']))
 def test_degenerate_calibration_blocked_not_redrawn(self):
  f=pd.DataFrame({'recording_id':['a','b','c','d'],'failure':[0,0,0,0]})
  from data import make_job
  with self.assertRaisesRegex(ValueError,'CLASS_SUPPORT'):make_job(f,0,'role',['a','b','c'],['d'],['a','b','c'],['d'])
 def test_fit_local_normalizer_and_sensor_formula(self):
  rng=np.random.default_rng(42);G=rng.normal(size=(40,4));C=rng.normal(size=(20,4));E=rng.normal(size=(5,4))
  yG=np.arange(40)%2;yC=np.arange(20)%2;m=sensor_fit(G,yG,C,yC)
  self.assertTrue(np.allclose(m['mean'],G.mean(0)))
  raw,p=sensor_predict(E,m);self.assertTrue(np.isfinite(p).all());self.assertTrue(((p>=0)&(p<=1)).all())
  self.assertTrue(np.allclose(raw,linear(transform(E,np.array(m['mean']),np.array(m['std'])),m['raw'])))
 def test_F2_probability_link_not_logit_mixing(self):
  x=np.array([[.1,.2],[.2,.7],[.7,.3],[.9,.8]]);m=stacker(x,np.array([0,0,1,1]))
  self.assertTrue(np.allclose(fused(x,m),sigmoid(m['intercept']+x@np.array(m['coefficient']))))
  self.assertFalse(m['balanced'])
 def test_held_label_sentinel_not_available_to_fit_helpers(self):
  class Labels:
   def __init__(self):self.seen=[]
   def __getitem__(self,i):
    if i>=60:raise AssertionError('Assessment label entered fitting')
    self.seen.append(i);return i%2
   def __array__(self,*a,**kw):raise AssertionError('Global label vector requested')
  labels=Labels();G=list(range(40));C=list(range(40,60));E=list(range(60,70));rng=np.random.default_rng(1);x=rng.normal(size=(70,3))
  m=sensor_fit(x[G],np.array([labels[i] for i in G]),x[C],np.array([labels[i] for i in C]));sensor_predict(x[E],m)
  # The actual visual head and fixed normalizer receive only G targets; held-out
  # feature inference cannot change that normalizer or request held-out labels.
  import torch
  from visual_model import Visual
  mean,std=standardizer(x[G]);visual=Visual(None,3,mean,std,False);target=torch.tensor([labels[i] for i in G],dtype=torch.float32)
  loss=torch.nn.functional.binary_cross_entropy_with_logits(visual(torch.tensor(x[G],dtype=torch.float32)),target);loss.backward();self.assertTrue(any(p.grad is not None and bool(torch.count_nonzero(p.grad)) for p in visual.head.parameters()))
  before=visual.mean.clone();visual.eval()
  with torch.no_grad():visual(torch.tensor(x[E],dtype=torch.float32))
  self.assertTrue(torch.equal(before,visual.mean));self.assertTrue(np.array_equal(visual.std.numpy(),std))
  self.assertEqual(set(labels.seen),set(G+C))
 def test_attributed_resampling_and_statistics(self):
  t=np.linspace(0,1,101);x=np.column_stack([t,2*t]);z=resample(t,x,0,1)
  self.assertEqual(z.shape,(512,2));self.assertEqual(statistics(z).shape,(20,));self.assertTrue(np.allclose(z[:,1],2*z[:,0],equal_nan=True))
 def test_partial_batch_gradient_normalization(self):
  import torch
  torch.manual_seed(4);x=torch.randn(5,3);y=torch.tensor([0.,1.,0.,1.,1.]);a=torch.nn.Linear(3,1);b=torch.nn.Linear(3,1);b.load_state_dict(a.state_dict())
  torch.nn.functional.binary_cross_entropy_with_logits(a(x).flatten(),y).backward()
  for i in range(5):(torch.nn.functional.binary_cross_entropy_with_logits(b(x[i:i+1]).flatten(),y[i:i+1])/5).backward()
  for pa,pb in zip(a.parameters(),b.parameters()):self.assertTrue(torch.allclose(pa.grad,pb.grad,atol=1e-7))
 def test_AP_definition_and_fixed_threshold(self):
  from evaluation import metrics
  from sklearn.metrics import average_precision_score
  y=np.array([0,1,0,1]);p=np.array([.1,.2,.3,.4]);m=metrics(y,p)
  self.assertEqual(m['AP'],average_precision_score(y,p));self.assertEqual(m['recall'],0);self.assertEqual(m['threshold'],.5)
  self.assertIsNone(metrics(np.zeros(3,int),np.array([.1,.2,.3]))['AP'])
 def test_contrast_definitions_and_interaction(self):
  from evaluation import contrasts
  from common import CONDITIONS
  values={(n,b):v for n,v in zip(CONDITIONS,[.4,.5,.45,.6]) for b in ['visual','fused']}
  values.update({(n,'sensor'):.48 for n in CONDITIONS});d=contrasts(values)
  self.assertAlmostEqual(d['fused:fine_tuned16_minus_frozen16'],.1);self.assertAlmostEqual(d['fused:frozen32_minus_frozen16'],.05);self.assertAlmostEqual(d['fused:interaction'],.05)
 def test_checkpoint_order_epoch_tail_resume(self):
  seed=123;G=np.arange(23);all_batches=[]
  for epoch in range(5):
   order=np.random.default_rng(seed+epoch).permutation(len(G));all_batches.extend((epoch,order[offset:offset+8].tolist()) for offset in range(0,len(G),8))
  epoch,next_batch=2,16;resumed=[]
  for ep in range(epoch,5):
   order=np.random.default_rng(seed+ep).permutation(len(G))
   resumed.extend((ep,order[offset:offset+8].tolist()) for offset in range(next_batch if ep==epoch else 0,len(G),8))
  self.assertEqual(resumed,all_batches[8:]);self.assertEqual(len(resumed[0][1]),7)
 def test_lossless_compressed_pixel_cache(self):
  from pixel_access import pack,unpack
  rng=np.random.default_rng(45);u=rng.integers(0,256,size=(32,3,8,9),dtype='uint8');u[0]=0;u[-1]=255
  v=unpack(pack(u));self.assertEqual(v.dtype,np.dtype('uint8'));self.assertTrue(np.array_equal(u,v))
 def test_attributed_pure_formulas_match_original_source(self):
  import ast
  from common import REPO
  scope={'np':np}
  for path,names in [('src/reassemble/alignment.py',['timestamps_1d','interval_indices','resample_progress']),('src/reassemble/section1_features.py',['statistics'])]:
   tree=ast.parse((REPO/path).read_text());selected=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names];self.assertEqual(len(selected),len(names));exec(compile(ast.Module(body=selected,type_ignores=[]),path,'exec'),scope)
  rng=np.random.default_rng(73);t=np.concatenate([np.arange(30)*.01,np.arange(30,80)*.01+.1]);x=rng.normal(size=(80,4));x[10:13,1]=np.nan
  for start,end in [(.005,.895),(.1,.7),(.01,.4)]:
   a=resample(t,x,start,end);b=scope['resample_progress'](t,x,start,end);self.assertTrue(np.array_equal(a,b,equal_nan=True));self.assertTrue(np.array_equal(statistics(a.astype('float32')),scope['statistics'](b.astype('float32')),equal_nan=True))
 def test_exclusive_RAM_disk_cache_retains_working_set(self):
  import tempfile,hashlib
  import pixel_access as cache
  from common import ROOT
  fields=['ROOT','config','resources','decode','RAM','RAM_BYTES','DISK','DISK_BYTES'];previous={name:getattr(cache,name) for name in fields};calls=[]
  try:
   with tempfile.TemporaryDirectory(prefix='unit_lossless_cache_',dir=ROOT/'temporary') as temporary:
    cache.ROOT=Path(temporary);cache.RAM=__import__('collections').OrderedDict();cache.RAM_BYTES=0;cache.DISK=None;cache.DISK_BYTES=0
    cache.config=lambda:{'pixel_cache_cap_bytes':30000,'pixel_RAM_cap_bytes':15000,'rescale_factor':1/255};cache.resources=lambda extra:None
    rng=np.random.default_rng(34);arrays={str(i):rng.integers(0,256,(32,3,8,8),dtype='uint8') for i in range(6)}
    def decode(s):calls.append(s['sample_id']);return arrays[s['sample_id']]
    cache.decode=decode
    for epoch in range(3):
     for key,u in arrays.items():
      sample={'sample_id':key,'pixel_cache':f'shared_cache/pixels/recording/{key}.npz','pixel_content_sha256':hashlib.sha256(u.tobytes()).hexdigest(),'positions16_in32':list(range(16))}
      actual=cache.input_pixels(sample,16).numpy();self.assertTrue(np.array_equal(actual,u[:16].astype('float32')*np.float32(1/255)))
      self.assertLessEqual(cache.RAM_BYTES,15000);self.assertLessEqual(cache.DISK_BYTES,30000);self.assertFalse({str(path) for blob,path in cache.RAM.values()}&set(cache.DISK))
    self.assertEqual(len(calls),6)
  finally:
   for name,value in previous.items():setattr(cache,name,value)
 def test_core_standardizer_small_variance_floor(self):
  mean,std=standardizer(np.array([[0,0],[1e-7,1e-3]],dtype='float32'));self.assertEqual(std[0],1);self.assertLess(std[1],1)
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
 from common import ROOT,write
 write(ROOT/'checks/unit_test_results.json',{'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'passed':result.wasSuccessful(),'scope':'New study only, synthetic inputs; dynamic real-CNN gradient/replay tests separate'})
 raise SystemExit(0 if result.wasSuccessful() else 1)
