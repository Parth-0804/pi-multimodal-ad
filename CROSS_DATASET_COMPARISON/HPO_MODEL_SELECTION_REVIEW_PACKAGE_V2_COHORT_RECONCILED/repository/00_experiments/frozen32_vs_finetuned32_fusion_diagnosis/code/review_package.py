"""Verify new numerical evidence and package small study artifacts; no model execution."""
import datetime as dt
import hashlib
import json
import math
import subprocess
import zipfile
import numpy as np
from sklearn.metrics import average_precision_score
from common import *

def independent_AP(rows,col):
    ordered=sorted(rows,key=lambda r:-float(r[col]));positive=sum(int(r['failure']) for r in ordered)
    if not positive:return np.nan
    total=0.;tp=previous=0
    for i,row in enumerate(ordered,1):
        tp+=int(row['failure'])
        if i==len(ordered) or float(ordered[i][col])!=float(row[col]):
            total+=(tp-previous)*tp/i/positive;previous=tp
    return total

def package(status,coverage,fits):
    import csv as stdcsv
    import pandas as pd
    results=csv(ROOT/'comparison/fusion_results.csv');ap_checks=[]
    for cov in coverage:
        seed=cov['seed']
        for condition in CONDITIONS:
            paths=[ROOT/f'seed_{seed}'/condition/fold/'assessment_predictions.csv' for fold in cov['matched_folds']]
            if not paths:continue
            rows=[]
            for path in paths:
                with path.open() as f:rows.extend(stdcsv.DictReader(f))
            assert len(rows)==len({r['sample_id'] for r in rows})
            for branch,col in [('visual','p_visual'),('sensor','p_sensor'),('uniform','p_uniform'),('F2','p_F2')]:
                actual=independent_AP(rows,col);expected=float(results[(results.seed==seed)&(results.condition==condition)&(results.scope=='pooled')&(results.branch==branch)].AP.iloc[0])
                assert abs(actual-expected)<1e-12
                ap_checks.append({'seed':seed,'condition':condition,'branch':branch,'AP':actual})
    for row in fits:
        model=REPO/row['model_reference'];assert sha(model)==row['model_sha256']
        done=read(STUDY/row['manifest'])
        if not row['reused']:
            assert done['epochs']==2 and done['saved_pixel_replay']['passed']
            assert read((STUDY/row['manifest']).parent/'weight_update_checks.json')['passed']
    # Re-check immutable consumed artifacts after scientific execution, not old model replays/tests.
    inputs=read(STUDY/'data_manifests/input_hashes.json')
    for name,expected in inputs.items():assert sha(REPO/name)==expected,('PROTECTED_INPUT_DRIFT',name)
    assert subprocess.check_output(['git','diff','--stat'],cwd=REPO)==(ROOT/'provenance/git_diff_stat_at_start.txt').read_bytes()
    (ROOT/'provenance/git_status_at_finish.txt').write_bytes(subprocess.check_output(['git','status','--short','--branch'],cwd=REPO))
    elapsed=(dt.datetime.now(dt.timezone.utc)-dt.datetime.fromisoformat(clock()['started_utc'])).total_seconds()
    write(ROOT/'checks/final_evidence_review.json',{'passed':True,'pooled_APs_independently_reproduced':ap_checks,'completed_fit_models_hash_checked':len(fits),
        'protected_input_hashes_checked':len(inputs),'new_saved_model_replays_checked':sum(not x['reused'] for x in fits),
        'old_replays_not_repeated':True,'review':'Self-review with second AP implementation; not independent scientific review',
        'elapsed_seconds_at_review':elapsed,'git_tracked_diff_unchanged':True,'coverage':coverage})
    write(ROOT/'provenance/source_hashes_at_finish.json',{str(p.relative_to(STUDY)):sha(p) for p in [STUDY/'run_experiment.py',*(STUDY/'code').glob('*.py'),*(STUDY/'tests').glob('*.py')]})
    target=ROOT/'REVIEW_PACKAGE.zip'
    if target.exists():
        # A report-only invocation must not overwrite an already published packet.
        event('EXISTING_PACKAGE_PRESERVED',existing_package=str(target.relative_to(STUDY)));return
    files=[]
    for p in sorted(STUDY.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(STUDY)
        if any(x in rel.parts for x in ['__pycache__','matplotlib_cache','shared_cache','synthetic_report_fixture']):continue
        if p.suffix in ['.pt','.pth','.npy','.npz','.zip','.lock']:continue
        if p.name in ['output_manifest.json','archive_verification.json','training.log','events.jsonl','STATE.json']:continue
        # Assessment and OOF banks suffice; individual-fit output duplicates remain local.
        if p.name=='identified_branch_predictions.csv':continue
        if p.stat().st_size>12*1024**2:continue
        files.append({'path':str(rel),'bytes':p.stat().st_size,'sha256':sha(p)})
    manifest={'files':files,'excluded':'Raw data, models/optimizers, feature/pixel caches, duplicate per-fit predictions, archive/verification itself; no automatic upload',
        'weights_retained_locally':fits,'created_utc':utc()}
    write(ROOT/'provenance/output_manifest.json',manifest)
    with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for row in files:z.write(STUDY/row['path'],row['path'])
        z.write(ROOT/'provenance/output_manifest.json','results/provenance/output_manifest.json')
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        for row in files:assert hashlib.sha256(z.read(row['path'])).hexdigest()==row['sha256']
    elapsed=(dt.datetime.now(dt.timezone.utc)-dt.datetime.fromisoformat(clock()['started_utc'])).total_seconds()
    write(ROOT/'checks/archive_verification.json',{'passed':True,'CRC_passed':True,'payload_hashes_verified':len(files),'archive_bytes':target.stat().st_size,
        'sha256':sha(target),'finished_utc':utc(),'actual_total_seconds':elapsed})
    state=read(STUDY/'STATE.json');write(STUDY/'STATE.json',{**state,'package_verified':True,'actual_total_seconds':elapsed,'review_package':str(target.relative_to(STUDY))})
    print('REVIEW_PACKAGE_VERIFIED',str(target),target.stat().st_size,flush=True)
