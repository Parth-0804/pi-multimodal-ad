"""Study-specific OOF fitting and matched assessment, with no branch fitting."""
import csv,time,traceback
import numpy as np,pandas as pd
from common import *
from engine import Bank,Branch,linear
from quality_fusion import *
CLEAN={'family':'clean','level':'clean','severity':0.,'repeat':0,'seed':None}
MODELS=['historical_static','static_augmented','quality_additive','quality_interaction']

def schedule():
 jobs=[CLEAN.copy()]
 for family,levels in [('image_noise',[.02,.05,.1]),('sensor_noise',[.1,.5,1.]),('image_blur',[1.,2.,4.]),('sensor_time_loss',[.1,.3,.5])]:
  for level,severity in zip(['mild','medium','strong'],levels):
   for repeat,seed in ([(0,None)] if family=='image_blur' else enumerate(ASSESS_SEEDS,1)):
    jobs.append({'family':family,'level':level,'severity':severity,'repeat':repeat,'seed':seed})
 for absent in ['image_absent','sensor_absent','both_absent']:jobs.append({'family':'missing_modality','level':absent,'severity':1.,'repeat':0,'seed':None})
 assert len(jobs)==34;return jobs

def source_identity():return {str(p.relative_to(STUDY)):sha(p) for p in sorted(list((STUDY/'code').glob('*.py'))+[STUDY/'run_experiment.py'])}
def check_lock():
 lock=read(RUN/'config/protocol_lock.json');assert lock['config_sha256']==sha(RUN/'config/resolved_config.json');assert lock['sources']==source_identity();assert lock['protocol_sha256']==sha(RUN/'PROTOCOL.md');assert lock['quality_definitions_sha256']==sha(RUN/'config/quality_definitions.json');assert lock['clock_sha256']==sha(RUN/'config/clock.json');return lock

def predict_input(bank,branch,index,scales,scale_hash,job,base=None):
 sample=bank.cohort[index];family=job['family']
 if base is None:
  mean,qi=bank.image_features(index,CLEAN);x,qs=bank.sensor_features(index,CLEAN,scales,scale_hash);rv,pv=branch.visual(mean);rs,ps=branch.sensory(x);base={'p_visual':pv,'p_sensor':ps,'raw_visual_logit':rv,'raw_sensor_logit':rs,'q':np.r_[qi,qs]}
 output={k:(v.copy() if isinstance(v,np.ndarray) else v) for k,v in base.items()}
 if family in ['image_noise','image_blur','frame_loss']:
  x,q=bank.image_features(index,job);output['raw_visual_logit'],output['p_visual']=branch.visual(x);output['q'][:4]=q;assert output['p_sensor']==base['p_sensor']
 elif family in ['sensor_noise','sensor_channel_loss','sensor_time_loss']:
  x,q=bank.sensor_features(index,job,scales,scale_hash);output['raw_sensor_logit'],output['p_sensor']=branch.sensory(x);output['q'][4:]=q;assert output['p_visual']==base['p_visual']
 elif family not in ['clean','missing_modality']:raise ValueError(family)
 return output,base

def training(bank,fold,jobs):
 check_lock();out=RUN/'fusion_fits'/fold;done=out/'complete.json'
 if done.exists():
  d=read(done);assert d['lock_sha256']==sha(RUN/'config/protocol_lock.json')
  for rel,h in d['outputs'].items():assert sha(out/rel)==h
  return read(out/'components.json')
 records=[];lineage=[];start=time.perf_counter()
 for j in jobs:
  if j['role']=='outer_assessment':continue
  branch=Branch(j);scales,sh=bank.scales(j);lineage.append({'role':j['role'],'visual_fit_id':branch.visual_complete['fit_id'],'sensor_fit_id':branch.sensor_complete['fit_id'],'scales_sha256':sh})
  saved=pd.read_csv(folder('cnn_only',j)/'identified_branch_predictions.csv',dtype={'recording_id':str,'segment_id':str}).set_index(['recording_id','segment_id']);sensor_saved=pd.read_csv(folder('sensor_reference',j)/'identified_branch_predictions.csv',dtype={'recording_id':str,'segment_id':str}).set_index(['recording_id','segment_id'])
  for k,i in enumerate(j['predict']):
   if k%25==0:guard();check_lock()
   s=bank.cohort[i];key=(s['recording_id'],s['segment_id']);base=None
   variants=[('clean',.5,CLEAN),('image',.25,training_variant(s['sample_id'],'image')),('sensor',.25,training_variant(s['sample_id'],'sensor'))]
   for modality,weight,job in variants:
    value,base=predict_input(bank,branch,i,scales,sh,job,base)
    if modality=='clean':
     assert abs(value['p_visual']-saved.loc[key,'p_visual'])<=config()['probability_replay_tolerance'];assert abs(value['p_sensor']-sensor_saved.loc[key,'p_sensor'])<=config()['probability_replay_tolerance']
    record={n:s[n] for n in ['sample_id','recording_id','segment_id','failure','start','end','action']};record.update(fold=fold,role=j['role'],variant=modality,sample_weight=weight,visual_fit_id=branch.visual_complete['fit_id'],sensor_fit_id=branch.sensor_complete['fit_id'],scale_sha256=sh,family=job['family'],severity=job['severity'],seed=job.get('seed'),p_visual=value['p_visual'],p_sensor=value['p_sensor'],raw_visual_logit=value['raw_visual_logit'],raw_sensor_logit=value['raw_sensor_logit']);record.update(dict(zip(NAMES,value['q'])));records.append(record)
   if k%100==0:state('GENERATING_OOF_AUGMENTATIONS',fold=fold,role=j['role'],completed_in_role=k+1,role_actions=len(j['predict']))
  bank.verify_frozen()
 table=pd.DataFrame(records);outer=next(j for j in jobs if j['role']=='outer_assessment');expected={bank.cohort[i]['sample_id'] for i in outer['T']};assert set(table.sample_id)==expected and len(table)==3*len(expected);assert set(table.recording_id).isdisjoint(outer['outer_E_recordings'])
 out.mkdir(parents=True,exist_ok=True);table.to_csv(out/'identified_OOF_training_inputs.csv',index=False,float_format='%.17g')
 components=fit_all(table[['p_visual','p_sensor']].to_numpy(),table[NAMES].to_numpy(),table.failure.to_numpy(),table.sample_weight.to_numpy(),table.sample_id.to_numpy())
 write(out/'components.json',components);write(out/'complete.json',{'lock_sha256':sha(RUN/'config/protocol_lock.json'),'outputs':{n:sha(out/n) for n in ['identified_OOF_training_inputs.csv','components.json']},'OOF_parent_actions':len(expected),'rows':len(table),'lineage':lineage,'seconds':time.perf_counter()-start,'E_labels_used':False,'augmentation_weights':[.5,.25,.25],'new_fusion_models':3});state('FUSION_MODELS_FITTED',fold=fold,new_training_started=True)
 return components

def assessment(bank,fold,jobs,components):
 check_lock();assert read(RUN/'config/fitted_components_lock.json')['components'][fold]==sha(RUN/'fusion_fits'/fold/'components.json');j=next(j for j in jobs if j['role']=='outer_assessment');out=RUN/'predictions'/fold;done=out/'complete.json'
 if done.exists():
  d=read(done);assert d['model_lock_sha256']==sha(RUN/'config/fitted_components_lock.json')
  for p,h in d['outputs'].items():assert sha(out/p)==h
  return
 branch=Branch(j);scales,sh=bank.scales(j);historical=read(ENC/'cnn_only'/fold/'F2_stacker.json');jobs_noise=schedule();writers={};streams={};paths={};out.mkdir(parents=True,exist_ok=True);start=time.perf_counter()
 saved=pd.read_csv(ENC/'cnn_only'/fold/'assessment_predictions.csv',dtype={'recording_id':str,'segment_id':str}).set_index(['recording_id','segment_id'])
 try:
  for number,i in enumerate(j['predict']):
   guard();s=bank.cohort[i];base=None
   for job in jobs_noise:
    value,base=predict_input(bank,branch,i,scales,sh,job,base);pv,ps=value['p_visual'],value['p_sensor'];q=value['q'];va=sa=True
    p=np.array([[pv,ps]]);scores={'historical_static':float(expit(linear(p,historical['model']))[0])};scores.update({name:float(predict(p,q[None,:],component)[0]) for name,component in components.items()})
    status='OK';policy='fusion'
    if job['family']=='clean':
     key=(s['recording_id'],s['segment_id'])
     assert max(abs(pv-saved.loc[key,'p_visual']),abs(ps-saved.loc[key,'p_sensor']),abs(scores['historical_static']-saved.loc[key,'p_fused']))<=config()['probability_replay_tolerance']
    if job['family']=='missing_modality':
     va=job['level']=='sensor_absent';sa=job['level']=='image_absent';status='UNAVAILABLE' if not (va or sa) else 'OK'
     for name in scores:scores[name],policy=route(pv,ps,va,sa,scores[name])
     if not va:pv=np.nan;value['raw_visual_logit']=np.nan;q[:4]=0
     if not sa:ps=np.nan;value['raw_sensor_logit']=np.nan;q[4:]=0
    record={n:s[n] for n in ['sample_id','recording_id','segment_id','failure','start','end','action']};record.update(fold=fold,**job,status=status,visual_available=va,sensor_available=sa,fallback_policy=policy,visual_fit_id=branch.visual_complete['fit_id'],sensor_fit_id=branch.sensor_complete['fit_id'],historical_stacker_fit_id=historical['fit_id'],new_components_sha256=sha(RUN/'fusion_fits'/fold/'components.json'),raw_scale_sha256=sh,p_visual=pv,p_sensor=ps,raw_visual_logit=value['raw_visual_logit'],raw_sensor_logit=value['raw_sensor_logit'],threshold=.5)
    record.update(dict(zip(NAMES,q)));record.update({'p_'+name:score for name,score in scores.items()});record.update({'decision_'+name:int(score>=.5) if score is not None else None for name,score in scores.items()})
    key=(job['family'],job['level'],job['repeat'])
    if key not in writers:
     path=out/job['family']/job['level']/f"repeat_{job['repeat']:02d}"/'predictions.csv';path.parent.mkdir(parents=True,exist_ok=True);paths[key]=path;stream=path.with_suffix('.writing.csv').open('w',newline='');streams[key]=stream;writers[key]=csv.DictWriter(stream,fieldnames=list(record));writers[key].writeheader()
    writers[key].writerow(record)
   if number%25==0:
    for stream in streams.values():stream.flush()
    state('ASSESSING_FIXED_MODELS',fold=fold,completed_parent_actions=number+1,total_parent_actions=len(j['predict']),realizations_per_parent=34)
  for stream in streams.values():stream.close()
  for path in paths.values():os.replace(path.with_suffix('.writing.csv'),path)
  bank.verify_frozen();write(done,{'model_lock_sha256':sha(RUN/'config/fitted_components_lock.json'),'outputs':{str(p.relative_to(out)):sha(p) for p in paths.values()},'parent_actions':len(j['predict']),'realizations':34,'failed_cases':0,'both_absent_unavailable_rows':len(j['predict']),'seconds':time.perf_counter()-start});state('ASSESSMENT_FOLD_COMPLETE',fold=fold)
 except BaseException as exc:
  for stream in streams.values():stream.close()
  write(out/'failure.json',{'recording_id':s['recording_id'],'segment_id':s['segment_id'],'job':job,'exception':repr(exc),'completed_parent_actions':number,'expected_parent_actions':len(j['predict']),'policy':'Stage stopped; incomplete .writing tables retained, no dropped-case AP reported.'});raise

def run():
 lock=check_lock();folds=config()['locked_folds'];assert folds;alljobs=read(ENC/'data/fit_partitions.json');bank=Bank()
 try:
  for fold in folds:training(bank,fold,[j for j in alljobs if j['fold_name']==fold])
  components_lock={'protocol_lock_sha256':sha(RUN/'config/protocol_lock.json'),'components':{fold:sha(RUN/'fusion_fits'/fold/'components.json') for fold in folds},'created_before_assessment':True}
  path=RUN/'config/fitted_components_lock.json'
  if path.exists():assert read(path)==components_lock
  else:
   assert not list((RUN/'predictions').glob('**/predictions.csv'));write(path,components_lock)
  for fold in folds:assessment(bank,fold,[j for j in alljobs if j['fold_name']==fold],read(RUN/'fusion_fits'/fold/'components.json'))
  state('INFERENCE_COMPLETE',completed_folds=folds)
 finally:bank.close()
