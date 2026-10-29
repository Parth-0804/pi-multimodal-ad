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
    cnn=None if condition=='V1' else backbone(c,condition,device)
    torch.manual_seed(seed)
    if str(device).startswith('cuda'):torch.cuda.manual_seed_all(seed)
    # PhaseVisual reuses original Head and promotes all FrozenBN affine for V2/V3.
    return source['PhaseVisual'](cnn,896,mean,std,condition!='V1').to(device)


@lru_cache(maxsize=1)
def processor(weights):
    from transformers import RTDetrImageProcessor
    p=RTDetrImageProcessor.from_pretrained(resolve(weights),local_files_only=True)
    assert p.do_rescale and not p.do_normalize
    assert p.size=={'height':640,'width':640}
    return p


def pixels(c,row):
    """48 RGB images in [camera,time,C,H,W] order; same16 indices in each view."""
    index=positions(row['frame_count'])
    views=[]
    for key in ['video_high','video_left','video_right']:
        frames=rgb_frames(video_path(c,row[key]),index)
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
