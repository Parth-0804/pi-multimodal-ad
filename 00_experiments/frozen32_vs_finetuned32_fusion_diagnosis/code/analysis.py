"""Evaluate only new matched32/two-epoch results; original seed42 FT outputs are explicit reuse."""
import datetime as dt
import json
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score,roc_auc_score,precision_score,recall_score,log_loss
from common import *

BRANCHES={'visual':'p_visual','sensor':'p_sensor','uniform':'p_uniform','F2':'p_F2'}

def metrics(frame,col):
    y=frame.failure.to_numpy(int);p=frame[col].to_numpy(float);d=p>=.5
    return {'samples':len(frame),'recordings':frame.recording_id.nunique(),'failures':int(y.sum()),'prevalence':float(y.mean()),
        'AP':float(average_precision_score(y,p)) if y.sum() else np.nan,'AUROC':float(roc_auc_score(y,p)) if len(np.unique(y))==2 else np.nan,
        'Brier':float(np.mean((p-y)**2)),'log_loss':float(log_loss(y,p,labels=[0,1])),
        'precision':float(precision_score(y,d,zero_division=0)),'recall':float(recall_score(y,d,zero_division=0)),
        'probability_mean':float(p.mean()),'probability_std':float(p.std()),
        'positive_probability_mean':float(p[y==1].mean()) if np.any(y==1) else np.nan,
        'positive_probability_std':float(p[y==1].std()) if np.any(y==1) else np.nan,
        'negative_probability_mean':float(p[y==0].mean()) if np.any(y==0) else np.nan,
        'negative_probability_std':float(p[y==0].std()) if np.any(y==0) else np.nan,
        'TP':int(np.sum(d&(y==1))),'FP':int(np.sum(d&(y==0))),'threshold':.5}

def true_loss(y,p):
    p=np.clip(np.asarray(p,float),np.finfo(float).eps,1-np.finfo(float).eps)
    return -np.where(np.asarray(y)==1,np.log(p),np.log1p(-p))

def weighted_AP_evaluator(y,p):
    y=np.asarray(y,int);p=np.asarray(p,float);order=np.argsort(-p,kind='stable')
    ends=np.r_[np.flatnonzero(np.diff(p[order])!=0),len(p)-1]
    def calculate(weights):
        w=np.asarray(weights)[order];positives=w*y[order];tp=np.cumsum(positives)[ends];n=np.cumsum(w)[ends]
        if not positives.sum():return np.nan
        precision=np.divide(tp,n,out=np.zeros(len(tp),float),where=n>0)
        return float(np.sum(np.diff(np.r_[0,tp])*precision)/positives.sum())
    return calculate

def table(name,rows,columns=None):
    f=rows if isinstance(rows,pd.DataFrame) else pd.DataFrame(rows,columns=columns)
    save_csv(ROOT/'comparison'/f'{name}.csv',f);return f

def report(status):
    try:
        return _report(status)
    except Exception as exc:
        write(ROOT/'provenance/reporting_error_receipt.json',{
            'utc':utc(),'scientific_status':status,
            'type':type(exc).__name__,'error':str(exc),
            'recovery':'Repair reporting only; preserve fits, predictions and the original clock.'})
        event('REPORTING_BLOCKED',finished=False,scientific_status=status,
              reporting_error=str(exc))
        raise

def _report(status):
    rows=[];oofrows=[];bins=[];calrows=[];coefrows=[];coverage=[];tables={};contrasts=[];complement=[];overlap=[];fit_evidence=[]
    frame=pd.DataFrame(read(STUDY/'data_manifests/cohort_and_frames.json'))
    jobs=read(STUDY/'data_manifests/fit_partitions.json')
    for seed in [42,20261023]:
        matched=[f'fold_{k:02}' for k in range(1,6) if all((ROOT/f'seed_{seed}'/c/f'fold_{k:02}'/'condition_complete.json').exists() for c in CONDITIONS)]
        coverage.append({'seed':seed,'matched_folds':matched,'count':len(matched),'complete':len(matched)==5})
        for condition in CONDITIONS:
            pieces=[]
            for fold in matched:
                dest=ROOT/f'seed_{seed}'/condition/fold;receipt=read(dest/'condition_complete.json')
                assert sha(dest/'assessment_predictions.csv')==receipt['assessment_sha256']
                a=csv(dest/'assessment_predictions.csv');pieces.append(a)
                oo=csv(dest/'oof_branch_predictions.csv')
                for role,data in [('inner_OOF',oo),('outer_assessment',a)]:
                    oofrows.append({'seed':seed,'fold':fold,'condition':condition,'evaluation_role':role,
                        'interpretation':'Visual branch-held-out; these rows train F2' if role=='inner_OOF' else 'Independent outer assessment within this fitted split',**metrics(data,'p_visual')})
                    pp=data.p_visual.to_numpy();bin_index=np.minimum((pp*10).astype(int),9)
                    for bi in range(10):
                        z=data[bin_index==bi]
                        bins.append({'seed':seed,'fold':fold,'condition':condition,'role':role,'bin':bi,'samples':len(z),'failures':int(z.failure.sum()),
                            'mean_probability':z.p_visual.mean(),'observed_failure_fraction':z.failure.mean()})
                model_path=ROOT/f'seed_{seed}'/'f2_fusion'/condition/fold/'model.json';f2=read(model_path)
                coefrows.append({'seed':seed,'fold':fold,'condition':condition,'visual_coefficient':f2['model']['coefficient'][0],
                    'sensor_coefficient':f2['model']['coefficient'][1],'intercept':f2['model']['intercept'],
                    'feature_order':','.join(f2['feature_columns']),'reused_F2':f2['reused'] is not None,
                    'visual_probability_std':float(a.p_visual.std(ddof=0)),'sensor_probability_std':float(a.p_sensor.std(ddof=0))})
            if not pieces:continue
            a=pd.concat(pieces,ignore_index=True).sort_values('sample_id').reset_index(drop=True)
            assert not a.sample_id.duplicated().any();tables[(seed,condition)]=a
            for scope,data in [('pooled',a),*list(a.groupby('fold_name'))]:
                for branch,col in BRANCHES.items():rows.append({'seed':seed,'condition':condition,'scope':scope,'branch':branch,'matched_folds':len(matched),**metrics(data,col)})
        for condition in CONDITIONS:
            for path in sorted((ROOT/f'seed_{seed}'/condition).glob('fold_*/*/complete.json')):
                done=read(path);j=done['job'];cal=read(path.parent/'calibrator.json');fit_evidence.append({'seed':seed,'condition':condition,'fold':j['fold_name'],'role':j['role'],
                    'fit_id':done['fit_id'],'reused':done['reused'],'manifest':str(path.relative_to(STUDY)),'manifest_sha256':sha(path),
                    'model_reference':done['model_reference'],'model_sha256':done['model_sha256'],'epochs':done['epochs']})
                calrows.append({'seed':seed,'condition':condition,'fold':j['fold_name'],'role':j['role'],'slope':cal['coefficient'][0],'intercept':cal['intercept'],
                    'monotonic_direction':'preserves_raw_ranking' if cal['coefficient'][0]>0 else 'reverses_raw_ranking' if cal['coefficient'][0]<0 else 'constant',
                    'G_samples':len(j['G']),'C_samples':len(j['C']),'C_recordings':len(j['C_recordings']),'reused':done['reused'],
                    'calibrator_reference':str((path.parent/'calibrator.json').relative_to(STUDY)),'calibrator_sha256':sha(path.parent/'calibrator.json')})
    metric_table=table('fusion_results',rows,columns=None if rows else ['seed','condition','scope','branch','AP','samples'])
    table('visual_results',metric_table[metric_table.branch=='visual'] if len(metric_table) else metric_table)
    oo=table('oof_vs_assessment',oofrows,columns=None if oofrows else ['seed','fold','condition','evaluation_role','AP'])
    table('reliability_bins',bins);table('calibration_comparison',calrows);coeff=table('F2_coefficients',coefrows)
    table('fit_evidence_index',fit_evidence)
    for seed in [42,20261023]:
        if (seed,CONDITIONS[0]) not in tables:continue
        a,b=[tables[(seed,c)] for c in CONDITIONS]
        assert a[['sample_id','recording_id','segment_id','failure','fold_name']].equals(b[['sample_id','recording_id','segment_id','failure','fold_name']])
        assert np.array_equal(a.p_sensor,b.p_sensor)
        for scope,ix in [('pooled',a.index),*[(f,g.index) for f,g in a.groupby('fold_name')]]:
            for branch in ['visual','uniform','F2']:
                col=BRANCHES[branch];ma=metrics(a.loc[ix],col);mb=metrics(b.loc[ix],col)
                contrasts.append({'seed':seed,'scope':scope,'branch':branch,'frozen_AP':ma['AP'],'finetuned_AP':mb['AP'],'AP_difference':mb['AP']-ma['AP'],
                    'samples':len(ix),'matched_folds':a.loc[ix].fold_name.nunique()})
            y=a.loc[ix].failure.to_numpy(int);s=a.loc[ix].p_sensor.to_numpy();groups={
                'sensor_missed_failure':(y==1)&(s<.5),'sensor_detected_failure':(y==1)&(s>=.5),
                'sensor_false_positive_success':(y==0)&(s>=.5),'sensor_correct_success':(y==0)&(s<.5)}
            for name,mask in groups.items():
                row={'seed':seed,'scope':scope,'group':name,'samples':int(mask.sum())}
                for branch in ['visual','uniform','F2']:
                    p=a.loc[ix,BRANCHES[branch]].to_numpy()[mask];q=b.loc[ix,BRANCHES[branch]].to_numpy()[mask];yy=y[mask]
                    row[branch+'_Brier_change']=float(np.mean((q-yy)**2-(p-yy)**2)) if len(yy) else np.nan
                    row[branch+'_log_loss_change']=float(np.mean(true_loss(yy,q)-true_loss(yy,p))) if len(yy) else np.nan
                complement.append(row)
            for condition,block in [(CONDITIONS[0],a.loc[ix]),(CONDITIONS[1],b.loc[ix])]:
                vc=(block.p_visual.to_numpy()>=.5).astype(int)==y;sc=(s>=.5).astype(int)==y
                for truth in [0,1]:
                    for vcorrect in [False,True]:
                        for scorrect in [False,True]:overlap.append({'seed':seed,'scope':scope,'condition':condition,'failure':truth,'visual_correct':vcorrect,'sensor_correct':scorrect,'samples':int(np.sum((y==truth)&(vc==vcorrect)&(sc==scorrect)))})
    effects=table('fold_comparisons',contrasts,columns=None if contrasts else ['seed','scope','branch','AP_difference'])
    table('complementarity',complement);table('correctness_overlap',overlap)
    # All sensor probabilities also remain identical across seed families.
    if all((s,CONDITIONS[0]) in tables for s in [42,20261023]):
        x=tables[(42,CONDITIONS[0])].set_index('sample_id');z=tables[(20261023,CONDITIONS[0])].set_index('sample_id')
        common_ids=sorted(set(x.index)&set(z.index));assert np.array_equal(x.loc[common_ids].p_sensor,z.loc[common_ids].p_sensor)
    intervals,draw_results,budget=bootstrap_new(tables,coverage,effects)
    ci=table('paired_intervals',intervals,columns=None if intervals else ['seed','branch','contrast','AP_difference','percentile95_low','percentile95_high'])
    table('bootstrap_new_contrast_draws',draw_results);table('budget_comparison',budget)
    stability=[]
    for seed in [42,20261023]:
        for branch in ['visual','uniform','F2']:
            g=effects[(effects.seed==seed)&(effects.branch==branch)] if len(effects) else pd.DataFrame()
            if g.empty:continue
            pooled=g[g.scope=='pooled'].iloc[0];folds=g[g.scope!='pooled']
            cirow=next((r for r in intervals if r['seed']==seed and r['branch']==branch and r['contrast']=='finetuned2_minus_frozen2'),{})
            stability.append({'seed':seed,'branch':branch,'matched_folds':len(folds),'samples':int(pooled.samples),
                'frozen_pooled_AP':pooled.frozen_AP,'finetuned_pooled_AP':pooled.finetuned_AP,'pooled_AP_difference':pooled.AP_difference,
                'frozen_mean_fold_AP':float(folds.frozen_AP.mean()),'finetuned_mean_fold_AP':float(folds.finetuned_AP.mean()),'mean_fold_AP_difference':float(folds.AP_difference.mean()),
                'folds_finetuned_improves':int((folds.AP_difference>0).sum()),'percentile95_low':cirow.get('percentile95_low',np.nan),'percentile95_high':cirow.get('percentile95_high',np.nan),
                'interpretation':'Two seeds described separately; no seed-variance estimate'})
    stable=table('seed_stability',stability,columns=None if stability else ['seed','branch','pooled_AP_difference'])
    plot_results(metric_table,oo,stable,pd.DataFrame(complement))
    causes=cause_assessment(stable,oo,coeff,budget,coverage)
    table('cause_assessment',causes)
    write_reports(status,coverage,metric_table,stable,causes,fit_evidence,budget)
    from review_package import package
    package(status,coverage,fit_evidence)

def bootstrap_new(tables,coverage,effects):
    intervals=[];draw_results=[];budget=[]
    draws=csv(PRIOR/'comparison/bootstrap_draws.csv');order=read(PRIOR/'comparison/bootstrap_recording_order.json');policy=read(PRIOR/'comparison/bootstrap_policy.json')
    assert sha(PRIOR/'comparison/bootstrap_draws.csv')==policy['draws_sha256'] and sha(PRIOR/'comparison/bootstrap_recording_order.json')==policy['recording_order_sha256']
    lookup={name:i for i,name in enumerate(order)}
    for cov in coverage:
        seed=cov['seed']
        if not cov['complete']:continue
        a,b=[tables[(seed,c)] for c in CONDITIONS];y=a.failure.to_numpy(int);cluster=a.recording_id.map(lookup).to_numpy(int)
        funcs={(tag,branch):weighted_AP_evaluator(y,z[BRANCHES[branch]]) for tag,z in [('frozen',a),('finetuned',b)] for branch in ['visual','uniform','F2']}
        baseline=None
        if seed==42:
            parts=[]
            for i in range(1,6):
                folder=PRIOR/'frozen_32_frames'/f'fold_{i:02}';receipt=read(folder/'condition_complete.json');assert sha(folder/'assessment_predictions.csv')==receipt['assessment_sha256'];parts.append(csv(folder/'assessment_predictions.csv'))
            baseline=pd.concat(parts,ignore_index=True).sort_values('sample_id').reset_index(drop=True)
            assert baseline.sample_id.equals(a.sample_id) and np.array_equal(baseline.p_sensor,a.p_sensor)
            for branch,col in [('visual','p_visual'),('F2','p_fused')]:funcs[('original_frozen5',branch)]=weighted_AP_evaluator(y,baseline[col])
        results={branch:[] for branch in ['visual','uniform','F2']};secondary={branch:[] for branch in ['visual','F2']}
        for row in draws.itertuples():
            weights=np.array(json.loads(row.recording_multiplicities))[cluster]
            if not (0<int(weights@y)<int(weights.sum())):continue
            vals={key:fun(weights) for key,fun in funcs.items()}
            for branch in results:
                delta=vals[('finetuned',branch)]-vals[('frozen',branch)];results[branch].append(delta)
                draw_results.append({'seed':seed,'replicate':row.replicate,'branch':branch,'contrast':'finetuned2_minus_frozen2','AP_difference':delta})
            if baseline is not None:
                for branch in secondary:secondary[branch].append(vals[('original_frozen5',branch)]-vals[('frozen',branch)])
        for branch,values in results.items():
            point=effects[(effects.seed==seed)&(effects.branch==branch)&(effects.scope=='pooled')].AP_difference.iloc[0]
            lo,hi=np.percentile(values,[2.5,97.5]);intervals.append({'seed':seed,'branch':branch,'contrast':'finetuned2_minus_frozen2','AP_difference':float(point),'percentile95_low':float(lo),'percentile95_high':float(hi),
                'valid_replicates':len(values),'requested_replicates':2000,'unit':'recording','seed_variability_included':False,'draws_sha256':policy['draws_sha256']})
        if baseline is not None:
            for branch,col in [('visual','p_visual'),('F2','p_fused')]:
                old=float(average_precision_score(y,baseline[col]));new=float(average_precision_score(y,a[BRANCHES[branch]]));ft=float(average_precision_score(y,b[BRANCHES[branch]]))
                lo,hi=np.percentile(secondary[branch],[2.5,97.5]);budget.append({'seed':42,'branch':branch,'original_frozen5_AP':old,'new_frozen2_AP':new,'fixed_finetuned2_AP':ft,
                    'original_finetuned_minus_frozen5':ft-old,'matched_finetuned_minus_frozen2':ft-new,'change_in_contrast_due_to_budget':old-new,
                    'percentile95_low':float(lo),'percentile95_high':float(hi),'status':'Secondary new comparison against old five-epoch baseline'})
                intervals.append({'seed':42,'branch':branch,'contrast':'original_frozen5_minus_new_frozen2_budget_effect','AP_difference':old-new,'percentile95_low':float(lo),'percentile95_high':float(hi),
                    'valid_replicates':len(secondary[branch]),'requested_replicates':2000,'unit':'recording','seed_variability_included':False,'draws_sha256':policy['draws_sha256']})
    return intervals,draw_results,budget

def cause_assessment(stable,oo,coeff,budget,coverage):
    complete=all(x['complete'] for x in coverage)
    rows=[]
    def item(name,for_,against,status='Unresolved'):rows.append({'candidate':name,'evidence_for':for_,'evidence_against_or_limit':against,'status':status})
    if not complete:
        for name in ['Seed instability','Unequal training budget','Limited sensor complementarity','Calibration/F2 interaction','OOF-to-assessment mismatch']:
            item(name,'Available matched coverage is reported; full two-seed evidence is incomplete','No full controlled two-seed cause assessment is possible')
        return rows
    def row(seed,branch):return stable[(stable.seed==seed)&(stable.branch==branch)].iloc[0]
    def confirmed(seed,branch,direction):
        r=row(seed,branch)
        return (r.percentile95_low>0 and r.folds_finetuned_improves>=4) if direction>0 else (r.percentile95_high<0 and r.folds_finetuned_improves<=1)
    diffs=[float(row(s,'F2').pooled_AP_difference) for s in [42,20261023]]
    signs_flip=diffs[0]*diffs[1]<0
    seed_supported=signs_flip and ((confirmed(42,'F2',1) and confirmed(20261023,'F2',-1)) or (confirmed(42,'F2',-1) and confirmed(20261023,'F2',1)))
    item('Seed instability',f'F2 effects by seed: {diffs}; sign reversal={signs_flip}','Only two seed families; recording intervals do not estimate a seed-variance distribution','Supported' if seed_supported else 'Weak evidence' if signs_flip else 'Unresolved')
    budget_detail='; '.join(f"{r['branch']}: old contrast {r['original_finetuned_minus_frozen5']:+.6f}, matched {r['matched_finetuned_minus_frozen2']:+.6f}" for r in budget)
    budget_changed=any(r['original_finetuned_minus_frozen5']*r['matched_finetuned_minus_frozen2']<0 for r in budget)
    item('Unequal training budget',budget_detail,'Direct fixed-seed budget comparison is bounded to seed42; same-seed reuse is not independent replication','Weak evidence' if budget_changed else 'Unresolved')
    patternA=[];patternB=[]
    for s in [42,20261023]:
        v,u,f=[row(s,b) for b in ['visual','uniform','F2']]
        patternA.append(v.pooled_AP_difference>0 and u.pooled_AP_difference>0 and f.pooled_AP_difference<=0)
        patternB.append(v.pooled_AP_difference>0 and u.pooled_AP_difference<=0 and f.pooled_AP_difference<=0)
    supportedA=all(confirmed(s,'visual',1) and confirmed(s,'uniform',1) and confirmed(s,'F2',-1) for s in [42,20261023])
    supportedB=all(confirmed(s,'visual',1) and confirmed(s,'uniform',-1) and confirmed(s,'F2',-1) for s in [42,20261023])
    item('Limited sensor complementarity',f'Predeclared Pattern B by seed: {patternB}; class-conditional true-label changes in complementarity.csv','Not improving AP does not establish absence of image information; probabilities and operating points can differ','Supported' if supportedB else 'Weak evidence' if any(patternB) else 'Unresolved')
    item('Calibration/F2 interaction',f'Predeclared Pattern A by seed: {patternA}; F2 coefficients and calibrators retained','Uniform and F2 use the same calibrated inputs; no causal calibration intervention was performed','Supported' if supportedA else 'Weak evidence' if any(patternA) else 'Unresolved')
    mismatch=[]
    for s in [42,20261023]:
        count=0
        for k in range(1,6):
            fold=f'fold_{k:02}';g=oo[(oo.seed==s)&(oo.fold==fold)]
            def ap(c,r):return g[(g.condition==c)&(g.evaluation_role==r)].AP.iloc[0]
            inner=ap(CONDITIONS[1],'inner_OOF')-ap(CONDITIONS[0],'inner_OOF');outer=ap(CONDITIONS[1],'outer_assessment')-ap(CONDITIONS[0],'outer_assessment')
            c=coeff[(coeff.seed==s)&(coeff.fold==fold)]
            down=c[c.condition==CONDITIONS[1]].visual_coefficient.iloc[0]<c[c.condition==CONDITIONS[0]].visual_coefficient.iloc[0]
            count+=int(inner<0 and outer>0 and down)
        mismatch.append(count)
    supportedE=all(n>=4 for n in mismatch) and all(confirmed(s,'visual',1) and confirmed(s,'F2',-1) for s in [42,20261023])
    item('OOF-to-assessment mismatch',f'Folds with OOF deficit, assessment gain and reduced visual coefficient by seed: {mismatch}/5','Different fits/training sizes/calibration sets; OOF banks overlap; F2 learned on those rows','Supported' if supportedE else 'Weak evidence' if any(mismatch) else 'Unresolved')
    return rows

def plot_results(metrics_table,oo,stable,complement):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    target=ROOT/'comparison/plots';target.mkdir(exist_ok=True,parents=True)
    if metrics_table.empty:return
    plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False})
    def save(fig,name):
        fig.tight_layout();fig.savefig(target/(name+'.png'),dpi=150);fig.savefig(target/(name+'.svg'));plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,4))
    for ax,seed in zip(axes,[42,20261023]):
        for condition in CONDITIONS:
            g=metrics_table[(metrics_table.seed==seed)&(metrics_table.condition==condition)&(metrics_table.branch=='visual')&(metrics_table.scope!='pooled')]
            ax.plot(np.arange(1,len(g)+1),g.AP,marker='o',label=condition)
        ax.set(title=f'Seed {seed}',xlabel='Matched outer fold',ylabel='Visual AP');ax.legend(fontsize=7)
    save(fig,'visual_AP_by_seed_and_fold')
    fig,axes=plt.subplots(1,2,figsize=(11,4))
    for ax,seed in zip(axes,[42,20261023]):
        for condition in CONDITIONS:
            g=metrics_table[(metrics_table.seed==seed)&(metrics_table.condition==condition)&(metrics_table.scope=='pooled')&(metrics_table.branch.isin(['uniform','F2']))]
            ax.plot(g.branch,g.AP,marker='o',label=condition)
        ax.set(title=f'Seed {seed}',ylabel='Pooled AP');ax.legend(fontsize=7)
    save(fig,'uniform_vs_F2_by_condition')
    fig,axes=plt.subplots(1,2,figsize=(11,4))
    for ax,seed in zip(axes,[42,20261023]):
        if not oo.empty:
            for condition in CONDITIONS:
                for role,style in [('inner_OOF','--'),('outer_assessment','-')]:
                    g=oo[(oo.seed==seed)&(oo.condition==condition)&(oo.evaluation_role==role)]
                    ax.plot(np.arange(1,len(g)+1),g.AP,style,marker='o',label=f'{condition}: {role}')
        ax.set(title=f'Seed {seed}',xlabel='Matched outer fold',ylabel='Visual AP');ax.legend(fontsize=6)
    save(fig,'OOF_vs_assessment_visual_AP')
    fig,ax=plt.subplots(figsize=(9,4))
    if not stable.empty:
        g=stable.dropna(subset=['percentile95_low','percentile95_high']);x=np.arange(len(g))
        if len(g):
            # Percentile intervals need not contain the original point estimate.
            # Draw their endpoints directly instead of requiring positive yerr.
            ax.vlines(x,g.percentile95_low,g.percentile95_high)
            ax.scatter(x,g.pooled_AP_difference,zorder=3)
            ax.scatter(x,g.percentile95_low,marker='_')
            ax.scatter(x,g.percentile95_high,marker='_')
        ax.set(xticks=x,xticklabels=[f'{r.seed}: {r.branch}' for r in g.itertuples()],ylabel='Fine-tuned minus frozen AP');ax.axhline(0,color='gray',lw=1)
    save(fig,'paired_AP_differences_with_intervals')
    fig,axes=plt.subplots(1,2,figsize=(11,4))
    for ax,seed in zip(axes,[42,20261023]):
        if not complement.empty:
            g=complement[(complement.seed==seed)&(complement.scope=='pooled')&(complement.group=='sensor_missed_failure')]
            if len(g):ax.bar(['visual','uniform','F2'],[g.iloc[0][b+'_Brier_change'] for b in ['visual','uniform','F2']])
        ax.set(title=f'Seed {seed}',ylabel='Brier change on sensor-missed failures');ax.axhline(0,color='gray',lw=1)
    save(fig,'sensor_missed_failure_complementarity')

def write_reports(status,coverage,metrics_table,stable,causes,fits,budget):
    finished=utc();complete=all(x['complete'] for x in coverage);final_status='COMPLETE' if complete and status!='BLOCKED' else 'BLOCKED' if status=='BLOCKED' else 'PARTIAL_NEW_SEED'
    new_count=sum(not x['reused'] for x in fits);reused=sum(x['reused'] for x in fits)
    lines=['# Frozen32 versus Fine-tuned32: matched two-epoch fusion diagnosis','',f'Status: **{final_status}**. Finished UTC: {finished}.',
        f'Completed visual fits: {new_count} new, {reused} explicitly reused. This is equal epoch/data budget, not equal compute.','',
        '| Seed | Matched folds | Scope |','|---|---:|---|']
    for x in coverage:lines.append(f"| {x['seed']} | {x['count']}/5 | {'Complete common 4,530-action cohort' if x['complete'] else 'Partial matched coverage only'} |")
    lines+=['','## AP results and recording uncertainty','','| Seed | Method | Frozen pooled AP | Fine-tuned pooled AP | Difference | 95% interval | Frozen mean-fold AP | Fine-tuned mean-fold AP |','|---|---|---:|---:|---:|---|---:|---:|']
    for r in stable.itertuples():
        interval=f'[{r.percentile95_low:+.6f}, {r.percentile95_high:+.6f}]' if np.isfinite(r.percentile95_low) else 'Unavailable: incomplete full-cohort coverage'
        lines.append(f'| {r.seed} | {r.branch} | {r.frozen_pooled_AP:.6f} | {r.finetuned_pooled_AP:.6f} | {r.pooled_AP_difference:+.6f} | {interval} | {r.frozen_mean_fold_AP:.6f} | {r.finetuned_mean_fold_AP:.6f} |')
    lines+=['','Pooled AP and mean-fold AP are distinct. Seeds reuse the same recordings and must not be pooled as independent samples. Recording intervals condition on fitted models; two seeds give descriptive sensitivity, not a robust estimate of seed uncertainty. Threshold0.5 and all settings were fixed before assessment.','',
        '## OOF, calibration and complementarity','','`oof_vs_assessment.csv` contains branch-held-out visual scores by seed/fold/condition/role. These OOF rows train F2, so F2 scores on them would be training performance, not independent validation. Read them alongside `F2_coefficients.csv`, `calibration_comparison.csv` and fixed ten-bin reliability counts. Positive calibrator slopes preserve raw within-fit ranking; negative slopes, if observed, reverse it and are reported without retuning. Calibration effects on cross-fold comparability and stacker inputs are not isolated as causal effects.','',
        '`complementarity.csv` reports true-label Brier/log-loss changes separately for sensor-missed/detected failures and sensor-false-positive/correct successes. `correctness_overlap.csv` separates failures and successes at the unchanged0.5 threshold. Sensor probabilities are identical for both arms and seeds. Subset AP is not used to rank different-prevalence groups.','',
        '## Training-budget control','','The source seed42 fine-tuned2 fits are fixed. `budget_comparison.csv` compares original frozen5 with new frozen2 under the same seed, data and head settings. New frozen2 training loss prefixes must agree with the retained original first-two-epoch logs within1e-6. A change in the original contrast can establish a bounded duration effect for this seed; it is not evidence that longer adaptation would improve results.','',
        '## Cause assessment','','| Candidate explanation | Evidence for | Evidence against / limit | Status |','|---|---|---|---|']
    for r in causes:lines.append(f"| {r['candidate']} | {r['evidence_for']} | {r['evidence_against_or_limit']} | {r['status']} |")
    supported=[r['candidate'] for r in causes if r['status']=='Supported']
    conclusion='Supported diagnostic candidate patterns: '+', '.join(supported)+'; a unique causal mechanism is not established.' if supported else 'CAUSE_NOT_RESOLVED'
    lines+=['','No cause is promoted merely because it is plausible. Supported labels require repeated fold/seed directions and relevant directional intervals under the locked protocol. They support candidate patterns rather than unique causation. **Defensible conclusion: '+conclusion+'**','',
        '## Evidence and limits','','Evidence: new and reused fit manifests in `fit_evidence_index.csv`, exact model/prediction/source hashes, three-action saved-model pixel replay for every new fit, new gradient/update checks, original verified replay receipts for reused fits, fixed sensor lineage, OOF membership checks, uniform/F2 arithmetic and source code lock. The original study, raw inputs and historical outputs were not edited.','',
        'Limits: exposed data, exactly two seed families, conditional recording uncertainty, different parameter/compute costs, fixed training/calibration recipe and no external validation. No architecture, corruption, sensor fitting, threshold search or new seed was added. Review is a self-review. Any interrupted/unpaired condition is excluded from matched comparisons and remains visible in its progress/manifests.','',
        'The Git gate was verified against origin/main before this study. See ../../GIT_COMMIT_REPORT.md. No ZIP was uploaded and no further work was scheduled.','']
    extra=[]
    if not stable.empty:
        oo=csv(ROOT/'comparison/oof_vs_assessment.csv')
        for cov in coverage:
            seed=cov['seed'];counts={}
            for role in ['inner_OOF','outer_assessment']:
                up=down=0
                for fold in cov['matched_folds']:
                    g=oo[(oo.seed==seed)&(oo.fold==fold)&(oo.evaluation_role==role)]
                    delta=g[g.condition==CONDITIONS[1]].AP.iloc[0]-g[g.condition==CONDITIONS[0]].AP.iloc[0]
                    up+=int(delta>0);down+=int(delta<0)
                counts[role]=(up,down)
            extra.append(f"Seed {seed}: fine-tuned visual AP is higher/lower in {counts['inner_OOF'][0]}/{counts['inner_OOF'][1]} matched OOF banks and {counts['outer_assessment'][0]}/{counts['outer_assessment'][1]} outer assessments; denominator {cov['count']} matched folds.")
        comp=csv(ROOT/'comparison/complementarity.csv')
        extra+=['','| Seed | Sensor group | Actions | Visual Brier change | Visual log-loss change | Uniform Brier change | F2 Brier change | F2 log-loss change |','|---|---|---:|---:|---:|---:|---:|---:|']
        for r in comp[comp.scope=='pooled'].itertuples():
            extra.append(f'| {r.seed} | {r.group} | {r.samples} | {r.visual_Brier_change:+.6f} | {r.visual_log_loss_change:+.6f} | {r.uniform_Brier_change:+.6f} | {r.F2_Brier_change:+.6f} | {r.F2_log_loss_change:+.6f} |')
        extra+=['','Negative true-label loss changes are improvements. Conditional probability scores do not identify causal sensor dominance.','']
    slot=lines.index('## Training-budget control');lines[slot:slot]=extra
    elapsed=(dt.datetime.now(dt.timezone.utc)-dt.datetime.fromisoformat(clock()['started_utc'])).total_seconds()
    lines+=['',f'Actual elapsed time through evaluation: {elapsed/3600:.3f} hours; archive verification records the final elapsed runtime.','']
    gap_path=ROOT/'provenance/resolved_training_progress_gap.json'
    if gap_path.exists():
        gap=read(gap_path)
        lines += [f"An observed progress-update gap lasted {gap['update_gap_seconds']/60:.2f} minutes and resolved without a training restart. Its cause was not established. The original clock and settings were unchanged; see `../provenance/resolved_training_progress_gap.json`.",'']
    lines += ['Optimizer/RNG restoration has a CPU head test; no deliberate GPU resume-equivalence test was run. Saved-model pixel replays verify the new completed model predictions.','']
    (ROOT/'comparison/RESULTS_SUMMARY.md').write_text('\n'.join(lines))
    (STUDY/'README_FIRST.md').write_text('# Frozen32 versus Fine-tuned32: two-epoch fusion diagnosis\n\n'+f'**{final_status}**. {new_count} new and {reused} reused visual fits. '+', '.join(f"seed {x['seed']}: {x['count']}/5 matched folds" for x in coverage)+'.\n\n'+
        '[Results and cause assessment](results/comparison/RESULTS_SUMMARY.md) · [Protocol](PROTOCOL.md) · [Git gate](GIT_COMMIT_REPORT.md) · [Review ZIP](results/REVIEW_PACKAGE.zip)\n\n'+
        'Visual, fixed sensor, uniform and F2 results are separate; pooled and mean-fold AP are both supplied. Equal epochs/data budgets do not imply equal compute. Two seeds describe sensitivity without establishing seed uncertainty.\n\n'+
        '**'+conclusion+'**. Read the candidate evidence and limits. No further experiment or schedule was launched. Historical Task4 remains excluded.\n')
    write(ROOT/'provenance/final_coverage.json',{'status':final_status,'coverage':coverage,'new_visual_fits_complete':new_count,'reused_visual_fits_complete':reused,'finished_utc':finished})
    event(final_status,finished=True,new_fits_completed=new_count,reused_fits=reused,coverage=coverage,defensible_conclusion=conclusion)

