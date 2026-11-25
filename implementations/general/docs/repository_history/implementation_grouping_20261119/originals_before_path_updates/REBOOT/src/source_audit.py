"""Public pinned-source metadata audit. No full dataset or model training."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import hashlib
import json
import os
import shutil
import time
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent
RUN=REPO/json.loads((ROOT/'00_dataset_overview/ACTIVE_RUN.json').read_text())['run']
RAW=ROOT/'01_raw_dataset'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_name(path.name+'.writing')
 temp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n');temp.replace(path)

def fetch(url,dest,expected_bytes=None,expected_sha256=None):
 dest=Path(dest);dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():
  if expected_bytes is not None:assert dest.stat().st_size==expected_bytes
  if expected_sha256 is not None:assert sha(dest)==expected_sha256
  return {'url':url,'path':str(dest.relative_to(REPO)),'bytes':dest.stat().st_size,'sha256':sha(dest),'reused':True}
 assert shutil.disk_usage(ROOT).free>15*1024**3,'Minimum15GiB free disk gate'
 request=urllib.request.Request(url,headers={'User-Agent':'REBOOT-independent-feasibility/1.0'})
 for attempt in range(4):
  try:
   with urllib.request.urlopen(request,timeout=90) as r:
    data=r.read()
   break
  except Exception:
   if attempt==3:raise
   time.sleep(1+attempt)
 if expected_bytes is not None:assert len(data)==expected_bytes,(url,len(data),expected_bytes)
 value=hashlib.sha256(data).hexdigest()
 if expected_sha256 is not None:assert value==expected_sha256,(url,'SOURCE_HASH_MISMATCH')
 with dest.open('xb') as f:f.write(data)
 return {'url':url,'path':str(dest.relative_to(REPO)),'bytes':len(data),'sha256':value,'reused':False,'download_utc':dt.datetime.now(dt.timezone.utc).isoformat()}


def dataset(item):
 ident=item['id'];rev=item['sha'];slug=ident.split('/')[1];dest=RAW/'official_release'/slug/rev
 api='https://huggingface.co/api/datasets/'+ident+'/tree/'+rev+'?recursive=true&expand=false&limit=1000'
 receipt=fetch(api,RUN/'evidence/file_trees'/(slug+'.json'));tree=json.loads((REPO/receipt['path']).read_text())
 files=[r for r in tree if r['type']=='file'];receipts=[receipt]
 selected=[r for r in files if r['path'].startswith('meta/') or r['path']=='README.md']
 for row in selected:
  if row.get('size',0)>5*1024**2:continue
  url='https://huggingface.co/datasets/'+ident+'/resolve/'+rev+'/'+row['path']
  oid=row.get('lfs',{}).get('oid');expected=oid if oid and len(oid)==64 else None
  receipts.append(fetch(url,dest/row['path'],row['size'],expected))
 info=json.loads((dest/'meta/info.json').read_text())
 return {'repo_id':ident,'revision':rev,'files':len(files),'total_remote_bytes':sum(r['size'] for r in files),
  'total_episodes':info.get('total_episodes'),'total_frames':info.get('total_frames'),'fps':info.get('fps'),
  'features':info.get('features'),'data_path':info.get('data_path'),'video_path':info.get('video_path'),
  'annotation_candidates':[r['path'] for r in files if any(x in r['path'].lower() for x in ['phase','annot','label','fail','event','session','subject'])],
  'metadata_receipts':receipts,'local_root':str(dest.relative_to(REPO)),'file_tree':receipt['path']}


def main():
 receipts=[]
 receipts.append(fetch('https://nanayawoa.github.io/REBOOT/',RUN/'evidence/official_project.html'))
 p=RUN/'evidence/official_dataset_collection.json';receipts.append(fetch('https://huggingface.co/api/datasets?author=REBOOT26&limit=100',p))
 items=json.loads(p.read_text());assert len(items)<100,'Dataset API pagination must be implemented'
 rows=[]
 with ThreadPoolExecutor(max_workers=4) as pool:
  for row in pool.map(dataset,items):
   rows.append(row);write(RUN/'manifests/source_audit_progress.json',rows)
   print('METADATA',row['repo_id'],row['total_episodes'],'annotation_candidates',row['annotation_candidates'],flush=True)
 write(ROOT/'00_dataset_overview/PINNED_DATASET_INVENTORY.json',rows)
 write(RUN/'manifests/initial_source_receipts.json',receipts)
 write(ROOT/'01_raw_dataset/METADATA_DOWNLOAD_MANIFEST.json',[r for row in rows for r in row['metadata_receipts']]+receipts)
 github='https://api.github.com/repos/anon-robo-account/REBOOT'
 p=RUN/'evidence/author_repository.json';receipts.append(fetch(github,p));branch=json.loads(p.read_text())['default_branch']
 p=RUN/'evidence/author_commit.json';receipts.append(fetch(github+'/commits/'+branch,p));commit=json.loads(p.read_text())['sha']
 p=RUN/'evidence/author_tree.json';receipts.append(fetch(github+'/git/trees/'+commit+'?recursive=1',p))
 tree=json.loads(p.read_text())['tree']
 names=['README.md','src/lerobot/datasets/lerobot_dataset.py','src/lerobot/robots/trossen_ai/configuration_trossen_ai.py',
  'src/lerobot/robots/trossen_ai/trossen_ai.py','src/lerobot/robots/bi_trossen_ai/bi_trossen_ai.py']
 for r in tree:
  name=r['path']
  if r['type']=='blob' and (name in names or name.startswith('dtset-trim/') or ('realsense' in name and name.endswith('.py'))):
   if r.get('size',0)<2*1024**2:
    receipts.append(fetch('https://raw.githubusercontent.com/anon-robo-account/REBOOT/'+commit+'/'+name,RUN/'evidence/author_code'/name))
 write(RUN/'manifests/author_code_receipts.json',{'repository':'https://github.com/anon-robo-account/REBOOT','revision':commit,'receipts':receipts})
 print('SOURCE_AUDIT_COMPLETE',len(rows),'repositories',flush=True)


if __name__=='__main__':main()
