import numpy as np
import torch
from reassemble.section3_visual import pixel_corruption,frame_quality
from reassemble.section3_sensor import corrupt_stream
from reassemble.section2_models import DecisionGate


def test_pixel_noise_reproducible_and_blur_preserves_constant():
    image=np.full((32,32,3),128,np.uint8)
    a=pixel_corruption(image,'V1',.05,7)
    assert np.array_equal(a,pixel_corruption(image,'V1',.05,7))
    assert not np.array_equal(a,image)
    assert np.array_equal(pixel_corruption(image,'V2',4,0),image)
    assert np.allclose(frame_quality([image]*8)[:2],[.5,.5])


def test_raw_channel_and_temporal_dropout_leave_other_values_unchanged():
    t=np.linspace(0,1,101);x=np.tile(np.arange(8),(101,1)).astype(float)
    args=(np.ones(8),np.zeros(8),np.array([1,6]),0,.2)
    channels=corrupt_stream(x,t,.1,.9,'S2',.3,7,*args)
    assert np.isnan(channels[10:91,[1,6]]).all()
    assert np.array_equal(channels[:,[0,2,3,4,5,7]],x[:,[0,2,3,4,5,7]])
    block=corrupt_stream(x,t,0,1,'S3',.3,7,*args)
    assert np.isnan(block[20:51]).all() and np.array_equal(block[:20],x[:20])
    stuck=corrupt_stream(x,t,.1,.9,'S4',1,7,*args)
    assert np.all(stuck[10:91,:6]==0) and np.array_equal(stuck[:,6:],x[:,6:])


def test_single_available_branch_has_zero_gate_gradient():
    model=DecisionGate(4,8);context=torch.randn(5,4);logits=torch.randn(5,2)
    availability=torch.tensor([[1.,0.]]*5)
    value,w=model(context,logits,availability)
    assert torch.equal(value,logits[:,0]) and torch.equal(w,availability)
    torch.nn.functional.binary_cross_entropy_with_logits(value,torch.ones(5)).backward()
    assert all(torch.count_nonzero(p.grad)==0 for p in model.parameters())


def test_vectorized_cluster_metrics_match_sklearn_with_ties_and_zero_weights():
    from reassemble.cluster_metrics import weighted_metrics
    from reassemble.section1_report import metrics
    rng=np.random.default_rng(77);y=np.arange(70)%4==0;p=np.round(rng.uniform(0,1,70),1);hard=p>=.4
    w=rng.integers(0,4,(9,70)).astype(float)
    expected=np.stack([metrics(y,p,hard,row) for row in w])
    assert np.allclose(weighted_metrics(y,p,hard,w,chunk=3),expected,atol=1e-12,rtol=1e-12)


def test_frozen_gate_missing_branch_is_exact_and_ignores_its_quality():
    from reassemble.section3_evaluate import gate_predict
    rng=np.random.default_rng(19);quality=rng.normal(size=(4,36)).astype('float32')
    probs=np.array([[.2,.7],[.3,.8],[.4,.9],[.5,.6]])
    action=np.eye(4,dtype='float32');availability=np.array([[0,1],[1,0],[0,1],[1,0]],dtype='float32')
    model=DecisionGate(42,8)
    checkpoint={'normalizers':{'quality':{'mean':[0.]*36,'std':[1.]*36}},'settings':{'hidden':8},'state_dict':model.state_dict()}
    p,w=gate_predict(checkpoint,'F6',probs,quality,action,availability)
    assert np.array_equal(p,np.array([.7,.3,.9,.5]))
    assert np.array_equal(w,availability)
    quality[availability[:,0]==0,:6]=np.nan;quality[availability[:,1]==0,6:]=1e9
    q,v=gate_predict(checkpoint,'F6',probs,quality,action,availability)
    assert np.array_equal(p,q) and np.array_equal(w,v)
