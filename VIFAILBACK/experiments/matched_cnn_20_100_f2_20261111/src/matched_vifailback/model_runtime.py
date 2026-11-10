"""Episode pooling with a CPU minibatch head and exact bounded CNN recomputation."""
from __future__ import annotations
import hashlib
from pathlib import Path
import numpy as np
import torch
from torch import nn
from .common import legacy_config, protocol, resolve, sha256, read_json
from vifailback.reference import primitives
from vifailback.visual import backbone as original_backbone


class EpisodeModel(nn.Module):
    def __init__(self, cnn, head, mean, std):
        super().__init__()
        self.backbone = cnn
        self.head = head.cpu()
        self.register_buffer('mean', torch.as_tensor(mean, dtype=torch.float32, device='cpu'))
        self.register_buffer('std', torch.as_tensor(std, dtype=torch.float32, device='cpu'))
        self.full = cnn is not None

    def classify(self, values):
        assert values.device.type == 'cpu'
        return self.head(torch.nan_to_num((values-self.mean)/self.std, nan=0., posinf=0., neginf=0.))

    def forward(self, values):
        if self.full:
            values = torch.stack([episode_features(self.backbone, x, grad=torch.is_grad_enabled()) for x in values]).cpu()
        return self.classify(values)


def make_model(mean, std, seed, full=False, device='cuda'):
    c = legacy_config()
    source = primitives()
    torch.set_num_threads(protocol()['resources']['CPU_threads'])
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    # Original pretrained construction precedes the head seed exactly as in V1/V2.
    cnn = original_backbone(c, 'V2', device) if full else None
    if full:
        source['promote_normalization_affine'](cnn)
        cnn.requires_grad_(True)
    torch.manual_seed(int(seed))
    if str(device).startswith('cuda') and torch.cuda.is_available():
        torch.cuda.manual_seed_all(int(seed))
    head = source['Head'](len(mean))
    result = EpisodeModel(cnn, head, mean, std)
    assert sum(p.numel() for p in head.parameters()) == 114945
    if full:
        assert sum(p.numel() for p in cnn.parameters()) == 11199968
        assert all(p.requires_grad for p in cnn.parameters())
    assert all(p.dtype == torch.float32 for p in result.parameters())
    return result


def cnn_device(cnn):
    return next(cnn.parameters()).device


def frame_features(cnn, x):
    return primitives()['pooled'](cnn, x)


def episode_features(cnn, pixels, chunk=4, *, grad=False):
    assert pixels.ndim == 5 and tuple(pixels.shape[:3]) == (3, 16, 3)
    flat = pixels.flatten(0, 1)
    with torch.set_grad_enabled(grad):
        # Same mean over48 frames as historical equal time/camera mean.
        maps = [frame_features(cnn, part.to(cnn_device(cnn), non_blocking=True)) for part in flat.split(chunk)]
        return torch.cat(maps).mean(0)


def full_batch_backward(model, examples, labels, positive_weight, chunk=4):
    """One loss per episode; one CPU dropout/head execution per minibatch.

    CNN has fixed running moments and no stochastic layers. The first pass yields
    CPU leaves; exact chain rule recomputes each frame chunk with dL/d(mean)/48.
    Caller owns optimizer zeroing, global clipping and its single update.
    """
    assert model.full and 1 <= len(examples) <= 8 and len(examples) == len(labels)
    pooled = torch.stack([episode_features(model.backbone, x, chunk).cpu() for x in examples])
    leaf = pooled.detach().requires_grad_(True)
    logits = model.classify(leaf)
    loss = nn.functional.binary_cross_entropy_with_logits(logits, labels.cpu(), pos_weight=positive_weight.cpu())
    assert torch.isfinite(loss)
    loss.backward()
    assert leaf.grad is not None and torch.isfinite(leaf.grad).all()
    for pixels, derivative in zip(examples, leaf.grad):
        flat = pixels.flatten(0, 1)
        gradient = (derivative / len(flat)).to(cnn_device(model.backbone))
        for part in flat.split(chunk):
            encoded = frame_features(model.backbone, part.to(cnn_device(model.backbone), non_blocking=True))
            (encoded * gradient).sum().backward()
    return loss.detach(), logits.detach()


def global_clip(model, maximum=1.):
    """Global norm covers both CPU head and CUDA CNN, with one common multiplier."""
    parameters = [p for p in model.parameters() if p.grad is not None]
    norm = torch.linalg.vector_norm(torch.stack([torch.linalg.vector_norm(p.grad.detach()).cpu() for p in parameters]))
    if not torch.isfinite(norm):
        raise FloatingPointError('Nonfinite joint CNN/head gradient norm')
    coefficient = (maximum / (norm + 1e-6)).clamp(max=1.)
    with torch.no_grad():
        for p in parameters:
            p.grad.mul_(coefficient.to(p.grad.device))
    return float(norm)


def optimizer_for(model, settings=None):
    c = settings or protocol()['optimizer']
    groups = [{'params': list(model.head.parameters()), 'lr': c['head_lr'], 'name': 'new_CPU_head'}]
    if model.full:
        groups.append({'params': list(model.backbone.parameters()), 'lr': c['backbone_lr'], 'name': 'all_CNN_conv_and_affine'})
    return torch.optim.AdamW(groups, weight_decay=c['weight_decay'], betas=tuple(c['betas']), eps=c['eps'], amsgrad=c['amsgrad'])


def snapshot(model):
    return {n: hashlib.sha256(v.detach().cpu().contiguous().numpy().tobytes()).hexdigest() for n, v in model.state_dict().items()}


def gradients(model):
    expected = {n for n, p in model.named_parameters() if p.requires_grad}
    values = {n: {'finite': bool(torch.isfinite(p.grad).all()), 'nonzero': bool(torch.count_nonzero(p.grad)), 'elements': p.numel()}
              for n, p in model.named_parameters() if p.grad is not None}
    assert set(values) == expected and all(v['finite'] for v in values.values())
    if model.full:
        for prefix in ['backbone.embedder.']+[f'backbone.encoder.stages.{i}.' for i in range(4)]:
            assert any(v['nonzero'] for n,v in values.items() if n.startswith(prefix)), prefix
    return values


def validate_donor():
    from safetensors import safe_open
    p = protocol()['donor']; path = resolve(p['checkpoint'])
    assert sha256(path) == p['sha256']
    receipt = read_json(path.parent/'PHASE1_FIT_COMPLETE.json')
    payload = torch.load(path, map_location='cpu', weights_only=True)
    assert receipt['executed_epochs'] == 100 and receipt['seed'] == 42 and receipt['job_index'] == 2
    assert receipt['arm'] == payload['arm'] == 'C_full_finetuned16'
    assert receipt['selected_model_sha256'] == p['sha256']
    assert payload['selected_epoch'] == receipt['best']['epoch'] == 47
    assert payload['fit_identity'] == receipt['fit_identity']
    weights = {n.removeprefix('backbone.'):v for n,v in payload['model'].items() if n.startswith('backbone.')}
    original_path = resolve(legacy_config()['pretrained_weights'])/'model.safetensors'
    assert sha256(original_path) == 'fe87a5a30f5daf298d10794c7682a63b6107986f97d6a770ba948d89e4340093'
    with safe_open(str(original_path),framework='pt',device='cpu') as f:
        original = {k.removeprefix('model.backbone.model.'):f.get_tensor(k) for k in f.keys() if k.startswith('model.backbone.model.')}
    assert weights.keys() == original.keys() and len(weights) == 115
    changed=[]
    for name,value in weights.items():
        assert value.shape == original[name].shape and value.dtype == original[name].dtype and torch.isfinite(value).all()
        if not torch.equal(value,original[name]): changed.append(name)
    assert not any('running_' in n for n in changed)
    assert all(any(n.startswith(prefix) for n in changed) for prefix in ['embedder.']+[f'encoder.stages.{i}.' for i in range(4)])
    return {'checkpoint_sha256':p['sha256'],'receipt_sha256':sha256(path.parent/'PHASE1_FIT_COMPLETE.json'),
            'selected_epoch':47,'executed_epochs':100,'CNN_tensor_count':115,'changed_CNN_tensors':changed,
            'excluded_source_state_keys':[k for k in payload['model'] if not k.startswith('backbone.')],
            'transfer_scope':'Frozen donor feature bank only; new target head and T-only target scaler'}
