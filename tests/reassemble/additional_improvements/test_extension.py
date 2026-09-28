import numpy as np
import pandas as pd
import pytest
import torch
from reassemble.additional_improvements.models import TemporalHead,AnchoredAdjustment,modality_fallback
from reassemble.section1_models import Standardizer,VisualHead,SensorHead
from reassemble.section1b import guard_partition
from reassemble.section3_visual import pixel_corruption

def test_anchor_initialization_and_gradients():
    torch.manual_seed(8);p=torch.rand(10,2);u=torch.randn(10,42)
    model=AnchoredAdjustment([2.,-.3],-.8)
    raw,delta,coef=model(p,u)
    assert torch.allclose(torch.sigmoid(raw),torch.sigmoid(-.8+2*p[:,0]-.3*p[:,1]),atol=1e-7)
    assert torch.equal(delta,torch.zeros_like(delta))
    torch.nn.functional.binary_cross_entropy_with_logits(raw,torch.arange(10).float()%2).backward()
    assert model.adjustment[-1].weight.grad.abs().sum()>0
    assert not model.coefficient.requires_grad
    assert (coef[:,1]<0).all()

def test_order_controls_and_mask():
    torch.manual_seed(2);x=torch.randn(3,16,896);perm=torch.randperm(16)
    model=TemporalHead(positions=False).eval();mean=VisualHead(896,{}).eval()
    with torch.no_grad():
        assert torch.allclose(model(x)[0],model(x[:,perm])[0],atol=1e-5)
        assert torch.allclose(mean(x.mean(1))[0],mean(x[:,perm].mean(1))[0],atol=1e-5)
        mask=torch.ones(3,16,dtype=torch.bool);mask[:,-2:]=False
        altered=x.clone();altered[:,-2:]=10000
        assert torch.allclose(model(x,mask)[0],model(altered,mask)[0],atol=1e-5)
        with pytest.raises(AssertionError):model(x,torch.zeros_like(mask))

def test_partition_parent_isolation():
    frame=pd.DataFrame({'recording_id':['a','a','b','b','c','c']})
    guard_partition(frame,np.array([0,1,2,3]),np.array([4,5]),[(np.array([0,1]),np.array([2,3])),(np.array([2,3]),np.array([0,1]))])
    with pytest.raises(AssertionError):guard_partition(frame,np.array([0,2,3]),np.array([1,4,5]),[])
    # Derivative copies must preserve the recording, not acquire independent IDs.
    parent=np.repeat(np.arange(6),9);groups=frame.recording_id.to_numpy()[parent]
    assert set(groups[parent<4]).isdisjoint(groups[parent>=4])

def test_training_only_scaler_and_fallback():
    x=np.array([[1.,2.],[3.,4.],[1000.,-900.]])
    sc=Standardizer().fit(x[:2]);assert np.array_equal(sc.mean,[2.,3.])
    branches=np.array([[.2,.7],[.4,.3],[.1,.9],[.9,.2]])
    availability=np.array([[1,0],[0,1],[0,0],[1,1]],bool)
    p,h=modality_fallback(np.full(4,.5),np.ones(4),branches,[.3,.4],availability)
    assert p[0]==.2 and h[0]==0 and p[1]==.3 and h[1]==0
    assert np.isnan(p[2]) and np.isnan(h[2]) and p[3]==.5

def test_raw_corruption_reproducible():
    image=np.full((20,30,3),100,np.uint8)
    assert np.array_equal(pixel_corruption(image,'V1',.05,12),pixel_corruption(image,'V1',.05,12))
    assert not np.array_equal(pixel_corruption(image,'V1',.05,12),pixel_corruption(image,'V1',.05,13))

def test_checkpoint_names_do_not_collapse_decimal_penalties():
    from pathlib import Path
    names=[Path(f'outer0_lambda{penalty}_inner{i}_seed{s}') for penalty in [.01,.1,1.] for i in range(4) for s in [20260927,20260928,20260929]]
    fixed=[(p.parent/p.name.replace('.', 'p')).with_suffix('.json') for p in names]
    assert len(set(fixed))==36

def test_corruption_weights_scaling_and_namespaces():
    from reassemble.additional_improvements.robust_fusion import VIEW_WEIGHTS,normalize
    from reassemble.additional_improvements.corruptions import corruption_seed,visual_conditions,sensor_conditions
    assert VIEW_WEIGHTS.sum()==1 and np.allclose(np.repeat(VIEW_WEIGHTS,7).reshape(9,7).sum(0),1)
    u=np.zeros((9,2,42),np.float32);u[:,:,4:40]=np.arange(9)[:,None,None];u[:,:,-2:]=1
    test=u.copy();test[:,:,4:40]=900
    tr,te,mean,std=normalize({'u':u},{'u':test},True)
    assert np.allclose(mean,np.dot(VIEW_WEIGHTS,np.arange(9)))
    assert np.allclose(tr[:,:,4:40].astype(float)*std+mean,u[:,:,4:40],atol=1e-6)
    assert np.all(te[:,:,4:40]>100)
    row=pd.Series(dict(recording_id='r',segment_id='s'))
    c={'seed':20260927};cond=visual_conditions()[0]
    assert corruption_seed(c,row,cond)==corruption_seed(c,row,cond)
    assert corruption_seed(c,row,cond)!=corruption_seed(c,row,{**cond,'split':'validation'})
    assert len(visual_conditions())==41 and len(sensor_conditions('test'))==46
