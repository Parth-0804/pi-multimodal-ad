"""Parallel independent recordings; keep original per-frame batch/numerics."""
from pathlib import Path
import subprocess
import sys
import json
import time
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root/'src'))
from reassemble.completion_common import config,progress
run=Path(config()['runs']['section3']);jobs=[]
for kind,count,script in [('visual',3,'12_section3_visual.py'),('sensor',4,'13_section3_sensor.py')]:
    for index in range(count):
        log=(run/f'{kind}_worker{index}.log').open('a')
        proc=subprocess.Popen([sys.executable,'-B',str(root/'scripts/reassemble'/script)],stdout=log,stderr=subprocess.STDOUT)
        jobs.append((kind,index,proc,log))
previous=None
while any(p.poll() is None for _,_,p,_ in jobs):
    failures=[(k,i,p.returncode) for k,i,p,_ in jobs if p.poll() not in [None,0]]
    if failures:
        for _,_,p,_ in jobs:
            if p.poll() is None:p.terminate()
        raise RuntimeError(('Extraction failure; stop and audit',failures))
    counts={name:len(list((run/name).glob('*.npz'))) for name in ['visual','sensor']}
    if counts!=previous:progress('Section 3 extraction checkpoints: '+str(counts));previous=counts
    time.sleep(30)
assert all(p.returncode==0 for _,_,p,_ in jobs)
assert all(len(list((run/name).glob('*.npz')))==148 for name in ['visual','sensor'])
for _,_,_,log in jobs:log.close()
progress('Section 3 parallel extraction complete: 148 visual and 148 sensor checkpoints')
