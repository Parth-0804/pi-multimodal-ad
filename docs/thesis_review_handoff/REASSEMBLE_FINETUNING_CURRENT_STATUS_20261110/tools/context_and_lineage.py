"""Current split, source, fusion and controller evidence; read-only."""
import audit as a
from pathlib import Path
import collections,csv,datetime as dt,json,os,psutil,shutil
import numpy as np
import pandas as pd
from scipy.special import expit

SOURCE_FILES=['configs/reassemble/section1.json','configs/reassemble/section1b.json','src/reassemble/section1_models.py','src/reassemble/section1_features.py','src/reassemble/section1b.py',
 str(a.BASE/'26102026_source/phase_model.py'),str(a.BASE/'26102026_source/phase_training.py'),str(a.BASE/'26102026_source/phase_metrics.py'),str(a.BASE/'26102026_source/phase_loader.py'),str(a.BASE/'26102026_source/phase_checkpoint.py'),
 str(a.BASE/'26102026_configuration/PHASE1_CONFIG.json'),str(a.BASE/'26102026_c_only_20epoch_revision_01/26102026_configuration/PHASE1_C_ONLY_CONFIG.json'),str(a.BASE/'26102026_c_only_20epoch_revision_01/26102026_source/c20_train.py'),str(a.BASE/'26102026_c_only_20epoch_revision_01/26102026_source/c20_controller.py'),str(a.BASE/'26102026_c_only_20epoch_revision_01/26102026_source/c20_report.py'),
 str(a.BASE/'26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_source/compare100_train.py'),str(a.BASE/'26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_source/compare100_common.py'),str(a.BASE/'26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_configuration/PHASE1_COMPARISON_CONFIG.json'),
 'parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01/source/visual_model.py',
 '00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/source/training.py','00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/source/fusion.py','00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/config/resolved_config.json',
 '00_experiments/frozen32_vs_finetuned32_fusion_diagnosis/PROTOCOL.md','src/reassemble/additional_improvements/finetune.py','src/reassemble/additional_improvements/models.py',
 str(a.FOLLOW/'src/evaluate.py'),'MSM/99_preserved_previous_work/MILLING_DATASET/source/msm/transfer.py','VIFAILBACK/src/vifailback/resources.py']

def main():
    canonical=a.rows(a.COHORT/'CANONICAL_ACTION_MANIFEST.csv');frame=pd.read_parquet(a.used('runs/reassemble/20260927T154732Z-section1/cohort.parquet'))
    keys=[r['recording_id']+'::'+str(r['segment_id']) for r in canonical]
    native=[str(r.recording_id)+'::'+str(r.segment_id) for r in frame.itertuples()]
    assert native==keys and frame.failure.astype(int).tolist()==[int(r['failure']) for r in canonical]
    plan=a.read(a.BASE/'26102026_evidence/PHASE1_FIT_PLAN.json');selected=a.read(a.BASE/'26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_configuration/PHASE1_SELECTED_JOB.json')
    splits=a.read('runs/reassemble/20260927T154732Z-section1/nested_splits.json')
    original_test=set(splits['folds'][0]['test_recordings']);outer={i for i,r in enumerate(canonical) if r['recording_id'] in original_test}
    assert outer==set(selected['predict']) and len(outer)==753 and len(original_test)==26
    inner=set(selected['original_inner_prediction_indices']);assert len(inner)==920 and not outer&inner
    roles={'T':set(selected['training']),'V':set(selected['validation']),'C':set(selected['C']),'INNER920':inner,'OUTER753':outer}
    assert all(not x&y for n,x in roles.items() for m,y in roles.items() if n<m)
    assert set.union(*roles.values())==set(range(4530))
    for role,k in [('T','training'),('V','validation'),('C','C')]:assert roles[role]==set(plan[2][k])
    subset={'larger_actions':4530,'larger_recordings':148,'larger_failures':509,'smaller_actions':753,'smaller_recordings':26,'smaller_failures':77,
        'strict_subset':True,'smaller_is_original_outer_fold0':True,'inner920_disjoint_from_outer753':True,
        'role_counts':{k:len(v) for k,v in roles.items()},'role_recording_counts':{k:len({canonical[i]['recording_id'] for i in v}) for k,v in roles.items()},
        'stale_prediction_recordings_N':len(selected['prediction_recordings']),'actual_prediction_recordings_N':len(original_test),
        'stale_prediction_recordings_are_inner920':set(selected['prediction_recordings'])=={canonical[i]['recording_id'] for i in inner},
        'plan_sha256':a.sha(a.BASE/'26102026_evidence/PHASE1_FIT_PLAN.json'),'canonical_source_sha256':a.sha('runs/reassemble/20260927T154732Z-section1/cohort.parquet'),
        'nested_split_sha256':a.sha('runs/reassemble/20260927T154732Z-section1/nested_splits.json'),'split_content_declared_sha256':splits['sha256']}
    a.write('support/CURRENT_SUBSET_AND_ROLE_PROOF.json',subset)
    role_rows=[{**r,**{name:i in ids for name,ids in roles.items()}} for i,r in enumerate(canonical)]
    a.table('support/CANONICAL_ACTIONS_AND_SELECTED_ROLES.csv',role_rows)
    a.table('support/ORIGINAL_OUTER_FOLDS.csv',a.rows(a.COHORT/'ORIGINAL_OUTER_FOLDS.csv'))
    a.table('support/EXACT_COHORT_REGISTRY.csv',a.rows(a.COHORT/'COHORT_REGISTRY.csv'))
    # Preserve and classify the additional old five-epoch superseded adaptation.
    extra=a.rows(a.OUT/'support/ADDITIONAL_COMPLETION_RECEIPTS.csv')
    configs=a.rows(a.OUT/'03_COMPLETE_MODEL_CONFIGURATIONS.csv');coverage=a.rows(a.OUT/'04_SEED_FOLD_AND_EPOCH_COVERAGE.csv')
    for e in extra:
        info=a.read(e['receipt']);job=info['job'];rid=str(Path(e['receipt']).parent)
        if any(r['run_id']==rid for r in configs):continue
        row={'run_id':rid,'dataset':'REASSEMBLE','experiment_id':'BOOTSTRAP_SUPERSEDED_FINALSTAGE5','model':info['condition'],
            'configuration_source':str(Path(e['receipt']).parents[5]/'config/resolved_config.json'),'evidence_class':a.V,
            'training_status':'COMPLETE SUPERSEDED INNER FIT; NOT A COMPLETE FIVE-FOLD EXPERIMENT',
            'cnn_scope':'FINAL STAGE + MEAN HEAD','model_seed':info.get('seed',job['seed']),'seed_family':42,'outer_fold_zero_based':job['outer_fold_original'],
            'inner_fold':job['role'],'split_role':job['role'],'executed_epochs':info['epochs_complete'],'selected_epoch':info['epochs_complete'],'max_configured_epochs':5,
            'frame_count':info['frames'],'image_dimensions':'640x640','head_learning_rate':.001,'backbone_learning_rate':1e-5,'optimizer':'AdamW',
            'weight_decay':.001,'betas':'UNKNOWN — framework default not recovered','epsilon':'UNKNOWN — framework default not recovered',
            'effective_batch_size':8,'microbatch_size':1,'gradient_accumulation':8,'precision':'float32','scheduler':'none; fixed5',
            'loss':'G-negative/positive-weighted BCEWithLogits','class_weighting':info.get('positive_weight_from_G',a.U),'dropout':.1,'warmup':'none','augmentation':'none',
            'checkpoint_selection':'fixed final fifth epoch; superseded by distinct two-epoch study','normalization':'G-only fixed feature moments; FrozenBN buffers frozen',
            'head':'896 ->128 ReLU Dropout0.1 ->1','trainable_parameters':8388608+114945,'frozen_parameters':11190112-8388608,
            'TRAIN_N':len(job['G']),'CALIBRATION_N':len(job['C']),'ASSESSMENT_N':len(job['predict']),
            'checkpoint_path':str(Path(e['receipt']).parent/'model.pt'),'history_source':e['receipt'],'initialization':'original pinned pretrained CNN; fresh head',
            'entry_point':'parth_ws_bootstrap/.../run_01/source/training.py (historical source snapshot; resolved original path in source index)'}
        row['configuration_source']='parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01/config/resolved_config.json'
        configs.append(row);coverage.append({k:row.get(k,a.U) for k in coverage[0]})
        cp=a.path(row['checkpoint_path']);assert a.sha(a.used(cp))==info['model_sha256']
        inventory=a.rows(a.OUT/'11_CHECKPOINT_INVENTORY.csv');inventory.append({'run_id':rid,'model':info['condition'],'path':a.rel(cp),'kind':'SUPERSEDED INNER FINAL-STAGE5','bytes':cp.stat().st_size,'sha256':a.sha(cp),'selected_epoch':5,'last_epoch':5,'model_state_available':True,'optimizer_scheduler_RNG':'UNKNOWN; historical recovery separate','verification':a.V});a.table('11_CHECKPOINT_INVENTORY.csv',inventory)
    a.table('03_COMPLETE_MODEL_CONFIGURATIONS.csv',configs);a.table('04_SEED_FOLD_AND_EPOCH_COVERAGE.csv',coverage)
    # F2 coefficient arithmetic against actual branch inputs; original five-fold and CNN100.
    coefficient=[];arithmetic=[]
    for k in range(5):
        p=Path('runs/reassemble/20260927T175336Z-section1b/stacking')/f'outer{k}.json';m=a.read(p)['stacker']
        bank=Path('runs/reassemble/20260927T175336Z-section1b/stacking')/f'outer{k}.npz'
        with np.load(a.used(bank),allow_pickle=False) as z:
            error=float(np.max(abs(expit(z['test_branch_probabilities']@np.array(m['coefficient'])+m['intercept'])-z['p'])))
        assert error<1e-12
        coefficient.append({'experiment':'ORIGINAL_F2','outer_fold':k,'source':a.rel(p),'source_sha256':a.sha(p),'fitted_coefficients':m})
        arithmetic.append({'experiment':'ORIGINAL_F2','fold':k,'max_abs_error':error,'verified':True})
    effective=a.read(a.OLD/'03_hyperparameter_configuration/EFFECTIVE_CONFIGURATIONS.json')
    for r in effective:
        if r['dataset']=='REASSEMBLE' and r['experiment_id'] in ['CNN100_STATIC_SENSOR_F2','LEGACY_VISUAL_ONE_DAY_F2','LEGACY_FROZEN32_F2','LEGACY_ENCODER_F2']:
            info=a.read(r['configuration_source']);coefficient.append({'experiment':r['experiment_id'],'run_id':r['run_id'],'model':r['model'],'source':r['configuration_source'],'source_sha256':a.sha(r['configuration_source']),'saved_fitted_state':info})
    a.write('support/FITTED_F2_COEFFICIENTS_AND_CONFIGS.json',coefficient);a.table('support/F2_DIRECT_ARITHMETIC_VERIFICATION.csv',arithmetic)
    status=a.read(a.BASE/'26102026_c_only_20epoch_revision_01/26102026_execution/PHASE1_C_ONLY_STATUS.json')
    stop=a.read(a.BASE/'26102026_c_only_20epoch_revision_01/02112026_stop_after25fits_01/STOP_AFTER_25_COMPLETE.json')
    run=a.path(a.BASE/'26102026_c_only_20epoch_revision_01/26102026_execution')
    marker_names=['PHASE1_C_ONLY_ALL_COMPLETE.json','PHASE1_C_ONLY_FINAL_METRICS.json']
    markers={n:(run/n).exists() for n in marker_names}
    current={'audit_client_date':'2026-11-10','snapshot_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'status':status,'approved_stop':stop,'terminal_marker_existence':markers,
        'recorded_controller_pid_exists_now':psutil.pid_exists(status['controller_pid']),
        'pid_alone_is_not_process_identity':True,'controller_restarted_or_signalled':False,
        'scheduling_source':'VIFAILBACK/src/vifailback/resources.py expects75-fit completion plus final metrics hash',
        'deferred_seeds':a.read(a.BASE/'26102026_configuration/PHASE1_CONFIG.json')['seeds'][1:]}
    a.write('support/CURRENT_CONTROLLER_AND_COMPLETION_STATUS.json',current)
    index=[]
    for s in SOURCE_FILES:
        p=a.used(s,'executing code/configuration excerpt');target=a.OUT/'source_extracts'/s;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
        index.append({'original_path':s,'audit_copy':str(target.relative_to(a.OUT)),'sha256':a.sha(p),'bytes':p.stat().st_size})
    a.table('support/SOURCE_EXTRACT_INDEX.csv',index)
    # Fresh native epoch histories are complete; other unchanged logs remain identifiable.
    histories=a.rows(a.OLD/'06_dataset_specific/REASSEMBLE/EPOCH_HISTORIES.csv')
    cnnids={r['run_id'] for r in configs if r.get('cnn_scope') not in ['SENSOR / CONTROL / OTHER CONTEXT','FUSION / CACHED VISUAL CONTEXT']}
    histories=[r for r in histories if r['run_id'] in cnnids]
    a.table('support/ALL_CNN_EPOCH_HISTORIES.csv',histories)
    a.table('support/LINEAGE_INPUTS.csv',list(a.INPUTS.values()))
    print(json.dumps({'current_run_records':len(configs),'additional_superseded_inner_fits':len(extra),'CNN_history_rows':len(histories),'source_extracts':len(index),'F2_original_arithmetic_verified':len(arithmetic)}))

if __name__=='__main__':main()
