from copy import deepcopy
from types import SimpleNamespace
import numpy as np
import torch
from torch import nn
from vifailback.visual import chunked_backward,features


class TinyCNN(nn.Module):
    def __init__(self):
        super().__init__();self.conv=nn.Conv2d(3,4,3,padding=1)
    def forward(self,x):return SimpleNamespace(feature_maps=[torch.relu(self.conv(x))])


class TinyModel(nn.Module):
    def __init__(self):
        super().__init__();self.backbone=TinyCNN();self.head=nn.Sequential(nn.Linear(4,1),nn.Flatten(0))
        self.register_buffer('mean',torch.zeros(4));self.register_buffer('std',torch.ones(4))


def test_two_pass_gradient_matches_full_graph_for_all48_images():
    torch.manual_seed(42);a=TinyModel();b=deepcopy(a);x=torch.rand(3,16,3,8,8)
    z=features(a.backbone,x,chunk=4,grad=True).mean(0,keepdim=True)
    loss=nn.functional.binary_cross_entropy_with_logits(a.head(z),torch.ones(1),pos_weight=torch.tensor(.2))
    loss.backward();other,_=chunked_backward(b,x,torch.ones(1),torch.tensor(.2),chunk=4)
    assert torch.allclose(loss,other,atol=1e-7)
    for (n,p),(m,q) in zip(a.named_parameters(),b.named_parameters()):
        assert n==m and torch.allclose(p.grad,q.grad,rtol=1e-5,atol=1e-7),(n,p.grad,q.grad)


def test_camera_temporal_pool_is_equal_mean_and_order_invariant():
    cnn=TinyCNN();x=torch.rand(3,16,3,8,8)
    a=features(cnn,x,4).reshape(3,16,4)
    b=features(cnn,x.flip(1),4).reshape(3,16,4)
    assert torch.allclose(a.mean((0,1)),b.mean((0,1)),atol=1e-6)
