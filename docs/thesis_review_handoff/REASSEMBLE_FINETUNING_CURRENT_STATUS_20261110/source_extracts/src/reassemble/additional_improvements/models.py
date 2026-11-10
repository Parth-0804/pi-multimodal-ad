"""Only the architectures specified in the frozen extension protocol."""
import math
import numpy as np
import torch
from torch import nn
from reassemble.section1_models import VisualHead, SensorHead

class TemporalHead(nn.Module):
    def __init__(self, width=896, positions=True):
        super().__init__()
        self.projection=nn.Linear(width,128)
        self.encoder=nn.TransformerEncoder(nn.TransformerEncoderLayer(128,4,256,.1,batch_first=True),1,enable_nested_tensor=False)
        self.classifier=nn.Linear(128,1)
        pe=torch.zeros(16,128);index=torch.arange(16).float()[:,None]
        rate=torch.exp(torch.arange(0,128,2).float()*(-math.log(10000.)/128))
        pe[:,0::2]=torch.sin(index*rate);pe[:,1::2]=torch.cos(index*rate)
        self.register_buffer('position',pe if positions else torch.zeros_like(pe))
    def forward(self,x,mask=None):
        if mask is None: mask=torch.ones(x.shape[:2],dtype=torch.bool,device=x.device)
        assert mask.any(1).all(), 'No valid frames'
        z=self.projection(x)+self.position[None,:x.shape[1]]
        z=self.encoder(z,src_key_padding_mask=~mask)
        z=(z*mask[:,:,None]).sum(1)/mask.sum(1)[:,None]
        return self.classifier(z).squeeze(-1),z

class AnchoredAdjustment(nn.Module):
    def __init__(self, coefficient, intercept, adaptive=True, width=42):
        super().__init__()
        self.register_buffer('coefficient',torch.as_tensor(coefficient,dtype=torch.float32))
        self.register_buffer('intercept',torch.as_tensor(intercept,dtype=torch.float32))
        if adaptive:
            self.adjustment=nn.Sequential(nn.Linear(width,16),nn.ReLU(),nn.Linear(16,2))
            nn.init.zeros_(self.adjustment[-1].weight);nn.init.zeros_(self.adjustment[-1].bias)
        else:
            self.adjustment=None;self.constant=nn.Parameter(torch.zeros(2))
    def forward(self,p,u):
        delta=torch.tanh(self.adjustment(u) if self.adjustment is not None else self.constant.expand(len(p),2))
        effective=self.coefficient*(1+delta)
        raw=self.intercept+(effective*p).sum(-1)
        return raw,delta,effective

def modality_fallback(probability,hard,branches,branch_thresholds,availability):
    probability=np.asarray(probability).copy();hard=np.asarray(hard,dtype=float).copy()
    available=np.asarray(availability,dtype=bool)
    for column in range(2):
        mask=available[:,column]&~available[:,1-column]
        probability[mask]=branches[mask,column]
        hard[mask]=(branches[mask,column]>=np.broadcast_to(branch_thresholds,branches.shape)[mask,column]).astype(float)
    missing=~available.any(1);probability[missing]=np.nan;hard[missing]=np.nan
    return probability,hard
