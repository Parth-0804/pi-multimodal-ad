"""Restartable per-file receipts around the existing exact-file downloader.

An incomplete attempt remains preserved in its unique staging directory. Completed
files have an adjacent receipt before the next transfer; reconciliation validates
published bytes after an interruption between publication and receipt creation.
"""
import argparse
import json
import os
import shutil
import sys
import time
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'stage2'))
from download_msm import audit_plan, transfer, sha256
from prepare_full_lab import write


def acquire(run, execute=False):
    cfg = json.loads((run/'config/download_config.json').read_text())
    root = Path(cfg['data_root'])
    inv = json.loads((run/'manifests/official_file_inventory.json').read_text())
    # Recover only our fully published staged files with exact byte/hash equality.
    for e in cfg['download_plan']:
        target = root/e['name']
        if not target.exists(): continue
        receipts = list(root.glob('_msm_download_receipt_*.json'))
        known = any(any(r.get('path') == e['name'] and r.get('sha256') == sha256(target)
                        for r in json.loads(p.read_text()).get('results', [])) for p in receipts)
        if known: continue
        matches = [p for p in (run/'staging').glob('*/'+e['name'])
                   if p.stat().st_size == e['bytes'] and sha256(p) == sha256(target)]
        if not matches: raise ValueError('Unverified existing file preserved: '+e['name'])
        if execute:
            stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            write(root/('_msm_download_receipt_'+stamp+'.json'), {'handle':cfg['handle'],
                 'reconciliation':'same fully published staging bytes',
                 'results':[{'path':e['name'],'bytes':e['bytes'],'sha256':sha256(target),'status':'reconciled'}]})
    rows = audit_plan(cfg, inv, root)
    missing = sum(r['bytes'] for r in rows if r['status']=='missing')
    assert missing <= 2_700_000_000
    assert shutil.disk_usage(root).free - missing >= 10*1024**3
    print('PREVIEW',len(rows),'files;',sum(r['status']=='missing' for r in rows),'missing;',missing,'bytes',flush=True)
    if not execute: return
    attempt = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    staging = run/'staging'/attempt
    results=[]
    for n,row in enumerate(rows):
        try:
            before=time.perf_counter()
            result = row if row['status']=='verified_existing' else transfer(cfg['handle'],row,root,staging)
            result['elapsed_s']=time.perf_counter()-before
            if result['status']=='downloaded':
                stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
                receipt={'handle':cfg['handle'],'started_attempt_utc':attempt,'results':[result]}
                write(root/('_msm_download_receipt_'+stamp+'.json'),receipt)
                write(run/'evidence'/('_msm_download_receipt_'+stamp+'.json'),receipt)
            results.append(result)
            print(n+1,result['status'],result['bytes'],result['path'],flush=True)
        except Exception as exc:
            write(run/'evidence'/('acquisition_failure_'+attempt+'.json'),
                  {'path':row['path'],'error_type':type(exc).__name__,
                   'http_status':exc.code if isinstance(exc,urllib.error.HTTPError) else None,
                   'completed_results':results,'preserved_partial_staging':str(staging)})
            raise
    write(run/'manifests'/('acquisition_receipt_'+attempt+'.json'),{'handle':cfg['handle'],'results':results})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',type=Path,required=True);parser.add_argument('--execute',action='store_true')
    args=parser.parse_args();acquire(args.run,args.execute)
