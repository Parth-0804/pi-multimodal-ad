"""Idempotent orchestrator: gates -> cached CNN -> full fits -> robustness/reports.

The two datasets have independent admission paths. Existing owned extraction jobs
are monitored rather than duplicated. No unrelated process is signaled.
"""
import argparse
import fcntl
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from external_eval.io import write_json,sha,utc

PYTHON='ma_thesis_env/bin/python'
ENV={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','CUBLAS_WORKSPACE_CONFIG':':4096:8',
     'PYTHONPATH':'src:MSM/99_preserved_previous_work/MILLING_DATASET/source:CROSS_DATASET_COMPARISON/src'}
HANDOVER_ROOT=Path('HANDOVER/experiments/common_support_v2')


def owned_running(stage,root,condition='P'):
    """Match exact Python argv of this evaluation only; no signals or broad logs."""
    import psutil
    for p in psutil.process_iter(['name']):
        if p.info['name'] not in ['python','python3']:continue
        try:cmd=p.cmdline()
        except (psutil.NoSuchProcess,psutil.AccessDenied):continue
        if '-m' not in cmd:continue
        module=cmd[cmd.index('-m')+1]
        if module=='external_eval.features' and stage=='features':
            if '--dataset' in cmd and cmd[cmd.index('--dataset')+1]==str(root) and cmd[cmd.index('--condition')+1]==condition:return p.pid
        if module=='external_eval.dispatch' and '--stage' in cmd and '--root' in cmd:
            if cmd[cmd.index('--stage')+1]==stage and cmd[cmd.index('--root')+1]==str(root) and cmd[cmd.index('--condition')+1]==condition:return p.pid
    return None


def invoke(argv,log,wait=True):
    log=Path(log);log.parent.mkdir(parents=True,exist_ok=True)
    # New attempt log names avoid overwriting earlier failures.
    if log.exists():log=log.with_name(log.stem+'_'+str(time.time_ns())+log.suffix)
    stream=log.open('x');process=subprocess.Popen(argv,stdout=stream,stderr=subprocess.STDOUT,env=ENV)
    stream.close()
    if wait:
        result=process.wait()
        if result:raise RuntimeError('Stage failed; inspect '+str(log))
    return process


def gpu_features(root,condition):
    done=root/'03_processed_model_inputs/visual_features'/condition/'complete.json'
    if done.exists():return
    if owned_running('features',root,condition):
        print('ATTACHED to existing owned feature job',root,condition,flush=True)
        while not done.exists():
            time.sleep(10)
            if not done.exists() and not owned_running('features',root,condition):raise RuntimeError('Owned feature job stopped before completion: '+str(root))
        return
    invoke([PYTHON,'-B','-m','external_eval.dispatch','--stage','features','--root',str(root),'--condition',condition],root/'logs'/f'{condition}_features_runner.txt')


def source_gate(name):
    config=json.loads(Path('CROSS_DATASET_COMPARISON/configs/frozen_core.json').read_text())
    folder=Path(config['source_R']['folder']);receipt=folder/'PHASE1_FIT_COMPLETE.json'
    info={'utc':utc(),'canonical_folder':str(folder),'receipt_exists':receipt.exists(),'P_not_blocked':True,'R_available':False,
        'source_selection':'Fixed canonical seed42 outer0 outer_assessment job4; never chosen using external test scores.'}
    if receipt.exists():
        sys.path[:0]=['src','MSM/99_preserved_previous_work/MILLING_DATASET/source']
        from msm.transfer import validated_source
        try:
            payload,complete=validated_source(folder,42,4)
            info.update(R_available=True,receipt=complete,checkpoint_sha256=complete['selected_model_sha256'])
        except (ValueError,FileNotFoundError,KeyError,RuntimeError) as exc:
            info.update(reason='Canonical source receipt/checkpoint failed validation; P remains independent.',validation_error=str(exc))
    else:info['reason']='Canonical completed full-backbone checkpoint is absent; active/other-inner/preflight checkpoints are inadmissible.'
    path=Path('CROSS_DATASET_COMPARISON/provenance')/name
    if not path.exists():write_json(path,info)
    return info


def pipeline(skip_reports=False):
    lock=Path('CROSS_DATASET_COMPARISON/provenance/runner.lock');handle=lock.open('a')
    try:fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:raise RuntimeError('A complete-workflow controller is already active')
    if Path('CROSS_DATASET_COMPARISON/provenance/DELIVERY_COMPLETE.json').exists():
        # A completed version is immutable, including its source-availability
        # boundary. A later R source belongs to a separately versioned extension.
        from external_eval.publication import prepare,seal
        from external_eval.leakage import audit
        for root in [Path('MSM'),HANDOVER_ROOT]:
            prepare(root);audit(root)
            for marker in (root/'06_evaluation_results').glob('*_EVALUATION_COMPLETE.json'):
                for case in json.loads(marker.read_text())['cases']:
                    for p,h in case['output_hashes'].items():
                        if sha(p)!=h:raise ValueError('Sealed prediction/metric evidence changed')
        seal();print('REUSED sealed full workflow; raw, cohort, prediction and final-report hashes verified',flush=True);return
    roots=[];blockers={}
    # Reuse completed acquisition and input audits. These paths also work on a
    # restart after an interrupted official download or partial trial audit.
    try:
        if not Path('MSM/02_labels_and_alignment/validation_gate.json').exists():invoke([PYTHON,'-B','MSM/src/validate_inputs.py'],'MSM/logs/runner_input_validation.txt')
        if not Path('MSM/04_experiment_protocol/experiment_config.json').exists():invoke([PYTHON,'-B','-m','external_eval.protocol'],'MSM/logs/runner_protocol.txt')
        roots.append(Path('MSM'))
    except Exception as e:blockers['MSM']=str(e)
    try:
        if not Path('HANDOVER/01_raw_dataset/source_evidence/sample_acquisition.json').exists():invoke([PYTHON,'-B','HANDOVER/src/acquire.py'],'HANDOVER/logs/runner_sample_download.txt')
        if not Path('HANDOVER/02_labels_and_alignment/sample_gate.json').exists():invoke([PYTHON,'-B','HANDOVER/src/validate_sample.py'],'HANDOVER/logs/runner_sample_gate.txt')
        if not Path('HANDOVER/01_raw_dataset/source_evidence/full_acquisition.json').exists():invoke([PYTHON,'-B','HANDOVER/src/acquire.py','--full'],'HANDOVER/logs/runner_full_download.txt')
        if not (HANDOVER_ROOT/'02_labels_and_alignment/validation_gate.json').exists():
            invoke([PYTHON,'-B','HANDOVER/src/validate_full.py','--root',str(HANDOVER_ROOT),'--common-support'],'HANDOVER/logs/runner_common_support.txt')
        roots.append(HANDOVER_ROOT)
    except Exception as e:blockers['HANDOVER']=str(e)
    plan_path=Path('CROSS_DATASET_COMPARISON/configs/execution_plan.json')
    if not plan_path.exists():write_json(plan_path,{'roots':[str(p) for p in roots],'Handover_amendment':'HANDOVER/04_experiment_protocol/COMMON_SUPPORT_AMENDMENT.json',
        'conditions':'P always; canonical R only if completed/validated; no source-performance selection',
        'seeds':[42,123,20261023],'all_predeclared_models_and_robustness':True,'initial_blockers':blockers})
    initial=source_gate('R_source_gate_initial.json');conditions=['P']+(['R'] if initial['R_available'] else [])
    completed_conditions=[]
    def condition_run(condition):
        evaluators=[]
        for root in roots:
            try:
                gpu_features(root,condition)
                done=root/'06_evaluation_results'/f'{condition}_EVALUATION_COMPLETE.json'
                if not done.exists():
                    process=owned_running('evaluate',root,condition)
                    if process:print('ATTACHED to existing owned evaluator',root,condition,flush=True)
                    else:process=invoke([PYTHON,'-B','-m','external_eval.dispatch','--stage','evaluate','--root',str(root),'--condition',condition],root/'logs'/f'{condition}_evaluation_runner.txt',wait=False)
                    evaluators.append((root,process))
            except Exception as e:blockers[str(root)+'_'+condition]=str(e)
        for root,process in evaluators:
            if isinstance(process,int):
                done=root/'06_evaluation_results'/f'{condition}_EVALUATION_COMPLETE.json'
                while not done.exists() and owned_running('evaluate',root,condition):time.sleep(10)
                failed=not done.exists()
            else:failed=process.wait()!=0
            if failed:blockers[str(root)+'_'+condition+'_models']='CPU evaluation failed; inspect attempt logs; completed fits/cases preserved'
        completed_conditions.append(condition)
    for condition in conditions:condition_run(condition)
    # Do not wait for source training. A newly completed canonical receipt can
    # unlock the additional comparison, never block the primary P results.
    later=source_gate('R_source_gate_after_P.json')
    if later['R_available'] and 'R' not in completed_conditions:condition_run('R')
    source_gate('R_source_gate_final.json')
    finished=Path('CROSS_DATASET_COMPARISON/provenance/execution_finished.json')
    if finished.exists():finished=finished.with_name('execution_finished_resume_'+str(time.time_ns())+'.json')
    write_json(finished,{'utc':utc(),'conditions_processed':completed_conditions,'blockers':blockers,
        'no_full_matrix_early_stop':True,'no_unrelated_process_signals':True})
    if not skip_reports:
        for root in roots:
            invoke([PYTHON,'-B','-m','external_eval.dispatch','--stage','reports','--root',str(root)],root/'logs/reports_runner.txt')
        invoke([PYTHON,'-B','-m','external_eval.comparison'],'CROSS_DATASET_COMPARISON/logs/comparison_reports.txt')
    print('FULL WORKFLOW FINISHED',json.dumps(blockers),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--skip-reports',action='store_true');pipeline(parser.parse_args().skip_reports)
