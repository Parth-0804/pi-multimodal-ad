"""Sixteen predetermined G-only examples; native/cache comparison and contact sheets."""
import os
for n in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[n]='2'
from common import *
import cv2,h5py,numpy as np,pandas as pd
from audit import times
cv2.setNumThreads(1)
def blob(ds):
 v=ds[()]
 if isinstance(v,(bytes,np.void)):return bytes(v)
 a=np.asarray(v);assert a.ndim==1 and a.dtype.kind in 'iu' and a.min()>=0 and a.max()<=255
 return a.astype('uint8').tobytes()
def main():
 from transformers import RTDetrImageProcessor
 f=pd.DataFrame(read(ENC/'data/cohort_and_frames.json'));jobs=read(ENC/'data/fit_partitions.json');job=next(j for j in jobs if j['fold_name']=='fold_01' and j['role']=='inner_fold_01');g=f.iloc[job['G']].copy();used=set();chosen=[]
 for a in ['pick','insert','remove','place']:
  for label in [0,1]:
   q=g.loc[(g.action==a)&(g.failure==label)].sort_values(['recording_id','start'])
   count=0
   for i,s in q.iterrows():
    if s.recording_id in used:continue
    chosen.append(int(i));used.add(s.recording_id);count+=1
    if count==2:break
   assert count==2,('AUDIT_EXAMPLE_SUPPORT',a,label)
 path=RUN/'config/audit_example_selection.json';selection={'rule':'first two chronologically ordered G actions in each action x failure stratum, without repeated recording; no predictions/errors consulted','branch_role':job['role'],'fold':'fold_01','rows':chosen,'sample_ids':f.iloc[chosen].sample_id.tolist()}
 if path.exists():assert read(path)==selection
 else:write(path,selection)
 weights=REPO/read(ENC.parent.parent/'config.json')['weights_dir'];processor=RTDetrImageProcessor.from_pretrained(weights,local_files_only=True)
 write(RUN/'checks/image_processor.json',{'config':processor.to_dict(),'source_sha256':sha(weights/'preprocessor_config.json'),'BGR_to_RGB':'explicit cv2.COLOR_BGR2RGB before processor','scaling':'processor original rescale; no added normalization','scope':'CPU processing and cache comparison, no extractor inference'})
 sensor_records=[];comparisons=[];base=read(REPO/'configs/reassemble/section1.json')
 for n,i in enumerate(chosen,1):
  s=f.iloc[i].to_dict();guard();native=RUN/'cache'/f'native_audit_{n:02d}.mp4'
  with h5py.File(REPO/s['source_path'],'r') as h:
   encoded=blob(h['hand']);native.write_bytes(encoded);native_hash=sha(native);cached_hash=sha(REPO/s['video_path']);assert native_hash==cached_hash,'NATIVE_CACHED_VIDEO_BYTES_DIFFER'
   g=h['segments_info'][s['segment_id']];annotation={'path':f"segments_info/{s['segment_id']}",'text':g['text'][()].decode(),'success':bool(g['success'][()]),'failure':s['failure'],'start':s['start'],'end':s['end'],'level':'high_level'}
   for channel in base['sensor']['channels']:
    t=times(h['timestamps'][channel][()]);inside=np.flatnonzero((t>=s['start'])&(t<=s['end']));x=np.asarray(h['robot_state'][channel][inside[0]:inside[-1]+1],float)
    for col in range(x.shape[1]):
     z=x[:,col];good=z[np.isfinite(z)];sensor_records.append({'example':n,'recording_id':s['recording_id'],'segment_id':s['segment_id'],'channel':f'{channel}[{col}]','count':len(z),'finite_fraction':float(np.isfinite(z).mean()),'native_first_time':float(t[inside[0]]),'native_last_time':float(t[inside[-1]]),'mean':float(good.mean()),'SD':float(good.std()),'min':float(good.min()),'max':float(good.max()),'units':str(h['robot_state'][channel].attrs.get('units','unspecified native units'))})
   vt=times(h['timestamps/hand'][()])
  a,b=cv2.VideoCapture(str(native)),cv2.VideoCapture(str(REPO/s['video_path']));assert a.isOpened() and b.isOpened();assert int(a.get(cv2.CAP_PROP_FRAME_COUNT))==len(vt)
  images=[];deltas=[]
  for idx in s['frames32']:
   a.set(cv2.CAP_PROP_POS_FRAMES,idx);b.set(cv2.CAP_PROP_POS_FRAMES,idx);ok,aa=a.read();ok2,bb=b.read();assert ok and ok2
   deltas.append(int(np.max(np.abs(aa.astype('int16')-bb.astype('int16')))));images.append(cv2.cvtColor(bb,cv2.COLOR_BGR2RGB))
  a.release();b.release();assert max(deltas)==0
  processed=processor(images=images,return_tensors='np')['pixel_values'];pixels=np.rint(processed/(1/255)).astype('uint8');assert __import__('hashlib').sha256(pixels.tobytes()).hexdigest()==s['pixel_content_sha256']
  selected=[images[k] for k in s['positions16_in32']];sheet=np.full((900,1120,3),255,np.uint8)
  title=f"{n:02d} {s['recording_id']} / {s['segment_id']}  {s['action']}  failure={s['failure']}"
  cv2.putText(sheet,title,(12,24),cv2.FONT_HERSHEY_SIMPLEX,.52,(0,0,0),1)
  for k,img in enumerate(selected):
   x=(k%4)*280;y=40+(k//4)*210;small=cv2.cvtColor(cv2.resize(img,(280,180)),cv2.COLOR_RGB2BGR);sheet[y:y+180,x:x+280]=small
   text=f"frame {s['frames16'][k]}  t={s['timestamps16'][k]-s['start']:.3f}s";cv2.putText(sheet,text,(x+4,y+199),cv2.FONT_HERSHEY_SIMPLEX,.40,(0,0,0),1)
  cv2.imwrite(str(RUN/'audit_examples'/f'example_{n:02d}.png'),sheet)
  write(RUN/'audit_examples'/f'example_{n:02d}.json',{'sample':s,'native_annotation':annotation,'partition':'fold_01 inner_fold_01 G','native_encoded_sha256':native_hash,'cached_encoded_sha256':cached_hash,'comparison':'identical encoded H.264/MP4 payload; independently decoded same frame indices with OpenCV; pixelwise BGR maximum absolute difference 0, hence PSNR infinite','native_cached_max_pixel_difference':max(deltas),'saved_processed_pixel_hash_matches':True,'human_semantic_review':'pending; contact sheet does not establish annotation correctness'})
  comparisons.append({'example':n,'sample_id':s['sample_id'],'recording_id':s['recording_id'],'segment_id':s['segment_id'],'encoded_bytes_identical':True,'decoded_max_absolute_error':max(deltas),'processed_cache_hash_verified':True});print('Audit contact sheet',n,flush=True)
 pd.DataFrame(sensor_records).to_csv(RUN/'audit_examples/aligned_sensor_summaries.csv',index=False,float_format='%.17g')
 write(RUN/'checks/native_cached_image_comparison.json',{'passed':True,'examples':comparisons,'method':'Payload SHA equality and same-codec decoded-pixel equality, preserving timestamp/index mapping','GPU_used':False})
if __name__=='__main__':main()
