"""Audit-only file helpers, explicit identity joins and bounded provenance checks."""
import hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import pandas as pd

def read(path):return json.loads(Path(path).read_text())
def digest(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def jsonable(obj):
 if isinstance(obj,dict):return {str(k):jsonable(v) for k,v in obj.items()}
 if isinstance(obj,(list,tuple)):return [jsonable(v) for v in obj]
 if isinstance(obj,np.ndarray):return jsonable(obj.tolist())
 if isinstance(obj,(np.integer,np.bool_)):return obj.item()
 if isinstance(obj,(float,np.floating)):return float(obj) if np.isfinite(obj) else None
 if isinstance(obj,Path):return str(obj)
 return obj

def write(path,obj):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('x') as f:json.dump(jsonable(obj),f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
def textfile(path,text):
 with Path(path).open('x') as f:f.write(text.rstrip()+'\n')
def csvfile(path,rows):pd.DataFrame(rows).to_csv(path,index=False)
def table(frame):
 if not isinstance(frame,pd.DataFrame):frame=pd.DataFrame(frame)
 clean=lambda x:str(x).replace('|','\\|').replace('\n',' ')
 return '| '+' | '.join(frame.columns)+' |\n| '+' | '.join(['---']*len(frame.columns))+' |\n'+''.join('| '+' | '.join(clean(x) for x in row)+' |\n' for row in frame.itertuples(index=False,name=None))
def now():return datetime.now(timezone.utc).isoformat()
def fingerprint(paths):return [{'path':str(p),'bytes':Path(p).stat().st_size,'sha256':digest(p)} for p in sorted(set(map(str,paths)))]
def check_fingerprints(entries):
 for entry in entries:
  p=Path(entry['path'])
  if not p.is_file() or p.stat().st_size!=entry['bytes'] or digest(p)!=entry['sha256']:raise ValueError('Changed protected source: '+str(p))
 return len(entries)
def join_predictions(cohort,pred):
 keys=['recording_id','segment_id']
 a=cohort.copy();b=pred.copy()
 for x in [a,b]:
  for key in keys:x[key]=x[key].astype(str)
  if x.duplicated(keys).any():raise ValueError('duplicate identity')
 if set(map(tuple,a[keys].to_numpy()))!=set(map(tuple,b[keys].to_numpy())):raise ValueError('missing/extra identity')
 merged=a.merge(b,on=keys,how='left',validate='one_to_one',sort=False,suffixes=('','_prediction'))
 for key in ['failure','fold']:
  if key in a and key in b and not np.array_equal(merged[key],merged[key+'_prediction']):raise ValueError('identity label/fold mismatch: '+key)
 return merged

def config_for(run):return read(Path(run)/'00_protocol/audit_config.json')
def freeze_revision(run,stage):
 directory=Path(run)/'00_protocol/script_revisions';directory.mkdir(exist_ok=True)
 paths=list(Path('scripts/thesis/final_validity_audit').glob('*.py'))+list(Path('tests/thesis/final_validity_audit').glob('*.py'))
 write(directory/(stage+'.json'),{'timestamp_UTC':now(),'git_HEAD':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'files':fingerprint(paths)})
