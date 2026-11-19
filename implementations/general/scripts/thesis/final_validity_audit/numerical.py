"""Independent retained-result, identity, cluster-bootstrap and sensitivity checks."""
import argparse,sys,json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn import metrics as sk
from .common import read,write,textfile,csvfile,table,fingerprint,check_fingerprints,join_predictions,config_for,freeze_revision,digest,now
from .metrics import metrics,paired_bootstrap,cluster_draws,interval


def load_cohort(c):
 s=c['sources'];a=pd.read_parquet(Path(s['inventory'])/'tables_v2/cohort.parquet')
 a=a[a.primary_task & a.dual_complete].reset_index(drop=True)
 core=pd.read_parquet(Path(s['S1'])/'cohort.parquet')
 keys=['recording_id','segment_id']
 for f in [a,core]:
  for k in keys:f[k]=f[k].astype(str)
  assert not f.duplicated(keys).any()
 # Provenance chain checks the ordered saved cohort against independently keyed inventory.
 joined=core.merge(a[keys+['failure','action','start','end']],on=keys,validate='one_to_one',suffixes=('','_audit'))
 for k in ['failure','action','start','end']:assert np.array_equal(joined[k],joined[k+'_audit'])
 assert set(map(tuple,core[keys].values))==set(map(tuple,a[keys].values))
 assert np.array_equal(core[keys].values,a[keys].values),'saved row-index cohort order disagrees with generator inventory'
 splits=read(Path(s['S1'])/'nested_splits.json');core['fold']=-1;allgroups=set(core.recording_id);seen=set()
 for outer in splits['folds']:
  tr,te=set(outer['train_recordings']),set(outer['test_recordings'])
  assert not tr&te and tr|te==allgroups and not seen&te;seen|=te
  core.loc[core.recording_id.isin(te),'fold']=outer['fold'];innerseen=set()
  for inner in outer['inner']:
   it,iv=set(inner['train_recordings']),set(inner['validation_recordings'])
   assert not it&iv and it|iv==tr and not innerseen&iv;innerseen|=iv
  assert innerseen==tr
 assert seen==allgroups and (len(core),int(core.failure.sum()),len(allgroups))==(4530,509,148)
 # Verify label semantics and keyed quality metadata independently of prediction y arrays.
 for rid,rows in core.groupby('recording_id',sort=True):
  record=read(Path(s['inventory'])/'records'/f'{rid}.json');ann={str(x['segment_id']):x for x in record['segments']}
  with np.load(Path(s['S1'])/'features'/f'{rid}.npz',allow_pickle=False) as z:
   ix=z['row_index'];assert np.array_equal(ix,rows.index.to_numpy())
  for r in rows.itertuples():
   x=ann[r.segment_id];assert int(not x['success'])==r.failure==x['failure']
   assert x['action']==r.action and x['start']==r.start and x['end']==r.end
 return core,splits


def source_preflight(c):
 r=Path(c['run']);s=c['sources'];proof=[];entries={};manifestpaths=[]
 for key in ['S1','S1B','S2','S3','DROP','FINAL']:
  p=Path(s[key])/('final_output_manifest.json' if key=='S1' else 'output_manifest.json')
  j=read(p);items=j['files'];manifestpaths.append(p)
  for e in items:
   pp=Path(e['path']);assert pp.is_file() and pp.stat().st_size==e['bytes'] and digest(pp)==e['sha256'],str(pp)
   entries[str(pp)]={'path':str(pp),'bytes':e['bytes'],'sha256':e['sha256']}
  proof.append({'run':key,'manifest':str(p),'entries_verified':len(items)})
 seal=read(Path(s['FINAL'])/'seal.json');assert seal['status']=='complete'
 assert read(Path(s['S1'])/'finalization/validation.json')['all_prediction_labels_and_folds_verified']
 assert read(Path(s['S1B'])/'validation.json')['outer_predictions']
 assert read(Path(s['S2'])/'validation.json')['exact_U1_U2_F2_reuse']
 extra=manifestpaths+list(Path('src/reassemble').glob('*.py'))+list(Path('docs/thesis').glob('*.md'))+list(Path('artifacts/thesis').glob('*'))
 extra=[p for p in extra if p.is_file()]
 extra+=list(Path('configs/reassemble').glob('*.json'))
 extra+=[Path(s['inventory'])/'tables_v2/cohort.parquet',Path(s['inventory'])/'recordings.parquet']
 extra+=list((Path(s['inventory'])/'records').glob('*.json'))
 extra+=list((Path(s['PHM'])/'tables').glob('*'))+[Path(s['PHM'])/'reports/loeo_summary.json',Path(s['PHM'])/'config/resolved_config.yaml',Path(s['PHM'])/'provenance.json']
 for e in fingerprint(extra):entries[e['path']]=e
 write(r/'00_protocol/source_manifest.json',list(entries.values()))
 write(r/'00_protocol/sealed_source_validation.json',{'timestamp_UTC':now(),'verified_manifests':proof,'final_seal_status':seal['status'],'additional_improvements_predictions_used':False,'no_active_queue_control_actions':True})
 return proof


def load_predictions(c,cohort,splits):
 s=c['sources'];keys=['recording_id','segment_id','failure','fold'];identity=[];models={}
 def keyed_piece(rows,values):
  q=cohort.iloc[np.asarray(rows)].loc[:,keys].copy();q['p']=values['p'];q['hard']=values['hard'];return q
 def validate(q,label):
  result=join_predictions(cohort,q)
  assert np.isfinite(result.p).all() and result.p.between(0,1).all() and result.hard.isin([0,1]).all()
  identity.append({'prediction':label,'unique_keys':len(q),'join':'composite recording_id + segment_id','labels_and_folds_verified':True,'finite_probability_range_verified':True,'identity_binding':'sealed inventory->cohort->feature row_index; keyed outer fold pieces and source provenance, not vector length'})
  return result
 for name,kind in [('U1','sensor_statistics'),('U2','rtdetr'),('ACTION_HIST','action_only')]:
  pieces=[]
  for outer in splits['folds']:
   ix=np.flatnonzero(cohort.recording_id.isin(outer['test_recordings']))
   with np.load(Path(s['S1'])/'predictions'/f"{kind}_perm00_fold{outer['fold']}.npz",allow_pickle=False) as z:pieces.append(keyed_piece(ix,z))
  q=validate(pd.concat(pieces),name)
  with np.load(Path(s['S1'])/'predictions'/f'{kind}_perm00.npz',allow_pickle=False) as z:
   assert np.array_equal(q.p,z['p']) and np.array_equal(q.hard,z['hard']) and np.array_equal(q.fold,z['fold']) and np.array_equal(q.failure,z['y'])
  models[name]=q
 pieces=[]
 for outer in splits['folds']:
  with np.load(Path(s['S1B'])/'stacking'/f"outer{outer['fold']}.npz",allow_pickle=False) as z:
   expected=np.flatnonzero(cohort.recording_id.isin(outer['test_recordings']));assert np.array_equal(z['test_rows'],expected)
   assert np.array_equal(z['train_rows'],np.flatnonzero(cohort.recording_id.isin(outer['train_recordings'])))
   pieces.append(keyed_piece(z['test_rows'],z))
 q=validate(pd.concat(pieces),'F2')
 with np.load(Path(s['S1B'])/'stacking/oof.npz',allow_pickle=False) as z:
  assert np.array_equal(q.p,z['p']) and np.array_equal(q.hard,z['hard'])
 models['F2']=q
 for name in ['F5','F6']:
  pieces=[]
  for outer in splits['folds']:
   with np.load(Path(s['S2'])/'predictions'/f"outer{outer['fold']}.npz",allow_pickle=False) as z:
    assert np.array_equal(z['test_rows'],np.flatnonzero(cohort.fold==outer['fold']))
    pieces.append(keyed_piece(z['test_rows'],{'p':z[name+'_p'],'hard':z[name+'_hard']}))
  models[name]=validate(pd.concat(pieces),name)
 with np.load(Path(s['S2'])/'predictions/oof.npz',allow_pickle=False) as z:
  for name in ['U1','U2','F2','F5','F6']:
   assert np.array_equal(models[name].p,z[name+'_p']) and np.array_equal(models[name].hard,z[name+'_hard'])
 # These sealed condition files inherit the validated source cohort/clean indices.
 for condition in ['clean','V1_0.1','V4','S5']:
  p=Path(s['S3'])/'predictions'/f'{condition}.npz';meta=read(p.with_suffix('.json'));assert meta['sha256']==digest(p)
  with np.load(p,allow_pickle=False) as z:
   assert np.array_equal(z['fold'],cohort.fold) and np.array_equal(z['y'],cohort.failure)
   for name in ['U1','U2','F2','F5','F6']:
    if not np.isfinite(z[name+'_p']).all():
     assert (condition,name) in [('V4','U2'),('S5','U1')];continue
    q=keyed_piece(np.arange(len(cohort)),{'p':z[name+'_p'],'hard':z[name+'_hard']})
    models[condition+':'+name]=validate(q,str(p)+':'+name)
   if condition in ['V4','S5']:
    col=0 if condition=='V4' else 1
    assert np.all(z['availability'][:,col]==0) and np.all(z['availability'][:,1-col]==1)
    for name in ['F5','F6']:
     assert np.all(z[name+'_weights'][:,col]==0) and np.all(z[name+'_weights'][:,1-col]==1)
 for condition in ['clean','V4','S5']:
  p=Path(s['DROP'])/'predictions'/f'{condition}.npz'
  with np.load(p,allow_pickle=False) as z:
   assert np.array_equal(z['fold'],cohort.fold) and np.array_equal(z['y'],cohort.failure)
   models[condition+':DROP']=validate(keyed_piece(np.arange(len(cohort)),z),str(p))
 return models,identity


def audit(c):
 r=Path(c['run']);out=r/'01_independent_result_check';s=c['sources'];freeze_revision(r,'numerical_before_results')
 source_preflight(c);frame,splits=load_cohort(c);models,identity=load_predictions(c,frame,splits)
 csvfile(out/'cohort_identity.csv',frame.to_dict('records'))
 write(out/'identity_checks.json',{'status':'VERIFIED_NUMERICALLY','entries':identity,'limitation':'Legacy NPZ files do not carry composite IDs internally. Binding is provenance-based using sealed inventory/cohort, per-recording feature row indices, per-fold pieces and generation source; this does not create independent execution-time identity logs.'})
 records=[];discrepancies=[];points={};tol=c['metric_tolerance']
 s1=read(Path(s['S1'])/'assessment/results.json');s2=read(Path(s['S2'])/'assessment/results.json');s3=read(Path(s['S3'])/'results.json');drop=read(Path(s['DROP'])/'results.json')
 for name,q in models.items():
  point=metrics(q.failure,q.p,q.hard);points[name]=point
  if name=='ACTION_HIST':historical=s1['metrics']['action_only']
  elif ':' not in name:historical=s2['metrics'][name]
  else:
   condition,model=name.split(':');historical=drop['conditions'][condition]['metrics'] if model=='DROP' else s3['conditions'][condition]['metrics'][model]
  lib={'AUPRC':sk.average_precision_score(q.failure,q.p),'AUROC':sk.roc_auc_score(q.failure,q.p),'Brier':sk.brier_score_loss(q.failure,q.p),'macro_F1':sk.f1_score(q.failure,q.hard,average='macro',zero_division=0),'balanced_accuracy':sk.balanced_accuracy_score(q.failure,q.hard),'failure_precision':sk.precision_score(q.failure,q.hard,zero_division=0),'failure_recall':sk.recall_score(q.failure,q.hard)}
  for metric,expected in historical.items():
   delta=point[metric]-expected['estimate'];ok=abs(delta)<=tol;libdiff=None if metric not in lib else point[metric]-lib[metric]
   if libdiff is not None:assert abs(libdiff)<=tol,(name,metric,'library',libdiff)
   rec={'model_condition':name,'metric':metric,'independent':point[metric],'historical':expected['estimate'],'difference':delta,'library_difference':libdiff,'status':'VERIFIED_NUMERICALLY' if ok else 'NUMERICAL_DISCREPANCY'};records.append(rec)
   if not ok:discrepancies.append(rec)
  q[['recording_id','segment_id','failure','fold','p','hard']].to_csv(out/(name.replace(':','_')+'_identified.csv'),index=False)
 # Check exact complete-loss branch, decisions and per-fold thresholds, without loading a model.
 fallback=[]
 for condition,remaining,kind in [('V4','U1','sensor_statistics'),('S5','U2','rtdetr')]:
  for model in ['F2','F5','F6','DROP']:
   q=models[condition+':'+model];ref=models[remaining];diff=float(np.max(abs(q.p-ref.p)));hard=bool(np.array_equal(q.hard,ref.hard));thresholdok=True
   for k in range(5):
    t=read(Path(s['S1'])/'predictions'/f'{kind}_perm00_fold{k}.json')['calibration']['threshold'];m=q.fold==k
    thresholdok&=np.array_equal(q.loc[m,'hard'],(q.loc[m,'p']>=t).astype(int))
   rec={'condition':condition,'model':model,'surviving':remaining,'max_probability_difference':diff,'hard_equal':hard,'fallback_threshold_verified':bool(thresholdok),'status':'VERIFIED_NUMERICALLY' if diff<=tol and hard and thresholdok else 'NUMERICAL_DISCREPANCY'};fallback.append(rec)
   if rec['status']=='NUMERICAL_DISCREPANCY':discrepancies.append(rec)
 csvfile(out/'metric_recomputation.csv',records);write(out/'complete_loss_invariants.json',fallback)
 # PHM groups/targets/errors, not the historical bootstrap-mean delta estimator.
 phm=pd.read_parquet(Path(s['PHM'])/'tables/loeo_predictions.parquet');report=read(Path(s['PHM'])/'reports/loeo_summary.json');phmrows=[]
 targetroot=Path('runs/phm2026_image_target/20260912T052857044116Z-c936a4e3');target=pd.read_parquet(targetroot/'tables/run_damage_targets.parquet')
 for row in report['summary']:
  a=phm[phm.model==row['model']];assert not a.duplicated(['experiment','run']).any()
  joined=a.merge(target[['experiment','run','raw_top3_mean_pct']],on=['experiment','run'],validate='many_to_one');assert np.allclose(joined.y_true,joined.raw_top3_mean_pct,rtol=0,atol=tol)
  values={'mae':float(np.mean(abs(a.y_true-a.y_pred))),'rmse':float(np.sqrt(np.mean((a.y_true-a.y_pred)**2)))}
  for m,v in values.items():
   ok=abs(v-row[m])<=tol;rec={'model':row['model'],'metric':m,'independent':v,'historical':row[m],'status':'VERIFIED_NUMERICALLY' if ok else 'NUMERICAL_DISCREPANCY'};phmrows.append(rec)
   if not ok:discrepancies.append(rec)
 csvfile(out/'phm_metric_recomputation.csv',phmrows)
 if discrepancies:
  write(out/'discrepancies.json',{'material':True,'findings':discrepancies,'dependent_interpretation_stopped':True});raise RuntimeError('Material numerical discrepancy; stop dependent interpretation')
 # Historical RNG/rule reproduced independently; no silent invalid-replicate redraw.
 draws=cluster_draws(frame.recording_id,c['bootstrap_replicates'],c['bootstrap_seed']);bmodels={name:q.p.to_numpy() for name,q in models.items() if name in ['U1','U2','F2','F6','V1_0.1:F2','V1_0.1:F5','V1_0.1:F6','V4:F5','V4:F6','V4:DROP','S5:F5','S5:F6','S5:DROP']}
 boot=paired_bootstrap(frame.failure.to_numpy(),bmodels,frame.recording_id,draws=draws)
 paired=[];s1b=read(Path(s['S1B'])/'assessment/results.json')
 contrasts=[('F2','U1',s1b['fusion_minus_sensor']),('F6','F2',s2['paired']['F6-F2']),('V1_0.1:F5','V1_0.1:F2',s3['conditions']['V1_0.1']['paired']['F5-F2']),('V1_0.1:F6','V1_0.1:F2',s3['conditions']['V1_0.1']['paired']['F6-F2'])]
 contrasts += [(cond+':'+model,ref,None) for cond,ref in [('V4','U1'),('S5','U2')] for model in ['F5','F6','DROP']]
 for a,b,hist in contrasts:
  for j,m in enumerate(['AUPRC','AUROC','Brier']):
   ci=interval(boot[a][:,j]-boot[b][:,j]);point=points[a][m]-points[b][m]
   expected=None if hist is None else hist[m];ok=expected is None or max(abs(point-expected['estimate']),abs(ci['lower_95']-expected['lower_95']),abs(ci['upper_95']-expected['upper_95']))<=tol
   enough=ci['valid_replicates']>=c['minimum_valid_bootstrap_fraction']*c['bootstrap_replicates']
   rec={'contrast':a+' minus '+b,'metric':m,'estimate':point,**ci,'historical_lower':None if expected is None else expected['lower_95'],'historical_upper':None if expected is None else expected['upper_95'],'status':'VERIFIED_NUMERICALLY' if ok and enough else 'NUMERICAL_DISCREPANCY'};paired.append(rec)
   if rec['status']=='NUMERICAL_DISCREPANCY':discrepancies.append(rec)
 csvfile(out/'paired_recomputation.csv',paired);np.savez_compressed(out/'paired_bootstrap.npz',**boot)
 write(out/'discrepancies.json',{'material':bool(discrepancies),'findings':discrepancies,'dependent_interpretation_stopped':bool(discrepancies),'no_tolerance_changed_after_results':True})
 if discrepancies:raise RuntimeError('Paired interval discrepancy; stop dependent interpretation')
 write(out/'numerical_status.json',{'status':'VERIFIED_NUMERICALLY','metric_rows':len(records),'paired_rows':len(paired),'PHM_rows':len(phmrows),'bootstrap_seed':c['bootstrap_seed'],'bootstrap_draws':c['bootstrap_replicates'],'undefined_replicates_count':sum(x['undefined_replicates'] for x in paired)})
 textfile(out/'01_INDEPENDENT_RESULT_CHECK.md','# Independent numerical result check\n\nSeparate NumPy score-tie implementation; no project report/metric wrappers imported. Synthetic tests precede this execution.\n\n'+f'{len(records)} full-precision core metric comparisons, {len(paired)} paired AP/AUROC/Brier comparisons and {len(phmrows)} PHM error comparisons match tolerance {tol}. Historical 2000-draw paired intervals reproduce with seed20310927; invalid draws are counted, never redrawn.\n\n'+table(pd.DataFrame(paired).query("contrast in ['F2 minus U1','F6 minus F2','V1_0.1:F5 minus V1_0.1:F2','V1_0.1:F6 minus V1_0.1:F2']")[['contrast','metric','estimate','lower_95','upper_95','status']])+'\nIdentity evidence: sealed inventory/cohort, per-record feature row maps, explicit per-fold rows and documented condition-generation order. Legacy NPZs do not embed IDs. All audit tables carry explicit composite IDs and are joined by them. This is a provenance-bound numerical check, not independent acquisition validation.\n\nComplete-loss probabilities and saved decisions equal the surviving calibrated branch, including its fold-specific threshold. Normalized masked scalar-logit weights become exactly zero/one; frozen remaining-branch output has no learnable gate-only path. This is structural fallback, not a statistical improvement or information recovery.\n\nPHM uses current v3 run-level targets, 20 runs and the actual experiment-disjoint loop. The image reference row is explicitly NOT LOEO. Stale v2/fixed-split fields in the retained config do not override the actual verified inputs and grouping. The old paired ΔMAE is a bootstrap mean, not the empirical difference of displayed means. No PHM raw files were recovered or revalidated. Fitting-scope coverage is separately reported in fitting_scope_trace.md.\n\nPoint/interval reproduction does not erase adaptive study/model selection or establish independent confirmation.')
 return frame,models,draws


def sensitivities(c,frame,models,draws):
 r=Path(c['run']);out=r/'03_sensitivity_and_operating_points';y=frame.failure.to_numpy();groups=frame.recording_id.to_numpy();ps={n:models[n].p.to_numpy() for n in ['U1','F2']};rows=[];details={}
 for action in c['diagnostic']['action_order']:
  m=(frame.action==action).to_numpy();sub=frame[m];support={'action':action,'segments':len(sub),'recordings':sub.recording_id.nunique(),'failures':int(sub.failure.sum()),'failure_recordings':sub[sub.failure==1].recording_id.nunique(),'successes':int((sub.failure==0).sum()),'success_recordings':sub[sub.failure==0].recording_id.nunique(),'prevalence':float(sub.failure.mean())}
  boot=paired_bootstrap(y,ps,groups,mask=m,draws=draws);details[action]={}
  for j,metric in enumerate(['AUPRC','AUROC']):
   values={n:metrics(y[m],p[m])[metric] for n,p in ps.items()};ci=interval(boot['F2'][:,j]-boot['U1'][:,j]);flag=support['failure_recordings']<5 or ci['valid_replicates']<.95*c['bootstrap_replicates']
   rec={**support,'metric':metric,'U1':values['U1'],'F2':values['F2'],'F2_minus_U1':values['F2']-values['U1'],**ci,'support_flag':'UNSTABLE_SUPPORT' if flag else 'No prespecified support flag'};rows.append(rec);details[action][metric]=rec
 csvfile(out/'per_action_fusion.csv',rows)
 unique,inverse,_=draws;size=np.bincount(inverse);w=1/size[inverse];prevalence=float(np.average(y,weights=w));weighted=[]
 boot=paired_bootstrap(y,ps,groups,balanced=True,draws=draws)
 for j,m in enumerate(['AUPRC','AUROC','Brier']):
  v={n:metrics(y,p,weights=w)[m] for n,p in ps.items()}
  weighted.append({'analysis':'recording-balanced sensitivity analysis','metric':m,'weighted_positive_prevalence':prevalence,'U1':v['U1'],'F2':v['F2'],'F2_minus_U1':v['F2']-v['U1'],**interval(boot['F2'][:,j]-boot['U1'][:,j])})
 csvfile(out/'recording_weight_sensitivity.csv',weighted)
 ops=[]
 for name in ['U1','U2','F2','F6']:
  q=models[name];v=metrics(y,q.p,q.hard);tp,fp,tn,fn=[int(v[k]) for k in ['TP','FP','TN','FN']];flags=tp+fp;successes=tn+fp;failures=tp+fn
  ops.append({'model':name,'TP':tp,'FP':fp,'TN':tn,'FN':fn,'failure_precision':tp/flags if flags else None,'failure_recall':tp/failures,'specificity':tn/successes,'false_positive_rate':fp/successes,'flagged_fraction':flags/len(y),'false_flags_per_100_successes':100*fp/successes,'true_failures_per_100_flags':100*tp/flags if flags else None,'misses_per_100_failures':100*fn/failures,'flags_denominator':flags,'success_denominator':successes,'failure_denominator':failures,'segment_denominator':len(y)})
 csvfile(out/'operating_points.csv',ops)
 write(out/'paired_sensitivity.json',{'per_action':details,'recording_balanced':weighted,'operating_points':ops,'resampling':'whole recording draws before action filtering; same counts for both models; weighted occurrence mass1','bootstrap_seed':c['bootstrap_seed'],'replicates':c['bootstrap_replicates'],'unchanged_primary_estimand':'ordinary segment-weighted pooled OOF metrics','scope':'post-hoc exploratory sensitivities, not independent confirmation'})
 textfile(out/'03_SENSITIVITY_AND_OPERATING_POINTS.md','# Sensitivity and operating points\n\nQuestion: does actual F2 gain depend on action or recording weighting, and what do the training-selected thresholds mean? Core sources: original sealed U1/U2/F2/F6, joined on recording+segment identity. No branch/model/threshold fitting in this task.\n\n## Within-action actual fusion gain\n\n'+table(pd.DataFrame(rows))+'\nThese are actual F2−U1 prediction-score effects, distinct from the prior error-complementarity table. All four actions are retained. Shared whole-recording draws are filtered by action; invalid one-class/empty draws are counted, not replaced. Different APs reflect action-specific prevalence as well as ranking; no favorable macro-AP headline is created.\n\n## Recording-balanced sensitivity analysis\n\n'+table(pd.DataFrame(weighted))+'\nEvery segment in recording r has weight1/n_r; a recording drawn k times contributes weight k/n_r per segment. This is weighted pooled AP/AUROC/Brier, not a mean of per-recording AUROCs. Original segment-weighted estimates remain primary; changing the target-population weighting is a sensitivity analysis, not automatic invalidity.\n\n## Established operating points\n\n'+table(pd.DataFrame(ops))+'\nCounts use saved hard decisions, checked against retained fold-specific training-selected thresholds. True failures per100 flags is precision×100; misses per100 actual failures is (1−recall)×100; false flags per100 successful segments is FPR×100. The procedure may select different thresholds in different outer folds. These are retrospective completed-action classifications, not prospective warnings; no false alarms/hour is inferred without validated exposure time. No new test-outcome cutoff was chosen. Intervals remain conditional on fitted models and do not eliminate adaptive study selection.')

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--run',required=True);args=parser.parse_args();c=config_for(args.run)
 frame,models,draws=audit(c);sensitivities(c,frame,models,draws)
 print('NUMERICAL_AND_SENSITIVITY_COMPLETE',flush=True)
