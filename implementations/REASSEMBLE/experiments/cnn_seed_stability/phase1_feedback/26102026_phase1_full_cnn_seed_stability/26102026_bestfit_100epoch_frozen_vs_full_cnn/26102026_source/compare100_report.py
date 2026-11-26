"""Single-split paired evaluation and honest progress for the100-epoch detour."""
import json
import numpy as np
from sklearn.metrics import average_precision_score,roc_auc_score

from compare100_common import DETOUR,RUN,REPORTS,CONFIG,JOB,EVIDENCE,configuration,folder_for,read,write,sha,utc
from phase_metrics import metrics,aligned_keys
from phase_reporting import plot_fit


def put(name,text):
    path=REPORTS/name
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.writing');temp.write_text(text);temp.replace(path)


def refresh(state,final=None):
    c=configuration();job=read(JOB)
    selection=read(DETOUR/'26102026_evidence/PHASE1_FIT_SELECTION.json')
    text=f'# Frozen versus full CNN,100 epochs — {"COMPLETE" if final else "PARTIAL"}\n\nUpdated {utc()}. Stage: {state["stage"]}.\n\n'
    text+='Selected completed C20 fit: seed '+str(c['seed'])+', original fit '+str(c['selected_original_job_index']+1)+'. Selection used training-side validation AP only.\n\n'
    text+='| Candidate original fit | Seed | Validation AP | Executed epochs |\n|---|---:|---:|---:|\n'
    for r in selection['candidate_snapshot']:
        text+=f"| {r['job_index']+1} | {r['seed']} | {r['validation_AP']:.6f} | {r['executed_epochs']} |\n"
    text+='\nValidation sets differ across candidates, so the ranking is descriptive. This is a post-selected single-split follow-up, not independent confirmation. Both new arms start fresh from identical original pretrained CNN initialization/seeded heads.\n\n'
    text+='| Arm | Completed epochs | Selected epoch | Training hours | Status |\n|---|---:|---:|---:|---|\n'
    for arm in c['arms']:
        folder=folder_for(arm,c['seed'],job)
        pointer=folder/'PHASE1_LATEST_EPOCH.json'
        curve=folder/'PHASE1_LEARNING_CURVE.json'
        done=folder/'PHASE1_COMPARISON_ARM_COMPLETE.json'
        history=read(curve) if curve.exists() else []
        epoch=read(pointer)['completed_epoch'] if pointer.exists() else 0
        complete=read(done) if done.exists() else None
        selected=complete['selected_epoch'] if complete else 'Pending'
        hours=(complete['training_seconds'] if complete else sum(r['training_seconds'] for r in history))/3600
        text+=f'| {arm} | {epoch}/100 | {selected} | {hours:.4f} | {"Complete" if complete else "In progress / queued"} |\n'
        if complete:plot_fit(folder)
    text+='\n| Arm | Sustained GPU kernel-busy % | Peak allocated GiB | Training actions/s | Mean training epoch seconds |\n|---|---:|---:|---:|---:|\n'
    for arm in c['arms']:
        curve=folder_for(arm,c['seed'],job)/'PHASE1_LEARNING_CURVE.json'
        h=read(curve) if curve.exists() else []
        h=h[1:] if len(h)>1 else h  # Exclude initialization epoch when available.
        if not h:
            text+=f'| {arm} | Pending | Pending | Pending | Pending |\n';continue
        seconds=sum(r['training_seconds'] for r in h)
        busy=sum(r['GPU_compute_percent']*r['training_seconds'] for r in h if r['GPU_compute_percent'] is not None)/seconds
        vram=max(r['peak_allocated_bytes'] for r in h)/1024**3
        rate=sum(r['training_actions'] for r in h)/seconds
        text+=f'| {arm} | {busy:.2f} | {vram:.3f} | {rate:.3f} | {seconds/len(h):.2f} |\n'
    attempts=RUN/'PHASE1_COMPARISON_PROCESS_ATTEMPTS.json'
    job_hours=sum(r.get('elapsed_seconds',0) for r in read(attempts))/3600 if attempts.exists() else 0
    text+=f'\nPlanning estimate:26–36 allocated GPU job hours. Actual active process time so far:{job_hours:.4f} GPU job hours (includes validation/checkpoints; excludes pause and GPU queue). Per-arm training-only hours are shown above. These are resource occupancy hours, not GPU-utilization-weighted compute hours.\n'
    text+='\nFrozen training reuses exact verified16-frame FP32 pooled features; its small head requires much less computation. Full training uses all CNN convolution/normalization-affine parameters and the classifier, four persistent workers, FFmpeg2, microbatch1 and accumulation8. Normalization running moments remain fixed. GPU kernel-busy activity and VRAM usage are distinct. All epoch curves and telemetry remain in each isolated arm folder.\n'
    if final:
        text+='\n## Shared outer assessment\n\n| Arm | AP | AUROC | Brier | Log loss | Prevalence |\n|---|---:|---:|---:|---:|---:|\n'
        for arm,r in final['metrics'].items():
            text+=f"| {arm} | {r['AP']:.6f} | {r['AUROC']:.6f} | {r['Brier']:.6f} | {r['log_loss']:.6f} | {r['prevalence']:.6f} |\n"
        text+='\nPaired C minus frozen differences and conditional recording-bootstrap intervals:\n\n```json\n'+json.dumps(final['paired'],indent=2)+'\n```\n'
        text+='\nThe753 assessment actions belong to outer-fold1 recordings excluded from every candidate training, selection, calibration and inner-assessment role. Calibration uses only the chosen original C groups. One fold/seed and prior dataset exposure limit generalization; the original75-fit study remains the broader evaluation. No new F2 model was fitted in this two-fit detour.\n'
    else:
        text+='\nHeld-out comparison remains pending until both100-epoch fits complete. Missing results are not imputed.\n'
    text+='\nThe paused study retains its original20-epoch cap and cosine50 prefix. On completion, its controller is relaunched with the saved model, optimizer, scheduler, RNG and sampler boundary. No100-epoch weights are copied into that study.\n'
    put('PHASE1_100EPOCH_COMPARISON_REPORT.md',text)


def finalize():
    c=configuration();job=read(JOB)
    cohort=read(EVIDENCE/'PHASE1_INPUT_IDENTITY_MANIFEST.json')
    expected=[cohort[i] for i in job['predict']]
    keys=[r['sample_id'] for r in expected]
    y=np.array([r['failure'] for r in expected])
    scores={};banks={};raw_metrics={}
    for arm in c['arms']:
        folder=folder_for(arm,c['seed'],job)
        done=read(folder/'PHASE1_COMPARISON_ARM_COMPLETE.json')
        assert done['epochs']==100 and done['configuration_sha256']==sha(CONFIG)
        assert sha(folder/'PHASE1_PREDICTIONS.json')==done['predictions_sha256']
        assert sha(folder/'PHASE1_BEST_MODEL.pt')==done['selected_model_sha256']
        lookup=aligned_keys(read(folder/'PHASE1_PREDICTIONS.json'),keys)
        rows=[lookup[key] for key in keys]
        for actual,reference in zip(rows,expected):
            assert all(actual[k]==reference[k] for k in ['failure','recording_id','segment_id'])
        banks[arm]=np.array([r['p_visual'] for r in rows])
        scores[arm]=metrics(y,banks[arm])
        raw=np.array([r['raw_visual_logit'] for r in rows])
        raw_metrics[arm]={'AP':float(average_precision_score(y,raw)),'AUROC':float(roc_auc_score(y,raw))}
    control,treatment=c['arms']
    groups=sorted({r['recording_id'] for r in expected})
    indices=[np.array([i for i,r in enumerate(expected) if r['recording_id']==group]) for group in groups]
    rng=np.random.default_rng(20261027)
    draws={'AP':[],'AUROC':[]}
    for _ in range(2000):
        ix=np.concatenate([indices[i] for i in rng.integers(len(indices),size=len(indices))])
        if len(np.unique(y[ix]))<2:continue
        for name,function in [('AP',average_precision_score),('AUROC',roc_auc_score)]:
            draws[name].append(float(function(y[ix],banks[treatment][ix])-function(y[ix],banks[control][ix])))
    paired={name:{'estimate':scores[treatment][name]-scores[control][name],
                  'lower95':float(np.quantile(values,.025)),'upper95':float(np.quantile(values,.975)),
                  'valid_draws':len(values),'unit':'recording; conditional on selected split and fitted models'}
            for name,values in draws.items()}
    result={'metrics':scores,'raw_logit_metrics':raw_metrics,'paired':paired,'seed':c['seed'],
            'assessment_actions':len(keys),'assessment_recordings':len(groups),
            'selection':'Best observed training-side validation fit; outer assessment excluded from all candidates',
            'both_arms_fresh_and100epochs':True,'new_F2_model_fitted':False}
    write(RUN/'PHASE1_100EPOCH_COMPARISON_METRICS.json',result)
    return result


def output_manifest():
    records=[]
    path=DETOUR/'26102026_evidence/PHASE1_COMPARISON_OUTPUT_MANIFEST.json'
    for p in DETOUR.rglob('*'):
        if not p.is_file() or p==path or p.name.endswith('.writing'):continue
        size=p.stat().st_size
        records.append({'path':str(p.relative_to(DETOUR)),'bytes':size,'sha256':sha(p) if size<64*1024**2 else None})
    write(path,{'utc':utc(),'files':records,'large_checkpoint_hashes':'Per-arm epoch pointers and immutable pause proof contain SHA256'})
