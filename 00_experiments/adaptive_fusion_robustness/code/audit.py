"""Independent, read-only audit of native annotation and frozen branch evidence."""
import os
os.environ['OPENBLAS_NUM_THREADS']='2';os.environ['OMP_NUM_THREADS']='2'
if hasattr(os,'sched_getaffinity'):os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:2])
import collections, re
import h5py,numpy as np,pandas as pd,torch
from common import *
torch.set_num_threads(2)
KEYS=['recording_id','segment_id']
WARNINGS={
 '2025-01-10-15-28-50':'hand camera missing initially',
 '2025-01-10-16-17-40':'hand camera unavailable',
 '2025-01-10-17-10-38':'hand camera missing initially',
 '2025-01-11-14-45-48':'last action force/torque invalid',
 '2025-01-11-15-27-19':'last action force/torque invalid',
 '2025-01-11-15-35-08':'last action force/torque invalid',
 '2025-01-13-11-16-17':'gripper broke during last action',
 '2025-01-13-11-18-57':'pose unavailable for last action'}
def success_value(x):
 a=np.asarray(x)
 if a.shape!=():raise ValueError('success must be scalar')
 v=a.item()
 if a.dtype.kind=='b':return int(v)
 if a.dtype.kind in 'iu' and v in (0,1):return int(v)
 raise ValueError('unsupported success datatype/value')
def times(a):
 a=np.asarray(a,dtype=np.float64)
 if a.ndim==2:
  if not np.allclose(a,a[:,:1],atol=1e-9,rtol=0):raise ValueError('per-channel clock disagreement')
  a=a[:,0]
 if a.ndim!=1 or not np.isfinite(a).all() or np.any(np.diff(a)<=0):raise ValueError('invalid timestamps')
 return a
def action(text):
 m=re.match(r'^\s*(pick|insert|remove|place)\b',text.lower());return m.group(1) if m else 'other'
def native_audit():
 f=pd.DataFrame(read(ENC/'data/cohort_and_frames.json'));old=pd.read_parquet(REPO/'runs/reassemble/20260927T141645Z-inventory/tables_v2/cohort.parquet')
 old.segment_id=old.segment_id.astype(str);indexed={(str(x.recording_id),str(x.segment_id)):x for x in old.itertuples()}
 recordings=pd.read_parquet(REPO/'runs/reassemble/20260927T141645Z-inventory/recordings.parquet')
 actual={(x.recording_id,x.segment_id):x for x in f.itertuples()};records=[];issues=[];errors=[];dtype=collections.Counter();streams=read(REPO/'configs/reassemble/section1.json')['sensor']['channels']
 for number,record in enumerate(recordings.sort_values('recording_id').itertuples()):
  path=REPO/'../datasets/REASSEMBLE/raw/data'/record.filename;stat=path.stat()
  assert (stat.st_size,stat.st_mtime_ns)==(int(record.size_bytes),int(record.mtime_ns))
  with h5py.File(path,'r') as h:
   vt=times(h['timestamps/hand'][()]) if 'hand' in h['timestamps'] else np.array([])
   sensor_t={n:times(h['timestamps'][n][()]) for n in streams}
   annotations=[]
   for sid,g in h['segments_info'].items():
    text=g['text'][()];text=text.decode('utf-8') if isinstance(text,bytes) else str(text)
    success=success_value(g['success'][()]);dtype[str(g['success'].dtype)]+=1
    s,e=float(g['start'][()]),float(g['end'][()]);key=(record.recording_id,str(sid));a=action(text)
    assert key in indexed;previous=indexed[key]
    assert (success,1-success,s,e,a)==(int(previous.success),int(previous.failure),previous.start,previous.end,previous.action),('NATIVE_MISMATCH',key)
    row={'recording_id':record.recording_id,'segment_id':str(sid),'annotation_path':f'segments_info/{sid}','annotation_level':'high_level','success_dtype':str(g['success'].dtype),'success':success,'failure':1-success,'text':text,'action':a,'start':s,'end':e,'low_level_count':len(g.get('low_level',g.get('Low_level',{}))),'primary_task':bool(previous.primary_task),'visual_usable':bool(previous.visual_usable),'sensor_usable':bool(previous.sensor_usable),'included':key in actual}
    if key in actual:
     sample=actual[key];assert (sample.failure,sample.start,sample.end,sample.action)==(1-success,s,e,a)
     ii=np.flatnonzero((vt>=s)&(vt<=e));chosen=ii[np.linspace(0,len(ii)-1,16).round().astype(int)]
     assert len(ii)>=32 and chosen.tolist()==sample.frames16 and np.array_equal(vt[chosen],sample.timestamps16)
     assert len(set(sample.frames16))==16 and len(set(sample.frames32))==32
     assert all(s<=t<=e for t in sample.timestamps16)
     row['frame_index_uniform_rule_verified']=True;row['frame_dt_min']=float(np.diff(vt[chosen]).min());row['frame_dt_max']=float(np.diff(vt[chosen]).max())
    records.append(row);annotations.append(row)
   if record.recording_id in WARNINGS:
    active=sorted([x for x in annotations if x['action']!='other'],key=lambda x:x['end'])
    candidates=active[-3:] if 'last action' in WARNINGS[record.recording_id] else active
    for row in candidates:
     counts={n:int(((t>=row['start'])&(t<=row['end'])).sum()) for n,t in sensor_t.items()}
     coverage={n:float(max(0,min(row['end'],t[-1])-max(row['start'],t[0]))/(row['end']-row['start'])) for n,t in sensor_t.items()}
     issues.append({**row,'official_note':WARNINGS[record.recording_id],'last_nonidle_action':row['segment_id']==active[-1]['segment_id'],'native_sensor_counts':counts,'native_time_range_overlap':coverage,'physical_validity_from_finiteness':False})
  if number%25==0:guard();print('Native recordings audited',number+1,flush=True)
 expected=set(map(tuple,old.loc[old.primary_task & old.dual_complete,KEYS].astype(str).values))
 assert expected==set(actual),'UPSTREAM_ELIGIBILITY_MISMATCH'
 table=pd.DataFrame(records);table.to_csv(RUN/'checks/native_annotation_audit.csv',index=False,float_format='%.17g')
 pd.DataFrame(issues).to_json(RUN/'checks/known_issue_actions.json',orient='records',indent=2)
 counts={'all_annotations':len(table),'primary_actions':int(table.primary_task.sum()),'primary_failures':int(table.loc[table.primary_task,'failure'].sum()),'included_actions':len(f),'included_failures':int(f.failure.sum()),'recordings':f.recording_id.nunique(),'excluded_primary':int(table.primary_task.sum())-len(f),'success_datatypes':dict(dtype)}
 write(RUN/'checks/native_audit.json',{'passed':True,'counts':counts,'mapping':'failure = 1 - explicitly validated native success','annotation_level':'high_level segments_info direct children; not Low_level','eligibility':'exact prior primary_task AND dual_complete, followed by >=32-frame eligibility; no new exclusions','frame_rule':'16 rounded linearly spaced positions within in-interval native frame indices; not uniform elapsed time','label_semantics':'Source annotations verified by identity; no claim that machine checks prove semantic correctness.'})
 return f

def fits_audit(f):
 jobs=read(ENC/'data/fit_partitions.json');identity=read(ENC/'provenance/scientific_identity.json');initial=read(ENC/'provenance/input_identity.json')
 assert sha(ENC/'provenance/input_identity.json')==identity['inputs']
 for rel,h in identity['code'].items():assert sha(ENC.parent.parent/rel)==h,rel
 assert sha(ENC.parent.parent/'config.json')==identity['config']
 feature=read(ENC/'cache/features_complete.json')
 for rel,h in feature['hashes'].items():assert sha(ENC/rel)==h
 assert sha(ENC/'data/cohort_and_frames.json')==feature['identity']['cohort']
 verified=[];losses=[];folds=[];allE=[]
 class Head(torch.nn.Module):
  def __init__(self,w):
   super().__init__();self.projection=torch.nn.Sequential(torch.nn.Linear(w,128),torch.nn.ReLU(),torch.nn.Dropout(.1));self.classifier=torch.nn.Linear(128,1)
  def forward(self,x):return self.classifier(self.projection(x)).squeeze(-1)
 for fold in sorted({j['fold_name'] for j in jobs}):
  js=[j for j in jobs if j['fold_name']==fold];outer=next(j for j in js if j['role']=='outer_assessment');allE.extend(outer['predict']);seen=[]
  T=set(outer['T']);E=set(outer['predict']);assert not T&E and T|E==set(range(len(f)))
  for j in js:
   G,C,V=[set(j[k]) for k in ['G','C','predict']]
   gr,cr,vr=[set(f.iloc[list(x)].recording_id) for x in [G,C,V]]
   assert not gr&cr and not (gr|cr)&vr
   assert (G|C|V)==(set(range(len(f))) if j['role']=='outer_assessment' else T)
   if j['role']!='outer_assessment':seen.extend(j['predict']);assert not (G|C|V)&E
   for condition in ['cnn_only','cnn_plus_encoder','sensor_reference']:
    dpath=folder(condition,j);d=read(dpath/'complete.json');assert d['job']==j
    component='sensor' if condition=='sensor_reference' else condition
    assert d['fit_id']==signature({'inputs':identity,'job':j,'component':component})
    for rel,h in d['outputs'].items():assert sha(dpath/rel)==h
    preds=pd.read_csv(dpath/'identified_branch_predictions.csv',dtype={k:str for k in KEYS});expect=f.iloc[j['predict']]
    assert preds[KEYS].values.tolist()==expect[KEYS].values.tolist() and np.array_equal(preds.failure,expect.failure)
    verified.append({'condition':condition,'fold':fold,'role':j['role'],'fit_id':d['fit_id'],'path':str(dpath.relative_to(REPO)),'complete_sha256':sha(dpath/'complete.json'),'outputs':d['outputs']})
    if condition=='cnn_plus_encoder':
     x=np.load(ENC/'cache/cnn_plus_encoder.npy',mmap_mode='r')[j['G']];assert np.isfinite(x).all()
     state=torch.load(dpath/'model.pt',map_location='cpu',weights_only=True);mu=state['mean'].numpy();sd=state['std'].numpy();rawsd=x.std(0);expected=np.where(np.isfinite(rawsd)&(rawsd>1e-6),rawsd,1).astype('float32')
     np.testing.assert_allclose(mu,x.mean(0),atol=0,rtol=0);np.testing.assert_array_equal(sd,expected)
     z=(x-mu)/sd;model=Head(x.shape[1]);model.load_state_dict(state['head']);model.eval().requires_grad_(False);yy=torch.tensor(f.iloc[j['G']].failure.to_numpy(),dtype=torch.float32)
     with torch.inference_mode():
      logits=model(torch.from_numpy(z));loss=torch.nn.functional.binary_cross_entropy_with_logits(logits,yy,pos_weight=torch.tensor(float((yy==0).sum()/(yy==1).sum())))
     assert torch.isfinite(loss)
     losses.append({'fold':fold,'role':j['role'],'G_actions':len(x),'dimensions':x.shape[1],'finite':True,'near_constant_sd_le_1e6':int((rawsd<=1e-6).sum()),'normalizer_floor_dimensions':int((rawsd<=1e-6).sum()),'maximum_abs_standardized':float(abs(z).max()),'fraction_abs_standardized_gt_10':float((abs(z)>10).mean()),'eval_mode_final_checkpoint_weighted_BCE':float(loss),'labels_scope':'G only; final fixed checkpoint; no tuning'})
  assert len(seen)==len(set(seen)) and set(seen)==T
  bank=ENC/'cnn_only'/fold/'fusion_training/identified_oof_branch_probabilities.csv';stack=read(ENC/'cnn_only'/fold/'F2_stacker.json');assert sha(bank)==stack['oof_sha256'];assert stack['fit_id']==signature({'inputs':identity,'job':outer,'component':'cnn_only_F2'})
  oof=pd.read_csv(bank,dtype={k:str for k in KEYS});assert not oof.duplicated(KEYS).any();assert set(map(tuple,oof[KEYS].values))==set(map(tuple,f.iloc[outer['T']][KEYS].values))
  folds.append({'fold':fold,'T_actions':len(T),'E_actions':len(E),'inner_roles':4,'OOF_recording_exclusion_verified':True,'stacker_sha256':sha(ENC/'cnn_only'/fold/'F2_stacker.json'),'OOF_sha256':sha(bank)})
 assert len(allE)==len(set(allE))==len(f)
 write(RUN/'checks/fitted_component_audit.json',{'passed':True,'verified_fits':verified,'folds':folds,'scientific_identity':identity,'feature_identity':feature})
 pd.DataFrame(losses).to_csv(RUN/'checks/encoder_training_diagnostics.csv',index=False,float_format='%.17g')
 for n in ['cohort_and_frames.json','fit_partitions.json']:(RUN/'provenance'/n).write_bytes((ENC/'data'/n).read_bytes())
 print('Verified all branch components and training-only encoder diagnostics',flush=True)

def main():
 f=native_audit();fits_audit(f);state('NATIVE_AND_FIT_AUDIT_PASSED',new_training_started=False)
if __name__=='__main__':main()
