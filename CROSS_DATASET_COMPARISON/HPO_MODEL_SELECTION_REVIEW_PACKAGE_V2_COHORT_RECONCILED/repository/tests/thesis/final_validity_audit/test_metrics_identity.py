import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import average_precision_score,roc_auc_score
from scripts.thesis.final_validity_audit.metrics import metrics,cluster_draws,paired_bootstrap
from scripts.thesis.final_validity_audit.common import join_predictions,fingerprint,check_fingerprints

@pytest.mark.parametrize('y,p,ap,auc',[
 ([0,0,1,1],[.1,.2,.8,.9],1.,1.),
 ([1,1,0,0],[.1,.2,.8,.9],5/12,0.),
 ([0,0,1,1],[.5,.5,.5,.5],.5,.5),
 ([1,0,1,0],[.9,.9,.2,.1],7/12,.625),
 ([1,0,1,0],[.8,.8,.4,.4],.5,.5),
])
def test_hand_calculated(y,p,ap,auc):
 x=metrics(y,p);assert x['AUPRC']==pytest.approx(ap);assert x['AUROC']==pytest.approx(auc)

def test_empty_one_class_and_invalid():
 assert all(np.isnan(x) for x in metrics([],[]).values())
 assert np.isnan(metrics([1,1],[.2,.8])['AUROC'])
 assert metrics([1,1],[.2,.8])['AUPRC']==1
 assert np.isnan(metrics([0,0],[.2,.8])['AUPRC'])
 with pytest.raises(ValueError):metrics([0,1],[-2,3])

def test_weighted_ties_library_and_ece_edges():
 y=np.array([0,1,0,1,1,0]);p=np.array([0,1/15,1/15,.5,1,1]);w=np.array([2,1,3,0,2,1])
 x=metrics(y,p,weights=w)
 assert x['AUROC']==pytest.approx(roc_auc_score(y,p,sample_weight=w))
 assert x['AUPRC']==pytest.approx(average_precision_score(y,p,sample_weight=w))
 assert x['Brier']==pytest.approx(np.average((y-p)**2,weights=w))
 expected=(abs((1/15-1)+3/15)+abs(2*(1-1)+(1-0)))/w.sum()
 assert x['ECE']==pytest.approx(expected)

def test_macro_f1_not_failure_f1():
 v=metrics([0,0,0,1],[.1,.1,.1,.1],[0,0,0,0])
 assert v['macro_F1']==pytest.approx(3/7);assert v['failure_precision']==0

def test_identity_join_checks_and_reorders():
 a=pd.DataFrame({'recording_id':['a','b'],'segment_id':['1','1'],'failure':[0,1],'fold':[0,1]})
 b=a.iloc[::-1].copy();b['p']=[.8,.2]
 assert join_predictions(a,b).p.tolist()==[.2,.8]
 with pytest.raises(ValueError):join_predictions(a,pd.concat([b,b.iloc[[0]]]))
 with pytest.raises(ValueError):join_predictions(a,b.iloc[[0]])
 b.loc[b.recording_id=='a','fold']=1
 with pytest.raises(ValueError):join_predictions(a,b)

def test_cluster_pairing_and_equal_recording_mass():
 g=np.array(['a','a','a','b','b']);y=np.array([0,1,0,1,0]);p=np.array([.1,.8,.2,.9,.3]);draws=cluster_draws(g,15,2);u,i,c=draws
 sizes=np.bincount(i);base=1/sizes[i]
 assert np.bincount(i,weights=base).tolist()==pytest.approx([1,1])
 for d in c:assert np.bincount(i,weights=d[i]*base).tolist()==pytest.approx(d.tolist())
 b=paired_bootstrap(y,{'a':p,'b':p.copy()},g,draws=draws,balanced=True)
 assert np.allclose(b['a'],b['b'],equal_nan=True)
 for row in c:assert row.sum()==len(u)

def test_historical_preservation_detection(tmp_path):
 p=tmp_path/'historical';p.write_text('frozen');before=fingerprint([p]);assert check_fingerprints(before)==1
 p.write_text('changed')
 with pytest.raises(ValueError):check_fingerprints(before)

def test_unsupported_bootstrap_draw_not_redrawn():
 y=np.array([0,1]);p=np.array([.2,.8]);g=np.array(['a','b'])
 draws=(np.array(['a','b']),np.array([0,1]),np.array([[2,0],[1,1],[0,2]]))
 b=paired_bootstrap(y,{'x':p},g,draws=draws)
 assert b['x'].shape==(3,3)
 assert np.isnan(b['x'][0,1]) and np.isnan(b['x'][2,1]) and b['x'][1,1]==1
 from scripts.thesis.final_validity_audit.metrics import interval
 assert interval(b['x'][:,1])['undefined_replicates']==2
