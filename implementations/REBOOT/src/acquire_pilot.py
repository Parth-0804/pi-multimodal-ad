"""Bounded pilot videos and numerical columns, preserving immutable source bytes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
import os
import re
import shutil
import time
import urllib.request

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from source_audit import ROOT,REPO,RUN,fetch,write

COLUMNS=['observation.state','action','timestamp','frame_index','episode_index','index','task_index']
CAMERAS=['observation.images.cam_high','observation.images.cam_low','observation.images.cam_left_wrist','observation.images.cam_right_wrist']


def streaming_fetch(item):
 dest=REPO/item['local_path'];dest.parent.mkdir(parents=True,exist_ok=True)
 expected=item['sha256']
 if dest.exists():
  h=hashlib.sha256()
  with dest.open('rb') as f:
   for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
  assert dest.stat().st_size==item['bytes'] and h.hexdigest()==expected
  return {**item,'complete':True,'reused':True}
 assert shutil.disk_usage(ROOT).free>15*1024**3
 for attempt in range(3):
  temp=dest.with_name(dest.name+'.attempt_'+str(time.time_ns())+'.partial');h=hashlib.sha256();count=0
  try:
   req=urllib.request.Request(item['url'],headers={'User-Agent':'REBOOT-bounded-feasibility/1.0'})
   with urllib.request.urlopen(req,timeout=120) as response,temp.open('xb') as out:
    for b in iter(lambda:response.read(4*1024**2),b''):
     out.write(b);h.update(b);count+=len(b)
   assert count==item['bytes'] and h.hexdigest()==expected,'Official LFS integrity mismatch'
   temp.rename(dest)
   print('DOWNLOADED',item['repo_id'],item['path'],count,flush=True)
   return {**item,'complete':True,'reused':False}
  except Exception:
   if attempt==2:raise
   time.sleep(2+attempt)


class RangeFile(io.RawIOBase):
 def __init__(self,url,size,folder):
  self.url=url;self.size=size;self.position=0;self.folder=Path(folder);self.folder.mkdir(parents=True,exist_ok=True)
  self.receipts=[];self.total_bytes=0;self.cache={}
 def readable(self):return True
 def seekable(self):return True
 def tell(self):return self.position
 def seek(self,offset,whence=0):
  self.position=offset if whence==0 else self.position+offset if whence==1 else self.size+offset
  if self.position<0:raise ValueError('Negative offset')
  return self.position
 def read(self,n=-1):
  if n<0:n=self.size-self.position
  n=min(n,self.size-self.position)
  if n<=0:return b''
  assert n<=4*1024**2 and self.total_bytes+n<16*1024**2,'Range budget exceeded: do not fetch unused depth arrays'
  a=self.position;b=a+n-1;key=(a,b)
  if key not in self.cache:
   url=self.url+'?download=true&feasibility_range='+str(a)+'_'+str(b)
   request=urllib.request.Request(url,headers={'Range':f'bytes={a}-{b}','Accept-Encoding':'identity','User-Agent':'REBOOT-column-feasibility/1.0'})
   with urllib.request.urlopen(request,timeout=90) as response:
    assert response.status==206,'Server ignored byte Range; abort instead of full download'
    content_range=response.headers.get('Content-Range');assert content_range==f'bytes {a}-{b}/{self.size}',content_range
    data=response.read(n+1)
   assert len(data)==n
   value=hashlib.sha256(data).hexdigest();path=self.folder/f'bytes_{a}_{b}_{value[:12]}.bin'
   if not path.exists():path.write_bytes(data)
   self.cache[key]=data;self.total_bytes+=n
   self.receipts.append({'source_url':self.url,'Content-Range':content_range,'source_file_bytes':self.size,
      'range_start':a,'range_end_inclusive':b,'bytes':len(data),'sha256':value,'raw_fragment_path':str(path.relative_to(REPO))})
  self.position+=n;return self.cache[key]
 def readinto(self,buffer):
  data=self.read(len(buffer));buffer[:len(data)]=data;return len(data)


def main():
 inventory={r['repo_id']:r for r in json.loads((ROOT/'00_dataset_overview/PINNED_DATASET_INVENTORY.json').read_text())}
 selected=json.loads((ROOT/'00_dataset_overview/PILOT_SELECTION.json').read_text())
 videos={};data_requests={};metadata={}
 for row in selected:
  ident=row['repo_id'];d=inventory[ident];folder=REPO/d['local_root']
  if ident not in metadata:metadata[ident]=pd.concat([pd.read_parquet(p) for p in (folder/'meta/episodes').rglob('*.parquet')]).set_index('episode_index')
  ep=metadata[ident].loc[row['episode_index']]
  tree={r['path']:r for r in json.loads((REPO/d['file_tree']).read_text()) if r['type']=='file'}
  for camera in CAMERAS:
   path=f"videos/{camera}/chunk-{int(ep[f'videos/{camera}/chunk_index']):03d}/file-{int(ep[f'videos/{camera}/file_index']):03d}.mp4"
   f=tree[path];oid=f['lfs']['oid'];assert len(oid)==64
   videos[(ident,path)]={'repo_id':ident,'revision':d['revision'],'path':path,'bytes':f['size'],'sha256':oid,
    'url':'https://huggingface.co/datasets/'+ident+'/resolve/'+d['revision']+'/'+path,'local_path':str((folder/path).relative_to(REPO))}
  path=f"data/chunk-{int(ep['data/chunk_index']):03d}/file-{int(ep['data/file_index']):03d}.parquet"
  data_requests[(ident,row['episode_index'])]=(row,d,tree[path],path,ep)
 write(ROOT/'00_dataset_overview/PILOT_DOWNLOAD_PLAN.json',{'diagnostic_episodes':len(selected),'verified_matched_pairs':0,
  'videos':list(videos.values()),'video_download_bytes':sum(r['bytes'] for r in videos.values()),
  'numerical_acquisition':'Full small sample Parquet files; exact measured-state/action/time column ranges for depth-heavy expert files. No full unused depth tables downloaded.',
  'storage_free_bytes_at_plan':shutil.disk_usage(ROOT).free,'minimum_free_bytes':15*1024**3})
 receipts=[]
 with ThreadPoolExecutor(max_workers=4) as pool:
  for r in pool.map(streaming_fetch,videos.values()):
   receipts.append(r);write(ROOT/'01_raw_dataset/PILOT_VIDEO_DOWNLOAD_MANIFEST.json',receipts)
 numerical=[]
 for (ident,index),(row,d,file,path,ep) in data_requests.items():
  slug=ident.split('/')[1];folder=REPO/d['local_root'];url='https://huggingface.co/datasets/'+ident+'/resolve/'+d['revision']+'/'+path
  if file['size']<1024**2:
   receipt=fetch(url,folder/path,file['size'],file['lfs']['oid']);table=pq.read_table(folder/path,columns=COLUMNS)
   schema_names=pq.ParquetFile(folder/path).schema_arrow.names;ranges=[];transport='Full original source file; official LFS SHA256 verified'
  else:
   reader=RangeFile(url,file['size'],ROOT/'01_raw_dataset/remote_range_evidence'/slug/f'episode_{index:03d}')
   parquet=pq.ParquetFile(reader,pre_buffer=False);schema_names=parquet.schema_arrow.names
   table=parquet.read(columns=COLUMNS);ranges=reader.receipts;transport='Pinned Parquet column pages and footer via exact HTTP206 ranges; full depth-heavy file not downloaded or globally hash-verified'
   receipt={'source_url':url,'source_file_bytes':file['size'],'official_full_file_sha256_reference':file['lfs']['oid'],
    'range_bytes_downloaded':reader.total_bytes,'range_receipts':ranges}
  frame=table.to_pandas();frame=frame[frame.episode_index==index].reset_index(drop=True)
  state=np.stack(frame['observation.state']);action=np.stack(frame['action']);timestamp=frame.timestamp.to_numpy(float)
  assert len(frame)==int(ep['length']) and state.shape==(len(frame),14) and action.shape==state.shape
  assert np.isfinite(state).all() and np.isfinite(action).all() and np.all(np.diff(timestamp)>0)
  assert np.array_equal(frame.frame_index.to_numpy(int),np.arange(len(frame)))
  out=ROOT/'03_video_sensor_alignment/numerical_projections'/slug/f'episode_{index:03d}.parquet';out.parent.mkdir(parents=True,exist_ok=True)
  if not out.exists():pq.write_table(table.filter(__import__('pyarrow').compute.equal(table['episode_index'],index)),out)
  native=json.loads((folder/'meta/info.json').read_text())
  flat=pd.DataFrame({'frame_index':frame.frame_index,'timestamp':timestamp,'episode_index':index})
  for j,name in enumerate(native['features']['observation.state']['names']):flat['observation.state/'+name]=state[:,j];flat['action_command/'+name]=action[:,j]
  flat.to_csv(out.with_suffix('.csv'),index=False)
  numerical.append({'repo_id':ident,'revision':d['revision'],'episode_index':index,'data_path':path,'native_schema_columns':schema_names,
   'projection_path':str(out.relative_to(REPO)),'projection_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
   'transport':transport,'source_receipt':receipt,'rows':len(frame),'state_shape':list(state.shape),'state_and_action_identical':bool(np.array_equal(state,action)),
   'state_action_mean_absolute_difference':float(np.mean(abs(state-action))),
   'max_nominal_30Hz_timestamp_residual_s':float(np.max(abs(timestamp-np.arange(len(frame))/30))),
   'video_metadata':{camera:{'file_index':int(ep[f'videos/{camera}/file_index']),'chunk_index':int(ep[f'videos/{camera}/chunk_index']),
     'from_timestamp':float(ep[f'videos/{camera}/from_timestamp']),'to_timestamp':float(ep[f'videos/{camera}/to_timestamp'])} for camera in CAMERAS}})
  write(ROOT/'03_video_sensor_alignment/NUMERICAL_ACQUISITION_MANIFEST.json',numerical)
  print('NUMERICAL_COLUMNS',ident,index,len(frame),'state/action_MAE',numerical[-1]['state_action_mean_absolute_difference'],flush=True)
 print('PILOT_ACQUISITION_COMPLETE',len(receipts),'videos',len(numerical),'episodes',flush=True)


if __name__=='__main__':main()
