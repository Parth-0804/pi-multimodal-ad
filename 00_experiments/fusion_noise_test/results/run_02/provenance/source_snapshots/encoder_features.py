"""Original pretrained native prefix only; runtime guards forbid detection work."""
import hashlib
import os
import re
import time
import numpy as np
import torch
from torch import nn
from common import RUN, REPO, config, sha, read, write, signature, budget, event, prior, local


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


def feature_identity(f):
    return {'cohort': sha(RUN/'data/cohort_and_frames.json'), 'weights': sha(RUN/'provenance/original_pretrained_identity.json'),
            'features_source': sha(__file__), 'data_source': sha(__import__('data').__file__),
            'precision': 'float32', 'pooling': 'each scale spatial mean, concatenate native order, mean16 independent images',
            'sample_frame_identity': signature(f[['recording_id','segment_id','frames16','timestamps16']].to_dict('records'))}


def preflight(extractor, pixels, f, job):
    from fitting import Head
    s = f.iloc[job['G'][0]].to_dict()
    x = pixels(s).cuda()
    before = extractor.active_state()
    result = {'sample_keys': [{k: s[k] for k in ('recording_id','segment_id','sample_id')}], 'training_only': True,
              'loading': extractor.loading_evidence, 'results': []}
    prior_array = np.load(prior()/'shared_cache/original_features_16.npy', mmap_mode='r')
    for condition in config()['conditions']:
        extractor.trace.clear()
        with torch.inference_mode():
            a = extractor.segment(x, condition).cpu().numpy().copy()
        trace = dict(extractor.trace)
        assert any(k.startswith('backbone.') for k in trace)
        if condition == 'cnn_plus_encoder':
            assert any(k.startswith('encoder_input_proj.') for k in trace)
            assert any('.self_attn' in k for k in trace), 'ATTENTION_NOT_EXECUTED'
            assert any(k.startswith('encoder.fpn_blocks.') for k in trace) and any(k.startswith('encoder.pan_blocks.') for k in trace)
        else:
            assert not any(k.startswith(('encoder.', 'encoder_input_proj.')) for k in trace)
            np.testing.assert_allclose(a, prior_array[job['G'][0]], rtol=config()['feature_agreement_rtol'], atol=config()['feature_agreement_atol'])
        with torch.inference_mode():
            perm = extractor.segment(x.flip(0), condition).cpu().numpy().copy()
            chunk = torch.cat([extractor(z, condition) for z in x.chunk(2)]).mean(0).cpu().numpy().copy()
            # Independently spell native sequence without full model forwarding.
            m = extractor.wrapper.model
            maps = m.backbone.model(x).feature_maps
            if condition == 'cnn_plus_encoder':
                maps = m.encoder([projection(z) for projection, z in zip(m.encoder_input_proj, maps)]).last_hidden_state
            native = pool_maps(maps).mean(0).cpu().numpy().copy()
        for other in (perm, chunk, native):
            np.testing.assert_allclose(a, other, rtol=config()['feature_agreement_rtol'], atol=config()['feature_agreement_atol'])
        torch.manual_seed(job['seed'])
        head = Head(len(a)).cuda().train()
        head_before = {k: tensor_sha(v) for k,v in head.state_dict().items()}
        # np copy removes inference tensor restrictions for autograd.
        ordinary = torch.from_numpy(a.copy()).cuda().unsqueeze(0)
        opt = torch.optim.AdamW(head.parameters(), lr=.001, weight_decay=.001)
        d = read(RUN/'progress.json')
        assert d['preflight_steps'] < config()['preflight_step_cap']
        d['preflight_steps'] += 1; write(RUN/'progress.json', d)
        loss = nn.functional.binary_cross_entropy_with_logits(head(ordinary), torch.tensor([s['failure']], dtype=torch.float32, device='cuda'))
        loss.backward()
        gradients = {n: {'finite': bool(torch.isfinite(p.grad).all()), 'nonzero': bool(torch.count_nonzero(p.grad))} for n,p in head.named_parameters()}
        assert all(v['finite'] for v in gradients.values()) and any(v['nonzero'] for v in gradients.values())
        opt.step()
        assert head_before != {k: tensor_sha(v) for k,v in head.state_dict().items()}
        assert extractor.active_state() == before
        extractor.train(); assert all(not z.training for z in extractor.modules())
        with torch.inference_mode():
            extractor.segment(x, condition)  # warm-up
            torch.cuda.synchronize(); start = time.perf_counter()
            for _ in range(3): extractor.segment(x, condition)
            torch.cuda.synchronize(); seconds = (time.perf_counter()-start)/3
        result['results'].append({'condition': condition, 'dimension': len(a), 'map_shapes': extractor.shapes[condition],
            'executed_modules': trace, 'guarded_modules': extractor.forbidden, 'head_gradients': gradients,
            'extractor_state_unchanged': True, 'head_updated': True, 'seconds_per_segment_after_warmup': seconds,
            'active_frozen_parameters': extractor.active_parameters(condition), 'trainable_head_parameters': sum(p.numel() for p in head.parameters()),
            'frame_permutation_max_abs': float(np.max(abs(a-perm))), 'chunk_max_abs': float(np.max(abs(a-chunk))),
            'native_prefix_max_abs': float(np.max(abs(a-native))), 'peak_cuda_bytes': torch.cuda.max_memory_allocated()})
    result['passed'] = True
    write(RUN/'checks/real_extractor_preflight.json', result)
    return result


def extract(extractor, pixels, f):
    identity = feature_identity(f)
    binding = RUN/'cache/feature_identity.json'
    if binding.exists(): assert read(binding) == identity, 'FEATURE_CACHE_DRIFT'
    else: write(binding, identity)
    fid = signature(identity)
    before = extractor.active_state()
    complete = RUN/'cache/features_complete.json'
    if complete.exists():
        d = read(complete); assert d['identity'] == identity
        for name, h in d['hashes'].items(): assert sha(RUN/name) == h
        assert read(RUN/'checks/live_cache_agreement.json')['passed'], 'LIVE_CACHE_CHECK_REQUIRED'
        return {c: np.load(RUN/f'cache/{c}.npy', allow_pickle=False) for c in config()['conditions']}
    rows = {c: [] for c in config()['conditions']}; timings = {c: 0. for c in rows}
    start = time.perf_counter()
    reference = np.load(prior()/'shared_cache/original_features_16.npy', mmap_mode='r')
    # Reuse the identified, live-checked CNN cache, no comparison score consulted.
    expected = read(prior()/'shared_cache/frozen_features_complete.json')['hashes']['shared_cache/original_features_16.npy']
    assert sha(prior()/'shared_cache/original_features_16.npy') == expected
    for i, s in enumerate(f.to_dict('records')):
        path = RUN/'cache/segment_vectors'/s['recording_id']/(s['sample_id']+'.npz')
        meta = path.with_suffix('.json')
        budget(16*2**20)
        if path.exists():
            d = read(meta); assert d['identity'] == fid and d['sample_key'] == [s['recording_id'], s['segment_id']] and sha(path) == d['sha256']
            with np.load(path, allow_pickle=False) as z: values = {c: z[c].copy() for c in rows}
        else:
            x = pixels(s).cuda()
            values = {'cnn_only': np.asarray(reference[i]).copy()}
            torch.cuda.synchronize(); t = time.perf_counter()
            with torch.inference_mode(): values['cnn_plus_encoder'] = extractor.segment(x, 'cnn_plus_encoder').cpu().numpy().copy()
            torch.cuda.synchronize(); timings['cnn_plus_encoder'] += time.perf_counter()-t
            local(path); tmp = local(path.with_suffix('.writing.npz'))
            np.savez_compressed(tmp, **values); os.replace(tmp, path)
            write(meta, {'identity': fid, 'sample_key': [s['recording_id'],s['segment_id']], 'sha256': sha(path),
                         'dimensions': {c: len(v) for c,v in values.items()}, 'cnn_only': 'REUSED original frozen16 cache; live training-only verification passed'})
        for c, v in values.items():
            assert np.isfinite(v).all(); rows[c].append(v)
        if (i+1)%25 == 0: event('EXTRACTING', completed_segments=i+1, total_segments=len(f))
    assert before == extractor.active_state(), 'FROZEN_STATE_CHANGED'
    arrays = {c: np.stack(v).astype('float32') for c,v in rows.items()}
    for c, array in arrays.items():
        path = local(RUN/f'cache/{c}.npy'); tmp = local(path.with_suffix('.writing.npy'))
        np.save(tmp, array, allow_pickle=False); os.replace(tmp, path)
    completion_record = {'identity': identity, 'hashes': {f'cache/{c}.npy': sha(RUN/f'cache/{c}.npy') for c in rows},
                     'new_extraction_wall_seconds': time.perf_counter()-start, 'compute_seconds_this_invocation': timings,
                     'dimensions': {c: a.shape[1] for c,a in arrays.items()}, 'storage_bytes': {c: a.nbytes for c,a in arrays.items()},
                     'cnn_only_status': 'REUSED', 'cnn_plus_encoder_status': 'NEW', 'state_unchanged': True}
    # Actual cache replay on training-only identities, ordinary arrays.
    j = next(j for j in read(RUN/'data/fit_partitions.json') if j['outer_fold_original']==0 and j['role']=='outer_assessment')
    replay = []
    for i in j['G'][:2]:
        x = pixels(f.iloc[i].to_dict()).cuda()
        for c in rows:
            with torch.inference_mode(): live = extractor.segment(x,c).cpu().numpy().copy()
            np.testing.assert_allclose(live, arrays[c][i], rtol=config()['feature_agreement_rtol'], atol=config()['feature_agreement_atol'])
            replay.append({'sample_id': f.iloc[i].sample_id, 'condition':c, 'max_abs':float(np.max(abs(live-arrays[c][i])))})
    write(RUN/'checks/live_cache_agreement.json', {'passed':True, 'training_only':True, 'rows':replay, 'identity':identity})
    write(complete, completion_record)
    return arrays
