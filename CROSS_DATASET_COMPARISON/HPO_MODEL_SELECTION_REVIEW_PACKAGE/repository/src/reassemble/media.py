"""Bounded media inspection using existing OpenCV and libsndfile decoders."""
import io
import os
import shutil
import uuid
from pathlib import Path
import cv2
import numpy as np
import soundfile as sf
cv2.setNumThreads(1)
from .alignment import interval_indices, interval_coverage, timestamps_1d


def blob_bytes(dataset):
    value = dataset[()]
    if isinstance(value, (bytes, np.void)):
        return bytes(value)
    array = np.asarray(value)
    if array.ndim == 1 and np.issubdtype(array.dtype, np.integer):
        if array.size and (array.min() < 0 or array.max() > 255):
            raise ValueError('Encoded byte values outside 0..255')
        return array.astype(np.uint8, copy=False).tobytes()
    raise ValueError(f'Unsupported encoded media dtype: {array.dtype}')


def inspect_video(dataset, timestamps, segments, cache_path, samples=16):
    cache_path = Path(cache_path)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    # Encoded cache is outside Git, separately identifiable; original HDF5 stays read-only.
    expected_bytes = dataset.size * dataset.dtype.itemsize
    if cache_path.exists() and cache_path.stat().st_size != expected_bytes:
        raise ValueError('Encoded cache size mismatch; preserve and inspect')
    if not cache_path.exists():
        if shutil.disk_usage(cache_path.parent).free < expected_bytes * 1.05 + 10 * 2**30:
            raise RuntimeError('Insufficient media-cache space with 10 GiB reserve')
        part = cache_path.with_name(cache_path.name + '.' + uuid.uuid4().hex + '.part')
        with part.open('xb') as f:
            f.write(blob_bytes(dataset))
        os.replace(part, cache_path)
    cap = cv2.VideoCapture(str(cache_path))
    count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    meta = {'decoded_container_open': cap.isOpened(), 'container_frames': count, 'timestamp_count': len(timestamps), 'frame_count_matches': count == len(timestamps), 'fps': cap.get(cv2.CAP_PROP_FPS), 'width': cap.get(cv2.CAP_PROP_FRAME_WIDTH), 'height': cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}
    output = {}
    for seg in segments:
        start, end = seg['start'], seg['end']
        idx = interval_indices(timestamps, start, end)
        chosen = np.unique(idx[np.linspace(0, len(idx)-1, min(samples, len(idx))).round().astype(int)]) if len(idx) else []
        brightness, focus, motion = [], [], []
        previous = None
        decoded = 0
        for i in chosen:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(i))
            ok, frame = cap.read()
            if not ok:
                continue
            decoded += 1
            gray = cv2.cvtColor(cv2.resize(frame, (160, 120)), cv2.COLOR_BGR2GRAY).astype(float) / 255
            brightness.append(float(gray.mean()))
            focus.append(float(cv2.Laplacian(gray, cv2.CV_64F).var()))
            if previous is not None:
                motion.append(float(np.abs(gray - previous).mean()))
            previous = gray
        quality = {**interval_coverage(timestamps, start, end), 'sampled_frames': len(chosen), 'decoded_frames': decoded, 'valid_frame_ratio': decoded/len(chosen) if len(chosen) else 0.0, 'decode_failure_ratio': 1-decoded/len(chosen) if len(chosen) else None, 'mean_brightness': float(np.mean(brightness)) if brightness else None, 'brightness_std': float(np.std(brightness)) if brightness else None, 'focus_proxy': float(np.mean(focus)) if focus else None, 'motion_proxy': float(np.mean(motion)) if motion else None}
        quality['usable'] = meta['frame_count_matches'] and quality['coverage'] >= .9 and decoded == samples
        output[seg['segment_id']] = quality
    cap.release()
    return meta, output


def decoded_frame_count(stream):
    count = 0
    while True:
        block = stream.read(262144, dtype='float32', always_2d=True)
        if not len(block):
            break
        count += len(block)
    stream.seek(0)
    return count


def inspect_audio(dataset, segments, timestamps=None, time_origin=0.0):
    output = {}
    with sf.SoundFile(io.BytesIO(blob_bytes(dataset))) as f:
        reported_frames = len(f)
        actual_frames = decoded_frame_count(f)
        duration = actual_frames / f.samplerate
        explicit = timestamps_1d(timestamps) if timestamps is not None else None
        aligned = explicit is not None and len(explicit) == actual_frames
        meta = {'sample_rate': f.samplerate, 'channels': f.channels, 'frames': actual_frames, 'reported_frames': reported_frames, 'duration': duration, 'decoder': 'libsndfile', 'clock_convention': 'official visualization uses zero-based decoded sample clock', 'alignment_verified': aligned, 'explicit_timestamp_count': len(explicit) if explicit is not None else 0, 'nominal_time_origin': time_origin}
        for seg in segments:
            start, end = seg['start'], seg['end']
            # Nominal coverage is explicitly distinct from verified cross-modal coverage.
            relative_start, relative_end = start-time_origin, end-time_origin
            lo = max(0, int(np.ceil(relative_start * f.samplerate)))
            hi = min(actual_frames, int(np.floor(relative_end * f.samplerate)) + 1)
            coverage = max(0, min(relative_end, duration)-max(relative_start, 0))/(end-start)
            if aligned:
                indices = interval_indices(explicit, start, end)
                lo = int(indices[0]) if len(indices) else 0
                hi = int(indices[-1])+1 if len(indices) else 0
                coverage = interval_coverage(explicit, start, end)['coverage']
            if hi <= lo:
                output[seg['segment_id']] = {'nominal_coverage': coverage, 'usable': False, 'aligned': False}
                continue
            f.seek(lo)
            samples = f.read(hi-lo, dtype='float32', always_2d=True)
            coverage = min(coverage, len(samples) / f.samplerate / (end-start))
            finite = np.isfinite(samples)
            good = samples[finite]
            output[seg['segment_id']] = {'nominal_coverage': coverage, 'valid_duration_ratio': coverage * float(finite.mean()), 'sample_count': len(samples), 'rms': float(np.sqrt(np.mean(good**2))) if len(good) else None, 'clipping_fraction': float((np.abs(good)>=.999).mean()) if len(good) else None, 'silence_fraction': float((np.abs(good)<1e-4).mean()) if len(good) else None, 'noise_snr_proxy': None, 'decodable': True, 'aligned': aligned, 'usable': bool(aligned and coverage >= .9 and finite.mean() >= .99)}
    return meta, output
