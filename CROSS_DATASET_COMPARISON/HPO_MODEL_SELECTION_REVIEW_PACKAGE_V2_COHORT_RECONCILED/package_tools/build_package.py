"""Export the completed audit and existing implementation evidence. Never import training code."""
from pathlib import Path
import collections
import csv
import datetime as dt
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import zipfile

csv.field_size_limit(256*1024**2)
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
AUDIT=REPO/'CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103'
MIRROR=ROOT/'repository'
ARCHIVE=REPO/'CROSS_DATASET_COMPARISON/HPO_MODEL_SELECTION_REVIEW_PACKAGE.zip'
BASE='26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability'
FOLLOW='experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison'
LEGACY='parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01'
SMALL={'.py','.md','.rst','.json','.csv','.yaml','.yml','.toml','.ini','.cfg','.txt','.tsv'}
BINARY={'.pt','.pth','.ckpt','.safetensors','.pkl','.pickle','.joblib','.npz','.npy','.parquet','.h5','.hdf5','.mp4','.avi','.mov','.mkv','.tar','.7z','.rar'}
SKIP_DIR={'.git','.codex','.agents','.aws','.ssh','ma_thesis_env','node_modules','__pycache__','.pytest_cache'}
SELECTED={};SKIPPED={};SOURCE_ROWS=[];LINK_REWRITES=[]


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024**2),b''):h.update(chunk)
    return h.hexdigest()


def write_json(path,value):
    path=Path(path);assert path.resolve().is_relative_to(ROOT.resolve())
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2)+'\n')


def write_csv(path,rows,fields=None):
    path=Path(path);assert path.resolve().is_relative_to(ROOT.resolve())
    path.parent.mkdir(parents=True,exist_ok=True)
    fields=fields or list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or ['no_records']);w.writeheader();w.writerows(rows)


def sensitive(path):
    parts=Path(path).parts
    for part in parts:
        p=part.lower()
        if part in SKIP_DIR or p in {'synology_cookies.txt','credentials','id_rsa','id_ed25519','source_access.json'}:return True
        if p=='.env' or p.startswith('.env.') or p.endswith(('.pem','.key')):return True
        if 'access_token' in p or 'session_cookie' in p:return True
    return False


def select(path,role,force=False):
    p=Path(path);p=p if p.is_absolute() else REPO/p
    if not p.is_relative_to(REPO) or p.is_relative_to(ROOT):return
    name=str(p.relative_to(REPO))
    if sensitive(name) or p.is_symlink() or not p.is_file():return
    if p.suffix.lower() in BINARY:return
    if not force and (p.suffix.lower() not in SMALL or p.stat().st_size>8*1024**2):return
    if name.startswith(('gtc-data-experiment/','data/Full Dataset/')):return
    SELECTED.setdefault(name,role)


def tree(relative,extensions=None):
    folder=REPO/relative
    if not folder.is_dir():return
    for base,dirs,files in os.walk(folder,followlinks=False):
        dirs[:]=sorted(d for d in dirs if d not in SKIP_DIR and not sensitive(d) and 'cache' not in d.lower()
                      and d.lower() not in {'temporary','tmp'} and not (Path(base)/d).is_symlink())
        for name in sorted(files):
            p=Path(base)/name
            if extensions is None or p.suffix.lower() in extensions:select(p,'implementation/configuration/protocol support')


def plan():
    for p in AUDIT.rglob('*'):
        if not p.is_file() or p.is_symlink():continue
        relative=p.relative_to(AUDIT)
        if 'test_tmp' in relative.parts or p.suffix in BINARY:continue
        if p.suffix=='.gz' and 'AUDIT_STATE' in p.name:continue
        if p.name=='AUDIT_WORKING_NOTES.md':continue
        select(p,'completed audit: unabridged tables/configurations/reports/curves',force=True)
    original={}
    with (AUDIT/'09_reviewer_handoff/FILE_AND_SOURCE_MANIFEST.csv').open() as f:
        for r in csv.DictReader(f):
            if r['record_type'].startswith('ORIGINAL'):
                original[r['path']]=r
                if r['record_type']=='ORIGINAL_INPUT':select(r['path'],'original audit evidence / fitted metadata / split / history')
    # Preserve complete implementation modules, including support imports and archived source versions.
    for folder in ['src','scripts','configs','tests/reassemble','tests/phm2026','tests/thesis',
                   'CROSS_DATASET_COMPARISON/src','CROSS_DATASET_COMPARISON/configs',
                   'MSM/src','MSM/tests','MSM/configs','MSM/99_preserved_previous_work/MILLING_DATASET/source',
                   'HANDOVER/src','HANDOVER/tests','VIFAILBACK/src','VIFAILBACK/scripts','VIFAILBACK/configs',
                   '00_experiments',LEGACY+'/source',LEGACY+'/tests',LEGACY+'/config',LEGACY+'/data_manifests']:
        tree(folder,{'.py','.yaml','.yml','.toml','.ini','.cfg'} if folder.startswith(('src','scripts','tests','00_experiments')) else None)
    # Existing phase receipts, explicit amendments, gradient/normalization checks and protocols.
    tree(BASE);tree(FOLLOW)
    for folder in ['VIFAILBACK/04_evaluation_splits','MSM/04_experiment_protocol',
                   'HANDOVER/experiments/common_support_v2/04_experiment_protocol']:
        tree(folder)
    # Official metadata are documentation, not raw recordings.
    select('HANDOVER/01_raw_dataset/source_evidence/zenodo_record_10708763.json','official participant/split documentation',force=True)
    tree('HANDOVER/01_raw_dataset/author_code',{'.py','.md','.txt','.json'})
    for pattern in ['pyproject.toml','setup.cfg','setup.py','requirements*.txt','environment*.yml','environment*.yaml','AGENTS.md']:
        for p in REPO.glob(pattern):select(p,'dependency/repository provenance')
    for p in ['docs/active_scope.md','docs/data_boundaries.md','docs/output_policy.md']:
        select(p,'preservation and provenance policy')
    return original


def copy_files(original):
    audit_expected={}
    with (AUDIT/'09_reviewer_handoff/FILE_AND_SOURCE_MANIFEST.csv').open() as f:
        for r in csv.DictReader(f):
            if r['record_type']=='AUDIT_OUTPUT':audit_expected[str(AUDIT.relative_to(REPO)/r['path'])]=r['sha256']
    patterns=[re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
              re.compile(rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),re.compile(rb'\bgh[pousr]_[A-Za-z0-9]{30,}\b'),
              re.compile(rb'\bgithub_pat_[A-Za-z0-9_]{40,}\b'),re.compile(rb'\bhf_[A-Za-z0-9]{30,}\b')]
    conflicts=[]
    for i,(name,role) in enumerate(sorted(SELECTED.items()),1):
        p=REPO/name;dest=MIRROR/name;dest.parent.mkdir(parents=True,exist_ok=True)
        before=p.stat();actual=sha(p)
        expected=original.get(name,{}).get('sha256',audit_expected.get(name,''))
        if expected and expected!=actual:conflicts.append({'path':name,'audit_sha256':expected,'export_sha256':actual})
        # Never inspect credential files; the path allowlist above excludes them entirely.
        if p.suffix in SMALL and p.stat().st_size<16*1024**2:
            data=p.read_bytes()
            if any(pattern.search(data) for pattern in patterns):
                SKIPPED[name]='Potential credential literal detected; value not exported or logged';continue
        shutil.copyfile(p,dest)
        assert sha(dest)==actual
        assert p.stat().st_size==before.st_size and p.stat().st_mtime_ns==before.st_mtime_ns
        SOURCE_ROWS.append({'package_path':str(dest.relative_to(ROOT)),'original_source_path':name,'role':role,
            'original_bytes':before.st_size,'original_sha256':actual,'audit_recorded_sha256':expected or 'NOT RECORDED',
            'copy_status':'BYTE_IDENTICAL'})
        if i%1000==0:print('COPIED',i,'of',len(SELECTED),flush=True)
    write_json(ROOT/'SOURCE_HASH_CONFLICTS.json',conflicts)
    assert not conflicts,'Original selected source changed since completed audit; do not silently export different evidence'


def external_index(original):
    rows=[]
    for name,r in sorted(original.items()):
        if (MIRROR/name).is_file():continue
        reason=SKIPPED.get(name)
        if not reason:
            reason='Checkpoint/serialized model binary: intentionally external' if Path(name).suffix.lower() in BINARY else 'Large prediction/feature bank or additional historical evidence: original path retained'
        rows.append({'original_source_path':name,'bytes':r['bytes'],'sha256':r['sha256'],'reason':reason})
    write_csv(ROOT/'EXTERNAL_ARTIFACTS.csv',rows)
    return rows


def rewrite_links():
    # Keep narrative/data unchanged; only make local Markdown navigation portable.
    token=re.compile(r'(?<!!)\[([^\]\n]*)\]\(([^)\n]+)\)')
    for p in sorted(MIRROR.rglob('*.md')):
        s=p.read_text()
        def convert(m):
            label,target=m.groups()
            if target.startswith(('http://','https://','mailto:','#')):return m.group(0)
            raw=target.strip('<>');base=raw.split('#',1)[0]
            if not base:return m.group(0)
            decoded=urllib.parse.unquote(base)
            resolved=(p.parent/decoded).resolve()
            if resolved.is_relative_to(ROOT) and resolved.exists():return m.group(0)
            # Original absolute repository links can be made relative inside the mirror.
            if decoded.startswith(str(REPO)+'/'):
                alternate=MIRROR/decoded[len(str(REPO))+1:]
                if alternate.exists():return '['+label+']('+urllib.parse.quote(os.path.relpath(alternate,p.parent),safe='/')+')'
            original_doc=Path(str(p.relative_to(MIRROR)))
            if Path(decoded).is_absolute():original_target=decoded
            else:original_target=os.path.normpath(str(original_doc.parent/decoded))
            number=len(LINK_REWRITES)+1
            LINK_REWRITES.append({'reference_id':f'EXT{number:05d}','document':str(p.relative_to(ROOT)),
                'original_link_target':target,'original_source_path':original_target,
                'disposition':'external evidence; see EXTERNAL_ARTIFACTS.csv for recorded paths/hashes'})
            replacement=urllib.parse.quote(os.path.relpath(ROOT/'EXTERNAL_REFERENCES.md',p.parent),safe='/')
            return '['+label+']('+replacement+')'
        changed=token.sub(convert,s)
        # Image references outside the chosen reports also need an explicit external destination.
        def image_convert(m):
            label,target=m.groups()
            if target.startswith(('https:','http:','data:')):return m.group(0)
            resolved=(p.parent/urllib.parse.unquote(target.split('#')[0].strip('<>'))).resolve()
            if resolved.is_relative_to(ROOT) and resolved.is_file():return m.group(0)
            LINK_REWRITES.append({'reference_id':f'EXT{len(LINK_REWRITES)+1:05d}','document':str(p.relative_to(ROOT)),
                'original_link_target':target,'original_source_path':os.path.normpath(str(Path(str(p.relative_to(MIRROR))).parent/target)),
                'disposition':'external image/raw example not included'})
            return '['+label+' (external figure)]('+urllib.parse.quote(os.path.relpath(ROOT/'EXTERNAL_REFERENCES.md',p.parent),safe='/')+')'
        changed=re.sub(r'!\[([^\]\n]*)\]\(([^)\n]+)\)',image_convert,changed)
        if changed!=s:p.write_text(changed)
    write_csv(ROOT/'LINK_TARGET_TRANSFORMATIONS.csv',LINK_REWRITES)


def readme():
    a='repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/'
    rows=[
      ('1. Executive summary,Tables A–H',a+'01_executive_overview/EXECUTIVE_AUDIT_SUMMARY.md'),
      ('2. Complete model configuration table',a+'03_hyperparameter_configuration/ALL_MODEL_CONFIGURATION_TABLE.md'),
      ('2/11. Every effective run configuration',a+'03_hyperparameter_configuration/EFFECTIVE_CONFIGURATIONS.json'),
      ('3. Hyperparameter tuning history',a+'03_hyperparameter_configuration/HYPERPARAMETER_TUNING_HISTORY.md'),
      ('4. All model results',a+'05_results/ALL_MODEL_RESULTS_SUMMARY.csv'),
      ('4/5. All numeric metrics,with seed/fold/scope',a+'05_results/ALL_RECORDED_METRICS_LONG.csv'),
      ('5. Exact training-run and seed/fold identities',a+'04_training_and_checkpoints/TRAINING_RUN_INVENTORY.csv'),
      ('6. Scientific comparability matrix',a+'05_results/COMPARABILITY_MATRIX.csv'),
      ('7. Model-selection evidence',a+'08_future_hpo_readiness/MODEL_SELECTION_EVIDENCE_TABLE.md'),
      ('8. HPO readiness and constraints',a+'08_future_hpo_readiness/HPO_READINESS_AND_CONSTRAINTS.md'),
      ('9. CNN loss curves',a+'06_dataset_specific/REASSEMBLE/100E_LOSS.png'),
      ('9. Validation AP curves',a+'06_dataset_specific/REASSEMBLE/100E_VALIDATION_AP.png'),
      ('9. LR schedules',a+'06_dataset_specific/REASSEMBLE/100E_LEARNING_RATES.png'),
      ('9/11. All C20 outer-refit curves',a+'06_dataset_specific/REASSEMBLE/C20_OUTER_REFIT_CURVES.png'),
      ('10. Full100-epoch comparison',a+'06_dataset_specific/REASSEMBLE/FROZEN_VS_FINETUNED_100_EPOCHS.md'),
      ('11. C20 status/configuration/results narrative',a+'06_dataset_specific/REASSEMBLE/MODEL_AND_CONFIGURATION_AUDIT.md'),
      ('11. Complete REASSEMBLE results',a+'06_dataset_specific/REASSEMBLE/COMPLETE_RESULTS.csv'),
      ('11. Complete epoch histories',a+'06_dataset_specific/REASSEMBLE/EPOCH_HISTORIES.csv'),
      ('12. Frozen/full-CNN fitter','repository/'+BASE+'/26102026_source/phase_training.py'),
      ('12/15. Architecture,optimizer and scheduler','repository/'+BASE+'/26102026_source/phase_model.py'),
      ('12. Original frozen branch training','repository/src/reassemble/section1_models.py'),
      ('12. C20 launcher and override','repository/'+BASE+'/26102026_c_only_20epoch_revision_01/26102026_source/c20_train.py'),
      ('12. Full/frozen100 launcher','repository/'+BASE+'/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_source/compare100_train.py'),
      ('12. Original F2 fitting and nested OOF','repository/src/reassemble/section1b.py'),
      ('12.100-epoch static-sensor F2 follow-up','repository/'+FOLLOW+'/src/evaluate.py'),
      ('13. Original sensor model and training settings','repository/configs/reassemble/section1.json'),
      ('13. External visual/sensor/fusion implementations','repository/CROSS_DATASET_COMPARISON/src/external_eval/models.py'),
      ('13. ViFailback sensor implementations','repository/VIFAILBACK/src/vifailback/baselines.py'),
      ('14. Recorded overfitting diagnostic',a+'06_dataset_specific/REASSEMBLE/TRAINING_GENERALIZATION_DIAGNOSTICS.md'),
      ('14. Recorded dropout/weight decay/augmentation',a+'03_hyperparameter_configuration/ALL_RUN_HYPERPARAMETERS.csv'),
      ('15. Checkpoint-selection audit',a+'04_training_and_checkpoints/CHECKPOINT_SELECTION_AUDIT.md'),
      ('16. Original REASSEMBLE nested splits','repository/runs/reassemble/20260927T154732Z-section1/nested_splits.json'),
      ('16. Phase1 actual fit/split plan','repository/'+BASE+'/26102026_evidence/PHASE1_FIT_PLAN.json'),
      ('16. External evaluation and OOF protocol','repository/CROSS_DATASET_COMPARISON/src/external_eval/evaluate.py'),
      ('16. ViFailback task partitions','repository/VIFAILBACK/04_evaluation_splits/train_validation_test/20261029T004900Z/fit_partitions.json'),
      ('16. MSM evaluation protocol','repository/MSM/04_experiment_protocol/split_protocol.md'),
      ('16. Handover protocol/participant limitation','repository/HANDOVER/experiments/common_support_v2/04_experiment_protocol/split_protocol.md'),
      ('17. Scientific missing evidence',a+'07_scientific_validity/MISSING_EVIDENCE.md'),
      ('17. Historical audit source manifest',a+'09_reviewer_handoff/FILE_AND_SOURCE_MANIFEST.csv'),
    ]
    for _,path in rows:assert (ROOT/path).is_file(),path
    body='''# HPO model-selection independent-review package

This portable export packages the completed2026-11-03 audit and the existing implementation evidence for independent model-selection discussion. No audit was rerun,no training/tuning/inference was started,and no experiment,checkpoint,label or result was modified. No final model or HPO budget is selected.

## Where to find every requested item

| Requested item | Package location |
|---|---|
'''
    for label,path in rows:body+='| '+label+' | ['+Path(path).name+']('+urllib.parse.quote(path,safe='/')+') |\n'
    body+='''
## Preserve run-level differences

The full configuration JSON/CSV,parameter provenance,all model metrics,per-seed/per-fold results and epoch histories are included without row reduction. Filter dataset,experiment,seed,fold,evaluation_scope,protocol,corruption,threshold and metric_path before aggregating. MSM pooled AP and mean-fold AP remain distinct. Original F2 and the100-epoch pilot have different stacking designs. C20 has25 completed20-epoch fits at seed42;the other50 original fits are deferred and C20 F2 finalization has not executed. Handover participant-OOF fusion and Vi full/transfer classifier training remain unexecuted. These historical findings are not re-evaluated by this export.

Every original implementation/configuration path is preserved below `repository/`,including support modules,legacy source versions,training receipts and split plans. Use `repository/` as the root when interpreting repository-relative values. Scientific configuration values and result cells are unchanged. Scripts are included for inspection;the package does not automatically run them and it does not contain the raw inputs/large weights needed for a training replay.

## External artifacts and portable references

Large checkpoint binaries,serialized estimators,raw recordings/datasets,feature arrays/caches and bulk prediction banks are intentionally external. Their original paths,recorded SHA256 identities and sizes are in [EXTERNAL_ARTIFACTS.csv](EXTERNAL_ARTIFACTS.csv),the historical checkpoint inventory and source manifest. Lack of a local binary is not missing scientific reporting. Available fitted JSON coefficients/scalers,configuration metadata and histories are included where selected.

Local Markdown links to included files resolve inside this package. Links to intentionally external historical evidence are redirected to [EXTERNAL_REFERENCES.md](EXTERNAL_REFERENCES.md);[LINK_TARGET_TRANSFORMATIONS.csv](LINK_TARGET_TRANSFORMATIONS.csv) retains the original target. Only exported Markdown navigation was changed. Original code,configuration values,metric rows and source evidence remain byte-identical. [SOURCE_FILE_MANIFEST.csv](SOURCE_FILE_MANIFEST.csv) records original and exported hashes,including any navigation-only transformation. Historical audit manifests refer to the original audit bytes;the package manifest governs exported bytes.

Derived working-state gzip duplicates,temporary synthetic checkpoint fixtures and in-progress audit notes are excluded;their complete final configurations/results remain included. [EXPORT_OMISSIONS.csv](EXPORT_OMISSIONS.csv) lists those audit-only exclusions. Credentials,environment secrets and raw datasets are not exported.

## Integrity and verification

[PACKAGE_MANIFEST.csv](PACKAGE_MANIFEST.csv) lists SHA256 and size for every package file except its own recursive entry. [EXPORT_VALIDATION.json](EXPORT_VALIDATION.json) records the packaging checks. The ZIP was CRC-tested,extracted into an independent temporary directory,and verified by file hash and internal Markdown references. No original experiment modules were imported or executed. Git HEAD and staged-state identity are recorded in [EXPORT_PROVENANCE.json](EXPORT_PROVENANCE.json);nothing was staged,committed or pushed.

After extracting,use `python package_tools/verify_package.py PATH_TO_PACKAGE_ROOT` to repeat package-integrity and reference checks using only the standard library. This verifies the export,not the research experiments.
'''
    (ROOT/'README.md').write_text(body)
    (ROOT/'EXTERNAL_REFERENCES.md').write_text('''# Explicitly external historical evidence

The link followed from a historical report points to evidence intentionally not copied,an old external location,or a historical link absent from the completed audit. It is not an unresolved internal package reference.

- [Original targets and referring documents](LINK_TARGET_TRANSFORMATIONS.csv)
- [Available external artifact paths,sizes and SHA256 identities](EXTERNAL_ARTIFACTS.csv)
- [Scientific evidence limitations](repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/07_scientific_validity/MISSING_EVIDENCE.md)

Raw datasets,large checkpoints and numerical caches remain at their original source locations. No binary was substituted or fitted to fill a gap. Archived configuration/source path literals retain their historical values;they do not assert that external data are bundled. Internal review navigation uses package-relative links.
''')


def main():
    if '--resume-validation' in sys.argv:
        return resume_validation()
    assert not ARCHIVE.exists(),'Never overwrite an existing archive'
    assert not MIRROR.exists(),'Never overwrite an existing package mirror'
    start=dt.datetime.now(dt.timezone.utc).isoformat()
    git=lambda *args:subprocess.check_output(['git',*args],cwd=REPO,text=True)
    head=git('rev-parse','HEAD');staged=git('diff','--cached','--name-status')
    original=plan();print('PLAN',len(SELECTED),'files',sum((REPO/p).stat().st_size for p in SELECTED),'bytes',flush=True)
    copy_files(original);externals=external_index(original);readme();rewrite_links()
    # Include byte identities for all copied evidence and explicitly identify link-only changes.
    for r in SOURCE_ROWS:
        p=ROOT/r['package_path'];r['exported_sha256']=sha(p);r['exported_bytes']=p.stat().st_size
        if r['exported_sha256']!=r['original_sha256']:
            assert p.suffix=='.md';r['copy_status']='EXPORTED_MARKDOWN_LINK_TARGETS_ONLY'
    write_csv(ROOT/'SOURCE_FILE_MANIFEST.csv',SOURCE_ROWS)
    omissions=[]
    selected=set(SELECTED)
    for p in AUDIT.rglob('*'):
        if p.is_file() and not p.is_symlink() and str(p.relative_to(REPO)) not in selected:
            omissions.append({'original_source_path':str(p.relative_to(REPO)),'bytes':p.stat().st_size,
                'reason':'Redundant derived audit work state / transient note / synthetic checkpoint fixture; final evidence retained'})
    write_csv(ROOT/'EXPORT_OMISSIONS.csv',omissions)
    assert head==git('rev-parse','HEAD');assert staged==git('diff','--cached','--name-status')
    write_json(ROOT/'EXPORT_PROVENANCE.json',{'started_utc':start,'assembled_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
        'source_audit':str(AUDIT.relative_to(REPO)),'git_head':head.strip(),
        'staged_state_sha256_before_and_after':hashlib.sha256(staged.encode()).hexdigest(),
        'existing_worktree_preserved':True,'training_or_tuning_executed':False,'research_audit_repeated':False,
        'commit_push_stage_performed':False,'original_code_config_result_cells_modified':False,
        'copied_source_files':len(SOURCE_ROWS),'external_artifact_rows':len(externals),'link_target_transformations':len(LINK_REWRITES),
        'export_size_policy':'Unabridged audit tables/configuration/history/curves; original code and small metadata; external large weights/raw/cache banks',
        'secret_files_accessed':False,'potential_credential_literals_rejected':len(SKIPPED)})
    from verify_package import verify_content,verify_manifest
    # The manifest is generated after content validation; create its readable header for internal navigation now.
    write_csv(ROOT/'PACKAGE_MANIFEST.csv',[],['package_path','bytes','sha256'])
    write_json(ROOT/'EXPORT_VALIDATION.json',{'status':'PACKAGING_VERIFICATION_IN_PROGRESS'})
    content=verify_content(ROOT)
    write_json(ROOT/'EXPORT_VALIDATION.json',{'package_content_check':content,'source_hash_conflicts':0,
        'copied_sources_hash_verified':len(SOURCE_ROWS),'archive_checks':'CRC plus independent extraction and manifest/reference verification; receipt written beside ZIP',
        'original_audit_checks_reused':True,'no_model_execution':True})
    # Every original selected source is checked for preservation after assembly; no model/dataset evaluation.
    for r in SOURCE_ROWS:assert sha(REPO/r['original_source_path'])==r['original_sha256']
    write_csv(ROOT/'PACKAGE_MANIFEST.csv',[{'package_path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)}
        for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='PACKAGE_MANIFEST.csv'])
    verify_manifest(ROOT)
    with zipfile.ZipFile(ARCHIVE,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
        for p in sorted(ROOT.rglob('*')):
            if p.is_file():z.write(p,arcname=ROOT.name+'/'+str(p.relative_to(ROOT)))
    print('ZIP_WRITTEN',ARCHIVE.stat().st_size,flush=True)
    with zipfile.ZipFile(ARCHIVE) as z:
        assert z.testzip() is None
        for info in z.infolist():
            p=Path(info.filename);assert not p.is_absolute() and '..' not in p.parts
            assert p.parts[0]==ROOT.name
        with tempfile.TemporaryDirectory(prefix='hpo_review_extract_',dir='/tmp') as temp:
            z.extractall(temp);extracted=Path(temp)/ROOT.name
            verified=verify_manifest(extracted);content_extracted=verify_content(extracted)
            assert content_extracted==content
    archive_sha=sha(ARCHIVE)
    receipt={'archive_path':str(ARCHIVE.relative_to(REPO)),'archive_bytes':ARCHIVE.stat().st_size,'archive_sha256':archive_sha,
        'package_files':sum(p.is_file() for p in ROOT.rglob('*')),'copied_source_files':len(SOURCE_ROWS),
        'manifest_verification':verified,'content_verification':content_extracted,
        'CRC_verified':True,'independent_extraction_verified':True,'Git_HEAD_unchanged':head==git('rev-parse','HEAD'),
        'Git_staged_state_unchanged':staged==git('diff','--cached','--name-status'),
        'completed_utc':dt.datetime.now(dt.timezone.utc).isoformat()}
    receipt_path=ARCHIVE.with_suffix('.verification.json')
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
    ARCHIVE.with_suffix('.zip.sha256').write_text(archive_sha+'  '+ARCHIVE.name+'\n')
    print(json.dumps(receipt),flush=True)


def resume_validation():
    """Resume this task-owned assembled export without touching/copying source experiments again."""
    assert not ARCHIVE.exists()
    provenance=json.loads((ROOT/'EXPORT_PROVENANCE.json').read_text())
    assert provenance['source_audit']==str(AUDIT.relative_to(REPO))
    assert provenance['training_or_tuning_executed'] is False
    assert json.loads((ROOT/'SOURCE_HASH_CONFLICTS.json').read_text())==[]
    rows=list(csv.DictReader((ROOT/'SOURCE_FILE_MANIFEST.csv').open()))
    for row in rows:
        assert sha(ROOT/row['package_path'])==row['exported_sha256']
        assert sha(REPO/row['original_source_path'])==row['original_sha256']
    git=lambda *args:subprocess.check_output(['git',*args],cwd=REPO,text=True)
    head=git('rev-parse','HEAD');staged=git('diff','--cached','--name-status')
    assert head.strip()==provenance['git_head']
    assert hashlib.sha256(staged.encode()).hexdigest()==provenance['staged_state_sha256_before_and_after']
    from verify_package import verify_content,verify_manifest
    write_json(ROOT/'EXPORT_VALIDATION.json',{'status':'PACKAGING_VERIFICATION_IN_PROGRESS'})
    content=verify_content(ROOT)
    print('CONTENT_VERIFIED',json.dumps(content),flush=True)
    write_json(ROOT/'EXPORT_VALIDATION.json',{'package_content_check':content,'source_hash_conflicts':0,
        'copied_sources_hash_verified':len(rows),'archive_checks':'CRC plus independent extraction and manifest/reference verification; receipt beside ZIP',
        'original_audit_checks_reused':True,'no_model_execution':True})
    write_csv(ROOT/'PACKAGE_MANIFEST.csv',[{'package_path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)}
        for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='PACKAGE_MANIFEST.csv'])
    verify_manifest(ROOT)
    with zipfile.ZipFile(ARCHIVE,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
        for p in sorted(ROOT.rglob('*')):
            if p.is_file():z.write(p,arcname=ROOT.name+'/'+str(p.relative_to(ROOT)))
    print('ZIP_WRITTEN',ARCHIVE.stat().st_size,flush=True)
    with zipfile.ZipFile(ARCHIVE) as z:
        assert z.testzip() is None
        for info in z.infolist():
            p=Path(info.filename);assert not p.is_absolute() and '..' not in p.parts and p.parts[0]==ROOT.name
        with tempfile.TemporaryDirectory(prefix='hpo_review_extract_',dir='/tmp') as temp:
            z.extractall(temp);extracted=Path(temp)/ROOT.name
            verified=verify_manifest(extracted);assert verify_content(extracted)==content
    archive_sha=sha(ARCHIVE)
    receipt={'archive_path':str(ARCHIVE.relative_to(REPO)),'archive_bytes':ARCHIVE.stat().st_size,'archive_sha256':archive_sha,
        'package_files':sum(p.is_file() for p in ROOT.rglob('*')),'copied_source_files':len(rows),
        'manifest_verification':verified,'content_verification':content,
        'CRC_verified':True,'independent_extraction_verified':True,'Git_HEAD_unchanged':head==git('rev-parse','HEAD'),
        'Git_staged_state_unchanged':staged==git('diff','--cached','--name-status'),
        'completed_utc':dt.datetime.now(dt.timezone.utc).isoformat()}
    ARCHIVE.with_suffix('.verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
    ARCHIVE.with_suffix('.zip.sha256').write_text(archive_sha+'  '+ARCHIVE.name+'\n')
    print(json.dumps(receipt),flush=True)

if __name__=='__main__':main()
