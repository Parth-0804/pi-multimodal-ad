"""CPU-only complete decode QC and deterministic 16-position RGB selection."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from collections import Counter
import hashlib
import re
import subprocess
import time
import numpy as np
import cv2
cv2.setNumThreads(1)

from .common import PROJECT, REPO, config, core, event, read, resolve, sha, utc, video_path, write


def ffmpeg():
    path = REPO / 'MILLING DATASET/.tools/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2'
    if not path.is_file():
        raise FileNotFoundError('Verified existing FFmpeg binary missing; no decoder substitution')
    return path


def positions(n, count=16):
    if n < count:
        raise ValueError('Insufficient distinct temporal positions')
    result = np.linspace(0, n - 1, count).round().astype(int)
    assert len(set(result)) == count and np.all(np.diff(result) > 0)
    return result


def rgb_frames(path, indices, width=640, height=480):
    select = '+'.join(f'eq(n\\,{int(index)})' for index in indices)
    command = [str(ffmpeg()), '-nostdin', '-hide_banner', '-loglevel', 'error', '-hwaccel', 'none',
               '-threads', '1', '-i', str(path), '-vf', 'select=' + select, '-filter_threads', '1',
               '-fps_mode', 'passthrough', '-pix_fmt', 'rgb24', '-f', 'rawvideo', 'pipe:1']
    result = subprocess.run(command, capture_output=True)
    if result.returncode or len(result.stdout) != len(indices) * width * height * 3:
        raise RuntimeError('RGB_SELECTION_DECODE_FAILURE:' + result.stderr.decode(errors='replace')[:300])
    return np.frombuffer(result.stdout, dtype=np.uint8).reshape(len(indices), height, width, 3).copy()


def inspect_video(path, *, expected_frames, expected_sha256, expected_size=None, width=640, height=480):
    started = time.monotonic()
    path = Path(path)
    if not path.is_file():
        return {'technical_valid': False, 'technical_category': 'C', 'reason': 'MISSING_CAMERA_FILE'}
    if expected_size is not None and path.stat().st_size != expected_size:
        return {'technical_valid': False, 'technical_category': 'D', 'reason': 'SOURCE_SIZE_MISMATCH'}
    actual_hash = sha(path)
    if actual_hash != expected_sha256:
        return {'technical_valid': False, 'technical_category': 'D', 'reason': 'SOURCE_HASH_MISMATCH'}
    command = [str(ffmpeg()), '-nostdin', '-hide_banner', '-loglevel', 'info', '-hwaccel', 'none',
               '-threads', '1', '-i', str(path), '-vf', 'scale=160:120:flags=area,format=gray,showinfo',
               '-filter_threads', '1', '-fps_mode', 'passthrough', '-pix_fmt', 'gray', '-f', 'rawvideo', 'pipe:1']
    decoded = subprocess.run(command, capture_output=True)
    stderr = decoded.stderr.decode(errors='replace')
    pts = [float(value) for value in re.findall(r'\bn:\s*\d+\s+pts:\s*[-\d]+\s+pts_time:([-+\d.eE]+)', stderr)]
    source_shape = re.search(r'Video:.*?\b(\d{2,5})x(\d{2,5})\b', stderr)
    shape = [int(source_shape[1]), int(source_shape[2])] if source_shape else None
    frame_bytes = 160 * 120
    count = len(decoded.stdout) // frame_bytes
    errors = []
    decode_warnings = [line[-500:] for line in stderr.splitlines() if re.search(r'corrupt|invalid data|error while|conceal', line, re.I)]
    if decoded.returncode: errors.append('FULL_DECODE_FAILED')
    if len(decoded.stdout) % frame_bytes or count != expected_frames: errors.append('DECODED_FRAME_COUNT_MISMATCH')
    if shape != [width, height]: errors.append('SOURCE_DIMENSION_MISMATCH')
    if len(pts) != count or not pts or not np.all(np.diff(pts) > 0): errors.append('INVALID_FRAME_PTS')
    max_timing = float(np.max(np.abs(np.asarray(pts) - np.arange(len(pts)) / 25))) if pts else None
    if max_timing is None or max_timing > 5e-5: errors.append('CONVERTED_CLOCK_MISMATCH')
    if decode_warnings: errors.append('BITSTREAM_CORRUPTION_REQUIRES_REVIEW')
    quality = {}
    if count and not len(decoded.stdout) % frame_bytes:
        frames = np.frombuffer(decoded.stdout, dtype=np.uint8).reshape(count, 120, 160)
        brightness = frames.mean((1, 2))
        contrast = frames.std((1, 2))
        black = (brightness < 3) & (contrast < 2)
        adjacent = np.mean(np.abs(np.diff(frames.astype(np.float32), axis=0)), axis=(1, 2))
        blur = np.asarray([cv2.Laplacian(frame, cv2.CV_32F).var() for frame in frames])
        quality = {'mean_brightness_0_255': float(brightness.mean()), 'mean_contrast': float(contrast.mean()),
                   'black_fraction': float(black.mean()), 'median_laplacian_variance_160x120': float(np.median(blur)),
                   'adjacent_identical_fraction': float((adjacent < 1e-6).mean()) if len(adjacent) else 1.,
                   'mean_adjacent_pixel_delta': float(adjacent.mean()) if len(adjacent) else 0.,
                   'low_detail_flag': bool(np.median(blur) < 5),
                   'occlusion_or_target_visibility': 'UNRESOLVED_REQUIRES_SEMANTIC_REVIEW',
                   'incidental_human_presence': 'UNRESOLVED_REQUIRES_SEMANTIC_REVIEW'}
        if black.mean() > .99: errors.append('EMPTY_OR_BLACK_RECORDING')
    chosen = positions(expected_frames).tolist()
    selected_hashes = []
    if not errors:
        images = rgb_frames(path, chosen, width, height)
        selected_hashes = [hashlib.sha256(image.tobytes()).hexdigest() for image in images]
    weak = quality.get('low_detail_flag', False) or quality.get('adjacent_identical_fraction', 0) > .95
    return {'source_sha256': actual_hash, 'source_bytes': path.stat().st_size, 'mtime_ns': path.stat().st_mtime_ns,
            'technical_valid': not errors, 'technical_category': 'D' if errors else 'A',
            'visual_quality_category': 'B' if weak else 'E',
            'quality_interpretation': 'B means automated weak-input flag, not proven absent object; E requires semantic review. Neither alone excludes an otherwise valid stream.',
            'reason': '|'.join(errors), 'decoded_frames': count, 'frame_PTS_seconds': pts,
            'source_width_height': shape, 'last_frame_time_seconds': pts[-1] if pts else None,
            'support_duration_seconds': pts[-1] + .04 if pts else None,
            'timestamp_vs_converted_index_max_error_seconds': max_timing,
            'selected_frame_indices': chosen, 'selected_RGB_sha256': selected_hashes,
            'distinct_selected_RGB_images': len(set(selected_hashes)), 'quality': quality,
            'decode_warnings': decode_warnings,
            'wall_seconds': time.monotonic() - started}


def audit(c=None, *, wait_for_download=True):
    c = c or config()
    publisher = read(resolve(c['publisher_inventory']))
    files = {row['rfilename']: row for row in publisher['siblings']}
    root = PROJECT / '02_dataset_verification/video_audit/runs' / c['run_id']
    root.mkdir(parents=True, exist_ok=True)
    policy = {'whole_decode': True, 'RGB_selection': '16 uniform unique positions', 'frames_per_camera': 16,
              'technical_exclusions': ['missing/hash/size/decode/frame count/PTS/dimensions/black recording'],
              'visual_weakness_exclusion': False, 'labels_used_for_frame_selection_or_quality': False,
              'semantic_visibility_and_incidental_human_status': 'flagged unresolved; no fabricated automated certainty',
              'ffmpeg_sha256': sha(ffmpeg())}
    if not (root / 'VIDEO_QC_POLICY.json').exists(): write(root / 'VIDEO_QC_POLICY.json', policy)
    jobs = [(episode, camera, key) for episode in core(c) for camera, key in zip(c['cameras'], ['video_high', 'video_left', 'video_right'])]

    def one(job):
        episode, camera, key = job
        relative = episode[key]
        path = video_path(c, relative)
        result_path = root / 'per_camera' / f'{episode["episode_index"]:06d}_{camera}.json'
        if result_path.exists():
            old = read(result_path)
            if old.get('technical_valid') and path.exists() and path.stat().st_size == old['source_bytes'] and path.stat().st_mtime_ns == old.get('mtime_ns'):
                return old
        while not path.exists() and wait_for_download:
            state = root / 'ACQUISITION_COMPLETE.json'
            if state.exists() and not read(state)['complete']:
                break
            time.sleep(10)
        item = files[relative]
        try:
            result = inspect_video(path, expected_frames=episode['frame_count'], expected_sha256=item['lfs']['sha256'], expected_size=item['size'])
        except Exception as error:
            result = {'technical_valid': False, 'technical_category': 'D', 'reason': type(error).__name__ + ':' + str(error)[:500]}
        result.update(episode_index=episode['episode_index'], canonical_task_id=episode['canonical_task_id'], camera=camera, source_path=relative, utc=utc())
        write(result_path, result)
        return result

    rows = []
    with ThreadPoolExecutor(max_workers=c['qc_workers']) as pool:
        futures = [pool.submit(one, job) for job in jobs]
        for future in as_completed(futures):
            rows.append(future.result())
            if len(rows) % 50 == 0:
                state = {'utc': utc(), 'done': len(rows), 'total': len(jobs),
                         'technical_valid': sum(row['technical_valid'] for row in rows),
                         'reason_counts': dict(Counter(row.get('reason') or 'VALID' for row in rows))}
                write(root / 'VIDEO_QC_PROGRESS.json', state)
                event(c, 'VIDEO_QC_PROGRESS', **state)
    rows.sort(key=lambda row: (row['episode_index'], row['camera']))
    write(root / 'VIDEO_QC_COMPLETE.json', {'utc': utc(), 'cameras': rows, 'technical_valid': sum(row['technical_valid'] for row in rows),
                                         'count': len(rows), 'full_semantic_human_review_complete': False})
    event(c, 'VIDEO_QC_FINISHED', cameras=len(rows), technical_valid=sum(row['technical_valid'] for row in rows))
    return rows
