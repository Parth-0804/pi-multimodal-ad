"""Descriptive diagnostics from existing numerical artifacts. Never imports study code."""
from pathlib import Path
import argparse
import datetime as dt
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys

OUT = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[4]
os.environ.setdefault('MPLCONFIGDIR', str(OUT / 'provenance/matplotlib_cache'))
os.environ.setdefault('OMP_NUM_THREADS', '4')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '4')
os.environ.setdefault('MKL_NUM_THREADS', '4')
import numpy as np
import pandas as pd
from scipy.special import expit, logit
from scipy.stats import spearmanr
from sklearn.metrics import average_precision_score, roc_auc_score, log_loss
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

INPUTS = {}


def register(path):
    path = Path(path)
    data = path.read_bytes()
    INPUTS[str(path.relative_to(REPO))] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    return data


def read_json(path):
    return json.loads(register(path))


def read_csv(path):
    register(path)
    return pd.read_csv(path, dtype={'sample_id': str, 'recording_id': str, 'segment_id': str})


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')


def save_table(name, records):
    df = records if isinstance(records, pd.DataFrame) else pd.DataFrame(records)
    df.to_csv(OUT / 'tables' / (name + '.csv'), index=False)
    return df


def ap(y, p):
    return float(average_precision_score(y, p)) if np.sum(y) else np.nan


def ap_contributions(y, score):
    """Allocate exact non-interpolated AP to positives, respecting score ties."""
    y, score = np.asarray(y, int), np.asarray(score, float)
    if not np.sum(y):
        return np.full(len(y), np.nan)
    order = np.argsort(-score, kind='stable')
    end = np.r_[np.flatnonzero(np.diff(score[order]) != 0), len(y) - 1]
    group_precision = np.cumsum(y[order])[end] / (end + 1)
    precision = np.repeat(group_precision, np.diff(np.r_[-1, end]))
    result = np.empty(len(y), float)
    result[order] = y[order] * precision / np.sum(y)
    return result


def metrics(y, p):
    y, p = np.asarray(y, int), np.asarray(p, float)
    dec = p >= .5
    return {'samples': len(y), 'failures': int(y.sum()), 'prevalence': float(y.mean()),
            'AP': ap(y, p), 'AUROC': float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else np.nan,
            'Brier': float(np.mean((p-y)**2)), 'log_loss': float(log_loss(y, p, labels=[0, 1])),
            'mean_probability': float(p.mean()), 'probability_sd': float(p.std()),
            'TP_at_0_5': int(np.sum(dec & (y == 1))), 'FP_at_0_5': int(np.sum(dec & (y == 0))),
            'FN_at_0_5': int(np.sum(~dec & (y == 1))), 'TN_at_0_5': int(np.sum(~dec & (y == 0)))}


def top_mask(frame, score, fraction):
    result = pd.Series(False, index=frame.index)
    for _, group in frame.groupby('fold_name', sort=True):
        selected = group.sort_values([score, 'sample_id'], ascending=[False, True]).head(int(np.ceil(len(group)*fraction)))
        result.loc[selected.index] = True
    return result.to_numpy()


def main():
    cfg = read_json(OUT / 'config/analysis_config.json')
    study = REPO / cfg['study_root']
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    condition_data, oof_data, coeffs, fit_rows, curves, cal_rows = {}, {}, {}, [], [], []
    prediction_checks = []
    source = read_json(study / 'config/resolved_config.json')
    policy = read_json(study / 'execution_policy.json')
    for file in ['training.py', 'visual_model.py', 'fusion.py']:
        register(study / 'source' / file)
    cohort = read_json(study / 'data_manifests/cohort_and_frames.json')
    cohort_by_id = {x['sample_id']: x for x in cohort}
    assert len(cohort_by_id) == len(cohort) == 4530
    lineage = read_json(study / 'data_manifests/fit_lineage_index.json')
    lineage_by_id = {x['fit_id']: x for x in lineage}
    for cond in cfg['conditions']:
        parts, oofparts = [], []
        for fold in [f'fold_{i:02}' for i in range(1, 6)]:
            p = study / cond / fold
            assessment = read_csv(p / 'assessment_predictions.csv').sort_values('sample_id').reset_index(drop=True)
            assert set(assessment.fold_name) == {fold}
            # Early frozen16 CSVs predate these two convenience columns. The
            # condition/epoch identity is verified against keyed fit manifests below.
            if 'condition' in assessment:
                assert set(assessment.condition) == {cond}
            if 'model_epochs' in assessment:
                assert set(assessment.model_epochs) == {policy['epoch_budgets'][cond]}
            assert not assessment.sample_id.duplicated().any()
            for row in assessment.itertuples():
                c = cohort_by_id[row.sample_id]
                assert (c['failure'], c['recording_id'], str(c['segment_id']), c['action']) == (row.failure, row.recording_id, row.segment_id, row.action)
            stacker = read_json(p / 'F2_stacker.json')
            coeffs[(cond, fold)] = stacker['model']
            m = stacker['model']
            expected = expit(assessment[['p_visual','p_sensor']].to_numpy() @ np.array(m['coefficient']) + m['intercept'])
            err = float(np.max(np.abs(expected-assessment.p_fused)))
            assert err < 1e-12
            assert set(assessment.stacker_fit_id) == {stacker['fit_id']}
            oof = read_csv(p / 'fusion_training/identified_oof_branch_probabilities.csv')
            assert not oof.sample_id.duplicated().any()
            assert set(oof.sample_id) == set(stacker['training_sample_ids'])
            assert not set(oof.recording_id) & set(assessment.recording_id)
            oof['fold_name'] = fold
            oofparts.append(oof)
            prediction_checks.append({'condition': cond, 'fold': fold, 'samples': len(assessment), 'F2_arithmetic_max_abs_error': err,
                'optional_metadata_absent': [k for k in ['condition','model_epochs'] if k not in assessment]})
            parts.append(assessment)
            roles = [*(('fusion_training/' + f'inner_fold_{i:02}', f'inner_fold_{i:02}') for i in range(1, 5)), ('outer_assessment', 'outer_assessment')]
            for folder, role in roles:
                f = p / folder / 'visual_fit'
                complete = read_json(f / 'complete.json')
                w = read_json(f / 'full_fit_weight_checks.json')
                cal = read_json(f / 'calibrator.json')
                curve = read_csv(f / 'learning_curve.csv')
                assert complete['fit_id'] == w['fit_id']
                assert complete['condition'] == cond and complete['job']['fold_name'] == fold
                assert hashlib.sha256((f / 'complete.json').read_bytes()).hexdigest() == lineage_by_id[complete['fit_id']]['manifest_sha256']
                assert complete['epochs_complete'] == len(curve) == policy['epoch_budgets'][cond]
                assert complete['replay']['passed'] and w['head_changed'] and w['earlier_backbone_and_running_buffers_unchanged']
                adapted = cond.startswith('fine_tuned')
                changes = w['changed_backbone_tensor_names']
                assert len(changes) == (5 if adapted else 0)
                assert all(x.startswith('encoder.stages.3.') for x in changes)
                assert all(x['finite'] for x in w['first_observed_post_resume_gradient_parameters'].values())
                if adapted:
                    assert any(x['nonzero'] for n,x in w['first_observed_post_resume_gradient_parameters'].items() if n.startswith('backbone.'))
                job = complete['job']
                groups = {key: {cohort[i]['recording_id'] for i in job[key]} for key in ['G', 'C', 'predict']}
                assert not groups['G'] & groups['C'] and not groups['G'] & groups['predict'] and not groups['C'] & groups['predict']
                caldata = read_csv(f / 'calibration_holdout_logits.csv')
                assert set(caldata.sample_id) == {cohort[i]['sample_id'] for i in job['C']}
                scoredata = assessment if role == 'outer_assessment' else oof[oof.visual_fit_id == complete['fit_id']]
                expected_cal = expit(cal['coefficient'][0]*scoredata.raw_visual_logit.to_numpy() + cal['intercept'])
                cal_error = float(np.max(np.abs(expected_cal-scoredata.p_visual)))
                assert cal_error < 1e-12 and len(scoredata) == len(job['predict'])
                assert set(scoredata.sample_id) == {cohort[i]['sample_id'] for i in job['predict']}
                assert set(scoredata.visual_fit_id) == {complete['fit_id']}
                assert cal['coefficient'][0] > 0
                raw_ap = ap(scoredata.failure, scoredata.raw_visual_logit)
                calibrated_ap = ap(scoredata.failure, scoredata.p_visual)
                assert abs(raw_ap-calibrated_ap) < 1e-12
                ident = {'condition': cond, 'fold': fold, 'role': role, 'fit_id': complete['fit_id']}
                fit_rows.append({**ident, 'epochs': len(curve), 'G_samples': len(job['G']), 'C_samples': len(job['C']),
                    'G_recordings': len(groups['G']), 'C_recordings': len(groups['C']), 'seed': complete['seed'],
                    'epoch_1_BCE': curve.training_BCE_mean.iloc[0], 'epoch_2_BCE': curve.training_BCE_mean.iloc[1],
                    'epoch_2_minus_1_BCE': curve.training_BCE_mean.iloc[1]-curve.training_BCE_mean.iloc[0],
                    'final_BCE': curve.training_BCE_mean.iloc[-1], 'head_changed': w['head_changed'],
                    'changed_CNN_tensors': len(changes), 'earlier_CNN_and_buffers_unchanged': True,
                    'saved_pixel_replay_passed': complete['replay']['passed'], 'positive_weight_G': complete['positive_weight_from_G'],
                    'trainable_CNN_parameters': complete['trainable_backbone_parameters'],
                    'training_wall_seconds': complete['training_wall_seconds'], 'calibration_replay_max_error': cal_error,
                    'G_membership_hash': hashlib.sha256(json.dumps(job['G']).encode()).hexdigest(),
                    'C_membership_hash': hashlib.sha256(json.dumps(job['C']).encode()).hexdigest()})
                for row in curve.to_dict('records'):
                    curves.append({**ident, **row})
                # C was used to fit this calibrator; its scores are not independent validation.
                cp = expit(cal['coefficient'][0]*caldata.raw_logit.to_numpy()+cal['intercept'])
                cal_rows.append({**ident, 'slope': cal['coefficient'][0], 'intercept': cal['intercept'],
                    'C_samples': len(caldata), 'C_failures': int(caldata.failure.sum()), 'C_recordings': caldata.recording_id.nunique(),
                    'C_apparent_Brier': float(np.mean((cp-caldata.failure)**2)), 'held_out_AP_raw': raw_ap,
                    'held_out_AP_calibrated': calibrated_ap, 'held_out_probability_sd': float(scoredata.p_visual.std(ddof=0))})
        joined = pd.concat(parts, ignore_index=True).sort_values('sample_id').reset_index(drop=True)
        assert len(joined) == 4530 and joined.failure.sum() == 509 and joined.recording_id.nunique() == 148
        assert not joined.sample_id.duplicated().any() and joined.groupby('recording_id').fold_name.nunique().max() == 1
        assert set(joined.sample_id) == set(cohort_by_id)
        assert np.isfinite(joined[['p_visual','p_sensor','p_fused','raw_visual_logit']]).all().all()
        assert ((joined[['p_visual','p_sensor','p_fused']] >= 0) & (joined[['p_visual','p_sensor','p_fused']] <= 1)).all().all()
        condition_data[cond] = joined
        oof_data[cond] = pd.concat(oofparts, ignore_index=True)
    fits = save_table('fit_learning_and_update_checks', fit_rows)
    save_table('all_learning_curves', curves)
    save_table('calibration_by_fit', cal_rows)
    reference = condition_data[cfg['conditions'][0]]
    sensor_raw_differences = {}
    for cond, frame in condition_data.items():
        assert frame[['sample_id','recording_id','segment_id','failure','action','fold_name']].equals(reference[['sample_id','recording_id','segment_id','failure','action','fold_name']])
        assert np.array_equal(frame.p_sensor, reference.p_sensor)
        sensor_raw_differences[cond] = float(np.max(np.abs(frame.raw_sensor_logit-reference.raw_sensor_logit)))
        assert sensor_raw_differences[cond] < 1e-12
        assert frame.sensor_fit_id.equals(reference.sensor_fit_id)
    for n in [16, 32]:
        a = fits[fits.condition == f'frozen_{n}_frames'].sort_values(['fold','role'])
        b = fits[fits.condition == f'fine_tuned_{n}_frames'].sort_values(['fold','role'])
        for col in ['G_membership_hash','C_membership_hash','seed','positive_weight_G']:
            assert np.array_equal(a[col], b[col])
    metric_rows, rel_rows, subgroup_rows, oof_rows, coef_rows = [], [], [], [], []
    bins = np.array(cfg['reliability_bin_edges'])
    for cond, frame in condition_data.items():
        for scope, data in [('pooled',frame), *list(frame.groupby('fold_name', sort=True))]:
            for branch, col in [('visual','p_visual'),('sensor','p_sensor'),('F2','p_fused')]:
                metric_rows.append({'condition':cond,'scope':scope,'branch':branch,**metrics(data.failure,data[col])})
        for branch, col in [('visual','p_visual'),('sensor','p_sensor'),('F2','p_fused')]:
            indices = np.clip(np.searchsorted(bins,frame[col],side='right')-1,0,len(bins)-2)
            for bi,(lo,hi) in enumerate(zip(bins[:-1],bins[1:])):
                sub = frame[indices == bi]
                rel_rows.append({'condition':cond,'branch':branch,'bin_low':lo,'bin_high':hi,'samples':len(sub),
                    'failures':int(sub.failure.sum()),'mean_probability':sub[col].mean(),'failure_rate':sub.failure.mean()})
        for grouping in ['action','recording_id']:
            for group, data in frame.groupby(grouping,sort=True):
                for branch,col in [('visual','p_visual'),('sensor','p_sensor'),('F2','p_fused')]:
                    subgroup_rows.append({'condition':cond,'grouping':grouping,'group':group,'branch':branch,
                        'recordings':data.recording_id.nunique(),'both_classes':data.failure.nunique()==2,**metrics(data.failure,data[col])})
        for fold, data in frame.groupby('fold_name',sort=True):
            oof=oof_data[cond]; oof=oof[oof.fold_name==fold]
            for stage, block in [('inner_OOF',oof),('outer_assessment',data)]:
                oof_rows.append({'condition':cond,'fold':fold,'scope':stage,**metrics(block.failure,block.p_visual)})
            m=coeffs[(cond,fold)];av,ass=m['coefficient']
            coef_rows.append({'condition':cond,'fold':fold,'visual_coefficient':av,'sensor_coefficient':ass,'intercept':m['intercept'],
                'visual_probability_sd':float(data.p_visual.std(ddof=0)),'sensor_probability_sd':float(data.p_sensor.std(ddof=0)),
                'visual_logit_term_sd':float((av*data.p_visual).std(ddof=0)), 'sensor_logit_term_sd':float((ass*data.p_sensor).std(ddof=0)),
                'visual_sensor_spearman':float(spearmanr(data.p_visual,data.p_sensor).statistic),
                'interpretation':'Score-scale description; not causal importance or modality percentages'})
    totals=save_table('assessment_metrics',metric_rows)
    rel=save_table('reliability_bins',rel_rows)
    save_table('action_and_recording_metrics',subgroup_rows)
    oof_metrics = save_table('OOF_vs_assessment_visual_metrics',oof_rows)
    save_table('fusion_coefficients_and_score_spread',coef_rows)
    transfer_rows = []
    for n in [16,32]:
        for fold in [f'fold_{i:02}' for i in range(1,6)]:
            frozen_cond, tuned_cond = f'frozen_{n}_frames', f'fine_tuned_{n}_frames'
            a = oof_data[frozen_cond].query('fold_name == @fold').sort_values('sample_id').reset_index(drop=True)
            b = oof_data[tuned_cond].query('fold_name == @fold').sort_values('sample_id').reset_index(drop=True)
            assert a[['sample_id','recording_id','failure']].equals(b[['sample_id','recording_id','failure']])
            assert np.array_equal(a.p_sensor,b.p_sensor)
            for stage in ['inner_OOF','outer_assessment']:
                ma = oof_metrics[(oof_metrics.condition==frozen_cond)&(oof_metrics.fold==fold)&(oof_metrics.scope==stage)].iloc[0]
                mb = oof_metrics[(oof_metrics.condition==tuned_cond)&(oof_metrics.fold==fold)&(oof_metrics.scope==stage)].iloc[0]
                transfer_rows.append({'frames':n,'fold':fold,'scope':stage,'samples':int(ma.samples),
                    'frozen_visual_AP':float(ma.AP),'fine_tuned_visual_AP':float(mb.AP),'visual_AP_change':float(mb.AP-ma.AP),
                    'visual_Brier_change':float(mb.Brier-ma.Brier),
                    'frozen_visual_coefficient':coeffs[(frozen_cond,fold)]['coefficient'][0],
                    'fine_tuned_visual_coefficient':coeffs[(tuned_cond,fold)]['coefficient'][0]})
    save_table('OOF_to_assessment_pair_changes',transfer_rows)
    prior=read_csv(study/'comparison/comparison_metrics.csv')
    for row in totals.itertuples():
        historical_branch = 'fused' if row.branch == 'F2' else row.branch
        old=prior[(prior.condition==row.condition)&(prior.scope==row.scope)&(prior.branch==historical_branch)]
        assert len(old)==1
        for name in ['AP','AUROC','Brier']:
            assert abs(float(old.iloc[0][name])-getattr(row,name))<1e-12
    old_intervals=read_csv(study/'comparison/paired_comparisons.csv')
    save_table('original_predeclared_intervals',old_intervals)
    pair_rows,rec_rows,action_rows,rank_rows,error_rows,example_rows,decomp_rows,sensor_rows=[],[],[],[],[],[],[],[]
    for n in [16,32]:
        a,b=condition_data[f'frozen_{n}_frames'],condition_data[f'fine_tuned_{n}_frames']
        pair=a[['sample_id','recording_id','segment_id','failure','action','fold_name']].copy()
        pair['frames']=n;pair['p_sensor']=a.p_sensor
        for branch,col in [('visual','p_visual'),('F2','p_fused')]:
            pair[f'{branch}_frozen_probability']=a[col]
            pair[f'{branch}_fine_tuned_probability']=b[col]
            pair[f'{branch}_probability_change']=b[col]-a[col]
            pair[f'{branch}_Brier_change']=(b[col]-a.failure)**2-(a[col]-a.failure)**2
            pair[f'{branch}_frozen_AP_contribution']=ap_contributions(a.failure,a[col])
            pair[f'{branch}_fine_tuned_AP_contribution']=ap_contributions(b.failure,b[col])
            pair[f'{branch}_AP_contribution_change']=pair[f'{branch}_fine_tuned_AP_contribution']-pair[f'{branch}_frozen_AP_contribution']
            assert abs(pair[f'{branch}_AP_contribution_change'].sum()-(ap(b.failure,b[col])-ap(a.failure,a[col])))<1e-12
            # Percentile ranks are within fold; negative change means an item moves toward the high-risk end.
            pair[f'{branch}_within_fold_rank_change']=b.groupby('fold_name')[col].rank(ascending=False,pct=True)-a.groupby('fold_name')[col].rank(ascending=False,pct=True)
            for scope,ix in [('pooled',a.index),*[(fold,g.index) for fold,g in a.groupby('fold_name')]]:
                pair_rows.append({'frames':n,'scope':scope,'branch':branch,'samples':len(ix),'failures':int(a.loc[ix].failure.sum()),
                    'frozen_AP':ap(a.loc[ix].failure,a.loc[ix,col]),'fine_tuned_AP':ap(b.loc[ix].failure,b.loc[ix,col]),
                    'AP_change':ap(b.loc[ix].failure,b.loc[ix,col])-ap(a.loc[ix].failure,a.loc[ix,col]),
                    'Brier_change':float(pair.loc[ix,f'{branch}_Brier_change'].mean())})
            da,db=a[col].to_numpy()>=.5,b[col].to_numpy()>=.5;y=a.failure.to_numpy()
            sensor=a.p_sensor.to_numpy()>=.5
            for group,mask in [('all',np.ones(len(y),bool)),('sensor_FN',(y==1)&~sensor),('sensor_FP',(y==0)&sensor)]:
                for class_y in [0,1]:
                    subset=mask&(y==class_y)
                    error_rows.append({'frames':n,'branch':branch,'group':group,'failure':class_y,'samples':int(subset.sum()),
                        'frozen_wrong_fine_correct':int(np.sum(subset&(da!=y)&(db==y))),
                        'frozen_correct_fine_wrong':int(np.sum(subset&(da==y)&(db!=y))),
                        'both_correct':int(np.sum(subset&(da==y)&(db==y))),
                        'both_wrong':int(np.sum(subset&(da!=y)&(db!=y)))})
        for grouping, storage in [('recording_id',rec_rows),('action',action_rows)]:
            for group,g in pair.groupby(grouping,sort=True):
                storage.append({'frames':n,grouping:group,'samples':len(g),'failures':int(g.failure.sum()),
                    'recordings':g.recording_id.nunique(),
                    **{f'{branch}_AP_contribution_change':float(g[f'{branch}_AP_contribution_change'].sum()) for branch in ['visual','F2']},
                    **{f'{branch}_Brier_change':float(g[f'{branch}_Brier_change'].mean()) for branch in ['visual','F2']}})
        for fraction in cfg['within_fold_top_fractions']:
            s=top_mask(a,'p_sensor',fraction);y=a.failure.to_numpy()==1
            for branch,col in [('visual','p_visual'),('F2','p_fused')]:
                f,t=top_mask(a,col,fraction),top_mask(b,col,fraction)
                rank_rows.append({'frames':n,'branch':branch,'top_fraction_within_fold':fraction,'selected_segments_per_recipe':int(f.sum()),
                    'total_failures':int(y.sum()),'sensor_captured_failures':int(np.sum(y&s)),
                    'frozen_captured_failures':int(np.sum(y&f)),'fine_tuned_captured_failures':int(np.sum(y&t)),
                    'frozen_captured_sensor_missed_failures':int(np.sum(y&~s&f)),
                    'fine_tuned_captured_sensor_missed_failures':int(np.sum(y&~s&t)),
                    'sensor_missed_newly_captured_by_fine_tuned':int(np.sum(y&~s&~f&t)),
                    'sensor_missed_lost_by_fine_tuned':int(np.sum(y&~s&f&~t))})
        cuts=np.array(cfg['sensor_probability_bin_edges'])
        which=np.clip(np.searchsorted(cuts,a.p_sensor,side='right')-1,0,len(cuts)-2)
        for bi,(lo,hi) in enumerate(zip(cuts[:-1],cuts[1:])):
            ix=a.index[which==bi]
            if not len(ix):continue
            for branch,col in [('visual','p_visual'),('F2','p_fused')]:
                sensor_rows.append({'frames':n,'sensor_probability_low':lo,'sensor_probability_high':hi,'branch':branch,
                    'samples':len(ix),'failures':int(a.loc[ix].failure.sum()),'recordings':a.loc[ix].recording_id.nunique(),
                    'frozen_AP_in_subset':ap(a.loc[ix].failure,a.loc[ix,col]),'fine_tuned_AP_in_subset':ap(b.loc[ix].failure,b.loc[ix,col]),
                    'global_AP_contribution_change':float(pair.loc[ix,f'{branch}_AP_contribution_change'].sum()),
                    'Brier_change':float(pair.loc[ix,f'{branch}_Brier_change'].mean())})
        for fold,g in pair.groupby('fold_name',sort=True):
            ix=g.index;ma,mb=coeffs[(f'frozen_{n}_frames',fold)],coeffs[(f'fine_tuned_{n}_frames',fold)]
            va,sa=ma['coefficient'];vb,sb=mb['coefficient']
            image_score=(va+vb)/2*(b.loc[ix,'p_visual']-a.loc[ix,'p_visual'])
            image_coefficient=(vb-va)*(b.loc[ix,'p_visual']+a.loc[ix,'p_visual'])/2
            sensor_coefficient=(sb-sa)*a.loc[ix,'p_sensor']
            intercept=mb['intercept']-ma['intercept']
            reconstructed=image_score+image_coefficient+sensor_coefficient+intercept
            observed=logit(b.loc[ix,'p_fused'])-logit(a.loc[ix,'p_fused'])
            assert np.max(np.abs(observed-reconstructed))<1e-11
            decomp_rows.append({'frames':n,'fold':fold,'samples':len(g),
                'mean_delta_fusion_logit':float(observed.mean()),'mean_abs_delta_fusion_logit':float(np.abs(observed).mean()),
                'mean_image_probability_term':float(image_score.mean()),'mean_image_coefficient_term':float(image_coefficient.mean()),
                'mean_sensor_coefficient_term':float(sensor_coefficient.mean()),'intercept_change':intercept,
                'mean_abs_image_probability_term':float(np.abs(image_score).mean()),'reconstruction_max_abs_error':float(np.max(np.abs(observed-reconstructed))),
                'interpretation':'Symmetric algebraic decomposition of existing predictions; not a causal or counterfactual experiment'})
        # Balanced directional illustrations, selected by absolute F2 squared-error change.
        for direction,ascending in [('fine_tuning_helps',True),('fine_tuning_hurts',False)]:
            selected=pair.sort_values(['F2_Brier_change','sample_id'],ascending=[ascending,True]).head(cfg['example_count_per_direction_per_pair'])
            for row in selected.to_dict('records'):
                example_rows.append({'selection':direction,**row,'image_review_status':'Numerical example only; raw frames not inspected'})
        save_table(f'paired_segments_{n}_frames',pair)
    pairs=save_table('paired_AP_and_Brier_changes',pair_rows)
    recordings=save_table('recording_AP_contributions',rec_rows)
    actions=save_table('action_AP_contributions',action_rows)
    ranks=save_table('fixed_budget_complementarity',rank_rows)
    save_table('threshold_error_transitions',error_rows)
    save_table('balanced_changed_prediction_examples',example_rows)
    save_table('exact_fusion_logit_change_decomposition',decomp_rows)
    save_table('sensor_score_strata',sensor_rows)
    # Compact summaries for a report, retaining the complete numerical tables above.
    training=[]
    for cond,g in fits.groupby('condition',sort=False):
        training.append({'condition':cond,'fits':len(g),'epoch_1_BCE_mean':float(g.epoch_1_BCE.mean()),
            'epoch_2_BCE_mean':float(g.epoch_2_BCE.mean()),'epoch_2_improved_fits':int((g.epoch_2_minus_1_BCE<0).sum()),
            'epoch_2_worsened_fits':int((g.epoch_2_minus_1_BCE>0).sum()),'training_hours':float(g.training_wall_seconds.sum()/3600)})
    train=save_table('learning_curve_summary',training)
    plot_diagnostics(cfg,condition_data,totals,pairs,train,rel,recordings,actions)
    findings={'completed_utc':dt.datetime.now(dt.timezone.utc).isoformat(), 'coverage':{'conditions':4,'assessment_segments_per_condition':4530,'failures':509,'recordings':148,'visual_fits':100},
        'pooled':totals[totals.scope=='pooled'].to_dict('records'),
        'paired_pooled':pairs[pairs.scope=='pooled'].to_dict('records'),
        'training_summary':training,'complementarity':ranks.to_dict('records'),
        'actions':actions.to_dict('records'),
        'important_limitations':['Exploratory diagnostics of already exposed outer assessments; no new confirmatory test.',
            'Frozen head five epochs versus fine-tuned head and final stage two epochs; cannot isolate adaptation from duration.',
            'One training seed family; recording uncertainty does not measure training randomness.',
            'No per-epoch held-out scores; C was used to fit calibrators, not an untouched tuning set.',
            'Overlapping training fits and repeated OOF rows across outer folds are not independent replicates.',
            'Numerical examples are deliberately selected; no new image review, label audit or feature-drift measurement.',
            'Recorded gradient/update/replay checks are inspected, not freshly executed model replays.'],
        'scope_executed':'Saved-result CPU diagnostics only; zero new model fits or raw-input inference', 'review':'Self-review; no independent reviewer used'}
    write_json(OUT/'findings.json',findings)
    write_json(OUT/'checks/analysis_checks.json',{'passed':True,'prediction_checks':prediction_checks,'fit_manifests_checked':len(fits),
        'all_assessment_metrics_match_original':True,'all_CNN_scope_checks_passed':True,'all_calibration_slopes_positive':True,
        'all_per_fit_visual_APs_preserved_by_calibration':True,'all_sensor_probabilities_identical':True,
        'sensor_raw_logit_max_abs_differences':sensor_raw_differences,'raw_logit_tolerance':1e-12,
        'all_pair_partitions_and_role_seeds_match':True,'AP_attribution_and_fusion_logit_decomposition_exact':True})
    versions={p:importlib.metadata.version(p) for p in ['numpy','pandas','scipy','scikit-learn','matplotlib']}
    write_json(OUT/'provenance/execution.json',{'started_utc':started,'finished_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
        'command': 'OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 ma_thesis_env/bin/python -B '+str(Path(__file__).relative_to(REPO)),
        'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
        'dirty_working_tree':True,'python':platform.python_version(),'packages':versions,'source_study':cfg['study_root'],
        'diagnostic_version':cfg['methodology_version'],'new_training_fits':0,'new_inference_segments':0,
        'raw_data_access':False,'network_access':False,'configuration_source':'config/analysis_config.json'})
    register(Path(__file__))
    write_json(OUT/'provenance/input_manifest.json',INPUTS)
    print(json.dumps({'status':'analysis complete','inputs':len(INPUTS),'fits_checked':100,'output':str(OUT.relative_to(REPO)),
        'pooled_differences':findings['paired_pooled'],'training':training,'complementarity':findings['complementarity']},indent=2))


def plot_diagnostics(cfg,data,totals,pairs,train,rel,recordings,actions):
    labels={'frozen_16_frames':'Frozen 16 (5 epochs)','fine_tuned_16_frames':'Fine-tuned 16 (2 epochs)',
            'frozen_32_frames':'Frozen 32 (5 epochs)','fine_tuned_32_frames':'Fine-tuned 32 (2 epochs)'}
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(10,4),constrained_layout=True)
    for ax,branch in zip(axes,['visual','F2']):
        for n,offset,color in [(16,-.06,'#1766a1'),(32,.06,'#cb6512')]:
            g=pairs[(pairs.frames==n)&(pairs.branch==branch)&(pairs.scope!='pooled')]
            ax.plot(np.arange(1,6)+offset,g.AP_change,marker='o',label=f'{n} frames',color=color)
        ax.axhline(0,color='gray',lw=1);ax.set(title=f'{branch}: fine-tuned minus frozen',xlabel='Outer assessment fold',ylabel='AP difference',xticks=range(1,6));ax.legend()
    fig.suptitle('Fine-tuning effects vary across folds; descriptive point differences')
    fig.savefig(OUT/'figures/fold_AP_changes.png',dpi=160);plt.close(fig)
    curves=pd.read_csv(OUT/'tables/all_learning_curves.csv')
    fig,axes=plt.subplots(1,2,figsize=(10,4),constrained_layout=True)
    for ax,n in zip(axes,[16,32]):
        for cond,color in [(f'frozen_{n}_frames','#1766a1'),(f'fine_tuned_{n}_frames','#cb6512')]:
            g=curves[curves.condition==cond]
            for _,f in g.groupby(['fold','role']):ax.plot(f.epoch,f.training_BCE_mean,alpha=.12,color=color)
            mean=g.groupby('epoch').training_BCE_mean.mean();ax.plot(mean.index,mean.values,marker='o',lw=2,label=labels[cond],color=color)
        ax.set(title=f'{n} frames',xlabel='Epoch',ylabel='Weighted training BCE',xticks=range(1,6));ax.legend(fontsize=8)
    fig.suptitle('Training loss only; no per-epoch held-out curve was saved')
    fig.savefig(OUT/'figures/training_dynamics.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,4),constrained_layout=True)
    for ax,branch in zip(axes,['visual','F2']):
        for cond in cfg['conditions']:
            g=rel[(rel.condition==cond)&(rel.branch==branch)&(rel.samples>=cfg['reliability_plot_min_samples'])]
            ax.plot(g.mean_probability,g.failure_rate,marker='o',label=labels[cond],alpha=.85)
        ax.plot([0,1],[0,1],ls='--',color='gray');ax.set(title=branch,xlabel='Mean predicted failure probability',ylabel='Observed failure fraction',xlim=(0,1),ylim=(0,1));ax.legend(fontsize=7)
    fig.suptitle('Outer-assessment reliability; plotted bins have at least 20 segments')
    fig.savefig(OUT/'figures/assessment_reliability.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,4),constrained_layout=True)
    for ax,n in zip(axes,[16,32]):
        g=actions[actions.frames==n]
        x=np.arange(len(g));ax.bar(x-.17,g.visual_AP_contribution_change,width=.34,label='Visual');ax.bar(x+.17,g.F2_AP_contribution_change,width=.34,label='Fusion')
        ax.axhline(0,color='gray',lw=1);ax.set(title=f'{n} frames',xticks=x,xticklabels=g.action,ylabel='Contribution to global AP difference');ax.legend()
    fig.suptitle('Exact AP accounting by action; contributions sum to the pooled change')
    fig.savefig(OUT/'figures/action_AP_accounting.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,4),constrained_layout=True)
    for ax,n in zip(axes,[16,32]):
        g=recordings[recordings.frames==n].sort_values('F2_AP_contribution_change')
        ax.bar(np.arange(len(g)),g.F2_AP_contribution_change,color=np.where(g.F2_AP_contribution_change>=0,'#228363','#bc4a46'))
        ax.axhline(0,color='gray',lw=1);ax.set(title=f'{n} frames; all 148 recordings',xlabel='Recording, sorted by AP contribution change',ylabel='Contribution to global fusion AP change')
    fig.suptitle('Recording contributions are accounting, not independent significance tests')
    fig.savefig(OUT/'figures/recording_AP_accounting.png',dpi=160);plt.close(fig)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    main()
