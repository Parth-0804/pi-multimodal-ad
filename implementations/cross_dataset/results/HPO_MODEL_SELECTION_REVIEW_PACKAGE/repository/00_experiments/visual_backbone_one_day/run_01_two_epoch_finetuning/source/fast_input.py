"""Fine-tuned-only ordered bounded prefetch; exact pixels, no augmentation/RNG."""
from concurrent.futures import ThreadPoolExecutor
from collections import deque
import hashlib,time
import numpy as np,torch,cv2
from common import ROOT,config
import pixel_access

def readonly_pixels(sample,frames):
 # Worker-local decoder/processor; no worker mutates disk or shared LRU state.
 path=ROOT/sample['pixel_cache']
 if sample['sample_id'] in pixel_access.RAM:u=pixel_access.unpack(pixel_access.RAM[sample['sample_id']][0])
 elif path.exists():u=pixel_access.unpack(path.read_bytes())
 else:u=pixel_access.decode(sample)
 assert hashlib.sha256(u.tobytes()).hexdigest()==sample['pixel_content_sha256'],'PIXEL_CONTENT_DRIFT'
 if frames==16:u=u[sample['positions16_in32']]
 return torch.from_numpy(u.astype('float32')*np.float32(config()['rescale_factor']))

def ordered_pixels(frame,rows,frames,workers=None):
 workers=config()['loader_workers'] if workers is None else workers
 if not workers:
  for row in rows:yield int(row),pixel_access.input_pixels(frame.iloc[int(row)].to_dict(),frames)
  return
 cv2.setNumThreads(1)
 # Only two in-flight tensors; return in sampler order regardless of completion.
 with ThreadPoolExecutor(max_workers=workers,thread_name_prefix='ordered-pixels') as pool:
  pending=deque();it=iter(rows)
  def fill():
   try:
    row=int(next(it));sample=frame.iloc[row].to_dict();pending.append((row,pool.submit(readonly_pixels,sample,frames)));return True
   except StopIteration:return False
  for _ in range(workers):fill()
  while pending:
   row,future=pending.popleft();yield row,future.result();fill()
