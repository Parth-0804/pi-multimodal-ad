"""Resume only incomplete phases after checkpointed corruption extraction."""
from pathlib import Path
from datetime import datetime,timezone
import importlib.metadata
import json
import os
import subprocess
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from reassemble.completion_common import config,read,write,storage,progress
from reassemble.section1_features import sha

c=config();root=Path(c['runs']['final-synthesis']);s3=Path(c['runs']['section3'])
while True:
    counts={name:len(list((s3/name).glob('*.json'))) for name in ['visual','sensor']}
    if all(n==148 for n in counts.values()):break
    for p in s3.glob('*_worker*.log'):
        assert 'Traceback (most recent call last)' not in p.read_text(),f'Inspect failed worker {p}; completed checkpoints retained'
    storage();time.sleep(30)
progress('All 296 recording-condition caches ready; running the remaining phases')
sequence=[('section3','14_section3_evaluate',s3/'predictions/S5.json'),('section3','16_section3_report',s3/'results.json'),('modality-dropout','17_modality_dropout',Path(c['runs']['modality-dropout'])/'results.json'),('audio-gate','18_completion_gates',Path(c['runs']['object-feasibility'])/'results.json'),('efficiency','19_completion_efficiency',Path(c['runs']['efficiency'])/'results.json'),('final-synthesis','20_completion_synthesis',root/'synthesis_context.json'),('final-synthesis','21_completion_audit',root/'validation.json')]
versions={name:importlib.metadata.version(name) for name in ['numpy','pandas','scikit-learn','torch','transformers','scipy','matplotlib','h5py']}
for phase,script,done in sequence:
    if done.exists():print('Already checkpointed:',script,flush=True);continue
    storage();folder=Path(c['runs'][phase]);path=Path('scripts/reassemble')/(script+'.py');command=[sys.executable,'-B',str(path)]
    attempt=1
    while (folder/f'{script}_attempt{attempt}.json').exists():attempt+=1
    provenance={'command':['ma_thesis_env/bin/python','-B',str(path)],'timestamp_UTC':datetime.now(timezone.utc).isoformat(),'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'dirty_tracked_paths':subprocess.check_output(['git','diff','--name-only'],text=True).splitlines(),'configuration':c,'corruptions':read('configs/reassemble/section3_corruptions.json'),'versions':versions,'script_sha256':sha(path),'source_hashes':{str(p):sha(p) for p in sorted(Path('src/reassemble').glob('*.py'))},'inputs':['Frozen Section 1/1B/2 manifests; raw identifiers in inventory recordings.parquet; strictly downstream artifacts from preceding phase'],'raw_input_root':c['data_root']+'/raw/data','warnings':'Expected missing-channel NaN warnings counted in sensor metadata. Prior intentional extraction interruptions retained in logs.'}
    write(folder/f'{script}_attempt{attempt}.json',provenance)
    log=folder/f'{script}_attempt{attempt}.log';progress('Executing '+script)
    with log.open('x') as stream:
        env=os.environ.copy();env.update({'PYTHONPATH':'src','PYTHONDONTWRITEBYTECODE':'1','MPLBACKEND':'Agg'})
        process=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,env=env)
    if process.returncode:
        progress('Software correction needed in '+script+'; inspect '+str(log)+'; completed evidence retained')
        raise SystemExit(process.returncode)
    assert done.exists(),str(done)
progress('All numerical phases and audit complete; inspect claims/figures, then run script 21 --seal')
