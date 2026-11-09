"""Plain-English, artifact-backed dataset reports after all permitted evaluations."""
import json
import os
import platform
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve,confusion_matrix

from external_eval.io import write_json,sha,utc
from external_eval.analysis import summarize


def table(frame,columns=None):
    if columns is not None:frame=frame[columns]
    def value(x):
        if isinstance(x,(float,np.floating)):return 'NA' if not np.isfinite(x) else f'{x:.6f}'
        return str(x).replace('|','/')
    return '| '+' | '.join(frame.columns)+' |\n| '+' | '.join(['---']*len(frame.columns))+' |\n'+''.join('| '+' | '.join(value(x) for x in row)+' |\n' for row in frame.itertuples(index=False,name=None))


def text(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if path.read_text()!=value.rstrip()+'\n':raise ValueError('Final report differs; preserve and use a versioned report: '+str(path))
        return
    with path.open('x') as f:f.write(value.rstrip()+'\n')


def figures(root,predictions,primary):
    clean=predictions[(predictions.protocol==primary)&(predictions.role=='test')&(predictions.corruption=='clean')]
    figure_root=root/'06_evaluation_results/figures';figure_root.mkdir(exist_ok=True)
    conditions=sorted(clean.initialization.unique());paths=[]
    for condition in conditions:
        data=clean[(clean.initialization==condition)&(clean.seed==42)]
        models=sorted(data.model.unique())
        fig,ax=plt.subplots(figsize=(10,7),layout='constrained')
        for model,g in data.groupby('model'):
            if model.endswith('DIAGNOSTIC'):continue
            precision,recall,_=precision_recall_curve(g.target,g.probability)
            ax.step(recall,precision,where='post',label=model)
        ax.axhline(float(data[data.model=='visual'].target.mean()),color='grey',ls='--',label='positive prevalence')
        ax.set(xlabel='Recall',ylabel='Precision',xlim=(0,1),ylim=(0,1.02),title=f'{root.name} / {condition}: held-out PR curves, fixed seed 42')
        ax.legend(fontsize=8);p=figure_root/(condition+'_precision_recall.png');fig.savefig(p,dpi=140);plt.close(fig);paths.append(p)
        n=len(models);fig,axes=plt.subplots(2,int(np.ceil(n/2)),figsize=(3*np.ceil(n/2),6),layout='constrained')
        for ax,model in zip(axes.flat,models):
            g=data[data.model==model];cm=confusion_matrix(g.target,g.probability>=.5,labels=[0,1]);ax.imshow(cm,cmap='Blues')
            for i in range(2):
                for j in range(2):ax.text(j,i,str(cm[i,j]),ha='center',va='center')
            ax.set(title=model,xticks=[0,1],yticks=[0,1],xlabel='Predicted',ylabel='Native binary target')
        for ax in list(axes.flat)[n:]:ax.axis('off')
        p=figure_root/(condition+'_confusion_matrices.png');fig.savefig(p,dpi=140);plt.close(fig);paths.append(p)
        fig,ax=plt.subplots(figsize=(9,7),layout='constrained');ax.plot([0,1],[0,1],ls='--',color='grey')
        reliability=[]
        for model,g in data.groupby('model'):
            if model.endswith('DIAGNOSTIC'):continue
            bins=np.minimum((g.probability.to_numpy()*10).astype(int),9);xs=[];ys=[]
            for k in range(10):
                selected=g.iloc[np.flatnonzero(bins==k)]
                if len(selected):
                    xs.append(float(selected.probability.mean()));ys.append(float(selected.target.mean()))
                    reliability.append({'initialization':condition,'model':model,'bin':k,'examples':len(selected),
                        'mean_predicted_probability':xs[-1],'observed_positive_fraction':ys[-1]})
            ax.plot(xs,ys,marker='o',label=model)
        ax.set(xlabel='Mean predicted failure/anomaly probability',ylabel='Observed positive fraction',xlim=(0,1),ylim=(0,1),title='Calibration assessment only; no held-out calibrator fitted')
        ax.legend(fontsize=8);p=figure_root/(condition+'_calibration.png');fig.savefig(p,dpi=140);plt.close(fig);paths.append(p)
        pd.DataFrame(reliability).to_csv(root/'06_evaluation_results/calibration'/(condition+'_bin_counts.csv'),index=False)
    return paths


def robustness_figures(root,pooled,primary):
    data=pooled[(pooled.protocol==primary)&(pooled.role=='test')&~pooled.model.str.endswith('DIAGNOSTIC')]
    dest=root/'07_robustness_experiments/comparison_reports';dest.mkdir(parents=True,exist_ok=True)
    paths=[]
    for condition,g in data.groupby('initialization'):
        matrix=g.groupby(['model','corruption']).AP.mean().unstack()
        columns=['clean']+[c for c in matrix.columns if c not in ['clean','missing_visual','missing_sensor']]+['missing_visual','missing_sensor']
        matrix=matrix.reindex(columns=[c for c in columns if c in matrix])
        fig,ax=plt.subplots(figsize=(17,max(4,.6*len(matrix))),layout='constrained')
        image=ax.imshow(matrix.to_numpy(),vmin=0,vmax=1,cmap='viridis',aspect='auto')
        ax.set(yticks=np.arange(len(matrix)),yticklabels=matrix.index,xticks=np.arange(len(matrix.columns)),xticklabels=matrix.columns,
            title=f'{condition}: held-out AP, mean of all three seeds; white = unavailable unimodal input')
        plt.setp(ax.get_xticklabels(),rotation=65,ha='right',fontsize=8);fig.colorbar(image,ax=ax,label='Average precision')
        p=dest/(condition+'_robustness_heatmap.png');fig.savefig(p,dpi=140);plt.close(fig);paths.append(p)
    return paths


def training_curves(root,cases,primary):
    """All fixed-seed primary outer-refit loss traces, without test selection."""
    records=[];fig,axes=plt.subplots(1,2,figsize=(14,5),layout='constrained')
    for case in cases:
        if case['protocol']!=primary:continue
        trace=json.loads((Path(case['predictions']).parent/'training_and_runtime.json').read_text())
        fit=trace['base_fits'][-1];losses=fit['log']['losses']
        label=f"{case['initialization']} seed{case['seed']} outer{case['fold']}"
        axes[0].plot(np.arange(1,len(losses)+1),losses,label=label,alpha=.7)
        for n,value in enumerate(losses):records.append({'case_id':case['case_id'],'model':'visual','update':n+1,'training_loss':value})
        case_root=root/'05_trained_models/f2_fusion'/case['case_id']
        for path in sorted(case_root.glob('*/QG_*.json')):
            if path.name not in ['QG_clean.json','QG_aug.json']:continue
            data=json.loads(path.read_text())
            axes[1].plot(np.arange(1,len(data['loss_by_epoch'])+1),data['loss_by_epoch'],alpha=.6,label=label+' '+path.stem)
            for n,value in enumerate(data['loss_by_epoch']):records.append({'case_id':case['case_id'],'model':path.stem,'update':n+1,'training_loss':value})
    axes[0].set(title='Visual head: every minibatch update',xlabel='Update',ylabel='Training weighted BCE');axes[0].legend(fontsize=6)
    axes[1].set(title='Quality gates: every fixed training epoch',xlabel='Epoch',ylabel='OOF-training BCE')
    if axes[1].lines:axes[1].legend(fontsize=5,ncol=2)
    else:axes[1].text(.1,.5,'Gate fitting blocked by participant-OOF gate',transform=axes[1].transAxes)
    dest=root/'06_evaluation_results/figures';dest.mkdir(exist_ok=True);fig.savefig(dest/'training_curves.png',dpi=140);plt.close(fig)
    pd.DataFrame(records).to_csv(root/'06_evaluation_results/metrics/training_loss_curves.csv',index=False)


def cohort_figures(root,manifest,dataset):
    dest=root/'08_visual_examples_and_eda';dest.mkdir(exist_ok=True)
    fig,axes=plt.subplots(1,2,figsize=(13,5),layout='constrained')
    group='machine' if dataset=='MSM' else 'official_split'
    counts=pd.crosstab(manifest[group],manifest.native_label)
    counts.plot.bar(ax=axes[0],rot=15);axes[0].set(title='Admitted native labels (no relabeling)',ylabel='Native prediction units')
    for label,g in manifest.groupby('native_label'):axes[1].hist(g.duration_s,bins=35,histtype='step',label=f'native{label}')
    axes[1].set(xlabel='Common observation duration (s)',ylabel='Native prediction units',title='Observation horizons; no class-dependent frame sampling');axes[1].legend()
    fig.savefig(dest/'cohort_overview.png',dpi=140);plt.close(fig)
    if dataset=='MSM':
        counts=pd.crosstab(manifest.direction,manifest.native_label);counts.to_csv(dest/'label_by_direction.csv')
        fig,axes=plt.subplots(1,2,figsize=(12,5),layout='constrained');counts.plot.bar(ax=axes[0],rot=0)
        axes[0].set(title='Cutting direction versus native class',ylabel='Native cuts')
        rates=manifest.groupby('direction').target.agg(['mean','count']);rates['mean'].plot.bar(ax=axes[1],rot=0)
        axes[1].set(title='Label1 prevalence by direction',ylabel='Fraction positive',ylim=(0,1))
        fig.savefig(dest/'direction_confound.png',dpi=140);plt.close(fig)


def methods(root,canonical,config,gate,manifest):
    dataset=config['dataset'];is_msm=dataset=='MSM'
    source='https://www.kaggle.com/datasets/manufuturetoday/multi-sensor-for-metal-milling-anomaly' if is_msm else 'https://zenodo.org/records/10708763'
    doi='10.34740/kaggle/ds/8392825' if is_msm else '10.5281/zenodo.10708763'
    scope=('56 laboratory experiments on VM20i/VMX30Ui; industrial VF10 excluded because it has no supplied video.' if is_msm else
        '589 native trials on Toyota HSR and Kinova Gen3, with 17 participants reported by the datasheet. Native participant IDs are not released.')
    why=('A manufacturing domain with native per-cut abnormalities, phone video and numerical MTC signals tests software/representation portability beyond robot manipulation.' if is_msm else
        'A human–robot interaction domain with successful and failed completed trials, RGB and wrist wrench observations tests a second task and sensor contract.')
    raw=(f"The original `MILLING DATASET/` tree remains intact. The canonical raw path is a verified relative symlink; no large video or sensor file was moved or copied. All 282 minimal laboratory raw-file hashes were verified. Historical Stage 1–5 reports, corrections, matched reviews and negative/blocked findings remain in `MSM/99_preserved_previous_work/MILLING_DATASET/`." if is_msm else
         'All official archives, labels, class mapping and datasheet were downloaded from pinned Zenodo record 10708763, version v1. Official MD5 and independent SHA-256 hashes are recorded. Only required video/wrench/time/metadata members were extracted; unused flow/I3D data remain preserved in the complete checked archives. The sample is a training subset and is never an independent model test.')
    labels=('Native 0 is stable normal cutting, 1 is intervention-worthy abnormal cutting and 2 is stable cutting with a defective tool. Primary binary target is 1 versus 0/2. The entire fitting/splitting pipeline is repeated after excluding label 2 as a separate sensitivity; no native label was rewritten.' if is_msm else
        'Released outcome IDs are verified from class_names.json: 0 success, 1 no approach, 2 no grasp (robot-to-human) or no release (human-to-robot), 3 drop. Binary failure is any native nonzero outcome. Trial IDs restart in each split, so identities are official-split-qualified; this is not a participant mapping. Native counts are 156 success, 131 no approach, 140 outcome-2 and 162 drop. The datasheet table has two more outcome-2 and two fewer drop cases; the released native files govern, and the binary failure total is unchanged.')
    alignment=('The corrected final Stage 2/5 audio calibration is reused, never refitted from labels. Video time = sensor time + offset, only inside accepted acoustic support. VMX9 remains +49.73 s (not the rejected +16.04 alias). Each native half-open cut has exactly 16 ordered unique source frames with content hashes, PTS and uncertainty guards. MTC uses the identical cut, finite 15-channel values, at least five rows and no gap over 0.5 s including edges; no interpolation or ACC substitution.' if is_msm else
        'Every admitted supplied wrench_resampled.npy is exactly reproduced from raw wrench.npy using the nearest raw timestamp, matching the author resample.py implementation. Each native camera index joins to head_cam_ts.npy and the corresponding six-wrench row. Video PTS are retained separately and are not assumed equal to sensor-clock seconds. The full-video audit is preserved, including its 92 test exclusions for unsupported tails. Before any Handover model score, an explicit common-support amendment froze the intersection of camera/raw-wrench support for every class/robot. Sixteen source-clock bin-center frames and sensor statistics use that same common recorded window. Maximum nearest timing gap remains 0.1 s; two training trials fail it. All 151 official test trials are retained. No action or outcome annotation chooses frames.')
    width=len(config['sensor_channels'])*6
    excluded=pd.read_csv(root/'02_labels_and_alignment/excluded_examples.csv',keep_default_na=False)
    exclusions=excluded.exclusion_reasons.value_counts().rename_axis('combined_technical_exclusion_reason').reset_index(name='native_examples')
    counts=manifest.groupby(['machine','native_label']).size().reset_index(name='eligible_examples') if is_msm else manifest.groupby(['official_split','target']).size().reset_index(name='eligible_examples')
    inventory=pd.read_csv(root/'02_labels_and_alignment/original_label_inventory.csv',keep_default_na=False)
    cohort=f'Native verified labels: **{len(inventory)}**. Eligible visual-plus-sensor examples: **{len(manifest)}**. Excluded: **{len(excluded)}**; all exclusions retain the original native label.\n\n'+table(counts)+'\n\nThe following rows partition the excluded native units by their complete combination of failure reasons (no double counting):\n\n'+table(exclusions)
    sensor=f"The allowed channels are `{', '.join(config['sensor_channels'])}`. Channel-major statistics are mean, population std (ddof 0), RMS, minimum, maximum and peak-to-peak: **{width} values** per native example. No label, tool ID, program, direction, folder, robot, task or participant metadata enters the main predictors. Training-only means/standard deviations are fitted separately for every inner and final fit."
    if not is_msm:sensor+=' Gripper/joint configurations differ between robots and are not fabricated into a shared joint vector. HSR wrench is measured; Gen3 wrench is estimated from joint torque. Fourteen trials have all-six-channel zero traces; they are retained as native, timestamp-valid observations and flagged as uninformative, not silently relabeled or “repaired”.'
    text(canonical/'09_final_reports/DATASET_OVERVIEW.md',f'# {dataset} dataset overview\n\n{why}\n\n{scope}\n\n{raw}\n\n{labels}\n\nOfficial source: [{doi}]({source}).\n')
    text(canonical/'09_final_reports/DATASET_VALIDATION.md',f'# {dataset} input validation\n\n{cohort}\n\n{alignment}\n\n{sensor}\n\nOne prediction is one native cutting interval or completed trial. It is retrospective classification, not early warning. Technical decoding/alignment is distinct from optical anomaly observability. Native labels, raw data and all prior results remain unchanged.\n\nThe machine-readable validation gate and exclusion inventory are under `{root}/02_labels_and_alignment/`.\n')
    text(root/'03_processed_model_inputs/data_contract.md',f'# {dataset} input/output contract\n\n16 ordered, distinct native RGB frames → aspect-preserving SAR-corrected 640×640 black letterbox, divide by 255, no ImageNet normalization → frozen ResNet CNN only → last three spatial-map means concatenate to 896 values per frame → mean over 16 frames → one 896-value vector. Source native frame indices, actual PTS and source-clock associations are retained.\n\n{sensor}\n\nOutputs: one abnormal/failure probability per original native example, with source label, split/fit identity and checkpoint hash. Image overlays/qualitative crops are never CNN training inputs.\n')
    architecture=f'''# {dataset} architecture implementation

The actual canonical constructors are reused: `reassemble.section1_features.load_visual`, `reassemble.section1_models.VisualHead`, the verified `msm.models` composition, `msm.splits` group checks, and `reassemble.section2_models.DecisionGate`. There is no copied detector/model framework. P is the hash-verified PekingU/rtdetr_r18vd revision ac77a11ff0170a41b771c03264987f8ce2b0d753. Only its 11,190,112-parameter CNN executes; transformer encoder, decoder, boxes and detector heads are excluded.

The 16-frame pooled CNN representation is 896-dimensional. A new head is Linear(896,128), ReLU, dropout 0.1, Linear(128,1): 114,945 trainable parameters. Training-only standardization precedes it. The frozen CNN has no optimizer or gradients. The numerical branch uses the dataset-specific {width}-value statistics vector, training-only standardization and newly fitted balanced L2 logistic regression (C1, lbfgs, max_iter2000). This is the verified statistical-sensor adaptation, not a claim to reproduce REASSEMBLE's original raw-sequence PatchTST sensor branch unchanged.

Original F2 is newly fitted unweighted L2 logistic late fusion on [p_visual,p_sensor], C1. Only group-OOF branch probabilities enter its fit. Source failure heads, normalizers and fusion coefficients are never transferred. The averaging control has no fitted fusion parameter.

QG_clean/QG_aug reuse the actual quality-only DecisionGate with hidden width 16 and softmax allocation over branch logits. The new dataset context contains six label-free visual-quality values, per-channel log1p(std), explicit missing-channel fractions and two availability flags. No action/direction/group IDs enter it. These are explicitly named external-dataset quality adapters, not the original F2 method or automatically a proven robust model. QG_clean sees clean OOF views; QG_aug sees clean plus seven lowest-severity OOF corruption views under a fixed exposure budget. F2_aug is the exposure-matched static logistic control. Each native row has total static augmentation weight one; each gate epoch samples one view per native example. Their performance must be compared with clean F2 and unimodal/fallback controls.

The original pretrained CNN and a completed REASSEMBLE-trained CNN are separate conditions. R is admissible only from canonical C_full_finetuned16, source seed42, outer0, outer_assessment, job4, with completed selection receipt and stable checkpoint hashes. Missing R never blocks P. Both conditions, if present, use a newly trained identical head and the same frozen-backbone rules.
'''
    text(canonical/'09_final_reports/MODEL_IMPLEMENTATION.md',architecture)
    text(root/'04_experiment_protocol/architecture_description.md',architecture)
    baselines='''# Predeclared baselines and training

Prevalence/majority: constant training positive prevalence, threshold 0.5. Sensor logistic: balanced L2 C1, lbfgs, 2000 iterations, training-only standardization. Strong sensor control: HistGradientBoosting, 100 iterations, learning rate0.1, max15 leaves, min10 leaf rows, L2=1, no early stopping, training-only balanced sample weights. Vision: the new frozen-CNN head, AdamW lr0.001/wd0.001, 10 fixed epochs, batch32, weighted BCE from training prevalence, gradient norm clip1, FP32. All use seeds42,123,20261023; existing MSM composition derives OOF seed=nominal+k and final refit seed=nominal+99. No search, early stopping, calibration or assessment-selected threshold.

Averaging and original F2 use the same visual/logistic-sensor branches. QG_clean/QG_aug use 40 fixed epochs, AdamW lr0.003/wd0.001, batch128 and clip1. F2_aug controls for its extra corruption exposure. No single-frame ablation was added. In-sample training scores are marked diagnostic and computed after fitting; they never fit F2. Saved OOF provenance proves exclusion of every row's group from each base fit.
'''
    text(root/'04_experiment_protocol/baseline_definitions.md',baselines)
    split=('Primary: the frozen three-outer/two-inner StratifiedGroupKFold protocol, outer seed42 and inner seed142+outer index, keeping all machine/experiment folders together. Predeclared sensitivities repeat all models/seeds for machine/reference-date and calendar-date grouping, and for label-2 exclusion. No fold-count weakening or seed search. All fit/OOF/assessment partitions require both classes and exact coverage. There are 45 nominal groups, 17 positive groups, seven machine/date proxies and five calendar dates. Dates are stricter proxies, not proven independent physical tools/workpieces; repeated NC content and tool/material descriptions remain limitations.' if is_msm else
        'Use the original official participant-based train/validation/test archives. Native counts337/101/151 become eligible335/101/151 under the pre-score common-support gate. Train only on the335 eligible training trials. Fixed validation is reported separately and never selects epochs/thresholds; it is not merged into training or test. No native participant IDs or mapping is supplied, so identity-level disjointness cannot be independently verified. Participant-OOF F2/F2_aug/QG_clean/QG_aug are BLOCKED, not replaced by trial-OOF or validation-set stacking. The five independently interpretable official-split baselines continue. No participant CI is fabricated from trial resampling.')
    text(root/'04_experiment_protocol/split_protocol.md','# Split and leakage protections\n\n'+split+'\n\nAll normalization, noise scales and imputations use only the relevant fit partition. Duplicate source video across official partitions is forbidden. No class-dependent frame selection, test-aware source checkpoint selection, target metadata features or in-sample F2 fit is allowed.\n')
    definitions=json.loads((root/'03_processed_model_inputs/split_manifests/frozen_splits.json').read_text());split_rows=[]
    lookup=manifest.set_index('sample_id')
    for protocol,definition in definitions.items():
        metadata=lookup.loc[definition['sample_ids']]
        def describe(indices):
            g=metadata.iloc[np.asarray(indices,int)]
            return {'examples':len(g),'positive':int(g.target.sum()),'groups':int(g[definition['grouping']].nunique()) if is_msm else None}
        for k,fold in enumerate(definition['plan']):
            partitions={'outer_train':fold['train'],'outer_test':fold['test']}
            if 'validation' in fold:partitions['official_validation']=fold['validation']
            for j,(fit,validation) in enumerate(fold.get('inner') or []):
                partitions[f'inner{j}_fit']=fit;partitions[f'inner{j}_OOF_validation']=validation
            for role,indices in partitions.items():split_rows.append({'protocol':protocol,'outer_fold':k,'role':role,
                'group_identity':definition['grouping'] if is_msm else 'participant identity unavailable; no trial proxy',**describe(indices)})
    pd.DataFrame(split_rows).to_csv(root/'04_experiment_protocol/group_split_inventory.csv',index=False)
    return architecture


def run(root):
    root=Path(root);config=json.loads((root/'04_experiment_protocol/experiment_config.json').read_text());dataset=config['dataset'];canonical=Path(dataset)
    from external_eval.publication import prepare
    prepare(root)
    done=canonical/'09_final_reports/REPORTS_COMPLETE.json'
    if done.exists():
        for p,h in json.loads(done.read_text())['hashes'].items():
            if sha(p)!=h:raise ValueError('Final report changed')
        print('REUSED final reports',dataset,flush=True);return
    predictions,pooled,summary,cases=summarize(root)
    from external_eval.validate_results import audit as validate_results
    validation=validate_results(root,predictions,cases)
    primary='primary__group_id' if dataset=='MSM' else 'official'
    main=summary[summary.protocol==primary]
    clean=pooled[(pooled.protocol==primary)&(pooled.role=='test')&(pooled.corruption=='clean')]
    manifest=pd.read_csv(root/'03_processed_model_inputs/final_sample_manifest.csv',keep_default_na=False)
    gate=json.loads((root/'02_labels_and_alignment/validation_gate.json').read_text())
    methods(root,canonical,config,gate,manifest)
    cohort_figures(root,manifest,dataset)
    paths=figures(root,predictions,primary)+robustness_figures(root,pooled,primary)
    training_curves(root,cases,primary)
    comparisons=pd.read_csv(root/'06_evaluation_results/metrics/paired_seed_differences.csv')
    pairs=comparisons[comparisons.protocol==primary]
    pair_summary=pairs.groupby(['initialization','comparison']).AP_difference.agg(['mean','min','max']).reset_index()
    fullmetrics=clean[['initialization','seed','model','AP','AUROC','F1','precision','recall','specificity','balanced_accuracy','Brier','log_loss','prevalence','TN','FP','FN','TP']]
    statuses='PASS' if dataset=='MSM' else 'PARTIAL'
    if dataset=='MSM':
        uncertainty=pd.read_csv(root/'06_evaluation_results/metrics/paired_group_bootstrap_95ci.csv')
        u=uncertainty[(uncertainty.protocol==primary)&(uncertainty.grouping=='calendar_date_group')&uncertainty.comparison.str.contains('F2 minus')]
        uncertainty_text='Paired cluster bootstrap (2,000 replicates) resamples complete groups with the same draws for all models/seeds. It is conditional on the fixed fitted models and split assignments; no bootstrap refitting was performed. Seeds are averaged descriptively, not treated as independent data. Both nominal-folder and calendar-date-proxy intervals are provided. Only five dates support the stricter interval; unknown tool/workpiece reuse across dates can still invalidate physical independence.\n\n'+table(u)
        confounds='Direction contingency and direction-only held-out baseline are reported separately. Direction is excluded from all main predictors. Both directions have support for the frozen primary grouped design. DOWN-only label-2-excluded training fails the fixed class-support split gate; no seed search or fold reduction was performed. Within-direction held-out subgroup metrics are descriptive, not a causal direction intervention.'
    else:
        uncertainty_text='Participant-level uncertainty is unavailable because the official release has no participant-to-trial mapping. No trial-based pseudo-independent CI is substituted. All three seed results and their descriptive range/std are reported. Official subject-based splitting is the publisher claim; it is not independently identity-verified.'
        confounds='F2, F2_aug, QG_clean and QG_aug are SKIPPED: participant-disjoint OOF probabilities cannot be certified without participant IDs. No in-sample probability stack or trial-group substitute was used. Robot and task differ in force estimation, camera view and class prevalence; see subgroup tables. The common-support amendment retains all151 official test trials; it is not a test-score-selected cohort.'
    # Subgroups use already frozen held-out predictions; they cannot select the final model.
    main_predictions=predictions[(predictions.protocol==primary)&(predictions.role=='test')&(predictions.corruption=='clean')]
    metadata=manifest.set_index('sample_id');subgroups=[]
    group_columns=['machine','direction','native_label'] if dataset=='MSM' else ['robot','task']
    from external_eval.evaluate import metrics as calculate
    for column in group_columns:
        for key,g in main_predictions.groupby(['initialization','seed','model']):
            values=metadata.loc[g.sample_id,column].to_numpy()
            for value in np.unique(values):
                selected=g.iloc[np.flatnonzero(values==value)]
                subgroups.append({'initialization':key[0],'seed':key[1],'model':key[2],'subgroup_type':column,'subgroup':value,
                    **calculate(selected.target,selected.probability)})
    pd.DataFrame(subgroups).to_csv(root/'06_evaluation_results/metrics/heldout_subgroup_metrics.csv',index=False)
    train_rows=[]
    for case in cases:
        p=Path(case['predictions']).parent/'TRAINING_ONLY_DIAGNOSTICS.json';d=json.loads(p.read_text())
        for name,value in d['in_sample_base_prediction_metrics'].items():
            train_rows.append({'initialization':case['initialization'],'protocol':case['protocol'],'seed':case['seed'],'fold':case['fold'],
                'model':name,'training_in_sample_AP':value['AP']})
    pd.DataFrame(train_rows).to_csv(root/'06_evaluation_results/metrics/training_diagnostic_AP.csv',index=False)
    overfit=pd.DataFrame(train_rows);overfit=overfit[(overfit.protocol==primary)&overfit.model.isin(['visual','sensor_logistic','sensor_histgradient'])]
    gap=overfit.groupby(['initialization','model']).training_in_sample_AP.mean().reset_index().merge(main[['initialization','model','AP_mean']],on=['initialization','model'])
    gap['train_minus_heldout_AP']=gap.training_in_sample_AP-gap.AP_mean
    text(canonical/'09_final_reports/EXPERIMENT_RESULTS.md',f'''# {dataset} independent evaluation results

**Status: {statuses}.** These are measured held-out results, not smoke-test metrics. Primary average precision is pooled over the independent outer tests (MSM) or the eligible official test split (Handover), calculated separately for every seed. Fixed threshold0.5 is used for classification metrics. AP is scikit-learn average precision, not trapezoidal PR area or the F-beta=2 score. F2 is the logistic-fusion model name.

## Complete three-seed comparison

{table(main)}
Standard deviations describe three head-training seeds, not three independent datasets. Deterministic classical models may be identical across seeds. P is original pretrained CNN initialization; any R rows use only the exact completed canonical source. No best seed/fold was selected.

## Paired within-dataset AP differences

{table(pair_summary)}
F2 is compared with its actual logistic-sensor component, vision, averaging and the stronger sensor control. An improvement over the logistic component alone does not establish superiority over the stronger numerical baseline. QG_aug has extra predefined corruption-training exposure; compare it with F2_aug as well as clean F2. Original F2 remains the clean-OOF model.

## Uncertainty and independence

{uncertainty_text}

## All per-seed held-out metrics

{table(fullmetrics)}
Per-fold metrics and all sensitivity protocols are in `{root}/06_evaluation_results/metrics/`; every prediction carries its native sample ID, split role, fit/case ID, model, seed and corruption. `metric_reproduction.json` verifies that all saved fold metrics match prediction artifacts within1e-12.

## Overfitting diagnostic

{table(gap)}
These in-sample scores were computed after model fitting and never entered F2. A train/held-out gap is consistent with overfitting and/or operating-condition/domain shift; it does not isolate the cause. Ten fixed head epochs and40 fixed gate epochs were used, with no assessment-selected stopping. Every loss curve and completed checkpoint is preserved.

## Data-specific limits

{confounds}

Technical frame/sensor eligibility does not prove that an anomaly is optically visible. Mean pooling also does not model frame order. The tasks are retrospective interval/trial classification, not online failure prediction, damage localization or early warning. Dataset/task prevalence and observation horizon differ from REASSEMBLE, so absolute cross-dataset AP cannot establish general superiority.
''')
    robust=pd.read_csv(root/'07_robustness_experiments/robustness_metrics.csv')
    r=robust[(robust.protocol==primary)&(robust.role=='test')]
    agg=r.groupby(['initialization','model','corruption'])[['AP','absolute_AP_degradation','relative_AP_degradation_percent']].mean().reset_index()
    text(canonical/'09_final_reports/ROBUSTNESS_RESULTS.md',f'''# {dataset} modality robustness

All corruptions/severities were fixed before inspecting held-out effects. RGB Gaussian blur (sigma1/2/4), brightness/contrast (0.8/0.5/0.2), centered content occlusion (10/25/40%) were applied to real image pixels and passed through the actual frozen CNN. They are not embedding noise proxies. Frame dropout omits4/8/12 real frames and pools the remaining cached frame embeddings, mathematically exact for this frozen independent-frame CNN and mean pool.

Gaussian measurement noise (0.1/0.5/1× pooled raw training channel SD), zeroed channels and explicitly missing channels (10/30/50%) act on the corresponding sensor observations/statistics. Statistics are recomputed for noise/zeroed channels. Missing-channel statistics use only clean training feature means, with explicit masks for the gate; no scaler is refitted on corrupted test data. Randomness is stable per sample/type and shared across models, seeds and P/R. Labels, groups and split roles do not change.

## All measured scenarios, means of the three seeds

{table(agg)}
Degradation is clean AP minus corrupted AP; negative values mean measured improvement. Relative degradation divides by clean AP. Individual seed values and all grouping/label sensitivities are preserved in the CSV, not selected by the heatmap.

For completely missing vision/sensors, the unavailable unimodal model is marked UNAVAILABLE_MODALITY. Averaging, F2 and quality gates use the separately identified deterministic surviving-branch fallback. F2 never receives an invented missing-branch prediction. Equal fallback performance is imposed behavior, not proof that a learned gate discovered robustness. Compare every corruption with the appropriate unaffected/surviving unimodal baseline, not only the clean fused score.

QG_clean and QG_aug are explicitly distinct from logistic F2. QG_aug/F2_aug saw the same seven lowest-severity OOF corruptions at fixed weight/exposure; higher severities are assessment only. Any advantage of augmentation is not automatically a quality-gating advantage. These experiments establish only behavior under the named synthetic corruptions and native data-quality limitations, not robustness to arbitrary real hardware faults, unseen robots/machines or all forms of missing data.

Brightness, image variance and sensor standard deviation are quality proxies that can also encode scene/process context. Gate weights are not causal explanations or independently verified reliability estimates. The saved quality_gate_allocations.csv records the actual held-out allocation summaries where gates were permitted.

{confounds}
''')
    # Cost records separate CNN extraction (shared once) from lightweight fitting.
    costs=[]
    for condition in sorted(predictions.initialization.unique()):
        folder=root/'03_processed_model_inputs/visual_features'/condition
        cost=json.loads((folder/'complete.json').read_text())
        if (folder/'cache_index.json').exists():
            decoding=[];forwarding=[]
            for item in json.loads((folder/'cache_index.json').read_text()):
                with np.load(item['path'],allow_pickle=False) as z:
                    decoding.append(float(z['decode_seconds']));forwarding.append(float(z['forward_seconds']))
            cost.update(total_native_decode_seconds=sum(decoding),total_synchronised_GPU_forward_seconds=sum(forwarding),
                cached_image_forward_count=len(forwarding)*160,
                aggregate_frames_per_s_synchronised=len(forwarding)*160/sum(forwarding),
                extraction_frames_per_s_this_invocation=cost['frames_forwarded_this_invocation']/cost['wall_seconds_this_invocation'])
        costs.append({'initialization':condition,**cost})
    fit_times=[];inference_times=[];allocations=[]
    for case in cases:
        record=json.loads((Path(case['predictions']).parent/'training_and_runtime.json').read_text())
        fit_times.extend({'case_id':case['case_id'],'role':fit['role'],'joint_visual_sensor_HGB_fit_seconds':fit['wall_seconds']} for fit in record['base_fits'])
        inference_times.extend({'case_id':case['case_id'],**value} for value in record['inference'])
        allocations.extend({'case_id':case['case_id'],'initialization':case['initialization'],'protocol':case['protocol'],'seed':case['seed'],'fold':case['fold'],**value} for value in record.get('quality_gate_allocation',[]))
    pd.DataFrame(fit_times).to_csv(root/'06_evaluation_results/metrics/base_fit_costs.csv',index=False)
    pd.DataFrame(inference_times).to_csv(root/'06_evaluation_results/metrics/cached_classifier_inference_costs.csv',index=False)
    if allocations:pd.DataFrame(allocations).to_csv(root/'07_robustness_experiments/quality_gate_allocations.csv',index=False)
    write_json(root/'06_evaluation_results/runtime_summary.json',{'CNN_extraction':costs,'case_wall_seconds_total':sum(c['wall_seconds'] for c in cases),
        'case_count':len(cases),'CNN_cache_reused_across_all_fits_seeds_groups':True,'shared_gpu_device_utilization_not_attributed_to_this_job':True})
    text(canonical/'09_final_reports/REPRODUCIBILITY.md',f'''# {dataset} reproducibility and validation

Run from repository root using the existing environment:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \\
PYTHONPATH='src:MSM/99_preserved_previous_work/MILLING_DATASET/source:CROSS_DATASET_COMPARISON/src' \\
ma_thesis_env/bin/python -B -m external_eval.run_all
```

The runner reuses immutable raw inputs, resumes per-example CNN caches and completed fits/cases, then automatically evaluates all fixed seeds and robustness scenarios. No additional GO is needed. Model-specific blockers do not silently replace a method. The active dataset root for this delivery is `{root}`. Handover's earlier full-video audit and its later common-support amendment remain separate preserved evidence.

Pinned configs/splits are under04_experiment_protocol and03_processed_model_inputs/split_manifests. Native sources/hashes, cache identities, source/model/config hashes, actual derived fit seeds, OOF group provenance, CPU/GPU times, FP32 parity check and checkpoint reload checks are preserved. The actual CNN cache reproduction maximum difference is0.0 on an outer-training-only example; no gradient flows through the frozen CNN. The new synthetic regression suite tests full outer composition, atomic integrity, labels, timestamps, dropout, OOF isolation, training gradients, exact reload, metrics and missing-modality semantics. Existing MSM tests are retained.

All reported fold metrics were independently recalculated from saved predictions. That checks saved-result consistency, not a separate rerun of every stochastic model. The full actual feature extraction and model matrix were executed here; raw-label/sensor/frame admission was also reproduced. Group bootstrap assumptions and unavailable Handover participant mapping remain explicit. No historical source dataset, PHM/Intel raw data or active REASSEMBLE experiment was modified; no staging/commit occurred.

The independent implementation_validation.json audit checks every planned case, native label/assessment identity, head-update budget, derived seed, checkpoint hash and exact reload receipt. On MSM it also refits the same fixed F2 estimator from saved clean OOF probabilities and checks its coefficients; it never uses assessment rows. A transient controller feature-polling race was corrected and regression-tested; the identical frozen MSM evaluator completed directly. Its correction receipt and original controller record remain preserved, with any resolved operational blocker documented separately from scientific gates.

Training is CPU FP32 for the small new heads/classifiers; real-image frozen CNN extraction uses the shared T4. The process memory cap is2GiB, measured peak tensor allocation about433MiB. Device-wide100% utilization belongs to the shared workload and is not an MSM/Handover utilization result. CNN caches store compact per-frame embeddings for clean plus real-image corruptions; no huge duplicated640×640 frame cache is retained. Runtime details: `{root}/06_evaluation_results/runtime_summary.json`.
''')
    source_R=Path('CROSS_DATASET_COMPARISON/provenance/R_source_gate_final.json')
    r_available=json.loads(source_R.read_text())['R_available'] if source_R.exists() else False
    measured=[]
    for initialization,g in pairs.groupby('initialization'):
        for comparison in (['F2 minus visual','F2 minus sensor_logistic','F2 minus sensor_histgradient','F2 minus averaging','QG_aug minus F2_aug'] if dataset=='MSM' else ['averaging minus visual','averaging minus sensor_logistic','averaging minus sensor_histgradient']):
            a=g.loc[g.comparison==comparison,'AP_difference'].to_numpy(float)
            if len(a):measured.append(f'{initialization}, {comparison}: mean {a.mean():+.6f} AP, seed range [{a.min():+.6f}, {a.max():+.6f}]. The sign is '+('positive in all seeds.' if np.all(a>0) else 'negative in all seeds.' if np.all(a<0) else 'mixed or zero across seeds.'))
    measured_text='\n\n'.join(measured)
    conclusion=f'''# {dataset} research conclusions

{measured_text}

The implementation reuses the verified CNN/head and late-fusion primitives with a dataset-specific annotation/sensor adapter and freshly fitted classifiers. This establishes software portability. Predictive value is the measured held-out within-dataset difference in EXPERIMENT_RESULTS.md, not the fact that code ran. Fusion can be weaker than a unimodal or stronger classical sensor model; the complete seed/condition tables preserve such outcomes.

The canonical REASSEMBLE full-backbone source was {'available and separately evaluated as R' if r_available else 'unavailable at the completed-receipt gate, so learned-weight transfer is NOT evaluated'}. P means original generic pretrained CNN weights, not a REASSEMBLE-trained CNN. New dataset heads/scalers/F2 coefficients are not reused source-domain parameters. No zero-shot or no-retraining claim is made.

{confounds}

Only the listed synthetic corruption/fallback experiments support robustness statements. All three seed results are retained; seeds do not replace independent physical experiments or participants. Unknown tool/workpiece reuse, five-date support (MSM), unprovided participant identities (Handover), camera occlusion, sensor estimation/holding and retrospective observation horizons constrain inference. These limitations remain even if AP is high.
'''
    text(canonical/'09_final_reports/RESEARCH_CONCLUSIONS.md',conclusion)
    handoff=f'''# {dataset} review handoff

**{statuses}.** Active measured evaluation: `{root}`. Main comparison uses all three fixed seeds; no best seed/fold, source checkpoint or threshold was selected using test scores.

{table(main)}
{confounds}

Read [EXPERIMENT_RESULTS.md](EXPERIMENT_RESULTS.md), [ROBUSTNESS_RESULTS.md](ROBUSTNESS_RESULTS.md), [DATASET_VALIDATION.md](DATASET_VALIDATION.md), [MODEL_IMPLEMENTATION.md](MODEL_IMPLEMENTATION.md) and [REPRODUCIBILITY.md](REPRODUCIBILITY.md). Source-native prediction tables, all per-fold/per-seed metrics and completed checkpoints are preserved in their separate dataset stages. No full-model efficacy is inferred from earlier smoke tests; prior blocked findings remain historical prerequisites, not negative model scores.
'''
    text(canonical/'09_final_reports/REVIEW_HANDOFF.md',handoff)
    # These README files were this task's unsealed preparation placeholders, not
    # historical evidence. Preserve the exact preimage before finalizing them.
    readme=canonical/'README.md';before=readme.read_text()
    preimage=canonical/'09_final_reports/README_preparation_preimage.json'
    if not preimage.exists():write_json(preimage,{'text':before,'sha256':sha(readme)})
    gallery=os.path.relpath(root/'08_visual_examples_and_eda/prediction_examples/index.html',canonical)
    readme.write_text(f'# {dataset} external evaluation\n\n**{statuses}.** Full permitted P-based models, all three seeds and predeclared robustness have completed.\n\n- [Results](09_final_reports/EXPERIMENT_RESULTS.md)\n- [Robustness](09_final_reports/ROBUSTNESS_RESULTS.md)\n- [Input validation](09_final_reports/DATASET_VALIDATION.md)\n- [Reproduction](09_final_reports/REPRODUCIBILITY.md)\n- [Real 16-frame examination gallery]({gallery})\n- [Review handoff](09_final_reports/REVIEW_HANDOFF.md)\n\nActive scientific outputs: `{root}`. Native labels, prior stages and raw data remain preserved.\n\n'+confounds+'\n')
    from external_eval.qualitative import make_examples
    make_examples(root,predictions,primary)
    files=[p for p in (canonical/'09_final_reports').rglob('*') if p.is_file()]
    write_json(done,{'dataset':dataset,'status':statuses,'active_root':str(root),'examples':len(manifest),
        'seeds':config['seeds'],'primary_models':sorted(m for m in clean.model.unique() if not m.endswith('DIAGNOSTIC')),
        'diagnostic_models':sorted(m for m in clean.model.unique() if m.endswith('DIAGNOSTIC')),'cases':len(cases),
        'hashes':{str(p):sha(p) for p in files},'completed_utc':utc()})
    print('REPORTS COMPLETE',dataset,statuses,flush=True)
