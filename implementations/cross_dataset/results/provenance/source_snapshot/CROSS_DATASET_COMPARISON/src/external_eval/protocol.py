"""Predeclare fixed comparisons before any held-out score is computed."""
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path[:0]=['src','MSM/99_preserved_previous_work/MILLING_DATASET/source','CROSS_DATASET_COMPARISON/src']
from msm.splits import nested_plan,grouped_plan
from external_eval.io import write_json,sha,utc


def core():
    old=json.loads(Path('MILLING DATASET/configs/stage3_protocol.json').read_text())
    return {'version':'EXTERNAL-REASSEMBLE-EVALUATION-v1','freeze_utc':utc(),
        'seeds':[42,123,20261023],'split_seed':42,'outer_folds':3,'inner_folds':2,
        'initializations':['P','R_if_canonical_complete'],
        'pretrained_revision':old['visual']['revision'],'msm_stage3_configuration':old,
        'visual':old['visual'],'sensor':{'classifier':'balanced L2 logistic C1 lbfgs max_iter2000; training-only standardization'},
        'strong_sensor':{'kind':'HistGradientBoostingClassifier','learning_rate':.1,'max_iter':100,'max_leaf_nodes':15,
            'min_samples_leaf':10,'l2_regularization':1.,'early_stopping':False,'sample_weight':'training-only inverse class frequency'},
        'model_names':['prevalence','sensor_logistic','sensor_histgradient','visual','averaging','F2','QG_clean','F2_aug','QG_aug'],
        'optional_single_frame_ablation':'not included; no scope expansion',
        'quality_gate':{'implementation':'reassemble.section2_models.DecisionGate (original quality-only F5 gate); new dataset context adapter',
            'hidden':16,'epochs':40,'learning_rate':.003,'weight_decay':.001,'batch_size':128,'clip_grad_norm':1.,
            'visual_quality':['mean_luminance','luminance_std','log1p_laplacian_variance','dark_fraction','saturated_fraction','retained_frame_fraction'],
            'sensor_quality':'per-channel log1p population std and explicit missing fraction, numerical channels only',
            'context':'training-only standardized quality plus two availability flags; no action/direction/participant/robot metadata',
            'QG_clean':'clean training OOF probabilities/quality only',
            'QG_aug':'clean plus lowest-severity OOF corruptions; fixed epochs, no assessment selection',
            'F2_aug':'exposure-matched augmentation control; original F2 remains clean-OOF only',
            'augmentation_weights':'clean 0.5; seven lowest-severity nonmissing corruption views share 0.5'},
        'corruptions':{
            'gaussian_blur':[1.,2.,4.],
            'brightness_contrast':[[.8,.8],[.5,.5],[.2,.2]],
            'partial_occlusion':[.10,.25,.40],
            'frame_dropout':[4,8,12],
            'sensor_noise':[.1,.5,1.],
            'channel_dropout':[.1,.3,.5],
            'missing_sensor_channels':[.1,.3,.5],
            'missing_modality':['visual','sensor'],
            'random_seed':20261027,
            'video_policy':'real RGB pixels within the resized image content, before CNN, padding unchanged; all severities fixed',
            'sensor_noise_policy':'noise added to actual interval measurements, using pooled RAW training-partition channel SD; recompute fixed statistics',
            'channel_dropout_policy':'deterministically chosen channels become all zero measurements; recompute statistics',
            'missing_channels_policy':'explicitly missing channels; replace their statistics with CLEAN training-partition feature means; masks sent only to gate',
            'frame_dropout_policy':'omit deterministic native frames; pool the retained cached per-frame embeddings (exact frozen-CNN equivalence)',
            'missing_modality_policy':'unavailable unimodal predictions are NA; average/F2/gates use explicitly named deterministic available-branch fallback; no fabricated branch probability'},
        'metrics':['AP','AUROC','F1','precision','recall','balanced_accuracy','specificity','TN','FP','FN','TP','Brier','log_loss','prevalence'],
        'threshold':.5,'model_selection':'fixed final epoch; no search, early stopping, calibrator or test-dependent threshold',
        'bootstrap':{'replicates':2000,'seed':20261027,'cluster':'group, paired model differences; average seeds descriptively, not independent observations'},
        'inference_precision':'FP32','cnn_microbatch':4,'cpu_threads':1,'gpu_process_cap_mib':2048,'gpu_free_reserve_mib':3072,
        'source_R':{'arm':'C_full_finetuned16','seed':42,'outer_fold':0,'role':'outer_assessment','job_index':4,
            'folder':'26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_execution/26102026_main_run_01/26102026_seed42_C_full_finetuned16_outer1_outerassessment'},
        'architectural_claims':'architecture portability and learned-weight transfer are separate; no fine optical anomaly visibility assumed'}


def freeze_msm(settings):
    root=Path('MSM');frame=pd.read_csv(root/'03_processed_model_inputs/final_sample_manifest.csv')
    plans={}
    for target,keep in [('primary',np.ones(len(frame),bool)),('exclude_label2',frame.native_label!=2)]:
        f=frame.loc[keep].reset_index(drop=True)
        for grouping in ['group_id','machine_date_group','calendar_date_group']:
            g=f.copy();g['group_id']=g[grouping]
            plan=nested_plan(g,3,2,42)
            key=target+'__'+grouping
            plans[key]={'target':target,'grouping':grouping,'sample_ids':f.sample_id.tolist(),'plan':plan,'confirmatory_role':'primary frozen nominal' if key=='primary__group_id' else 'predeclared sensitivity'}
    config={**settings,'dataset':'MSM','primary_target':'native 1 vs 0/2','sensor_channels':settings['msm_stage3_configuration']['sensor']['channels'],
        'sensor_statistics':settings['msm_stage3_configuration']['sensor']['statistics'],
        'primary_grouping':'group_id','strict_sensitivities':['machine_date_group','calendar_date_group'],
        'grouping_limitation':'Nominal experiments and filename-date proxies; physical tools/workpieces across dates unresolved; no claim of proven independent physical sessions',
        'visibility_policy':'No new label-dependent visual filtering; technically valid coarse camera context; report occlusion limitation',
        'sample_manifest_sha256':sha(root/'03_processed_model_inputs/final_sample_manifest.csv'),
        'prior_labeled_inspection':'Ten matched cuts from five groups were shown to researcher; review crops are not CNN inputs; all primary settings preserve frozen Stage 3 definition',
        'new_cnn_crops':False}
    write_json(root/'04_experiment_protocol/experiment_config.json',config)
    write_json(root/'03_processed_model_inputs/split_manifests/frozen_splits.json',plans)
    # Direction-specific gates are diagnostic only; direction is never an ordinary predictor.
    controlled={}
    for direction,g in frame.groupby('direction'):
        for label2 in [False,True]:
            f=g.loc[g.native_label!=2].copy() if label2 else g.copy();f=f.reset_index(drop=True)
            try:nested_plan(f,3,2,42);passed=True;reason='passes fixed three outer/two inner class/group gates'
            except ValueError as e:passed=False;reason=str(e)
            controlled[direction+('__exclude2' if label2 else '__primary')]={'intervals':len(f),'positive':int(f.target.sum()),'groups':f.group_id.nunique(),
                'positive_groups':f.loc[f.target==1].group_id.nunique(),'passed':passed,'reason':reason}
    write_json(root/'02_labels_and_alignment/direction_controlled_feasibility.json',controlled)
    print('MSM fixed plans frozen:',len(plans))


def main():
    settings=core()
    shared=Path('CROSS_DATASET_COMPARISON/configs/frozen_core.json')
    if shared.exists():settings=json.loads(shared.read_text())
    else:write_json(shared,settings)
    freeze_msm(settings)


if __name__=='__main__':main()
