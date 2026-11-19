"""Same predeclared probability tolerance at32frames; zero optimizer updates."""
import sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import numpy as np,torch
from common import ROOT,REPO,config,read,write
from data import load_cohort
from training import compact_load
from fast_input import ordered_pixels
from fusion import calibrated

def main():
 start=time.monotonic();frame=load_cohort();old=REPO/config()['original_run'];folder=old/'fine_tuned_16_frames/fold_01/fusion_training/inner_fold_01/visual_fit';d=read(folder/'complete.json');rows=np.array(d['job']['G'][:4]);m=compact_load(folder/'model.pt',896,True,d['seed']).eval();items=list(ordered_pixels(frame,rows,32,0));other=list(ordered_pixels(frame,rows,32,2));assert all(a==b and torch.equal(x,y) for (a,x),(b,y) in zip(items,other));outputs={};cost=[]
 with torch.inference_mode():
  for batch in [1,2]:
   out=[];torch.cuda.reset_peak_memory_stats();t=time.monotonic()
   for off in range(0,len(rows),batch):out.extend(m(torch.stack([x for _,x in items[off:off+batch]]).cuda()).cpu().numpy().tolist())
   torch.cuda.synchronize();seconds=time.monotonic()-t;outputs[batch]=calibrated(np.array(out),d['calibrator']);cost.append({'frames':32,'batch_segments':batch,'segments':len(rows),'seconds_excluding_decode':seconds,'peak_cuda_bytes':torch.cuda.max_memory_allocated()})
 same=bool(np.allclose(outputs[1],outputs[2],atol=1e-6,rtol=1e-5));result={'passed':same,'frames':32,'sample_ids':frame.iloc[rows].sample_id.tolist(),'training_G_only':True,'comparison_model':'Unchanged historical final-stage16 model used only to verify numerical batch independence at32 input frames; not a32 scientific fit','atol':1e-6,'rtol':1e-5,'probability_max_abs':float(np.max(abs(outputs[1]-outputs[2]))),'loader_pixels_and_order_exact':True,'CNN_eval':all(not mod.training for mod in m.backbone.modules()),'measurements':cost,'wall_seconds':time.monotonic()-start,'optimizer_steps':0};assert result['wall_seconds']+read(ROOT/'checks/performance_benchmark.json')['wall_seconds']<600;write(ROOT/'checks/prediction32_batch_check.json',result)
 if not same:raise AssertionError('32-frame batch2 fails fixed tolerance; must retain original batch1')
 print(result)
if __name__=='__main__':main()
