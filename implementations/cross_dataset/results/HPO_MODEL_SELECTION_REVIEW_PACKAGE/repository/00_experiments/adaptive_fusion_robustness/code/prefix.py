"""Attributed snapshot of encoder-study prefix, trimmed to inference only.
Original identity recorded at preparation; no upstream module is imported.
"""
import hashlib
import os
import re
import time
import numpy as np
import torch
from torch import nn
from common import RUN, REPO, config, sha, read


def tensor_sha(t):
    return hashlib.sha256(t.detach().cpu().contiguous().numpy().tobytes()).hexdigest()


def pool_maps(maps):
    assert isinstance(maps, (list, tuple)) and maps
    assert all(m.ndim == 4 and m.shape[0] == maps[0].shape[0] for m in maps)
    assert all(bool(torch.isfinite(m).all()) for m in maps), 'NONFINITE_MAP'
    return torch.cat([m.float().mean((-2, -1)) for m in maps], -1)


def pool_segments(vectors, frames=16):
    assert vectors.ndim == 3 and vectors.shape[1] == frames, 'FRAME_GROUPING'
    return vectors.mean(1)


class Prefix(nn.Module):
    def __init__(self, wrapper):
        super().__init__()
        self.wrapper = wrapper
        self.wrapper.requires_grad_(False)
        self.wrapper.eval()
        self.trace = {}
        self.shapes = {}
        self.handles = []
        m = wrapper.model
        # Guard every excluded subtree, the full model, and full detector entry.
        allowed = {'backbone', 'encoder_input_proj', 'encoder'}
        self.forbidden = ['wrapper', 'model']
        self.handles.append(wrapper.register_forward_pre_hook(self._forbid('wrapper')))
        self.handles.append(m.register_forward_pre_hook(self._forbid('model')))
        for name, module in m.named_children():
            if name not in allowed:
                self.forbidden.append('model.'+name)
                for subname, sub in module.named_modules():
                    self.handles.append(sub.register_forward_pre_hook(self._forbid('model.'+name+'.'+subname)))
        for name, module in wrapper.named_children():
            if name != 'model':
                self.forbidden.append(name)
                for subname, sub in module.named_modules():
                    self.handles.append(sub.register_forward_pre_hook(self._forbid(name+'.'+subname)))
        for prefix in sorted(allowed):
            for name, module in getattr(m, prefix).named_modules():
                key = prefix + ('.'+name if name else '')
                self.handles.append(module.register_forward_hook(self._observe(key)))

    def _forbid(self, name):
        def hook(module, inputs):
            raise RuntimeError('FORBIDDEN_DETECTION_EXECUTION ' + name)
        return hook

    def _observe(self, name):
        def hook(module, inputs, output):
            self.trace[name] = self.trace.get(name, 0) + 1
        return hook

    def train(self, mode=True):
        # Recursive parent.train() cannot activate extractor dropout or BN.
        super().train(False)
        self.wrapper.eval()
        return self

    def active_state(self):
        return {name: tensor_sha(t) for name, t in self.wrapper.state_dict().items()
                if name.startswith(('model.backbone.', 'model.encoder_input_proj.', 'model.encoder.'))}

    def active_parameters(self, condition):
        m = self.wrapper.model
        modules = [m.backbone] + ([m.encoder_input_proj, m.encoder] if condition == 'cnn_plus_encoder' else [])
        return sum(p.numel() for mod in modules for p in mod.parameters())

    def forward(self, images, condition):
        assert condition in ('cnn_only', 'cnn_plus_encoder')
        assert images.ndim == 4 and images.shape[1] == 3
        assert all(not m.training for m in self.wrapper.modules())
        assert not any(p.requires_grad for p in self.wrapper.parameters())
        m = self.wrapper.model
        if condition == 'cnn_only':
            maps = m.backbone.model(images).feature_maps
        else:
            mask = torch.ones((len(images), *images.shape[-2:]), device=images.device)
            features = m.backbone(images, mask)
            assert len(features) == len(m.encoder_input_proj)
            projected = [m.encoder_input_proj[i](source) for i, (source, _) in enumerate(features)]
            # Installed RTDetrHybridEncoder returns final PAN maps here. No
            # flattening or decoder-side projection, proposal or query code.
            maps = m.encoder(projected).last_hidden_state
            assert len(maps) == len(features)
        self.shapes[condition] = [list(x.shape) for x in maps]
        return pool_maps(maps)

    def segment(self, images, condition):
        assert len(images) == 16
        return pool_segments(self(images, condition).unsqueeze(0))[0]


def original(device='cpu'):
    from transformers import RTDetrForObjectDetection
    from safetensors import safe_open
    folder = REPO/config()['weights_dir']
    recorded = read(RUN/'provenance/original_pretrained_identity.json')
    for name, info in recorded['weights'].items():
        assert sha(folder/name) == info['sha256'], 'CHECKPOINT_DRIFT'
    wrapper, info = RTDetrForObjectDetection.from_pretrained(folder, local_files_only=True, output_loading_info=True)
    used = ('model.backbone.', 'model.encoder_input_proj.', 'model.encoder.')
    assert not any(str(k).startswith(used) for k in info.get('missing_keys', [])), 'MISSING_USED_WEIGHTS'
    assert not info.get('mismatched_keys') and not info.get('error_msgs'), 'CHECKPOINT_LOAD_ERRORS'
    checked = []
    with safe_open(folder/'model.safetensors', framework='pt', device='cpu') as source:
        keys = set(source.keys())
        # Installed transformers/conversion_mapping.py rt_detr rules. Verify
        # exact values after conversion; never permit missing/random weights.
        converted = {}
        for key in keys:
            target = key.replace('out_proj', 'o_proj')
            target = re.sub(r'layers\.(\d+)\.fc([12])', r'layers.\1.mlp.fc\2', target)
            target = re.sub(r'encoder\.encoder\.(\d+)\.layers', r'encoder.aifi.\1.layers', target)
            assert target not in converted, 'CHECKPOINT_RENAME_COLLISION'
            converted[target] = key
        for name, value in wrapper.state_dict().items():
            if not name.startswith(used):
                continue
            if name.endswith('num_batches_tracked') and name not in converted:
                assert int(value) == 0
                continue  # Non-forward counter only; FrozenBatchNorm removes it.
            assert name in converted, 'UNINITIALIZED_USED_STATE ' + name
            assert torch.equal(value.cpu(), source.get_tensor(converted[name])), 'LOADED_WEIGHT_MISMATCH ' + name
            checked.append({'loaded': name, 'checkpoint': converted[name]})
    p = Prefix(wrapper).to(device).eval()
    p.loading_evidence = {'diagnostics': {k: sorted(v) if isinstance(v, set) else v for k, v in info.items()}, 'checked_checkpoint_tensors': checked,
                          'all_executed_weights_equal_checkpoint': True,
                          'unused_detection_keys': [k for k in keys if not k.startswith(used)],
                          'native_scale_order': list(wrapper.model.backbone.model.out_features),
                          'strides': list(wrapper.config.feat_strides),
                          'processor': read(folder/'preprocessor_config.json')}
    return p

