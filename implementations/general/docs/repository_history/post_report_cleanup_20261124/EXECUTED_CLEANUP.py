"""Gated, reversible dataset navigation/source consolidation and disposable-cache cleanup.

No repository mutation occurs until the fit, analysis, report and process gates
pass. Data, run artifacts, frozen code/config contents and credentials are not
read or removed. The earlier three-hour post-fit limit remains the outer budget.
"""
from __future__ import annotations
import ast
from collections import Counter
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

REPO=Path(os.environ.get('PI_REPO_ROOT',str(Path.cwd()))).resolve()
TASK=Path(__file__).resolve().parent
STUDY=REPO/'VIFAILBACK/experiments/matched_cnn_20_100_f2_20261111'
STOP=STUDY/'18_fit_stop_and_analysis_20261124T1955Z'
DEST=REPO/'implementations/general/docs/repository_history/post_report_cleanup_20261124'
PRIMITIVES=['__init__.py','alignment.py','section1_features.py','section1_models.py','section2_models.py']
AUTH='cool, then could you proceed with structural changes inspiring like VIFAILBACK but making it in implementations/ SO the overall structure is humanly readable and easily findable for datasets and for other folders think on how to make it clean and findable, making sure AI heavy unwanted files are removed, But do it once the final epoch and the report is over'

def utc():return dt.datetime.now(dt.timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def record(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    t=p.with_name(p.name+f'.writing.{os.getpid()}')
    t.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');os.replace(t,p)
def identity(p):
    s=p.stat();return [s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns]
def git_summary():
    lines=subprocess.check_output(['git','status','--short','--branch','--untracked-files=all'],cwd=REPO,text=True).splitlines()
    return {'branch':lines[0],'status_counts':dict(Counter(line[:2] for line in lines[1:]))}
def process_alive(pid):
    p=Path('/proc')/str(pid)/'stat'
    try:return p.read_text().rsplit(')',1)[1].split()[0]!='Z'
    except FileNotFoundError:return False
def gate():
    final=STOP/'FINAL_STATUS.json';state=STOP/'GUARD_STATUS.json'
    if not final.exists() or not state.exists():return False,'WAITING_FOR_FIT_AND_REPORT',None
    f=read(final)
    if f.get('stage')!='CLOSED_COMPLETED_SCOPE':return False,'REPORT_NOT_SUCCESSFULLY_CLOSED',f
    if read(state).get('stage')!='FINISHED':return False,'WAITING_FOR_STOP_GUARD_EXIT',f
    request=read(STOP/'CONTROL_REQUEST.json')
    if any(process_alive(request[k]['pid']) for k in ('controller','watcher')):
        return False,'WAITING_FOR_TRAINING_REPORT_PROCESSES_TO_EXIT',f
    launched=read(STOP/'LAUNCH_RECEIPT.json')
    if process_alive(launched['pid']):return False,'WAITING_FOR_STOP_GUARD_EXIT',f
    return True,'REPORT_COMPLETE',f

class Changes:
    def __init__(self):self.edits=[];self.moves=[];self.links=[];self.deleted=[]
    def save(self):record(DEST/'CHANGES.json',self.__dict__)
    def edit(self,relative,text):
        p=REPO/relative
        if p.is_symlink():raise RuntimeError(f'Refuse document edit through symlink: {relative}')
        before=p.read_bytes() if p.exists() else None
        data=text.encode()
        if before==data:return
        if before is not None:
            backup=DEST/'preimages'/relative;backup.parent.mkdir(parents=True,exist_ok=True)
            if backup.exists():raise FileExistsError(backup)
            backup.write_bytes(before)
        p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        self.edits.append({'path':relative,'before_sha256':hashlib.sha256(before).hexdigest() if before is not None else None,'after_sha256':sha(p)})
        self.save()
    def link(self,relative,target):
        p=REPO/relative;t=REPO/target
        if not t.exists():raise FileNotFoundError(t)
        if p.is_symlink():
            if p.resolve()!=t.resolve():raise RuntimeError(f'Conflicting link: {relative}')
            return
        if p.exists():raise FileExistsError(p)
        p.parent.mkdir(parents=True,exist_ok=True)
        p.symlink_to(os.path.relpath(t,p.parent),target_is_directory=t.is_dir())
        self.links.append({'path':relative,'target':target});self.save()
    def move(self,source,destination,keep_link=False):
        a=REPO/source;b=REPO/destination
        if a.is_symlink() or b.exists() or b.is_symlink():raise RuntimeError(f'Unsafe move {source} -> {destination}')
        files={str(p.relative_to(a)):identity(p) for p in a.rglob('*') if p.is_file() and not p.is_symlink()} if a.is_dir() else {}
        before=identity(a);b.parent.mkdir(parents=True,exist_ok=True);a.rename(b)
        assert identity(b)==before
        assert all(identity(b/name)==expected for name,expected in files.items())
        self.moves.append({'source':source,'destination':destination,'identity':before,'regular_files_checked':len(files) if files else 1,'bytes_unchanged':'rename, device/inode/size/mtime preserved'})
        if keep_link:self.link(source,destination)
        self.save()
    def delete_bytecode(self,cache):
        # Only ordinary bytecode with retained Python source is disposable here.
        if cache.is_symlink():raise RuntimeError(f'Cache symlink refused: {cache}')
        for p in list(cache.iterdir()):
            source=cache.parent/(p.name.split('.')[0]+'.py')
            canonical=REPO/'implementations/REASSEMBLE/src/reassemble'/source.name
            if p.is_symlink() or not p.is_file() or p.suffix!='.pyc' or not (source.is_file() or canonical.is_file()):
                raise RuntimeError(f'Unexpected cache content retained: {p}')
        for p in list(cache.iterdir()):
            self.deleted.append({'path':str(p.relative_to(REPO)),'bytes':p.stat().st_size,'reason':'Inactive disposable Python bytecode; corresponding source retained'})
            p.unlink()
        cache.rmdir();self.save()

def table(rows,headers=('Stage','Location')):return '\n'.join([f'| {headers[0]} | {headers[1]} |','|---|---|']+[f'| {a} | {b} |' for a,b in rows])
def link(label,path):return f'[{label}]({path})'

def dataset_guides(changes):
    entries={
      'PHM2026':('Gear-condition research using photos and vibration. Image-derived targets are proxy supervision, not independently validated physical damage labels.',[
       ('01 — Data and targets',link('Data configuration','configs/dataset.yaml')+'; '+link('Target-version ledger','docs/studies/TARGET_VERSION_LEDGER.md')),
       ('02 — Verification and preprocessing',link('Data contracts and preprocessing','src/phm2026')+'; '+link('Derived vibration features','results/processed/raw_vibration')),
       ('03 — Protocols and experiments',link('Study workspaces','experiments')+'; '+link('Experiment configurations','configs/experiments')),
       ('04 — Models and training',link('Model implementations','src/phm2026/models')+'; '+link('Training entry points','scripts/training')),
       ('05 — Results and limitations',link('Saved runs','results/runs')+'; '+link('Study reports','docs/studies')),
       ('06 — Recovery and history',link('Raw-data recovery','docs/RAW_DATA_RECOVERY.md')+'; '+link('Research history','docs/research_history'))],
       'Canonical selection remains EXP-A Runs 1–5, EXP-B Runs 1–7 and EXP-F Runs 1–8. The protected initial EDA remains at `experiments/exp_a_initial_eda_r1_r3_r5/` in the repository root. Raw-retirement records do not authorize another deletion or restoration.'),
      'REASSEMBLE':('Retrospective completed-action failure classification using visual and numerical sensor representations. This is not online early warning.',[
       ('01 — Labels, alignment and protocols',link('Methodology','docs')+'; '+link('Configurations','configs')),
       ('02 — Representations and models',link('Implementation','src/reassemble')+'; '+link('Core walkthrough','experiments/core/README.md')),
       ('03 — Core training and fusion',link('Unimodal baselines','results/runs/unimodal_baselines_visual_sensor')+'; '+link('Static F2 and sensor controls','results/runs/sensor_controls_f2_nested_stacking')),
       ('04 — Further experiments',link('Additional studies','experiments/additional')+'; '+link('CNN seed stability','experiments/cnn_seed_stability')),
       ('05 — Assessment and robustness',link('Fusion comparison','results/runs/fusion_method_comparison')+'; '+link('Missing/degraded modalities','results/runs/missing_degraded_modality_robustness')),
       ('06 — Reports and completion',link('Core closure','results/artifacts/reports/REASSEMBLE_COMPLETION_STATUS.md')+'; '+link('Extension closure','results/artifacts/reports/ADDITIONAL_IMPROVEMENTS_STATUS.md')+'; '+link('All scientific reports','results/artifacts/reports'))],
       'Core, extensions and later CNN studies retain distinct protocols, cohorts and completion boundaries. The source package now lives here. Root `src/reassemble` is a compatibility link preserving historical imports and source identities. Original phase-one and bootstrap fit references remain at their recorded root paths.'),
      'MSM':('Metal-milling interval classification from video and machine measurements. Earlier milling work is part of this dataset history, not another independent dataset.',[
       ('01 — Dataset and labels',link('Label/alignment records','results/02_labels_and_alignment')),
       ('02 — Preprocessing',link('Processed model inputs','results/03_processed_model_inputs')),
       ('03 — Protocol',link('Experiment protocol','results/04_experiment_protocol')),
       ('04 — Models and training',link('Adapters','src')+'; '+link('Trained-model records','results/05_trained_models')),
       ('05 — Assessment and robustness',link('Evaluation','results/06_evaluation_results')+'; '+link('Robustness','results/07_robustness_experiments')),
       ('06 — Examples and handoff',link('Examples and EDA','results/08_visual_examples_and_eda')+'; '+link('Research handoff','results/09_final_reports/REVIEW_HANDOFF.md')),
       ('07 — Earlier studies',link('Legacy milling studies','experiments/legacy'))],
       'Native inputs remain at repository-root `MSM/01_raw_dataset/` and `MILLING DATASET/data/`. Failed scientific gates and study eligibility remain authoritative. Shared fitting/evaluation implementation is in ../cross_dataset/src/external_eval/.'),
      'HANDOVER':('Robot handover success/failure classification. Recording/task groups do not establish participant independence.',[
       ('01 — Labels and alignment',link('Data-contract records','results/02_labels_and_alignment')),
       ('02 — Preprocessing and protocol',link('Processed inputs','results/03_processed_model_inputs')+'; '+link('Protocol','results/04_experiment_protocol')),
       ('03 — Models and training',link('Adapters','src')+'; '+link('Training records','results/05_trained_models')),
       ('04 — Main eligible study',link('Common-support study','experiments/common_support_v2')),
       ('05 — Assessment and robustness',link('Evaluation','results/06_evaluation_results')+'; '+link('Robustness','results/07_robustness_experiments')),
       ('06 — Examples and handoff',link('Examples','results/08_visual_examples_and_eda')+'; '+link('Research handoff','results/09_final_reports/REVIEW_HANDOFF.md'))],
       'Native inputs stay at repository-root HANDOVER/01_raw_dataset/. Preserve participant-identity limitations and mandatory participant-safe OOF gates. Missing identity is not permission to substitute trial groups or in-sample stacking.'),
      'REBOOT':('Dataset, annotation and visual-observability feasibility. Feasibility evidence is not completed model training.',[
       ('01 — Dataset overview',link('Source and overview','results/00_dataset_overview')),
       ('02 — Labels and alignment',link('Annotations','results/02_labels_and_annotations')+'; '+link('Video/sensor alignment','results/03_video_sensor_alignment')),
       ('03 — Visual review',link('Failure review','results/04_visual_failure_review')),
       ('04 — Architecture and evaluation gates',link('Architecture compatibility','results/05_architecture_compatibility')+'; '+link('Evaluation feasibility','results/06_evaluation_feasibility')),
       ('05 — Research decision',link('Decision and remaining gates','results/07_research_decision')),
       ('06 — Examples',link('Examples and EDA','results/08_visual_examples_and_eda'))],
       'Native inputs and retained investigation runs remain in repository-root REBOOT/. Training is not authorized by this guide; annotation/control/grouping and independent review gates remain necessary.'),
    }
    for name,(description,rows,boundary) in entries.items():
        text=f'# {name}\n\n{description}\n\n{table(rows)}\n\n'
        parts=[]
        for label,child in [('Source','src'),('Scripts','scripts'),('Configurations','configs'),('Tests','tests'),('Documentation','docs')]:
            if (REPO/'implementations'/name/child).exists():parts.append(link(label,child))
        text+=' · '.join(parts)+'\n\n'+boundary+'\n\n'
        text+='Each study\'s frozen protocol, fit manifests and assessment records determine what ran and which comparisons are eligible. A folder or script is not execution evidence. Historical commands retain their original paths; navigation/package checks are not model reproduction.\n\n'
        text+='[All datasets](../README.md) · [Repository map](../../REPO_MAP.md)\n'
        changes.edit(f'implementations/{name}/README.md',text)

def main_phase(final):
    deadline=dt.datetime.fromisoformat(final['target_completed_utc']).timestamp()+10800
    if time.time()+900>deadline:raise RuntimeError('Insufficient time remains inside the existing three-hour post-fit limit; no restructure started')
    gpu=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
    if gpu:raise RuntimeError('Another GPU process is present; defer structural changes without touching it')
    if DEST.exists():raise FileExistsError(DEST)
    # Preflight all shared source collisions and bytecode before the first move.
    source=REPO/'src/reassemble';canonical=REPO/'implementations/REASSEMBLE/src/reassemble'
    if source.is_symlink():raise RuntimeError('Source layout changed since planning')
    if set(p.name for p in source.iterdir())-set(PRIMITIVES)-{'__pycache__'}:raise RuntimeError('Unexpected root package content')
    source_hashes={}
    for n in PRIMITIVES:
        if not (source/n).is_file() or (canonical/n).exists():raise RuntimeError(f'Primitive collision {n}')
        source_hashes[n]=sha(source/n)
    cache=source/'__pycache__'
    if cache.exists():
        for p in cache.iterdir():
            original_source=source/(p.name.split('.')[0]+'.py')
            moved_source=canonical/original_source.name
            if p.is_symlink() or not p.is_file() or p.suffix!='.pyc' or not (original_source.is_file() or moved_source.is_file()):
                raise RuntimeError(f'Unexpected root cache entry retained: {p}')
    DEST.mkdir(parents=True)
    shutil.copy2(__file__,DEST/'EXECUTED_CLEANUP.py')
    record(DEST/'AUTHORIZATION.json',{'utc':utc(),'researcher_instruction':AUTH,'completion_gate':final,
        'scope':'One post-report organization phase; archive old AI notes, remove only ordinary disposable tool caches, preserve raw/frozen scientific evidence',
        'postfit_deadline_utc':dt.datetime.fromtimestamp(deadline,dt.timezone.utc).isoformat()})
    record(DEST/'GIT_BEFORE.json',git_summary())
    c=Changes()
    record(DEST/'STATUS.json',{'utc':utc(),'stage':'SOURCE_CONSOLIDATION'})
    for name in PRIMITIVES:c.move('src/reassemble/'+name,'implementations/REASSEMBLE/src/reassemble/'+name)
    if cache.exists():c.delete_bytecode(cache)
    source.rmdir();c.link('src/reassemble','implementations/REASSEMBLE/src/reassemble')
    for package,where in [('phm2026','implementations/PHM2026/src/phm2026'),('intel_welding','implementations/INTEL_WELDING/src/intel_welding'),('external_eval','implementations/cross_dataset/src/external_eval')]:
        c.link('src/'+package,where)
    assert all(sha(source/n)==source_hashes[n] for n in PRIMITIVES)
    # The canonical VIFAILBACK view uses links so immutable raw/frozen run paths do not move.
    folders=['src','scripts','configs','tests','experiments','01_original_dataset','02_dataset_verification','03_preprocessing','04_evaluation_splits','05_model_implementations','06_training_experiments','07_robustness_experiments','08_visual_examples_and_eda','09_evaluation_results','10_final_research_reports']
    for folder in folders:c.link('implementations/VIFAILBACK/'+folder,'VIFAILBACK/'+folder)
    c.link('implementations/VIFAILBACK/latest_results','VIFAILBACK/experiments/matched_cnn_20_100_f2_20261111/18_fit_stop_and_analysis_20261124T1955Z/completed_scope_analysis')
    vif='# VIFAILBACK\n\nMultiview completed-episode outcome classification. This is the canonical browsing entry under implementations/. Linked folders retain the original immutable data and frozen experiment locations; no raw data or checkpoint is copied or moved.\n\n'
    vif+=table([('01 — Dataset source',link('Original dataset and acquisition','01_original_dataset')),('02 — Verification',link('Labels, alignment and availability','02_dataset_verification')),('03 — Preprocessing',link('Representations','03_preprocessing')),('04 — Protocol and splits',link('Evaluation splits','04_evaluation_splits')+'; '+link('Study workspaces','experiments')),('05 — Models and training',link('Model definitions','05_model_implementations')+'; '+link('Training records','06_training_experiments')),('06 — Assessment',link('Dataset-level results','09_evaluation_results')+'; '+link('Latest completed-scope analysis','latest_results/RESULT_ANALYSIS.md')),('07 — Robustness',link('Condition-specific work','07_robustness_experiments')),('08 — Examples',link('Examples and EDA','08_visual_examples_and_eda')),('09 — Reports',link('Historical reports','10_final_research_reports')+'; '+link('Current training comparison','latest_results/TRAINING_COMPARISON.md'))])
    vif+='\n\n[Source](src) · [Scripts](scripts) · [Configurations](configs) · [Tests](tests)\n\nThe current training queue is closed by the researcher. Unexecuted fits are not negative model results. Use the study-local stop, coverage and analysis records for actual completion; the older dataset-level status may describe an earlier plan. No restart is authorized by this navigation.\n\n[Original workspace](../../VIFAILBACK/README.md) · [All datasets](../README.md) · [Repository map](../../REPO_MAP.md)\n'
    c.edit('implementations/VIFAILBACK/README.md',vif)
    dataset_guides(c)
    # Preserve AI notes intact as history rather than deleting unique provenance.
    for folder in ['parth_ws_bootstrap','thesis_writing']:
        a='implementations/general/research_workflow/'+folder
        b='implementations/general/docs/repository_history/ai_workflow_notes/'+folder
        if any(p.is_symlink() for p in (REPO/a).rglob('*')):raise RuntimeError('Unexpected AI-note symlink; retain without archival')
        c.move(a,b,keep_link=True)
    c.edit('implementations/general/docs/repository_history/ai_workflow_notes/README.md',
       '# Historical AI workflow notes\n\nOld prompt packs, planning notes and writing-session records are retained here unchanged. They are history, not current execution instructions. Original paths are compatibility links; no unique scientific or authorization record was deleted. Current task authority comes from the researcher and repository policies.\n\n- [Research prompt pack](parth_ws_bootstrap)\n- [Writing-session records](thesis_writing)\n')
    c.edit('implementations/general/research_workflow/README.md',
       '# Research workflow support\n\nUse dataset-specific guides for model execution. This folder retains older research-automation infrastructure and historical aliases. Saved queues do not authorize new work.\n\n- [Research rules and protocol template](automation/README.md)\n- [Archived AI prompt and writing-session notes](../docs/repository_history/ai_workflow_notes/README.md)\n- [Thesis documentation](../docs/thesis)\n- [General tools](../README.md)\n\nThe historical experiment previously called Task 4 remains excluded unless explicitly reauthorized.\n')
    general='# Research support\n\nRepository-wide tools and thesis material. Dataset-owned implementation belongs in the dataset folders; shared external evaluation belongs in cross_dataset/.\n\n'
    general+=table([('Thesis evidence and writing',link('Thesis records','docs/thesis')+'; '+link('Thesis tools','scripts/thesis')),('Repository maintenance',link('Maintenance tools','scripts/ops')+'; '+link('Maintenance checks','tests/ops')),('Dataset screening',link('Discovery and feasibility records','docs/dataset_research/README.md')),('Presentations',link('Generation tools','scripts/presentation')+'; '+link('Documents','docs/presentations')),('Shared EDA and fixtures',link('EDA utilities','scripts/eda')+'; '+link('Tiny synthetic fixtures','tests/fixtures')),('Historical evidence',link('Research reviews and retained outputs','results')+'; '+link('Repository history','docs/repository_history')+'; '+link('Storage history','docs/storage_history')),('AI workflow history',link('Archived notes','docs/repository_history/ai_workflow_notes/README.md')+'; '+link('Automation records','research_workflow/automation/README.md'))])
    general+='\n\nScientific protocols, authorization records, negative/incomplete results and required AI-use provenance remain retained. Old command records are historical; consult current dataset guides and the path mapping before reuse.\n\n[All datasets](../README.md) · [Repository map](../../REPO_MAP.md)\n'
    c.edit('implementations/general/README.md',general)
    dataset_rows=[]
    descriptions={'PHM2026':'Gear condition and image-derived proxy targets','PADERBORN':'Historical bearing-mechanism study','INTEL_WELDING':'Historical welding research and feasibility audits','MSM':'Metal-milling interval classification','HANDOVER':'Robot handover success/failure','REBOOT':'Annotation and visual-observability feasibility','REASSEMBLE':'Completed-action failure classification and fusion','VIFAILBACK':'Multiview manipulation outcomes'}
    for name,desc in descriptions.items():dataset_rows.append((link(name,name+'/README.md'),desc))
    index='# Datasets and research support\n\nChoose a dataset, then follow its numbered reading order from source and labels through protocol, models, assessment and reports. Numbering is navigation, not proof that a stage ran. Each study keeps its own protocol and evidence.\n\n'
    index+=table(dataset_rows,('Dataset','Research role'))+'\n\n## Repository-wide work\n\n- [Cross-dataset evaluation and comparisons](cross_dataset/README.md)\n- [Thesis, maintenance, presentations and research history](general/README.md)\n\nSource, scripts, configurations and tests live with their dataset where applicable. Data and frozen run references retain protected original paths; links expose them here without copying. Root src/ contains compatibility import links, not duplicate implementations.\n\n[Repository map](../REPO_MAP.md) · [Working instructions](../AGENTS.md)\n'
    c.edit('implementations/README.md',index)
    readme='# pi-multimodal-ad\n\nMaster’s thesis workspace for visual and numerical sensor representations, multimodal fusion and missing/degraded-modality evaluation.\n\nStart with **[Datasets and research support](implementations/README.md)**. Every dataset has a guide linking its inputs and labels, protocols, model implementation, saved assessment and reports.\n\n- [Cross-dataset comparisons](implementations/cross_dataset/README.md)\n- [Thesis and repository support](implementations/general/README.md)\n- [Complete repository map](REPO_MAP.md)\n- [VS Code implementations workspace](.vscode/thesis.code-workspace)\n\n## Reuse and evidence\n\nData and frozen experiments retain their original identities and paths. Raw inputs, checkpoints, negative results and incomplete work remain preserved. See each study’s protocol and actual fit records before drawing scientific conclusions. Proxy targets are not physical ground truth; independent dataset-specific fitting is not zero-shot generalization.\n\nThe post-report organization phase consolidates the shared REASSEMBLE source and repairs package visibility. It does not rerun models or validate every historical command. The [phase record](implementations/general/docs/repository_history/post_report_cleanup_20261124/STATUS.json) reports checks actually performed and any remaining source/configuration path issues. Dependencies remain in [pyproject.toml](pyproject.toml) and [requirements.txt](requirements.txt); no installation was performed by this phase.\n\nRead [AGENTS.md](AGENTS.md), [active scope](docs/active_scope.md), [data boundaries](docs/data_boundaries.md) and [output policy](docs/output_policy.md) before changing experiments or data. Protected identities include gtc-data-experiment/ and data/Full Dataset/ even when absent locally. Historical PHM EDA remains protected. The [REASSEMBLE cache-retention record](docs/maintenance/REASSEMBLE_CACHE_RETENTION.md) governs historical cache availability.\n\n[License](LICENSE)\n'
    c.edit('README.md',readme)
    mapping='# Repository map\n\nThe human-facing entry is [implementations/](implementations/README.md). Each dataset guide gives a staged route to its code, protocol, saved results and reports.\n\n'
    mapping+=table([(link('Dataset implementations','implementations/README.md'),'PHM2026, PADERBORN, INTEL_WELDING, MSM, HANDOVER, REBOOT, REASSEMBLE and VIFAILBACK'),(link('Cross-dataset work','implementations/cross_dataset/README.md'),'Shared external evaluation and comparison evidence'),(link('Research support','implementations/general/README.md'),'Thesis, maintenance, presentations, discovery and retained history'),(link('Policies','docs'),'Scope, raw-data boundaries, retention and output rules')])
    mapping+='\n\n## Protected and historical locations\n\nNative raw inputs remain at their original roots, including MSM/01_raw_dataset/, HANDOVER/01_raw_dataset/, REBOOT/01_raw_dataset/, MILLING DATASET/data/ and VIFAILBACK/01_original_dataset/. Root VIFAILBACK/ retains its complete frozen workspace; implementations/VIFAILBACK/ provides relative browsing links. No raw tree or scientific run was relocated by this phase.\n\nRoot src/ provides compatibility links to canonical dataset packages. The five remaining shared REASSEMBLE primitives were consolidated into implementations/REASSEMBLE/src/reassemble/ without changing their bytes. Original phase-one and bootstrap source/configuration/fit references remain at 26.10.2026_feedback_experiments/ and parth_ws_bootstrap/00_experimentation/. The protected initial PHM EDA stays at experiments/exp_a_initial_eda_r1_r3_r5/. REBOOT/runs/ retains investigation evidence.\n\n## History and reproducibility\n\n- [Current organization phase and checks](implementations/general/docs/repository_history/post_report_cleanup_20261124/STATUS.json)\n- [Current move/link/deletion record](implementations/general/docs/repository_history/post_report_cleanup_20261124/CHANGES.json)\n- [Earlier dataset consolidation](implementations/general/docs/repository_history/dataset_layout_cleanup.json)\n- [Earlier physical move mapping](implementations/general/docs/repository_history/physical_restructure_20261119/PATH_MAPPING.json)\n- [Archived AI workflow notes](implementations/general/docs/repository_history/ai_workflow_notes/README.md)\n\nFrozen manifests and commands retain historical content and revisions. Relocation is not training reproduction. Package/import and selected synthetic checks do not establish that every historical command is runnable; consult the actual phase results. Old broad compatibility aliases remain removed except the explicitly recorded source import and preserved-history links.\n\nScientific scope remains governed by [AGENTS.md](AGENTS.md), [active scope](docs/active_scope.md), [data boundaries](docs/data_boundaries.md) and [output policy](docs/output_policy.md).\n'
    c.edit('REPO_MAP.md',mapping)
    # Keep physical source in implementations while preserving old import identities.
    project=(REPO/'pyproject.toml').read_text()
    project=project.replace('include = ["phm2026*", "intel_welding*", "reassemble*", "pi_multimodal_ad*"]','include = ["phm2026*", "intel_welding*", "reassemble*", "external_eval*"]')
    project=project.replace('# The moved tests remain reachable through their original compatibility paths.\n# Avoid collecting the same files again during repository-wide discovery.','# Dataset-owned tests are explicit; historical run snapshots are not test roots.\ntestpaths = ["implementations/PHM2026/tests", "implementations/INTEL_WELDING/tests", "implementations/REASSEMBLE/tests", "implementations/MSM/tests", "implementations/HANDOVER/tests", "implementations/REBOOT/tests", "implementations/cross_dataset/tests", "implementations/general/tests"]\naddopts = "--import-mode=importlib"')
    project=project.replace('"{arch}", "implementations",','"{arch}",')
    c.edit('pyproject.toml',project)
    workspace=read(REPO/'.vscode/thesis.code-workspace')
    workspace.setdefault('settings',{}).setdefault('files.exclude',{}).update({'**/__pycache__':True,'**/.pytest_cache':True,'**/*.writing*':True,'**/*.lock':True})
    c.edit('.vscode/thesis.code-workspace',json.dumps(workspace,indent=2)+'\n')
    # Further disposable source caches only; never traverse experiments/results/raw/history.
    for domain in ['PHM2026','INTEL_WELDING','REASSEMBLE','MSM','HANDOVER','REBOOT','cross_dataset','general']:
        for role in ['src','scripts','tests']:
            root=REPO/'implementations'/domain/role
            if not root.exists():continue
            for base,dirs,files in os.walk(root,followlinks=False):
                dirs[:]=[d for d in dirs if not (Path(base)/d).is_symlink()]
                if '__pycache__' in dirs:
                    cache=Path(base)/'__pycache__'
                    try:c.delete_bytecode(cache)
                    except RuntimeError:pass
                    dirs.remove('__pycache__')
    record(DEST/'STATUS.json',{'utc':utc(),'stage':'VALIDATING','training_launched':False,'scientific_results_changed':False})
    # Validate link resolution and small source identity without model execution.
    missing=[]
    for edit in c.edits:
        p=REPO/edit['path']
        if p.suffix=='.md':
            for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
                if '://' not in target and not (p.parent/target.split('#')[0]).exists():missing.append([edit['path'],target])
    checks=[]
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','CUDA_VISIBLE_DEVICES':'','OMP_NUM_THREADS':'2','OPENBLAS_NUM_THREADS':'2','MKL_NUM_THREADS':'2','PYTHONPATH':str(REPO/'src')}
    commands=[
      ['ma_thesis_env/bin/python','-B','-c','from setuptools import find_packages; import phm2026,intel_welding,reassemble,external_eval; from reassemble import alignment,section1_features,section1_models,section2_models; print(find_packages("src")); print("canonical imports OK")'],
      ['ma_thesis_env/bin/python','-B','-m','pytest','-q','-p','no:cacheprovider','--import-mode=importlib','implementations/PHM2026/tests/test_timeseries_preprocessing.py','implementations/PHM2026/tests/test_data_contracts.py','implementations/PHM2026/tests/test_late_fusion.py','implementations/REASSEMBLE/tests/test_alignment.py'],
      ['git','diff','--check']]
    for i,cmd in enumerate(commands):
        left=min(600,deadline-time.time()-30)
        if left<=0:checks.append({'command':cmd,'status':'NOT_RUN_DEADLINE'});break
        with (DEST/f'check_{i}.log').open('w') as log:
            try:
                result=subprocess.run(cmd,cwd=REPO,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=left)
                checks.append({'command':cmd,'returncode':result.returncode,'log':f'check_{i}.log'})
            except subprocess.TimeoutExpired:checks.append({'command':cmd,'status':'DEADLINE_OR_CHECK_TIMEOUT','log':f'check_{i}.log'})
    changed=[str(p.relative_to(REPO)) for p in [source/n for n in PRIMITIVES] if sha(p)!=source_hashes[p.name]]
    assert not changed,changed
    scoped_paths=sorted(set([x['path'] for x in c.edits]+[x['source'] for x in c.moves]+[x['destination'] for x in c.moves]+[x['path'] for x in c.links]))
    diff_stat=subprocess.check_output(['git','diff','--stat','--',*scoped_paths],cwd=REPO,text=True)
    (DEST/'DIFF_STAT.txt').write_text(diff_stat+'\nUntracked destinations and links are listed separately in CHANGES.json; this tracked diff also includes pre-existing changes to these scoped paths.\n')
    report={'utc':utc(),'stage':'COMPLETE' if not missing and all(x.get('returncode')==0 for x in checks) else 'ORGANIZED_WITH_VALIDATION_LIMITATIONS',
       'authorization':AUTH,'gate':'Current fit, final evaluation, independent analysis and reports completed; training/watcher/guard processes exited',
       'moves':len(c.moves),'links':len(c.links),'documents_and_configuration_edits':len(c.edits),'deleted_disposable_bytecode_files':len(c.deleted),
       'raw_data_moved_or_deleted':False,'model_training_evaluation_or_preprocessing_launched':False,'scientific_run_artifacts_moved_or_changed':False,
       'shared_primitive_bytes_unchanged':not changed,'markdown_missing_links':missing,'checks':checks,'three_hour_postfit_limit_observed':time.time()<=deadline,
       'remaining_limits':['No claim of a fully validated historical training quickstart; old source/config/output paths require study-specific checks.','VIFAILBACK immutable source/run/data workspace remains in place and is exposed through canonical implementation links.','Unique AI-use, authorization, protocol and scientific records retained; only verified disposable source bytecode deleted.'],
       'git_after':git_summary(),'scoped_diff_stat':'DIFF_STAT.txt','commit_or_push_performed':False}
    record(DEST/'STATUS.json',report)
    # Plain human handoff, with separate scope from pre-existing uncommitted moves.
    (DEST/'HANDOFF.md').write_text('# Post-report organization\n\n'+report['stage']+'\n\nCanonical browsing starts at implementations/README.md. VIFAILBACK has real stage/source browsing links, dataset guides use numbered reading order, shared REASSEMBLE source is consolidated, and inactive AI notes are archived with original-path links. Verified disposable source bytecode is removed; data, run outputs, protocols and provenance are retained.\n\nSee CHANGES.json for only this phase\'s edits/moves/deletions, preimages/ for edited document/configuration versions, and STATUS.json plus check logs for validation actually performed. The large pre-existing unstaged relocation state was not staged, reset or discarded. No commit/push, new training or raw-data operation was performed.\n')
    record(TASK/'STATUS.json',report)

def main():
    record(TASK/'STATUS.json',{'utc':utc(),'stage':'WAITING_FOR_FINAL_FIT_AND_REPORT','repository_changes_started':False,'authorization':AUTH})
    while True:
        completion=STUDY/'04_full20/seed42/outer0_inner2/COMPLETE.json'
        if completion.exists():
            limit=dt.datetime.fromisoformat(read(completion)['completed_utc']).timestamp()+10800
            if time.time()>=limit:
                record(TASK/'STATUS.json',{'utc':utc(),'stage':'NOT_STARTED_POSTFIT_LIMIT_REACHED','repository_changes_started':False})
                return
        ready,stage,final=gate()
        if ready:break
        if stage=='REPORT_NOT_SUCCESSFULLY_CLOSED':
            record(TASK/'STATUS.json',{'utc':utc(),'stage':stage,'repository_changes_started':False,'reason':'Researcher requires reports finished first; leave all structure unchanged'})
            return
        time.sleep(10)
    try:main_phase(final)
    except BaseException as exc:
        state={'utc':utc(),'stage':'STOPPED_WITH_ERROR','error':repr(exc),'do_not_resume_training':True}
        record(TASK/'STATUS.json',state)
        if DEST.exists():record(DEST/'STATUS.json',state)
        raise

if __name__=='__main__':main()
