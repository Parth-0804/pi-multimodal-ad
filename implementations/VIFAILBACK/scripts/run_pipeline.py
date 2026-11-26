#!/usr/bin/env python3
"""Autonomous sequential controller. A file lock prevents duplicate controllers."""
from pathlib import Path
import fcntl,json,os,subprocess,sys,time,traceback,psutil
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from vifailback.common import PROJECT,REPO,config,code_identity,event,provenance,read,sha,utc,write,software_versions


def main():
    c=config();logs=PROJECT/'logs'/c['run_id'];logs.mkdir(parents=True,exist_ok=True)
    with (logs/'pipeline.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        expected=code_identity();receipt=logs/'EXECUTION_PROVENANCE.json'
        if receipt.exists():assert read(receipt)['implementation']==expected,'CODE_DRIFT_REQUIRES_NEW_VERSIONED_RUN'
        else:write(receipt,provenance(c))
        state_path=logs/'PIPELINE_STATUS.json';history=logs/'STAGE_HISTORY.json';completed=read(history) if history.exists() else [];issues=[]
        def status(stage,**extra):
            write(state_path,{'utc':utc(),'stage':stage,'controller_pid':os.getpid(),'completed_stages':completed,**extra})
        def frozen():
            assert code_identity()==expected,'CODE_DRIFT_AFFECTED_STAGE_STOPPED'
            recorded=read(receipt);current=software_versions()
            assert current['python']==recorded['python'] and current['packages']==recorded['packages'],'SOFTWARE_DRIFT_AFFECTED_STAGE_STOPPED'
            from vifailback.reference import identities
            assert identities()==recorded['reused_source'],'REASSEMBLE_SOURCE_DRIFT_AFFECTED_STAGE_STOPPED'
        def stage(name,command,essential=True):
            frozen()
            if any(r['stage']==name and r['returncode']==0 for r in completed):return True
            status(name)
            from vifailback.resources import process_alive
            active=logs/'ACTIVE_CHILD.json'
            if active.exists():
                previous=read(active)
                if process_alive(previous):
                    assert previous['stage']==name,'ANOTHER_OWN_STAGE_IS_STILL_RUNNING'
                    status(name,child_pid=previous['pid'],resuming_controller_wait=True)
                    while process_alive(previous):time.sleep(30)
                    # Re-enter the stage after an orphaned child; completed artifacts
                    # are verified and reused, incomplete fits resume their checkpoint.
            with (logs/(name+'.log')).open('a') as stream:
                attempt_started=time.perf_counter();attempt_utc=utc()
                child=subprocess.Popen(command,cwd=REPO,stdout=stream,stderr=subprocess.STDOUT)
                write(active,{'stage':name,'pid':child.pid,'create_time':psutil.Process(child.pid).create_time(),'command':command})
                status(name,child_pid=child.pid,log=str((logs/(name+'.log')).relative_to(REPO)))
                last_report=time.monotonic()
                while child.poll() is None:
                    if time.monotonic()-last_report>=3600:
                        from vifailback.reporting import publish
                        publish(c,stage=name);last_report=time.monotonic()
                    time.sleep(30)
                code=child.returncode
            completed.append({'stage':name,'started_utc':attempt_utc,'utc':utc(),'wall_seconds':time.perf_counter()-attempt_started,
                              'returncode':code,'pid':child.pid,'command':command});write(history,completed)
            if code:
                message=f'{name}_FAILED_EXIT_{code}; inspect logs/{c["run_id"]}/{name}.log'
                if essential:raise RuntimeError(message)
                issues.append(message);return False
            return True
        worker=[sys.executable,'-B',str(PROJECT/'scripts/worker.py')]
        qcroot=PROJECT/'02_dataset_verification/video_audit/runs'/c['run_id']
        try:
            # The initial acquisition/QC workers may already exist; do not duplicate them.
            status('WAITING_FULL_ACQUISITION_AND_VIDEO_QC')
            from vifailback.resources import process_alive
            while not (qcroot/'ACQUISITION_COMPLETE.json').exists():
                pid=logs/'ACQUISITION_PROCESS.json'
                if not pid.exists() or not process_alive(read(pid)):
                    stage('ACQUISITION_RESUME',[sys.executable,'-B',str(PROJECT/'scripts/acquire_videos.py')])
                    assert (qcroot/'ACQUISITION_COMPLETE.json').exists()
                else:time.sleep(30)
            acquisition=read(qcroot/'ACQUISITION_COMPLETE.json')
            if not acquisition['complete']:
                blocked=[r for r in acquisition['rows'] if r['status'] not in ['ACQUIRED_VERIFIED','VERIFIED_EXISTING']]
                if any('PERMISSION' in r['status'] for r in blocked):raise PermissionError('SOURCE_ACCESS_RESTRICTION; no bypass attempted')
                # Preserve each failed receipt before a transparent retry of exact public source paths.
                for attempt in range(1,4):
                    write(qcroot/f'ACQUISITION_PRIOR_ATTEMPT_{attempt}.json',acquisition)
                    stage(f'ACQUISITION_RETRY_{attempt}',[sys.executable,'-B',str(PROJECT/'scripts/acquire_videos.py')])
                    acquisition=read(qcroot/'ACQUISITION_COMPLETE.json')
                    if acquisition['complete']:break
                    if any('PERMISSION' in r['status'] for r in acquisition['rows']):raise PermissionError('SOURCE_ACCESS_RESTRICTION')
                if not acquisition['complete']:raise RuntimeError('SOURCE_FILES_UNAVAILABLE_AFTER_TRANSIENT_RETRIES')
            while not (qcroot/'VIDEO_QC_COMPLETE.json').exists():
                pid=logs/'VIDEO_QC_PROCESS.json'
                if not pid.exists() or not process_alive(read(pid)):
                    stage('VIDEO_QC_RESUME',[sys.executable,'-B',str(PROJECT/'scripts/audit_videos.py')])
                    assert (qcroot/'VIDEO_QC_COMPLETE.json').exists()
                else:time.sleep(30)
            qc=read(qcroot/'VIDEO_QC_COMPLETE.json')
            # Revisit missing payloads after a successful retry, not confirmed
            # source bitstream defects. Those remain immutable exclusions.
            if any(r.get('technical_category')=='C' for r in qc['cameras']):
                write(qcroot/'VIDEO_QC_PRIOR_PASS.json',qc)
                stage('VIDEO_QC_RECHECK',[sys.executable,'-B',str(PROJECT/'scripts/audit_videos.py')])
            stage('NATIVE_LABEL_VERIFICATION',worker+['--stage','labels'])
            stage('FINAL_COHORT_AND_SPLITS',worker+['--stage','cohort'])
            stage('BLINDED_FULL_TASK_QC_GALLERY',worker+['--stage','qc_gallery'],essential=False)
            stage('SENSOR_FEATURES',worker+['--stage','sensors'])
            sensors_ok=stage('SENSOR_BASELINES',worker+['--stage','baselines'],essential=False)
            stage('ORIGINAL_FROZEN_FEATURES_CPU',worker+['--stage','features','--condition','V1'])
            visual_ok={'V1':stage('FROZEN_CLASSIFIER_100_EPOCHS',worker+['--stage','train','--condition','V1'],essential=False)}
            stage('FROZEN_HIGH_ONLY_ABLATION',worker+['--stage','train','--condition','V1_high_only'],essential=False)
            fusion_ok={'V1':stage('FROZEN_FUSION',worker+['--stage','fusion','--condition','V1'],essential=False) if sensors_ok and visual_ok['V1'] else False}
            stage('FROZEN_REPORTS',worker+['--stage','reports'])
            stage('DONOR_INITIAL_FEATURES_CPU',worker+['--stage','features','--condition','V3'])
            from vifailback.resources import wait_for_gpu
            status('WAITING_REASSEMBLE75_COMPLETE_AND_GPU_IDLE');wait_for_gpu(c)
            stage('GPU_BENCHMARK',[sys.executable,'-B',str(PROJECT/'scripts/benchmark_gpu.py')])
            for condition in ['V2','V3']:
                visual_ok[condition]=stage(condition+'_FULL_CNN_100_EPOCHS',worker+['--stage','train','--condition',condition,'--device','cuda'],essential=False)
                fusion_ok[condition]=stage(condition+'_FUSION',worker+['--stage','fusion','--condition',condition],essential=False) if sensors_ok and visual_ok[condition] else False
            for condition in ['V1','V2','V3']:
                if not fusion_ok[condition]:continue
                stage(condition+'_MATCHED_META_AUGMENTATION',worker+['--stage','augmentation','--condition',condition,'--device','cuda'],essential=False)
                stage(condition+'_ROBUSTNESS',worker+['--stage','robustness','--condition',condition,'--device','cuda'],essential=False)
                stage(condition+'_SAVED_PREDICTION_GALLERY',worker+['--stage','gallery','--condition',condition],essential=False)
            stage('INDEPENDENT_RESULT_VERIFICATION',worker+['--stage','verify'])
            from vifailback.reporting import publish
            final='PARTIAL_WITH_BLOCKERS' if issues else 'COMPLETE'
            frozen();publish(c,stage=final,error='; '.join(issues) or None,with_uncertainty=True);status(final,issues=issues)
            from vifailback.git_handoff import capture
            capture(c,commit=True)
            event(c,'PIPELINE_FINISHED',status=final,scientific_claims_require_report_review=True)
        except BaseException as error:
            status('BLOCKED_OR_INTERRUPTED',error=repr(error),traceback=traceback.format_exc())
            from vifailback.reporting import publish
            publish(c,stage='BLOCKED_OR_INTERRUPTED',error=str(error))
            raise


if __name__=='__main__':main()
