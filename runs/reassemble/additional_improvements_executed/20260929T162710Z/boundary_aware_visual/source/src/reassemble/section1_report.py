"""Recording-clustered assessment of frozen Section 1 predictions."""
import argparse
import json
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score,average_precision_score
from .section1_features import cohort,sha

MODELS=['prior','majority','action_only','sensor_statistics','rtdetr','patchtst']
METRICS=['AUROC','AUPRC','balanced_accuracy','macro_F1','failure_recall','failure_precision','Brier','ECE']


def metrics(y,p,hard,w=None):
    w=np.ones(len(y)) if w is None else np.asarray(w,dtype=float)
    tp=w[(y==1)&(hard==1)].sum();fn=w[(y==1)&(hard==0)].sum();tn=w[(y==0)&(hard==0)].sum();fp=w[(y==0)&(hard==1)].sum()
    div=lambda a,b:float(a/b) if b else 0.
    ece=0.;bins=np.minimum((p*15).astype(int),14)
    for b in range(15):
        m=bins==b;mass=w[m].sum()
        if mass:ece+=mass/w.sum()*abs(np.average(p[m],weights=w[m])-np.average(y[m],weights=w[m]))
    return np.array([roc_auc_score(y,p,sample_weight=w),average_precision_score(y,p,sample_weight=w),.5*(div(tp,tp+fn)+div(tn,tn+fp)),.5*(div(2*tp,2*tp+fp+fn)+div(2*tn,2*tn+fp+fn)),div(tp,tp+fn),div(tp,tp+fp),np.average((p-y)**2,weights=w),ece])


def correlation(a,b):
    return float(np.corrcoef(a,b)[0,1]) if np.std(a)>0 and np.std(b)>0 else None


def display_correlation(value):
    return 'undefined (constant)' if value is None else round(value,4)


def table(columns,rows):
    return '| '+' | '.join(map(str,columns))+' |\n| '+' | '.join(['---']*len(columns))+' |\n'+''.join('| '+' | '.join(map(str,r))+' |\n' for r in rows)


def assess(config):
    run=Path(config['run_dir']);out=run/'assessment'
    if out.exists():raise RuntimeError('Assessment output already exists; preserve evidence and choose a fresh report namespace')
    out.mkdir();frame=cohort(config);y=frame.failure.to_numpy(dtype=int)
    predictions={}
    for name in MODELS:
        with np.load(run/'predictions'/f'{name}_perm00.npz') as z:predictions[name]={k:z[k] for k in ['y','p','hard','fold']}
        assert np.array_equal(predictions[name]['y'],y)
    groups,gi=np.unique(frame.recording_id,return_inverse=True);rng=np.random.default_rng(config['seed']+50000)
    point=np.stack([metrics(y,predictions[m]['p'],predictions[m]['hard']) for m in MODELS]);boot=[]
    for i in range(config['bootstrap_replicates']):
        w=np.bincount(rng.integers(len(groups),size=len(groups)),minlength=len(groups))[gi]
        if not w[y==1].sum() or not w[y==0].sum():continue
        boot.append(np.stack([metrics(y,predictions[m]['p'],predictions[m]['hard'],w) for m in MODELS]))
        if (i+1)%250==0:print('BOOTSTRAP',i+1,flush=True)
    boot=np.stack(boot);lo,hi=np.quantile(boot,[.025,.975],axis=0)
    result={m:{metric:{'estimate':float(point[j,k]),'lower_95':float(lo[j,k]),'upper_95':float(hi[j,k])} for k,metric in enumerate(METRICS)} for j,m in enumerate(MODELS)}
    differences={};gates={};permutations={}
    for name in ['rtdetr','patchtst']:
        index=MODELS.index(name);differences[name]={};positive=True;point_supported=True
        for base in ['prior','action_only']:
            j=MODELS.index(base);d=point[index]-point[j];dl,dh=np.quantile(boot[:,index]-boot[:,j],[.025,.975],axis=0)
            differences[name][base]={metric:{'estimate':float(d[k]),'lower_95':float(dl[k]),'upper_95':float(dh[k])} for k,metric in enumerate(METRICS)}
            positive &= bool(np.all(dl[:2]>0));point_supported &= bool(np.all(d[:2]>0))
        null=[]
        for perm in range(1,config['permutations']+1):
            meta=json.loads((run/'predictions'/f'{name}_perm{perm:02d}.json').read_text())
            null.append({k:meta[k] for k in ['permutation','AP','AUROC','changed_labels']})
        pvalue=(1+sum(n['AP']>=point[index,1] for n in null))/(1+len(null))
        permutations[name]={'null':null,'p_value_AP':pvalue,'observed_AP':float(point[index,1]),'scheme':config['permutation_scheme']}
        gates[name]='PASS' if positive and pvalue<=.05 else ('FAIL' if not point_supported else 'CONDITIONAL')
    # PatchTST versus statistics is descriptive, not an extra eligibility criterion.
    d=point[5]-point[3];dl,dh=np.quantile(boot[:,5]-boot[:,3],[.025,.975],axis=0)
    differences['patchtst']['sensor_statistics']={metric:{'estimate':float(d[k]),'lower_95':float(dl[k]),'upper_95':float(dh[k])} for k,metric in enumerate(METRICS)}
    decision='FUSION GO — VISUAL AND SENSOR MODALITIES BOTH DEMONSTRATE SIGNAL' if all(g=='PASS' for g in gates.values()) else ('FUSION NO-GO — MULTIPLE INFORMATIVE MODALITIES NOT DEMONSTRATED' if any(g=='FAIL' for g in gates.values()) else 'FUSION CONDITIONAL — EVIDENCE REQUIRES REVIEW')
    complementarity=None
    if all(g=='PASS' for g in gates.values()):
        v=predictions['rtdetr'];s=predictions['patchtst'];vc=v['hard']==y;sc=s['hard']==y
        complementarity={}
        for name,mask in [('all',np.ones(len(y),bool)),('failures',y==1)]+[(a,(frame.action==a).to_numpy()) for a in ['pick','insert','remove','place']]:
            complementarity[name]={'segments':int(mask.sum()),'both_correct':int((mask&vc&sc).sum()),'both_wrong':int((mask&~vc&~sc).sum()),'visual_only_correct':int((mask&vc&~sc).sum()),'sensor_only_correct':int((mask&~vc&sc).sum()),'failure_disagreement':int((mask&(y==1)&(vc!=sc)).sum()),'prediction_correlation':correlation(v['p'][mask],s['p'][mask]),'error_correlation':correlation((~vc)[mask].astype(float),(~sc)[mask].astype(float))}
    calibration={};per_action={};fold_metrics={}
    for name,pred in predictions.items():
        calibration[name]=[];p=pred['p'];bins=np.minimum((p*15).astype(int),14)
        for b in range(15):
            mask=bins==b
            calibration[name].append({'bin':b,'count':int(mask.sum()),'mean_probability':float(p[mask].mean()) if mask.any() else None,'observed_failure_rate':float(y[mask].mean()) if mask.any() else None})
        per_action[name]={a:dict(zip(METRICS,map(float,metrics(y[m],p[m],pred['hard'][m])))) for a in ['pick','insert','remove','place'] if (m:=(frame.action==a).to_numpy()).any()}
        fold_metrics[name]={str(f):dict(zip(METRICS,map(float,metrics(y[m],p[m],pred['hard'][m])))) for f in range(5) if (m:=pred['fold']==f).any()}
    results={'metrics':result,'paired_differences':differences,'permutation_controls':permutations,'modality_gates':gates,'decision':decision,'complementarity':complementarity,'calibration':calibration,'per_action':per_action,'per_fold':fold_metrics,'bootstrap_replicates':len(boot),'bootstrap_unit':'recording; pooled OOF metrics, conditional on fits'}
    (out/'results.json').write_text(json.dumps(results,indent=2,allow_nan=False)+'\n')
    rows=[]
    for m in MODELS:rows.append([m]+[f"{result[m][k]['estimate']:.4f} [{result[m][k]['lower_95']:.4f}, {result[m][k]['upper_95']:.4f}]" for k in METRICS])
    full_table=table(['model']+METRICS,rows)
    (out/'metrics.md').write_text(full_table)
    delta_rows=[]
    for model,baselines in differences.items():
        for base,vals in baselines.items():
            delta_rows.append([model+' minus '+base]+[f"{vals[k]['estimate']:.4f} [{vals[k]['lower_95']:.4f}, {vals[k]['upper_95']:.4f}]" for k in ['AUROC','AUPRC']])
    delta_table=table(['contrast','AUROC difference','AP difference'],delta_rows)
    modelmeta=json.loads((run/'pretrained_model.json').read_text());samplemeta=json.loads(next((run/'features').glob('*.json')).read_text())
    tuning={m:[{'fold':f['fold'],'selected':f.get('selected'),'calibration':f.get('calibration'),'refit':f.get('refit')} for f in json.loads((run/'predictions'/f'{m}_perm00.json').read_text())['folds']] for m in MODELS}
    (out/'tuning.json').write_text(json.dumps(tuning,indent=2)+'\n')
    text='# SECTION 1 — Unimodal models and signal validation\n\n'+datetime.now(timezone.utc).isoformat()+'\n\n'
    text+='## A. Question\n\nDo frozen visual representations and sensor sequences independently identify failure beyond prior/action context on unseen recordings?\n\n'
    text+='## B. Why this came before fusion\n\nFusion needs two demonstrably informative branches. Combining unsupported branches cannot establish complementarity; disagreement alone does not demonstrate fusion benefit.\n\n'
    text+='## C. Evaluation protocol\n\n4,530 complete action segments, 509 failures, 148 source HDF5 recordings. Exact frozen 5 outer / 4 inner recording-disjoint folds; seed 20260927. Models see no identity, text, absolute time or object labels. All scaling, selection, calibration and thresholds are fitted in outer training/inner folds. Epoch/C choices maximize mean inner AP. Inner-OOF sigmoid calibration and balanced-accuracy thresholds precede outer refitting; no test selection. ECE uses 15 fixed bins. '+str(len(boot))+' recording-cluster bootstrap replicates give percentile intervals and paired differences. Intervals condition on fitted models; shared collection-day/scene effects remain a limitation.\n\n'
    text+='## D. Baselines\n\nPrior and majority measure trivial support. Four-action logistic regression tests context shortcuts. Per-channel statistical sensor logistic regression tests whether temporal complexity adds value; C in [0.1,1,10]. Statistics: mean, std, median, min, max, quartiles, range, RMS, progress slope.\n\n'
    text+='## E. RT-DETR\n\nPinned PekingU/rtdetr_r18vd COCO backbone; final three maps spatial-mean pooled, 16 deterministic in-segment frames temporally mean pooled. Shipped preprocessing: bilinear resize to 640x640 RGB and divide by255; do_normalize=False in the pinned processor (no ImageNet mean/std normalization). All backbone parameters frozen; train 128-dimensional ReLU/dropout projection and binary head. AdamW lr .001, decay .001, batch 128; 5 or 10 epochs selected inside training folds. No boxes, detector training or fine-tuning. Exact model revision, processor and weight checksums: pretrained_model.json. Selected budgets/calibration: assessment/tuning.json.\n\n'
    text+='## F. PatchTST\n\nChannels: '+', '.join(samplemeta['channel_names'])+'.\n\n512 in-segment progress positions, no extrapolation/long-gap interpolation. Training-only per-channel standard scaling; missing values filled with training mean and mask retained. Internal scaling disabled; masks do not suppress attention, so missingness robustness is untested. Transformers PatchTST initialized from scratch: 32 hidden units, 2 layers, 4 heads, FFN64, patch32/stride16, dropout .1; channel-independent shared encoder; mean patch pooling, channel concatenation, 128-dimensional projection. AdamW lr .001, decay .001, batch128; 3 or6 epochs selected by inner AP. This bounded budget does not establish optimal architecture suitability.\n\n'
    text+='## G. Results\n\nPoint estimate [95% recording-cluster interval]. Failure is positive; AUPRC means average precision.\n\n'+full_table+'\n'+delta_table+'\nAll outer-fold, per-action and calibration-bin results: assessment/results.json.\n\n'
    text+='## H. Permutation controls\n\n19 full nested refits per deep branch; circular label shifts within each recording/action, preserving stratum prevalence and circular runs. Fixed original folds. This is a conditional cyclic-exchangeability control, not an IID null or a proof against scene/object shortcuts. p=(1+null AP >= observed AP)/20, resolution .05.\n\n'
    text+=table(['model','observed AP','null AP range','p'],[[m,f"{v['observed_AP']:.4f}",f"{min(n['AP'] for n in v['null']):.4f}–{max(n['AP'] for n in v['null']):.4f}",v['p_value_AP']] for m,v in permutations.items()])+'\nComplete null scores and changed-label counts: results.json.\n\n'
    text+='## I. Complementarity\n\n'
    text+=(table(['subset','N','both correct','both wrong','visual only','sensor only','failure disagreement','prediction r','error r'],[[k,v['segments'],v['both_correct'],v['both_wrong'],v['visual_only_correct'],v['sensor_only_correct'],v['failure_disagreement'],display_correlation(v['prediction_correlation']),display_correlation(v['error_correlation'])] for k,v in complementarity.items()])+'\nDescriptive OOF analysis only; no fusion model tested.\n\n') if complementarity else 'Not computed: two informative branches have not both passed the predeclared gate.\n\n'
    text+='## J. Failed attempts / corrections\n\nSee failures_and_corrections.md in this run. Earlier acquisition corrections (audio header length, trailing-idle defect masks, optional report formatter) are retained in the audit; audio is outside this section. No outer-result-driven architecture change is allowed.\n\n'
    text+='## K. Interpretation\n\nThe table and modality gates support only the tested, recording-disjoint models and cohort. PatchTST versus the simple sensor comparator addresses whether the temporal model adds value. Conditional evidence requires researcher review.\n\n'
    text+='## L. What cannot be claimed\n\nNo fusion advantage, corruption robustness, unseen-object/site generalization, causal failure diagnosis, independent segment observations, verified audio alignment, optimal hyperparameters or superiority of all Transformers. OOF uncertainty omits full refitting uncertainty. Conditional permutation invariance and a small Monte Carlo sample limit inference.\n\n'
    text+='## M. Decision\n\n'+table(['modality','decision'],list(gates.items()))+'\nPASS requires positive paired lower bounds versus prior and action-only on both primary metrics, plus conditional permutation p<=.05. Both must pass for the joint GO; this is an intersection-union decision, not choosing a winning modality. Stop for researcher review before Section 2.\n\n'
    text+='## N. Provenance\n\nRun: `'+str(run)+'`. Configuration: `configs/reassemble/section1.json`; protocol: `docs/reassemble/SECTION_1_PROTOCOL.md`. Baseline Git commit and frozen protocol/config/split hashes: provenance.json. Actual training source hashes/device: training_implementation.json. Initial audit checkpoint: 6721414. Input identities: preceding audit input_manifest.json. Model weights/checkpoints, OOF predictions and permutation evidence stay in this unique run. Final output identities: output_manifest.json. No fusion, audio or robustness model was trained.\n\n'+decision+'\n'
    (out/'SECTION_1_UNIMODAL_HANDOFF.md').write_text(text)
    target=Path('artifacts/reassemble/reports/SECTION_1_UNIMODAL_HANDOFF.md')
    with target.open('x') as f:f.write(text)
    files=[p for p in run.rglob('*') if p.is_file() and p.name!='output_manifest.json' and p.suffix!='.log' and p.name not in ['live_status.json']]
    (run/'output_manifest.json').write_text(json.dumps({'timestamp_utc':datetime.now(timezone.utc).isoformat(),'files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)]},indent=2)+'\n')
    print(decision,flush=True)


def main():
    a=argparse.ArgumentParser();a.add_argument('--config',default='configs/reassemble/section1.json');args=a.parse_args();assess(json.loads(Path(args.config).read_text()))

if __name__=='__main__':main()
