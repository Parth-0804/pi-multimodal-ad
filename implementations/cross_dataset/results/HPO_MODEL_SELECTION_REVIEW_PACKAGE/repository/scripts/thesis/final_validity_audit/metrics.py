"""Independent weighted metrics from score ties and confusion counts (NumPy only)."""
import numpy as np

NAMES=['AUROC','AUPRC','Brier','ECE','balanced_accuracy','macro_F1','failure_recall','failure_precision','specificity']

def metrics(y,p,hard=None,weights=None):
 y=np.asarray(y);p=np.asarray(p,dtype=np.float64)
 if y.ndim!=1 or p.shape!=y.shape:raise ValueError('shape')
 w=np.ones(len(y)) if weights is None else np.asarray(weights,dtype=np.float64)
 if w.shape!=y.shape or not np.isfinite(w).all() or np.any(w<0):raise ValueError('weights')
 if not np.isin(y,[0,1]).all() or not np.isfinite(p).all() or np.any((p<0)|(p>1)):raise ValueError('labels/probabilities')
 if hard is not None:
  hard=np.asarray(hard)
  if hard.shape!=y.shape or not np.isin(hard,[0,1]).all():raise ValueError('hard decisions')
 keep=w>0;y=y[keep].astype(int);p=p[keep];w=w[keep];hard=None if hard is None else hard[keep]
 out={name:float('nan') for name in NAMES}
 if not len(y):return out
 total=w.sum();pos=np.dot(w,y);neg=total-pos
 order=np.argsort(p,kind='stable');scores=p[order];ys=y[order];ws=w[order]
 starts=np.r_[0,np.flatnonzero(scores[1:]!=scores[:-1])+1]
 positives=np.add.reduceat(ws*ys,starts);negatives=np.add.reduceat(ws*(1-ys),starts)
 if pos and neg:out['AUROC']=float(np.dot(positives,np.cumsum(negatives)-.5*negatives)/(pos*neg))
 if pos:
  dp=positives[::-1];dn=negatives[::-1]
  out['AUPRC']=float(np.sum((dp/pos)*(np.cumsum(dp)/np.cumsum(dp+dn))))
 out['Brier']=float(np.dot(w,(p-y)**2)/total)
 bins=np.minimum(np.floor(p*15).astype(int),14)
 mass=np.bincount(bins,weights=w,minlength=15)
 delta=np.bincount(bins,weights=w*(p-y),minlength=15)
 out['ECE']=float(np.abs(delta[mass>0]).sum()/total)
 if hard is not None:
  tp=float(w[(y==1)&(hard==1)].sum());fn=float(w[(y==1)&(hard==0)].sum());tn=float(w[(y==0)&(hard==0)].sum());fp=float(w[(y==0)&(hard==1)].sum())
  div=lambda a,b:float(a/b) if b else float('nan')
  recall=div(tp,tp+fn);specificity=div(tn,tn+fp)
  out.update(TP=tp,FP=fp,TN=tn,FN=fn,failure_recall=recall,failure_precision=div(tp,tp+fp) if tp+fp else 0.,specificity=specificity,balanced_accuracy=.5*(recall+specificity),macro_F1=.5*((2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0)+(2*tn/(2*tn+fp+fn) if 2*tn+fp+fn else 0)))
 return out

def cluster_draws(groups,replicates,seed):
 unique,inverse=np.unique(np.asarray(groups,dtype=str),return_inverse=True)
 rng=np.random.default_rng(seed)
 counts=np.stack([np.bincount(rng.integers(len(unique),size=len(unique)),minlength=len(unique)) for _ in range(replicates)])
 return unique,inverse,counts

def paired_bootstrap(y,models,groups,replicates=2000,seed=20310927,mask=None,balanced=False,draws=None):
 unique,inverse,counts=cluster_draws(groups,replicates,seed) if draws is None else draws
 size=np.bincount(inverse,minlength=len(unique));base=1/size[inverse] if balanced else np.ones(len(y))
 select=np.ones(len(y),bool) if mask is None else np.asarray(mask,bool)
 out={k:np.full((len(counts),3),np.nan) for k in models};metricnames=['AUPRC','AUROC','Brier']
 for i,c in enumerate(counts):
  weights=c[inverse]*base
  for name,p in models.items():
   v=metrics(np.asarray(y)[select],np.asarray(p)[select],weights=weights[select]);out[name][i]=[v[m] for m in metricnames]
 return out

def interval(values):
 values=np.asarray(values,dtype=float);valid=values[np.isfinite(values)]
 q=np.quantile(valid,[.025,.975],method='linear') if len(valid) else [np.nan,np.nan]
 return {'lower_95':float(q[0]),'upper_95':float(q[1]),'valid_replicates':len(valid),'undefined_replicates':len(values)-len(valid)}
