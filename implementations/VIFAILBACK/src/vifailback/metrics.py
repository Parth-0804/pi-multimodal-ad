"""Episode metrics and paired task-cluster uncertainty; no frame-level scoring."""
import numpy as np
from sklearn.metrics import (average_precision_score,roc_auc_score,balanced_accuracy_score,
                            precision_recall_fscore_support,brier_score_loss,log_loss,confusion_matrix)


def metrics(y,p):
    y=np.asarray(y,dtype=int);p=np.asarray(p,dtype=float)
    assert y.shape==p.shape and len(y) and set(np.unique(y))=={0,1}
    assert np.isfinite(p).all() and np.all((p>=0)&(p<=1))
    predicted=(p>=.5).astype(int)
    precision,recall,f1,support=precision_recall_fscore_support(y,predicted,labels=[0,1],zero_division=0)
    a=average_precision_score(y,p);b=average_precision_score(1-y,1-p)
    edges=np.linspace(0,1,11); bins=np.minimum(np.searchsorted(edges,p,side='right')-1,9)
    calibration=[{'lower':float(edges[i]),'upper':float(edges[i+1]),'count':int((bins==i).sum()),
                  'mean_probability':float(p[bins==i].mean()) if (bins==i).any() else None,
                  'observed_failure':float(y[bins==i].mean()) if (bins==i).any() else None} for i in range(10)]
    ece=sum(r['count']/len(y)*abs(r['mean_probability']-r['observed_failure']) for r in calibration if r['count'])
    return {'episodes':len(y),'positive_prevalence':float(y.mean()),'success_prevalence':float(1-y.mean()),
            'AP_failure':float(a),'AP_success':float(b),'macro_AP':float((a+b)/2),
            'AUROC':float(roc_auc_score(y,p)),'balanced_accuracy':float(balanced_accuracy_score(y,predicted)),
            'macro_F1':float(f1.mean()),'precision_success':float(precision[0]),'recall_success':float(recall[0]),
            'precision_failure':float(precision[1]),'recall_failure':float(recall[1]),
            'Brier':float(brier_score_loss(y,p)),'log_loss':float(log_loss(y,np.clip(p,1e-15,1-1e-15),labels=[0,1])),
            'ECE10':float(ece),'calibration':calibration,'confusion_matrix_0_1':confusion_matrix(y,predicted,labels=[0,1]).tolist()}


def independent_ap(y,p):
    """Direct threshold-integral AP, including tied scores; independent of sklearn."""
    y=np.asarray(y);p=np.asarray(p);assert y.sum()>0
    order=np.argsort(-p,kind='stable');ys=y[order];ps=p[order]
    ends=np.r_[np.flatnonzero(np.diff(ps)!=0),len(ps)-1]
    tp=np.cumsum(ys)[ends]; precision=tp/(ends+1)
    return float(np.sum(np.diff(np.r_[0,tp])*precision)/y.sum())


def independent_check(y,p,reported):
    y=np.asarray(y,dtype=int);p=np.asarray(p,dtype=float)
    a=independent_ap(y,p);b=independent_ap(1-np.asarray(y),1-np.asarray(p))
    for key,value in [('AP_failure',a),('AP_success',b),('macro_AP',(a+b)/2)]:
        assert abs(reported[key]-value)<1e-12,('METRIC_DISAGREEMENT',key)
    cm=np.zeros((2,2),int)
    for actual,predicted in zip(y,np.asarray(p)>=.5):cm[int(actual),int(predicted)]+=1
    assert reported['confusion_matrix_0_1']==cm.tolist()
    assert abs(reported['Brier']-np.mean((np.asarray(y)-p)**2))<1e-12
    precision=np.diag(cm)/np.maximum(cm.sum(0),1);recall=np.diag(cm)/cm.sum(1)
    f1=2*precision*recall/np.maximum(precision+recall,1e-15)
    positive=p[y==1];negative=p[y==0]
    auc=float(np.mean((positive[:,None]>negative[None,:])+.5*(positive[:,None]==negative[None,:])))
    for name,value in [('AUROC',auc),('balanced_accuracy',recall.mean()),('macro_F1',f1.mean()),
                       ('precision_success',precision[0]),('recall_success',recall[0]),
                       ('precision_failure',precision[1]),('recall_failure',recall[1])]:
        assert abs(reported[name]-value)<1e-12,('INDEPENDENT_METRIC_DISAGREEMENT',name)
    clipped=np.clip(p,1e-15,1-1e-15)
    assert abs(reported['log_loss']-np.mean(-y*np.log(clipped)-(1-y)*np.log1p(-clipped)))<1e-12
    return {'independent_AP_AUC_confusion_F1_precision_recall_Brier_logloss_check':True}


def paired_task_bootstrap(y,a,b,task_ids,seed_ids,repeats=2000,seed=20261029):
    """One resampled task set shared by both models and all seeds; average seed deltas.

    This estimates task-sampling variability conditional on these fitted models,
    not uncertainty from collecting another robot/operator or retraining donors.
    """
    y=np.asarray(y);a=np.asarray(a);b=np.asarray(b);g=np.asarray(task_ids);s=np.asarray(seed_ids)
    groups=np.unique(g);seeds=np.unique(s);rng=np.random.default_rng(seed)
    group_index={group:i for i,group in enumerate(groups)}
    gi=np.asarray([group_index[group] for group in g]);kernels=[]
    for sd in seeds:
        j=np.flatnonzero(s==sd);pairs=[]
        for p in [a,b]:
            classes=[]
            for target,score in [(y[j],p[j]),(1-y[j],1-p[j])]:
                order=np.argsort(-score,kind='stable');ends=np.r_[np.flatnonzero(np.diff(score[order])!=0),len(order)-1]
                classes.append((target[order],gi[j][order],ends))
            pairs.append(classes)
        kernels.append(pairs)
    def delta(counts):
        values=[]
        for pairs in kernels:
            scores=[]
            for classes in pairs:
                ap=[]
                for target,index,ends in classes:
                    weights=counts[index];tp=np.cumsum(weights*target)[ends];den=np.cumsum(weights)[ends]
                    if not tp[-1]:return None
                    ap.append(float(np.sum(np.diff(np.r_[0,tp])*tp/np.maximum(den,1))/tp[-1]))
                scores.append(np.asarray([ap[0],ap[1],sum(ap)/2]))
            values.append(scores[0]-scores[1])
        return np.mean(values,axis=0)
    samples=[]
    for _ in range(repeats):
        counts=np.bincount(rng.integers(0,len(groups),len(groups)),minlength=len(groups))
        d=delta(counts)
        if d is not None:samples.append(d)
    assert samples
    point=delta(np.ones(len(groups),dtype=int));interval=np.quantile(samples,[.025,.975],axis=0)
    return {'macro_AP_A_minus_B':float(point[2]),'AP_failure_A_minus_B':float(point[0]),'AP_success_A_minus_B':float(point[1]),
            'task_bootstrap_95_percentile':interval[:,2].tolist(),
            'AP_failure_task_bootstrap_95_percentile':interval[:,0].tolist(),
            'AP_success_task_bootstrap_95_percentile':interval[:,1].tolist(),
            'valid_resamples':len(samples),'seed':seed,'resampling_unit':'canonical task shared across models/seeds',
            'implementation':'integer task multiplicities; weighted threshold AP exactly equals explicitly repeated episode rows',
            'limitation':'conditional on fitted models; task dependence beyond canonical identity remains unknown'}
