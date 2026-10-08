import numpy as np
from scripts.thesis.final_validity_audit.diagnostics import TrainingTransform,fit_base,choose_threshold

def test_training_transform_does_not_use_heldout():
 x=np.array([[1.,np.nan],[3.,4.],[1e9,-1e9]])
 a=TrainingTransform().fit(x[:2]);assert np.allclose(a.mean,[2,4]);assert np.allclose(a.std,[1,1])
 assert np.allclose(a.transform([[np.nan,np.nan]]),[[0,0]])

def test_test_outcomes_and_values_cannot_change_fit():
 action=np.eye(2)[[0,1,0,1,0,1,0,1]];x=np.arange(8.)[:,None];y=np.array([0,1,1,0,0,1,1,0]);tr=np.arange(6);te=np.arange(6,8)
 _,a=fit_base(action,x,y,tr,te);x2=x.copy();x2[te]=1e12;y2=y.copy();y2[te]=1-y2[te]
 _,b=fit_base(action,x2,y2,tr,te)
 assert a['mean']==b['mean'] and a['std']==b['std'] and a['coef']==b['coef'] and a['intercept']==b['intercept']

def test_threshold_uses_supplied_training_rows():
 assert choose_threshold(np.array([0,1]),np.array([.1,.9]))==.5
