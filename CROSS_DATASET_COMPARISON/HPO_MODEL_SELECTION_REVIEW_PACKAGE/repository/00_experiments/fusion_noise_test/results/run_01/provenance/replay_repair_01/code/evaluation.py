"""Pooled/fold metrics; stochastic repeats are averaged metrics, never extra rows."""
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score,roc_auc_score,precision_score,recall_score,balanced_accuracy_score,f1_score,brier_score_loss
from common import RUN,config,read,csv,write,sha
KEYS=['recording_id','segment_id']


def metrics(y,p,threshold=.5):
    y=np.asarray(y,int);p=np.asarray(p,float);d=p>=threshold
    assert len(y)==len(p) and np.isfinite(p).all() and ((p>=0)&(p<=1)).all()
    two=len(np.unique(y))==2
    return {'AP':float(average_precision_score(y,p)) if np.any(y==1) else None,'AUROC':float(roc_auc_score(y,p)) if two else None,
        'failure_precision':float(precision_score(y,d,zero_division=0)),'failure_recall':float(recall_score(y,d,zero_division=0)),
        'balanced_accuracy':float(balanced_accuracy_score(y,d)) if two else None,'macro_F1':float(f1_score(y,d,labels=[0,1],average='macro',zero_division=0)),
        'Brier':float(brier_score_loss(y,p))}


def paired_interval(clean,repeats,column='p_fused',difference='clean_minus_new',replicates=None):
    clean=clean.sort_values(KEYS).reset_index(drop=True);repeats=[t.sort_values(KEYS).reset_index(drop=True) for t in repeats]
    for t in repeats:
        assert t[KEYS].values.tolist()==clean[KEYS].values.tolist() and np.array_equal(t.failure,clean.failure),'UNPAIRED_ROWS'
    assert not clean.duplicated(KEYS).any()
    y=clean.failure.to_numpy();groups=clean.recording_id.to_numpy();unique=np.unique(groups);ix=[np.flatnonzero(groups==g) for g in unique]
    def delta(rows):
        base=average_precision_score(y[rows],clean[column].to_numpy()[rows]);other=np.mean([average_precision_score(y[rows],t[column].to_numpy()[rows]) for t in repeats])
        return float(other-base if difference=='new_minus_clean' else base-other)
    count=replicates if replicates is not None else config()['bootstrap_replicates'];rng=np.random.default_rng(314159);values=[];skipped=0
    for _ in range(count):
        rows=np.concatenate([ix[i] for i in rng.integers(0,len(unique),len(unique))])
        if len(np.unique(y[rows]))<2:skipped+=1;continue
        values.append(delta(rows))
    low,high=np.percentile(values,[2.5,97.5]) if values else (None,None)
    return {'difference':delta(np.arange(len(y))),'lower95':float(low) if low is not None else None,'upper95':float(high) if high is not None else None,'effective_replicates':len(values),'skipped_replicates':skipped,'realizations':len(repeats)}


def evaluate():
    if not (RUN/'model_selection/selected_model.json').exists():
        for name,columns in [('robustness_metrics',['family','level','repeat','branch','scope','AP','AP_drop','status']),('paired_differences',['family','level','branch','difference','lower95','upper95']),('modality_sensitivity',['family','level','repeat','fusion_minus_sensor_AP','fusion_minus_visual_AP']),('absence_fallback',['level','policy','AP','coverage'])]:csv(RUN/'comparison'/(name+'.csv'),pd.DataFrame(columns=columns))
        return
    selected=read(RUN/'model_selection/selected_model.json');folds=selected['folds'];groups={}
    for p in (RUN/'predictions').glob('**/complete.json'):
        d=read(p);table=p.parent/'predictions.csv';assert sha(table)==d['predictions_sha256']
        job=d['job'];key=(job['family'],job['level'],job['repeat'])
        groups.setdefault(key,{})[d['fold']]=pd.read_csv(table,dtype={k:str for k in KEYS})
    complete={key:pd.concat([v[fold] for fold in folds],ignore_index=True) for key,v in groups.items() if set(v)==set(folds)}
    if ('clean','clean',0) not in complete:return
    clean=complete[('clean','clean',0)];records=[];sensitivity=[];absence=[];reliability=[]
    for (family,level,repeat),t in complete.items():
        assert set(map(tuple,t[KEYS].values))==set(map(tuple,clean[KEYS].values))
        for scope,q in [('pooled',t)]+[(fold,t.loc[t.fold_name==fold]) for fold in folds]:
            base=clean if scope=='pooled' else clean.loc[clean.fold_name==scope]
            for branch in ['visual','sensor','fused']:
                good=np.isfinite(q['p_'+branch])&(q.status=='OK');n=int(good.sum())
                if n!=len(q):
                    records.append(dict(family=family,level=level,repeat=repeat,branch=branch,scope=scope,status='INCOMPLETE_OR_ABSENT',samples=len(q),finite_predictions=n));continue
                m=metrics(q.failure,q['p_'+branch],selected['thresholds'][branch]);bm=metrics(base.failure,base['p_'+branch],selected['thresholds'][branch])
                records.append(dict(family=family,level=level,repeat=repeat,branch=branch,scope=scope,status='COMPLETE',samples=len(q),failures=int(q.failure.sum()),recordings=q.recording_id.nunique(),AP_drop=bm['AP']-m['AP'],**m))
                if scope=='pooled':
                    bins=np.minimum((q['p_'+branch].to_numpy()*10).astype(int),9)
                    for b in range(10):
                        ii=bins==b
                        if ii.any():reliability.append(dict(family=family,level=level,repeat=repeat,branch=branch,bin=b,count=int(ii.sum()),mean_probability=float(q['p_'+branch].to_numpy()[ii].mean()),failure_fraction=float(q.failure.to_numpy()[ii].mean())))
        if family=='missing_modality':
            if (t.status=='OK').all():absence.append(dict(level=level,policy=t.fallback_policy.iloc[0],coverage=len(t),**metrics(t.failure,t.p_fused)))
        elif (t.status=='OK').all():
            ap=lambda branch:metrics(t.failure,t['p_'+branch])['AP']
            sensitivity.append(dict(family=family,level=level,repeat=repeat,fusion_minus_sensor_AP=ap('fused')-ap('sensor'),fusion_minus_visual_AP=ap('fused')-ap('visual')))
    frame=pd.DataFrame(records);averages=[]
    for (family,level,branch,scope),g in frame.groupby(['family','level','branch','scope']):
        if family in ['image_noise','frame_loss','sensor_noise','sensor_channel_loss','sensor_time_loss'] and set(g.repeat)=={1,2,3} and (g.status=='COMPLETE').all():
            r=g.iloc[0].to_dict();r.update(repeat='mean_of_3_metrics',AP=float(g.AP.mean()),AP_drop=float(g.AP_drop.mean()))
            for metric in ['AUROC','failure_precision','failure_recall','balanced_accuracy','macro_F1','Brier']:r[metric]=float(g[metric].mean())
            averages.append(r)
    csv(RUN/'comparison/robustness_metrics.csv',pd.concat([frame,pd.DataFrame(averages)],ignore_index=True))
    csv(RUN/'comparison/modality_sensitivity.csv',pd.DataFrame(sensitivity));csv(RUN/'comparison/absence_fallback.csv',pd.DataFrame(absence))
    csv(RUN/'comparison/reliability_bins.csv',pd.DataFrame(reliability))
    comparisons=[]
    for family,level in sorted({(k[0],k[1]) for k in complete if k[0] not in ['clean','missing_modality']}):
        reps=[t for (fa,le,_),t in complete.items() if (fa,le)==(family,level)]
        expected=1 if family=='image_blur' else 3
        if len(reps)!=expected or not all((t.status=='OK').all() for t in reps):continue
        for branch in ['visual','sensor','fused']:
            comparisons.append(dict(family=family,level=level,branch=branch,**paired_interval(clean,reps,'p_'+branch)))
    csv(RUN/'comparison/paired_differences.csv',pd.DataFrame(comparisons))
    if len(records):plots(pd.DataFrame(records),pd.DataFrame(reliability))


def plots(m,r):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from common import local
    for family in ['image_noise','sensor_noise','image_blur','frame_loss','sensor_channel_loss','sensor_time_loss']:
        q=m.loc[(m.family==family)&(m.scope=='pooled')&(m.status=='COMPLETE')]
        if q.empty:continue
        fig,ax=plt.subplots(figsize=(6,4))
        for branch in ['fused','visual','sensor']:
            means=q.loc[q.branch==branch].groupby('level').AP.mean().reindex(['mild','medium','strong'])
            ax.plot(['mild','medium','strong'],means,'o-',label=branch)
        ax.set(title=family,ylabel='Failure AP',xlabel='Predefined severity');ax.legend();fig.tight_layout();fig.savefig(local(RUN/'comparison/plots'/(family+'.png')),dpi=140);plt.close(fig)
    if not r.empty:
        fig,ax=plt.subplots(figsize=(6,4))
        for (family,level,repeat),g in r.loc[(r.branch=='fused')&((r.family=='clean')|((r.family.isin(['image_noise','sensor_noise']))&(r.level=='strong')))].groupby(['family','level','repeat']):
            ax.plot(g.mean_probability,g.failure_fraction,'o-',label=f'{family} {level} {repeat}')
        ax.plot([0,1],[0,1],'k--');ax.set(xlabel='Mean predicted failure probability',ylabel='Observed failure fraction');ax.legend(fontsize=7);fig.tight_layout();fig.savefig(local(RUN/'comparison/plots/reliability.png'),dpi=140);plt.close(fig)
