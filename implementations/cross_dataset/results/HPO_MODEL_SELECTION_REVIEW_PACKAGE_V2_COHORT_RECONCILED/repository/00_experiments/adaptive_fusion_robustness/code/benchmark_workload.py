"""End-to-end G-only benchmark and runtime-only fixed-prefix admission."""
import os,time
for n in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[n]='8'
os.sched_setaffinity(0,list(range(4,12)))
import numpy as np,torch
from common import *
from engine import Bank,Branch
from quality_fusion import training_variant
import corruptions
torch.set_num_threads(8)
def main():
 c=config();c.update(threads=8,cpu_ids=list(range(4,12)));write(RUN/'config/resolved_config.json',c)
 jobs=read(ENC/'data/fit_partitions.json');j=next(j for j in jobs if j['fold_name']=='fold_01' and j['role']=='outer_assessment');b=Bank();branch=Branch(j);start=time.perf_counter();scales,sh=b.scales(j);scale_seconds=time.perf_counter()-start
 samples=j['G'][:3];records=[];replay=[]
 for i in samples:
  s=b.cohort[i];clean={'family':'clean','severity':0.,'seed':None};start=time.perf_counter();im=b.images(s);decode=time.perf_counter()-start
  for job in [clean,{'family':'image_noise','severity':.1,'seed':60101},{'family':'image_blur','severity':4.,'seed':None},training_variant(s['sample_id'],'image')]:
   start=time.perf_counter();mean,q=b.image_features(i,job);raw,p=branch.visual(mean);records.append({'sample_id':s['sample_id'],'scope':'G','kind':job['family'],'seconds':time.perf_counter()-start,'decode_once_seconds':decode})
  for job in [clean,{'family':'sensor_noise','severity':1.,'seed':60101},{'family':'sensor_time_loss','severity':.5,'seed':60101},training_variant(s['sample_id'],'sensor')]:
   start=time.perf_counter();x,q=b.sensor_features(i,job,scales,sh);raw,p=branch.sensory(x);records.append({'sample_id':s['sample_id'],'scope':'G','kind':job['family'],'seconds':time.perf_counter()-start,'decode_once_seconds':0})
  streams=b.streams(s);clean_native=[(name,t,x,np.zeros(x.shape,bool)) for name,t,x in streams];x=corruptions.statistics_for(clean_native,s['start'],s['end']);err=float(abs(x-b.clean_statistics[i]).max());assert err==0
  pixels=b.processor(images=im,return_tensors='pt')['pixel_values']
  with torch.inference_mode():v=torch.cat([b.model(pixels[k:k+4],'cnn_only') for k in range(0,16,4)]).mean(0).numpy()
  raw,p=branch.visual(v);raw0,p0=branch.visual(b.clean_vectors[i]);assert abs(p-p0)<=1e-5;replay.append({'sample_id':s['sample_id'],'raw_native_sensor_feature_max_abs':err,'raw_native_visual_probability_max_abs':abs(p-p0),'tolerance':1e-5})
  print('Complete end-to-end G benchmark',s['sample_id'],flush=True)
 b.verify_frozen();b.close();write(RUN/'checks/end_to_end_benchmark.json',{'passed':True,'G_samples':samples,'records':records,'raw_scale_seconds':scale_seconds,'clean_replay':replay,'GPU_used':False,'CPU_ids':list(range(4,12)),'threads':8})
 # Deliberately conservative: max observed family time, all training images cost a full noisy extraction, all clean qualities charged separately; 30% execution margin plus 30 min fitting/check overhead. Evaluation already has separate 3h reserve.
 maximum=lambda names:max(r['seconds'] for r in records if r['kind'] in names)
 decode=max(r['decode_once_seconds'] for r in records);image=max(maximum(['image_noise']),maximum(['image_blur']));sensor=max(maximum(['sensor_noise']),maximum(['sensor_time_loss']));clean=max(r['seconds'] for r in records if r['kind']=='clean')
 estimates=[];fold_names=sorted({z['fold_name'] for z in jobs});left=remaining()
 for count in range(1,6):
  selected=fold_names[:count];outer=[z for z in jobs if z['fold_name'] in selected and z['role']=='outer_assessment'];E=sum(len(z['predict']) for z in outer);T=sum(len(z['T']) for z in outer);unique_training=len(set(i for z in outer for i in z['T']))
  # Per-fold 18 Gaussian +3 blur +9 time faults +clean +three absence routes.
  raw=unique_training*(decode+image+clean)+T*(sensor+clean)+E*(decode+12*image+18*sensor+clean)+5*count*scale_seconds+1800
  estimate=1.30*raw;estimates.append({'fold_prefix':selected,'E_actions':E,'OOF_parent_rows':T,'seconds_with_30pct_margin':estimate,'admitted':estimate<left})
 admitted=[x for x in estimates if x['admitted']];chosen=admitted[-1]['fold_prefix'] if admitted else []
 write(RUN/'checks/workload_admission.json',{'measured_remaining_scientific_seconds':left,'estimates':estimates,'selected_prefix':chosen,'basis':'Training-only end-to-end maximum timings; no assessment scores or predictions used; three-hour reporting reserve excluded from available scientific time.'})
 state('WORKLOAD_BENCHMARKED',proposed_fold_prefix=chosen)
 print('Runtime-only prefix',chosen,'remaining h',left/3600,flush=True)
if __name__=='__main__':main()
