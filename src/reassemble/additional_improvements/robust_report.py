"""Paired recording/realization uncertainty, without a denoising ensemble."""
from pathlib import Path
import re
import numpy as np
import pandas as pd
from reassemble.section1_features import cohort
from reassemble.section1_report import metrics,METRICS,table
from reassemble.cluster_metrics import draws,weighted_metrics,intervals
from .common import config,read,write,progress

LABELS=['clean_F2','augmented_F2','clean_F6','augmented_F6','clean_A-ADAPTIVE','augmented_A-ADAPTIVE','HIST_F2','HIST_F6','TASK3_A']

def main():
    c=config();root=Path(c['run_dir']);task=root/'04_corruption_training';base=read(c['section1_config']);frame=cohort(base);y=frame.failure.to_numpy(int);n=len(y);fold=np.full(n,-1);predictions={}
    names=None;branch=None;thresholds=np.zeros((n,2));weights={};seeds={}
    for label in LABELS:
        for k in range(5):
            with np.load(task/f'outer{k}_{label}.npz') as z:
                rows=z['rows'];fold[rows]=k
                for condition,remaining in [('test_missing_visual',1),('test_missing_sensor',0)]:
                    index=list(z['names']).index(condition)
                    assert np.array_equal(z['p'][index],z['branch_p'][index,:,remaining]),(label,k,condition,'fallback probability')
                    assert np.array_equal(z['hard'][index],z['branch_p'][index,:,remaining]>=z['branch_thresholds'][:,remaining]),(label,k,condition,'fallback threshold')
                if names is None:
                    names=z['names'].copy();branch=np.zeros((len(names),n,2))
                assert np.array_equal(names,z['names'])
                if label not in predictions:
                    predictions[label]=dict(p=np.zeros((len(names),n)),hard=np.zeros((len(names),n)))
                    weights[label]=np.zeros((len(names),n,2));seeds[label]=dict(p=np.zeros((len(z['seed_p']),len(names),n)),hard=np.zeros((len(z['seed_p']),len(names),n)))
                for key in ['p','hard']:predictions[label][key][:,rows]=z[key];seeds[label][key][:,:,rows]=z['seed_'+key]
                weights[label][:,rows]=z['weights'];branch[:,rows]=z['branch_p'];thresholds[rows]=z['branch_thresholds']
    for column,label in [(0,'U_VISUAL'),(1,'U_SENSOR')]:predictions[label]=dict(p=branch[:,:,column],hard=(branch[:,:,column]>=thresholds[:,column]).astype(int))
    groups={}
    for i,name in enumerate(names):groups.setdefault(re.sub(r'_r\d+$','',str(name)),[]).append(i)
    bootstrap=draws(frame.recording_id.to_numpy(),c['bootstrap_replicates'],c['bootstrap_seed']);B=len(bootstrap);rng=np.random.default_rng(c['bootstrap_seed']+100)
    outputs={};boot={};points={};absolute=[];foldrows=[];seedrows=[];coefficient=[]
    for condition,indices in groups.items():
        outputs[condition]={};r=len(indices);sample=rng.integers(r,size=(B,r)) if r>1 else np.zeros((B,1),int)
        for label,values in predictions.items():
            if (condition=='test_missing_visual' and label=='U_VISUAL') or (condition=='test_missing_sensor' and label=='U_SENSOR'):continue
            point=np.mean([metrics(y,values['p'][i],values['hard'][i]) for i in indices],axis=0)
            replicate=np.stack([weighted_metrics(y,values['p'][i],values['hard'][i],bootstrap) for i in indices])
            conditional=np.mean(replicate[sample,np.arange(B)[:,None]],axis=1)
            points[condition,label]=point;boot[condition,label]=conditional
            outputs[condition][label]=intervals(point,conditional);absolute.append(dict(condition=condition,model=label,realizations=r,**dict(zip(METRICS,point))))
            for k in range(5):
                ii=fold==k;v=np.mean([metrics(y[ii],values['p'][i,ii],values['hard'][i,ii]) for i in indices],axis=0);foldrows.append(dict(condition=condition,model=label,fold=k,**dict(zip(METRICS,v))))
            if label in seeds:
                for s in range(len(seeds[label]['p'])):
                    v=np.mean([metrics(y,seeds[label]['p'][s,i],seeds[label]['hard'][s,i]) for i in indices],axis=0);seedrows.append(dict(condition=condition,model=label,seed=c['seeds'][s],**dict(zip(METRICS,v))))
            if label in weights:
                changed=weights[label][indices].mean((0,1));clean=weights[label][0].mean(0)
                coefficient.append(dict(condition=condition,model=label,visual=float(changed[0]),sensor=float(changed[1]),visual_change=float(changed[0]-clean[0]),sensor_change=float(changed[1]-clean[1]),interpretation='softmax gate weight' if label.endswith('F6') else 'effective probability-input logit coefficient'))
        progress(4,f'Hierarchical paired evaluation: {condition} complete')
    comparisons={};rows=[]
    for condition in groups:
        comparisons[condition]={}
        for label in LABELS:
            for reference in ['clean_F2','augmented_F2']:
                if label==reference:continue
                effect=intervals(points[condition,label]-points[condition,reference],boot[condition,label]-boot[condition,reference]);key=label+' minus '+reference;comparisons[condition][key]=effect
                rows.append(dict(condition=condition,contrast=key,**{m:effect[m]['estimate'] for m in METRICS},AP_lower95=effect['AUPRC']['lower_95'],AP_upper95=effect['AUPRC']['upper_95']))
            key=label+' degraded minus clean';comparisons[condition][key]=intervals(points[condition,label]-points['clean',label],boot[condition,label]-boot['clean',label])
            remaining='U_SENSOR' if any(v in condition for v in ['_V1_','_V2_','_V3_','missing_visual']) else 'U_VISUAL'
            if condition!='clean':comparisons[condition][label+' minus remaining '+remaining]=intervals(points[condition,label]-points[condition,remaining],boot[condition,label]-boot[condition,remaining])
    for condition in groups:
        for family in ['F2','F6','A-ADAPTIVE']:
            augmented='augmented_'+family;clean='clean_'+family
            effect=intervals(points[condition,augmented]-points[condition,clean],boot[condition,augmented]-boot[condition,clean]);key=augmented+' minus '+clean
            comparisons[condition][key]=effect
            rows.append(dict(condition=condition,contrast=key,**{m:effect[m]['estimate'] for m in METRICS},AP_lower95=effect['AUPRC']['lower_95'],AP_upper95=effect['AUPRC']['upper_95']))
    seen=[name for name in groups if name.startswith('test_V1_') or name.startswith('test_S1_')];assert len(seen)==6
    primary_point=np.mean([points[key,'augmented_A-ADAPTIVE']-points[key,'augmented_F2'] for key in seen],axis=0)
    primary_boot=np.mean([boot[key,'augmented_A-ADAPTIVE']-boot[key,'augmented_F2'] for key in seen],axis=0);primary=intervals(primary_point,primary_boot)
    ni={}
    for label in ['augmented_F2','augmented_F6','augmented_A-ADAPTIVE']:
        difference=intervals(points['clean',label]-points['clean','clean_F2'],boot['clean',label]-boot['clean','clean_F2'])
        own=label.replace('augmented_', 'clean_');own_difference=intervals(points['clean',label]-points['clean',own],boot['clean',label]-boot['clean',own])
        ni[label]=dict(versus_clean_F2=dict(metrics=difference,AP_margin=.01,noninferiority_supported=difference['AUPRC']['lower_95']>-.01),versus_own_clean_model=dict(metrics=own_difference,AP_margin=.01,noninferiority_supported=own_difference['AUPRC']['lower_95']>-.01))
    result=dict(metric_note='AUPRC means average precision',absolute=outputs,paired=comparisons,primary_seen_family_contrast=primary,clean_noninferiority=ni,
                uncertainty='2000 paired recording bootstrap draws; additionally sample realization indices within each condition, identical draws for all models. Average per-realization metrics, not probabilities. Deterministic conditions have one realization. Conditional on fits; marginal 95%; not independent confirmation or retraining uncertainty.',seen_conditions=seen)
    write(task/'results.json',result)
    for name,data in [('absolute_metrics',absolute),('paired_comparisons',rows),('per_fold_metrics',foldrows),('per_seed_metrics',seedrows),('weight_coefficient_response',coefficient)]:pd.DataFrame(data).to_csv(task/(name+'.csv'),index=False)
    ap=primary['AUPRC'];status='supported improvement' if ap['lower_95']>0 else ('supported deterioration' if ap['upper_95']<0 else 'inconclusive difference')
    text='# Task 4 — exposure-matched corruption training\n\nADDITIONAL EXPLORATORY EXPERIMENTS. [VERIFIED EXECUTION]\n\n'
    text+='Question: does exposure to partial degradation improve robustness, and does adaptation beat static fusion with the same exposure? Branch architectures, original fit procedures, cohort and folds are unchanged.\n\n'
    text+='Exact protocol: four training realizations per segment/family; mixture .5 clean/.25 native-pixel Gaussian (.01–.08)/.25 raw-sensor Gaussian (.05–.8 times training-channel SD). Quality is recomputed; no injected fault identifiers enter the model. Each parent contributes total weight1. Neural fits sample one view per parent epoch; static C1 fits the exact weighted expansion. All branch fit/selection/calibration/noise scale and quality normalization exclude the assessment recording. Validation uses distinct realizations and shared .5 cleanAP+.25 visualAP+.25 sensorAP objective. F6 is the original masked-logit family with hidden16; A-ADAPTIVE retains the frozen clean F2 anchor and Task3 bounded adjustments. Matched clean fits use identical architecture/budget/selection objective.\n\n'
    text+=f'[OBSERVED RESULT] Primary six-condition mean: augmented A-ADAPTIVE minus augmented F2 ΔAP {ap["estimate"]:+.4f}, marginal paired 95% [{ap["lower_95"]:+.4f}, {ap["upper_95"]:+.4f}]: **{status}**.\n\n'
    text+='Every Gaussian/frame-drop/channel-drop/block-drop condition has five fixed new realizations; blur, stuck F/T and complete loss are deterministic. Test observations are shared across models. Metrics, not predictions, are averaged. Paired intervals resample recordings and realization indices. Highest Gaussian severities extrapolate beyond augmentation; lower levels are in-range. Other families are held out of augmentation, but were already examined in the original study.\n\n'
    text+='All absolute metrics, clean changes, paired contrasts against both static controls and remaining unimodal references: `results.json`, `absolute_metrics.csv`, `paired_comparisons.csv`. Fold/seed results: `per_fold_metrics.csv`, `per_seed_metrics.csv`. Weight/coefficient response: `weight_coefficient_response.csv`; coefficients are not normalized probability weights or causal explanations. Single-loss predictions are explicitly replaced by the surviving branch probability and its original threshold.\n\n'
    rows=[]
    for condition in groups:
        effect=comparisons[condition].get('augmented_A-ADAPTIVE minus augmented_F2');v=effect['AUPRC'];rows.append([condition,f'{outputs[condition]["clean_F2"]["AUPRC"]["estimate"]:.4f}',f'{outputs[condition]["augmented_F2"]["AUPRC"]["estimate"]:.4f}',f'{outputs[condition]["augmented_A-ADAPTIVE"]["AUPRC"]["estimate"]:.4f}',f'{v["estimate"]:+.4f} [{v["lower_95"]:+.4f},{v["upper_95"]:+.4f}]'])
    text+=table(['Condition','clean F2 AP','augmented F2 AP','augmented adaptive AP','adaptive−augmented static ΔAP,95%'],rows)
    text+='\nClean non-inferiority uses a prospectively fixed .01 AP margin. A confidence interval crossing zero does not establish equivalence or non-inferiority; see the explicit lower-bound decisions in `results.json`. Adaptation claims require both appropriate coefficient response and advantage over equally exposed static fusion. Isolated favorable cells do not establish a general robustness claim.\n\n'
    text+='Limitations: same outcome-informed cohort; marginal intervals across many reported cells; fixed fitted models; finite seed/realization bank; artificial faults are not a representative industrial deployment distribution. Historical models remain additional sealed references, without rewriting historical conclusions. No changes from Tasks1/2 are inserted into this task.\n'
    (root/'reports/04_CORRUPTION_TRAINING_RESULTS.md').write_text(text)
    progress(4,'Matched corruption fits, all conditions, hierarchical uncertainty and report complete','complete')

if __name__=='__main__':main()
