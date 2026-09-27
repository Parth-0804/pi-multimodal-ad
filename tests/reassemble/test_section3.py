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
