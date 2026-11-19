import os,time
for n in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[n]='2'
os.sched_setaffinity(0,[4,5])
import numpy as np,torch,cv2
from common import *
from prefix import original
from transformers import RTDetrImageProcessor
torch.set_num_threads(2);cv2.setNumThreads(1)
def main():
 guard();c=config();f=read(ENC/'data/cohort_and_frames.json');j=next(j for j in read(ENC/'data/fit_partitions.json') if j['fold_name']=='fold_01' and j['role']=='inner_fold_01');ids=j['G'][:3]
 processor=RTDetrImageProcessor.from_pretrained(REPO/c['weights_dir'],local_files_only=True);m=original('cpu');before=m.active_state();rows=[];reference=np.load(ENC/'cache/cnn_only.npy',mmap_mode='r')
 for i in ids:
  sample=f[i];start=time.perf_counter();cap=cv2.VideoCapture(str(REPO/sample['video_path']));images=[]
  for idx in sample['frames16']:
   cap.set(cv2.CAP_PROP_POS_FRAMES,idx);ok,img=cap.read();assert ok;images.append(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
  cap.release();decode=time.perf_counter()-start;x=processor(images=images,return_tensors='pt')['pixel_values'];prep=time.perf_counter()-start-decode;compute=time.perf_counter();vectors=[]
  with torch.inference_mode():
   for k in range(0,16,c['image_batch_frames']):vectors.append(m(x[k:k+c['image_batch_frames']],'cnn_only'))
  feature=torch.cat(vectors).mean(0).numpy();seconds=time.perf_counter()-compute
  rows.append({'row':i,'sample_id':sample['sample_id'],'role':'G','decode_seconds':decode,'processor_seconds':prep,'CNN_seconds':seconds,'total_seconds':time.perf_counter()-start,'feature_max_abs_vs_saved':float(abs(feature-reference[i]).max())})
  print(rows[-1],flush=True)
 assert before==m.active_state();assert all(k.startswith('backbone') for k,v in m.trace.items() if v),'FORBIDDEN_NON_CNN_TRACE'
 write(RUN/'checks/cpu_extractor_benchmark.json',{'passed':True,'samples':rows,'CPU_ids':sorted(os.sched_getaffinity(0)),'threads':2,'GPU_used':False,'state_unchanged':True,'shapes':m.shapes,'trace':m.trace,'scope':'G-only extractor timing and feature comparison; branch probability replay and workload admission remain required'})
if __name__=='__main__':main()
