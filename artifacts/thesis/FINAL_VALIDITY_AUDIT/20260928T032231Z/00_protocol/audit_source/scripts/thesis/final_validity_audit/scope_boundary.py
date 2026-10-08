"""Source/partition trace and timestamp-only boundary checks; no feature/model reruns."""
import argparse,re
from pathlib import Path
import numpy as np
import pandas as pd
import h5py
from .common import read,write,textfile,csvfile,table,config_for,freeze_revision,digest
from .numerical import load_cohort


def trace(c,frame,splits):
 root=Path(c['run']);s=c['sources'];out=root/'01_independent_result_check';groups=frame.recording_id.to_numpy();partition_checks=[];subchecks=[]
 for outer in splits['folds']:
  k=outer['fold'];ot=set(outer['test_recordings'])
  for inner in outer['inner']:
   j=inner['fold'];meta=read(Path(s['S1B'])/'stacking'/f'outer{k}_inner{j}.json');it=set(meta['train_recordings']);iv=set(meta['validation_recordings'])
   assert it==set(inner['train_recordings']) and iv==set(inner['validation_recordings']) and not (it|iv)&ot
   seen=set()
   for f in meta['subfolds']:
    a,b=set(f['train_recordings']),set(f['validation_recordings']);assert not a&b and a|b==it and not seen&b;seen|=b
   assert seen==it
   with np.load(Path(s['S2'])/'inputs'/f'outer{k}_inner{j}.npz',allow_pickle=False) as z:
    assert set(groups[z['train_rows']])==it and set(groups[z['validation_rows']])==iv
    assert len(z['train_rows'])==sum(frame.recording_id.isin(it)) and len(z['validation_rows'])==sum(frame.recording_id.isin(iv))
   partition_checks.append({'outer':k,'inner':j,'assessment_recordings':len(iv),'training_recordings':len(it),'outer_test_excluded':True,'row_maps_match':True})
   for sub in range(4):
    detail=read(Path(s['S2'])/'inputs'/f'outer{k}_inner{j}_sub{sub}.json');tr=np.asarray(detail['train_rows']);te=np.asarray(detail['test_rows']);a,b=set(groups[tr]),set(groups[te]);assert not a&b and a|b==it and not (a|b)&(iv|ot)
    seen2=set()
    for sel in detail['selection_partitions']:
     u,v=set(groups[sel['train_rows']]),set(groups[sel['validation_rows']]);assert not u&v and u|v==a and not (u|v)&(b|iv|ot) and not seen2&v;seen2|=v
    assert seen2==a
    with np.load(Path(s['S2'])/'inputs'/f'outer{k}_inner{j}_sub{sub}.npz',allow_pickle=False) as z:assert np.array_equal(z['rows'],te)
    subchecks.append({'outer':k,'inner':j,'sub':sub,'branch_assessment_excluded_from_selection_and_training':True,'outer_and_inner_assessment_excluded':True,'selection_folds':len(detail['selection_partitions'])})
 # Source identities bind code inspected here to retained training revisions.
 hashes=[]
 for artifact in [Path(s['S1'])/'training_implementation.json',Path(s['S1B'])/'implementation.json',Path(s['S2'])/'implementation.json']:
  obj=read(artifact)
  for path,expected in obj['source_sha256'].items():hashes.append({'path':path,'matches_training_source':digest(path)==expected,'source_manifest':str(artifact)})
 source_gaps=[x for x in hashes if not x['matches_training_source']]
 # Independently compare the retained final F6 quality scaler against outer0 training metadata.
 base=read('configs/reassemble/section1.json');cfg=read('configs/reassemble/section2.json')
 names=['hand.'+k for k in cfg['quality_visual']]+[n+'.'+k for n in base['sensor']['channels'] for k in cfg['quality_sensor']];records={}
 for rid in sorted(frame.recording_id.unique()):
  for seg in read(Path(s['inventory'])/'records'/f'{rid}.json')['segments']:
   values=[seg['video']['hand'].get(k) for k in cfg['quality_visual']]+[seg['sensor'][n].get(k) for n in base['sensor']['channels'] for k in cfg['quality_sensor']]
   records[rid,str(seg['segment_id'])]=values
 q=np.asarray([records[r.recording_id,r.segment_id] for r in frame.itertuples()],dtype=np.float32);tr=np.flatnonzero(frame.fold!=0)
 mean=np.nanmean(q[tr],axis=0).astype('float32');std=np.nanstd(q[tr],axis=0).astype('float32');mean=np.nan_to_num(mean,nan=0);std=np.where(np.isfinite(std)&(std>1e-6),std,1).astype('float32')
 fitted=read(Path(s['S2'])/'fits/F6_outer0_final_s0.json')['normalizers']['quality'];delta_mean=float(np.max(abs(mean-np.asarray(fitted['mean']))));delta_std=float(np.max(abs(std-np.asarray(fitted['std']))));assert max(delta_mean,delta_std)<=1e-8
 outermeta=read(Path(s['S1B'])/'stacking/outer0.json');deep=read(Path(s['S2'])/'inputs/outer0_inner0_sub0.json')
 summary={'status':'COMPLETED_WITH_PROVENANCE_LIMITATIONS','outer_inner_partition_checks':partition_checks,'additional_subpartition_checks':subchecks,'training_source_hashes':hashes,'source_hash_gaps':source_gaps,'representative':{'outer':0,'inner':0,'sub':0,'F6_quality_scaler_mean_max_difference':delta_mean,'F6_quality_scaler_std_max_difference':delta_std,'F2_stacker_training_segments':int((frame.fold!=0).sum()),'F2_stacker':outermeta['stacker'],'deep_branch_selected':{k:v['selected'] for k,v in deep['branches'].items()}},'limitations':['Exact original optimizer-step sample logs not retained; identities are recorded partition/source/provenance evidence, not a replay of every execution.','Original S1 statistical-sensor scaler/model state not retained at its original fit; subsequent recovery parity is reported separately.','Deep manual trace samples outer0/inner0/sub0; automated partition checks cover all20 inner and80 extra subfold manifests.','F2 threshold-only crossfit conditions on the branch OOF bank, as originally declared; not an unbiased end-to-end inner score.'],'suspected_outer_or_required_inner_assessment_leakage':bool(source_gaps)}
 write(out/'fitting_scope_checks.json',summary)
 stages=[
 ['Cohort/splits','Frozen inventory filter and saved cohort; all5 outer/20 inner partitions; S1 feature row indices','Direct identity and partition inspection','All required assessment recordings separated; branch features are label-independent full-segment measurements'],
 ['Branch scaling/fitting','section1_models.py Standardizer/logistic_fit/neural_fit; section1b.py fit_branch; outer0_inner0.json','Training source hashes and recorded partitions inspected','Normalizers use x[train]; epochs/C selected by subfold assessment confined to current training set'],
 ['Branch calibration','section1b.py fit_branch -> calibrate(oof[selected][train], y[train], raw_test)','Source and saved calibration coefficients inspected','Outer/inner assessment labels absent from calibration arguments; original optimizer execution not independently replayed'],
 ['Meta-training predictions','S1B stacking/outer0_inner0 plus subfold identities; S2 inputs/outer0_inner0_sub0','Recorded row arrays and disjoint groups independently checked','Each meta row is branch-held-out; additional S2 depth excludes inner assessment from gate-training branch selection/calibration'],
 ['F2 fit/threshold','S1B stacking/outer0.npz train_rows/test_rows and outer0.json stacker; fit_stacker source','Direct saved index/parameter evidence and source inspection','Only outer training branch OOF enters final stacker. Threshold crossfit is conditional on this bank; not independent full-pipeline inner performance'],
 ['F6 normalizer/fitting','S2 F6_outer0_final_s0.json, train_outer and fit_head source','Independent numerical scaler check plus recorded inputs','Quality mean/std equal outer0 training-only metadata; no assessment labels accepted by fit_head'],
 ['F6 selection/threshold','S2 outer0 inner candidates and predictions/outer0.json','Source/manifest trace','Configuration via mean inner AP; threshold via selected inner OOF. No final test selection; adaptivity of the study remains'],
 ['Outer predictions','S1 fold pieces; S1B test_rows; S2 outer0 test_rows; global OOF keyed joins','Independent keyed parity checks','Correct cohort/splits and frozen scores; no GPU or model fitting performed in this trace'],
 ]
 textfile(out/'fitting_scope_trace.md','# Fitting-scope trace\n\nRepresentative deep trace fixed before outcomes: outer0, inner0, additional sub0. Automated checks cover every available20 inner and80 additional branch-subfold identity manifests.\n\n'+table(pd.DataFrame(stages,columns=['Stage','Evidence','Evidence type','Finding']))+'\n\nOuter0 final F6 quality-scaler maximum mean/std differences: '+str((delta_mean,delta_std))+'.\n\n## Provenance limits\n\n'+''.join('- '+x+'\n' for x in summary['limitations'])+'\nStatus: COMPLETED_WITH_PROVENANCE_LIMITATIONS. No required assessment-recording overlap was found in the checked scopes. This does not certify every optimizer operation, historical cohort selection or independent study confirmation. Missing execution-level fit logs are PROVENANCE_GAP, not silently declared fully verified. F2’s conditional threshold crossfit is a declared training-only procedure and does not expose outer-test outcomes.\n')
 if source_gaps:raise RuntimeError('Historical training source mismatch; stop dependent fitting-scope interpretation')
 return summary


def boundaries(c,frame):
 s=c['sources'];out=Path(c['run'])/'02_task_and_shortcut_audit';rec=pd.read_parquet(Path(s['inventory'])/'recordings.parquet').set_index('recording_id');rows=[];overlaps=[];raw_metadata=[]
 streams=read('configs/reassemble/section1.json')['sensor']['channels']
 for rid,part in frame.groupby('recording_id',sort=True):
  path=Path(c['data_root'])/'raw/data'/rec.loc[rid,'filename'];before=path.stat();assert before.st_size==int(rec.loc[rid,'size_bytes']) and before.st_mtime_ns==int(rec.loc[rid,'mtime_ns'])
  ann=read(Path(s['inventory'])/'records'/f'{rid}.json');byid={str(x['segment_id']):x for x in ann['segments']}
  ordered=sorted([x for x in ann['segments'] if x['valid_interval']],key=lambda z:(z['start'],z['segment_id']))
  for a,b in zip(ordered,ordered[1:]):
   if a['end']>=b['start']:overlaps.append({'recording_id':rid,'segment_a':a['segment_id'],'segment_b':b['segment_id'],'overlap_seconds':float(a['end']-b['start']),'kind':'positive overlap' if a['end']>b['start'] else 'shared inclusive endpoint'})
  with h5py.File(path,'r') as h, np.load(Path(s['S1'])/'features'/f'{rid}.npz',allow_pickle=False) as z:
   chosen={int(ix):v for ix,v in zip(z['row_index'],z['frame_indices'])}
   for name in ['hand']+streams:
    t=np.asarray(h['timestamps'][name][()],dtype=np.float64)
    if t.ndim==2:assert np.allclose(t,t[:,:1],rtol=0,atol=1e-9);t=t[:,0]
    assert t.ndim==1 and np.isfinite(t).all() and np.all(np.diff(t)>0)
    for row in part.itertuples():
     ix=np.flatnonzero((t>=row.start)&(t<=row.end));entry={'recording_id':rid,'segment_id':row.segment_id,'action':row.action,'failure':row.failure,'stream':name,'count':len(ix),'samples_beyond_end':0 if not len(ix) else int((t[ix]>row.end).sum()),'samples_before_start':0 if not len(ix) else int((t[ix]<row.start).sum()),'start_endpoint_exact':bool(np.any(t[ix]==row.start)),'end_endpoint_exact':bool(np.any(t[ix]==row.end))}
     quality=byid[row.segment_id]['video']['hand'] if name=='hand' else byid[row.segment_id]['sensor'][name]
     assert quality['count']==len(ix)
     if name=='hand':
      expected=ix[np.linspace(0,len(ix)-1,16).round().astype(int)];assert np.array_equal(expected,chosen[row.Index]);assert len(np.unique(expected))==16
      entry['saved_frame_indices_match']=True;entry['first_selected_time']=float(t[expected[0]]);entry['last_selected_time']=float(t[expected[-1]])
     rows.append(entry)
  after=path.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
  raw_metadata.append({'path':str(path),'bytes':before.st_size,'mtime_ns':before.st_mtime_ns})
 csvfile(out/'timestamp_boundary_details.csv',rows);csvfile(out/'annotation_adjacencies.csv',overlaps)
 summary={'status':'COMPLETED_WITH_TASK_LIMITATIONS','recordings':len(raw_metadata),'stream_segment_checks':len(rows),'saved_visual_frame_selections_verified':sum(x.get('saved_frame_indices_match',False) for x in rows),'beyond_end_samples':sum(x['samples_beyond_end'] for x in rows),'before_start_samples':sum(x['samples_before_start'] for x in rows),'adjacent_overlap_or_shared_endpoint_count':len(overlaps),'positive_overlap_count':sum(x['overlap_seconds']>0 for x in overlaps),'interval_convention':'closed [start,end]; endpoint can legitimately be shared if annotations touch','sensor_values_not_reread':'Only raw timestamp arrays were read; sensor windows/counts and frame indices independently checked, exact historical signal extraction execution inferred from sealed source/cache.','whole_recording_timing_dependency':'native_dt uses median diff of whole-recording timestamp arrays for gap policy; no values outside segment interpolated. This timing metadata dependency is not an online causal preprocessing proof.','semantic_boundary_limit':'Whether an annotation includes trailing idle, intended outcome or next-action content cannot be established from timestamps alone; human boundary review pending.','label_filter':'same extraction functions for successes/failures; primary action and dual-complete filter based on audit availability, not correctness; selected complete-cohort conditioning remains a limitation','raw_metadata':raw_metadata}
 write(out/'boundary_checks.json',summary)
 ledger=[
 ['Annotated start/end','segments_info start/end -> inventory.py; alignment.interval_indices','Closed interval; annotation-derived boundaries','only from annotation / after completion','verified in raw timestamp selection','All branch windows and quality','Retrospective annotated action classification','Boundary annotation may encode outcome-dependent stopping; human review pending'],
 ['Action label','inventory.action_from_text; section2 action one-hot','Regex prefix only; free-text suffix/object excluded','only from annotation; action-start availability assumed, not proven by controller log','source verified; prospective availability unverified','Historical action baseline and F4/F6; not U1/U2/F2 input','Action-conditioned retrospective comparison','Recipe/process context predicts outcome; fixed D0 quantifies baseline'],
 ['Full duration','end-start; implicit in windows, explicit only in new D1/D2','Positive interval length and log for diagnostics','only after completion','verified construction','Not explicit core model field; affects sampling/quality','Retrospective diagnostic','Action failure can alter termination duration; does not alone prove shortcut use'],
 ['Progress resampling','alignment.resample_progress; section1_features.extract','512 evenly spaced positions over completed interval; no value extrapolation; long gaps NaN','only after completion','source and timestamp counts verified','All sensor features; statistics U1','Completed-segment sensor representation','Whole-recording clock cadence used in gap rule; not early warning'],
 ['Frame selection','section1_features.extract frame_indices','16 linspace-rounded inclusive in-segment indices, chronological pooling','only after completion','All4530 saved selections independently matched','Frozen visual features / U2 / fusion','Completed-segment visual representation','May include visible failure consequences; valid within task, not proof of prediction before failure'],
 ['Padding/observed masks','resampling and Standardizer; section1_models.SensorHead','NaN mask then training-mean fill; PatchTST mask not attention masking','after full segment','source inspected','PatchTST candidate; U1 statistics see training-only imputation','Missing-data handling','Not demonstrated online mask behavior or learned missing-modality robustness'],
 ['Sample counts','alignment.interval_coverage; audited stream count','Number of observed timestamp samples inside closed interval','after completion','All counts checked','No direct count in core gate; indirectly quality/sampling','Acquisition metadata','No raw count added to D2; fixed coverage fields only'],
 ['Coverage/missingness','sensor_quality / inspect_video; section2_data.quality_features','Finite/resampled finite/interpolated fractions, decoded/valid ratios, missing channels','during action provisional; full value only after completion','source and retained audit identity verified','F5/F6 quality;22 selected label-free quantities also in D2','Retrospective quality covariates','Quality can encode action dynamics rather than reliability; D2 is diagnostic'],
 ['Brightness/focus/motion/MAD/constant channels','media.py and alignment.sensor_quality','Descriptive in-window content/quality measurements','full quantity after completion','source inspected','Core quality gates only; excluded from D2','Content-conditioned allocation','Not a clean causal instrument for acquisition reliability'],
 ['Robot/controller measurements','robot_state five allowlisted streams','Force, torque, gripper positions, efforts, velocities','during action, full representation after completion','schema/source verified','Sensor branch and fusion through probabilities','Physical/control-response association with annotated outcome','Controller response can reflect failure consequence; no causal fault localization'],
 ['Absolute timestamps','raw timestamps; internal alignment only','Select intervals and estimate cadence; not feature column','acquisition-time metadata','source allowlist inspected','No explicit predictor; internal indexing only','Align measurements','Temporal/session drift may remain despite no ID input'],
 ['Recording/segment IDs and filenames','cohort/grouping/cache keys','Identity joins, folds, persistence only','acquisition/annotation metadata','source allowlist and split trace inspected','Not predictor','Recording-disjoint evaluation','Shared collection-day/objects can recur; no site/object OOD claim'],
 ['Free text / objects / success label','segments_info text and success','Action prefix; failure=not success target; object suffix retained in audit only','annotation-only','keyed inventory/label mapping verified','Free text/object not predictor; success only target','Annotated outcome task','No claim of independently verified physical truth; blinded sample pending'],
 ['Availability masks','section2_models DecisionGate; section3_evaluate','Core all ones; explicit zero/one at missingness intervention','measurement availability once known','saved weights and fallback verified','F4–F6; fixed fallback F1/F2','Structural missingness behavior','Masks enforce allocation, not learned reliability'],
 ]
 csvfile(out/'input_availability.csv',[dict(zip(['quantity','source_field_code','construction','availability','verification','enters_model','legitimate_interpretation','shortcut_and_limits'],row)) for row in ledger])
 textfile(out/'BOUNDARY_FINDINGS.md','# Input and task-boundary findings\n\n'+table(pd.DataFrame([{k:v for k,v in summary.items() if isinstance(v,(int,str)) and k!='raw_metadata'}]))+'\nAll timestamp/count/frame-index checks use sealed identities. Actual sensor values and deep features were not regenerated. No success-dependent extraction branch was found; the same inclusive window and frame/progress rules apply to both labels.\n\nA completed-segment classifier may legitimately observe full duration, controller response and visible failure consequences before the annotated end. That does not establish early warning. Whole-recording timestamp cadence enters the missing-gap policy; annotation semantics and any trailing idle remain a human-review question. Shared endpoints are an explicit closed-interval convention, not automatically next-action leakage. Positive annotation overlap, if present, is retained for boundary review rather than silently trimmed.\n')
 return summary

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--run',required=True);a=p.parse_args();c=config_for(a.run);freeze_revision(c['run'],'scope_before_trace');frame,splits=load_cohort(c);trace(c,frame,splits);boundaries(c,frame);print('SCOPE_AND_BOUNDARY_COMPLETE',flush=True)
