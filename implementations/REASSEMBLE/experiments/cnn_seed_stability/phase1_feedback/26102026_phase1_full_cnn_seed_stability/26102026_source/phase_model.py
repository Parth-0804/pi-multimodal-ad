"""Small full-backbone extension of the verified historical CNN primitive."""
import sys
import numpy as np
import torch
from torch import nn

from phase_common import STUDY, config
sys.path.insert(0, str(STUDY / 'source'))
from visual_model import Visual, original, pooled
from fusion import standardizer, sensor_fit, sensor_predict, calibrate, calibrated, stacker, fused


def promote_normalization_affine(backbone):
    """Preserve the exact FrozenBatchNorm forward while learning affine values."""
    promoted = []
    for name, module in backbone.named_modules():
        if type(module).__name__ == 'RTDetrFrozenBatchNorm2d':
            for parameter in ('weight', 'bias'):
                value = module._buffers.pop(parameter)
                module.register_parameter(parameter, nn.Parameter(value.detach().clone()))
                promoted.append(name + '.' + parameter)
    assert promoted, 'Expected original RT-DETR frozen normalization modules'
    return promoted


class PhaseVisual(Visual):
    def __init__(self, backbone, width, mean, std, full):
        super().__init__(backbone, width, mean, std, adapted=full)
        self.full = full
        self.promoted_affine = []
        if full:
            self.promoted_affine = promote_normalization_affine(self.backbone)
            self.backbone.requires_grad_(True)
            assert all(p.requires_grad for p in self.backbone.parameters())

    def train(self, mode=True):
        # All executed convolution/affine parameters train. FrozenBatchNorm's
        # exact forward has no train/eval-dependent running-statistic updates.
        return nn.Module.train(self, mode)


def make_model(arm, train_rows, seed, device='cuda'):
    features = np.load(STUDY / 'shared_cache/original_features_16.npy', allow_pickle=False)
    mean, std = standardizer(features[train_rows])
    full = arm == 'C_full_finetuned16'
    backbone = original(device=device) if full else None
    torch.manual_seed(seed)
    if str(device).startswith('cuda'):
        torch.cuda.manual_seed_all(seed)
    return PhaseVisual(backbone, 896, mean, std, full).to(device)


def make_optimizer(model):
    c = config()
    groups = [{'params': list(model.head.parameters()), 'lr': c['head_lr'], 'name': 'classifier'}]
    if model.full:
        groups.append({'params': list(model.backbone.parameters()), 'lr': c['backbone_lr'], 'name': 'full_executed_CNN'})
    return torch.optim.AdamW(groups, weight_decay=c['weight_decay'])


def make_scheduler(optimizer):
    import math
    maximum = config()['max_epochs']
    return torch.optim.lr_scheduler.LambdaLR(optimizer, lambda epoch: .1 + .9 * .5 * (1 + math.cos(math.pi * epoch / maximum)))


def snapshot(model):
    return {name: value.detach().cpu().clone() for name, value in model.state_dict().items()}


def gradient_evidence(model):
    result = {name: {'finite': bool(torch.isfinite(p.grad).all()), 'nonzero': bool(torch.count_nonzero(p.grad)),
                     'elements': p.numel()} for name, p in model.named_parameters() if p.grad is not None}
    expected = [n for n, p in model.named_parameters() if p.requires_grad]
    assert set(result) == set(expected), ('MISSING_GRADIENT', set(expected) - set(result))
    assert all(v['finite'] for v in result.values())
    if model.full:
        for prefix in ['backbone.embedder.', 'backbone.encoder.stages.0.', 'backbone.encoder.stages.1.',
                       'backbone.encoder.stages.2.', 'backbone.encoder.stages.3.', 'head.']:
            assert any(v['nonzero'] for n, v in result.items() if n.startswith(prefix)), ('ZERO_GRADIENT_SCOPE', prefix)
        assert not any(any(t in n for t in ['decoder', 'attention', 'class_embed', 'bbox_embed']) for n in result)
    return result
