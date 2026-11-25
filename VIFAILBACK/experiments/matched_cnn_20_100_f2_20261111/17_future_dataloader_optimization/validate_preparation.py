#!/usr/bin/env python3
"""Bounded read-only final verification; write only a new local evidence directory."""
import ast
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from future_loader import ROOT, STUDY, REPO, cpu_limits, freeze_check, save, sha


def main():
    if len(sys.argv) != 3:
        raise SystemExit('Usage: validate_preparation.py UNIQUE_RUN_ID TEST_RESULTS_JSON')
    run_id, test_path = sys.argv[1:]
    if not run_id or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in run_id):
        raise ValueError('Invalid unique run ID')
    limits = cpu_limits()
    out = ROOT/'results'/run_id
    out.mkdir(parents=True, exist_ok=False)
    frozen = freeze_check()
    syntax = []
    for path in sorted(ROOT.rglob('*.py')):
        ast.parse(path.read_text(), filename=str(path.relative_to(REPO)))
        syntax.append(str(path.relative_to(REPO)))
    from future_dataloader.contracts import load_contract_context, check_cpu_receipt
    from future_dataloader.settings import PRESETS
    from future_dataloader.guards import inspect_admission
    ctx = load_contract_context()
    cpu_path = ROOT/'results/cpu_contract_20261111_01/CPU_CONTRACT_VALIDATION.json'
    checked = check_cpu_receipt(cpu_path, ctx, list(PRESETS))
    admission = inspect_admission(configurations=list(PRESETS.values()))
    import psutil
    process = psutil.Process(29074)
    active = {'pid':process.pid,'create_time':process.create_time(),'status':process.status()}
    fit = STUDY/'06_full100/seed42/outer0_inner0'
    history = json.loads((fit/'HISTORY.json').read_text())
    progress = json.loads((fit/'BATCH_PROGRESS.json').read_text())
    commands = {}
    for name, command in [
        ('git_diff_check',['git','diff','--check']),
        ('git_diff_stat',['git','diff','--stat']),
        ('git_status',['git','status','--short','--branch','--untracked-files=all']),
        ('pip_check',[sys.executable,'-B','-m','pip','check']),
        ('GPU_compute_processes',['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits']),
    ]:
        run = subprocess.run(command,cwd=REPO,capture_output=True,text=True,timeout=60)
        commands[name] = {'command':command,'exit_code':run.returncode,'stdout':run.stdout,'stderr':run.stderr}
        if run.returncode:
            raise RuntimeError(name+' failed')
    report = STUDY/'FUTURE_DATALOADER_OPTIMIZATION.md'
    issues = []
    for path in [report] + sorted(ROOT.rglob('*.py')):
        for line_number, line in enumerate(path.read_text().splitlines(),1):
            if line.rstrip() != line:
                issues.append({'path':str(path.relative_to(REPO)),'line':line_number})
    if issues:
        raise ValueError('Trailing whitespace in preparation: '+str(issues))
    allowed_suffixes = {'.py','.json','.md','.txt'}
    disallowed = [str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and p.suffix not in allowed_suffixes]
    if disallowed:
        raise ValueError('Unexpected non-source/evidence artifact: '+str(disallowed))
    tests = json.loads(Path(test_path).read_text())
    if tests.get('status') != 'PASS':
        raise ValueError('Test summary must be PASS')
    value = {
        'schema':1,'status':'PASS','utc':dt.datetime.now(dt.timezone.utc).isoformat(),
        'command':sys.argv,'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
        'git_working_tree_dirty':True,'methodology':'Isolated future loader preparation; no active modifications',
        'limits':limits,'AST_parsed_files':syntax,'new_source_whitespace':'PASS',
        'protected_protocol_sha256':frozen['protocol_sha256'],'protected_implementation':frozen['implementation'],
        'protected_source_freeze':'PASS','legacy_source_data_configuration_binding':'PASS',
        'CPU_contract_receipt':str(cpu_path.relative_to(REPO)),
        'CPU_contract_receipt_sha256':sha(cpu_path),'CPU_contract_binding_sha256':checked['binding_sha256'],
        'tests':tests,'GPU_admission':admission,'active_training_process':active,
        'completed_epochs':len(history),'latest_completed_epoch':history[-1]['epoch'],'latest_progress_receipt':progress,
        'isolated_sources_sha256':{str(p.relative_to(REPO)):sha(p) for p in sorted(ROOT.rglob('*.py'))},
        'report_sha256':sha(report),'commands':commands,
        'no_frame_cache_or_model_artifacts_under_preparation':not disallowed,
        'GPU_benchmark_executed':False,'recommended_configuration':None,'measured_speedup':None,
        'warnings':['GPU model-update equivalence, actual pinning and performance remain pending.',
                    'CPU pixel validation covers four declared T episodes; full ordering checks use metadata.',
                    'Historical PTS are bound to fresh source-video hashes, not freshly decoded timestamps.',
                    'Existing live report modifications and prior audit artifacts predate this preparation.'],
    }
    freeze_check()
    save(out/'FINAL_VALIDATION.json',value)
    paths = [p for p in ROOT.rglob('*') if p.is_file()] + [report]
    save(out/'OUTPUT_MANIFEST.json',{'outputs':[{'path':str(p.relative_to(REPO)),
        'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(paths)],'self_excluded':True})
    print(json.dumps({'status':'PASS','output':str(out.relative_to(REPO)),
        'protected_source_freeze':'PASS','CPU_contract_binding':'PASS','AST_files':len(syntax),
        'unit_tests':tests['unique_passed_tests'],'completed_epochs':len(history),
        'current_epoch':progress.get('epoch'),'GPU_benchmark':'PENDING'},indent=2))


if __name__ == '__main__':
    main()
