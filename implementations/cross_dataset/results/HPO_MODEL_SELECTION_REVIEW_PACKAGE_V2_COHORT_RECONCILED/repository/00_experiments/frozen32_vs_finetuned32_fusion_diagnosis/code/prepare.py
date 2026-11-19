"""Targeted reuse checks for this study, not a repeat of earlier experiment suites."""
from pathlib import Path
import datetime as dt
import importlib.metadata
import os
import subprocess
from common import *

def prepare():
    import numpy as np
    old=read(PRIOR/'config/resolved_config.json');lock=read(PRIOR/'provenance/scientific_fit_lock.json')
    cfg={k:old[k] for k in ['weights_dir','checkpoint_revision','head_lr','final_stage_lr','weight_decay','gradient_clip','effective_batch_segments','microbatch_segments','precision','rescale_factor','normalizer_std_floor','head','temporal_pooling','augmentation','sensor_C','fusion_C','max_iter','threshold','evaluation_seed']}
    cfg.update(protocol='FROZEN32-FT32-MATCHED2-SEEDS2-FUSION-DIAGNOSIS-v1',seeds=[42,20261023],frames=32,epochs=2,
        conditions=list(CONDITIONS),cpu_threads=4,loader_workers=2,prediction_batch_segments_finetuned=2,
        pixel_cache_cap_bytes=0,pixel_RAM_cap_bytes=0,minimum_free_bytes=10*1024**3,host_memory_ceiling_bytes=32*1024**3,
        new_storage_cap_bytes=8*1024**3,bootstrap_replicates=2000,probability_replay_tolerance=1e-5,
        predeclared_cost_multiplier=1.15,historical_Task4='EXCLUDED',equal_budget='epochs and action passes; not compute',
        fixed_sensor='Original 25 fit-specific models/calibrators/probabilities reused for both visual arms and seeds',
        calibration='Same fixed recording-disjoint G/C memberships as seed42; only visual training role seed changes',
        source_study=str(PRIOR.relative_to(REPO)),source_primitives=['visual_model.py','fusion.py','pixel_access.py','fast_input.py'],
        scheduler='none; constant head1e-3/final-stage1e-5',head_checkpoint_policy='Retain compact models and per-fit last optimizer state; no new cleanup of historical artifacts',
        classification='completed-action failure classification, not online early warning',sensor_refit_allowed=False)
    if (STUDY/'resolved_config.json').exists():assert read(STUDY/'resolved_config.json')==cfg
    else:write(STUDY/'resolved_config.json',cfg)
    hashes={};receipts=[]
    for rel,key in [('data_manifests/cohort_and_frames.json','cohort'),('data_manifests/fit_partitions.json','partitions'),('shared_cache/frozen_features_complete.json','feature_metadata'),('provenance/original_pretrained_identity.json','original_pretrained_identity'),('provenance/runtime_environment.json','runtime_identity')]:
        assert sha(PRIOR/rel)==lock[key],('IDENTITY_MISMATCH',rel)
        target=STUDY/rel if rel.startswith('data_manifests/') else STUDY/'existing_evidence'/Path(rel).name
        target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists():target.write_bytes((PRIOR/rel).read_bytes())
        assert sha(target)==lock[key];hashes[str((PRIOR/rel).relative_to(REPO))]=lock[key]
    write(STUDY/'existing_evidence/scientific_fit_lock.json',lock)
    target=ROOT/'provenance/original_pretrained_identity.json'
    if not target.exists():target.write_bytes((PRIOR/'provenance/original_pretrained_identity.json').read_bytes())
    original_weights=read(target)
    for name,m in original_weights['weights'].items():assert sha(REPO/cfg['weights_dir']/name)==m['sha256']
    features=read(PRIOR/'shared_cache/frozen_features_complete.json')
    feature_path=PRIOR/'shared_cache/original_features_32.npy';assert sha(feature_path)==features['hashes']['shared_cache/original_features_32.npy']
    hashes[str(feature_path.relative_to(REPO))]=sha(feature_path)
    source=read(STUDY/'data_manifests/cohort_and_frames.json');jobs=read(STUDY/'data_manifests/fit_partitions.json')
    prior_checks=read(PRIOR.parent/'fine_tuning_diagnostics_01/provenance/input_manifest.json')
    for fold in [f'fold_{i:02}' for i in range(1,6)]:
        for rel in ['assessment_predictions.csv','fusion_training/identified_oof_branch_probabilities.csv','F2_stacker.json']:
            path=PRIOR/'fine_tuned_32_frames'/fold/rel;key=str(path.relative_to(REPO))
            assert sha(path)==prior_checks[key]['sha256'],('REUSED_CANONICAL_BANK_DRIFT',key)
            hashes[key]=sha(path)
    assert len(source)==4530 and sum(r['failure'] for r in source)==509 and len({r['recording_id'] for r in source})==148
    assert len(jobs)==25 and all(len(r['frames32'])==len(set(r['frames32']))==32 for r in source)
    for row in {r['video_path']:r for r in source}.values():
        st=(REPO/row['video_path']).stat();assert (st.st_size,st.st_mtime_ns)==(row['video_bytes'],row['video_mtime_ns'])
    for job in jobs:
        assert role_seed(42,job)==job['seed']
        sets={key:{source[i]['recording_id'] for i in job[key]} for key in ['G','C','predict']}
        assert not sets['G']&sets['C'] and not sets['G']&sets['predict'] and not sets['C']&sets['predict']
        folder=PRIOR/'fine_tuned_32_frames'/job['fold_name']/('outer_assessment' if job['role']=='outer_assessment' else 'fusion_training/'+job['role'])/'visual_fit'
        done=read(folder/'complete.json')
        assert done['job']==job and done['seed']==job['seed'] and done['epochs_complete']==2 and done['frames']==32
        assert done['identities']==lock and done['final_stage_trainable'] and done['replay']['passed']
        assert sha(folder/'model.pt')==done['model_sha256'] and sha(folder/'identified_branch_predictions.csv')==done['predictions_sha256']
        for name in ['complete.json','calibrator.json','full_fit_weight_checks.json','learning_curve.csv','model.pt','identified_branch_predictions.csv']:
            hashes[str((folder/name).relative_to(REPO))]=sha(folder/name)
        sensor=PRIOR/'sensor_reference'/job['fold_name']/job['role'];sd=read(sensor/'complete.json')
        assert sd['job']==job and sha(sensor/'identified_branch_predictions.csv')==sd['predictions_sha256']
        prediction=csv(sensor/'identified_branch_predictions.csv');expected=[source[i]['sample_id'] for i in job['predict']]
        assert prediction.sample_id.tolist()==expected and prediction.failure.tolist()==[source[i]['failure'] for i in job['predict']]
        for name in ['complete.json','model_and_calibrator.json','identified_branch_predictions.csv']:
            hashes[str((sensor/name).relative_to(REPO))]=sha(sensor/name)
        frozen=PRIOR/'frozen_32_frames'/job['fold_name']/('outer_assessment' if job['role']=='outer_assessment' else 'fusion_training/'+job['role'])/'visual_fit'
        assert read(frozen/'complete.json')['epochs_complete']==5
        assert {p.name for p in frozen.glob('*.pt')}=={'model.pt'},'Inspect potential additional frozen checkpoint before reuse decision'
        receipts.append({'fold':job['fold_name'],'role':job['role'],'fine_tuned42':'REUSE_VERIFIED_TWO_EPOCH_FIT','fine_tuned42_manifest':str((folder/'complete.json').relative_to(REPO)),
            'fine_tuned42_fit_id':done['fit_id'],'sensor_fit_id':sd['fit_id'],'sensor_probability_sha256':sd['predictions_sha256'],
            'frozen42':'NEW_TWO_EPOCH_FIT_REQUIRED; only final five-epoch state retained','new_seed':'Both arms new, memberships and sensor fixed',
            'partition_seed':job['seed'],'new_training_seed':role_seed(20261023,job)})
    runtime=read(PRIOR/'provenance/runtime_environment.json')
    for p,v in runtime['packages'].items():assert importlib.metadata.version(p)==v,('PACKAGE_VERSION_DRIFT',p)
    assert os.environ.get('CUBLAS_WORKSPACE_CONFIG')==runtime['CUBLAS_WORKSPACE_CONFIG']
    costs=csv(PRIOR/'comparison/fit_costs_and_parameters.csv');costs=costs[costs.condition=='fine_tuned_32_frames']
    historical=float((costs.training_wall_seconds+costs.C_prediction_seconds+costs.V_prediction_seconds+costs.full_pixel_replay_seconds).sum())
    estimate={'historical_25_fits_seconds':historical,'conservative_new_seed_finetuning_seconds':historical*1.15,
        'new_frozen_fits_allowance_seconds':900,'reporting_reserved_seconds':7200,'basis':'Existing final32-frame two-epoch training, C/V predictions and compact replay; multiplier1.15; all25new FT fits required',
        'new_visual_fits':75,'reused_visual_fits':25,'sensor_fits_new':0,'new_F2_fits_planned':15,'reused_F2_fits':5,
        'admission':'Reassess immediately before new seed; do not start if whole matched seed plus reserve cannot fit'}
    write(STUDY/'data_manifests/reuse_inventory.json',receipts);write(STUDY/'data_manifests/input_hashes.json',hashes)
    write(ROOT/'checks/reuse_and_input_checks.json',{'passed':True,'reused_fits':25,'sensor_roles':25,'frame_keys':4530,'recordings':148,'unchanged_memberships':True,'unchanged_source_primitives':True,'fit_models_and_predictions_hash_verified':True,'old_replays_reused_not_rerun':True})
    write(ROOT/'provenance/runtime_estimate.json',estimate)
    install_prior_primitives();import torch
    assert torch.version.cuda==runtime['torch_cuda'] and torch.backends.cudnn.version()==runtime['cudnn_version']
    write(ROOT/'provenance/runtime_environment.json',runtime)
    print(json.dumps(estimate,indent=2))
    event('PREPARED',reused_fits=25,expected_new_fits=75,new_fits_completed=read(STUDY/'STATE.json').get('new_fits_completed',0))

