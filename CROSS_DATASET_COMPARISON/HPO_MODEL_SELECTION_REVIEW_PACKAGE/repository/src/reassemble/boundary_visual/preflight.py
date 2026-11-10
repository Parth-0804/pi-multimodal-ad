"""Read-only alignment and identity checks; never use human reviewed case lists."""
from pathlib import Path
import numpy as np,pandas as pd,h5py
from reassemble.section1_features import cohort
from reassemble.section1_models import verify_splits
from reassemble.alignment import timestamps_1d,interval_indices
from .common import read,write,sha,identity

def load(run,publish=False):
 c=read(run/'config.json');base=read(c['section1_config']);old=Path(base['run_dir']);cache=Path(c['sequence_cache'])
 assert base==read(old/'config.json')
 assert sha(base['splits'])==sha(old/'nested_splits.json')
 splits=read(base['splits']);frame=cohort(base);verify_splits(frame,splits)
 assert read(cache/'pretrained_model.json')==read(old/'pretrained_model.json'),'Model/preprocessing identity mismatch'
 model=read(old/'pretrained_model.json')
 for name,v in model['files'].items():assert sha(Path(base['data_root'])/'cache/section1_models'/model['revision']/name)==v['sha256']
 records=pd.read_parquet(Path(base['audit_run'])/'recordings.parquet').set_index('recording_id')
 n=len(frame);seq=np.empty((n,16,896),np.float32);mean=np.empty((n,896),np.float32);indices=np.empty((n,16),int);fold=np.full(n,-1);evidence=[];delta=0.
 assert len(list(cache.glob('*.npz')))==148
 for rid,rows in frame.groupby('recording_id',sort=True):
  p=cache/(rid+'.npz');historic=old/'features'/(rid+'.npz');meta=read(p.with_suffix('.json'));hm=read(historic.with_suffix('.json'));ix=rows.index.to_numpy()
  assert identity(p)==meta['output'] and identity(historic)==meta['input_features']
  assert sha(historic)==hm['feature_sha256']
  assert meta['source_sha256']==hm['source_sha256']==records.loc[rid,'sha256']
  assert identity(cache/'pretrained_model.json')==meta['model_identity']
  assert meta['mean_parity_max_abs']<=5e-5
  source=Path(base['data_root'])/'raw/data'/records.loc[rid,'filename'];st=source.stat()
  assert st.st_size==int(records.loc[rid,'size_bytes']) and st.st_mtime_ns==int(records.loc[rid,'mtime_ns'])
  with np.load(p) as z,np.load(historic) as h:
   assert np.array_equal(z['row_index'],ix) and np.array_equal(h['row_index'],ix)
   assert z['features'].shape==(len(ix),16,896) and z['features'].dtype==np.float32 and np.isfinite(z['features']).all()
   assert z['valid'].all() and np.array_equal(z['frame_indices'],h['frame_indices'])
   with h5py.File(source,'r') as raw:t=timestamps_1d(raw['timestamps/hand'][()])
   assert np.array_equal(z['timestamps'],t[z['frame_indices']])
   for j,row in enumerate(rows.itertuples()):
    available=interval_indices(t,row.start,row.end);expected=available[np.linspace(0,len(available)-1,16).round().astype(int)]
    assert np.array_equal(expected,z['frame_indices'][j]) and len(np.unique(expected))==16
   seq[ix]=z['features'];mean[ix]=h['visual'];indices[ix]=z['frame_indices']
   d=float(np.max(abs(z['features'].mean(1)-h['visual'])));assert d<=5e-5;delta=max(delta,d)
  evidence.append({'recording_id':rid,'sequence':identity(p),'historical':identity(historic),'audited_raw_sha256':meta['source_sha256'],'raw_bytes':st.st_size,'raw_mtime_ns':st.st_mtime_ns,'numpy_mean_max_abs':d})
 for outer in splits['folds']:fold[frame.recording_id.isin(outer['test_recordings'])]=outer['fold']
 with np.load(old/'predictions/rtdetr_perm00.npz') as z:
  assert np.array_equal(z['y'],frame.failure.to_numpy(int)) and np.array_equal(z['fold'],fold)
 result={'cohort_segments':n,'recordings':148,'failures':509,'frames':16,'dimension':896,'max_numpy_mean_difference':delta,'feature_tolerance':5e-5,'folds':identity(base['splits']),'cohort':identity(Path(base['audit_run'])/'tables_v2/cohort.parquet'),'model':identity(old/'pretrained_model.json'),'recordings_verified':evidence,'human_case_inputs':[],'raw_verification':'Audited SHA identity plus unchanged size/mtime and exact HDF5 frame timestamps; no full raw payload rehash.'}
 if publish:
  write(run/'cache_preflight.json',result)
  frame[['recording_id','segment_id','action','failure','start','end']].assign(outer_fold=fold).to_csv(run/'cohort_identity.csv',index=False)
 return c,base,frame,splits,seq,mean,fold,result
