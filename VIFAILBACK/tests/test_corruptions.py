import numpy as np
import torch
from vifailback.corruptions import alter_sensor,alter_visual,SCENARIOS,visual_quality


def test_sensor_corruptions_reproducible_without_labels():
    a=np.arange(32*28,dtype='float32').reshape(32,28)
    s=next(s for s in SCENARIOS if s['name']=='missing_channels_0.5')
    x,av=alter_sensor(a,7,s,np.ones(28));y,_=alter_sensor(a,7,s,np.ones(28))
    assert np.array_equal(x,y,equal_nan=True) and av and np.isnan(x).sum()==32*14
    assert np.isfinite(a).all()


def test_missing_camera_retains_other_views_and_quality_reflects_missing_frames():
    x=torch.ones(3,16,3,32,32)*.5
    s=next(s for s in SCENARIOS if s['name']=='camera_unavailable_1')
    y,av=alter_visual(x,1,s);assert av and (y.sum((1,2,3,4))==0).sum()==1
    assert torch.equal(x,torch.ones_like(x)*.5)
    assert visual_quality(y)[2]>visual_quality(x)[2]
