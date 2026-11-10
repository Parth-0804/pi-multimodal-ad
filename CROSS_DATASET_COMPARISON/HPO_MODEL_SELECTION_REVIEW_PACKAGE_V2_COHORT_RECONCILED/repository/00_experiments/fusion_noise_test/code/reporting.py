"""Preparation and review package; unavailable outcomes are never fabricated."""
from pathlib import Path
import importlib.metadata
import os,shutil,zipfile,hashlib
import numpy as np
import pandas as pd
from common import STUDY,RUN,REPO,config,read,write,write_text,csv,sha,local,event,budget,readiness,utc,command


def prepare():
    c=config();prior=REPO/c['visual_run'];enc=REPO/c['encoder_run']
    source_paths={'cohort_and_frames.json':prior/'data_manifests/cohort_and_frames.json','fit_partitions.json':prior/'data_manifests/fit_partitions.json',
        'cohort_lock.json':prior/'data_manifests/cohort_lock.json','input_manifest.json':prior/'data_manifests/input_manifest.json'}
    lock=read(source_paths['cohort_lock.json'])
    assert sha(source_paths['cohort_and_frames.json'])==lock['cohort_sha256'] and sha(source_paths['fit_partitions.json'])==lock['partitions_sha256']
    record=RUN/'provenance/preparation_identity.json'
    if record.exists():
        identity=read(record);assert identity['config_sha256']==sha(STUDY/'config.json'),'CONFIG_DRIFT'
        for name,source in source_paths.items():assert sha(source)==identity['data'][name]==sha(RUN/'data'/name),'INPUT_DRIFT'
        for name,v in identity['versions'].items():assert importlib.metadata.version(name)==v,'SOFTWARE_DRIFT'
    else:
        budget(64*2**20)
        for name,source in source_paths.items():shutil.copyfile(source,local(RUN/'data'/name))
        shutil.copyfile(prior/'provenance/original_pretrained_identity.json',local(RUN/'provenance/original_pretrained_identity.json'))
        shutil.copyfile(REPO/c['base_config'],local(RUN/'provenance/base_config.json'))
        for label,path in [('visual',prior/'config/resolved_config.json'),('encoder',enc/'resolved_config.json')]:shutil.copyfile(path,local(RUN/'provenance'/(label+'_config.json')))
        # Attribution snapshots are evidence only; no upstream implementation is imported.
        sources=[prior/'source/data.py',prior/'source/visual_model.py',prior/'source/fusion.py',prior/'source/training.py',REPO/'00_experiments/rt_detr_encoder_comparison/code/features.py']
        snapshots={}
        for source in sources:
            name=('encoder_' if source.name=='features.py' else 'visual_')+source.name
            shutil.copyfile(source,local(RUN/'provenance/source_snapshots'/name));snapshots[str(source.relative_to(REPO))]=sha(source)
        identity={'prepared_utc':utc(),'config_sha256':sha(STUDY/'config.json'),'data':{name:sha(p) for name,p in source_paths.items()},'source_snapshots':snapshots,
                  'versions':{n:importlib.metadata.version(n) for n in ['numpy','pandas','scipy','scikit-learn','torch','transformers','opencv-python','h5py','safetensors','matplotlib']},'git':command(['git','rev-parse','HEAD'])}
        write(record,identity);write(RUN/'resolved_config.json',c)
    for name,info in read(RUN/'provenance/original_pretrained_identity.json')['weights'].items():assert sha(REPO/c['weights_dir']/name)==info['sha256'],'ORIGINAL_WEIGHTS_DRIFT'
    f=pd.DataFrame(read(RUN/'data/cohort_and_frames.json'));jobs=read(RUN/'data/fit_partitions.json')
    from selection import validate_job,collect,comparison_inventory
    assert len(jobs)==25 and not f.duplicated(['recording_id','segment_id']).any()
    for j in jobs:validate_job(f,j)
    for sample in f.to_dict('records'):
        assert len(sample['frames16'])==len(set(sample['frames16']))==16
        assert len(sample['frames32'])==len(set(sample['frames32']))==32
        assert [sample['frames32'][i] for i in sample['positions16_in32']]==sample['frames16']
        for n in (16,32):
            times=sample['timestamps'+str(n)]
            assert len(times)==n and times==sorted(times) and all(sample['start']<=t<=sample['end'] for t in times),'FRAME_INTERVAL_DRIFT'
    for s in f.drop_duplicates('source_path').to_dict('records'):
        st=(REPO/s['source_path']).stat();assert (st.st_size,st.st_mtime_ns)==(s['source_bytes'],s['source_mtime_ns'])
    for s in f.drop_duplicates('video_path').to_dict('records'):
        st=(REPO/s['video_path']).stat();assert (st.st_size,st.st_mtime_ns)==(s['video_bytes'],s['video_mtime_ns'])
    write(RUN/'checks/cohort_and_memberships.json',{'passed':True,'samples':len(f),'failures':int(f.failure.sum()),'recordings':int(f.recording_id.nunique()),'fit_roles':len(jobs),'raw_video_stats_unchanged':True})
    from inputs import processor_check
    if not (RUN/'checks/processor_noop.json').exists():processor_check()
    if not (RUN/'model_selection/selected_model.json').exists():
        candidates,reference=collect(rank_allowed=False);csv(RUN/'model_selection/clean_comparison.csv',comparison_inventory(candidates))
        write(RUN/'model_selection/candidate_inventory.json',{k:{key:value for key,value in v.items() if key!='folds'}|{'available_fold_names':list(v['folds'])} for k,v in candidates.items()})
    write_text(RUN/'experiment_plan.md','''# Fixed selected-model robustness protocol\n\nSelection is deferred until both upstream tasks are terminal and outputs stable. Canonical reference is new frozen_16_frames, with cnn_only as a documented fallback alias only if the canonical reference is unavailable. Eligibility precedes scores. All eligible candidates with at least one complete replayable outer fold enter the whole-fold intersection. Zero-fold candidates are untested; an empty intersection blocks. Five folds are full coverage; any fallback is PARTIAL_COVERAGE_PILOT. No row-subset cherry-picking.\n\nWinner uses unrounded pooled failure-class fused AP, tolerance1e-12. Retain reference unless exceeded; ties prefer reference, fewer frames, fewer reliably measured executed parameters, alphabetical name. No visual-only or noisy metric enters selection. Lock condition, per-fold components, cohort, config and sources before corrupting any assessment inputs. Selection is DEVELOPMENT-EXPOSED and exploratory.\n\nOnly selected fixed saved models run: original/fine-tuned CNN or frozen encoder prefix exactly as fitted, existing head, normalizers, calibrators, sensor logistic model, static F2 and thresholds. Detector/decoder/proposal paths guarded. All parameters/BN/dropout frozen, inference-mode only. No training, refitting, recalibration or optimizer steps.\n\nGaussian RGB sigma .02/.05/.10 at native resolution, float RGB clipped[0,1]; processor float path preferred only if no-op matches. Required uint8 quantization is recorded. Blur sigma1/2/4, reflect boundaries, radius ceil(3sigma), spatial axes only. Frame loss10/30/50% removes seeded nested prefixes, floor(fN+.5), at least1 and at mostN-1; survivors remain chronological.\n\nSensor Gaussian alpha .10/.50/1.00 times finite native raw-channel population SD computed only from saved G intervals. Each action interval contributes its finite samples once; overlapping intervals, if present, contribute per action. Channel loss10/30/50% uses nested named channel prefixes. Time loss masks10/30/50% duration about one seed-derived center[.25,.75], propagated through resampling so interpolation cannot recreate removed support. Missing features use unchanged saved imputation. All rows retained.\n\nSeeds271828/271829/271830. Stable SHA256 keys bind seed, recording+segment, family, frame/channel; severity excluded for common draws and nested masks. One modality at a time. Declared image absence returns calibrated sensor branch; sensor absence returns visual branch; both absent abstains. Partial faults always use F2.\n\n51 realizations per fold: clean1, image noise9, sensor noise9, blur3, frame loss9, channel loss9, time loss9, absence2. All clean folds replay before any new corrupted assessment inference. Then image/sensor Gaussian severity-repeat blocks across all folds, then blur/frame/channel/time/absence. Streaming predictions and compact fold-specific clean frame vectors; no damaged dataset copies.\n\nReport per-fold and pooled AP/AUROC, fixed-threshold precision/recall/balanced accuracy/macroF1/Brier. For stochastic faults average three separately computed metrics, never probabilities or duplicated subjects. AP_drop=clean-corrupted. Paired recording-cluster bootstrap2000, seed314159, same multiplicities, all rows per recording; average fixed-realization metrics within replicate. Undefined draws counted. Reliability10 equal-width bins, final bin includes1. Intervals do not account for winner selection/training uncertainty. Absence results separate.\n\nLimits: one allocated GPU after upstream release;2 CPU threads and0 decode workers;24h from original request including interruptions/waiting;30GiB new storage,10GiB filesystem reserve;monitored32GiB RSS. At most60min foreground waiting, polls no faster than60s, no queued continuation. Reserve15min for reports. At most2 technical repairs per failed stage. Historical Task4 excluded.\n''')
    event('PREPARED',cohort_samples=len(f),cohort_failures=int(f.failure.sum()),cohort_recordings=int(f.recording_id.nunique()))


def report():
    progress=read(RUN/'progress.json') if (RUN/'progress.json').exists() else {'status':'NOT_PREPARED'}
    lock=RUN/'model_selection/selected_model.json';selected=read(lock) if lock.exists() else None
    status=progress['status'];ready=read(RUN/'checks/readiness.json') if (RUN/'checks/readiness.json').exists() else {}
    if selected:
        choice=f"Selected {selected['condition']}; saved clean fused AP {selected['clean_AP']:.12g}, reference {selected['reference_AP']:.12g}, difference {selected['clean_AP_improvement']:+.12g}. Coverage: {selected['coverage']} on {len(selected['folds'])} folds and {selected['samples']} rows."
    else:choice='No model selected. F2 has not been retained or replaced: ranking and the selection lock are deferred until upstream results are terminal and eligible coverage is established.'
    summary=[]
    p=RUN/'model_selection/clean_comparison.csv'
    if p.exists():
        t=pd.read_csv(p).fillna('')
        for _,r in t.iterrows():summary.append(f"| {r['condition']} | {r.get('fold_count',r.get('folds','—'))} | {r.get('fused_AP') if pd.notna(r.get('fused_AP')) else 'NOT_RANKED'} | {r.get('reason','')} |")
    table='| Candidate | Available folds | Clean fused AP | Status / reason |\n|---|---|---|---|\n'+'\n'.join(summary)
    findings=[]
    metrics_path=RUN/'comparison/robustness_metrics.csv'
    if selected and metrics_path.exists() and metrics_path.stat().st_size>2:
        try:
            m=pd.read_csv(metrics_path)
            for family,level,repeat in [('clean','clean','0'),('image_noise','strong','mean_of_3_metrics'),('sensor_noise','strong','mean_of_3_metrics')]:
                q=m.loc[(m.family==family)&(m.level==level)&(m.branch=='fused')&(m.scope=='pooled')&(m['repeat'].astype(str)==repeat)]
                if len(q):findings.append(f"{family}: AP={q.iloc[0].AP:.8g}, clean-minus-fault drop={q.iloc[0].AP_drop:.8g}")
        except pd.errors.EmptyDataError:pass
    result='; '.join(findings) or 'Clean replay, strongest predefined image-noise AP and strongest predefined sensor-noise AP: NOT_RUN. Paired drops and uncertainty are not computable.'
    limits=f"Stage: {status}. Blocker: {progress.get('blocker','none recorded')}. Upstream status: {ready.get('upstream_states',{})}. No background job or scheduled continuation exists."
    repair=RUN/'provenance/replay_repair_01/approved_revision.json'
    if repair.exists():
        replay_complete=(RUN/'checks/clean_replay.json').exists()
        limits+=('\n\nTechnical replay repair 01: initial clean replay stopped after 61 passing rows; no corrupted assessment predictions had been generated. The sensor adapter incorrectly promoted float32 statistics to float64. The repaired adapter preserves the original float32 reduction path and exactly reproduces the failed row’s saved features and sensor probability. Visual mean pooling and standardization also now use the original Torch arithmetic. A failing-then-passing regression test is retained. The selection lock, fitted components, frame count, corruption configuration and 1e-5 tolerance are unchanged. Original and repaired source hashes are recorded in provenance/replay_repair_01/approved_revision.json. '+('Full repaired clean replay completed; see checks/clean_replay.json.' if replay_complete else 'Full repaired clean replay remains PENDING; this repair is not proof that all clean rows pass.'))
    if selected and not findings:
        limits+='\n\nNo completed newly replayed clean or corrupted prediction table exists. Directly identified upstream selection evidence is model_selection/clean_predictions/'+selected['condition']+'.csv; partial clean frame caches are not claimed as a completed prediction bank.'

    selection=f'''# Model selection — {status}\n\n{choice}\n\n{table}\n\nThe canonical reference is the matched first-study frozen_16_frames F2, not historical anonymous scores. cnn_only is an alias/replicate, never an extra winner chosen for a favorable score. Eligibility, exact fold rows, component hashes, G/C/T/E and inner-OOF coverage are checked before ranking. While upstream work is active, completed immutable prediction tables may be copied as UNRANKED evidence; this does not authorize a premature partial pilot.\n\n{limits}\n\nSelection, when eligible, uses pooled failure-class clean fused AP with tolerance1e-12 and the fixed tie rules. Clean candidate tables are retained under clean_predictions after selection; preliminary copies are under unranked_upstream_predictions. An absent selected_model.json means no lock and no authorized corrupted assessment inference. DEVELOPMENT-EXPOSED: a winner selected on these outer predictions is not independently confirmed, and intervals do not undo selection.\n'''
    write_text(RUN/'model_selection/selection_report.md',selection)
    text=f'''# Selected-model robustness — {status}\n\n{choice}\n\n{result}\n\n{table}\n\n## What ran and what did not\n\nInspect checks for actual synthetic tests, processor checks, component verification and runtime replay. An implemented transform is not an executed corruption study. No predictor training, recalibration, threshold tuning or historical Task4 work is permitted.\n\n{limits}\n\n## Interpretation\n\nUntil matched noisy predictions exist, image-versus-sensor sensitivity, harmful fusion and robustness are unknown. Full absence uses a separately declared sensor-only or visual-only fallback; noisy-but-present inputs keep the saved F2. Both absent must abstain. A winning newer model would be the only fusion pipeline evaluated under noise; discarded F2/candidates would remain clean-selection evidence only.\n\nThe primary fault summaries are strongest prescribed image Gaussian sigma0.10 and sensor Gaussian alpha1.00, with means of three separately computed AP values. No worst-observed severity is substituted. AP drops are clean minus corrupted. Paired bootstrap clusters recordings, preserving all rows and averaging metrics across fixed realizations. Equal severity labels across modalities are not equivalent physical faults. This is exposed-data exploratory analysis, not untouched generalization, causality or a claim about adaptive fusion.\n\n## Teaching chain\n\nClean results -> eligibility and whole-fold coverage -> candidate selection -> lock frozen selected pipeline -> one-modality raw-input perturbation -> branch/F2 predictions -> matched metrics -> bounded conclusion.\n\n## Review artifacts and next decision\n\nThe package contains source/tests/config, exact cohort/frame/fit manifests, copied completed upstream prediction tables clearly marked unranked where appropriate, and any actually executed noise predictions. It cannot recalculate nonexistent results. Model blobs/raw inputs are excluded and referenced by hashes.\n\nRecommended next decision: resume this same evaluation once the predecessor runs reach a stable terminal state and the allocated GPU is free, within the original deadline; a later budget needs explicit authorization. Do not resume upstream training from this task.\n\nEvidence checked: distinguish recorded source and synthetic checks from upstream execution. Still uncertain: any unexecuted model selection, full clean replay and fault metrics. Defensible conclusion: {('no selected-model robustness result yet' if not findings else 'only the completed matched conditions support conclusions under the stated exposed-data protocol')}.\n'''
    write_text(RUN/'comparison/RESULTS_SUMMARY.md',text)
    write_text(RUN/'README_FIRST.md',f'''# {status}\n\n{choice}\n\n{result}\n\n{limits}\n\n- [Selection report](model_selection/selection_report.md)\n- [Clean comparison](model_selection/clean_comparison.csv)\n- [Results summary](comparison/RESULTS_SUMMARY.md)\n- [Progress](progress.json), [resume](how_to_resume.md), [review package](REVIEW_PACKAGE.zip)\n\nAll work stays inside this study. No selected_model.json is created until valid one-time selection. Unranked inherited predictions are not newly replayed or corrupted predictions.\n''')
    write_text(RUN/'how_to_resume.md','''# Supported resume\n\nFrom the repository root:\n\n```bash\nma_thesis_env/bin/python -B 00_experiments/fusion_noise_test/run_experiment.py resume --wait-seconds 600\n```\n\nThis runs through eligible selection, clean replay, selected-only raw-input inference and evaluation automatically. If upstream work remains active, it safely returns WAITING_FOR_PREVIOUS_RESULTS after the foreground wait. Total waiting across resumptions is capped at60minutes; polls are at least60seconds apart. Nothing is queued.\n\nOriginal task start:21October2026 01:01 Europe/Berlin (20October23:01UTC), including interruptions. Deadline:22October2026 01:01 Europe/Berlin (21October23:01UTC), with15minutes reserved for reporting. Repeated instructions/resume do not reset this deadline. No training of this or predecessor studies is authorized.\n''')


def package():
    files=[]
    for p in STUDY.rglob('*'):
        rel=p.relative_to(STUDY)
        if not p.is_file() or p.is_symlink() or any(x in rel.parts for x in ['cache','__pycache__']):continue
        if '.writing' in p.name or p.name in ['REVIEW_PACKAGE.zip','package_manifest.json','package_verification.json']:continue
        if p.suffix not in ['.py','.md','.json','.jsonl','.csv','.txt','.png']:continue
        if p.stat().st_size>32*2**20:raise RuntimeError('REVIEW_FILE_TOO_LARGE')
        files.append(p)
    manifest={str(p.relative_to(STUDY)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)}
    write(RUN/'provenance/package_manifest.json',manifest);files.append(RUN/'provenance/package_manifest.json');budget(sum(p.stat().st_size for p in files),scientific=False)
    target=local(RUN/'REVIEW_PACKAGE.zip');tmp=local(RUN/'REVIEW_PACKAGE.writing.zip')
    with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(files):z.write(p,str(p.relative_to(STUDY)))
    os.replace(tmp,target)
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        for name,d in manifest.items():
            data=z.read(name);assert len(data)==d['bytes'] and hashlib.sha256(data).hexdigest()==d['sha256']
    write(RUN/'checks/package_verification.json',{'passed':True,'files_verified':len(manifest),'bytes':target.stat().st_size,'sha256':sha(target)})
