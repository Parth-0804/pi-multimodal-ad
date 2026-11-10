"""Bounded, training-derived FP32 inference/loader measurement, zero optimizer steps."""
import sys,time,json,subprocess,gc
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import numpy as np,torch
from common import ROOT,REPO,read,write,config,sha
from data import load_cohort
from training import compact_load
from fast_input import ordered_pixels
from fusion import calibrated

def main():
 started=time.monotonic();frame=load_cohort();old=REPO/config()['original_run'];folder=old/'fine_tuned_16_frames/fold_01/fusion_training/inner_fold_01/visual_fit';d=read(folder/'complete.json');job=d['job'];rows=np.array(job['G'][:8]);m=compact_load(folder/'model.pt',896,True,job['seed']).eval();results={'tolerance_predeclared':{'atol':1e-6,'rtol':1e-5},'sample_ids':frame.iloc[rows].sample_id.tolist(),'training_G_only':True,'additional_optimizer_steps':0,'baseline_postfit_C_seconds':d['raw_prediction_cost_C']['seconds'],'baseline_postfit_V_seconds':d['raw_prediction_cost_V']['seconds'],'CPU_affinity_kept':list(__import__('os').sched_getaffinity(0)),'CPU_entitlement':'Host cpuset0-15 visible; no explicit entitlement to increase prior4CPU allocation; retain4','benchmarks':[]};pixels={};outputs={}
 with torch.inference_mode():
  list(ordered_pixels(frame,rows,16,0)) # identical warm compressed sample set for both paths
  results['loader_measurement_scope']='Same8 G segments, warmed compressed RAM cache; no claim of cold-decode throughput'
  for workers in [0,2]:
   t=time.monotonic();items=list(ordered_pixels(frame,rows,16,workers));seconds=time.monotonic()-t
   pixels[workers]=items;results['benchmarks'].append({'kind':'loader','workers':workers,'segments':len(items),'seconds':seconds,'segments_per_second':len(items)/seconds,'prefetch_bound':2 if workers else 0,'worker_type':'threads with worker-local processor/video capture; OpenCV internal threads1' if workers else 'original compressed exclusive RAM/disk LRU'})
  assert [a for a,_ in pixels[0]]==[a for a,_ in pixels[2]]==rows.tolist()
  assert all(torch.equal(x,y) for (_,x),(_,y) in zip(pixels[0],pixels[2]))
  for batch in [1,2]:
   torch.cuda.reset_peak_memory_stats();logits=[];h2d=0.;forward=0.;start=time.monotonic()
   for off in range(0,len(rows),batch):
    t=time.monotonic();x=torch.stack([v for _,v in pixels[0][off:off+batch]]).cuda();torch.cuda.synchronize();h2d+=time.monotonic()-t;t=time.monotonic();logits.extend(m(x).cpu().numpy().tolist());torch.cuda.synchronize();forward+=time.monotonic()-t
   seconds=time.monotonic()-start;outputs[batch]=calibrated(np.array(logits),d['calibrator']);results['benchmarks'].append({'kind':'prediction','batch_segments':batch,'seconds_excluding_decode':seconds,'H2D_seconds':h2d,'forward_D2H_seconds':forward,'segments':len(rows),'segments_per_second_excluding_decode':len(rows)/seconds,'peak_cuda_bytes':torch.cuda.max_memory_allocated()})
  same=bool(np.allclose(outputs[1],outputs[2],atol=1e-6,rtol=1e-5));err=float(np.max(abs(outputs[1]-outputs[2])))
 results.update(loader_order_and_pixels_exact=True,batch_independence_all_CNN_eval=all(not x.training for x in m.backbone.modules()),prediction_batch_agreement_passed=same,probability_max_abs=err)
 loader={x['workers']:x for x in results['benchmarks'] if x['kind']=='loader'};pred={x['batch_segments']:x for x in results['benchmarks'] if x['kind']=='prediction'}
 results['chosen_loader_workers']=2 if loader[2]['seconds']<loader[0]['seconds']*.95 else 0
 results['chosen_prediction_batch_segments']=2 if same and pred[2]['seconds_excluding_decode']<pred[1]['seconds_excluding_decode']*.95 else 1
 results['wall_seconds']=time.monotonic()-started;assert results['wall_seconds']<600,'OPTIONAL_GPU_BENCHMARK_TIME_LIMIT'
 write(ROOT/'checks/performance_benchmark.json',results);print(json.dumps(results,indent=2))
if __name__=='__main__':main()
