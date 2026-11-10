"""Only missing CPU diagnostics; reuse completed checks, metric tables and bootstrap draws."""
from pathlib import Path
import datetime as dt
import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import time

os.environ.setdefault('OMP_NUM_THREADS','4')
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
os.environ.setdefault('MKL_NUM_THREADS','4')
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

OUT=Path(__file__).resolve().parents[1]
REPO=Path(__file__).resolve().parents[4]
CFG=json.loads((OUT/'config.json').read_text())
STUDY=REPO/CFG['study_root']
PRIOR=REPO/CFG['prior_diagnostics']
CONDITIONS=['frozen_16_frames','fine_tuned_16_frames','frozen_32_frames','fine_tuned_32_frames']
INPUTS={};EXPECTED={};VERIFIED=[]


def guard():
    assert dt.datetime.now(dt.timezone.utc)<dt.datetime.fromisoformat(CFG['deadline_utc']), '30-minute task boundary reached'


def get(path):
    guard();data=path.read_bytes();key=str(path.relative_to(REPO));sha=hashlib.sha256(data).hexdigest()
    INPUTS[key]={'bytes':len(data),'sha256':sha}
    if key in EXPECTED:
        assert EXPECTED[key]==sha,'Input identity changed: '+key
        VERIFIED.append(key)
    return data


def js(path):return json.loads(get(path))
def csv(path):
    get(path)
    return pd.read_csv(path,dtype={'sample_id':str,'recording_id':str,'segment_id':str})
def write(path,obj):path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def table(name,rows):
    frame=rows if isinstance(rows,pd.DataFrame) else pd.DataFrame(rows)
    frame.to_csv(OUT/'tables'/f'{name}.csv',index=False)
    return frame


def loss(y,p):
    p=np.clip(np.asarray(p,float),np.finfo(float).eps,1-np.finfo(float).eps)
    return -np.where(np.asarray(y)==1,np.log(p),np.log1p(-p))


def prepare_weighted_ap(y,score):
    order=np.argsort(-np.asarray(score),kind='stable')
    ends=np.r_[np.flatnonzero(np.diff(np.asarray(score)[order])!=0),len(order)-1]
    def evaluate(weights):
        w=np.asarray(weights)[order];positive=w*np.asarray(y)[order]
        totals=np.cumsum(w)[ends];tp=np.cumsum(positive)[ends]
        increment=np.diff(np.r_[0,tp]);precision=np.divide(tp,totals,out=np.zeros(len(tp),float),where=totals>0)
        return float(np.sum(increment*precision)/positive.sum())
    return evaluate


def main():
    guard();started=time.monotonic()
    if (OUT/'STATE.json').exists():raise RuntimeError('Completed packet already exists; do not overwrite it')
    old_inputs=js(PRIOR/'provenance/input_manifest.json')
    EXPECTED.update({k:v['sha256'] for k,v in old_inputs.items()})
    old_outputs=js(PRIOR/'provenance/output_manifest.json')
    EXPECTED.update({str((PRIOR/x['path']).relative_to(REPO)):x['sha256'] for x in old_outputs['files']})
    final_evaluation=js(STUDY/'comparison/evaluation.json')
    EXPECTED.update({str((STUDY/k).relative_to(REPO)):v for k,v in final_evaluation['prediction_sources'].items()})
    # Read actual reports/check receipts; reuse their scope rather than execute them again.
    receipts=['checks/analysis_checks.json','checks/final_self_check.json','checks/synthetic_tests.log','checks/SELF_REVIEW.md',
              'checks/pip_check.log','source/test_diagnostics.py','source/analyse_saved_results.py','FINE_TUNING_DIAGNOSTIC_REPORT.md']
    for name in receipts:get(PRIOR/name)
    get(STUDY/'checks/SELF_REVIEW_FINAL.md')
    get(STUDY/'source/evaluation.py')
    assert INPUTS[str((STUDY/'source/evaluation.py').relative_to(REPO))]['sha256']==final_evaluation['code']
    reused_metrics=csv(PRIOR/'tables/assessment_metrics.csv')
    original_intervals=csv(STUDY/'comparison/paired_comparisons.csv')
    data={};models={};distribution=[];overlap=[];calibrators=[]
    for condition in CONDITIONS:
        parts=[]
        for fold in [f'fold_{i:02}' for i in range(1,6)]:
            f=STUDY/condition/fold
            block=csv(f/'assessment_predictions.csv');parts.append(block)
            model=js(f/'F2_stacker.json')
            assert model['feature_columns']==['p_visual','p_sensor']
            models[(condition,fold)]=model['model']
            cal=js(f/'outer_assessment/visual_fit/calibrator.json')
            calibrators.append({'condition':condition,'fold':fold,'slope':cal['coefficient'][0],'intercept':cal['intercept'],
                'feature_order':'p_visual,p_sensor','F2_fit_id':model['fit_id']})
        a=pd.concat(parts,ignore_index=True).sort_values('sample_id').reset_index(drop=True)
        data[condition]=a
        for scope,g in [('pooled',a),*list(a.groupby('fold_name'))]:
            for truth in [None,0,1]:
                h=g if truth is None else g[g.failure==truth]
                for col in ['raw_visual_logit','p_visual','raw_sensor_logit','p_sensor','p_fused']:
                    q=h[col].quantile([.05,.5,.95])
                    distribution.append({'condition':condition,'scope':scope,'failure':'all' if truth is None else truth,'score':col,
                        'samples':len(h),'failures':int(h.failure.sum()),'mean':float(h[col].mean()),'std':float(h[col].std(ddof=0)),
                        'min':float(h[col].min()),'q05':float(q.loc[.05]),'median':float(q.loc[.5]),'q95':float(q.loc[.95]),'max':float(h[col].max()),
                        'unique_scores':int(h[col].nunique()),'segments_in_tied_groups':int(h[col].duplicated(keep=False).sum())})
        for branch,col in [('visual','p_visual'),('F2','p_fused')]:
            sensor_correct=(a.p_sensor>=.5).astype(int)==a.failure
            branch_correct=(a[col]>=.5).astype(int)==a.failure
            for truth in [0,1]:
                for bcorrect in [False,True]:
                    for scorrect in [False,True]:
                        mask=(a.failure==truth)&(branch_correct==bcorrect)&(sensor_correct==scorrect)
                        overlap.append({'condition':condition,'branch':branch,'failure':truth,'branch_correct':bcorrect,'sensor_correct':scorrect,
                            'samples':int(mask.sum()),'class_total':int((a.failure==truth).sum()),
                            'class_fraction':float(mask.sum()/(a.failure==truth).sum())})
    table('cross_modality_error_overlap_at_0_5',overlap)
    table('raw_and_calibrated_score_distributions',distribution)
    table('saved_calibrators_and_F2_feature_order',calibrators)
    continuous=[];ranking=[];examples=[]
    for frames in [16,32]:
        a,b=data[f'frozen_{frames}_frames'],data[f'fine_tuned_{frames}_frames']
        paired=csv(PRIOR/f'tables/paired_segments_{frames}_frames.csv').sort_values('sample_id').reset_index(drop=True)
        assert paired.sample_id.equals(a.sample_id) and paired.sample_id.equals(b.sample_id)
        paired['sensor_correct_at_0_5']=((a.p_sensor>=.5).astype(int)==a.failure)
        for branch,col in [('visual','p_visual'),('F2','p_fused')]:
            paired[f'{branch}_log_loss_change']=loss(b.failure,b[col])-loss(a.failure,a[col])
            paired[f'{branch}_pooled_rank_change']=b[col].rank(ascending=False,method='average',pct=True)-a[col].rank(ascending=False,method='average',pct=True)
        table(f'label_aware_paired_changes_{frames}_frames',paired)
        for truth in [0,1]:
            for correct in [None,False,True]:
                g=paired[paired.failure==truth]
                if correct is not None:g=g[g.sensor_correct_at_0_5==correct]
                for branch in ['visual','F2']:
                    continuous.append({'frames':frames,'failure':truth,'sensor_correct':'all' if correct is None else correct,'branch':branch,'samples':len(g),
                        'mean_Brier_change_reused':float(g[f'{branch}_Brier_change'].mean()),
                        'mean_log_loss_change':float(g[f'{branch}_log_loss_change'].mean()),
                        'Brier_improved_segments':int((g[f'{branch}_Brier_change']<0).sum()),
                        'log_loss_improved_segments':int((g[f'{branch}_log_loss_change']<0).sum())})
        positives=paired[paired.failure==1].copy()
        def direction(x):return np.where(x<0,'up',np.where(x>0,'down','same'))
        for rank_scope,suffix in [('pooled','pooled_rank_change'),('within_fold','within_fold_rank_change')]:
            positives['visual_direction']=direction(positives[f'visual_{suffix}'])
            positives['fusion_direction']=direction(positives[f'F2_{suffix}'])
            for (vd,fd),g in positives.groupby(['visual_direction','fusion_direction']):
                ranking.append({'frames':frames,'rank_scope':rank_scope,'visual_direction':vd,'fusion_direction':fd,'failures':len(g),
                    'visual_global_AP_contribution_change_reused':float(g.visual_AP_contribution_change.sum()),
                    'fusion_global_AP_contribution_change_reused':float(g.F2_AP_contribution_change.sum()),
                    'visual_mean_Brier_change':float(g.visual_Brier_change.mean()),'fusion_mean_Brier_change':float(g.F2_Brier_change.mean())})
                if rank_scope=='within_fold':
                    chosen=g.assign(displacement=g.visual_within_fold_rank_change.abs()).sort_values(['displacement','sample_id'],ascending=[False,True]).head(2)
                    for row in chosen.to_dict('records'):
                        sid=row['sample_id'];ix=a.index[a.sample_id==sid][0];fold=row['fold_name']
                        extra={}
                        for label,cond,block in [('frozen',f'frozen_{frames}_frames',a),('fine_tuned',f'fine_tuned_{frames}_frames',b)]:
                            m=models[(cond,fold)];r=block.loc[ix]
                            extra.update({f'{label}_visual_logit_term':float(m['coefficient'][0]*r.p_visual),
                                f'{label}_sensor_logit_term':float(m['coefficient'][1]*r.p_sensor),f'{label}_F2_intercept':m['intercept']})
                        row.pop('displacement',None)
                        examples.append({'selection':'Two largest within-fold visual rank displacements per nonempty visual/fusion direction cell',**row,**extra})
    table('label_aware_change_summary_by_truth_and_sensor',continuous)
    table('failure_rank_direction_combinations',ranking)
    table('selected_keyed_failure_rank_examples',examples)
    # Missing paired intervals only. Reuse original draws; never generate new draws.
    draws=csv(STUDY/'comparison/bootstrap_draws.csv');order=js(STUDY/'comparison/bootstrap_recording_order.json');policy=js(STUDY/'comparison/bootstrap_policy.json')
    assert INPUTS[str((STUDY/'comparison/bootstrap_draws.csv').relative_to(REPO))]['sha256']==policy['draws_sha256']
    assert INPUTS[str((STUDY/'comparison/bootstrap_recording_order.json').relative_to(REPO))]['sha256']==policy['recording_order_sha256']
    reference=data[CONDITIONS[0]];y=reference.failure.to_numpy(int);lookup={name:i for i,name in enumerate(order)}
    cluster=reference.recording_id.map(lookup).to_numpy(int)
    # Test only the new weighted-AP shortcut; do not rerun existing diagnostic/model tests.
    rng=np.random.default_rng(73)
    for _ in range(12):
        sy=rng.integers(0,2,12);sy[:2]=[0,1];sp=rng.integers(0,4,12);sw=rng.integers(0,4,12);sw[:2]=1
        assert abs(prepare_weighted_ap(sy,sp)(sw)-average_precision_score(sy,sp,sample_weight=sw))<1e-12
    evaluators={}
    for cond in CONDITIONS:
        assert data[cond].sample_id.equals(reference.sample_id)
        for branch,col in [('visual','p_visual'),('fused','p_fused')]:
            evaluators[(cond,branch)]=prepare_weighted_ap(y,data[cond][col].to_numpy())
    contrasts=[('fine_tuned32_minus_frozen32','fine_tuned_32_frames','frozen_32_frames'),('fine_tuned32_minus_frozen16','fine_tuned_32_frames','frozen_16_frames')]
    reps=[]
    for row in draws.itertuples():
        guard()
        if not row.valid_two_classes:continue
        counts=np.array(json.loads(row.recording_multiplicities));w=counts[cluster]
        values={key:fn(w) for key,fn in evaluators.items()}
        for name,left,right in contrasts:
            for branch in ['visual','fused']:
                reps.append({'replicate':row.replicate,'contrast':branch+':'+name,'AP_difference':values[(left,branch)]-values[(right,branch)]})
    replicate_table=table('missing_contrast_replicates_from_original_draws',reps)
    intervals=[]
    for name,left,right in contrasts:
        for branch in ['visual','fused']:
            col='visual' if branch=='visual' else 'F2'
            ma=reused_metrics[(reused_metrics.condition==left)&(reused_metrics.branch==col)&(reused_metrics.scope=='pooled')].iloc[0]
            mb=reused_metrics[(reused_metrics.condition==right)&(reused_metrics.branch==col)&(reused_metrics.scope=='pooled')].iloc[0]
            values=replicate_table[replicate_table.contrast==branch+':'+name].AP_difference
            lo,hi=np.percentile(values,[2.5,97.5])
            intervals.append({'contrast':branch+':'+name,'AP_difference':float(ma.AP-mb.AP),'percentile_95_low':float(lo),'percentile_95_high':float(hi),
                'valid_replicates':len(values),'primary':False,'status':'NEW_EXPLORATORY','draws_sha256':policy['draws_sha256']})
    new_intervals=table('new_exploratory_paired_intervals',intervals)
    complete_intervals=original_intervals.copy();complete_intervals['status']='REUSED'
    table('requested_paired_intervals',pd.concat([complete_intervals,new_intervals],ignore_index=True))
    # Separate pooled, mean-fold and each fold; all numbers come from completed metrics.
    summaries=[]
    for (condition,branch),g in reused_metrics.groupby(['condition','branch'],sort=False):
        summaries.append({'condition':condition,'branch':branch,'pooled_AP':float(g[g.scope=='pooled'].AP.iloc[0]),
            'mean_fold_AP':float(g[g.scope!='pooled'].AP.mean()),**{f'{r.scope}_AP':r.AP for r in g[g.scope!='pooled'].itertuples()}})
    table('pooled_mean_fold_and_per_fold_AP_reused',summaries)
    # Bundle selected existing evidence byte-for-byte, without recomputing it.
    reused=['FINE_TUNING_DIAGNOSTIC_REPORT.md','checks/analysis_checks.json','checks/final_self_check.json','checks/SELF_REVIEW.md','checks/synthetic_tests.log',
        'tables/assessment_metrics.csv','tables/OOF_to_assessment_pair_changes.csv','tables/fixed_budget_complementarity.csv',
        'tables/sensor_score_strata.csv','tables/calibration_by_fit.csv','tables/reliability_bins.csv',
        'tables/fusion_coefficients_and_score_spread.csv','tables/exact_fusion_logit_change_decomposition.csv',
        'tables/action_AP_contributions.csv','tables/recording_AP_contributions.csv','tables/learning_curve_summary.csv','source/test_diagnostics.py']
    reused_index=[]
    for name in reused:
        contents=get(PRIOR/name);target=OUT/'reused'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(contents)
        reused_index.append({'source':str((PRIOR/name).relative_to(REPO)),'packet_copy':str(target.relative_to(OUT)),'sha256':hashlib.sha256(contents).hexdigest()})
    for name in ['comparison/plots/pooled_precision_recall.png','comparison/bootstrap_policy.json']:
        contents=get(STUDY/name);target=OUT/'reused'/Path(name).name;target.write_bytes(contents)
        reused_index.append({'source':str((STUDY/name).relative_to(REPO)),'packet_copy':str(target.relative_to(OUT)),'sha256':hashlib.sha256(contents).hexdigest()})
    write(OUT/'provenance/reused_evidence.json',reused_index)
    get(OUT/'config.json');get(Path(__file__))
    write(OUT/'provenance/input_manifest.json',INPUTS)
    write(OUT/'checks/missing_diagnostics_checks.json',{'passed':True,'weighted_AP_synthetic_cases':12,'original_draws_reused':2000,
        'new_exploratory_intervals':4,'input_identity_matches_to_prior_evidence':len(set(VERIFIED)),
        'all_saved_F2_feature_orders_match':True,'completed_model_or_validation_suites_repeated':False,
        'full_AP_attribution_recomputed':False,'plots_regenerated':False,'alternative_models_evaluated':False})
    write(OUT/'provenance/execution.json',{'finished_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'started_utc':CFG['started_utc'],
        'elapsed_analysis_script_seconds':time.monotonic()-started,'command':'OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 ma_thesis_env/bin/python -B '+str(Path(__file__).relative_to(REPO)),
        'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),'python':platform.python_version(),
        'packages':{p:importlib.metadata.version(p) for p in ['numpy','pandas','scikit-learn']},'CPU_only':True,'new_fits':0,'new_raw_input_inference':0,
        'review':'Self-review; no independent reviewer','source_study':str(STUDY.relative_to(REPO))})
    print(json.dumps({'status':'missing computations complete','new_intervals':intervals,'ranking':ranking,'continuous':continuous},indent=2))


if __name__=='__main__':main()
