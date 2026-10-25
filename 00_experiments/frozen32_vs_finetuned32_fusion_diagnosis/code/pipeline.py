"""Sequential paired folds; immutable canonical sensors; no assessment-based selection."""
import datetime as dt
import fcntl
import os
import signal
import subprocess
import time
import numpy as np
import pandas as pd
from common import *
install_prior_primitives()
from data import load_cohort
from branch_fit import visual_fit,fit_folder,request_stop
from fusion import stacker,fused

def canonical_sensor(job):
    base=PRIOR/'fine_tuned_32_frames'/job['fold_name']
    source=base/'assessment_predictions.csv' if job['role']=='outer_assessment' else base/'fusion_training/identified_oof_branch_probabilities.csv'
    block=csv(source);done=read(PRIOR/'sensor_reference'/job['fold_name']/job['role']/'complete.json')
    block=block[block.sensor_fit_id==done['fit_id']].copy()
    frame=load_cohort();expected=frame.iloc[job['predict']].sample_id.tolist()
    assert set(block.sample_id)==set(expected) and not block.sample_id.duplicated().any()
    block=block.set_index('sample_id').loc[expected].reset_index()
    return block[['sample_id','raw_sensor_logit','p_sensor','sensor_fit_id']],{'manifest':str((PRIOR/'sensor_reference'/job['fold_name']/job['role']/'complete.json').relative_to(REPO)),
        'fit_id':done['fit_id'],'canonical_probability_source':str(source.relative_to(REPO)),'canonical_source_sha256':sha(source)}

def merge_sensor(pred,job):
    sensor,identity=canonical_sensor(job)
    out=pred.merge(sensor,on='sample_id',validate='one_to_one',sort=False)
    assert len(out)==len(pred) and out.sample_id.tolist()==sensor.sample_id.tolist()
    assert np.array_equal(out.p_sensor.to_numpy(),sensor.p_sensor.to_numpy())
    return out,identity

def condition_fold(seed,condition,foldjobs,features,frame):
    final=next(j for j in foldjobs if j['role']=='outer_assessment');fold=final['fold_name']
    dest=ROOT/f'seed_{seed}'/condition/fold;dest.mkdir(parents=True,exist_ok=True)
    donefile=dest/'condition_complete.json'
    if donefile.exists():
        done=read(donefile);assert sha(dest/'assessment_predictions.csv')==done['assessment_sha256'];return
    pieces=[];lineage=[]
    for job in [j for j in foldjobs if j['role']!='outer_assessment']:
        pred,manifest=visual_fit(seed,condition,job,frame,features)
        z,sensor=merge_sensor(pred,job);pieces.append(z)
        lineage.append({'role':job['role'],'visual_fit_id':manifest['fit_id'],'sensor':sensor})
    oof=pd.concat(pieces,ignore_index=True);expected=set(frame.iloc[final['T']].sample_id)
    assert set(oof.sample_id)==expected and not oof.sample_id.duplicated().any()
    assert not set(oof.recording_id)&set(final['outer_E_recordings'])
    if seed==42 and condition=='finetuned32_two_epochs':
        old=PRIOR/'fine_tuned_32_frames'/fold
        previous=csv(old/'fusion_training/identified_oof_branch_probabilities.csv')
        a=oof.sort_values('sample_id').reset_index(drop=True);b=previous.sort_values('sample_id').reset_index(drop=True)
        assert a.sample_id.equals(b.sample_id) and np.max(np.abs(a.p_visual-b.p_visual))<1e-14
        assert np.array_equal(a.p_sensor,b.p_sensor)
        oof=previous;f2=read(old/'F2_stacker.json');assert f2['feature_columns']==['p_visual','p_sensor']
        model=f2['model'];stacker_id=f2['fit_id'];stacker_reuse={'source':str((old/'F2_stacker.json').relative_to(REPO)),'sha256':sha(old/'F2_stacker.json')}
    else:
        model=stacker(oof[['p_visual','p_sensor']].to_numpy(),oof.failure.to_numpy(int))
        stacker_id=signature({'seed':seed,'condition':condition,'fold':fold,'OOF_ids':oof.sample_id.tolist(),'model':model,'lineage':lineage});stacker_reuse=None
    save_csv(dest/'oof_branch_predictions.csv',oof)
    pred,manifest=visual_fit(seed,condition,final,frame,features);out,sensor=merge_sensor(pred,final)
    if seed==42 and condition=='finetuned32_two_epochs':
        old=csv(PRIOR/'fine_tuned_32_frames'/fold/'assessment_predictions.csv')
        assert out.sample_id.tolist()==old.sample_id.tolist()
        assert np.max(np.abs(out.p_visual-old.p_visual))<1e-14 and np.array_equal(out.p_sensor,old.p_sensor)
        out=old.copy();out['p_F2']=out.p_fused
    else:out['p_F2']=fused(out[['p_visual','p_sensor']].to_numpy(),model)
    out['p_uniform']=.5*out.p_visual+.5*out.p_sensor
    out['seed_family']=seed;out['condition']=condition;out['fold_name']=fold;out['model_epochs']=2;out['threshold']=.5;out['stacker_fit_id']=stacker_id
    assert np.max(np.abs(fused(out[['p_visual','p_sensor']].to_numpy(),model)-out.p_F2))<1e-12
    assert np.array_equal(out.p_uniform.to_numpy(),.5*out.p_visual.to_numpy()+.5*out.p_sensor.to_numpy())
    save_csv(dest/'assessment_predictions.csv',out)
    uniform_path=ROOT/f'seed_{seed}'/'uniform_fusion'/condition/fold
    f2_path=ROOT/f'seed_{seed}'/'f2_fusion'/condition/fold
    keys=['sample_id','recording_id','segment_id','failure','action','fold_name','condition','seed_family','p_visual','p_sensor','visual_fit_id','sensor_fit_id']
    save_csv(uniform_path/'assessment_predictions.csv',out[keys+['p_uniform']])
    save_csv(f2_path/'assessment_predictions.csv',out[keys+['p_F2']])
    write(f2_path/'model.json',{'fit_id':stacker_id,'model':model,'feature_columns':['p_visual','p_sensor'],'training_sample_ids':oof.sample_id.tolist(),
        'training_role':'inner OOF inputs; F2 performance on these rows is training performance','no_extra_calibration':True,'reused':stacker_reuse,'lineage':lineage})
    loaded=csv(dest/'assessment_predictions.csv');assert np.array_equal(loaded.p_sensor.to_numpy(),out.p_sensor.to_numpy())
    write(donefile,{'seed':seed,'condition':condition,'fold':fold,'assessment_sha256':sha(dest/'assessment_predictions.csv'),
        'OOF_sha256':sha(dest/'oof_branch_predictions.csv'),'stacker_fit_id':stacker_id,'sensor':sensor,'branch_fit_manifest':str((fit_folder(seed,condition,final)/'complete.json').relative_to(STUDY)),
        'uniform_arithmetic_checked':True,'F2_arithmetic_checked':True,'no_assessment_rows_in_stacking':True,'rows':len(out)})
    event('CONDITION_COMPLETE',last_condition={'seed':seed,'condition':condition,'fold':fold},active_fit=None)

def admit_new_seed():
    estimate=read(ROOT/'provenance/runtime_estimate.json');now=dt.datetime.now(dt.timezone.utc)
    remaining=(dt.datetime.fromisoformat(clock()['training_cutoff_utc'])-now).total_seconds()
    needed=estimate['conservative_new_seed_finetuning_seconds']+estimate['new_frozen_fits_allowance_seconds']/2
    decision={'utc':utc(),'training_seconds_remaining':remaining,'estimated_complete_matched_seed_seconds':needed,'admitted':needed<=remaining,
        'report_reserve_seconds':7200,'policy':'Whole five-fold matched new seed required; fixed epochs/folds/architecture; no automatic extension'}
    write(ROOT/'provenance/new_seed_admission.json',decision)
    if not decision['admitted']:raise StopStudy('PARTIAL_NEW_SEED: complete matched new seed not admitted within budget')

def run():
    lock=(ROOT/'writer.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    signal.signal(signal.SIGTERM,request_stop);signal.signal(signal.SIGINT,request_stop)
    assert read(ROOT/'checks/focused_tests.json')['passed']
    assert read(ROOT/'checks/reuse_and_input_checks.json')['passed'];guard()
    gpu_pids=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip().splitlines()
    assert all(not p.strip() or int(p.strip())==os.getpid() for p in gpu_pids),'ANOTHER_SCIENTIFIC_GPU_JOB_IS_RUNNING'
    for name in ['cohort_and_frames.json','fit_partitions.json']:
        assert sha(STUDY/'data_manifests'/name)==sha(PRIOR/'data_manifests'/name)
    frame=load_cohort();jobs=read(STUDY/'data_manifests/fit_partitions.json')
    features=np.load(PRIOR/'shared_cache/original_features_32.npy',mmap_mode='r',allow_pickle=False)
    record=ROOT/'provenance/fit_code_lock.json';identity={name:sha(STUDY/'code'/name) for name in ['common.py','data.py','branch_fit.py','pipeline.py']}
    if record.exists():assert read(record)==identity
    else:write(record,identity)
    event('RUNNING',pid=os.getpid(),reused_fits=25,seed_families=[42,20261023])
    status='COMPLETE'
    try:
        for seed in [42,20261023]:
            if seed==20261023 and not all((ROOT/f'seed_{seed}'/c/f'fold_{i:02}'/'condition_complete.json').exists() for c in CONDITIONS for i in range(1,6)):
                if not (ROOT/'provenance/new_seed_admission.json').exists():admit_new_seed()
                else:assert read(ROOT/'provenance/new_seed_admission.json')['admitted']
            for outer in range(5):
                group=[j for j in jobs if j['outer_fold_original']==outer]
                for condition in CONDITIONS:condition_fold(seed,condition,group,features,frame)
                event('PAIRED_FOLD_COMPLETE',last_paired_fold={'seed':seed,'fold':f'fold_{outer+1:02}'})
    except StopStudy as exc:
        status='PARTIAL_NEW_SEED';write(ROOT/'provenance/stop_receipt.json',{'utc':utc(),'reason':str(exc),'status':status});event(status,stop_reason=str(exc))
    except Exception as exc:
        status='BLOCKED';write(ROOT/'provenance/error_receipt.json',{'utc':utc(),'type':type(exc).__name__,'error':str(exc)});event(status,error=str(exc));raise
    finally:
        # Report completed matched coverage even when a fit is interrupted. No new training is started by reporting.
        if (STUDY/'code/analysis.py').exists():
            from analysis import report
            report(status)
        else:event('TRAINING_FINISHED_REPORT_PENDING',training_status=status)

