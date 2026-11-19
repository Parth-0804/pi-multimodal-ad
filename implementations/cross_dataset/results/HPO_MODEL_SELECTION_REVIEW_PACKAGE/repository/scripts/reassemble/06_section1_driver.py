"""Resume-safe orchestration and live IDE handoff; never starts Section 2."""
import argparse
from datetime import datetime,timezone
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',default='configs/reassemble/section1.json');args=p.parse_args()
    config=json.loads(Path(args.config).read_text());run=Path(config['run_dir']);lock=(run/'driver.lock').open('a')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    handoff=Path('docs/reassemble/CONTINUATION.md')
    def status(stage,pid=None,error=None):
        features=len(list((run/'features').glob('*.npz')));finished=len(list((run/'predictions').glob('*_perm??.npz')));folds=len(list((run/'predictions').glob('*_fold*.npz')))
        data={'utc':datetime.now(timezone.utc).isoformat(),'stage':stage,'driver_pid':os.getpid(),'child_pid':pid,'feature_recordings':features,'expected_recordings':148,'completed_models':finished,'expected_models':44,'completed_outer_fits':folds,'error':error}
        (run/'live_status.json').write_text(json.dumps(data,indent=2)+'\n')
        handoff.write_text('# REASSEMBLE continuation — Section 1\n\n'+data['utc']+'\n\nAuthorized: SECTION_PLAN.md Section 1; **no fusion**. Frozen choices: SECTION_1_PROTOCOL.md\nand configs/reassemble/section1.json. Run: `'+str(run)+'`.\n\nCurrent stage: **'+stage+'**. Feature recordings '+str(features)+'/148; completed model/control runs '+str(finished)+'/44; completed outer fits '+str(folds)+'/220.\nDriver PID '+str(os.getpid())+'; current child '+str(pid)+'. Check live_status.json and logs before restarting.\n'+('Error: '+error+'\n' if error else '')+'\nCommands (repository environment):\n```bash\nma_thesis_env/bin/python -B scripts/reassemble/03_section1_features.py\nma_thesis_env/bin/python -B scripts/reassemble/06_section1_driver.py\n```\nThe driver waits for extraction, then runs 04_section1_train.py and 05_section1_report.py.\nDo not start duplicate jobs. An OS file lock prevents duplicate drivers. After a failure,\ninspect logs and retain partial outputs. Completed extraction/fits are reused only under\nthe recorded implementation; changed code requires explicit correction/versioning.\n\nLogs: features.log, training.log, report.log. Full input evidence: audit run\n20260927T141645Z-inventory; prior acquisition handoff: previous_continuation.md here.\nBaseline audit Git checkpoint: 6721414. This section explicitly authorizes training.\n40 tests plus synthetic neural training smoke checks passed before real fitting.\n\nFinal target: artifacts/reassemble/reports/SECTION_1_UNIMODAL_HANDOFF.md. After completion,\nverify results, manifests, dependency/whitespace checks, protected-file metadata, and\ncreate a scoped additive checkpoint. STOP for researcher review; Section 2 is NOT authorized\nuntil that review. Keep PHM/Intel, raw sources, archives and historical evidence unchanged.\n')
    while not (run/'cohort.parquet').exists():
        log=(run/'features.log').read_text() if (run/'features.log').exists() else ''
        if 'Traceback (most recent call last)' in log:
            status('FAILED extraction',error='Inspect features.log; do not train');return 1
        status('feature extraction running');time.sleep(30)
    for stage,script,logname,marker in [('nested training and controls','04_section1_train.py','training.log',run/'predictions/patchtst_perm19.npz'),('clustered assessment','05_section1_report.py','report.log',Path('artifacts/reassemble/reports/SECTION_1_UNIMODAL_HANDOFF.md'))]:
        if marker.exists():continue
        with (run/logname).open('a') as log:
            process=subprocess.Popen([sys.executable,'-B','scripts/reassemble/'+script,'--config',args.config],stdout=log,stderr=subprocess.STDOUT)
            while process.poll() is None:status(stage,process.pid);time.sleep(30)
            if process.returncode:
                status('FAILED '+stage,error=f'{script} exit {process.returncode}; inspect {logname}')
                with (run/'failures_and_corrections.md').open('a') as f:f.write(f'\n{datetime.now(timezone.utc).isoformat()}: {script} exited {process.returncode}; retained {logname} and all partial evidence.\n')
                return process.returncode
    status('Section 1 computed; final validation/researcher review required')
    return 0

if __name__=='__main__':raise SystemExit(main())
