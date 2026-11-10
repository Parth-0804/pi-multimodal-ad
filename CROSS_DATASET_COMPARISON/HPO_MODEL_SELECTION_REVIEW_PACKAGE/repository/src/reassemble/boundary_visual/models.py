import math
import numpy as np
import torch
from torch import nn

BINS={'V1':[(0,8),(8,16)],'V2':[(0,4),(4,12),(12,16)],'V3':[(12,16)],'V4':[(0,4),(12,16)]}
def aggregate(x,variant):
 if variant=='V5':return x
 return np.stack([x[:,a:b].mean(1) for a,b in BINS[variant]],axis=1)
class Binned(nn.Module):
 def __init__(self,bins):
  super().__init__();self.projection=nn.Sequential(nn.Linear(896,128),nn.ReLU(),nn.Dropout(.1));self.classifier=nn.Linear(128*bins,1)
 def forward(self,x):return self.classifier(self.projection(x).flatten(1)).squeeze(-1)
class Ordered(nn.Module):
 def __init__(self):
  super().__init__();self.projection=nn.Sequential(nn.Linear(896,64),nn.ReLU(),nn.Dropout(.1));self.encoder=nn.GRU(64,64,num_layers=1,batch_first=True);self.classifier=nn.Linear(64,1)
  t=torch.arange(16)[:,None];frequency=torch.exp(torch.arange(0,64,2)*(-math.log(10000.)/64));pe=torch.zeros(16,64);pe[:,0::2]=torch.sin(t*frequency);pe[:,1::2]=torch.cos(t*frequency);self.register_buffer('position',pe)
 def forward(self,x):
  z=self.projection(x)+self.position;h,_=self.encoder(z);return self.classifier(h.mean(1)).squeeze(-1)
def make(variant):return Ordered() if variant=='V5' else Binned(len(BINS[variant]))
