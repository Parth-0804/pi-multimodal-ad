"""Post-execution provenance, membership, numerical replay and preservation checks."""
from pathlib import Path
import json,hashlib,os,datetime
for name in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[name]='2'
if hasattr(os,'sched_getaffinity'):os.sched_setaffinity(0,[12,13])
import numpy as np,pandas as pd
from scipy.special import expit
RUN=Path(__file__).resolve().parent.parent;STUDY=RUN.parents[1];REPO=STUDY.parents[1]
Q=['image_gradient','image_clipping','image_contrast','unique_frame_fraction','sensor_finite_fraction','available_channel_fraction','sensor_max_gap_fraction','sensor_relative_variation']
def read(p):return json.loads(p.read_text())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024**2),b''):h.update(b)
 return h.hexdigest()
def main():
 cfg=read(RUN/'config/resolved_config.json');lock=read(RUN/'config/protocol_lock.json');assert sha(RUN/'config/resolved_config.json')==lock['config_sha256'];assert sha(RUN/'config/clock.json')==lock['clock_sha256'];assert sha(RUN/'PROTOCOL.md')==lock['protocol_sha256']
 for name,h in lock['sources'].items():assert sha(STUDY/name)==h,name
 assert read(RUN/'checks/tests.json')['passed'];cohort=read(RUN/'provenance/cohort_and_frames.json');partitions=read(RUN/'provenance/fit_partitions.json');model_lock=read(RUN/'config/fitted_components_lock.json');assert model_lock['protocol_lock_sha256']==sha(RUN/'config/protocol_lock.json');replayed=0;files=0
 for fold in cfg['locked_folds']:
  job=next(j for j in partitions if j['fold_name']==fold and j['role']=='outer_assessment');training=pd.read_csv(RUN/'fusion_fits'/fold/'identified_OOF_training_inputs.csv',dtype={'recording_id':str,'segment_id':str,'sample_id':str});assert set(training.sample_id)=={cohort[i]['sample_id'] for i in job['T']};assert set(training.recording_id).isdisjoint(job['outer_E_recordings']);assert (training.groupby('sample_id').size()==3).all();assert (training.groupby('sample_id').sample_weight.sum()==1).all()
  models=read(RUN/'fusion_fits'/fold/'components.json');assert sha(RUN/'fusion_fits'/fold/'components.json')==model_lock['components'][fold];q=training[Q].to_numpy();w=training.sample_weight.to_numpy();mean=np.average(q,axis=0,weights=w);std=np.sqrt(np.average((q-mean)**2,axis=0,weights=w));std=np.where(std>1e-6,std,1)
  for model in models.values():np.testing.assert_allclose(mean,model['normalizer']['mean'],atol=1e-12,rtol=1e-12);np.testing.assert_allclose(std,model['normalizer']['std'],atol=1e-12,rtol=1e-12)
  done=read(RUN/'predictions'/fold/'complete.json');assert len(done['outputs'])==34;clean=pd.read_csv(RUN/'predictions'/fold/'clean/clean/repeat_00/predictions.csv',dtype={'recording_id':str,'segment_id':str}).sort_values(['recording_id','segment_id']).reset_index(drop=True)
  for name,h in done['outputs'].items():
   path=RUN/'predictions'/fold/name;assert sha(path)==h;t=pd.read_csv(path,dtype={'recording_id':str,'segment_id':str}).sort_values(['recording_id','segment_id']).reset_index(drop=True);assert t[['recording_id','segment_id']].equals(clean[['recording_id','segment_id']]);assert np.array_equal(t.failure,clean.failure);files+=1
   if t.family.iloc[0]=='missing_modality':
    level=t.level.iloc[0]
    for name in ['historical_static']+list(models):
     if level=='both_absent':assert t['p_'+name].isna().all() and t.status.eq('UNAVAILABLE').all()
     else:np.testing.assert_array_equal(t['p_'+name],t['p_sensor' if level=='image_absent' else 'p_visual'])
    continue
   assert t.status.eq('OK').all()
   if t.family.iloc[0].startswith('image_'):np.testing.assert_array_equal(t[Q[4:]],clean[Q[4:]])
   if t.family.iloc[0].startswith('sensor_'):np.testing.assert_array_equal(t[Q[:4]],clean[Q[:4]])
   p=t[['p_visual','p_sensor']].to_numpy();rawq=t[Q].to_numpy()
   for name,model in models.items():
    z=np.clip((rawq-np.asarray(model['normalizer']['mean']))/np.asarray(model['normalizer']['std']),-10,10)
    x=p if name=='static_augmented' else (np.c_[p,z] if name=='quality_additive' else np.c_[p,z,p[:,0,None]*z,p[:,1,None]*z]);pred=expit(x@np.asarray(model['coefficient'])+model['intercept']);np.testing.assert_allclose(pred,t['p_'+name],atol=1e-12,rtol=0);replayed+=len(t)
 protected=read(RUN/'provenance/protected_prior_artifacts.json')
 for name,h in protected['hashes'].items():assert sha(REPO/name)==h,name
 raw={}
 for s in cohort:
  for kind in ['source','video']:raw[s[kind+'_path']]=(s[kind+'_bytes'],s[kind+'_mtime_ns'])
 for path,expected in raw.items():
  stat=(REPO/path).stat();assert (stat.st_size,stat.st_mtime_ns)==tuple(expected),path
 result={'passed':True,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'prediction_files':files,'new_fusion_predictions_replayed':replayed,'raw_paths_size_mtime_verified':len(raw),'source_config_clock_and_fit_locks_unchanged':True,'training_membership_weights_and_quality_normalization_verified':True,'prior_artifact_hashes_unchanged':True,'scope':'Independent saved-table arithmetic and metadata checks; not independent human label adjudication.'};(RUN/'checks/completion_integrity.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
