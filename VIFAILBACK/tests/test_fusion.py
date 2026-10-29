import numpy as np
import pytest
from vifailback.reference import primitives
from vifailback.fusion import fit_gate,gate_predict


def test_f2_is_source_probability_logistic_and_never_source_coefficients():
    source=primitives();p=np.asarray([[.1,.2],[.9,.7],[.2,.4],[.8,.6]]);y=np.asarray([0,1,0,1])
    model=source['stacker'](p,y)
    assert len(model['coefficient'])==2 and model['C']==1 and not model['balanced']
    expected=1/(1+np.exp(-(p@model['coefficient']+model['intercept'])))
    assert np.allclose(source['fused'](p,model),expected)


def test_gate_availability_mask_is_explicit_fallback_and_both_missing_rejected():
    rng=np.random.default_rng(42);q=rng.normal(size=(12,11)).astype('float32')
    p=rng.uniform(.1,.9,size=(12,2)).astype('float32');y=np.arange(12)%2
    model=fit_gate(p,q,y,42,epochs=2)
    av=np.tile([0,1],(12,1));actual,w=gate_predict(model,p,q,av)
    assert np.allclose(actual,p[:,1],atol=1e-6) and np.all(w[:,0]==0)
    with pytest.raises(AssertionError):gate_predict(model,p,q,np.zeros_like(av))
