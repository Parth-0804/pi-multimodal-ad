"""Paired admissibility assessment; no model selection from outer outcomes."""
import json
from pathlib import Path
import numpy as np
from sklearn.metrics import average_precision_score,roc_auc_score
from .section1_report import metrics,METRICS,table,correlation
from .section1b import frozen_predictions,write_json,progress


def complement(y,v,s,mask):
    vc=v['hard']==y;sc=s['hard']==y;n=int(mask.sum())
    cells={'both_correct':int((mask&vc&sc).sum()),'both_wrong':int((mask&~vc&~sc).sum()),'visual_only_correct':int((mask&vc&~sc).sum()),'sensor_only_correct':int((mask&~vc&sc).sum())}
    assert sum(cells.values())==n
    return {'segments':n,**cells,'prediction_correlation':correlation(v['p'][mask],s['p'][mask]) if n else None,'error_correlation':correlation((~vc)[mask].astype(float),(~sc)[mask].astype(float)) if n else None,'oracle_correct':n-cells['both_wrong'],'oracle_correct_fraction':(n-cells['both_wrong'])/n if n else None,'sensor_correct_fraction':float(sc[mask].mean()) if n else None,'visual_correct_fraction':float(vc[mask].mean()) if n else None}


def decide(config,delta,folds,leaveout,rescue_recordings,rescue_lower,p_value):
    g=config['gate'];positive=rescue_recordings>=5 and rescue_lower>0
    improvement=delta['AUPRC']['estimate']>=g['meaningful_AP_gain'] and delta['AUPRC']['lower_95']>0
    coherent=sum(f['AUPRC']>0 for f in folds)>=g['positive_AP_outer_folds_at_least'] and all(f['AUPRC']>0 for f in leaveout)
    auc_safe=delta['AUROC']['lower_95']>g['AUROC_paired_lower_95_gt']
    sensor_valid=p_value<=g['sensor_control_required_p_AP_at_most']
    if positive and improvement and coherent and auc_safe and sensor_valid:decision='FUSION GO'
    elif not positive or (delta['AUPRC']['estimate']<=0 and delta['AUPRC']['upper_95']<=g['meaningful_AP_gain']):decision='FUSION NO-GO'
    else:decision='FUSION CONDITIONAL'
    return {'decision':decision,'positive_failure_complementarity':positive,'meaningful_AP_gain_with_positive_interval':improvement,'coherent_fold_evidence':coherent,'AUROC_noninferiority_supported':auc_safe,'sensor_permutation_pass':sensor_valid,'old_unimodal_intersection_union_gate_applied':False}


def assess(config,frame):
    run=Path(config['run_dir']);out=run/'assessment'
    if (out/'results.json').exists():return
    out.mkdir(exist_ok=True)
    v=frozen_predictions(config,'rtdetr');s=frozen_predictions(config,'sensor_statistics')
    with np.load(run/'stacking/oof.npz') as z:f={k:z[k] for k in ['p','hard','y','fold']}
    y=frame.failure.to_numpy(dtype=int)
    assert all(np.array_equal(x['y'],y) and np.array_equal(x['fold'],s['fold']) for x in [v,s,f])
    names=['sensor_statistics','rtdetr','minimal_late_fusion'];preds=[s,v,f]
    point=np.stack([metrics(y,x['p'],x['hard']) for x in preds]);groups,gi=np.unique(frame.recording_id,return_inverse=True)
    rescue=(y==1)&(v['hard']==y)&(s['hard']!=y);rescue_recordings=int(frame.loc[rescue,'recording_id'].nunique())
    rng=np.random.default_rng(config['seed']+50000);boot=[];rescues=[]
    for i in range(config['bootstrap_replicates']):
        w=np.bincount(rng.integers(len(groups),size=len(groups)),minlength=len(groups))[gi]
        if not w[y==1].sum() or not w[y==0].sum():continue
        boot.append(np.stack([metrics(y,x['p'],x['hard'],w) for x in preds]));rescues.append(float(w[rescue].sum()/w[y==1].sum()))
    boot=np.stack(boot);lo,hi=np.quantile(boot,[.025,.975],axis=0);d=point[2]-point[0];dl,dh=np.quantile(boot[:,2]-boot[:,0],[.025,.975],axis=0)
    result={name:{m:{'estimate':float(point[j,k]),'lower_95':float(lo[j,k]),'upper_95':float(hi[j,k])} for k,m in enumerate(METRICS)} for j,name in enumerate(names)}
    delta={m:{'estimate':float(d[k]),'lower_95':float(dl[k]),'upper_95':float(dh[k])} for k,m in enumerate(METRICS)}
    fold_rows=[];leaveout=[]
    for k in range(5):
        for mask,rows in [(f['fold']==k,fold_rows),(f['fold']!=k,leaveout)]:
            a,b=metrics(y[mask],f['p'][mask],f['hard'][mask]),metrics(y[mask],s['p'][mask],s['hard'][mask])
            rows.append({'fold':k,'segments':int(mask.sum()),'failures':int(y[mask].sum()),'AUROC':float(a[0]-b[0]),'AUPRC':float(a[1]-b[1]),'fusion_AUROC':float(a[0]),'sensor_AUROC':float(b[0]),'fusion_AUPRC':float(a[1]),'sensor_AUPRC':float(b[1])})
    masks={'all':np.ones(len(y),bool),'failures':y==1}
    for a in ['pick','insert','remove','place']:
        masks[a]=(frame.action==a).to_numpy();masks[a+'_failures']=masks[a]&(y==1)
    comp={name:complement(y,v,s,mask) for name,mask in masks.items()}
    null=[]
    for k in range(1,config['permutations']+1):
        r=json.loads((run/'sensor_controls/predictions'/f'sensor_statistics_perm{k:02d}.json').read_text());null.append({a:r[a] for a in ['permutation','AUROC','AP','changed_labels']})
    observed={'AUROC':float(point[0,0]),'AUPRC':float(point[0,1])}
    permutation={'observed':observed,'null':null,'p_AUROC':(1+sum(r['AUROC']>=observed['AUROC'] for r in null))/(len(null)+1),'p_AUPRC':(1+sum(r['AP']>=observed['AUPRC'] for r in null))/(len(null)+1)}
    rescue_ci=np.quantile(rescues,[.025,.975]);gate=decide(config,delta,fold_rows,leaveout,rescue_recordings,float(rescue_ci[0]),permutation['p_AUPRC'])
    evidence={'metrics':result,'fusion_minus_sensor':delta,'outer_fold_differences':fold_rows,'leave_one_outer_fold_out_differences':leaveout,'complementarity':comp,'failure_rescue_recordings':rescue_recordings,'failure_rescue_fraction':{'estimate':float(rescue.sum()/(y==1).sum()),'lower_95':float(rescue_ci[0]),'upper_95':float(rescue_ci[1])},'sensor_permutation':permutation,'gate':gate,'bootstrap_replicates':len(boot),'oracle':'Correct if either original branch is correct; diagnostic using true labels, not deployable.'}
    write_json(out/'results.json',evidence)
    def metric_table():return table(['Model']+METRICS,[[n]+[f"{result[n][m]['estimate']:.4f} [{result[n][m]['lower_95']:.4f}, {result[n][m]['upper_95']:.4f}]" for m in METRICS] for n in names])
    def comp_table(keys):
        cols=['Subset','N','score r','error r','both correct','both wrong','visual only','sensor only','oracle correct','oracle rate']
        rows=[]
        for k in keys:
            x=comp[k];fmt=lambda v:'undefined' if v is None else f'{v:.4f}'
            rows.append([k,x['segments'],fmt(x['prediction_correlation']),fmt(x['error_correlation']),x['both_correct'],x['both_wrong'],x['visual_only_correct'],x['sensor_only_correct'],x['oracle_correct'],fmt(x['oracle_correct_fraction'])])
        return table(cols,rows)
    text='# SECTION 1B — Fusion admissibility handoff\n\n'
    text+='## 1. Why PatchTST was not tuned further\n\nSection1 is frozen. Its tested PatchTST was significantly worse than engineered sensor statistics. The researcher explicitly excluded longer training or another architecture search; this remains a bounded SQ1 negative result, not a claim that all temporal Transformers lack value.\n\n'
    text+='## 2. Why statistical sensors were selected\n\nThis was the strongest Section1 sensor model (AUROC0.7793, AP0.4294). Its frozen per-channel statistics, logistic architecture, training-only scaling, C grid[0.1,1,10], four-inner-fold mean-AP selection, calibration and thresholds were reused. RT-DETR uses its existing frozen representations and the original5/10-epoch head budgets. No backbone fine-tuning or feature re-extraction occurred.\n\n'
    text+='## 3. Statistical-sensor permutation result\n\nSame19 circular shifts within recording/action, same seeds, outer/inner folds and complete branch procedure as Section1. Nulls retain recording/action prevalence and require conditional cyclic exchangeability. Monte Carlo resolution is0.05; no universal IID-chance interpretation. Both null metrics and changed-label counts follow.\n\n'
    text+=table(['Run','AUROC','AUPRC','changed labels'],[['observed',f"{observed['AUROC']:.4f}",f"{observed['AUPRC']:.4f}",0]]+[[r['permutation'],f"{r['AUROC']:.4f}",f"{r['AP']:.4f}",r['changed_labels']] for r in null])
    text+=f"\nPlus-one p-values: AUROC **{permutation['p_AUROC']:.2f}**, AP **{permutation['p_AUPRC']:.2f}**. Numerical reproduction and identical selected C are recorded in sensor_reproduction.json; original BLAS threading is restored after the one-thread reproduction failed its strict parity guard; the failed attempt is retained.\n\n"
    text+='## 4. RT-DETR/statistical-sensor complementarity\n\nOriginal recording-disjoint OOF scores and original training-selected hard decisions, unmodified. Correlations are Pearson; error correlation uses binary errors. Different branch thresholds affect correctness overlap.\n\n'+comp_table(['all'])+'\n'
    text+='## 5. Failure-only complementarity\n\n'+comp_table(['failures'])+f"\nVisual rescues of sensor-missed failures occur in **{rescue_recordings} recordings**. Rescue fraction among all failures: **{evidence['failure_rescue_fraction']['estimate']:.4f} [{rescue_ci[0]:.4f}, {rescue_ci[1]:.4f}]**. The failure-only oracle rate is oracle recall. It uses the true outcome to choose the right model, so it is not deployable and does not establish attainable fusion benefit.\n\n"
    text+='## 6. Per-action complementarity\n\n'+comp_table([a for a in ['pick','insert','remove','place']])+ '\nFailure-only within each action:\n\n'+comp_table([a+'_failures' for a in ['pick','insert','remove','place']])+'\n'
    text+='## 7. Minimal late-fusion result\n\nExactly one static L2 logistic stacker (C1, unweighted, lbfgs, max_iter2000) on two calibrated probabilities. No adaptive/quality gate. Every outer-training meta-row is predicted by branch models whose selection, calibration and scaling exclude that row\'s inner assessment recording. Four sub-inner recording folds implement each inner-training branch procedure. Final branches are refitted on the original outer training data using the exact Section1 procedure; their predictions must numerically match the frozen branch evidence.\n\nThe fixed stacker fits only outer-training inner-OOF probabilities. Its decision threshold uses meta-cross-fitted training predictions, balanced accuracy, grid0.01..0.99 and ties nearest0.5. No extra calibrator or stacker hyperparameter search. These threshold scores condition on the branch OOF matrix and are not claimed unbiased inner performance estimates. No outer-test OOF score was used to fit fusion.\n\n'+metric_table()+'\n'
    text+='## 8. Paired uncertainty and coherence\n\n2,000 paired recording-cluster percentile bootstrap replicates; intervals condition on fitted models. Differences are fusion minus statistical sensors; lower Brier/ECE is better.\n\n'
    text+=table(['Metric','Difference [95% interval]'],[[m,f"{delta[m]['estimate']:.4f} [{delta[m]['lower_95']:.4f}, {delta[m]['upper_95']:.4f}]"] for m in METRICS])+'\n'
    text+=table(['Outer fold','N','failures','AUROC difference','AP difference'],[[r['fold'],r['segments'],r['failures'],f"{r['AUROC']:.4f}",f"{r['AUPRC']:.4f}"] for r in fold_rows])+'\n'
    text+=table(['Omitted outer fold','Pooled AUROC difference','Pooled AP difference'],[[r['fold'],f"{r['AUROC']:.4f}",f"{r['AUPRC']:.4f}"] for r in leaveout])+'\n'
    text+='The rule was frozen before Section1B outcomes: AP gain>=0.01 with lower95%>0, >=3 positive outer-fold AP differences, all leave-one-fold-out AP differences>0, AUROC lower95%>-0.01, positive failure complementarity across>=5 recordings, and sensor conditional permutation AP p<=0.05. The old standalone RT-DETR intersection-union gate is not used.\n\n'+table(['Requirement','Satisfied'],[[k,v] for k,v in gate.items() if k not in ['decision','old_unimodal_intersection_union_gate_applied']])+'\n'
    text+='## 9. Allowed claims\n\nComplementarity describes the frozen predictions on this cohort. The paired results quantify the incremental performance of this one predeclared stacker over the selected sensor model. The permutation result addresses the specified conditional null only. Any positive decision supports a bounded next-phase comparison, not a claim that complex gating is needed.\n\n'
    text+='## 10. Claims not supported\n\nNo optimal architecture, adaptive gating, corruption robustness, audio benefit, causal diagnosis, online warning, unseen-site/object generalization or deployable oracle. This follow-up hypothesis and sensor choice were informed by Section1 results on the same folds: it is an adaptive exploratory assessment, not independent confirmatory evidence. Nested refitting prevents training leakage but does not erase that prior outcome-informed study choice. No new held-out dataset was added.\n\n'
    text+='## 11. Exact recommendation for Section2\n\n'
    if gate['decision']=='FUSION GO':text+='After researcher review, authorize a bounded clean fusion comparison using frozen RT-DETR and statistical-sensor branches, with this stacker and the strong sensor baseline retained. Do not substitute PatchTST without a separately authorized rationale. Gate complexity must demonstrate added value over static fusion. This run does not itself authorize Section2.\n\n'
    elif gate['decision']=='FUSION CONDITIONAL':text+='Do not automatically begin Section2. Review the paired uncertainty and fold coherence. If the researcher explicitly approves conditional continuation, retain statistical sensors as the sensor branch and this exact static stacker as a comparator; characterize architecture comparisons as exploratory. No further branch tuning is implied.\n\n'
    else:text+='Do not advance to full fusion architecture training on this evidence. Retain the statistical-sensor result, PatchTST negative result and measured visual complementarity as thesis evidence; the tested minimal fusion has not justified added complexity. Further work needs a new explicit question and approval.\n\n'
    text+='## 12. Artifact paths, configs and commits\n\nRun: `'+str(run)+'`. Frozen config: `configs/reassemble/section1b.json`; protocol: `docs/reassemble/SECTION_1B_PROTOCOL.md`; live/final IDE handoff: `docs/reassemble/SECTION_1B_CONTINUATION.md`. Section1 evidence commit08d498d; branch implementation852a123. Current implementation commit/source hashes: implementation.json. Protocol/config/source identities: provenance.json. All metrics, controls and complementarity: assessment/results.json. Subfold memberships, coefficients, thresholds, branch parity and inner probabilities: stacking/. Sensor null predictions and selections: sensor_controls/predictions/. Input feature/OOF identities remain in the unchanged Section1 final_output_manifest.json. New final validation and output identities are recorded separately in this run.\n\n'
    text+='## 13. Failed attempts and corrections\n\nSee failures_and_corrections.md and validation.json for executed checks and any exceptions. No failed attempt is erased or used to alter the decision rule. Section1 remains unchanged; this follow-up replaces neither its results nor its original gate.\n\n'+gate['decision']+'\n'
    write_json(out/'stacker_coefficients.json',[json.loads((run/'stacking'/f'outer{k}.json').read_text())['stacker'] for k in range(5)])
    (out/'SECTION_1B_FUSION_ADMISSIBILITY_HANDOFF.md').write_text(text)
    target=Path('artifacts/reassemble/reports/SECTION_1B_FUSION_ADMISSIBILITY_HANDOFF.md')
    with target.open('x') as h:h.write(text)
    progress(config,gate['decision']+'; report generated')
