"""Create a new portable review export; preserve v1 and all research evidence."""
from pathlib import Path
import csv
import datetime as dt
import hashlib
import importlib.util
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

csv.field_size_limit(256*1024**2)
RECON=Path(__file__).resolve().parents[1]
REPO=RECON.parents[1]
PARENT=REPO/'CROSS_DATASET_COMPARISON'
V1=PARENT/'HPO_MODEL_SELECTION_REVIEW_PACKAGE'
ROOT=PARENT/'HPO_MODEL_SELECTION_REVIEW_PACKAGE_V2_COHORT_RECONCILED'
ZIP=ROOT.with_suffix('.zip')
AUDIT='repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103'
EXPECTED_V1='f1a4db4717e6623413318212c801a7c90a5035e3535eb72afdcdff610ad36dfc'

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
    return h.hexdigest()
def rows(p):
    with Path(p).open(newline='') as f:return list(csv.DictReader(f))
def save(p,rs,fields=None):
    with Path(p).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rs[0]));w.writeheader();w.writerows(rs)
def js(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)
def module(p,name):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    assert not ROOT.exists() and not ZIP.exists(),'Never overwrite an existing versioned export'
    started=dt.datetime.now(dt.timezone.utc).isoformat()
    head=git('rev-parse','HEAD').decode().strip()
    staged=hashlib.sha256(git('diff','--cached','--binary')).hexdigest()
    status=git('status','--porcelain=v1','--untracked-files=no')
    assert sha(V1.with_suffix('.zip'))==EXPECTED_V1,'Original archive identity changed'
    assert json.loads((RECON/'RECONCILIATION_VALIDATION.json').read_text())['passed']
    before=rows(V1/'PACKAGE_MANIFEST.csv')
    for r in before:assert sha(V1/r['package_path'])==r['sha256'],r['package_path']
    print('COPY_V1',len(before)+1,flush=True)
    shutil.copytree(V1,ROOT)
    shutil.copytree(RECON,ROOT/'COHORT_RECONCILIATION')
    source=rows(ROOT/'SOURCE_FILE_MANIFEST.csv');by_path={r['package_path']:r for r in source}
    external=rows(ROOT/'EXTERNAL_ARTIFACTS.csv');external_names={r['original_source_path'] for r in external}
    # Include newly used small identity receipts/manifests, never raw/model/cache arrays.
    resolution=[];added=0
    for r in rows(RECON/'SOURCE_PROVENANCE.csv'):
        p=REPO/r['path'];assert sha(p)==r['sha256'],('SOURCE_DRIFT',r['path'])
        dest=ROOT/'repository'/r['path']
        small=p.suffix.lower() in {'.json','.csv','.md','.py','.yaml','.yml','.toml','.txt','.tsv'}
        assert not any(q in p.parts for q in ['.env','synology_cookies.txt','.aws','.ssh','.git'])
        if not dest.exists() and small:
            dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);added+=1
            package_path=str(dest.relative_to(ROOT))
            src={'package_path':package_path,'original_source_path':r['path'],
                'role':'new cohort reconciliation original identity/seed evidence','original_bytes':r['bytes'],
                'original_sha256':r['sha256'],'audit_recorded_sha256':'NOT RECORDED',
                'copy_status':'BYTE_IDENTICAL','exported_sha256':r['sha256'],'exported_bytes':r['bytes']}
            source.append(src);by_path[package_path]=src
        internal=dest.is_file()
        if not internal and r['path'] not in external_names:
            external.append({'original_source_path':r['path'],'bytes':r['bytes'],'sha256':r['sha256'],
                'reason':'Source probability/feature-container or parquet binary remains external. Exact identities and clean evaluation probability rows exported in COHORT_RECONCILIATION.'})
            external_names.add(r['path'])
        resolution.append({'original_source_path':r['path'],'original_sha256':r['sha256'],
            'included_package_path':str(dest.relative_to(ROOT)) if internal else 'EXTERNAL_ARTIFACTS.csv',
            'status':'INCLUDED' if internal else 'EXTERNAL BY SIZE/FORMAT POLICY'})
    save(ROOT/'RECONCILIATION_SOURCE_RESOLUTION.csv',resolution)
    save(ROOT/'EXTERNAL_ARTIFACTS.csv',external)
    shutil.copy2(ROOT/'README.md',ROOT/'README_V1.md')
    intro='''# HPO model-selection review package — cohort-reconciled version2

Start with [MATCHED_COMPARISON_SUMMARY.md](COHORT_RECONCILIATION/MATCHED_COMPARISON_SUMMARY.md). This version preserves the complete original audit and implementation evidence and adds a verified REASSEMBLE action/recording/split/seed reconciliation. The original version1 archive and all experiments remain unchanged. No training, inference, tuning or fusion fitting was run.

The753-action pilot is exactly original outer fold0 (legacy fold_01):77 failures across26 recordings, within the4,530-action/148-recording cohort. The selected inner “fit3” originally assessed920 different actions. Its100-epoch follow-up assesses753 outer actions, retaining its1,752/419/686 training/validation/calibration roles. The C20 outer refit is the C20 run with matching753-action assessment.

Direct descriptive comparisons are permitted only within the same verified matched_comparison_group. Pooled4,530-action AP and753-action fold AP are separate estimands. Matching actions does not remove training, calibration, checkpoint, stacking or prior test-selection differences. The revised active comparability matrix applies these rules; the version1 matrix is retained beside it for provenance.

| Added evidence | Location |
|---|---|
| Main findings, matched753 and pooled4530 AP tables | [Matched comparison summary](COHORT_RECONCILIATION/MATCHED_COMPARISON_SUMMARY.md) |
| Every experiment's counts, folds and seeds | [Training experiment summary](COHORT_RECONCILIATION/EXPERIMENT_COHORT_SPLIT_SEED_SUMMARY.csv), [prediction-workflow summary](COHORT_RECONCILIATION/ALL_PREDICTION_WORKFLOW_SUMMARY.csv) |
| All6,894 fit records, exact role counts and seed provenance | [Run cohort passports](COHORT_RECONCILIATION/ALL_TRAINING_RUN_COHORTS.csv) |
| Every saved evaluation's exact cohort and matching eligibility | [Evaluation cohort passports](COHORT_RECONCILIATION/ALL_EVALUATION_COHORTS.csv) |
| Every action and recording identity | [Action memberships](COHORT_RECONCILIATION/COHORT_ACTION_MEMBERSHIP.csv), [cohort recording lists](COHORT_RECONCILIATION/COHORT_REGISTRY.csv), [canonical actions](COHORT_RECONCILIATION/CANONICAL_ACTION_MANIFEST.csv) |
| Smaller-set subset proof and exact recording list | [Subset proof](COHORT_RECONCILIATION/SMALLER_COHORT_SUBSET_PROOF.json), [26 recordings](COHORT_RECONCILIATION/SMALLER_COHORT_EXACT_RECORDINGS.csv) |
| All1,498,629 clean held-out probability rows, without row sampling | [Predictions](COHORT_RECONCILIATION/ALL_CLEAN_HELD_OUT_PREDICTIONS.csv) |
| Matched comparisons, duplicate score evidence | [Explicit matrix](COHORT_RECONCILIATION/COMPARABILITY_MATRIX.csv), [all matching groups](COHORT_RECONCILIATION/MATCHED_COMPARISON_GROUPS.csv), [score aliases](COHORT_RECONCILIATION/IDENTICAL_PREDICTION_ALIASES.csv) |
| Stale28-versus26 recording metadata | [Metadata conflicts](COHORT_RECONCILIATION/METADATA_CONFLICTS.csv) |
| Missing evidence and qualifications | [Reconciliation limits](COHORT_RECONCILIATION/MISSING_EVIDENCE.md) and original audit report below |
| Original paths, source hashes and internal/external resolution | [Source provenance](COHORT_RECONCILIATION/SOURCE_PROVENANCE.csv), [resolution manifest](RECONCILIATION_SOURCE_RESOLUTION.csv) |
| Reconciliation validation | [Validation result](COHORT_RECONCILIATION/RECONCILIATION_VALIDATION.json) |

CSV joins: evaluation_id links probabilities to evaluation passports; native_key links probabilities to canonical actions; role cohort IDs link fits to exact action memberships and recording lists. Native key is recording_id::segment_id. Seed families, actual estimator RNG seeds, split/role seeds and validation seeds are distinct fields. NOT RECORDED is never a zero-size split. Identical score vectors are repeated exports, not independent replications.

For verification after extracting: run `python package_tools/verify_package.py PATH_TO_PACKAGE_ROOT`, then `python COHORT_RECONCILIATION/tools/verify_reconciliation.py PATH_TO_COHORT_RECONCILIATION`. Both are standard-library verification tools; neither executes research models. Large weights, datasets and feature caches remain external with hashes and original paths. The exported source/report modification manifest identifies review annotations; original configuration values, source implementations and result cells are preserved.

## Original audit and implementation evidence navigation

The following preserved navigation covers all17 original requested items, including Tables A–H, full configurations/results, scripts, curves and checkpoint logic. Read historical conclusions under the cohort qualifications above. [README_V1.md](README_V1.md) preserves the prior handoff verbatim.

'''
    old=(ROOT/'README_V1.md').read_text()
    (ROOT/'README.md').write_text(intro+old[old.index('## Where to find every requested item'):])
    # Active table: retain other datasets, replace REASSEMBLE blanket statements.
    active=ROOT/AUDIT/'05_results/COMPARABILITY_MATRIX.csv'
    shutil.copy2(active,active.with_name('V1_COMPARABILITY_MATRIX.csv'))
    original_matrix=rows(active)
    replace={'Original REASSEMBLE branches/F2','B100 versus C100','100-epoch F2 versus sensor/visual',
        'Original pooled F2 versus100-epoch pilot','Original outer1 F2 versus100-epoch F2',
        'C20 versus original frozen','C20 versus C100','Boundary/legacy follow-ups'}
    combined=[r for r in original_matrix if r['comparison'] not in replace]
    newmatrix=rows(RECON/'COMPARABILITY_MATRIX.csv')
    fields=list(dict.fromkeys(k for r in combined+newmatrix for k in r))
    save(active,combined+newmatrix,fields)
    reports=['01_executive_overview/EXECUTIVE_AUDIT_SUMMARY.md',
        '06_dataset_specific/REASSEMBLE/MODEL_AND_CONFIGURATION_AUDIT.md',
        '06_dataset_specific/REASSEMBLE/FROZEN_VS_FINETUNED_100_EPOCHS.md',
        '06_dataset_specific/REASSEMBLE/FUSION_RESULTS_AND_CONFIGURATIONS.md',
        '08_future_hpo_readiness/MODEL_SELECTION_EVIDENCE_TABLE.md',
        '08_future_hpo_readiness/HPO_READINESS_AND_CONSTRAINTS.md',
        '07_scientific_validity/LEAKAGE_AND_SELECTION_AUDIT.md',
        '07_scientific_validity/MISSING_EVIDENCE.md']
    changes=[]
    for name in reports:
        p=ROOT/AUDIT/name;oldtext=p.read_text();target=os.path.relpath(ROOT/'COHORT_RECONCILIATION/MATCHED_COMPARISON_SUMMARY.md',p.parent)
        notice=f'''# Version2 cohort qualification

The [verified action/split reconciliation]({target}) governs REASSEMBLE comparisons in this package. The753 actions (26 recordings) are exactly original outer fold0 within4,530 actions (148 recordings). The920-action selected inner assessment is disjoint. C20 outer refit job4 shares the753 held-out actions with CNN100; C20 inner job2 does not. Compare only matching action/label/assessment/observation passports. Training and selection differences remain limitations. A stale prediction_recordings list is documented without altering the original JSON. No training or inference was run.

The original audit text and numerical results follow unchanged; generic pre-reconciliation comparison statements are historical context and are superseded by the revised comparability matrix and passports.

---

'''
        p.write_text(notice+oldtext);changes.append(str(p.relative_to(ROOT)))
    changes.append(str(active.relative_to(ROOT)))
    for package_path in changes:
        r=by_path[package_path];r['exported_sha256']=sha(ROOT/package_path);r['exported_bytes']=(ROOT/package_path).stat().st_size
        r['copy_status']='V2 REVIEW ANNOTATION / COHORT-QUALIFIED MATRIX; ORIGINAL RESULTS PRESERVED'
    save(ROOT/'SOURCE_FILE_MANIFEST.csv',source)
    save(ROOT/'V2_REVIEW_TRANSFORMATIONS.csv',[{'package_path':p,'original_sha256':by_path[p]['original_sha256'],
        'v1_exported_sha256':sha(V1/p),'v2_exported_sha256':sha(ROOT/p),
        'change':'Review qualification added; original report body preserved' if p.endswith('.md') else 'Active matrix replaced with exact-identity qualified rows; original at V1_COMPARABILITY_MATRIX.csv'} for p in changes])
    # All source implementations, scientific configs and result cells stay byte-identical to v1.
    allowed=set(changes)|{'README.md','SOURCE_FILE_MANIFEST.csv','EXTERNAL_ARTIFACTS.csv','EXPORT_VALIDATION.json',
        'EXPORT_PROVENANCE.json','package_tools/verify_package.py'}
    for r in before:
        if r['package_path'] not in allowed:assert sha(ROOT/r['package_path'])==r['sha256'],('UNEXPECTED_EXPORT_CHANGE',r['package_path'])
    # Update the copied verifier to include the new cohort checks without importing research code.
    p=ROOT/'package_tools/verify_package.py';text=p.read_text()
    pos=text.index("if __name__=='__main__':")
    wrapper='''_verify_original_content=verify_content
def verify_content(root):
    result=_verify_original_content(root)
    import importlib.util
    path=Path(root)/'COHORT_RECONCILIATION/tools/verify_reconciliation.py'
    spec=importlib.util.spec_from_file_location('cohort_verification',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    result['cohort_reconciliation']=module.verify(Path(root)/'COHORT_RECONCILIATION')
    return result


'''
    p.write_text(text[:pos]+wrapper+text[pos:])
    shutil.copy2(ROOT/'EXPORT_PROVENANCE.json',ROOT/'EXPORT_PROVENANCE_V1.json')
    shutil.copy2(ROOT/'EXPORT_VALIDATION.json',ROOT/'EXPORT_VALIDATION_V1.json')
    provenance={'started_utc':started,'assembled_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
        'git_head':head,'dirty_tracked_worktree':bool(status),'tracked_worktree_status_sha256':hashlib.sha256(status).hexdigest(),
        'staged_state_sha256_before_and_after':staged,'prior_archive_path':str(V1.with_suffix('.zip').relative_to(REPO)),
        'prior_archive_sha256_preserved':EXPECTED_V1,'prior_package_files_verified':len(before)+1,
        'reconciliation_source_files':len(resolution),'additional_small_source_files_copied':added,
        'reconciliation_command':['tools/reconcile.py --refresh-working-output','tools/complete_review.py','tools/verify_reconciliation.py'],
        'package_command':str(Path(__file__).relative_to(REPO)),
        'python':platform.python_version(),'training_inference_tuning_or_new_fusion_fit':False,
        'original_experiments_source_results_modified':False,'git_stage_commit_push':False,
        'secret_files_read':False,'package_policy':'Complete v1 retained; cohort identity and clean score export added; no model/raw/cache binaries'}
    js(ROOT/'EXPORT_PROVENANCE.json',provenance)
    # Placeholders resolve navigation before the final manifest is written.
    js(ROOT/'EXPORT_VALIDATION.json',{'status':'verification in progress'})
    save(ROOT/'PACKAGE_MANIFEST.csv',[],['package_path','bytes','sha256'])
    print('VERIFY_CONTENT',flush=True)
    verify=module(ROOT/'package_tools/verify_package.py','package_verification')
    validation=verify.verify_content(ROOT)
    assert head==git('rev-parse','HEAD').decode().strip()
    assert staged==hashlib.sha256(git('diff','--cached','--binary')).hexdigest()
    assert status==git('status','--porcelain=v1','--untracked-files=no')
    for r in rows(RECON/'SOURCE_PROVENANCE.csv'):assert sha(REPO/r['path'])==r['sha256']
    assert sha(V1.with_suffix('.zip'))==EXPECTED_V1
    validation.update({'prior_archive_preserved':True,'source_hashes_preserved':True,
        'original_implementations_configs_and_result_cells_preserved':True,'git_head_index_tracked_worktree_preserved':True,
        'archive_extraction_check':'Recorded in adjacent final verification receipt to avoid a self-referential ZIP hash.'})
    js(ROOT/'EXPORT_VALIDATION.json',validation)
    manifest=[{'package_path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)}
        for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='PACKAGE_MANIFEST.csv']
    save(ROOT/'PACKAGE_MANIFEST.csv',manifest)
    verify.verify_manifest(ROOT)
    print('ZIP',len(manifest)+1,flush=True)
    with zipfile.ZipFile(ZIP,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
        for p in sorted(ROOT.rglob('*')):
            if p.is_file():z.write(p,str(Path(ROOT.name)/p.relative_to(ROOT)))
    with zipfile.ZipFile(ZIP) as z:
        assert z.testzip() is None
        assert len(z.infolist())==len(manifest)+1
        with tempfile.TemporaryDirectory(prefix='hpo_cohort_review_verify_') as tmp:
            target=Path(tmp)
            for item in z.infolist():assert (target/item.filename).resolve().is_relative_to(target.resolve())
            z.extractall(target);extracted=target/ROOT.name
            extracted_hashes=verify.verify_manifest(extracted)
            extracted_content=verify.verify_content(extracted)
    receipt={'archive_path':str(ZIP.relative_to(REPO)),'archive_bytes':ZIP.stat().st_size,'archive_sha256':sha(ZIP),
        'archive_entries':len(manifest)+1,'uncompressed_bytes':sum(r['bytes'] for r in manifest)+(ROOT/'PACKAGE_MANIFEST.csv').stat().st_size,
        'ZIP_CRC_passed':True,'independent_extraction_hash_verification':extracted_hashes,
        'independent_extraction_content_verification':extracted_content,'prior_archive_sha256':sha(V1.with_suffix('.zip')),
        'completed_utc':dt.datetime.now(dt.timezone.utc).isoformat()}
    js(ROOT.with_suffix('.verification.json'),receipt)
    print(json.dumps({'archive':receipt['archive_path'],'bytes':receipt['archive_bytes'],'sha256':receipt['archive_sha256'],'files':receipt['archive_entries']}),flush=True)

if __name__=='__main__':main()
