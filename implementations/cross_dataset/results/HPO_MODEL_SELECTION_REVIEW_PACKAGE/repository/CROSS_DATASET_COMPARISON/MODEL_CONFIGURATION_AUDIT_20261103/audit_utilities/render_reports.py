"""Render evidence-based audit documents and compact review tables. No model fitting."""
from pathlib import Path
import collections
import datetime as dt
import json
import math
import os
import statistics
from audit_common import OUT,REPO,NR,read,text,evidence,digest,rel,write,csv_write,flush_evidence


def cell(v):
    if isinstance(v,float):return f'{v:.6f}'
    if isinstance(v,(list,dict)):v=json.dumps(v,sort_keys=True)
    return str(v).replace('|','/').replace('\n',' ') if v is not None else 'none'


def table(headers,rows):
    return '| '+' | '.join(headers)+' |\n| '+' | '.join('---' for _ in headers)+' |\n'+''.join('| '+' | '.join(cell(v) for v in row)+' |\n' for row in rows)


def report(name,title,body,sources=()):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
    body=body.replace('unweighted C1 L2 logistic','unweighted C1 logistic (penalty omitted: FRAMEWORK DEFAULT — NOT VERIFIED)')
    content=f'# {title}\n\nAudit date: 2026-11-03. Read-only reconstruction; no new model fitting, feature extraction or experiment changes.\n\n'+body.strip()+'\n'
    if sources:
        content+='\n## Evidence anchors\n\n'
        for s,where in sources:
            source=REPO/s
            if source.exists():
                evidence(source,'report evidence anchor')
                url=os.path.relpath(source,p.parent).replace(' ','%20')
                content+=f'- [{s}]({url}) — {where}.\n'
            else:content+=f'- `{s}` — NOT RECORDED / source unavailable; {where}.\n'
    p.write_text(content)


FAMILIES=[
('F01','All primary','Prevalence constant','Training-side positive prior; no learned neural parameters','CROSS_DATASET_COMPARISON/src/external_eval/evaluate.py','metrics/predictions'),
('F02','REASSEMBLE','Action-only logistic','One-hot action context → balanced logistic','src/reassemble/section1_models.py','logistic_fit/evaluate_model'),
('F03','All primary','Static sensor logistic','Training-only standardization → logistic → optional sigmoid calibration; penalty default unverified where absent','src/reassemble/section1_models.py','Standardizer/logistic_fit'),
('F04','MSM/HANDOVER/VIFAILBACK','Sensor HGB','Histogram gradient-boosted classification trees','VIFAILBACK/src/vifailback/baselines.py','run'),
('F05','All primary','Frozen R18vd mean + MLP','128+256+512 spatial means → temporal/camera mean896 →128 ReLU dropout0.1 →1','src/reassemble/section1_models.py','VisualHead'),
('F06','REASSEMBLE','Last-stage CNN adaptation','Frozen CNN prefix + final stage trainable + visual head','src/reassemble/additional_improvements/finetune.py','FineTunedVisual'),
('F07','REASSEMBLE','Full CNN adaptation','All executed CNN convolutions + promoted FrozenBN affine + fresh head; fixed running moments','26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_source/phase_model.py','full CNN forward / optimizer'),
('F08','REASSEMBLE legacy','CNN + RT-DETR hybrid encoder','CNN → input projections → RTDetrHybridEncoder AIFI/FPN/PAN → pooled head','00_experiments/rt_detr_encoder_comparison/code/features.py','Prefix.forward'),
('F09','REASSEMBLE','Positional temporal Transformer','896→128, sinusoidal time positions, 1 encoder layer/4 heads/FF256, masked mean →1','src/reassemble/additional_improvements/models.py','TemporalHead'),
('F10','REASSEMBLE','Temporal Transformer without positions','Same TemporalHead, positions=False; order ablation','src/reassemble/additional_improvements/models.py','TemporalHead.forward'),
('F11','REASSEMBLE','Boundary-bin visual pooling','Shared 896→128 ReLU dropout0.1; selected frame-bin means concatenated →1','src/reassemble/boundary_visual/models.py','V0–V4'),
('F12','REASSEMBLE','Temporal GRU','896→64 ReLU dropout0.1 + positions → GRU64 → mean →1','src/reassemble/boundary_visual/models.py','V5'),
('F13','REASSEMBLE','PatchTST classification','22 channels×512 progress points, patch32/stride16, d32, 2 layers/4 heads/FF64 →128→1','src/reassemble/section1_models.py','SensorHead'),
('F14','All primary except blocked Handover','F2 probability logistic','sigmoid(b+wV*pV+wS*pS); signed unconstrained constant coefficients','src/reassemble/section1b.py','fit_stacker'),
('F15','All primary','Probability average','(pV+pS)/2; no fitted fusion coefficients','CROSS_DATASET_COMPARISON/src/external_eval/models.py','predictions'),
('F16','REASSEMBLE','Feature concatenation F3','Visual128 and sensor220 separately→128; concat256 LayerNorm→32/64 ReLU dropout→1','src/reassemble/section2_models.py','ConcatHead'),
('F17','REASSEMBLE/MSM/VIFAILBACK','Masked softmax logit gate','Context→hidden ReLU→2; masked softmax; sigmoid(sum alpha*logit(p))','src/reassemble/section2_models.py','DecisionGate'),
('F18','REASSEMBLE','Anchored constant adjustment','Fixed F2 anchor; two learned tanh-bounded coefficient adjustments','src/reassemble/additional_improvements/models.py','AnchoredAdjustment'),
('F19','REASSEMBLE','Anchored adaptive adjustment','Context42→16→2 adjusts fixed F2 coefficients per sample','src/reassemble/additional_improvements/models.py','AnchoredAdjustment.forward'),
('F20','REASSEMBLE legacy','Additive quality logistic','sigmoid(b + w·[pV,pS,z8])','00_experiments/adaptive_fusion_robustness/code/quality_fusion.py','design/fit_all'),
('F21','REASSEMBLE legacy','Interaction quality logistic','sigmoid(b + w·[pV,pS,z8,pV*z8,pS*z8])','00_experiments/adaptive_fusion_robustness/code/quality_fusion.py','design/fit_all'),
('F22','PHM legacy','PatchTST scalar regression','Minute feature channels → PatchTST encoders → scalar damage regression','src/phm2026/models/patchtst/model.py','PatchTSTRegressor'),
('F23','PHM legacy','Ridge regression','Per-normalized-minute feature mean/std/min/max/last → Ridge','src/phm2026/models/patchtst/regression.py','Ridge alpha selection'),
('F24','PHM legacy','RT-DETR scalar regression','Detector-derived image representation → scalar pseudo-damage head','src/phm2026/models/rtdetr/regression.py','regressor forward'),
('F25','PHM legacy','RT-DETR object detection','Ultralytics detector, pseudo-bounding-box target; detection losses','src/phm2026/models/rtdetr/detection.py','detector training'),
('F26','PHM legacy','RT-DETR multitask','Joint detector loss and scalar regression loss','src/phm2026/models/rtdetr/multitask.py','multitask forward'),
('F27','PHM legacy','Latent sensor late fusion','One PatchTST per sensor group; pooled embeddings concatenate → scalar head','src/phm2026/fusion/late_fusion.py','LateFusionRegressor'),
('F28','PHM legacy','Decision sensor late fusion','Per-group PatchTST+scalar head; learned affine combination of scalars','src/phm2026/fusion/modality_fusion.py','DecisionLevelFusion'),
('F29','PHM legacy','Process-aware sensor gate','Per-group embeddings project to32; process-context gate softmax; weighted embedding→scalar head','src/phm2026/fusion/modality_fusion.py','ProcessAwareGatedFusion'),
('F30','PHM legacy evaluation','DINOv2 change scoring','Frozen DINOv2 patch cosine NN to baseline bank; mean/top fractions/max score','scripts/phm2026/results/anomalydino_sweep.py','20 frozen scoring configurations; no gradient fits'),
('F31','PHM legacy diagnostic','Sorted profile constant','Mean ordered training tooth profile; top3 scalar diagnostic','scripts/phm2026/results/verify_target_constants.py','sorted_profiles; no neural fit'),
('F32','REASSEMBLE','Static/temporal sensor hybrid','Static and temporal SENSOR probability combination; no video branch','src/reassemble/additional_improvements/hybrid.py','main')]

SOURCES={
 'original':[('configs/reassemble/section1.json','visual/sensor/logistic_C/selection/calibration'),('src/reassemble/section1_models.py','actual classifier forwards, neural_fit, logistic_fit'),('src/reassemble/section1_features.py','frame pooling and normalized-progress sensor resampling'),('runs/reassemble/20260927T154732Z-section1/training_implementation.json','recorded original implementation revision')],
 'f2':[('src/reassemble/section1b.py','fit_stacker, branch_fit, nested train-side OOF'),('runs/reassemble/20260927T175336Z-section1/assessment/results.json','NOT USED; see canonical section1b path')],
 'msm':[('MSM/04_experiment_protocol/experiment_config.json','fixed P recipe, labels/groups/sensor channels'),('MSM/03_processed_model_inputs/final_sample_manifest.csv','1895 eligible sample IDs/native labels/clock mapping/source hashes'),('MSM/06_evaluation_results/P_EVALUATION_COMPLETE.json','54 completed protocol/fold/seed cases, output hashes'),('CROSS_DATASET_COMPARISON/src/external_eval/evaluate.py','execute_case: train, inner OOF, official validation, held-out scopes'),('CROSS_DATASET_COMPARISON/src/external_eval/models.py','fit_base/fit_fusions/fit_quality/predictions')],
 'handover':[('HANDOVER/experiments/common_support_v2/04_experiment_protocol/experiment_config.json','participant_oof_gate/observation_amendment/validation_use'),('HANDOVER/experiments/common_support_v2/03_processed_model_inputs/final_sample_manifest.csv','587 mapped IDs, native labels, empty participant IDs'),('HANDOVER/experiments/common_support_v2/06_evaluation_results/P_EVALUATION_COMPLETE.json','three seeds complete; fused methods skipped'),('HANDOVER/01_raw_dataset/source_evidence/zenodo_record_10708763.json','official dataset record and metadata')],
 'vi':[('VIFAILBACK/configs/experiment.json','revision, seeds, donor SHA, architecture,100-epoch recipe'),('VIFAILBACK/src/vifailback/splits.py','plans/require_oof task-disjoint roles'),('VIFAILBACK/src/vifailback/training.py','fit checkpoint selection and optimizer'),('VIFAILBACK/src/vifailback/baselines.py','S3 LR and three S2 HGB candidate settings'),('VIFAILBACK/src/vifailback/fusion.py','F2 and quality/availability gates'),('VIFAILBACK/src/vifailback/resources.py','gpu_state75-fit scheduling barrier'),('VIFAILBACK/logs/20261029T004900Z/PIPELINE_STATUS.json','historical waiting state, not process liveness')]
}


def main():
    state=read(OUT/'provenance/FINAL_AUDIT_STATE_04.json');runs=state['runs'];results=state['results'];hist=state['histories']
    checkpoint=read(OUT/'provenance/CHECKPOINT_SUMMARY.json');summary=read(OUT/'provenance/EXTRACTION_SUMMARY.json')
    base='26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability'
    comp=base+'/26102026_bestfit_100epoch_frozen_vs_full_cnn'
    follow='experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison'
    pair=[r for r in runs if r['experiment_id']=='REASSEMBLE_100E_SINGLE_FIT']
    sources100=[(comp+'/26102026_configuration/PHASE1_COMPARISON_CONFIG.json','effective shared100 horizon; head/backbone LR'),(base+'/26102026_source/phase_model.py','all CNN stages, FrozenBN affine promotion; fixed running moments'),(comp+'/26102026_source/compare100_train.py','training100/checkpoint selection/recovery')]+[(r['history_source'],'history/best/executed_epochs, T/V/C/assessment sample identities') for r in pair]
    sourcesfusion=[('runs/reassemble/20260927T175336Z-section1b/assessment/results.json','metrics, paired recording intervals, complementation'),('runs/reassemble/20260927T175336Z-section1b/assessment/stacker_coefficients.json','five fitted F2 coefficient states'),('src/reassemble/section1b.py','fit_stacker; nested calibrated probability inputs'),(follow+'/07_evaluation_results/ALL_MODEL_METRICS.json','M1–M7 common-threshold metrics'),(follow+'/07_evaluation_results/PAIRED_RECORDING_BOOTSTRAP.json','conditional paired recording intervals'),(follow+'/07_evaluation_results/HISTORICAL_COMPARABILITY.json','canonical sensor identities and stacking-bank limitations')]
    # All fit/config rows remain available; human tables group only identical named study/model families.
    groups=collections.defaultdict(list)
    for r in runs:groups[(r['dataset'],r['experiment_id'],r['model'])].append(r)
    experiments=[]
    for (dataset,experiment),rs in itertools_group(runs):
        confs=sorted({r['configuration_source'] for r in rs});entries=sorted({r.get('entry_point',NR) for r in rs})
        experiments.append({'experiment_id':experiment,'dataset':dataset,'model_families':sorted({r['model'] for r in rs}),
            'objective':'native-failure classification and fusion' if dataset!='PHM2026' else 'historical provisional damage/appearance study',
            'entry_points':entries,'configuration_sources':confs,'output_directories':sorted({r['run_id'].split('::')[0] for r in rs}),
            'training_status':'COMPLETE with documented reused states; parent scope may be partial',
            'completed_fit_records':sum(r['training_status']=='COMPLETE' for r in rs),'reused_records':sum(r['training_status']=='REUSED' for r in rs),
            'planned_runs':75 if experiment=='REASSEMBLE_PHASE1_C20' else len(rs),
            'planned_count_basis':'original plan75, approved cap25' if experiment=='REASSEMBLE_PHASE1_C20' else 'reconstructed completed recipe only; earlier interrupted/unlogged attempts NOT RECORDED',
            'checkpoints_referenced':sum((REPO/r.get('checkpoint_path','NOT RETAINED')).is_file() for r in rs),
            'result_record_count':sum(r['dataset']==dataset and r['experiment_id']==experiment for r in results),
            'source_revision':sorted({r.get('source_revision',NR) for r in rs}),
            'execution_date':'source receipts and directory timestamps; per-run original path preserved; missing dates NOT RECORDED'})
    csv_write(OUT/'01_executive_overview/EXPERIMENT_INVENTORY.csv',experiments)
    csv_write(OUT/'02_model_architecture/MODEL_FAMILY_CATALOG.csv',[dict(zip(['family_id','datasets','family','architecture','source_file','source_symbol'],r)) for r in FAMILIES])
    parameter_rows=[]
    seen=set()
    for r in runs:
        c=r['effective_configuration'];key=(r['dataset'],r['experiment_id'],r['model'],str(c['total_parameters']),str(c['trainable_parameters']),str(c['frozen_parameters']))
        if key in seen:continue
        seen.add(key);parameter_rows.append({'dataset':r['dataset'],'experiment_id':r['experiment_id'],'model':r['model'],
            'total_parameters':c['total_parameters'],'trainable_parameters':c['trainable_parameters'],'frozen_parameters':c['frozen_parameters'],
            'scope':c.get('parameter_count_scope','fitted model only unless specified; unknown counts NOT RECORDED'),
            'example_run_id':r['run_id'],'source':r['configuration_source'],'checkpoint':r.get('checkpoint_path',NR)})
    csv_write(OUT/'02_model_architecture/MODEL_PARAMETER_COUNTS.csv',parameter_rows)
    jsonstates=[]
    for r in runs:
        p=r.get('checkpoint_path','')
        if p.endswith('.json') and (REPO/p).is_file():
            jsonstates.append({'run_id':r['run_id'],'dataset':r['dataset'],'model':r['model'],'path':p,'bytes':(REPO/p).stat().st_size,'sha256':digest(p),'state_type':'fitted JSON coefficients/calibration or embedded model; inspect source key'})
    csv_write(OUT/'04_training_and_checkpoints/JSON_FITTED_STATE_REFERENCES.csv',jsonstates)
    costs=[]
    for r in runs:
        hs=[h for h in hist if h['run_id']==r['run_id']] if r['experiment_id'].startswith('REASSEMBLE_PHASE1') or r['experiment_id']=='REASSEMBLE_100E_SINGLE_FIT' else []
        numeric=lambda key:[h[key] for h in hs if isinstance(h.get(key),(int,float))]
        costs.append({'run_id':r['run_id'],'dataset':r['dataset'],'experiment_id':r['experiment_id'],'model':r['model'],
            'training_hours':r.get('duration_training_hours',NR),'train_plus_validation_hours':r.get('duration_train_plus_validation_hours',NR),
            'fit_wall_hours':r.get('duration_fit_wall_hours',NR),'inference_calibration_hours':r.get('duration_inference_calibration_hours',NR),
            'validation_hours':sum(numeric('validation_seconds'))/3600 if hs else NR,
            'mean_training_epoch_seconds':statistics.mean(numeric('training_seconds')) if numeric('training_seconds') else NR,
            'mean_training_GPU_compute_percent':statistics.mean(numeric('GPU_compute_percent')) if numeric('GPU_compute_percent') else NR,
            'peak_allocated_VRAM_GiB':max(numeric('peak_allocated_bytes'))/1024**3 if numeric('peak_allocated_bytes') else NR,
            'max_reserved_VRAM_GiB':NR,'mean_actions_per_second':statistics.mean(numeric('actions_per_second')) if numeric('actions_per_second') else NR,
            'allocated_GPU_job_hours':NR,'actual_kernel_compute_hours':NR,'feature_extraction_hours':NR,
            'epochs':r['effective_configuration']['executed_epochs'],'effective_batch':r['effective_configuration']['effective_batch_size'],
            'optimizer_updates':r['effective_configuration']['optimizer_updates'],'source':r.get('history_source',r['configuration_source'])})
    csv_write(OUT/'04_training_and_checkpoints/TRAINING_DURATION_AND_GPU_USAGE.csv',costs)
    curated=[]
    # Original pooled metrics are split into interval objects; reconstruct a display row without changing results.
    original=read('runs/reassemble/20260927T175336Z-section1b/assessment/results.json')
    for model,m in original['metrics'].items():
        curated.append({'dataset':'REASSEMBLE','model':model,'study':'original SECTION1B','seed':'one original split/offset family','fold':'pooled5','N':4530,'prevalence':509/4530,
            **{k:v['estimate'] for k,v in m.items() if isinstance(v,dict) and 'estimate' in v},'status':'COMPLETE; exploratory test reuse','source':'runs/reassemble/20260927T175336Z-section1b/assessment/results.json'})
    for r in results:
        take=(r['experiment_id']=='CNN100_STATIC_SENSOR_F2' or (r['experiment_id']=='REASSEMBLE_PHASE1_C20' and r['evaluation_scope']=='HELD-OUT POOLED') or (r['dataset']=='VIFAILBACK' and r['evaluation_scope']=='HELD-OUT POOLED'))
        if take:curated.append({'dataset':r['dataset'],'model':r['model'],'study':r['experiment_id'],'seed':r['seed'],'fold':r['fold'],'N':r.get('held_out_N',NR),'prevalence':r.get('prevalence',77/753 if r['experiment_id']=='CNN100_STATIC_SENSOR_F2' else NR),
            **{k:v for k,v in r.items() if isinstance(v,(int,float))},'status':'COMPLETE; scope limited as documented','source':r['metric_output_file']})
    externalmeans=[]
    for ds,protocol in [('MSM','primary__group_id'),('HANDOVER','official')]:
        selected=[r for r in results if r['dataset']==ds and r['experiment_id']=='EXTERNAL_P_'+protocol and r['evaluation_scope']=='HELD-OUT' and r.get('corruption')=='clean' and r.get('model_status')=='COMPLETE']
        fold_records=selected
        if ds=='MSM':
            selected=[r for r in results if r['dataset']==ds and r['experiment_id']=='EXTERNAL_P_'+protocol
                      and r['evaluation_scope']=='HELD-OUT POOLED' and r.get('corruption')=='clean'
                      and r['metric_output_file'].endswith('pooled_heldout_metrics.csv')]
            assert len(selected)==30
        for model in sorted({r['model'] for r in selected}):
            ms=[r for r in selected if r['model']==model];d={'dataset':ds,'model':model,'study':protocol,'seed':'mean3 seeds','fold':'pooled3 outer per seed' if ds=='MSM' else 'official test','N':1895 if ds=='MSM' else 151,'prevalence':336/1895 if ds=='MSM' else 110/151,
                'status':'COMPLETE; mean of per-seed pooled AP' if ds=='MSM' else 'COMPLETE; mean seeds official test','source':';'.join(sorted({r['metric_output_file'] for r in ms}))}
            for k in ['AP','AUROC','F1','Brier','precision','recall','balanced_accuracy']:
                vals=[r[k] for r in ms if k in r]
                if vals:d[k]=statistics.mean(vals)
            curated.append(d);externalmeans.append(d)
        if ds=='MSM':
            reconcile=[]
            for model in sorted({r['model'] for r in selected}):
                reconcile.append({'model':model,'mean_seed_pooled_AP':statistics.mean(r['AP'] for r in selected if r['model']==model),
                    'mean_seed_and_fold_AP':statistics.mean(r['AP'] for r in fold_records if r['model']==model),
                    'pooled_source':'MSM/06_evaluation_results/metrics/pooled_heldout_metrics.csv',
                    'fold_sources':';'.join(sorted({r['metric_output_file'] for r in fold_records if r['model']==model}))})
            csv_write(OUT/'06_dataset_specific/MSM/AP_AGGREGATION_RECONCILIATION.csv',reconcile)
    csv_write(OUT/'05_results/IMPORTANT_HELD_OUT_RESULTS.csv',curated)
    configrows=[]
    for (ds,exp,model),rs in sorted(groups.items()):
        def vals(key):
            vs=list(dict.fromkeys(cell(r['effective_configuration'].get(key,NR)) for r in rs))
            return ', '.join(vs) if len(vs)<=8 else f'{len(vs)} values; see per-run CSV'
        configrows.append([ds,exp,model,len(rs),vals('optimizer'),vals('learning_rate') if vals('head_learning_rate')==NR else vals('head_learning_rate'),vals('weight_decay'),vals('batch_size'),vals('max_configured_epochs'),vals('executed_epochs'),vals('selected_epoch'),vals('trainable_parameters'),vals('seed')])
    fullconfigs=table(['Dataset','Experiment','Model','Records','Optimizer','LR/head LR','Weight decay','Batch','Max epochs','Executed','Selected epoch','Trainable','Seeds'],configrows)
    display=table(['Dataset','Study/model','Seed','Fold','Held-out N','Prevalence','AP','AUROC','F1','Brier','Status'],[[r['dataset'],r['study']+'/'+r['model'],r.get('seed',NR),r.get('fold',NR),r['N'],r['prevalence'],r.get('AP',r.get('AUPRC',NR)),r.get('AUROC',NR),r.get('F1',r.get('macro_F1',NR)),r.get('Brier',NR),r['status']] for r in curated])
    report('05_results/IMPORTANT_RESULTS_TABLE.md','Important completed model evaluations',display+'\nAP values are never ranked across datasets. MSM entries are means across seeds of pooled3-outer AP; ViFailback and original REASSEMBLE entries are pooled AP. ViFailback both-class metrics are in its dataset report. All other recorded model variants, folds, robustness conditions and metric endpoints remain in ALL_MODEL_RESULTS_SUMMARY.csv and ALL_RECORDED_METRICS_LONG.csv. Missing individual metric values are NOT RECORDED, not zero.')
    report('03_hyperparameter_configuration/ALL_MODEL_CONFIGURATION_TABLE.md','All study/model configurations',fullconfigs+'\nEach cell summarizes recorded values, not a synthesized universal default. The per-run CSV and EFFECTIVE_CONFIGURATIONS.json resolve overrides and preserve all candidates. Framework defaults without state-level verification are explicitly marked. Different class weights, precision, frame contracts and calibration scopes require the configuration differences report.')
    inventory=table(['ID','Dataset','Model family','Actual architecture','Status/results'],[[i,d,m,arch,'SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines'] for i,d,m,arch,src,fn in FAMILIES])
    report('02_model_architecture/COMPLETE_MODEL_INVENTORY.md','Complete model inventory',f"""
The audit defines **{len(FAMILIES)} computational families**, separating distinct forward paths and explicitly including non-gradient baselines. This is a taxonomy, not a count of independent trained models. RT-DETR pretrained detector archives, tutorials, random-gradient tests and recovery slots are not additional scientific families. Mean16/32/48, seed repetitions and augmented versions remain variants of their computational family.

{inventory}

There are {len(runs):,} reconstructed per-fit/configuration records: {summary['completed_training_records']:,} marked COMPLETE and 40 REUSED. Of COMPLETE, 174 PHM SQ2/SQ3 calls are inferred from completed aggregate output plus source control flow, not individual receipts. The remaining 7,755 are individually corroborated by fit logs/receipts/candidate validation tables. They include permutation controls, nested candidate trials and recovery reconstruction refits; they are **not 7,929 independent replications**. Calibration/meta-crossfit nuisance estimators are not all included in that count. Other unlogged historical fits may not be recoverable.

See EXPERIMENT_INVENTORY.csv for study entry points/configurations/status and TRAINING_RUN_INVENTORY.csv for every record. The 4,920 checkpoint candidates include pretrained/disposable/copied/recovery artifacts; 4,438 unique hashes are byte identities, not unique model count. JSON coefficient-state references are indexed separately.

REBOOT has feasibility/parsing evidence, but no trained native-failure model artifacts were found. Intel welding material is preliminary data/EDA/source evidence, not a completed comparable classifier study. PHM architecture/results are historical provisional damage-target research and must remain separate from native binary failure outcomes.
""",[(r[4],r[5]) for r in FAMILIES])
    report('02_model_architecture/VISUAL_ARCHITECTURES.md','Visual architectures and executed trainable scope',"""
The primary research visual representation is **RT-DETR R18vd CNN only**, loaded from `PekingU/rtdetr_r18vd`, pinned revision `ac77a11ff0170a41b771c03264987f8ce2b0d753`. Source forwards select `.model.backbone.model`; the RT-DETR hybrid encoder, decoder, boxes and object scores are not consumed. Every frame contributes spatial means of the final 128/256/512 maps, concatenated to 896. Temporal averaging removes order in the mean baseline. The head is Linear896→128, ReLU, Dropout0.1, Linear128→1; sigmoid is applied for probabilities. A training-only fixed standardizer precedes the head. Head parameters: **114,945**.

Original visual inputs: RGB, 640×640, rescale1/255, no ImageNet mean/std. Sixteen uniform ordered action frames use rounded linspace indices; original extraction uses FP16 autocast and stores FP32 features. New Phase1/100e uses the preserved action-frame contract and FP32 fine-tuning. MSM/Handover use 16 temporal-bin centers, aspect-preserving letterbox640 with sample-aspect-ratio correction: this is a dataset-specific preprocessing adaptation, not an identical pixel path. ViFailback uses 16 rounded-linspace frames from each of three ordered cameras (48 embeddings), equal mean over time then cameras; high-only is 16-frame ablation.

Frozen CNN has 11,190,112 parameters, plus 114,945 head: conceptual pipeline **11,305,057 total**, **114,945 trainable**, **11,190,112 frozen**. Cached-head checkpoints can contain only the head and moments; absence of backbone tensors is expected for that fit module and requires the separately identified pretrained bank for end-to-end inference.

Full C promotes **9,856 FrozenBatchNorm affine buffers** into trainable parameters, preserving tensor names and pretrained values. CNN count becomes **11,199,968**; with head, **11,314,913 trainable/total**, zero frozen *parameters*. Frozen running means/variances remain buffers and remain fixed. All executed convolution stages are trainable. First-update and full-fit gradient/weight checks are retained in each original fit directory. Fresh original pretrained CNN and a freshly seeded head initialize both100e arms; C100 did not resume C20. Different parameter count comes from promoted affine buffers, not a changed feature width.

Historical `FineTunedVisual` and one-day/32-frame probes tune only the final CNN stage, with frozen prefix; they must not be described as full CNN training. The additional-improvements V-FT also warm-starts an existing temporal head and uses FP16 autocast/GradScaler. Its learning conditions differ from C100.

TemporalHead projects896→128, optional sinusoidal positions, one TransformerEncoder layer (4 heads, FF256, dropout0.1), masked temporal mean→1 (247,425 trainable parameters). V-MEAN retains mean pooling; V-NOPOS disables positions. Boundary V0–V4 use bin-based means with shared896→128 projection: V1 two8-frame bins, V2 4/8/4, V3last4, V4first4+last4; V5 uses64-dimensional one-layer GRU with positional encoding. They consume frozen CNN features.

The legacy encoder comparison actually executes CNN + input_proj + `RTDetrHybridEncoder` (AIFI and FPN/PAN), then pooling/head; no decoder or object outputs. Its feature width and parameter capacity differ, so any score difference is a complete-pipeline comparison, not isolated proof of attention benefit. Exact checkpoint/config counts are in MODEL_PARAMETER_COUNTS.csv; unrecovered values are NOT RECORDED.

PHM RT-DETR detection/regression/multitask implementations are separate Ultralytics/pseudo-target work. They do not define the native-failure architecture. Frozen DINOv2 nearest-baseline patch scoring is also distinct and has no new gradient training.
""",SOURCES['original']+sources100+[(r[4],r[5]) for r in FAMILIES if r[0] in ['F06','F08','F09','F11','F12','F30']])
    report('02_model_architecture/SENSOR_ARCHITECTURES.md','Sensor feature contracts and estimators',"""
| Dataset | Native channels | Window/clock | Statistical vector | Missing/scaling |
|---|---|---|---|---|
| REASSEMBLE | force3, torque3, gripper2, efforts7, velocities7 =22 | Annotated action window; per-stream timestamps;512 normalized-progress points |22×10=220: mean, population SD, median, min/max, Q25/Q75, peak-to-peak, RMS, slope over progress |Observed mask retained; fit-local mean fill/standardization; no new filtering |
| MSM |15 configured real MTConnect numerical channels | Native cut interval; verified video/sensor mapping; variable irregular samples |15×6=90: mean, SD, RMS, min, max, peak-to-peak |Finite real measurements; fit-local scaling; corruption scale derived from training rows |
| Handover |6 measured/estimated wrench channels | Explicit common video/sensor support; nearest native frame/sample mapping, <=0.1s bound |6×6=36, same external statistics contract |14 zero-channel traces retained; HSR measured versus Gen3 estimated wrench is a domain limitation |
| ViFailback |14 state+12 joint velocity+2 gripper effort =28 |25Hz episode-relative clock; entire recorded episode |28×10=280, exact channel list in sensor contract |Training-only imputation/scaling; finite cache join by episode ID; not a force/torque sensor |

REASSEMBLE512 is a sample count per action, **not512Hz**. None of these window-level predictors proves early failure detection. Original action labels are native outcomes; no lifecycle-to-health relabeling is allowed.

Original REASSEMBLE static sensor LR: balanced classes, candidate C0.1/1/10, max_iter2000, random_state0; mean inner AP selects C, training-OOF sigmoid calibration and balanced-accuracy threshold. Solver/penalty/tolerance omitted from original construction are FRAMEWORK DEFAULT — NOT VERIFIED unless a fitted estimator supplies them. Later F2 follow-up reuses the canonical original sensor probabilities/calibration rather than retraining a convenient replacement. Later shared legacy recipes use random_state42; nominal experiment seed and estimator RNG are separate fields.

MSM/Handover LR is predefined balanced C1, lbfgs, max_iter2000, random_state0. HGB: learning_rate0.1,max_iter100,max_leaf_nodes15,min_samples_leaf10,l2_regularization1,early_stoppingFalse; balanced sample weights. Saved source-identified estimator.get_params is retained in the per-run configuration. No fixed-depth value is invented when max_depth=None.

ViFailback S1=S3 is one actual balanced C1 logistic method, max_iter2000, random_state42, plus separate C calibration. S2 HGB varies max_leaf_nodes7/15/31; learning_rate0.05,max_iter200,min_samples_leaf20,l2_regularization0.1,early_stoppingFalse; training balance weights and nominal seed. Validation macro AP selects among three candidates before C calibration.36 jobs imply108 actual candidate fits,36 selected states. The three deterministic seeds can yield identical sensor predictions; they are not independent data samples.

REASSEMBLE PatchTST classifier:22channels/context512,patch32,stride16,d_model32,2layers,4heads,FF64,dropout0.1,channel pooled22×32→128→1, random initialization;3/6 epoch snapshots. S-6/S-LONG change budget, not the native channel definition. S-HYBRID combines sensor branches; it is not visual fusion. PHM PatchTST is a separate scalar-regression implementation using72 derived minute-feature channels in its standard recipe, train-only median imputation/population SD, masked temporal pooling, GELU/dropout scalar head. Ridge summarizes these sequences and selects alpha by EXP-A MAE.

No feature-selection algorithm is demonstrated for the fixed primary sensor contracts. Specific channel names, raw source paths, native label mapping, timestamps and group identities are linked in the native manifests; they are preserved rather than replaced with generic names.
""",SOURCES['original']+SOURCES['msm']+SOURCES['handover']+SOURCES['vi'])
    report('02_model_architecture/FUSION_ARCHITECTURES.md','Actual fusion mathematics and fitting scopes',"""
Let pV,pS be branch probabilities and l(p)=log(p/(1-p)) after source-defined clipping. Calibration of branches and fitting a fused calibrator are different operations.

| Method | Exact prediction / inputs | Estimation and OOF scope | Missing modalities |
|---|---|---|---|
| Average |(pV+pS)/2 |No fusion fit; branch calibration remains dataset-specific |Explicit surviving-branch fallback where wrapper supplies availability |
| Original F2 |sigmoid(b+wV*pV+wS*pS) |Unweighted C1 L2 logistic,lbfgs,max_iter2000,random_state0, signed unconstrained constant coefficients; calibrated nested training-side OOF, no p/logit transform, no fused calibration |Original complete-modality study; later wrappers explicitly bypass fusion to surviving branch |
| External/Vi F2 |Same probability logistic formula |MSM:2-inner OOF fixed branches; Vi:3-inner OOF with T/V/C task roles; source-specific random_state; no outer labels |Explicit deterministic branch fallback; both absent undefined/abstain |
| F3 |sigmoid(MLP(LayerNorm([proj128(v128),proj128(s220)]))) |Weighted BCE feature-level model; inner grid hidden/epochs32/10 or64/20, three seed-mean predictions; new OOF calibrator |No inherent missing-branch semantics; inspect wrapper/masks |
| F4/F5/F6 |alpha=masked_softmax(MLP(context)); sigmoid(alphaV*l(pV)+alphaS*l(pS)) |Unweighted BCE; action4+availability2 / quality36+availability2 / both42; hidden8or16,40epochs; fit train-side OOF context and branch scores |Mask unavailable branch; surviving branch deterministic; both absent abstain |
| F6 dropout |Same gate |Training availability probabilities V-only.15,S-only.15,both.70 |Fallback is architectural, not proof learned robustness |
| Anchored constant/adaptive |sigmoid(b+sum ai*(1+tanh hi(u))*pi) |Fixed F2 anchor; two parameters or context42→16→2,zero final init; lambda0.01/0.1/1 penalties; training-side validation |Source modality_fallback handles missing inputs |
| Quality additive / interaction LR |sigmoid(b+w·[p,z8]) / sigmoid(b+w·[p,z8,pV*z8,pS*z8]) |C1 unweighted logistic with clean/imageaug/sensoraug sample weights.5/.25/.25; train-only weighted quality moments and clip±10 |Explicit fallback; both absent abstain |
| Vi quality / neutral gate |Masked logit gate,13→16→2 |11quality+2availability; neutral ablation sets quality tozero with identical capacity;40epochs,lr.001,wd.001,batch64; train-side OOF |Availability mask and explicit missing branch behavior |

F2 is **not** a softmax convex mixture and its coefficients need not sum to one or be positive. A quality-aware name alone does not identify a shared model: the legacy quality LR, neural logit gate and anchored probability adjustment are mathematically distinct. Quality dimensionality/meaning is adapted to the dataset; MSM38 input entries differ from Vi13. The original F4 uses action context, not measured signal quality.

Original REASSEMBLE F2 uses5outer×4inner plus nested branch-selection subfolds; its threshold comes from meta-crossfit balanced accuracy. The100e follow-up has one920-row genuinely base-held-out stacking bank, **not four100e inner folds**; fitted coefficients are retained, but its selection history and onefold/one seed limit inference. MSM uses fixed10epoch heads and fixed sensor LR; shared external frozen settings do not reproduce the original REASSEMBLE branch selection/calibration protocol exactly. Handover F2/gates have no fitted results because participant OOF cannot be certified.

OOF correctness requires each meta-training sample to be absent from its base fit, base selection and base calibration groups. Saved split/lineage checks support the intended grouping for REASSEMBLE/MSM/Vi; repeated use of exposed outer scores for later architecture proposals still makes the overall research program exploratory. Neither this audit nor the reports create a missing F2 fit.

PHM latent, scalar-decision and process-aware fusions combine **sensor sub-modalities**, not video plus sensors. Their scalar regression loss/output, provisional damage target and legacy LOEO preprocessing limitations prevent comparison to native-failure F2 AP.
""",sourcesfusion+[('src/reassemble/section2_models.py','actual F3/gate forward'),('src/reassemble/additional_improvements/models.py','anchored formula/fallback'),('00_experiments/adaptive_fusion_robustness/code/quality_fusion.py','additive/interaction design and fitting')]+SOURCES['vi'])
    # Precise HPO verdicts with source-level anchors; no automatic framework claim.
    tuning=[
      ['Original REASSEMBLE static/action LR','SYSTEMATICALLY TUNED','C0.1/1/10','3 per selection fold','mean inner AP; selected refit','configs/reassemble/section1.json; section1_models.evaluate_model'],
      ['Original visual head / PatchTST','CHECKPOINT SELECTION ONLY','epochs5/10;3/6','2 stored epoch candidates each','mean inner AP; same optimizer recipe','configs/reassemble/section1.json'],
      ['F3','SYSTEMATICALLY TUNED','hidden32/epochs10 vs64/epochs20','2 coupled configs','mean inner AP of three-seed mean','configs/reassemble/section2.json; section2.py'],
      ['F4/F5/F6','SYSTEMATICALLY TUNED','hidden8/16','2 per gate family','mean inner AP','src/reassemble/section2.py; section2_models.py'],
      ['Anchored F2 adjustments','SYSTEMATICALLY TUNED','lambda.01/.1/1','3 per adjustment family','inner validation AP/robust selection from saved execution','configs/reassemble/additional_improvements/execution.json'],
      ['Boundary V0–V5 / legacy16/32/encoder','LIMITED/MANUAL TUNING','architecture/frame/final-stage alternatives','see variant receipts','outer-score-informed follow-up; exploratory','src/reassemble/boundary_visual/runner.py; legacy receipts'],
      ['C20 and B/C100','CHECKPOINT SELECTION ONLY','validation epoch; fixed LR/wd/batch','one recipe per arm','V AP; no optimizer search','PHASE1_C_ONLY_CONFIG.json; PHASE1_COMPARISON_CONFIG.json'],
      ['MSM/Handover primary recipe','PREDEFINED CONFIGURATION','no optimizer grid','1 per family','fixed final epoch; group/sensitivity comparisons','CROSS_DATASET_COMPARISON/configs/frozen_core.json'],
      ['Vi frozen head / F2 / gates / LR','CHECKPOINT SELECTION ONLY / PREDEFINED CONFIGURATION','V epoch only for head','one recipe','V macro AP for head; fixed other fits','VIFAILBACK/src/vifailback/training.py; fusion.py'],
      ['Vi HGB','SYSTEMATICALLY TUNED','max_leaf_nodes7/15/31','3×36=108 fitted candidates','V macro AP then C calibration','VIFAILBACK/src/vifailback/baselines.py; S2_SELECTION_AND_CALIBRATION.json'],
      ['PHM Ridge','SYSTEMATICALLY TUNED','alpha.01/.1/1/10/100','5×6 saved studies=30','EXP-A MAE','src/phm2026/models/patchtst/regression.py; ridge_selection.json'],
      ['PHM DINO scoring','LIMITED/MANUAL TUNING','2backbones×2banks×5aggregations','20 evaluation configs, no new gradient fits','same38 human calls reused; best biased','docs/thesis/ANOMALYDINO_SWEEP.csv; scripts/phm2026/results/anomalydino_sweep.py']]
    tuningtable=table(['Model','Verdict','Parameters tested','Configurations/trials','Selection','Evidence'],tuning)
    report('03_hyperparameter_configuration/HYPERPARAMETER_TUNING_HISTORY.md','Hyperparameter tuning history and verdicts',tuningtable+"""

Small explicit nested grids **are systematic tuning**. No evidence was found for Optuna, GridSearchCV, RandomizedSearchCV, Ray Tune, Bayesian search, Hyperband or successive halving in the discovered research source/notebooks. Absence of an HPO framework does not negate manual grids. Exact observed selected values and every retained trial are in EFFECTIVE_CONFIGURATIONS.json; unretained original candidate weights limit exact re-inference.

Training to100 epochs is a budget change, not by itself hyperparameter optimization. Choosing an epoch is checkpoint selection. Fitting sigmoid calibration or F2 coefficients estimates model parameters and is not tuning its C unless C was compared. Repeating seeds is stability analysis. Comparing full/frozen or16/32 frames is model/protocol comparison and becomes exploratory selection if the exposed outer result drives the next experiment.

Search count is distinct from fit count: e.g.540 Section2 logs include seeds, inner candidates and final refits, not540 different hyperparameter configurations. The original Section1 and sensor-null trial expansions include19 permutation controls; they are not independent evidence of native predictive performance. PHM DINO's best-of20 and boundary variants lack fresh confirmatory held-out selection evidence.
""",SOURCES['original']+[(s,w) for s,w in sources100[:3]]+SOURCES['vi']+[('src/phm2026/models/patchtst/regression.py','Ridge candidate loop'),('docs/thesis/ANOMALYDINO_SWEEP.csv','all20 scoring configurations')])
    differences="""
| Comparison | Preserved factors | Material differences / effect on interpretation |
|---|---|---|
| Original frozen versus C100 |Pinned CNN family,16frames,896→128→1 |Batch128 versus8; short5/10 snapshots versus100cosine; original extraction FP16 versus full FP32; T/V/C role changes; test-exposed fit selection. Not an isolated fine-tuning effect. |
| Paired B100 versus C100 |Seed42,same1752 T/419 V/686 C/753assessment, fresh head, FP32,100horizon,headLR.001,wd.001,batch8,16frames,no augmentation |C adds backboneLR1e-5 and trains all CNN+affine; B uses cached fixed features; time/VRAM excludes B extraction. Controlled within-pilot point comparison, one exposed fold. |
| C20 versus C100 |Full-CNN architecture,original pretrained initialization |Different jobs/cohort roles; C20 executes cosine50 prefix to20, C100cosine100; C100 restarts fresh. No continuation or monotonic budget inference. |
| Original F2 versus100eF2 |Canonical static sensor probabilities/labels for same original outer1 |Original nested fourinner branches versus single920holdout stack bank; different visual branches and fitting rows, exposed test. Raw AP gain cannot isolate representation effect. |
| Historical V-FT versus fullC |Same R18vd family |Last-stage-only, temporal warm-start,AMP versus all CNN/affine fresh-head FP32. Different computational architecture/training scope. |
| External P across datasets |Fixed base/fusion code and hyperparameters |Real sensor definitions,frame sampling/letterbox,window/native labels/group granularity differ; Handover participant OOF blocked. Scores cannot rank datasets. |
| Vi V1 versus high-only |Same task splits,seeds,100head recipe |48frame3-camera versus16framehigh; not matched observation bandwidth. V2/V3 model training absent. |

Every per-run field can be resolved in PARAMETER_PROVENANCE.csv. Missing betas/epsilon remain FRAMEWORK DEFAULT — NOT VERIFIED unless recovered from the actual state;28 Phase1/100e optimizer states were statically verified as betas(.9,.999),eps1e-8. Do not silently apply that recovery to other source-only histories.
"""
    report('03_hyperparameter_configuration/CONFIGURATION_DIFFERENCES.md','Configuration differences that matter',differences,SOURCES['original']+sources100+sourcesfusion+SOURCES['vi'])
    # Checkpoint chain and cost limitations.
    repro=table(['Study/model','Code/config','Checkpoint/predictions','Split/history','Overall status'],[
        ['Phase1 C20/B and B/C100','available; current source plus recorded hashes','best CPU state + rolling resumable slots; saved probabilities','IDs/history complete','COMPLETE for artifact chain; no training replay during audit'],
        ['Original REASSEMBLE branch trials','available','selected outer states/banks; many inner/control weights not retained','splits/losses/OOF probabilities','PARTIAL; selected inference stronger than exact all-trial resume'],
        ['Original F2','available','JSON coefficients/OOF bank/outer predictions','nested split/lineage and thresholds','COMPLETE fitted-state-to-metric chain; preprocessing depends on pinned inputs'],
        ['100eF2 pilot','available','small heads/calibrators/coefficients/7scores','920stackbank/same753test identities','COMPLETE artifact chain; limited scientific design'],
        ['MSM/Handover completed baselines','available','hash-verified head/LR/HGB/outputs','native cohort/splits/logs','INFERENCE_ONLY or PARTIAL resume; selected inference complete'],
        ['MSM F2/quality','available','JSONF2/PTgates and OOF/outputs','fit context/inner group provenance','INFERENCE_ONLY; optimizer/RNG not retained for all'],
        ['Handover F2/quality','code/config only','none','participant IDs missing','MISSING_ARTIFACTS; NOT EXECUTED, not a failed trained model'],
        ['Vi frozenV1/high','available','BEST_MODEL + FINAL_EPOCH100 + predictions','tasksplit/100history/recovery metadata','COMPLETE saved chain; no raw decode/inference replay'],
        ['Vi LR/HGB/fusion','available','selected fitted states and OOF/outputs','task IDs; rejected HGB candidate metrics','INFERENCE_ONLY / PARTIAL candidate replay'],
        ['PHM SQ2/SQ3 / latefusion','current source/config','aggregate evidence; no saved per-fit states','perseed aggregate; perfit epochs absent','METRICS_ONLY for unretained models'],
        ['PHM canonical scalar/detector models','available','safe state inspection where supported; legacy detector declined','histories/config/targets','PARTIAL; provisional targets, payload trust restrictions']])
    report('04_training_and_checkpoints/REPRODUCIBILITY_ASSESSMENT.md','Reproducibility assessment',repro+"""

Loading for inference, replaying evaluation, resuming optimization and reproducing from initialization are separate claims. A state dict plus config can support inference while lacking optimizer/scheduler/RNG needed for exact resume. A last slot contains later training state, not the validation-selected best model. Code presence at current HEAD does not prove historical execution of current bytes; use archived source snapshots or executed source hashes. Dirty worktree provenance is retained.

All4920 binary candidates were hashed;3828 safe CPU inspections succeeded. Declined weights-only loads were **not** retried using unsafe Torch pickle. Source-identified study-owned small sklearn estimators were inspected on CPU only after matching receipt SHA. Literal AdamW parameters were recovered from pickle opcodes without executing them. No checkpoint was loaded into GPU. No inference/feature extraction/training replay was required to verify saved prediction metrics.

JSON_FITTED_STATE_REFERENCES.csv supplies additional fitted coefficients not included in binary4920. It is a run-to-state reference table, so several records may point to one file. CHECKPOINT_INVENTORY.csv records aliases and available optimizer/scheduler/RNG evidence, with unknown metadata explicitly partial. A training COMPLETE receipt is not a blanket claim of scientific reproducibility or all-state resume.
""",sources100+sourcesfusion+SOURCES['msm']+SOURCES['vi'])
    report('04_training_and_checkpoints/CHECKPOINT_SELECTION_AUDIT.md','Checkpoint selection and training completion',"""
Original visual/PatchTST select a common epoch candidate by mean inner AP (5/10 or3/6); candidate training loss trajectories do not constitute held-out curves. F3/gates select an inner configuration and evaluate source-defined final epochs. Later temporal/anchored models use100maximum,min10,patience12 and saved validation objective; V-FT uses20maximum,patience5. Per-run best/final values are preserved rather than inferred from directory names.

B100 and C100 each executed100epochs. Best epochs **14 and47** are selected by V AP, with V weighted BCE/earliest tie rule in the Phase1 code. All100epoch histories exist; selected checkpoint state epoch agrees with receipt and history. This is not early termination at14/47. Checkpoint selection uses V, not the753assessment labels. However the choice of this particular fit for a new100epoch follow-up was informed by earlier experiment results, so the final cohort is not pristine.

C20 executes exactly20epochs for25fits at seed42; no early stop, originalcosine50prefix. Receipt predictions correspond to the V-selected best checkpoint, not automatically epoch20. The approved stop marker is final for the25-fit cap; it is not the original75-fit all-complete marker. Vi frozen100 similarly runs all100 and picks the first strict maximum of V macro AP, verified for all72heads.

PHM saved histories/counts are separate from native classification. Legacy SQ2/SQ3 aggregate results do not retain actual selected epochs or executed epoch histories: those fields remain NOT RECORDED. No epoch count is invented from max80.

For every exact best/last path, hash, available state components and recorded epoch, use CHECKPOINT_INVENTORY.csv, TRAINING_RUN_INVENTORY.csv and JSON_FITTED_STATE_REFERENCES.csv. Original selected outputs were hash-checked before metric recomputation.
""",sources100+SOURCES['vi']+[('src/reassemble/additional_improvements/neural.py','early stop and best-state selection')])
    report('05_results/TRAIN_VS_VALIDATION_VS_TEST.md','Metric scopes and definitions',"""
`evaluation_scope` is mandatory in the long tables. TRAINING / TRAINING IN-SAMPLE diagnose fit; VALIDATION / VALIDATION OFFICIAL choose epochs/settings or describe official validation; INNER-OOF ASSESSMENT supports training-side meta fitting; HELD-OUT is the outer/official assessment; PAIRED DIFFERENCE and BOOTSTRAP INTERVAL are contrasts/interval endpoints, not standalone model predictions. Permutation controls and human-appearance development are separate. Do not pool these categories.

AP is non-interpolated average precision, sum of recall increments times precision at each score threshold; ties are grouped. Original `AUPRC` here is the saved average-precision implementation, not assumed trapezoidal PR area. AUROC is pairwise ranking with half credit for ties. Binary threshold metrics use source threshold (often0.5); native original training-OOF balanced-accuracy thresholds are retained separately. F1 versus macro_F1 are distinct. Vi macro_AP is mean of failure AP on p and success AP on1-p. Prevalence is required context:REASSEMBLE509/4530,selected100pilot77/753,MSM336/1895,Handover110/151,Vi3753/4382. A constant prior can have different pooled ranking if its fold-specific training prior varies; do not replace MSM pooled prior AP with overall prevalence.

Precision=TP/(TP+FP),recall=TP/(TP+FN),specificity=TN/(TN+FP),balanced accuracy=(recall+specificity)/2. Brier is mean squared probability error; log loss uses source-defined clipping. Original ECE uses15bins; external fixed recipe does not record ECE, so absent entries are NOT RECORDED. Zero divisions follow the original evaluation. Confusion matrices are flattened as TN/FP/FN/TP where available; original matrix/classification tables retain their source paths.

Mean-fold AP, pooled out-of-fold AP, seed-mean AP and AP of seed-mean predictions are different quantities. The audit does not merge them. Robustness tables preserve corruption name/severity and evaluation subset. Conditional confidence intervals resample recording/group/run where recorded; seed repeats on the same held-out samples do not increase independent N. Absent intervals are NOT AVAILABLE; no new interval is manufactured.

ALL_RECORDED_METRICS_LONG.csv includes every extracted numeric metric and recorded interval endpoint, plus epoch metrics. The raw metric key is preserved to avoid silently changing scientific definitions. `held_out_N` in historical aggregate rows may be NOT RECORDED where the source does not specify scope. Source `metric_path` is retained for nested aggregates; arrays of bootstrap draws are linked rather than copied. Summary CSVs omit epoch rows only; EPOCH_HISTORIES and long metrics retain them. Official Handover validation rows are explicitly labeled VALIDATION OFFICIAL.
""",[('CROSS_DATASET_COMPARISON/src/external_eval/evaluate.py','metrics and execute_case roles'),('VIFAILBACK/src/vifailback/metrics.py','both-class metrics'),('src/reassemble/section1_models.py','original AP/calibration/threshold'),(follow+'/07_evaluation_results/ORIGINAL_NATIVE_THRESHOLD_METRICS.json','native versus0.5 thresholds')])
    # Dataset reports.
    report('06_dataset_specific/REASSEMBLE/MODEL_AND_CONFIGURATION_AUDIT.md','REASSEMBLE model and configuration audit',"""
Primary original cohort:4530 dual-complete primary actions,509native failures,148recordings. Grouping is recording;5outer/4inner with further nested branch-selection folds, original seed20260927 plus deterministic fold/fit offsets. Four context actions and complete-modality criteria are source-defined. Shifts within recording/action strata supply19null controls plus observed runs; they are not new datasets.

The original CNN is frozen R18vd-only,16uniformframes,896featuremean and128ReLU/dropout0.1head,AdamW.001,wd.001,batch128,clip1,FP32head training on FP16-extracted features. Select5/10 by mean inner AP. Original static220sensor LR selects C.1/1/10 with balanced classes; PatchTST22×512 has3/6snapshots. Independent selection/calibration applies to each branch; F2 uses their nested OOF probabilities, fixedC1. Section2 F3/F4/F5/F6,modality dropout,additional temporal/anchored/sensor extensions,boundary variants and legacy final-stage/encoder probes are separately indexed. Per-run effective configuration, actual epochs, selected epochs and retained states are not replaced by generic defaults.

Current C-only study: **25/25 approved fits complete,25/75 original fits complete**, seed42 all5outer folds (4inner+1outer each). All20epochs per fit completed; seeds123 and20261023 deferred. No main training job was live at initial read-only inspection. C20 pooled held-out visual AP **0.312127025700**,AUROC **0.756385557356** over4530 unique IDs; this audit computed only metrics from already saved predictions. C20 F2 finalization has NOT EXECUTED and no C20 fusion result is created here. Original frozen B has only one retained long-run receipt before C-only revision; no complete paired fivefold B20 exists.

The100epoch pair is a separate fresh-initialization singlefit/seed42 pilot, selected original fit3/job_index2,outer_fold_original0. Bselected14,Cselected47,each100completed. The same753heldout actions (77failures,26recordings) were already exposed in earlier work. The separate100e static-sensor F2 pilot is complete, but not a fivefold/three-seed100e fusion experiment. See the two adjacent detailed reports.

Transfer: canonical seed42 outerassessment donor now has a valid completed20epoch receipt and matching selected-state SHA. MSM/Handover validator still requires>=25executed epochs; no R external run was executed. Vi has a valid identified C100 donor featurebank but no V3 classifier/fusion training, and a separate75-fit scheduling barrier. Feature availability is not evidence of completed model transfer performance.

Historical mean-frame/final-stage/temporal/probe experiments should be described as exploratory. Boundary fusion variant choice uses exposed outer AP; later pilots reuse the same outer cohort. This limits confirmatory conclusions without invalidating the existence of their saved predictions. No final model selection is made.
""",SOURCES['original']+sources100+sourcesfusion+[(base+'/26102026_c_only_20epoch_revision_01/26102026_execution/PHASE1_C_ONLY_STATUS.json','current25cap status'),(base+'/26102026_c_only_20epoch_revision_01/02112026_stop_after25fits_01/STOP_AFTER_25_COMPLETE.json','stop receipt and protected model/prediction hashes')])
    pairtable=table(['Model','Executed / selected epoch','T/V/C/assessment','Training h','Peak allocated GiB','Mean TRAINING compute %','AP','AUROC'],[
        ['B_frozen100','100 /14','1752/419/686/753',.0609923873655498,.080301,21.4613,.19377557761499092,.6646046261430877],
        ['C_full_finetuned16','100 /47','1752/419/686/753',23.964191181254733,7.7700304985,99.713245,.21258450333908707,.6753246753246753]])
    report('06_dataset_specific/REASSEMBLE/FROZEN_VS_FINETUNED_100_EPOCHS.md','Frozen versus full-CNN100epoch evidence',pairtable+"""

Both use fresh original pretrained CNN and fresh seed42head;16frames/FP32,headLR0.001,wd0.001,clip1,effectivebatch8,micro1,100epochcosine multiplier1→.1,workers4,decoderthreads2,pinned/persistentprefetch2,no augmentation. CbackboneLR1e-5; allCNNconvolutions and FrozenBNaffine trainable, running moments fixed. AdamWbetas(.9,.999),eps1e-8 were recovered from actual resumable optimizer metadata without executing pickle. The frozen model operates on cached CNN features; its tiny head-training GPU memory/time omit feature extraction. Bprefix training order checks and Cgradient checks were previously retained.

The audit verifies100consecutiveepochs and selectedbest epochs14/47, receipt/statehash correspondence and saved prediction metrics on identical nativeIDs. `EPOCH_HISTORIES.csv` contains every epoch's training/validationloss,validationAP/AUROC,LR,updates,seconds,VRAM/utilization where recorded. The figures beside this report use those exact rows. Best checkpoints are PHASE1_BEST_MODEL.pt in each execution arm; last-state pointers are PHASE1_LATEST_EPOCH.json with hash-identified rotating recovery slots. Full paths/hashes remain in the checkpoint/run CSVs, and original held-out predictions remain linked in RESULTS_PROVENANCE.csv.

Visual AP difference is **+0.01880892572409615** on this selected cohort. It supports an observed improvement under this matched pilot recipe. It does not establish the average effect across folds/seeds or explain differences from the earlier short frozen study, which used batch128,short epochs and different fitting roles. No comparison interval is fabricated. Both branch probability calibrators are training-side, but pilot selection/test reuse makes later inference exploratory.

Ctraining23.964191h,validation1.629115h,inference/calibration.062891h. The process-attempt record has B271.338s and C10646.992+30.070+82269.026s: **pair active child wall25.89373h**, C-only25.81836h. These are neither pure GPU kernel hours nor uninterrupted calendar duration. Mean per-epoch sampled TRAINING NVML utilization99.713% is an activity statistic; it is not VRAM utilization. Peak allocated7.770GiB is a memory statistic, not reservedVRAM or compute percent. There is no defensible all-history GPU-hours grand total because many historical stages lack allocation/telemetry records.

Checkpoint chain is complete for saved-state/prediction/metric verification; no expensive inference or training was replayed. Single seed42,onepreviouslyexposedouterfold and preselection of fit3 are material limitations. Stronger independent effect estimation would require an agreed fresh/grouped assessment design; this audit neither chooses nor launches it.
""",sources100+[(comp+'/26102026_execution/PHASE1_COMPARISON_PROCESS_ATTEMPTS.json','active child attempts and restart overhead')])
    report('06_dataset_specific/REASSEMBLE/FUSION_RESULTS_AND_CONFIGURATIONS.md','Original static F2 and100epoch follow-up',"""
Original pooled5outer F2 AP **0.447298551440**,AUROC **0.794968361094**; sensorAP **0.429391869368**,visualAP **0.230658315043**. F2−sensorAP **+0.017906682072**,paired recording95% interval **[0.008602699847,0.028284279537]**,2000draws conditional on saved models. This is the original canonical static F2 result, not C20 fusion. On originalouter1 alone F2AP0.367155245715,sensor0.327704564506.

| Same753assessment /seed42 | AP | AUROC | F1 at0.5 | Brier |
|---|---|---|---|---|
| Frozen100visual |0.193775577615|0.664604626143|0|0.089570168276|
| Full100visual |0.212584503339|0.675324675325|0.070588235294|0.089255169208|
| Canonical static sensor |0.327704564506|0.723680165988|0.252631578947|0.081479485480|
| Frozen100F2 |0.334977351562|0.728675170983|0.177777777778|0.080453165174|
| Full100F2 |0.349094220121|0.740298163375|0.177777777778|0.080157140841|
| Frozen100average |0.348006752040|0.721240298163|0.073170731707|0.081604536011|
| Full100average |0.358533402216|0.745984784446|0.074074074074|0.080793130568|

Follow-up F2 uses calibrated branch probabilities and saved signed logistic coefficients, fixedC1,lbfgs,max_iter2000,unweighted fit; no probability-to-logit transform or second fused calibrator. The static branch is the original canonical220statLR/calibrator. A genuine920-row base-held-out bank supports stacking, but this is not the original complete4inner-fold100epoch OOF design. Common0.5 metrics above are separate from native thresholds: sensor0.14,frozenF20.10,fullF20.14.

Paired recording intervals: fullF2−frozenF2AP **+0.014116868559**,95% **[-0.00077261755,0.02908933571]**; fullF2−sensor **+0.021389655616**,**[-0.00034530379,0.03635822909]**; frozenF2−sensor **+0.007272787057**,**[-0.00315139872,0.01537746535]**. Both F2 variants exceed their corresponding visual-only branch with positive conditional intervals, but the fusion-versus-fusion and fusion-versus-sensor gains are inconclusive. Averaging has a higher point AP in this pilot; no final architecture is selected on this reused test set.

Do not equate visual fine-tuning improvement with established fusion improvement. The follow-up supports a conditional point estimate, one seed/onefold; the original broader F2 is a different fitted protocol. C20 F2 finalization remains NOT EXECUTED. Every M1–M7 metric, subgroup/calibration/native-threshold table and bootstrap contrast is linked in COMPLETE_RESULTS/RESULTS_PROVENANCE; large prediction/draw banks stay at original paths.
""",sourcesfusion)
    for ds,sources in [('MSM',SOURCES['msm']),('HANDOVER',SOURCES['handover'])]:
        own=table(['Model','Mean held-out AP','AUROC','F1','Brier'],[[r['model'],r.get('AP',NR),r.get('AUROC',NR),r.get('F1',NR),r.get('Brier',NR)] for r in externalmeans if r['dataset']==ds])
        if ds=='MSM':
            body="""
1895eligible cutting intervals,336positive; native labels retained, original label2 retention/exclusion sensitivity explicit. Positive target is source-defined abnormal-cut mapping, not stage/run number.45nominalgroups; physicaltool/workpiece/session IDs incomplete. Threeouter/twoinnerfolds,seeds42/123/20261023. Sixprotocols (retain/exclude label2 × nominal/machine_date/calendar_date) yield54completed cases;594fitted model records comprise base fits and F2/gates. Primary table is mean of9outerfold/seed AP values, not pooledAP and not independentN=9×1895.

Fixed visual10epochs,batch32,AdamWlr.001/wd.001,clip1,FP32,frozenCNNhead114945;16bincenterletterbox640RGB frames,SARcorrected.15MTConnectchannels×6stats90;LRbalancedC1lbfgs2000,random0;HGB.1/100/15leaf/minleaf10/l2=1/earlystopFalse,balanced sampleweights. Average/F2 use LR sensor, not HGB. F2C1unweighted probabilitylogistic; QGclean/QGaug hidden16,40epochs,lr.003/wd.001,batch128clip1,quality36+availability2. Augmented variants use source-fixed lowest-severity corruption views, no HPO. No multi-setting optimizer tuning occurred in this recipe.

Reported approximateAPs are reconciled to saved per-case tables:visual.298901,LR.828616,HGB.901299,average.735594,F2.756879,F2aug.760170,QGclean.837418,QGaug.826521. The pooled prevalence baselineAP.145395 differs from cohortprevalence.177309 because the fold-trained constant priors differ. Primary group independence is nominal dataset group, with only5dateproxies; these do not certify physical-tool independence. Saved paired2000group bootstrap intervals are conditional on fitted models and grouped units. Every corruption/severity,perseed/perfold,subgroup and source-recorded interval is retained in COMPLETE_RESULTS.

Every available case output hash and clean held-out metric was checked against saved probabilities. Native sample/label joins and train/assessment disjoint IDs were independently verified across all saved role/corruption rows. Fit group and OOF lineage follow execute_case/fit_fusions. Current Rtransfer remains NOT EXECUTED: canonical donor exists at20epochs but source validator still demands>=25. Neither donor nor validator was altered.
"""
        else:
            body="""
Native589trials;finalcommon_support_v2 has587aligned examples:335train,101officialvalidation,151officialtest;110testfailure/41success,prevalence.7284768. Two trainingtrials were excluded for nearest wrench/video gap>0.1s. Earlier full-tail eligibility audit flagged92testtails; the explicit common observation window amendment before fitting supersedes that old cohort rule and retainsall151test. It must be disclosed as a preprocessing amendment, not hidden.

Visual16bincenterletterbox640RGB/frozenR18vdhead,10epochs,AdamW.001/wd.001,batch32,clip1. Sensor6wrenchchannels×6stats36;LRbalancedC1,lbfgs,max2000,random0;HGB.1/100/15leaf/minleaf10/l2=1,earlystopFalse with balanceweights. Three seeds42/123/20261023 completed all baseline families. Officialvalidation rows are descriptive under the fixed recipe, not synthetic training curves. Average uses visual+LR, not HGB.

F2,F2aug,QGclean,QGaug are **NOT EXECUTED / BLOCKED**. Official documentation claims participant-disjoint splitting, but the available native metadata/authorloader identifies robot/task/trial, not participants. Empty participant_id is preserved. Trial IDs,robot IDs,task IDs or dates cannot be substituted for people. Certifiable participant-disjoint inner OOF is therefore unavailable; officialvalidation/test must not be repurposed to fit fusion. No participantbootstrap can be justified. Seed repetition on the same151testtrials does not supply independent participant evidence.

Clock/window mapping,selectedframes/nativewrenchindices/sourcehashes remain in the finalmanifest. HSRwrench is measured while Gen3wrench is estimated;14zerochanneltraces are retained. These are dataset limitations, not silently repaired signals. MeanAP visual.771647,LR.823624,HGB.906319,average.803102;constantpriorAP.728477. Failure prevalence is high. TransferRnotexecuted; canonical20epochdonor fails>=25validator. Participant mapping recovery requires official pseudonymous identity metadata, not invented assignments.
"""
        report(f'06_dataset_specific/{ds}/MODEL_AND_CONFIGURATION_AUDIT.md',ds+' model and configuration audit',body+'\n'+own,sources)
    virows=[r for r in curated if r['dataset']=='VIFAILBACK']
    vit=table(['Model','Seed','Failure AP','Success AP','Macro AP','AUROC','F1 at0.5','Brier'],[[r['model'],r['seed'],r['AP_failure'],r['AP_success'],r['macro_AP'],r['AUROC'],r['F1'],r['Brier']] for r in virows])
    report('06_dataset_specific/VIFAILBACK/MODEL_AND_CONFIGURATION_AUDIT.md','ViFailback current models and status',"""
Currentfinalcore **4382episodes=3753failures+629successes,99tasks**, not historical4384/3755/629. Native5202=4545/657. CameraQC13150/13152, followed by2further exclusions; sensorfeaturecache still4384 and model joins correctly subset by finalepisodeID. Task55quarantined/B02uncertainty are documented source limitations. Whole-recorded-episode classification does not establish action-level localization/early warning. Physical-session independence and hardware-clock synchronization are unverified.

Task-disjoint3outer/3inner,source hash-ordered labelblind assignment. T/V/C/A task roles are disjoint and eachmetaOOFepisode is absent from its own fit/validation/calibration. Three seeds42/123/20261023. **72frozen100epochhead fits complete**:36V1threecamera+36high-only. **36sensorjobs** eachLR+3HGBcandidates (36+108fits,36selectedHGBstates). **9V1fusionjobs** eachF2+quality+availability-neutralgate (27fits). Total243fitted classifier/gate/candidate records. V2fullfine0,V3transferclassifier0. BothoriginalV1andC100donorV3featurebanks arecomplete; cached donorfeatures do not constitute a trained transferhead.

Frozenhead896→128ReLUdropout.1→1,114945trainable,100cosineepochs,batch8,lr.001/wd.001/clip1,FP32. SelectfirststrictmaxVmacroAP,calibrateonC,keepBESTandFINAL_EPOCH100. Sensors28×10=280 at25Hz (state/velocity/grippereffort,notforce/torque). S1=S3onebalancedC1LR,random42,2000iter. HGB.05/200iter/minleaf20/l2.1/noearlystop;leaves7/15/31selectedVmacroAP,thenCcalibration. F2C1probabilitylogistic oninnerOOF;gate11quality+2availability→16→2,40epochs,lr.001/wd.001,batch64;neutralablationzerosquality,notanuntrainedconstant.

Allpooledscoresbelowuse the same4382heldout IDs perseed. The sameepisodes across3seeds are not13146independentobservations. Failureprevalence.856458makesfailureAPalone misleading; reportbothclasses andmacroAP. HGBandLR aredeterministicacrosssavedseeds. F2macroAPisbelowLRinall3savedseeds; no newCIortrainingiscreatedhere.

SavedPIPELINE_STATUS (Oct30) saysWAITING_REASSEMBLE75_COMPLETE_AND_GPU_IDLE,withdeadcontrollerPID290646atauditstart. Itisnotalivejustbecauseastatusfileexists. resources.gpu_staterequires75fitallcompletemarker+finalmetricshash;approved25fitcapdoesnotproduceit. ThusV2/V3trainingisNOTEXECUTEDandblockedbyschedulingcontract,notcurrentlyprogressing. Auditdoesnotfixorrestartthiscontroller.
"""+'\n'+vit,SOURCES['vi']+[('VIFAILBACK/04_evaluation_splits/train_validation_test/20261029T004900Z/fit_partitions.json','all12T/V/C/Ajobs and OOF coverage')])
    # Validity/comparability, missing evidence and future-decision information.
    comparisons=[
        ['Original REASSEMBLE visual/sensor/F2','DIRECTLY COMPARABLE','same4530nativeIDs/labels,5outergroupcohort andAP; original nestedrecipe; exploratory program'],
        ['B100 versus C100','COMPARABLE WITH LIMITATIONS','same753IDs/TVC/seed/headbudget; onepreselectedexposedfold; cachedBcostexcludesCNN'],
        ['100F2 versus its sensor/visual','COMPARABLE WITH LIMITATIONS','same753labels/canonicalsensor; one920stackholdout/seed; conditionalintervals'],
        ['Original F2 pooled versus100eF2 pilot','NOT DIRECTLY COMPARABLE','4530pooled versus753selectedfold; OOFtrainingandselectionhistory differ'],
        ['Original outer1F2 versus100eF2','COMPARABLE WITH LIMITATIONS','sameassessmentIDs but stackingfitbanks differ; notisolatedrepresentationeffect'],
        ['C20 versus original frozen','COMPARABLE WITH LIMITATIONS','sameouterassessmentcohort possible; batch/schedule/TVC/recipe differ; onlyseed42'],
        ['C20 versus C100','NOT DIRECTLY COMPARABLE','5outer versus1selectedjob; cosine50prefix20 versus100freshrestart'],
        ['MSM Pvisual/LR/HGB/average/F2/QG','DIRECTLY COMPARABLE','sameprimarysplitIDs; allviews/protocol matched; HGBisstrongsensorbaseline,notF2branch'],
        ['MSM nominal versusdate/label2sensitivity','NOT DIRECTLY COMPARABLE','changedgroupunit/eligiblepopulation; sensitivity notsameheldoutprotocol'],
        ['Handover baseline families','COMPARABLE WITH LIMITATIONS','same151officialtest; participantdisjointclaimunverifiable; sameclock/windowamendment'],
        ['Handover F2/QG versusbaselines','INSUFFICIENT EVIDENCE','F2/QGnotexecuted; noavailableparticipantOOF'],
        ['Vi V1/LR/HGB/F2/QG/neutral','DIRECTLY COMPARABLE','same4382IDs/taskouterfolds/labels/seed; reportmacroAPandbothclasses'],
        ['Vi high-only versus3camera','COMPARABLE WITH LIMITATIONS','sameepisodes/splits/recipe; differentobservationalbandwidth'],
        ['Vi V2/V3 versusV1','INSUFFICIENT EVIDENCE','newfull/transferclassifiertrainingnotexecuted'],
        ['REASSEMBLE/MSM/Handover/Vi AP ranking','NOT DIRECTLY COMPARABLE','differenttargets/prevalence/cohort/window/group/camera/sourcecontracts'],
        ['Boundaryselected/legacyfollowups','COMPARABLE WITH LIMITATIONS','savedpairedpredictionsbutouterAPreusedforarchitecturechoice'],
        ['PHM LOEO fusion versusprimaryclassifiers','NOT DIRECTLY COMPARABLE','provisionalregressiontargets,notfailureAP; fixedEXPBnormalizerleaksLOEOBassessment'],
        ['PHM DINO best20 versusheldoutclaim','NOT DIRECTLY COMPARABLE','same38humancallsscoreandselect20configs; nofreshassessment']]
    csv_write(OUT/'05_results/COMPARABILITY_MATRIX.csv',[{'comparison':a,'classification':b,'reason':c} for a,b,c in comparisons])
    comptable=table(['Comparison','Verdict','Evidence/constraint'],comparisons)
    missing=[
        ['Handover participant identities','officialpseudonymousparticipantmapping','cannotcertifyofficialorinnerparticipantdisjointness; F2/QGblocked','externalrecoverypossible','obtainofficialidentitymapping; neverinfer'],
        ['REASSEMBLE original75','50seed123/20261023fits and completeC20F2','one-seedcoverageonly; fusionnotfinalized','newauthorizedworkrequired','review25capandscope; donotresumeautomatically'],
        ['100e pilot','otherfolds/seeds,freshindependentassessment,fullnested100OOF','cannotgeneralizepilotgainorprovefusionbenefit','newauthorizedstudyonly','agreeassessment/selectiondesignfirst'],
        ['Vi full/transfer','V2/V3trainedhead/fusionmetrics','cannotclaimadaptation/transferresults','futureexecutiononly','resolve75fitgate/25capcontractbeforeauthorization'],
        ['MSM/Handover transfer','Rcompletedruns,>=25epochvalidcanonicaldonor','noRtransferperformanceavailable','validator/scientificpolicydecisionrequired','reconcile20vs25withoutchangingduringaudit'],
        ['Historicalfits','unretainedinnerweights/optimizer/scheduler/RNG/exactepochs','notalltrialsloadableorresumable','somefromlogs;othersnotrecoverable','preservepartialstatusandpinnedsourcebanks'],
        ['HistoricalGPUcost','fullallocation/telemetry/extractioncoverage','noglobalexactGPU-hoursorcompute-costtotal','schedulerlogsifretained','requestallocationlogs; donotestimateasmeasured'],
        ['Physicalindependence','MSMtool/workpieceandVi sessionclockmetadata','groupindependenceweakerthanphysical/sessionclaim','publishermetadataifavailable','documentgroupunit; noinventedIDs'],
        ['PHM legacyLOEO','per-fitstates/histories/source-executionhashes/foldlocalnormalizers','aggregateonly; preprocessing/targetconflictslimitcomparison','existinglogsornewseparatecorrectionstudy','retainlegacyresults; reviewdefectseparately'],
        ['FutureHPO','prespecifiedtargetmetric,selectionprotocol,unexposedassessment,budget','cannotchoose/tuneconfirmatorilyyet','researchdecision','independentreviewthenexplicitauthorizedprotocol'],
        ['Auditcoverage','unlogged/deletedfits and unseenexternalartifacts','countsarecompletefordiscoveredevidence,notomniscienthistory','onlyadditionalrecords','supplymissingartifactsandprovenance']]
    missingtable=table(['Experiment','Missing evidence','Impact','Recoverability','Required next action'],missing)
    report('07_scientific_validity/LEAKAGE_AND_SELECTION_AUDIT.md','Leakage and selection audit',"""
Saved-ID checks support disjoint sample roles for25REASSEMBLEplannedjobs and12ViT/V/C/Ajobs; Vi taskgroups and3completeOOFpoolsofinnerassessmentIDs matchoutertrainingpools. AllMSM/Handover savedprediction IDs/targets were joined to their finalnative manifests, including every corruption/role row. Alloriginalcaseoutputhashes and763independentmetric/historychecks passed. SPLIT_AND_LABEL_VERIFICATION.csv records each check and limitation. A passedgroupcontractdoesnotcertifyunknownphysicalparticipant/tool/sessionidentity.

Original REASSEMBLE normalization, branch selection, sigmoid calibration and fusion fitting are training-side nested. Phase1 has disjoint T/V/C/assessment, but later choosing fit3 for100epochs and boundaryvariants using exposedouterAP introduces research-level postselection. Distinguish correct per-fit data isolation from a pristine finalconfirmatorytest. The100e920rowstackbankisgenuinebaseheldoutbutnotfull4inner100OOF. InnerOOF rows are used totrainfusion,soitsperformanceonthoserowsisfusiontraining,notheldoutfusiontest.

MSM nominalgroupOOF is explicitly checked; dateproxysensitivities and unknown tool/workpiece reuse limit stronger independence claims. Externalfitlocalstandardizers/quality moments/corruption scales use fitting rows only. Handover trialdisjoint IDs cannot certify participantdisjointness; the participantOOF gate correctly prevents fused training. The observationwindow amendment is documented,not silently ignored. No artificial participantidentities were reconstructed.

Vi task-disjointness is supported; physicalsession/hardwareclock independence remains unverified. Repeatedtasks are kept together,whereasthethree seeds reuse the sameepisodeassessmentcohort. Labels indicatewhole-episodeoutcome,notvisiblefailuretime. Featurebank4384versusfinal4382 is an IDsubsetjoin,notautomaticallyleakage.

**PHM legacy defect:** `scripts/phm2026/results/sq2_sq3_fusion.py::main` fits one normalizer before LOEO using default `training_split='train'` (fixedEXP-B in minute table). LOEO changes training experiment toF forA/Bassessments. Thus Bheldout data enter its normalization; for Aassessment the scaler usesBvalidation rather thanFtraining. Source `fit_feature_normalizer` is trainonlyforthecanonicalB/A/Fsplit,butnotfoldlocalinthisLOEOscript. The aggregate results must be labeled limited,not silently repaired. Saved latefusion summaries claim targetv3 while some resolvedconfigsdeclarev2; preservebothanddonotinferequivalence. PHM DINO20settings reuse38humancalls; best-of20isoptimisticdevelopment performance.

No evidence in this audit establishes malicious leakage. Missing identity metadata, repeated test exposure and concrete preprocessing-scope mismatches are separately documented. No source,formula,target,splitorhistoricalresultwaschangedtofixappearance.
""",SOURCES['original']+SOURCES['msm']+SOURCES['handover']+SOURCES['vi']+[('scripts/phm2026/results/sq2_sq3_fusion.py','main fixednormalizer before evaluate/train_fold LOEO'),('src/phm2026/preprocessing/timeseries.py','fit_feature_normalizer training_split=train'),('docs/thesis/ANOMALYDINO_RESULT_20260913T215556Z.md','bestof20development caveat')])
    coverage=table(['Dataset/study','Seeds actually represented','Outer/inner coverage','Inference limit'],[
        ['OriginalREASSEMBLE','20260927withdeterministicoffsets; Section2threeoffsetfamilies','5outer/4inner/nested; nullcontrols19','notthePhase1threecanonicalseeds'],
        ['C20','42only;123/20261023deferred','25fits=5×(4inner+1outer)','onefullouterpartition,not3seedstability'],
        ['B/C100andF2pilot','42only','1selectedjob;753assessment','onefold/postselected;920stackbank'],
        ['MSM','42/123/20261023','3outer/2inner,6protocols=54cases','sameheldoutIDsacrossseeds'],
        ['Handover','42/123/20261023','official335/101/151;noeligibleparticipantinnerfolds','noindependentparticipantreplication'],
        ['Vi','42/123/20261023','12jobs/seed/headcondition;3outer/3inner','same4382episodes; deterministicLR/HGB'],
        ['PHM canonical','savedrunseed/config','EXP-Btrain/Aval/Ftest','20runsandprovisionaltarget'],
        ['PHM SQ2/SQ3','1/2/3','3LOEO,aggregateperseed','174callsinferred;foldnormalizationlimitation']])
    report('07_scientific_validity/SEED_AND_FOLD_COVERAGE.md','Seed and fold coverage',coverage+'\nExact per-run seeds, not just seed families, remain in the configuration CSV. Negative-control label permutations and reused checkpoints are labeled. More checkpoint files do not create additional independent folds or datasets. No running task is inferred from stale PID/status metadata.',SOURCES['original']+SOURCES['vi'])
    report('07_scientific_validity/MISSING_EVIDENCE.md','Missing evidence required for independent verification',missingtable+'\nMissing configuration is NOT RECORDED. Suspected defaults are FRAMEWORK DEFAULT — NOT VERIFIED. Missing intervals are NOT AVAILABLE. Planned/blocked training is NOT EXECUTED. Model evidence statuses COMPLETE/PARTIAL/INFERENCE_ONLY/METRICS_ONLY/MISSING_ARTIFACTS describe reproducibility, not scientific superiority. Large raw data/checkpoints/predictions were intentionally not copied, but source paths and hashes are retained. The earlier sealed independent-review package remains unchanged.')
    report('07_scientific_validity/SCIENTIFIC_COMPARABILITY_VERDICT.md','Scientific comparability verdict',comptable+'\nDirect comparability means matched evaluation contracts, not a final recommendation or proof of statistical significance. Comparisons across targets/prevalence/sampling units must stay separate. No final model is selected. Existing uncertainty intervals are conditional on saved models and their resampling unit; repeated seed metrics are descriptive.')
    report('08_future_hpo_readiness/HYPERPARAMETERS_ALREADY_EXPLORED.md','Hyperparameters already explored',tuningtable+'\nUse every saved candidate row rather than assuming untested optimizer freedom. Current evidence does not contain a broad LR×weightdecay×dropout×batch search for fullCNN. Search ranges are historical facts,not proposed next ranges.',SOURCES['original']+SOURCES['vi'])
    report('08_future_hpo_readiness/PARAMETERS_NOT_YET_TUNED.md','Parameters without systematic tuning evidence',"""
For the primary fullCNN, no systematic validation-only sweep of backboneLR,headLR,weightdecay,batch/microbatch,dropout,normalizationpolicy,optimizerfamily,schedule/warmup,framecount oraugmentationstrength was found. The20/100epoch studies are budgets withcheckpointselection; historical16/32frames/final-stage variants are exploratory comparisons,not confirmatoryoptimizerHPO.

MSM/Handover externalLR C,HGB learningrate/depth/regularization,visualheadLR/dropout andqualitygate optimizer settings are fixed recipes. ViLR C,headLR/dropout andgatecapacity/regularization were not systematically searched; ViHGBleafcountwas. OriginalF2 Cwasfixed1;fittingitscoefficientsisnotCsearch. Anchoredlambdaandoriginalgatehiddenwidthalreadyhaveexplicitgrids. OriginalstaticLRChasnestedsearch.

Missing trials are not evidence of optimality. Omitted default fields are not recovered values. This list describes audit evidence; it does not authorize a search or choose candidate ranges,budgetorwinner.
""")
    decisionrows=[['Target/endpoint','Confirmnativefailuredefinition,episode/actionhorizon,primarymetricandboth-classreporting','allcandidates'],['Scientificcomparison','Choosematchedcohort/splits/branchsensor/threshold/calibrationandacceptableobservationaldifferences','familycomparisons'],['Independentassessment','Decidehowtohandleexposedoutertestsandpostselection;preservegrouping','REASSEMBLEpilots/boundary'],['Identitymetadata','ObtainparticipantIDsoracceptblockedfusion;verifyphysicaltool/sessionassumptions','Handover/MSM/Vi'],['Existingpartialscope','Confirm25capversus75gatesand20versus25donorvalidatorcontract','C20/Vi/Rtransfer'],['Reproducibility','Reviewpinnedsourcehashes,retainedstatesandNRdefaults;resolvePHMnormalization/targetconflicts','all/legacy'],['Resourceevidence','Agreefuturebudgetonlyafterprotocol;historicalfullGPU-hoursunavailable','expensivefullCNN'],['Selectionauthority','Independentreviewmustchoosecandidatefamily;audithasnotselected','futureHPO']]
    decisiontable=table(['Information required','Decision to make','Applies to'],decisionrows)
    readiness=table(['Candidate evidence','Available support','Constraint before future decision'],[['OriginalstaticLR/F2','fulloriginalcohort/OOF/coefficient/intervalchain','exposedoutertest;fixedF2CversusLRgrid'],['Frozen/fullCNN','same753paired100pilot plusC20fiveoutervisual','onepairedseed/fold;C20fusionabsent;comparisondesign'],['MSMvisual/sensor/HGB/fusion','all3seeds/3outerandrobustness/sensitivity','nominalvsphysicalgrouping;fixedrecipe'],['Handoverbaselines','officialtest/3seeds/sourcepredictionchain','participantsunknown;fusionblocked'],['ViV1/S3/S2/F2/gates','completefrozen/sensor/meta3seedtaskstudy','failureimbalance;physicalsessionunknown;V2/V3absent'],['Temporal/anchored/qualitylegacy','sourceandmanyfitartifacts','exploratoryselectionandprotocolmismatches'],['PHMmodels','realhistoricalmodel/aggregateartifacts','provisionaltarget;LOEOnormalizationdefect;notnativefailurecomparison']])
    report('08_future_hpo_readiness/MODEL_SELECTION_EVIDENCE_TABLE.md','Evidence available for a later model-selection discussion',readiness+'\n'+decisiontable+'\nNo candidate is selected by this audit. Existing point scores do not by themselves establish a transferable best model.')
    report('08_future_hpo_readiness/HPO_READINESS_AND_CONSTRAINTS.md','HPO readiness and constraints',decisiontable+"""

A defensible future study needs a frozen eligiblemanifest/labelcontract,independentgroupunit,train-onlypreprocessing,explicitinnerselection/calibration/OOFdesign,metric/prevalence/thresholddefinitionandunexposedassessmentortransparentexploratoryscope. Reproducibilityrequirespinneddata/source/initialweights/config,selected-and-laststatesandbudgetaccounting. Participantidentityandcurrentcontrollergatecontradictionsmustberesolvedbeforedependentwork. PHMscientificcorrectionmustbeseparatefromhistoricalpreservation.

These are information requirements, not a newapprovedexperiment. No tuningranges,computeallocationorfinalcandidatearechosen. Retainnegativeandunstableoutcomes,anddistinguishseedvariationfromindependentsampleuncertainty.
""")
    current="""
| Study | Actual state at audit | Completed / intended | Outstanding |
|---|---|---|---|
| REASSEMBLE C20 |STOPPED_AFTER_25_COMPLETED_FITS,approvedcapfinishedNov3 12:23:30UTC (13:23Berlin) |25/25cap,25/75original;seed42,all20epochs |50otherseedfitsdeferred;C20F2notfinalized |
| REASSEMBLE B/C100 |COMPLETE |2/2arms,100epochseach |Noother100epochpairedfolds/seeds |
|100e staticF2 follow-up |COMPLETE pilot |2F2states pluscanonicalbranches/M1–M7 |No4inner100OOF/fullfivefoldstudy |
| MSM P |COMPLETE |54cases/6protocols/3seeds |Rtransfernotexecuted,20epochdonorfails>=25validator |
| Handover P baselines |COMPLETE |3seeds,officialcohort |F2/QGblockedbymissingparticipantIDs;Rnotexecuted |
| Vi frozen/sensors/V1fusion |COMPLETE saved chains |72heads,36LR+108HGBtrials,27fusion/gates |V2/V3trainedmodels0;75fitgateincompatiblewith25cap |
| PHM legacy |Historicalcompleted/partialevidencetypes |Canonicalstatesandaggregatefusions |Provisionaltargets,unretainedstates/epochs,LOEOnormalizationdefect |
| REBOOT/Intel |Feasibility/EDA/sourceonly |Notrainednativeclassifierfound |Notaperformanceclaim |

Noactiveprimaryresearchtrainingwasfoundatauditstart. ViwaitingPIDmetadatawasstale;currentliveness/resourcesnapshotsareinprovenance. Astausfilealonecannotproverunningorpaused. Theauditdoesnotsignal,launch,restartorrescheduleanyjob. Acompleted25capdoesnotmeanfailedfitor75completion. Newexternalprocesseschangesafterthesnapshotarenotcontrolledbythisaudit.
"""
    report('01_executive_overview/CURRENT_EXPERIMENT_STATUS.md','Current experiment status',current,[(base+'/26102026_c_only_20epoch_revision_01/26102026_execution/PHASE1_C_ONLY_STATUS.json','authoritativecompleted25status'),(base+'/26102026_c_only_20epoch_revision_01/02112026_stop_after25fits_01/STOP_AFTER_25_COMPLETE.json','completiontimestamp/hashreceipt')]+SOURCES['vi'])
    report('01_executive_overview/KEY_FINDINGS_AND_LIMITATIONS.md','Key findings and limitations',"""
1. Exactmodelnamesdonotprovearchitecture:primaryvisualisR18vdCNNonly;legacyhybridencoderandPHMdetectorareseparate. FullCtrainseveryexecutedCNNstageandnormaffine,withfixedrunningmoments.
2. Smallsystematicgridsdidoccur;100epochsandseedrepetitionarenotbroadHPO. Recoveredrunrecordsincludecontrols,candidatesandrefits,notthousandsofindependentresearchreplications.
3. C20approved25capisfinished,notstilltraining. Seed42coversallfiveouterfolds;50originalfitsdeferredandC20F2hasnotrun. Vi75completiongateandMSM/Handover>=25epochdonorgateconflictwithcurrent20epoch/25fitstop.
4.100evisualAP.193776→.212585isrealon753matchedactions,onepreselectedfold/seed. F2AP.334977→.349094isapointincreasewithpairedintervalincludingzero. Broadfusionbenefitnotestablished.
5. OriginalstaticF2pooledAP.447299isareal5outerresultwithsensorAP.429392;itisadifferentprotocolfrom100eF2pilot. MSMHGBandViHGB/LRareessentialstrongsensorcomparators.
6. Handoverparticipantsareunknown;officialsplitclaimcannotbeindependentlycertifiedandfusioncorrectlyremainsunexecuted. DonotinventgroupIDs.
7. Vi4382finalepisodesreplace4384provisionalcore;3seedsreuseidenticalassessmentIDs. Failureprevalence.856458requiresboth-classmetrics. Original/donorfeaturecompletionisnotV2/V3modelcompletion.
8. LegacyPHMLOEOusesfixedEXP-Bnormalizationoutsideitschangingtrainingfold,andincludessummary/configtargetversionconflicts. Thesearepreserveddefects,notfixedbyanexport.
9.99.7%TRAININGcomputeactivityforC100and7.77GiBallocatedVRAMaredifferentmeasurements.25.8937hispairedactive-childwall,notpureCtrainingorglobalGPUcompute-hours.
10. Reproducibilityisgraded:state/prediction/metricchainscanbecompletewhileoptimizer/RNGorindependentassessmentismissing. Noarchitectureorwinnerisselected,andnotraining/tuningoccurred.
""")
    # Executive A–H, with complete linked tables and explicit scientific questions.
    essentialconfig=table(['Model','Optimizer','Head/backbone LR','WD','Batch','Max/executed/selected','Trainable','Seed'],[
        ['OriginalfrozenR18head','AdamW','.001/0',.001,128,'10 /source5–10 /inner5or10',114945,'20260927+offsets'],
        ['B100','AdamW','.001/0',.001,8,'100/100/14',114945,42],['C100','AdamW','.001/1e-5',.001,8,'100/100/47',11314913,42],
        ['C20','AdamW','.001/1e-5',.001,8,'20/20/Vselected',11314913,'42only'],['MSM/Handovervisual','AdamW','.001/0',.001,32,'10/10/10',114945,'42/123/20261023'],
        ['Vi frozen','AdamW','.001/0',.001,8,'100/100/VmacroAP',114945,'42/123/20261023'],['StaticLR/F2','L2logistic','notapplicable','Csource', 'allrows','notepochs','d+1','source-specific']])
    fuse=table(['Dataset/protocol','VisualAP','SensorAP','AverageAP','F2AP','QualityAP','Comparability'],[
        ['REASSEMBLEoriginalpooled5',.230658315,.429391869,NR,.447298551,'seecompleteSection2results','same4530;exploratory'],
        ['REASSEMBLE100pilot',.212584503,.327704565,.358533402,.349094220,NR,'same753;singlefold/seed/postselected'],
        ['MSM mean seed pooled3',.298901,.828616,.735594,.756879,'.837418clean/.826521aug','matchedprimary;HGB.901299'],
        ['Handovermeanseed',.771647,.823624,.803102,'NOT EXECUTED','NOT EXECUTED','official151;participantsunknown'],
        ['Vi pooledseed42 macroAP',.495156,.648974,.610399,.628787,.634019,'same4382;HGB.700020;differentmetric']])
    questionanswers="""
### Q1. Did systematic tuning occur?
Yes:smallnestedREASSEMBLEC/hidden/lambdagrids,ViHGBleavesandhistoricalPHMRidge. NobroadfullCNNoptimizerHPOframeworkevidence. SeeTableF/sourceanchors.

### Q2. Original REASSEMBLE visual hyperparameters?
FrozenpinnedR18vdCNN,16frames640RGB/255,mean896→128ReLUdropout.1→1,training-onlystandardizer,AdamWlr.001/wd.001,batch128,clip1,5/10epochinnerAPselection;FP16extraction/FP32head. Betas/epsnotverifiedfororiginalsource-onlyfits.

### Q3. Fully fine-tuned100epoch hyperparameters?
Seed42,freshoriginalCNN/head,allconvs+FrozenBNaffine,FP32,16frames,head.001/backbone1e-5,wd.001,betas(.9,.999),eps1e-8,clip1,micro1/effective8,workers4,cosine100floor.1,noaugmentation/earlystop,all100execute,selectVAPepoch47.

### Q4. Apart from backbone training, what differs?
WithinmatchedB100/C100:backboneLR/trainability/promotedaffineandcached-vs-livecomputation;sharedhead/roles/seed/budget/precision/schedule. Versusoriginalshortfrozen:batch,budget,schedule,featureprecisionandfitting/calibrationrolesalsodiffer. SeeCONFIGURATION_DIFFERENCES.

### Q5. Was the gain caused by full fine-tuning?
Thematchedpilotisolatesthebackboneadaptationconditioncloselyandsupportsitsobservedpointgain,butonepostselectedfold/seeddoesnotestablishgeneraleffect. Original-vs100differencescannotbeuniquelyattributedtofine-tuning.

### Q6. Static sensor and original F2 exact settings?
220stats/22channels/512progresspoints;fitlocalstandardizer,balancedLRC.1/1/10selectedinnerAP,max2000,random0,OOFsigmoid+threshold. F2sigmoid(b+wVpV+wSpS),unweightedC1lbfgs/max2000/random0,nestedOOFcalibratedprobabilities,noextrafusedcalibrator.

### Q7. Were branches/fusion tuned independently?
OriginalsensorCselectionandvisualepochselectionareseparate;F2Cisfixedwhilecoefficientsarefitted. F3/gatewidthandanchoredlambdahavetheirowngrids. ExternalPfixedrecipesarenotindependentoptimizersearches. ViHGBleafselectionisindependentofmeta-fusionfitting.

### Q8. Did100epoch fusion improve?
Completedpilotexists:frozenF2AP.334977351562,fullF2.349094220121,delta+.014116868559,paired95%[-.00077261755,.02908933571]. Pointincrease,inconclusiveinterval,singleexposedfold. C20F2absent.

### Q9. Which results have multiple seeds?
MSM/HandoverandVifrozen/sensors/meta3seeds;originalSection2threeoffsetseedfamilies. C20only42;paired100and100F2only42. OriginalSection1hasonebaseoffsetfamilypluspermutationcontrols. Legacy32diagnosisseedfamiliesareseparatelyrecorded;controlsarenotreplication.

### Q10. Complete reproducibility chains?
Phase1/100selectedstates+history+predictions+metricsandVifrozenchainsareverified. OriginalF2coefficients/OOF/prediction/metricchaincomplete. ExternalPbaselines/fusionshaveinferencechainsbutnotallresumablestates. Manyhistoricalinnerweights/PHMaggregateepochsareabsent. Reproductionfrominitializationwasnotreplayed.

### Q11. Which are comparable?
MatchedoriginalREASSEMBLEbranches/F2,MSMwithinprimaryprotocolandViwithin4382taskprotocol. Paired100andHandoverbaselineshaveexplicitlimits. CrossdatasetAPranking,originalpooledvsselectedpilot,V2/V3unexecutedandPHMpseudodamageversusnativefailureareinvalidcomparisons.

### Q12. What precedes defensible HPO?
Agreelabel/horizon/metric,groupidentityandeligiblemanifest,train-onlynestedselection/calibration/OOF,freshortransparentexploratoryassessment,source/checkpointprovenance;resolveparticipantand75fit/25cap/20vs25barriers;reviewPHMdefectseparately. Nooptimizationislaunched.

### Q13. What candidates have evidence for discussion?
OriginalstaticLR/F2,frozen/fullCNNpilotandC20visual,MSMfixedbranches/HGB/fusion,Handoversupportedbaselines,ViV1/LR/HGB/metaandhistoricaltemporal/gatevariantsallhavegradedartifactevidence. Full/transferViandHandoverfusionlacktrainedresults. Eligibilityfordiscussionisnotselectionofawinner.
"""
    # Undo compact drafting whitespace only in prose: preserve identifiers and numerical tokens.
    # Long exact technical tokens remain intentional; readable replacement is applied below.
    executive=f"""The audit reconstructs actual source/config/state/prediction evidence, with no new training, inferencefeatureextractionorHPO. **32computationalfamilies;7,969effectiveconfigurationrecords;7,929COMPLETEfitrecords(7,755individuallycorroborated+174legacycontrol-flowinferred);40REUSED;4,920binarycandidates/4,438hashes**. Countsincludecontrols/candidates/reconstructionrefitsandarenotindependentscientificreplications. JSONfittedstatesareindexedseparately. **{summary['numeric_metric_records']:,}numericmetricrecords**,includingepochsandintervalendpoints;held-out-onlycountsareinthevalidationinventory. Morethanonequeryrowcanrepresentthesamemodel/metricunderadifferentrecordedaggregation.

## TABLE A — ALL IMPLEMENTED MODELS

{inventory}

## TABLE B — MODEL CONFIGURATIONS

{essentialconfig}

Completeallstudy/modeltable: `03_hyperparameter_configuration/ALL_MODEL_CONFIGURATION_TABLE.md`;everyperrunvalue:ALL_RUN_HYPERPARAMETERS.csv/EFFECTIVE_CONFIGURATIONS.json. Unverifieddefaultsarenotinvented.

## TABLE C — MODEL RESULTS

{display}

Allotherrecordedvariants,seeds/folds/robustnessmetricsremaininthecompleteCSVtables;seeIMPORTANT_RESULTS_TABLE.mdforastandaloneview. Thesearedescriptivewithinprotocolresults,notacrossdatasetranking.

## TABLE D — FROZEN VS FINETUNED CNN

{pairtable}

Checkpointpaths:eacharm'sPHASE1_BEST_MODEL.ptunder`{comp}/26102026_execution/`;exactpaths/hashesandlastslotsinthecheckpointCSV. Pairactive-childwall25.89373h;Ctraining23.96419h. ComputeactivityandVRAMareseparatemeasurements.

## TABLE E — FUSION COMPARISON

{fuse}

## TABLE F — HYPERPARAMETER OPTIMIZATION STATUS

{tuningtable}

## TABLE G — REPRODUCIBILITY

{repro}

## TABLE H — MISSING EVIDENCE

{missingtable}

## Explicit scientific answers

{questionanswers}

No final model or HPO budget is selected. Independentreviewshoulduseexactcohort/split/metric/sourceidentities,notonlythesesummarypointestimates.
"""
    report('01_executive_overview/EXECUTIVE_AUDIT_SUMMARY.md','Executive model/configuration/results audit',executive,SOURCES['original']+sources100+sourcesfusion+SOURCES['msm']+SOURCES['handover']+SOURCES['vi'])
    report('09_reviewer_handoff/RESEARCHER_HANDOFF.md','Independent researcher handoff',"""
Start with README and EXECUTIVE_AUDIT_SUMMARY TablesA–H/Q1–Q13. ReviewCURRENT_EXPERIMENT_STATUSbeforeinterpretingstalecontrollers. UseCOMPLETE_MODEL_INVENTORY/SOURCE_FUNCTION_INDEXtofindactualforwards;perrunconfigurationsinEFFECTIVE_CONFIGURATIONSandPARAMETER_PROVENANCEresolvedefaultsandcheckpointoverrides. Sourcepathsarefirst-classcolumns,notjustconversationreferences.

Forresults,filterdataset,experiment_id,evaluation_scope,seed,fold,protocol,corruption,metric_pathandthresholdbeforeaggregating. Inspectnativeprevalenceandpositiveclass. UseCOMPARABILITY_MATRIXbeforecomparingAP. Thelongmetricfileincludesallepochs/endpoints;summaryfilesretainallnon-epochmetricrows. Sourcepredictionfilesremainintheiroriginalpositions,notduplicated. FilehashesandrunIDsallowindependentjoinchecks. CheckpointbinaryaliasesandJSONmodelstatesareseparateinventories.

Review100epochpairwithitsselected753cohortand920stackbank,notastheoriginal4530pooledstudy. Recomputeonlysavedscoresifdesired;donotimplicitlyfitmissingfusion. ForHandover,readtheofficialrecord,emptyidentityfieldsandparticipantOOFgatebeforeassumingafailureofthetrainedfusionmodel. ForVi,reportbothclassesandnoteV2/V3trainingabsentdespitecompletefeaturebanks. ForPHM,reviewprovisionaltargetandfoldnormalizationdefectbeforeusinglegacyLOEOresults.

TheauditreadCPUmetadata/savedpredictionsonly. Itdidnotaltermodels,labels,rawdata,sourceorresults,anddidnotinterrupt/restartjobs. NoGitcommit/pushwasmadebecauseexistingworktreecontainsmanyunrelatedchangesandtheauditincludeslargegeneratedtables;gitstatussnapshots/HEADarepreserved. Thisfolderisnewreviewevidence,notareplacementforhistoricaloutputs.

Missing_evidenceandHPOreadinessdocumentsseparatefactsfromdecisions. Theindependentreviewmustchoosefuturemetric/protocol/candidatesandbudget;thisauditdoesnot.
""")
    report('README.md','Model configuration audit — reviewer entry point',f"""
This is the requested complete evidence audit of REASSEMBLE,ViFailback,MSMandHandover,withseparatehistoricalPHMcoverage. Userrequestispreservedinprovenance/USER_AUDIT_REQUEST.txt. No training,tuning,featureextraction,modelchangesorjobsignalingwasperformed.

1. Read [executiveoverview](01_executive_overview/EXECUTIVE_AUDIT_SUMMARY.md) forTablesA–H andQ1–Q13.
2. Read [currentstatus](01_executive_overview/CURRENT_EXPERIMENT_STATUS.md) and [limitations](01_executive_overview/KEY_FINDINGS_AND_LIMITATIONS.md).
3. Inspect [architectureinventory](02_model_architecture/COMPLETE_MODEL_INVENTORY.md), [allmodelconfigurations](03_hyperparameter_configuration/ALL_MODEL_CONFIGURATION_TABLE.md), [tuninghistory](03_hyperparameter_configuration/HYPERPARAMETER_TUNING_HISTORY.md).
4. Use [allresults](05_results/ALL_MODEL_RESULTS_SUMMARY.csv), [longmetrics](05_results/ALL_RECORDED_METRICS_LONG.csv), [comparabilitymatrix](05_results/COMPARABILITY_MATRIX.csv),anddataset-specificreports/plots.
5. Review [missing evidence](07_scientific_validity/MISSING_EVIDENCE.md), [reproducibility](04_training_and_checkpoints/REPRODUCIBILITY_ASSESSMENT.md), [validation](09_reviewer_handoff/AUDIT_VALIDATION_RESULTS.md),and [handoff](09_reviewer_handoff/RESEARCHER_HANDOFF.md).

Scope:32explicitcomputationalfamilies,7,969reconstructedfit/configrecords(7,929COMPLETE/40REUSED;174COMPLETElegacycallscontrol-flowinferred),4,920binarycandidatefiles/4,438distinctSHA256s,additionalJSONfittedstatereferences,{summary['numeric_metric_records']:,}numericmetricrecordsand{summary['epoch_history_rows']:,}epochhistoryrows. Controls,candidates,refitsandreusedstatesarenotindependentreplications. Exactheldoutrecordcountsandverificationtotalsareinthevalidationreport.

Largecheckpoints,rawdatasets,cachesandpredictionbanksremainatsourcepaths;thisauditisportableasmetadata/reportsbutfullinference/datareplayrequiresoriginalartifacts. Relativepathsresolvefromrepositoryrootunlessexplicitlyabsoluteexternalprovenance. SourcehashesareinFILE_AND_SOURCE_MANIFEST.csvandcheckpointinventory. NOTRECORDEDandFRAMEWORKDEFAULT—NOTVERIFIEDmeanexactlythosestates. Noabsentresultisfilledwithzero.

Auditutilitiesarein`audit_utilities/`. Theywriteonlyinside thisauditroot;extractorsreadhistoricaloutputsandmetricchecksneverfitmodels. ValidationtestsrunonCPU. Intermediateauditworkingstatesmaybegzip-compressedwithroundtriphashreceipts;requiredCSV/JSONevidenceremainsunabridged. GitHEADattheauditstartwas`eb3888f5d23310aa097dbb1be14605e931190b4a`;thisauditremainsuncommittedandwasnotpushed.
""")
    write(OUT/'provenance/REPORT_COUNTS.json',{'families':len(FAMILIES),'configuration_records':len(runs),'completed_records':summary['completed_training_records'],
        'individual_corroborated_complete':7755,'source_control_flow_inferred_complete':174,'reused_records':40,
        'binary_checkpoint_candidates':4920,'unique_binary_hashes':4438,'json_state_references':len(jsonstates),
        'result_rows':len(results),'held_out_result_rows':sum('HELD-OUT' in r['evaluation_scope'] for r in results),
        'held_out_numeric_metric_records':sum(sum(isinstance(v,(float,int)) and not isinstance(v,bool) for k,v in r.items() if k not in ['seed','fold','held_out_N','positive_count','negative_count','train_N','validation_N','threshold','epoch','csv_row','n_groups','confidence_level','bootstrap_draws']) for r in results if 'HELD-OUT' in r['evaluation_scope']),
        'curated_result_rows':len(curated),'experiment_groups':len(experiments)})
    flush_evidence('REPORT_EVIDENCE_LEDGER.json')
    from polish_reports import polish_all
    polish_all()
    print('REPORTS_WRITTEN',len(list(OUT.rglob('*.md'))),flush=True)


def itertools_group(runs):
    groups=collections.defaultdict(list)
    for r in runs:groups[(r['dataset'],r['experiment_id'])].append(r)
    return sorted(groups.items())


if __name__=='__main__':main()
