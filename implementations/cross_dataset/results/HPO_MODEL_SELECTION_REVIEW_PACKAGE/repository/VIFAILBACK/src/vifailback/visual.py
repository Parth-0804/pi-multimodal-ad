"""Source-owned CNN/head with fixed multiview pooling and exact chunked gradients."""
import gc
import hashlib
from functools import lru_cache
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from .common import config,resolve,sha,signature,video_path
from .reference import primitives
from .video import positions,rgb_frames


def backbone(c,condition,device='cpu'):
    from transformers import RTDetrForObjectDetection
    original=resolve(c['pretrained_weights'])
    assert sha(original/'model.safetensors')=='fe87a5a30f5daf298d10794c7682a63b6107986f97d6a770ba948d89e4340093'
    wrapper=RTDetrForObjectDetection.from_pretrained(original,local_files_only=True)
    cnn=wrapper.model.backbone.model
    del wrapper
    donor=None
    if condition=='V3':
        source=resolve(c['donor_checkpoint']);assert sha(source)==c['donor_sha256']
        donor=torch.load(source,map_location='cpu',weights_only=True)
        assert donor['selected_epoch']==47 and donor['seed']==42
        weights={k[len('backbone.'):]:v for k,v in donor['model'].items() if k.startswith('backbone.')}
        assert len(weights)==len(cnn.state_dict())==115
        cnn.load_state_dict(weights,strict=True)
    cnn.eval();cnn.requires_grad_(False)
    return cnn.to(device)


def make(c,condition,mean,std,seed,device):
    source=primitives();torch.set_num_threads(c['cpu_threads'])
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    cnn=None if condition=='V1' else backbone(c,condition,device)
    torch.manual_seed(seed)
    if str(device).startswith('cuda'):torch.cuda.manual_seed_all(seed)
    # PhaseVisual reuses original Head and promotes all FrozenBN affine for V2/V3.
    model=multiview_class()(cnn,896,mean,std,condition!='V1').to(device)
    assert all(p.dtype==torch.float32 for p in model.parameters())
    return model


@lru_cache(maxsize=1)
def multiview_class():
    base=primitives()['PhaseVisual']
    class MultiviewVisual(base):
        """One output per action; preserve source modules, fix the camera batch axis.

        Frozen input is[B,896]. Full RGB input is[B,3,16,3,H,W], or
        [3,16,3,H,W] for one episode. Training uses chunked_backward to avoid
        retaining all48 frame activation graphs; forward also supports ordinary
        gradients when sufficient memory is available.
        """
        def forward(self,x):
            if self.backbone is None:
                assert x.ndim==2 and x.shape[1]==len(self.mean)
                return super().forward(x)
            if x.ndim==5:x=x.unsqueeze(0)
            assert x.ndim==6 and tuple(x.shape[1:4])==(3,16,3)
            z=torch.stack([features(self.backbone,episode,4,grad=torch.is_grad_enabled()).mean(0) for episode in x])
            return self.head(torch.nan_to_num((z-self.mean)/self.std,nan=0,posinf=0,neginf=0))
    return MultiviewVisual


@lru_cache(maxsize=1)
def processor(weights):
    from transformers import RTDetrImageProcessor
    p=RTDetrImageProcessor.from_pretrained(resolve(weights),local_files_only=True)
    assert p.do_rescale and not p.do_normalize
    assert p.size=={'height':640,'width':640}
    return p


@lru_cache(maxsize=16384)
def verify_changed_source(path,size,mtime,expected):
    assert sha(Path(path))==expected,'VIDEO_SOURCE_CHANGED_AFTER_QC'
    return True


def pixels(c,row):
    """48 RGB images in [camera,time,C,H,W] order; same16 indices in each view."""
    index=positions(row['frame_count'])
    views=[]
    for view,key in enumerate(['video_high','video_left','video_right']):
        path=video_path(c,row[key])
        if 'camera_sha256' in row:
            st=path.stat();assert st.st_size==row['camera_bytes'][view]
            if st.st_mtime_ns!=row['camera_mtime_ns'][view]:verify_changed_source(str(path),st.st_size,st.st_mtime_ns,row['camera_sha256'][view])
        frames=rgb_frames(path,index)
        if 'selected_RGB_sha256' in row:
            assert [hashlib.sha256(f.tobytes()).hexdigest() for f in frames]==row['selected_RGB_sha256'][view],'FRAME_IDENTITY_OR_ORDER_DRIFT'
        # Use the verified original processor, including its PIL bilinear resize.
        x=torch.from_numpy(processor(c['pretrained_weights'])(images=list(frames),return_tensors='np')['pixel_values'])
        views.append(x)
    result=torch.stack(views)
    assert result.shape==(3,16,3,640,640) and torch.isfinite(result).all()
    return result


def features(cnn,x,chunk=4,*,grad=False):
    flat=x.flatten(0,1) if x.ndim==5 else x
    assert flat.ndim==4
    pooled=primitives()['pooled']
    with torch.set_grad_enabled(grad):
        return torch.cat([pooled(cnn,part) for part in flat.split(chunk)],dim=0)


def chunked_backward(model,x,target,positive_weight,divisor=1,chunk=4):
    """Exact chain rule for mean aggregation, with bounded CNN activation memory.

    First pass gives a leaf aggregate; a second deterministic CNN pass propagates
    d(loss)/d(mean) to every frame. FrozenBN moments and no CNN dropout make the
    two passes identical. Only the original head has dropout (one execution).
    """
    flat=x.flatten(0,1) if x.ndim==5 else x
    with torch.no_grad():z=features(model.backbone,flat,chunk).mean(0,keepdim=True)
    leaf=z.detach().requires_grad_(True)
    logit=model.head(torch.nan_to_num((leaf-model.mean)/model.std,nan=0,posinf=0,neginf=0))
    loss=F.binary_cross_entropy_with_logits(logit,target.reshape(1),pos_weight=positive_weight)/divisor
    loss.backward()
    assert leaf.grad is not None and torch.isfinite(leaf.grad).all()
    gradient=leaf.grad.detach()/len(flat)
    pooled=primitives()['pooled']
    for part in flat.split(chunk):
        encoded=pooled(model.backbone,part)
        (encoded*gradient).sum().backward()
    return loss.detach()*divisor,logit.detach()


def snapshot(module):
    return {n:hashlib.sha256(v.detach().cpu().contiguous().numpy().tobytes()).hexdigest()
            for n,v in module.state_dict().items()}


def gradient_evidence(model):
    expected={n for n,p in model.named_parameters() if p.requires_grad}
    gradients={n:{'finite':bool(torch.isfinite(p.grad).all()),'nonzero':bool(torch.count_nonzero(p.grad))}
               for n,p in model.named_parameters() if p.grad is not None}
    assert set(gradients)==expected and all(v['finite'] for v in gradients.values())
    if model.full:
        for prefix in ['backbone.embedder.']+[f'backbone.encoder.stages.{i}.' for i in range(4)]+['head.']:
            assert any(v['nonzero'] for n,v in gradients.items() if n.startswith(prefix)),prefix
    return gradients
