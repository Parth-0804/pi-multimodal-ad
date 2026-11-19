"""Reconstruct one selected frozen fold; no optimizer or fit calls exist here."""
import numpy as np
import torch
from torch import nn
from scipy.special import expit
from common import REPO,config,sha
from prefix import original,tensor_sha


def transform(x,mean,std):return np.nan_to_num((x-np.asarray(mean,dtype='float32'))/np.asarray(std,dtype='float32'),nan=0,posinf=0,neginf=0).astype('float32')
def linear(x,model):return np.asarray(x)@np.asarray(model['coefficient'])+model['intercept']
def calibrate(raw,model):return expit(linear(np.asarray(raw).reshape(-1,1),model))

class Head(nn.Module):
    def __init__(self,width):
        super().__init__();self.projection=nn.Sequential(nn.Linear(width,128),nn.ReLU(),nn.Dropout(.1));self.classifier=nn.Linear(128,1)
    def forward(self,x):return self.classifier(self.projection(x)).squeeze(-1)

class Pipeline:
    def __init__(self,selected,fold,device='cuda'):
        from common import read
        self.selected=selected;self.fold=fold;self.device=device;self.parts=selected['components'][fold]
        for record in self.parts.values():assert sha(REPO/record['path'])==record['sha256'],'COMPONENT_DRIFT'
        self.extractor=original(device);state=torch.load(REPO/self.parts['head']['path'],map_location='cpu',weights_only=True)
        adapted=selected['condition'].startswith('fine_tuned')
        if adapted:
            assert state.get('stage') is not None,'MISSING_LEARNED_FINAL_STAGE'
            self.extractor.wrapper.model.backbone.model.encoder.stages[-1].load_state_dict(state['stage'],strict=True)
        else:assert state.get('stage') is None,'UNEXPECTED_ADAPTED_STATE'
        self.extractor.eval().requires_grad_(False)
        self.mean=state['mean'].numpy();self.std=state['std'].numpy()
        self.head=Head(len(self.mean)).to(device);self.head.load_state_dict(state['head'],strict=True);self.head.eval().requires_grad_(False)
        self.calibrator=read(REPO/self.parts['calibrator']['path']);self.sensor=read(REPO/self.parts['sensor']['path'])
        self.stacker=read(REPO/self.parts['stacker']['path'])['model'];self.branch='cnn_plus_encoder' if selected['condition']=='cnn_plus_encoder' else 'cnn_only'
        self.initial=self.state()

    def state(self):
        return {'extractor':self.extractor.active_state(),'head':{k:tensor_sha(v) for k,v in self.head.state_dict().items()}}

    def frames(self,pixels):
        assert pixels.ndim==4 and len(pixels)>0
        values=[]
        with torch.inference_mode():
            for offset in range(0,len(pixels),config()['image_batch_frames']):
                values.append(self.extractor(pixels[offset:offset+config()['image_batch_frames']].to(self.device),self.branch).cpu().numpy().copy())
        return np.concatenate(values)

    def visual(self,features):
        with torch.inference_mode():
            z=torch.from_numpy(features).to(self.device).mean(0,keepdim=True)
            mean=torch.as_tensor(self.mean,device=self.device);std=torch.as_tensor(self.std,device=self.device)
            z=torch.nan_to_num((z-mean)/std,nan=0,posinf=0,neginf=0)
            raw=float(self.head(z).cpu()[0])
        return raw,float(calibrate([raw],self.calibrator)[0])

    def sensor_predict(self,statistics):
        x=transform(np.asarray(statistics,dtype='float32')[None,:],self.sensor['mean'],self.sensor['std'])
        raw=float(linear(x,self.sensor['raw'])[0]);return raw,float(calibrate([raw],self.sensor['calibrator'])[0])

    def assert_frozen(self):
        assert self.state()==self.initial,'MODEL_STATE_CHANGED'
        assert all(not m.training for m in self.extractor.modules()) and all(not m.training for m in self.head.modules())
        assert all(not p.requires_grad for p in self.extractor.parameters()) and all(not p.requires_grad for p in self.head.parameters())
