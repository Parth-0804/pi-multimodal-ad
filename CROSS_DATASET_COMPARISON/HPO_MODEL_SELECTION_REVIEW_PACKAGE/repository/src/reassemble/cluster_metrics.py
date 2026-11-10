"""Exact fixed-prediction recording bootstrap, avoiding repeated score sorting."""
import numpy as np
from .section1_report import METRICS,metrics


def draws(groups, count=2000, seed=20310927):
    unique, inverse=np.unique(groups,return_inverse=True)
    rng=np.random.default_rng(seed)
    counts=np.stack([np.bincount(rng.integers(len(unique),size=len(unique)),minlength=len(unique)) for _ in range(count)])
    return counts[:,inverse].astype('float64')


def weighted_metrics(y,p,hard,weights,chunk=128):
    y=np.asarray(y,dtype=int);p=np.asarray(p,dtype=float);hard=np.asarray(hard,dtype=int)
    order=np.argsort(-p,kind='stable');end=np.r_[np.flatnonzero(np.diff(p[order])),len(p)-1]
    yp=y[order];out=[];bins=np.minimum((p*15).astype(int),14)
    masks=np.stack([(y==1)&(hard==1),(y==1)&(hard==0),(y==0)&(hard==0),(y==0)&(hard==1)],axis=1).astype(float)
    residuals=np.stack([np.where(bins==b,y-p,0) for b in range(15)],axis=1)
    for w in np.array_split(weights,max(1,int(np.ceil(len(weights)/chunk)))):
        total=w.sum(1);positive=w@y;negative=total-positive
        assert np.all(positive>0)&np.all(negative>0)
        ordered=w[:,order];tp=np.cumsum(ordered*yp,axis=1)[:,end];fp=np.cumsum(ordered*(1-yp),axis=1)[:,end]
        recall=tp/positive[:,None];fpr=fp/negative[:,None]
        auc=np.sum(np.diff(np.c_[np.zeros(len(w)),fpr],axis=1)*(recall+np.c_[np.zeros(len(w)),recall[:,:-1]])/2,axis=1)
        precision=np.divide(tp,tp+fp,out=np.zeros_like(tp),where=(tp+fp)>0)
        ap=np.sum(np.diff(np.c_[np.zeros(len(w)),recall],axis=1)*precision,axis=1)
        ct=w@masks;tpos,fn,tn,fpos=ct.T
        divide=lambda a,b:np.divide(a,b,out=np.zeros_like(a),where=b!=0)
        balanced=.5*(divide(tpos,tpos+fn)+divide(tn,tn+fpos))
        f1=.5*(divide(2*tpos,2*tpos+fpos+fn)+divide(2*tn,2*tn+fpos+fn))
        out.append(np.stack([auc,ap,balanced,f1,divide(tpos,tpos+fn),divide(tpos,tpos+fpos),(w@((p-y)**2))/total,np.abs(w@residuals).sum(1)/total],axis=1))
    return np.concatenate(out)


def intervals(point,boot):
    low,high=np.quantile(boot,[.025,.975],axis=0)
    return {metric:{'estimate':float(point[i]),'lower_95':float(low[i]),'upper_95':float(high[i])} for i,metric in enumerate(METRICS)}
