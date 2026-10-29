"""Versioned evidence reports; every numerical claim comes from saved predictions."""
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
import os
import numpy as np

from .common import PROJECT,REPO,config,read,sha,utc,write
from .metrics import metrics,paired_task_bootstrap

TITLES=['01_EXECUTIVE_SUMMARY','02_DATASET_AND_LABEL_VERIFICATION','03_DATA_PREPROCESSING',
        '04_ARCHITECTURE_EXPLANATION','05_TRAINING_AND_CHECKPOINTS','06_UNIMODAL_BASELINE_RESULTS',
        '07_FUSION_RESULTS','08_ROBUSTNESS_EVALUATION','09_STATISTICAL_COMPARISON','10_INDEPENDENT_VERIFICATION',
        '11_LIMITATIONS_AND_THREATS_TO_VALIDITY','12_FINAL_SCIENTIFIC_CONCLUSION','13_RESEARCHER_HANDOFF']


def result_tables(c):
    eligible=PROJECT/'03_preprocessing/processed_manifests'/c['run_id']/'eligible.json'
    if not eligible.exists():return {},[]
    groups={r['episode_index']:r['canonical_task_id'] for r in read(eligible)};models=defaultdict(list)
    branches={'visual_frozen':'V1','visual_frozen_high_only':'V1_high_only','visual_finetuned100':'V2','reassemble_transfer':'V3'}
    for branch,condition in branches.items():
        for path in sorted((PROJECT/'06_training_experiments'/branch/'runs'/c['run_id']).glob('seed*/outer*_final/predictions.json')):
            if not path.with_name('COMPLETE.json').exists():continue
            for row in read(path):models[condition].append({**row,'canonical_task_id':groups[row['episode_index']],'p':row['probability']})
    for path in sorted((PROJECT/'06_training_experiments/sensor_baselines/runs'/c['run_id']).glob('seed*/outer*_final/predictions.json')):
        if not path.with_name('COMPLETE.json').exists():continue
        for row in read(path):
            for name in ['S3','S2']:models[name].append({**row,'canonical_task_id':groups[row['episode_index']],'p':row[name+'_probability']})
            models['T_prevalence'].append({**row,'canonical_task_id':groups[row['episode_index']],'p':row['training_prevalence_probability']})
    for path in sorted((PROJECT/'06_training_experiments/fusion_experiments/runs'/c['run_id']).glob('*/seed*/outer*/predictions.json')):
        if not path.with_name('COMPLETE.json').exists():continue
        condition=path.parents[2].name
        for row in read(path):
            for name,key in [('F1','F1_average'),('F2','F2_probability'),('Gate','gate_probability'),('Gate_static','gate_static_probability')]:
                models[name+'_'+condition].append({**row,'canonical_task_id':groups[row['episode_index']],'p':row[key]})
    for path in sorted((PROJECT/'06_training_experiments/fusion_experiments/augmentation/runs'/c['run_id']).glob('*/seed*/outer*/predictions.json')):
        if not path.with_name('COMPLETE.json').exists():continue
        condition=path.parents[2].name
        for row in read(path):
            for name,key in [('F2_aug','F2_aug_probability'),('Gate_aug','gate_aug_probability'),('Gate_static_aug','gate_static_aug_probability')]:
                models[name+'_'+condition].append({**row,'canonical_task_id':groups[row['episode_index']],'p':row[key]})
    summaries=[]
    for name,rows in sorted(models.items()):
        for seed in c['seeds']:
            subset=[r for r in rows if r['seed']==seed]
            if not subset:continue
            for fold in ['pooled']+list(range(c['outer_folds'])):
                part=subset if fold=='pooled' else [r for r in subset if r['outer']==fold]
                if not part:continue
                score=metrics(np.asarray([r['label'] for r in part]),np.asarray([r['p'] for r in part]))
                summaries.append({'model':name,'seed':seed,'outer':fold,**{k:v for k,v in score.items() if isinstance(v,(float,int))}})
    return dict(models),summaries


def paired_comparisons(c,models):
    pairs=[('V2','V1'),('V3','V2'),('S2','V2'),('S3','V2'),('V1_high_only','V1')]
    pairs += [(v,'T_prevalence') for v in ['V1','V2','V3','S2','S3']]
    for v in ['V1','V2','V3']:
        pairs += [('F2_'+v,v),('F2_'+v,'S3'),('F2_'+v,'S2'),('Gate_'+v,'F2_'+v),('Gate_'+v,'F1_'+v),('Gate_'+v,'Gate_static_'+v)]
        pairs += [('Gate_aug_'+v,'F2_aug_'+v),('Gate_aug_'+v,'Gate_static_aug_'+v),('Gate_aug_'+v,'Gate_'+v),('F2_aug_'+v,'F2_'+v)]
    pairs += [('F2_V2','F2_V1'),('F2_V3','F2_V2')]
    results=[]
    for a,b in pairs:
        if a not in models or b not in models:continue
        ar={(r['seed'],r['episode_index']):r for r in models[a]};br={(r['seed'],r['episode_index']):r for r in models[b]}
        if ar.keys()!=br.keys():continue
        if len(ar)!=4384*3:
            # Technical QC can reduce cohort; require all3seeds and all3folds.
            if any(len({r['outer'] for r in ar.values() if r['seed']==sd})!=3 for sd in c['seeds']):continue
        ix=sorted(ar);ra=[ar[i] for i in ix];rb=[br[i] for i in ix]
        assert all(x['label']==y['label'] and x['canonical_task_id']==y['canonical_task_id'] for x,y in zip(ra,rb))
        result=paired_task_bootstrap(np.asarray([r['label'] for r in ra]),np.asarray([r['p'] for r in ra]),np.asarray([r['p'] for r in rb]),
                                    np.asarray([r['canonical_task_id'] for r in ra]),np.asarray([r['seed'] for r in ra]))
        results.append({'A':a,'B':b,**result})
    return results


def stress_summary(c):
    """All conditions/folds/seeds, one episode per metric row; no best-seed selection."""
    result=[]
    for condition in ['V1','V2','V3']:
        base=PROJECT/'07_robustness_experiments/combined_corruption/runs'/c['run_id']/condition
        paths=[p for p in sorted(base.glob('seed*/outer*/metrics.json')) if p.with_name('COMPLETE.json').exists()]
        for path in paths:
            seed=int(path.parents[1].name.removeprefix('seed'));outer=int(path.parent.name.removeprefix('outer'))
            for scenario,report in read(path).items():
                for name in ['visual_probability','S3_probability','S2_probability','F1_average','F2_probability','gate_probability','gate_static_probability','F2_aug_probability','gate_aug_probability','gate_static_aug_probability']:
                    if name not in report:continue
                    result.append({'condition':condition,'scenario':scenario,'model':name,'seed':seed,'outer':outer,
                                   'scored':report['scored'],'abstained':report['abstained'],
                                   **{k:v for k,v in report[name].items() if isinstance(v,(float,int))}})
    return result


def stress_comparisons(c):
    from .corruptions import SCENARIOS
    output=[];pooled=[]
    for condition in ['V1','V2','V3']:
        base=PROJECT/'07_robustness_experiments/combined_corruption/runs'/c['run_id']/condition
        paths=[p for p in sorted(base.glob('seed*/outer*/predictions.json')) if p.with_name('COMPLETE.json').exists()]
        if len(paths)!=len(c['seeds'])*c['outer_folds']:continue
        records=[r for path in paths for r in read(path)]
        for scenario in SCENARIOS:
            part=[r for r in records if r['scenario']==scenario['name'] and r['status']=='PREDICTED']
            if not part:continue  # Both missing: no unsupported AP for abstentions.
            y=np.asarray([r['label'] for r in part]);g=np.asarray([r['canonical_task_id'] for r in part]);s=np.asarray([r['seed'] for r in part])
            for sd in c['seeds']:
                selected=[r for r in part if r['seed']==sd];ys=np.asarray([r['label'] for r in selected])
                for key in ['visual_probability','S3_probability','S2_probability','F1_average','F2_probability','gate_probability','gate_static_probability','F2_aug_probability','gate_aug_probability','gate_static_aug_probability']:
                    if key not in selected[0]:continue
                    report=metrics(ys,np.asarray([r[key] for r in selected]))
                    pooled.append({'condition':condition,'scenario':scenario['name'],'model':key,'seed':sd,
                                   **{k:report[k] for k in ['episodes','positive_prevalence','AP_failure','AP_success','macro_AP','AUROC','Brier','log_loss']}})
            pairs=[('gate_probability',key) for key in ['F2_probability','F1_average','gate_static_probability']]
            pairs += [('gate_aug_probability',key) for key in ['F2_aug_probability','gate_static_aug_probability','gate_probability']]
            for candidate,comparator in pairs:
                if candidate not in part[0] or comparator not in part[0]:continue
                gate=np.asarray([r[candidate] for r in part])
                other=np.asarray([r[comparator] for r in part])
                result=paired_task_bootstrap(y,gate,other,g,s)
                output.append({'condition':condition,'scenario':scenario['name'],'A':candidate,'B':comparator,
                               'hardcoded_surviving_branch_fallback':all(r['hardcoded_surviving_branch_fallback'] for r in part),**result})
        del records
    return output,pooled


def conclusions(c,summaries,comparisons):
    if not comparisons:return 'The required paired held-out comparison is not complete. Q1–Q12 remain unresolved; no source checkpoint or pipeline check substitutes for these results.\n'
    text='| Paired comparison | Macro AP difference | Conditional95%task interval | Interpretation |\n|---|---:|---|---|\n'
    for r in comparisons:
        lo,hi=r['task_bootstrap_95_percentile']
        interpretation='interval includes zero' if lo<=0<=hi else 'A higher within this cohort' if lo>0 else 'A lower within this cohort'
        text+=f'| {r["A"]} minus {r["B"]} | {r["macro_AP_A_minus_B"]:.6f} | [{lo:.6f}, {hi:.6f}] | {interpretation}; exploratory |\n'
    pooled=[r for r in summaries if r['outer']=='pooled']
    text+='\n| Model | Mean across3seeds: AP failure | AP success | Macro AP | Macro AP seed SD |\n|---|---:|---:|---:|---:|\n'
    for model in sorted({r['model'] for r in pooled}):
        rows=[r for r in pooled if r['model']==model]
        if len(rows)!=3:continue
        a=np.mean([r['AP_failure'] for r in rows]);b=np.mean([r['AP_success'] for r in rows]);v=[r['macro_AP'] for r in rows]
        text+=f'| {model} | {a:.6f} | {b:.6f} | {np.mean(v):.6f} | {np.std(v,ddof=1):.6f} |\n'
    text+='''\nQ1 maps to V2−V1; Q2 to V3−V2; Q3 compares both-class AP with its held-out prevalence baseline and macro_AP0.5; Q4 compares S3/S2 with vision; Q5/Q6 require F2 versus S3, S2 and vision separately; Q7 maps to F2_V2−F2_V1; Q8 to F2_V3−F2_V2; Q9 compares Gate with F2 and averaging. Q10/Q11 require the complete visual/sensor stress tables; Q12 considers all seeds/folds and every prespecified stress scenario, rather than choosing a favorable result.

The table reports observed task-cohort differences conditional on these fits. Source transfer, visual-only improvement and fusion improvement are distinct comparisons. Intervals are exploratory, not multiplicity-adjusted and do not establish universality. A positive average can coexist with poor success-class AP or unstable folds; inspect both class APs and every seed before making a thesis claim. Programmed missing-modality fallback is not learned adaptation.\n'''
    return text


def publish(c=None,stage='IN_PROGRESS',error=None,with_uncertainty=False):
    c=c or config();root=PROJECT/'10_final_research_reports';root.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    snapshot=root/'report_snapshots'/c['run_id']/stamp;snapshot.mkdir(parents=True,exist_ok=False)
    def optional(path):return read(path) if path.exists() else None
    qcroot=PROJECT/'02_dataset_verification/video_audit/runs'/c['run_id']
    acquisition=optional(qcroot/'ACQUISITION_COMPLETE.json') or optional(qcroot/'ACQUISITION_PROGRESS.json')
    qc=optional(qcroot/'VIDEO_QC_COMPLETE.json') or optional(qcroot/'VIDEO_QC_PROGRESS.json')
    cohort=optional(PROJECT/'03_preprocessing/processed_manifests'/c['run_id']/'COMPLETE.json')
    native=optional(PROJECT/'02_dataset_verification/label_audit'/c['run_id']/'INDEPENDENT_NATIVE_RECOUNT.json')
    preflight=optional(PROJECT/'05_model_implementations/visual_models'/c['run_id']/'CPU_PREFLIGHT.json')
    models,summaries=result_tables(c);comparisons=paired_comparisons(c,models) if with_uncertainty else []
    write(snapshot/'PER_FOLD_AND_SEED_METRICS.json',summaries);write(snapshot/'PAIRED_TASK_COMPARISONS.json',comparisons)
    stresses=stress_summary(c);write(snapshot/'STRESS_PER_FOLD_AND_SEED_METRICS.json',stresses)
    stress_pairs,stress_pooled=stress_comparisons(c) if with_uncertainty else ([],[])
    write(snapshot/'STRESS_PAIRED_TASK_COMPARISONS.json',stress_pairs)
    write(snapshot/'STRESS_POOLED_PER_SEED_METRICS.json',stress_pooled)
    decision_text=conclusions(c,summaries,comparisons)
    table='| Model | Seed | Outer | Episodes | AP failure | AP success | Macro AP | AUROC |\n|---|---:|---|---:|---:|---:|---:|---:|\n'
    table+=''.join(f'| {r["model"]} | {r["seed"]} | {r["outer"]} | {r["episodes"]} | {r["AP_failure"]:.6f} | {r["AP_success"]:.6f} | {r["macro_AP"]:.6f} | {r["AUROC"]:.6f} |\n' for r in summaries)
    if not summaries:table='No held-out ViFailback predictions have been completed. No performance result exists yet.\n'
    complete_fits={branch:len(list((PROJECT/'06_training_experiments'/branch/'runs'/c['run_id']).glob('seed*/*/COMPLETE.json'))) for branch in ['visual_frozen','visual_frozen_high_only','visual_finetuned100','reassemble_transfer','sensor_baselines']}
    progress=f'Acquisition: {acquisition.get("counts") if acquisition else "pending"}. Camera QC: {(qc.get("technical_valid"),qc.get("count",qc.get("done"))) if qc else "pending"}. Final cohort: {cohort.get("eligible") if cohort else "pending complete payload QC"}. Completed fits: {complete_fits}.'
    cohort_text=(f'Final common cohort: **{cohort["eligible"]} episodes**, {cohort["labels"].get("1",0)} failures, {cohort["labels"].get("0",0)} no-failures, {cohort["tasks"]} canonical tasks; {cohort["excluded"]} unique exclusions/quarantines.' if cohort else 'Final common cohort remains pending complete payload QC.')
    shared=f'Run `{c["run_id"]}`. Published {utc()}. Pipeline state: **{stage}**. Immutable report snapshot: `{snapshot.relative_to(REPO)}`.\n\n'
    paths='''Configuration: `VIFAILBACK/configs/experiment.json` and `VIFAILBACK/configs/protocol.json`.
Controller: `VIFAILBACK/scripts/run_pipeline.py`; live status: `VIFAILBACK/logs/20261029T004900Z/PIPELINE_STATUS.json`.
Final cohort: `VIFAILBACK/03_preprocessing/processed_manifests/20261029T004900Z/eligible.json`.
Splits: `VIFAILBACK/04_evaluation_splits/train_validation_test/20261029T004900Z/fit_partitions.json`.
Checkpoints/predictions: `VIFAILBACK/06_training_experiments/{visual_frozen,visual_finetuned100,reassemble_transfer,sensor_baselines,fusion_experiments}/runs/20261029T004900Z/`.
Robustness: `VIFAILBACK/07_robustness_experiments/combined_corruption/runs/20261029T004900Z/`.
Historical unblinding and exclusions remain under `DATASET_RESEARCH/VIFAILBACK_VERIFICATION/FOLLOWUP_REVIEW/20261028T233227Z/`.
'''
    limitation='''Canonical-task independence is tested; session, operator, robot and object-instance independence are not established. The native outcome is an episode failure annotation, not a frame-level fault time or independently scored final mechanical success. The known human-intervention category is excluded; incidental human presence and semantic visibility remain incompletely reviewed. Whole-episode sensors and RGB are retrospective inputs, so these results cannot establish early warning.

Coordinate task55 remains quarantined; no guessed sign transformation or clipping is applied. All converted sensor tables were checked, but original HDF5 comparisons cover only3 anomalous episodes/9 arrays. Position/velocity/gripper-effort fields are measured observations, not calibrated force/torque. Converted25Hz agreement does not establish independent hardware clock synchronization.

The historical20-example visual pilot was selected for observability and balance. Nineteen decided observations agreed with native labels; B02 remains uncertain. It is neither a prevalence sample nor a held-out classifier benchmark. The conservative cohort excludes818 episodes before video QC; exclusions change the estimand and their counts overlap by reason.

Mean pooling is invariant to permutation of retained frames and camera order. Within-episode shifts change sampled content through edge padding; they do not prove tolerance to real hardware clock errors. Quality gating has clean-only training; robustness claims require measured stress-test results. Explicit missing-modality masks and surviving-branch fallback are programmed behavior, not learned reliability recognition. All-both-missing cases abstain. Fixed masks and severities are simulations, not evidence about every deployment failure.

Meta models see smaller-data inner branch predictions than final outer branches. This stacking distribution shift is reported rather than repaired using test outcomes. The fixed three-seed design does not make repeated folds or episodes independent replications. Task bootstrap intervals are conditional on fitted models, do not capture donor selection uncertainty, and multiple comparisons remain exploratory.
'''
    training='''V1 uses frozen original pretrained CNN features and a new896→128→1 head. V2 trains the complete CNN convolution and promoted FrozenBN affine from the original pretrained source. V3 uses the verified REASSEMBLE full-CNN donor, a new head, and the same adaptation recipe as V2. All100 epochs execute; highest validation macro_AP selects the checkpoint, earliest tie. T-only balanced BCE; AdamW head1e-3/backbone1e-5, wd1e-3, clip1, cosine100→0.1initial LR, FP32, effective batch8. FrozenBN moments stay fixed. Full models use exact two-pass frame chunks4 with all48 images.

Each fit saves `BEST_MODEL.pt`, `FINAL_EPOCH100.pt`, `RECOVERY.pt`, `HISTORY.json`, gradient/update evidence, calibrator, predictions, metrics and a hash receipt. Final/recovery are hardlinks to the same immutable payload, saving space. Epoch-boundary recovery stores model/optimizer/scheduler and Python/NumPy/Torch/CUDA RNG; an interrupted epoch replays. Source checkpoint compatibility alone is not a trained target result.

There are12 fit partitions per seed and condition,36 per visual condition,72 full-CNN fits across V2/V3. The live GPU is reserved for the ongoing REASSEMBLE75-fit study. Target GPU runs wait for its verified completion marker and an idle GPU; no GPU-hour cutoff or reduction of100 epochs is applied. This can require a long queue. The CPU preflight is not a GPU throughput estimate.
'''
    reference=f'''Original weights: `{c['pretrained_weights']}/model.safetensors`, SHA256 `fe87a5a30f5daf298d10794c7682a63b6107986f97d6a770ba948d89e4340093`.
Donor: `{c['donor_checkpoint']}`, SHA256 `{c['donor_sha256']}`; selected epoch47,100 executed, seed42. Only115 compatible CNN tensors transfer; source head, normalization buffers, calibrators, fusion coefficients and gates do not transfer. The source's75-fit study is separate and unfinished at initial inspection.
'''
    decisions='''Q1–Q12 require paired saved outer predictions. Until the corresponding matrix completes, fine-tuning improvement, transfer benefit, visual utility, sensor advantage, F2 benefit over each strong unimodal branch, gate benefit, and corruption robustness remain unresolved. A successfully decoded clip, valid gradient, completed script or training loss decrease cannot answer those questions.

When evidence is available, report all seeds/folds and co-primary class APs, compare F2 against S2 as well as S3 and each visual branch, and separate representation portability from learned-weight transfer. Never infer adaptive robustness merely from using an independent dataset. No global superiority, novelty, early-warning or new-robot generalization claim follows from this protocol.
'''
    bodies={
      TITLES[0]:f'{progress}\n\n'+('The experimental matrix is complete; assess the measured tables and paired intervals before making a scientific claim.\n' if stage=='COMPLETE' else 'The investigation is active. No completed-matrix success or superiority claim is warranted.\n')+f'\n{error or ""}\n\nRead02 for data evidence,05 for actual training completion,06–09 for measured results, and13 for resume instructions.\n',
      TITLES[1]:f'''Pinned converted source `{c['repository']}` revision `{c['revision']}`. Original source `sii-rhos-ai/ViFailback-Dataset`, revision `21df46c2585c52e5a62df5f4b946bae6cbc6fed7`.

Native5202 episodes:4545 failure,657 no-failure across100 canonical tasks/109 source directories. Independently rejoined all native records, not README labels. Conservative provisional core4384:3755 failure,629 no-failure,99 tasks;818 unique excluded/quarantined. Final eligible count only exists after complete three-camera QC.

{progress}

Exact native verification: `VIFAILBACK/02_dataset_verification/label_audit/{c['run_id']}/INDEPENDENT_NATIVE_RECOUNT.json`. Every original annotation hash and converted metadata identity is recorded there. Video QC includes source SHA/size, full decoding, count, dimensions, PTS, black frames, blur/repetition flags and selected RGB hashes. Semantic uncertainty is separate from technical validity; weak images are retained. Acquisition failures must be inspected/retried rather than silently called corrupt data.
''',
      TITLES[2]:'''One complete episode is one target, not48 independent labeled frames. Uniform rounded linspace selects16 matching frame indices in each camera, without avoid/correct keyframes or outcome labels. Three views pool equally after the original image processor. No full decoded-image cache is retained; resumable per-frame CNN feature banks retain896float32 values per frame.

Measured sensor channels:14state,12nonplaceholder velocity,2gripper-effort fields. Exact source10statistics/channel produce280 stat-major features. Placeholder constant channels are excluded. Per-episode statistics have no population fitting. Model standardizers fit T only; sigmoid calibration fits disjoint C only. All labels, failure types, native keyframes, source/task IDs, action commands and manual judgments are excluded from ordinary input features. Time is normalized episode progress only for slope.

Runtime contract, feature names, source identities and exclusions are under `03_preprocessing/`. Model comparisons use the identical final technically eligible cohort. Semantically uncertain videos stay flagged and do not get filtered by model correctness.
''',
      TITLES[3]:'''The visual branch executes the RT-DETR-derived ResNet18VD CNN only, not its detection transformer or bounding-box head. Spatial means of128/256/512 feature maps concatenate to896; mean over16times and3cameras produces896; original new-task head896→128 ReLU dropout0.1→1 predicts an episode logit. T-only feature scaling and C-only sigmoid calibration follow the source workflow.

The source framework is imported through `src/vifailback/reference.py`, not copied. ViFailback adapters own label/episode joins, multiview sampling, sensor channels, feature names, groups, fit orchestration and corruption policy. S1=S3 is source-exact balanced C1 logistic plus C calibration. S2 is balanced HGB with200iterations, leaves7/15/31 selected on V; no internal random early stopping.

F1 averages calibrated probabilities. Exact F2 fits unweighted C1 logistic on[visual_probability,S3_probability], using grouped OOF predictions. It is not the F2 classification metric. The original F5-style DecisionGate uses quality and availability only:13→16 ReLU→2softmax weights branch logits. Fixed40epochs and OOF-only scaling; no task/action one-hot. All target heads/calibration/F2/gates fit anew.
\n'''+reference,
      TITLES[4]:training+'\n'+reference+f'\nMeasured disposable CPU preflight: {[(round(t,3)) for t in preflight["step_seconds"]] if preflight else "pending"}seconds/update; all73 CNN/head trainable tensors changed, moments fixed and replay exact when the preflight receipt passes. These updates are not retained as a target classifier or evaluated as evidence.\n\n'+progress,
      TITLES[5]:table+'\nS1=S3 is deterministic given the split; repeating seed labels does not create new independent sensor evidence. Separate class prevalence baselines are essential: constant-probability AP_failure=prevalence, AP_success=success prevalence, macro_AP=0.5.\n',
      TITLES[6]:table+'\nEvery F2/gate fit must trace to inner branch assessment predictions whose task was excluded from T/V/C. Final outer models use the same cohort, seeds and T/V/C partitions. Source-domain F2/gate coefficients are never reused. See per-fit META_TRAINING_PREDICTIONS and hash receipts.\n',
      TITLES[7]:'''Stress tests are fixed in `src/vifailback/corruptions.py`: missing25/50%frames, dropped temporal windows25/50%, blur kernels5/15, square occlusion25/50%area,1/2 cameras unavailable, JPEG20/5, visual shifts10/25%; sensor channels missing25/50%, intervals20/40%, Gaussian noise0.5/1.0 T-channel std, frozen readings, shifts10/25%; combined partial degradation and complete modality loss. Selection/masks never consult labels.

Clean-trained branches, F2 and gate face matched test corruptions. No corruption augmentation was given only to the gate. Raw observations are corrupted before source statistics; missing statistics use T-scaled mean imputation for logistic and native HGB missing-value handling. Input quality is recomputed identically from clean/corrupted selected frames and sensor arrays. Synthetic shifts are within-episode sampling perturbations.

Complete visual/sensor absence invokes the same explicitly programmed surviving-branch fallback for all fusion methods. Missing unimodal scores use a declared T-prevalence reference. Both missing abstains, with coverage reported separately. These fallbacks are not learned robustness. No robustness result exists until the matching saved stress predictions/metric tables complete. Exact outputs live under07_robustness_experiments, never inferred from clean AP.
''',
      TITLES[8]:table+'\nPaired task bootstrap results: `PAIRED_TASK_COMPARISONS.json` in this immutable report snapshot. Resample the same canonical tasks for both methods and every seed; average seed deltas. Do not treat9fold/seed cells as independent. Intervals condition on these fitted models and do not resolve operator/session dependence. Comparisons are exploratory and not multiplicity-adjusted. Report per-fold and pooled-per-seed results rather than only a best fold/seed.\n',
      TITLES[9]:'''Native joins are independently recounted from109 source annotation files; raw SHA identities, converted metadata and V2 labels agree. All original and follow-up artifact manifests were rehashed before preservation. The locked20-example review is unchanged; B02 stays uncertain.

Synthetic checks exercise task disjointness, contamination rejection, exact source statistics/F2, both-class AP and prevalence baselines, 48-image chunked/full-graph gradient parity, availability masks, deterministic corruptions, optimizer/RNG reload and the actual100epoch orchestration. Real-image CPU preflight independently checks executed CNN scopes,73updated tensors, fixed moments and exact replay. Source donor115tensor compatibility is verified separately from adaptation performance.

`src/vifailback/verification.py` rejoins native source records and independently recomputes saved-prediction metrics. Direct AP threshold integration, rank-pair AUROC, confusion-derived precision/recall/F1/accuracy, Brier and logloss formulas are separate from sklearn report calculations. OOF tables are rechecked against exact T/V/C/A IDs. This is automated independent calculation, not a signed second-human review. Final scientific interpretation still merits researcher review.
''',
      TITLES[10]:limitation,
      TITLES[11]:(decisions if stage!='COMPLETE' else '')+'\n'+decision_text+'\n'+table,
      TITLES[12]:progress+'\n\n'+paths+'''\nReproduce/resume using `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 CUBLAS_WORKSPACE_CONFIG=:4096:8 ma_thesis_env/bin/python -B VIFAILBACK/scripts/run_pipeline.py`. It acquires only the declared conservative cohort, waits for full QC, freezes the common manifest/splits, runs CPU baselines/features/frozen heads, then waits for the existing study before GPU full100/fusion/robustness. Failures are recorded and stop the affected stage. Never launch a second controller while its file lock is held. Per-stage commands are available through `scripts/worker.py --help`.

The active report index is versioned on every publication. Prior report bytes remain in report_snapshots. Raw and historical evidence are preserved. Large videos/features/checkpoints remain ignored. Relevant local commits are recorded in `researcher_handoff/GIT_HANDOFF.json`; nothing is pushed. The original3unrelated tracked modifications and unrelated pre-existing untracked trees remain untouched. Final performance and prediction galleries must only be read when their COMPLETE receipts exist.
'''}
    bodies[TITLES[2]]+='\nSecondary camera ablation: V1_high_only retrains the same frozen head on16high-camera frames, using the same primary cohort and task partitions. The camera was fixed before held-out prediction; this is not a fine-tuned single-camera or fusion experiment.\n'
    bodies[TITLES[0]]+='\n'+cohort_text+'\n'
    bodies[TITLES[1]]+='\n'+cohort_text+'\n'
    bodies[TITLES[3]]+='\nQuality attribution includes a separately trained availability-only DecisionGate with identical width/hidden size, seed and budget, but zero quality fields throughout fitting/inference. Supplemental F2_aug/Gate_aug/Gate_static_aug all receive identical clean plus corrupted OOF records. One fixed label-blind corruption per native meta episode comes from blur5, occlusion0.25, channels-missing0.25, noise0.5 or combined-partial. Each record is generated by that episode’s own held-out inner checkpoint/calibrator, with its T-only noise scale. No branch CNN/sensor is retrained for this control. Gate augmentation uses20epochs over2N records, matching40N presentations of the clean40epoch schedule. Repeated corruptions do not increase independent episode/group counts.\n'
    bodies[TITLES[7]]+='\nMatched augmented controls distinguish quality conditioning from merely receiving corruption training: compare Gate_aug with F2_aug and Gate_static_aug. Comparison with clean-trained unimodal models alone cannot attribute an advantage to conditioning. Static F2_aug uses the same C1 source method on the augmented records; augmentation also changes its effective sample count/regularization context. All control choices predate held-out results.\n'
    if stress_pooled:
        grouped=defaultdict(list)
        for r in stress_pooled:grouped[r['condition'],r['scenario'],r['model']].append(r)
        bodies[TITLES[7]]+='\n| Visual condition | Stress | Model | AP failure | AP success | Macro AP | Macro AP seed SD |\n|---|---|---|---:|---:|---:|---:|\n'
        for (condition,scenario,model),values in sorted(grouped.items()):
            if len(values)!=3:continue
            bodies[TITLES[7]]+=f'| {condition} | {scenario} | {model} | {np.mean([r["AP_failure"] for r in values]):.6f} | {np.mean([r["AP_success"] for r in values]):.6f} | {np.mean([r["macro_AP"] for r in values]):.6f} | {np.std([r["macro_AP"] for r in values],ddof=1):.6f} |\n'
        bodies[TITLES[7]]+='\nValues pool each seed’s three outer assessments before averaging the three seed metrics. Both-missing coverage is zero and has no AP. Conditional paired task intervals for every scored stress are in STRESS_PAIRED_TASK_COMPARISONS.json; both class AP differences and macro differences are retained.\n'
    bodies[TITLES[10]]+='\nExact raw trajectory and video-triplet duplicates are screened; near-duplicate executions and semantic overlap between different canonical tasks are not exhaustively resolved. Shared workspaces, robots, objects and unknown sessions can limit effective independence. The donor has one fixed source training seed; three target seeds do not establish donor-seed stability.\n'
    bodies[TITLES[10]]+='\nSome native judgments depend on intended task goals and corrective history, which may not be uniquely observable from16sampled images and episode statistics. The experiment predicts native whole-episode annotations; it does not establish instruction-compliant final success, causal fault localization or early warning.\n'
    previous=optional(root/'LATEST_PUBLICATION.json');identities={}
    for title in TITLES:
        name=title+'.md';target=root/name
        if target.exists():assert previous and sha(target)==previous['reports'][name],'REPORT_WAS_EDITED_EXTERNALLY_PRESERVED'
    for title in TITLES:
        name=title+'.md';content='# '+title.replace('_',' ')+'\n\n'+shared+bodies[title]
        path=snapshot/name;path.write_text(content);identities[name]=sha(path)
        target=root/name
        if target.exists():
            assert previous and sha(target)==previous['reports'][name],'REPORT_WAS_EDITED_EXTERNALLY_PRESERVED'
        temp=target.with_suffix('.writing.md');temp.write_text(content);os.replace(temp,target)
    summary=f'''# ViFailback research completion status

**{stage}.** {error or ''}

{progress}

Verified native5202episodes:4545failure/657no-failure. Provisional conservative4384episodes:3755/629,99tasks;818excluded/quarantined. {cohort_text} Sensor280feature contract, native joins and real48-image CPU gradient/reload checks are available. Pipeline/code validation does not establish fusion benefit.

Three task-disjoint outer folds,3inner OOF folds, seeds42/123/20261023; 100executed epochs for V2/V3. GPU work waits for the ongoing REASSEMBLE75-fit study. There is no shortened epoch schedule. Full training, transfer and robustness questions remain unresolved until their saved artifacts complete.

Read `10_final_research_reports/01_EXECUTIVE_SUMMARY.md`, `05_TRAINING_AND_CHECKPOINTS.md`, `11_LIMITATIONS_AND_THREATS_TO_VALIDITY.md`, and `13_RESEARCHER_HANDOFF.md`. Live stage/PID/errors: `logs/{c['run_id']}/PIPELINE_STATUS.json`; immutable report snapshot: `{snapshot.relative_to(PROJECT)}`.

Scientific status: technically reproducible investigation in progress; no superiority/robustness claim. Native failure is whole-episode, positions/velocities/gripper-effort are not force/torque, hardware clocks and session independence are unverified, task55 remains quarantined, B02 remains uncertain.

Commits are local only; no push or PR. Exact hashes/worktree exclusions: `10_final_research_reports/researcher_handoff/GIT_HANDOFF.json`. Historical evidence and unrelated work remain preserved.
'''
    status=PROJECT/'RESEARCH_COMPLETION_STATUS.md'
    if status.exists():(snapshot/'PREVIOUS_COMPLETION_STATUS.md').write_bytes(status.read_bytes())
    status.write_text(summary)
    auxiliary={str(p.relative_to(REPO)):sha(p) for p in snapshot.glob('*.json')}
    write(root/'LATEST_PUBLICATION.json',{'utc':utc(),'stage':stage,'snapshot':str(snapshot.relative_to(REPO)),
                                         'reports':identities,'auxiliary':auxiliary,'completion_status_sha256':sha(status)})
    return {'snapshot':str(snapshot.relative_to(REPO)),'completed_fits':complete_fits,'models_with_saved_outer_predictions':list(models)}
