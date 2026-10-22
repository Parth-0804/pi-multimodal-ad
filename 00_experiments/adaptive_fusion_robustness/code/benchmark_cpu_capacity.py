"""Bounded CPU throughput check on fixed G inputs, no labels/scores or tuning."""
import os,time
for name in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[name]='2'
os.sched_setaffinity(0,list(range(4,12)))
import cv2,numpy as np,torch
from common import *
from prefix import original
from transformers import RTDetrImageProcessor
cv2.setNumThreads(1)
def main():
 f=read(ENC/'data/cohort_and_frames.json');j=next(j for j in read(ENC/'data/fit_partitions.json') if j['fold_name']=='fold_01' and j['role']=='inner_fold_01');s=f[j['G'][0]]
 p=RTDetrImageProcessor.from_pretrained(REPO/config()['weights_dir'],local_files_only=True);m=original('cpu');cap=cv2.VideoCapture(str(REPO/s['video_path']));images=[]
 for k in s['frames16']:
  cap.set(cv2.CAP_PROP_POS_FRAMES,k);ok,b=cap.read();assert ok;images.append(cv2.cvtColor(b,cv2.COLOR_BGR2RGB))
 cap.release();x=p(images=images,return_tensors='pt')['pixel_values'];records=[];baseline=None
 for threads in [4,8]:
  os.sched_setaffinity(0,list(range(4,4+threads)));torch.set_num_threads(threads);durations=[]
  for repeat in range(2):
   guard();start=time.perf_counter()
   with torch.inference_mode():y=torch.cat([m(x[k:k+4],'cnn_only') for k in range(0,16,4)]).mean(0).numpy()
   durations.append(time.perf_counter()-start)
   if baseline is None:baseline=y.copy()
   assert np.max(abs(y-baseline))<=1e-5
  record={'threads':threads,'CPU_ids':list(range(4,4+threads)),'seconds_per_action':durations,'training_sample_id':s['sample_id'],'max_feature_difference':float(abs(y-baseline).max())};records.append(record);print(record,flush=True)
 write(RUN/'checks/cpu_capacity_benchmark.json',{'passed':True,'GPU_used':False,'performance_only':True,'numerical_policy':'float32; original frozen CNN; no assessment outputs generated','records':records})
if __name__=='__main__':main()
