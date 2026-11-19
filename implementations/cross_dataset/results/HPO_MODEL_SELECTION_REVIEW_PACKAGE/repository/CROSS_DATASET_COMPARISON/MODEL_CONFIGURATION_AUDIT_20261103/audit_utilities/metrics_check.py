"""Independent NumPy AP/AUC and fixed-threshold checks on saved predictions."""
import numpy as np


def metrics(y, p, threshold=.5):
    y=np.asarray(y,dtype=int);p=np.asarray(p,dtype=float)
    assert y.shape==p.shape and np.isin(y,[0,1]).all() and np.isfinite(p).all()
    assert ((p>=0)&(p<=1)).all()
    order=np.argsort(-p,kind='stable');ys=y[order];ps=p[order]
    ends=np.r_[np.flatnonzero(np.diff(ps)!=0),len(ps)-1]
    tp=np.cumsum(ys)[ends].astype(float);predicted=ends+1
    positives=int(y.sum());negatives=len(y)-positives
    ap=float(np.sum(np.diff(np.r_[0,tp/positives])*tp/predicted)) if positives else float('nan')
    ranks=np.empty(len(p),float);asc=np.argsort(p,kind='stable');sorted_p=p[asc]
    starts=np.r_[0,np.flatnonzero(np.diff(sorted_p)!=0)+1]
    stops=np.r_[starts[1:],len(p)]
    for a,b in zip(starts,stops):ranks[asc[a:b]]=(a+1+b)/2
    auc=float((ranks[y==1].sum()-positives*(positives+1)/2)/(positives*negatives)) if positives and negatives else float('nan')
    hard=p>=threshold
    TP=int(np.sum(hard&(y==1)));FP=int(np.sum(hard&(y==0)))
    FN=positives-TP;TN=negatives-FP
    precision=TP/(TP+FP) if TP+FP else 0.
    recall=TP/positives if positives else 0.
    specificity=TN/negatives if negatives else 0.
    clipped=np.clip(p,np.finfo(np.float64).eps,1-np.finfo(np.float64).eps)
    return {'AP':ap,'AUROC':auc,'precision':precision,'recall':recall,
            'F1':2*TP/(2*TP+FP+FN) if 2*TP+FP+FN else 0.,
            'balanced_accuracy':(recall+specificity)/2,'specificity':specificity,
            'TN':TN,'FP':FP,'FN':FN,'TP':TP,'Brier':float(np.mean((p-y)**2)),
            'log_loss':float(-np.mean(y*np.log(clipped)+(1-y)*np.log1p(-clipped))),
            'prevalence':float(y.mean())}


def compare(y,p,saved,tolerance=1e-10,threshold=.5):
    calculated=metrics(y,p,threshold)
    differences={key:abs(calculated[key]-float(saved[key])) for key in calculated
                 if key in saved and saved[key] is not None and np.isfinite(float(saved[key]))}
    return {'passed':all(v<=tolerance for v in differences.values()),
            'metric_absolute_differences':differences,'tolerance':tolerance,
            'implementation':'independent NumPy ties-aware AP, ranks AUC, binary formulas',
            'calculated':calculated}
