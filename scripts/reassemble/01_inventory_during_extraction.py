#!/usr/bin/env python3
"""Audit only fully written members after all source ZIP CRC checks pass."""
import argparse
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
import json
from pathlib import Path
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from reassemble.inventory import audit_recording

p=argparse.ArgumentParser();p.add_argument('--run-dir',required=True);p.add_argument('--acquisition-run',required=True);p.add_argument('--config',default='configs/reassemble/audit.json');p.add_argument('--workers',type=int,default=3)
a=p.parse_args();config=json.loads(Path(a.config).read_text());root=Path(config['data_root']).resolve()/'REASSEMBLE'
# Written by acquisition only after all three archives pass integrity checks.
manifest=json.loads((Path(a.acquisition_run)/'archive_inventory.json').read_text())
expected={m['name']:m['size_bytes'] for z in manifest if z['archive']=='data.zip' for m in z['members'] if m['name'].endswith('.h5')}
pending=set(expected);active={};completed=set()
with ProcessPoolExecutor(max_workers=a.workers) as pool:
    while pending or active:
        for name in sorted(pending):
            if len(active)>=a.workers:break
            raw=root/'raw' if (root/'raw').exists() else root/'raw.extracting'
            source=raw/name
            if not source.exists() or source.stat().st_size!=expected[name]:continue
            future=pool.submit(audit_recording,(str(source),config,a.run_dir,str(root/'cache'/'encoded_media')))
            active[future]=name;pending.remove(name)
        if active:
            done,_=wait(active,timeout=5,return_when=FIRST_COMPLETED)
            for future in done:
                name=active.pop(future)
                try:result=future.result()
                except FileNotFoundError:
                    # Acquisition may atomically promote raw.extracting during the initial hash.
                    if not (root/'raw'/name).exists():raise
                    pending.add(name);continue
                completed.add(name);print(f'{len(completed)}/{len(expected)} {result}',flush=True)
        else:
            time.sleep(5)
        if not (root/'raw').exists() and 'Traceback (most recent call last)' in (Path(a.acquisition_run)/'acquisition.log').read_text():
            raise RuntimeError('Acquisition failed; stop scheduling audit work')
print('PER-RECORDING AUDIT COMPLETE',flush=True)
