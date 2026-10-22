"""Direct keyed held-out metrics and paired recording-cluster bootstrap."""
import json
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score, recall_score, precision_score, balanced_accuracy_score, f1_score, brier_score_loss
from common import STUDY,RUN,config,read,write,write_text,save_csv,sha,local,budget
from data import KEYS


def metrics(y,p):
    y=np.asarray(y,int);p=np.asarray(p,float)
    assert len(y)==len(p) and np.isfinite(p).all() and ((p>=0)&(p<=1)).all()
    both=len(np.unique(y))==2;decision=p>=.5
    return {'AP':float(average_precision_score(y,p)) if np.any(y==1) else None,
            'AUROC':float(roc_auc_score(y,p)) if both else None,
            'failure_recall':float(recall_score(y,decision,zero_division=0)),
            'failure_precision':float(precision_score(y,decision,zero_division=0)),
            'balanced_accuracy':float(balanced_accuracy_score(y,decision)) if both else None,
            'macro_F1':float(f1_score(y,decision,labels=[0,1],average='macro',zero_division=0)),
            'Brier':float(brier_score_loss(y,p))}


def paired_bootstrap(a,b,reps=2000):
    assert a[KEYS].values.tolist()==b[KEYS].values.tolist()
    assert np.array_equal(a.failure,b.failure) and np.array_equal(a.p_sensor,b.p_sensor)
    names=['F2_encoder_minus_CNN','visual_encoder_minus_CNN','F2_CNN_minus_sensor','F2_encoder_minus_sensor']
    y=a.failure.to_numpy();groups=a.recording_id.to_numpy();unique=np.unique(groups)
    ix=[np.flatnonzero(groups==g) for g in unique]
    def contrasts(rows):
        ap=lambda p:float(average_precision_score(y[rows],p[rows]))
        av=ap(a.p_visual.to_numpy());bv=ap(b.p_visual.to_numpy());af=ap(a.p_fused.to_numpy());bf=ap(b.p_fused.to_numpy());s=ap(a.p_sensor.to_numpy())
        return np.array([bf-af,bv-av,af-s,bf-s])
    observed=contrasts(np.arange(len(a)));rng=np.random.default_rng(314159);values=[];skipped=0
    for _ in range(reps):
        rows=np.concatenate([ix[i] for i in rng.integers(0,len(unique),len(unique))])
        if len(np.unique(y[rows]))<2:skipped+=1;continue
        values.append(contrasts(rows))
    limits=np.percentile(values,[2.5,97.5],axis=0) if values else np.full((2,4),np.nan)
    return pd.DataFrame([dict(contrast=name,AP_difference=observed[i],lower95=limits[0,i],upper95=limits[1,i],effective_replicates=len(values),skipped_replicates=skipped,requested_replicates=reps,seed=314159) for i,name in enumerate(names)])


def paired_tables():
    parts={c:[] for c in config()['conditions']};folds=[]
    for k in range(1,6):
        name=f'fold_{k:02d}'
        if not all((RUN/c/name/'condition_complete.json').exists() for c in parts):continue
        tables={}
        for c in parts:
            p=RUN/c/name/'assessment_predictions.csv';d=read(p.parent/'condition_complete.json')
            assert sha(p)==d['predictions_sha256']
            tables[c]=pd.read_csv(p,dtype={'recording_id':str,'segment_id':str,'sample_id':str}).sort_values(KEYS).reset_index(drop=True)
            assert not tables[c].duplicated(KEYS).any()
        a,b=tables.values()
        assert a[KEYS].values.tolist()==b[KEYS].values.tolist() and np.array_equal(a.failure,b.failure) and np.array_equal(a.p_sensor,b.p_sensor)
        for c in parts:parts[c].append(tables[c])
        folds.append(name)
    return {c:pd.concat(v,ignore_index=True) if v else pd.DataFrame() for c,v in parts.items()},folds


def evaluate(bootstrap=True):
    tables,folds=paired_tables();rows=[];summary=[]
    for c,t in tables.items():
        if not t.empty:
            assert not t.duplicated(KEYS).any(), 'POOLED_KEY_DUPLICATION'
        if t.empty:
            summary.append({'condition':c,'visual_AP':'NOT_RUN','sensor_AP':'NOT_RUN','F2_AP':'NOT_RUN','completed_folds':0,'status':'NOT_RUN'})
            continue
        save_csv(RUN/'comparison'/('identified_outer_predictions_'+c+'.csv'),t)
        for scope,q in [('pooled',t)]+[(k,t.loc[t.fold_name==k]) for k in folds]:
            for branch in ['visual','sensor','fused']:
                rows.append(dict(condition=c,scope=scope,branch=branch,samples=len(q),failures=int(q.failure.sum()),recordings=int(q.recording_id.nunique()),prevalence=float(q.failure.mean()),threshold=.5,**metrics(q.failure,q['p_'+branch])))
        summary.append({'condition':c,'visual_AP':metrics(t.failure,t.p_visual)['AP'],'sensor_AP':metrics(t.failure,t.p_sensor)['AP'],'F2_AP':metrics(t.failure,t.p_fused)['AP'],'completed_folds':len(folds),'status':'+'.join(sorted(set(t.status)))})
    save_csv(RUN/'comparison/comparison_table.csv',pd.DataFrame(summary))
    save_csv(RUN/'comparison/metrics.csv',pd.DataFrame(rows,columns=['condition','scope','branch','samples','failures','recordings','prevalence','threshold','AP','AUROC','failure_recall','failure_precision','balanced_accuracy','macro_F1','Brier']))
    if folds:
        a,b=tables.values()
        contrasts=paired_bootstrap(a,b,config()['bootstrap_replicates']) if bootstrap else pd.DataFrame()
        save_csv(RUN/'comparison/paired_comparisons.csv',contrasts)
        # Outcome-selected illustrations, deterministic key tie-breaking.
        change=a[KEYS+['failure','fold_name']].copy()
        eps=np.finfo(float).eps
        def loss(p):return -(a.failure*np.log(np.clip(p,eps,1-eps))+(1-a.failure)*np.log(np.clip(1-p,eps,1-eps)))
        change['CNN_probability']=a.p_fused;change['encoder_probability']=b.p_fused
        change['true_class_loss_improvement']=loss(a.p_fused)-loss(b.p_fused)
        examples=[]
        for label in [0,1]:
            for direction,ascending in [('improvement',False),('deterioration',True)]:
                z=change.loc[change.failure==label].sort_values(['true_class_loss_improvement',*KEYS],ascending=[ascending,True,True]).head(10).copy()
                z['selection']=direction;examples.append(z)
        save_csv(RUN/'comparison/changed_predictions.csv',pd.concat(examples,ignore_index=True))
        plot_reliability(tables)
    else:
        save_csv(RUN/'comparison/paired_comparisons.csv',pd.DataFrame(columns=['contrast','AP_difference','lower95','upper95','effective_replicates','skipped_replicates']))
        save_csv(RUN/'comparison/changed_predictions.csv',pd.DataFrame(columns=KEYS+['failure','CNN_probability','encoder_probability','true_class_loss_improvement','selection']))
    state=read(RUN/'progress.json') if (RUN/'progress.json').exists() else {'status':'NOT_PREPARED'}
    status='COMPLETE' if len(folds)==5 else ('PARTIAL' if folds else state['status'])
    lines=['| Condition | Visual AP | Sensor AP | F2 AP | Paired folds | Fit status |','|---|---:|---:|---:|---:|---|']
    for r in summary:
        fmt=lambda x:f'{x:.6f}' if isinstance(x,float) else str(x)
        lines.append('| '+' | '.join(fmt(r[k]) for k in ['condition','visual_AP','sensor_AP','F2_AP','completed_folds','status'])+' |')
    table='\n'.join(lines)
    findings=('No real encoder features or paired assessment predictions are available. No empirical AP difference, uncertainty interval, or scientific ranking can be reported.' if not folds else
              'Pooled AP is computed from identical directly keyed outer rows, separately from fold APs. The paired intervals are conditional on this exposed dataset and one fitted seed family; secondary contrasts are exploratory and unadjusted.')
    evidence='Runtime GPU checks have not run.'
    cpu=RUN/'checks/original_weight_CPU_path.json'
    if cpu.exists():
        d=read(cpu)
        evidence+=' Original-checkpoint CPU forwards on two synthetic 64x64 images passed. Hooks observed encoder input projections, self-attention, FPN and PAN only in the encoder condition; forbidden detector/model/decoder/proposal-head entry calls raised before execution. Extractor tensors and buffers stayed unchanged. This does not validate real 640x640 frame extraction or GPU execution.'
        for r in d['results']:
            evidence+=f" {r['condition']}: D={r['dimension']}, active frozen parameters={r['active_frozen_parameters']:,}, head parameters={r['head_parameters']:,}."
        evidence+=' The encoder has additional frozen computation but a smaller pooled width and fewer head parameters in this checkpoint; capacity is not matched.'
    if (RUN/'checks/real_extractor_preflight.json').exists():evidence='Real training-only extraction/preflight evidence is in checks/real_extractor_preflight.json; each completed outer fit includes a full saved-model replay.'
    text=f'''# Encoder comparison — {status}\n\n{table}\n\n{findings}\n\nFailure is positive (1), success negative (0); AP uses sklearn average_precision_score, not trapezoidal PR area. Threshold is fixed .5. Only identically completed paired folds enter these tables. One fold is an incomplete pilot.\n\n## Evidence and interpretation\n\n{evidence}\n\nSource inspection, synthetic tests, original-weight CPU path checks, real extraction/training, replay and statistical conclusions are distinct evidence levels. Inspect checks for which actually ran. Reference-only inherited tables, if available, are under `data/reference_only`; their origin hashes and cached CPU replay are in `checks/reference_cached_CPU_replay.json`. They are not paired comparison outputs and do not establish encoder performance. The source calls backbone -> encoder projections -> hybrid encoder final PAN maps, ending before decoder projections or proposals. The two heads share the 128-unit family but can differ in parameter count due to feature width. This tests the complete hybrid representation pipeline, not attention alone, full detection, temporal modelling, robustness or real-time operation.\n\n## Review and independent recalculation\n\n`comparison/identified_outer_predictions_cnn_only.csv` and `comparison/identified_outer_predictions_cnn_plus_encoder.csv` are emitted only when paired folds actually complete; absence means NOT_RUN. Recalculate with `ma_thesis_env/bin/python -B 00_experiments/rt_detr_encoder_comparison/run_experiment.py evaluate`. Per-fit inner predictions and the assembled OOF probabilities are under each condition's fold folder. `data/memberships` records direct G/C/T and prediction keys plus E recording IDs.\n\nReliability uses 10 fixed equal-width bins (last includes 1), plotting mean prediction versus empirical failure frequency. Changed predictions are outcome-selected log-loss illustrations, tied by sample keys, not independent explanatory evidence.\n\n## Walkthrough\n\nInput: exact same 16 hand-camera images per action. Image representation: frozen independent-image CNN or CNN/projections/hybrid encoder, per-scale spatial means then frame mean. Partition-specific head: G-only standardization and training, C-only branch calibration. Two branch probabilities: calibrated visual and identical sensor reference. F2: outer-training held-inner probabilities fit a static C=1 logistic stacker. Held-out evaluation: apply the separately calibrated outer branches and stacker to E. Bounded conclusion: only this fixed completed-action protocol is tested.\n\n## Incomplete work / limits\n\nCurrent stage: {state.get('status')}. Blocker: {state.get('blocker','none recorded')}. No queued job or background continuation exists. Deadline includes waiting, all stages, and reporting; the resume command cannot renew it. No unsupported metric is substituted from historical anonymous results.\n\nEvidence checked: see actual test and runtime records. Still uncertain: any unexecuted extraction, full fitting, replay and paired effect. Defensible conclusion: {('no comparison result yet' if not folds else 'interpret only the paired completed rows under the stated protocol')}.\n'''
    write_text(RUN/'comparison/RESULTS_SUMMARY.md',text)
    write_text(RUN/'README_FIRST.md',f'''# {status}\n\n{findings}\n\n{table}\n\n- [Results](comparison/RESULTS_SUMMARY.md)\n- [Configuration](resolved_config.json) and [plan](experiment_plan.md)\n- [Progress](progress.json), [readiness](checks/readiness.json), [resume instructions](how_to_resume.md)\n- [Review package](REVIEW_PACKAGE.zip)\n\nBlocker: {state.get('blocker','none recorded')}. No background worker is queued. Metrics and directly keyed prediction files are produced only after actual paired fits.\n''')
    return summary


def plot_reliability(tables):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axs=plt.subplots(1,2,figsize=(10,4)); bins=[]
    for ax,(c,t) in zip(axs,tables.items()):
        for branch in ['visual','sensor','fused']:
            p=t['p_'+branch].to_numpy();y=t.failure.to_numpy();index=np.minimum((p*10).astype(int),9);xs=[];ys=[]
            for i in range(10):
                take=index==i
                if not take.any():continue
                x=float(p[take].mean());z=float(y[take].mean());xs.append(x);ys.append(z)
                bins.append(dict(condition=c,branch=branch,bin=i,count=int(take.sum()),mean_probability=x,failure_fraction=z))
            ax.plot(xs,ys,'o-',label=branch)
        ax.plot([0,1],[0,1],'k--');ax.set(title=c,xlabel='Mean predicted failure probability',ylabel='Observed failure fraction');ax.legend()
    fig.tight_layout();fig.savefig(local(RUN/'comparison/plots/reliability.png'),dpi=150);plt.close(fig)
    save_csv(RUN/'comparison/reliability_bins.csv',pd.DataFrame(bins))


def package():
    """Small new review artifacts only; excludes all pretrained/model/cache blobs."""
    files=[]
    for p in STUDY.rglob('*'):
        rel=p.relative_to(STUDY)
        if not p.is_file() or p.is_symlink():continue
        if any(x in rel.parts for x in ['cache','__pycache__','.pytest_cache']):continue
        if p.name in ['REVIEW_PACKAGE.zip','package_manifest.json','package_verification.json'] or '.writing' in p.name:continue
        if p.suffix not in ['.py','.json','.jsonl','.md','.csv','.txt','.png']:continue
        if p.stat().st_size>32*2**20:raise RuntimeError('UNEXPECTED_LARGE_REVIEW_FILE '+str(rel))
        files.append(p)
    manifest={str(p.relative_to(STUDY)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)}
    write(RUN/'provenance/package_manifest.json',manifest)
    files.append(RUN/'provenance/package_manifest.json')
    budget(sum(p.stat().st_size for p in files),scientific=False)
    target=local(RUN/'REVIEW_PACKAGE.zip');tmp=local(RUN/'REVIEW_PACKAGE.writing.zip')
    with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(files):z.write(p,str(p.relative_to(STUDY)))
    import os,hashlib
    os.replace(tmp,target)
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        for name,record in manifest.items():
            data=z.read(name)
            assert len(data)==record['bytes'] and hashlib.sha256(data).hexdigest()==record['sha256']
    write(RUN/'checks/package_verification.json',{'passed':True,'archive_sha256':sha(target),'bytes':target.stat().st_size,'verified_files':len(manifest),'manifest':'provenance/package_manifest.json','large_blobs_excluded':True})
