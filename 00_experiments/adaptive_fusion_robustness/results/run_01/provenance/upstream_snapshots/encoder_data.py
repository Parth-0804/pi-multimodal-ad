"""Read-only predecessor manifests and videos; no imported mutable prior loader."""
from pathlib import Path
import hashlib
import importlib.metadata
import os
import shutil
import numpy as np
import pandas as pd
from common import STUDY, RUN, REPO, config, prior, sha, read, write, write_text, signature, event, local, budget, code_identity, command

KEYS = ['recording_id', 'segment_id']
META = ['sample_id', *KEYS, 'failure', 'action', 'start', 'end']


def frame():
    return pd.DataFrame(read(RUN / 'data/cohort_and_frames.json'))


def validate_job(f, job):
    n = len(f)
    groups = {}
    for role in ('G', 'C', 'predict', 'T'):
        ids = job[role]
        assert ids and len(ids) == len(set(ids)) and all(type(i) is int and 0 <= i < n for i in ids), role
        groups[role] = set(f.iloc[ids].recording_id)
        # Every included recording must be complete within this locked cohort.
        assert set(np.flatnonzero(f.recording_id.isin(groups[role]))) == set(ids), 'SPLIT_RECORDING'
    G, C, V, T = [groups[k] for k in ('G', 'C', 'predict', 'T')]
    E = set(job['outer_E_recordings'])
    assert not G & C and not (G | C) & V, 'ROLE_LEAKAGE'
    assert G | C == set(job['A_recordings'])
    assert G == set(job['G_recordings']) and C == set(job['C_recordings'])
    assert V == set(job['prediction_recordings']) and not T & E
    assert T | E == set(f.recording_id)
    if job['role'] == 'outer_assessment':
        assert G | C == T and V == E
    else:
        assert G | C | V == T and not (G | C | V) & E
    for role in ('G', 'C'):
        assert set(f.iloc[job[role]].failure) == {0, 1}, 'CLASS_SUPPORT ' + role
    return {role: f.iloc[job[role]][META].to_dict('records') for role in ('G', 'C', 'predict', 'T')} | {'E_recordings': sorted(E), 'job': job}


def validate_all(f, jobs):
    assert len(f) and not f.duplicated(KEYS).any() and not f.sample_id.duplicated().any(), 'DUPLICATE_KEY'
    assert set(f.failure) == {0, 1}
    for s in f.to_dict('records'):
        assert len(s['frames16']) == len(set(s['frames16'])) == 16
        assert len(s['frames32']) == len(set(s['frames32'])) == 32
        assert [s['frames32'][i] for i in s['positions16_in32']] == s['frames16']
        assert len(s['timestamps16']) == 16 and all(s['start'] <= t <= s['end'] for t in s['timestamps16'])
        assert s['timestamps16'] == sorted(s['timestamps16'])
    assert len(jobs) == 25
    all_e = []
    counts = []
    for k in range(5):
        js = [j for j in jobs if j['outer_fold_original'] == k]
        assert len(js) == 5
        outer = next(j for j in js if j['role'] == 'outer_assessment')
        inner = [j for j in js if j['role'] != 'outer_assessment']
        assert {j['role'] for j in inner} == {f'inner_fold_{i:02d}' for i in range(1, 5)}
        v = []
        for j in js:
            validate_job(f, j)
            assert j['T'] == outer['T'] and j['outer_E_recordings'] == outer['outer_E_recordings']
            if j['role'] != 'outer_assessment':
                v += j['predict']
        assert len(v) == len(set(v)) and set(v) == set(outer['T']), 'INNER_COVERAGE'
        all_e += outer['predict']
        for role in ('G', 'C', 'predict', 'T'):
            q = f.iloc[outer[role]]
            counts.append(dict(fold=outer['fold_name'], role=role, samples=len(q), failures=int(q.failure.sum()), recordings=int(q.recording_id.nunique())))
    assert len(all_e) == len(set(all_e)) == len(f) and set(all_e) == set(range(len(f)))
    return counts


def check_input_stats(f):
    for s in f.drop_duplicates('source_path').to_dict('records'):
        p = REPO / s['source_path']; st = p.stat()
        assert (st.st_size, st.st_mtime_ns) == (s['source_bytes'], s['source_mtime_ns']), 'RAW_STAT_DRIFT'
    for s in f.drop_duplicates('video_path').to_dict('records'):
        p = REPO / s['video_path']; st = p.stat()
        assert (st.st_size, st.st_mtime_ns) == (s['video_bytes'], s['video_mtime_ns']), 'VIDEO_STAT_DRIFT'


def prepare():
    budget(128*2**20)
    src = prior()
    lock = read(src / 'data_manifests/cohort_lock.json')
    assert sha(src / 'data_manifests/cohort_and_frames.json') == lock['cohort_sha256']
    assert sha(src / 'data_manifests/fit_partitions.json') == lock['partitions_sha256']
    files = ['data_manifests/cohort_and_frames.json', 'data_manifests/fit_partitions.json',
             'data_manifests/cohort_lock.json', 'data_manifests/input_manifest.json', 'data_manifests/exclusions.csv',
             'config/resolved_config.json', 'provenance/original_pretrained_identity.json',
             'shared_cache/sensor_statistics.npy', 'shared_cache/frozen_features_complete.json',
             'shared_cache/original_feature_extraction_identity.json', 'shared_cache/original_features_16.npy']
    sources = ['source/'+p.name for p in (src/'source').glob('*.py')]
    identities = {p: sha(src / p) for p in files + sources}
    identity_file = RUN / 'provenance/input_identity.json'
    if identity_file.exists():
        old = read(identity_file)
        # Prior scientific source may still change; saved manifests/statistics may not.
        for p in files:
            assert old['prior_files'][p] == identities[p], 'PRIOR_INPUT_DRIFT ' + p
        assert old['config'] == sha(STUDY/'config.json'), 'CONFIG_DRIFT'
        for name in ['cohort_and_frames.json', 'fit_partitions.json', 'cohort_lock.json', 'input_manifest.json', 'exclusions.csv']:
            assert sha(RUN/'data'/name) == old['prior_files']['data_manifests/'+name], 'LOCAL_MANIFEST_DRIFT'
        assert sha(RUN/'cache/sensor_statistics.npy') == old['prior_files']['shared_cache/sensor_statistics.npy'], 'LOCAL_SENSOR_DRIFT'
        for name, version in old['versions'].items():
            assert importlib.metadata.version(name) == version, 'SOFTWARE_DRIFT '+name
        return
    for p in files[:5]:
        shutil.copyfile(src / p, local(RUN / 'data' / Path(p).name))
    for p in sources:
        shutil.copyfile(src / p, local(RUN / 'provenance/prior_source' / Path(p).name))
    shutil.copyfile(src / 'config/resolved_config.json', local(RUN/'provenance/prior_config.json'))
    shutil.copyfile(src / 'provenance/original_pretrained_identity.json', local(RUN/'provenance/original_pretrained_identity.json'))
    shutil.copyfile(src/'shared_cache/sensor_statistics.npy', local(RUN/'cache/sensor_statistics.npy'))
    f = frame(); jobs = read(RUN/'data/fit_partitions.json')
    counts = validate_all(f, jobs); check_input_stats(f)
    assert (len(f), int(f.failure.sum()), f.recording_id.nunique()) == (lock['samples'], lock['failures'], lock['recordings'])
    stats = np.load(RUN/'cache/sensor_statistics.npy', allow_pickle=False)
    assert len(stats) == len(f) and np.isfinite(stats).all()
    # Verify the keyed preparation record and row order, not label/fold similarity.
    keyed_stats = {}
    for rid in f.recording_id.unique():
        directory = src/'shared_cache/preparation'/rid
        prepared = read(directory/'complete_v2.json')
        values = np.load(directory/'statistics.npy', allow_pickle=False)
        assert len(values) == len(prepared['samples'])
        for sample, value in zip(prepared['samples'], values):
            key = (sample['recording_id'], sample['segment_id'])
            assert key not in keyed_stats
            keyed_stats[key] = (sample, value)
    for i, s in enumerate(f.to_dict('records')):
        original, values = keyed_stats[(s['recording_id'], s['segment_id'])]
        assert original['sample_id'] == s['sample_id'] and original['frames16'] == s['frames16']
        assert np.array_equal(stats[i], values, equal_nan=True), 'SENSOR_ROW_IDENTITY'
    write(RUN/'checks/cohort_partitions.json', {'passed': True, 'samples': len(f), 'failures': int(f.failure.sum()), 'recordings': int(f.recording_id.nunique()), 'counts': counts, 'sensor_keyed_row_check': True})
    for j in jobs:
        write(RUN/'data/memberships'/j['fold_name']/(j['role']+'.json'), validate_job(f, j))
    c = config(); previous = read(RUN/'provenance/prior_config.json')
    matches = {k: previous.get(k) == c[k] for k in ['epochs','effective_batch_segments','microbatch_segments','precision','head_lr','weight_decay','gradient_clip','seed','sensor_C','sensor_class_weight','max_iter','fusion_C','threshold','normalizer_std_floor']}
    assert all(matches.values()), 'PREDECESSOR_PROTOCOL_MISMATCH'
    write(RUN/'provenance/protocol_compatibility.json', {'settings': matches, 'policy': 'Reuse only complete exact-role reference artifacts whose source/config/feature identity can be verified; otherwise NEW matched fits. No selection by scores.', 'sensor_statistics': 'Keyed preparation and saved order verified exactly.'})
    weights = read(RUN/'provenance/original_pretrained_identity.json')
    for name, info in weights['weights'].items():
        assert sha(REPO/c['weights_dir']/name) == info['sha256'], 'WEIGHT_DRIFT'
    write(RUN/'resolved_config.json', c)
    versions = {n: importlib.metadata.version(n) for n in ['torch','transformers','numpy','pandas','scikit-learn','scipy','opencv-python','safetensors','matplotlib']}
    write(RUN/'provenance/input_identity.json', {'prior_files': identities, 'config': sha(STUDY/'config.json'), 'checkpoint': weights, 'versions': versions, 'git': command(['git','rev-parse','HEAD']), 'prepared_utc': __import__('common').utc()})
    # A second fingerprint ensures this snapshot was not copied across a write.
    for p in files:
        assert sha(src/p) == identities[p], 'MANIFEST_CHANGED_DURING_COPY'
    write_text(RUN/'experiment_plan.md', '''# Fixed encoder comparison\n\nFailure=1; success=0. Common >=32-frame-eligible cohort, exact saved 16 frames, five outer/four inner recording splits and saved G/C memberships. No score-based choices.\n\nOriginal local checkpoint -> independent images -> native multiscale maps -> per-scale spatial means -> concatenation -> 16-frame arithmetic mean. CNN reference omits projections/encoder; encoder branch includes pretrained encoder projections/AIFI/FPN/PAN and ends before decoder projections. All pretrained state frozen/eval. Float32 both branches.\n\nEach raw head uses G-only standardization, 128 hidden units, ReLU/dropout .1, 5 epochs, AdamW lr/decay .001, clipping 1, effective batch 8 with per-segment accumulation and actual partial-batch denominator. NumPy role-seed+epoch ordering independent of head dimension. G-only positive weighting. Sigmoid calibrators fitted on C. Shared balanced C=1 sensor logistic model and C-only calibration. F2 C=1 unweighted logistic uses held-inner calibrated probabilities, no scaling/fused calibrator. E excluded from all fitting.\n\nFold order 01..05; both conditions completed before advancing. Maximum 50 planned visual/25 sensor/10 stacker fits, caps 55/30/12 including retries. Shared original features/statistics may be cached across folds; no fitted normalizer is shared across roles.\n\nPrimary: pooled paired AP(F2 encoder)-AP(F2 CNN). Per-fold and pooled AP, AUROC, precision/recall at .5, balanced accuracy, macro F1, Brier. Reliability: 10 equal-width probability bins, mean predicted versus empirical failure fraction. 2000 paired recording-cluster bootstrap replicates, seed314159, percentile95% intervals, degenerate replicates skipped and counted. Secondary exploratory visual AP and each F2-minus-shared-sensor AP. No new trial based on outcomes.\n\nCPU preparation capped at two threads; one allocated T4 only after priority process/device release and stable manifests. 24h including waiting, 30GiB new storage, 10GiB free reserve, 32GiB monitored RSS. Budget checks before stages/writes and during fitting; elapsed reporting reserve15min. GPU runtime traces and saved-model replay are prerequisites, not inferred from source.\n\nNo assessment scores examined in preparation. Resource estimate: compact features are N*(observed CNN D+observed encoder D)*4 bytes, head files at most55*(128*D+257)*4 plus optimizer checkpoints; no pixel cache retained. Exact dimensions and training-only benchmark determine remaining execution feasibility before full extraction. Review ZIP excludes model blobs and feature arrays.\n''')
    event('PREPARED', cohort_samples=len(f), failures=int(f.failure.sum()), recordings=int(f.recording_id.nunique()), planned_visual_fits=50, planned_sensor_fits=25, planned_stackers=10)


class Pixels:
    """Decode prior 32 support frames solely to validate its saved pixel hash.

    Only the exact 16 selected images enter either extractor. Never touch the
    predecessor's mutable RAM/disk pixel cache and never write decoded images.
    """
    def __init__(self):
        import cv2
        from transformers import RTDetrImageProcessor
        cv2.setNumThreads(1)
        self.processor = RTDetrImageProcessor.from_pretrained(REPO/config()['weights_dir'], local_files_only=True)
        self.captures = {}

    def __call__(self, sample):
        import cv2
        import torch
        path = REPO/sample['video_path']
        st = path.stat()
        assert (st.st_size, st.st_mtime_ns) == (sample['video_bytes'], sample['video_mtime_ns'])
        key = str(path)
        if key not in self.captures:
            self.close()
            cap = cv2.VideoCapture(key)
            assert cap.isOpened(), 'VIDEO_OPEN'
            self.captures[key] = cap
        cap = self.captures[key]; images = []
        for index in sample['frames32']:
            current = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            if index < current or index-current > 64:
                cap.set(cv2.CAP_PROP_POS_FRAMES, index)
            else:
                for _ in range(index-current):
                    cap.grab()
            ok, img = cap.read()
            assert ok, ('LOCKED_FRAME_DECODE_FAILURE', sample['sample_id'], index)
            images.append(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        pixels = self.processor(images=images, return_tensors='np')['pixel_values']
        u = np.rint(pixels/config()['rescale_factor']).astype('uint8')
        assert np.array_equal(u.astype('float32')*np.float32(config()['rescale_factor']), pixels)
        assert hashlib.sha256(u.tobytes()).hexdigest() == sample['pixel_content_sha256'], 'PIXEL_IDENTITY_DRIFT'
        return torch.from_numpy(pixels[sample['positions16_in32']].copy())

    def close(self):
        for cap in self.captures.values():
            cap.release()
        self.captures.clear()
