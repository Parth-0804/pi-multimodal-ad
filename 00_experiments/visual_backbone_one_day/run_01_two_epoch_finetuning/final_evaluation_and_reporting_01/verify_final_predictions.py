"""CPU-only independent arithmetic/lineage self-review of saved predictions."""
from pathlib import Path
import sys,json,math,subprocess,datetime
import numpy as np,pandas as pd
from sklearn.metrics import average_precision_score
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'source'))
from common import read,write,sha,config,CONDITIONS
from data import load_cohort
frame=load_cohort();lookup=frame.set_index('sample_id');jobs={(j['fold_name'],j['role']):j for j in read(ROOT/'data_manifests/fit_partitions.json')};evaluation=read(ROOT/'comparison/evaluation.json')
assert evaluation['status']=='COMPLETE' and len(evaluation['paired_folds'])==5
all_tables={};max_fusion_error=0.;checks=[]
for condition in CONDITIONS:
 parts=[]
 for fold in evaluation['paired_folds']:
  folder=ROOT/condition/fold;z=pd.read_csv(folder/'assessment_predictions.csv',dtype={'recording_id':str,'segment_id':str});job=jobs[fold,'outer_assessment'];expected=set(frame.iloc[job['predict']].sample_id)
  assert set(z.sample_id)==expected and not z.sample_id.duplicated().any()
  assert np.array_equal(z.failure.to_numpy(),lookup.loc[z.sample_id].failure.to_numpy())
  assert np.array_equal(z.recording_id.to_numpy(),lookup.loc[z.sample_id].recording_id.to_numpy())
  oof=pd.read_csv(folder/'fusion_training/identified_oof_branch_probabilities.csv');f2=read(folder/'F2_stacker.json');assert set(oof.sample_id)==set(frame.iloc[job['T']].sample_id)==set(f2['training_sample_ids']);assert not oof.sample_id.duplicated().any()
  assert not set(oof.recording_id)&set(z.recording_id)
  for role in ['inner_fold_01','inner_fold_02','inner_fold_03','inner_fold_04']:
   j=jobs[fold,role];v=read(folder/'fusion_training'/role/'visual_fit/complete.json');ix=oof.sample_id.isin(frame.iloc[j['predict']].sample_id);assert int(ix.sum())==len(j['predict']);assert set(oof.loc[ix,'visual_fit_id'])=={v['fit_id']}
  m=f2['model'];assert not m['balanced'] and m['C']==1 and f2['feature_columns']==['p_visual','p_sensor']
  value=z[['p_visual','p_sensor']].to_numpy()@np.asarray(m['coefficient'])+m['intercept'];direct=1/(1+np.exp(-value));error=float(np.max(np.abs(direct-z.p_fused)));assert error<=1e-12;max_fusion_error=max(max_fusion_error,error)
  for branch in ['visual','sensor','fused']:assert np.array_equal(z['decision_'+branch].to_numpy(),(z['p_'+branch].to_numpy()>=.5).astype(int))
  parts.append(z);checks.append({'condition':condition,'fold':fold,'assessment_rows':len(z),'T_OOF_rows':len(oof),'F2_arithmetic_max_absolute_error':error})
 all_tables[condition]=pd.concat(parts).sort_values('sample_id').reset_index(drop=True)
 q=all_tables[condition];assert len(q)==4530 and not q.sample_id.duplicated().any();assert q.groupby('recording_id').fold_name.nunique().eq(1).all()
 expected_row=next(x for x in evaluation['comparison'] if x['condition']==condition)
 for branch in ['visual','sensor','fused']:
  assert abs(average_precision_score(q.failure,q['p_'+branch])-expected_row[branch+'_pooled_AP'])<=1e-12
reference=all_tables[CONDITIONS[0]]
for name,q in all_tables.items():
 assert q[['sample_id','recording_id','segment_id','failure']].equals(reference[['sample_id','recording_id','segment_id','failure']])
 assert np.allclose(q.p_sensor,reference.p_sensor,atol=1e-14,rtol=0)
order=read(ROOT/'comparison/bootstrap_recording_order.json');draws=pd.read_csv(ROOT/'comparison/bootstrap_draws.csv');assert len(draws)==2000
rng=np.random.default_rng(config()['evaluation_seed']);cluster=pd.Categorical(reference.recording_id,categories=order).codes;expanded_errors=[]
for i in range(10):
 expected=np.bincount(rng.integers(0,len(order),len(order)),minlength=len(order));observed=np.asarray(json.loads(draws.iloc[i].recording_multiplicities));assert np.array_equal(expected,observed)
 if i<3:
  weights=observed[cluster];repeated=np.repeat(np.arange(len(reference)),weights)
  for condition in ['frozen_16_frames','fine_tuned_16_frames']:
   q=all_tables[condition];weighted=average_precision_score(q.failure,q.p_fused,sample_weight=weights);expanded=average_precision_score(q.failure.to_numpy()[repeated],q.p_fused.to_numpy()[repeated]);error=abs(weighted-expanded);assert error<=1e-12;expanded_errors.append(error)
assert subprocess.check_output(['git','diff','--binary'],cwd=ROOT.parents[2])==(ROOT/'provenance/git_diff_at_amendment.patch').read_bytes()
for old in read(ROOT/'provenance/historical_checkpoints_preserved.json'):assert sha(old['path'])==old['sha256']
write(ROOT/'final_evaluation_and_reporting_01/independent_arithmetic_self_review.json',{'passed':True,'scope':'Independent arithmetic implementation in the same assistant self-review; not an independent human or separate agent review','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'complete_outer_folds':5,'same_keyed_samples_per_condition':4530,'recordings':len(order),'outer_and_OOF_key_label_lineage_checks':True,'F2_probability_level_unweighted_logistic_checks':True,'F2_arithmetic_max_absolute_error':max_fusion_error,'thresholds_exactly_point5':True,'shared_sensor_probability_identity':True,'all12pooled_AP_values_recomputed':True,'first10bootstrap_draws_match_seed':True,'first3recording_cluster_draws_weighted_vs_expanded_AP_max_error':max(expanded_errors),'preexisting_tracked_binary_diff_unchanged':True,'historical_checkpoint_hashes_unchanged':True,'checks':checks})
print('Passed:20F2/OOF/assessment lineages,12AP values, grouped bootstrap semantics and original dirty-tree/checkpoint preservation.')
