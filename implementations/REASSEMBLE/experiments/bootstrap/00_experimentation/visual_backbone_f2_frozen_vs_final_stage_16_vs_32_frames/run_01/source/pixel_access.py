"""Bounded RAM/disk reads and exact re-decoding. No new image approximation."""
from collections import OrderedDict
import hashlib,threading,io,os,time
import cv2,numpy as np,torch
from common import ROOT,REPO,config,resources
from data import processor_only
LOCAL=threading.local()
RAM=OrderedDict();RAM_BYTES=0;DISK=None;DISK_BYTES=0
def pack(u):
 stream=io.BytesIO();np.savez_compressed(stream,pixels=u);return stream.getvalue()
def unpack(blob):
 with np.load(io.BytesIO(blob),allow_pickle=False) as z:return z['pixels']
def disk_index():
 global DISK,DISK_BYTES
 if DISK is None:
  paths=list((ROOT/'shared_cache/pixels').rglob('*.npz'));DISK=OrderedDict((str(p),p.stat().st_size) for p in sorted(paths,key=lambda p:p.stat().st_mtime_ns));DISK_BYTES=sum(DISK.values())
def remove_disk(path):
 global DISK_BYTES
 key=str(path)
 if key in DISK:DISK_BYTES-=DISK.pop(key)
 assert path.resolve().is_relative_to((ROOT/'shared_cache/pixels').resolve()) and not path.is_symlink()
 path.unlink(missing_ok=True)
def spill(path,blob):
 global DISK_BYTES
 disk_index();cap=config()['pixel_cache_cap_bytes']
 if len(blob)>cap:return
 if str(path) in DISK:remove_disk(path)
 while DISK and DISK_BYTES+len(blob)>cap:
  old=next(iter(DISK));remove_disk(__import__('pathlib').Path(old))
 resources(len(blob)+32*1024**2);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix('.writing.npz');tmp.write_bytes(blob);os.replace(tmp,path);DISK[str(path)]=len(blob);DISK_BYTES+=len(blob)
def decode(sample):
 if not hasattr(LOCAL,'processor'):LOCAL.processor=processor_only();LOCAL.captures=OrderedDict()
 key=sample['video_path']
 if key not in LOCAL.captures:
  if len(LOCAL.captures)>=4:
   _,old=LOCAL.captures.popitem(last=False);old.release()
  cap=cv2.VideoCapture(str(REPO/key));assert cap.isOpened();LOCAL.captures[key]=cap
 cap=LOCAL.captures[key];LOCAL.captures.move_to_end(key);images=[]
 for index in sample['frames32']:
  current=int(cap.get(cv2.CAP_PROP_POS_FRAMES))
  if int(index)<current or int(index)-current>64:cap.set(cv2.CAP_PROP_POS_FRAMES,int(index))
  else:
   for _ in range(int(index)-current):cap.grab()
  ok,img=cap.read();assert ok,('LOCKED_DECODE_FAILURE',sample['sample_id'],index)
  images.append(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
 v=LOCAL.processor(images=images,return_tensors='np')['pixel_values'];u=np.rint(v/config()['rescale_factor']).astype('uint8')
 assert np.array_equal(u.astype('float32')*np.float32(config()['rescale_factor']),v)
 return u
def input_pixels(sample,frames):
 global RAM_BYTES
 key=sample['sample_id'];disk_index();path=ROOT/sample['pixel_cache']
 # Exclusive compressed RAM/disk tiers preserve more samples than a raw uint8
 # RAM cache. Only this study's regenerable cache files move between tiers.
 if key in RAM:
  blob,stored_path=RAM.pop(key);RAM[key]=(blob,stored_path);u=unpack(blob)
 else:
  if path.exists():
   blob=path.read_bytes();u=unpack(blob)
   assert hashlib.sha256(u.tobytes()).hexdigest()==sample['pixel_content_sha256'],'PIXEL_CONTENT_DRIFT'
   remove_disk(path)
  else:u=decode(sample);blob=pack(u)
  RAM[key]=(blob,path);RAM_BYTES+=len(blob)
  while RAM_BYTES>config().get('pixel_RAM_cap_bytes',0) and len(RAM)>1:
   _,(old,old_path)=RAM.popitem(last=False);RAM_BYTES-=len(old);spill(old_path,old)
 assert hashlib.sha256(u.tobytes()).hexdigest()==sample['pixel_content_sha256'],'PIXEL_CONTENT_DRIFT'
 if frames==16:u=u[sample['positions16_in32']]
 return torch.from_numpy(u.astype('float32')*np.float32(config()['rescale_factor']))
def clear(flush=False):
 global RAM_BYTES
 if flush:
  for blob,path in RAM.values():spill(path,blob)
 RAM.clear();RAM_BYTES=0
 if hasattr(LOCAL,'captures'):
  for cap in LOCAL.captures.values():cap.release()
  LOCAL.captures.clear()
