"""Full-cohort read-only target and exact selected-frame identity verification.

Decodes only the locked required 32 support frames and the selected 16; never
reads all video frames into memory, writes decoded pixels, or accesses raw payloads
beyond segment labels and hand-camera timestamps. No GPU initialization/training.
"""
from concurrent.futures import ProcessPoolExecutor
from collections import defaultdict
import hashlib
import multiprocessing as mp
from pathlib import Path
import sys
import time

import h5py
import numpy as np
import torch

from phase_common import AUDIT, STUDY, REPO, EVIDENCE, EXEC, sha, read, write, utc
from reassemble.alignment import action_from_text, timestamps_1d

DECODER = None


def initialize():
    global DECODER
    torch.set_num_threads(1)
    sys.path.insert(0, str(AUDIT / 'source'))
    from isolated_decode import IsolatedDecoder
    c = read(STUDY / 'config/resolved_config.json')
    DECODER = IsolatedDecoder(REPO, c['weights_dir'], c['rescale_factor'], decoder_threads=2)


def check_recording(rows):
    source = REPO / rows[0]['source_path']
    video = REPO / rows[0]['video_path']
    assert source.stat().st_size == rows[0]['source_bytes']
    assert source.stat().st_mtime_ns == rows[0]['source_mtime_ns']
    assert video.stat().st_size == rows[0]['video_bytes']
    assert video.stat().st_mtime_ns == rows[0]['video_mtime_ns']
    result = []
    with h5py.File(source, 'r') as raw:
        timestamps = timestamps_1d(raw['timestamps/hand'][()])
        for row in rows:
            assert source.stem == row['recording_id']
            group = raw['segments_info'][str(row['segment_id'])]
            text = np.asarray(group['text'][()]).item()
            text = text.decode('utf-8') if isinstance(text, bytes) else str(text)
            assert action_from_text(text) == row['action'], ('ACTION_IDENTITY_DRIFT', row['sample_id'])
            success = np.asarray(group['success'][()]).item()
            assert success in (0, 1, False, True)
            assert int(not bool(success)) == row['failure']
            assert float(np.asarray(group['start'][()]).item()) == row['start']
            assert float(np.asarray(group['end'][()]).item()) == row['end']
            interval = np.flatnonzero((timestamps >= row['start']) & (timestamps <= row['end']))
            expected = interval[np.linspace(0, len(interval) - 1, 16).round().astype(int)]
            assert expected.tolist() == row['frames16'], ('FRAME_SELECTION_DRIFT', row['sample_id'])
            assert len(set(row['frames16'])) == 16
            assert [row['frames32'][i] for i in row['positions16_in32']] == row['frames16']
    return {'recording_id': rows[0]['recording_id'], 'actions': len(rows), 'labels_and_uniform_whole_action_frames': True,
            'raw_action_text_and_source_recording_associations': True,
            'source_path': rows[0]['source_path'], 'source_recorded_sha256': rows[0]['source_recorded_sha256'],
            'source_bytes': source.stat().st_size, 'source_mtime_ns': source.stat().st_mtime_ns,
            'video_path': rows[0]['video_path'], 'video_bytes': video.stat().st_size, 'video_mtime_ns': video.stat().st_mtime_ns}


def verify_pixel(row):
    start = time.monotonic()
    original = DECODER(row)
    assert original.dtype == np.uint8 and original.shape == (32, 3, 640, 640)
    assert hashlib.sha256(original.tobytes()).hexdigest() == row['pixel_content_sha256'], ('ORIGINAL_PIXEL_DRIFT', row['sample_id'])
    expected = original[row['positions16_in32']]
    expected_sha = hashlib.sha256(expected.tobytes()).hexdigest()
    selected = DECODER(dict(row, frames32=row['frames16']))
    assert selected.dtype == np.uint8 and selected.shape == (16, 3, 640, 640)
    assert np.array_equal(selected, expected), ('SELECTED16_PIXEL_DRIFT', row['sample_id'])
    return {'sample_id': row['sample_id'], 'recording_id': row['recording_id'], 'segment_id': row['segment_id'],
            'failure': row['failure'], 'action': row['action'], 'selected16_sha256': expected_sha,
            'original32_sha256': row['pixel_content_sha256'], 'seconds': time.monotonic() - start,
            'shape': [16, 3, 640, 640], 'decoded_dtype': 'uint8', 'model_dtype': 'float32', 'scale': 1 / 255}


def main():
    EXEC.mkdir(parents=True, exist_ok=True)
    identity = EXEC / '26102026_input_identity'
    identity.mkdir(exist_ok=True)
    rows = read(STUDY / 'data_manifests/cohort_and_frames.json')
    assert len(rows) == 4530 and sum(r['failure'] for r in rows) == 509
    assert len({r['sample_id'] for r in rows}) == len(rows)
    grouped = defaultdict(list)
    for row in rows:
        grouped[row['recording_id']].append(row)
    assert len(grouped) == 148
    metadata = [check_recording(r) for r in grouped.values()]
    write(EVIDENCE / 'PHASE1_LABEL_FRAME_ALIGNMENT.json', metadata)
    if '--metadata-only' in sys.argv:
        print(utc(), 'FULL_COHORT_METADATA_RECHECK_COMPLETE', len(rows), 'actions', len(metadata), 'recordings', flush=True)
        return
    extraction = read(STUDY / 'shared_cache/frozen_features_complete.json')
    assert sha(STUDY / 'shared_cache/original_features_16.npy') == extraction['hashes']['shared_cache/original_features_16.npy']
    assert np.load(STUDY / 'shared_cache/original_features_16.npy', allow_pickle=False).shape == (4530, 896)
    completed = {}
    for p in identity.glob('*.json'):
        value = read(p)
        if 'sample_id' in value:
            completed[value['sample_id']] = value
    remaining = [r for r in rows if r['sample_id'] not in completed]
    write(EVIDENCE / 'PHASE1_INPUT_VERIFICATION_STATUS.json', {'status': 'RUNNING', 'utc': utc(), 'completed': len(completed), 'total': len(rows)})
    if remaining:
        with ProcessPoolExecutor(max_workers=4, mp_context=mp.get_context('spawn'), initializer=initialize) as pool:
            for value in pool.map(verify_pixel, remaining, chunksize=1):
                write(identity / (value['sample_id'] + '.json'), value)
                completed[value['sample_id']] = value
                if len(completed) % 50 == 0:
                    write(EVIDENCE / 'PHASE1_INPUT_VERIFICATION_STATUS.json', {'status': 'RUNNING', 'utc': utc(), 'completed': len(completed), 'total': len(rows)})
                    print(utc(), 'verified', len(completed), '/', len(rows), flush=True)
    manifest = [dict(row, selected16_sha256=completed[row['sample_id']]['selected16_sha256']) for row in rows]
    write(EVIDENCE / 'PHASE1_INPUT_IDENTITY_MANIFEST.json', manifest)
    write(EVIDENCE / 'PHASE1_INPUT_VERIFICATION_STATUS.json', {'status': 'COMPLETE', 'utc': utc(), 'completed': len(completed),
        'total': len(rows), 'recordings': len(grouped), 'failure_positive': 509,
        'manifest_sha256': sha(EVIDENCE / 'PHASE1_INPUT_IDENTITY_MANIFEST.json'),
        'original_cohort_sha256': sha(STUDY / 'data_manifests/cohort_and_frames.json'),
        'original_features16_sha256': sha(STUDY / 'shared_cache/original_features_16.npy'),
        'selected16_equals_verified_original32_subset': True, 'raw_payloads_rewritten': False})
    print(utc(), 'FULL_COHORT_IDENTITY_COMPLETE', flush=True)


if __name__ == '__main__':
    main()
