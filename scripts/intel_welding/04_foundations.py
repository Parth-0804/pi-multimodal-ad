#!/usr/bin/env python3
"""Read-only foundation audit. Never trains, chooses splits, or estimates test signal.

Run: ma_thesis_env/bin/python -B scripts/intel_welding/04_foundations.py
Existing outputs are preserved; each run creates a new directory.
"""
from __future__ import annotations
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
import numpy as np
import pandas as pd

PROC = ['WELD_TYPE', 'THICKNESS_MM', 'STEEL_TYPE', 'CURRENT_A', 'VOLTAGE_V', 'GAS_BAR', 'ROBOT_SPEED_CPM']
MODS = {'audio': '.flac', 'video': '.avi', 'sensor': '.csv'}


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def save_json(path, obj):
    with Path(path).open('x') as f:
        json.dump(obj, f, indent=2, default=str, allow_nan=False)
        f.write('\n')


def checked_path(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Manifest path escapes data root')
    return path


def timing(frame):
    """Timestamp rate uses positive adjacent differences, not rows/span."""
    if not {'Date', 'Time'}.issubset(frame.columns):
        return {'timestamp_valid': False}
    t = pd.to_datetime(frame.Date.astype(str).str.strip() + ' ' + frame.Time.astype(str).str.strip(),
                       format='%m/%d/%Y %H:%M:%S.%f', errors='coerce')
    dt = t.diff().dt.total_seconds().iloc[1:]
    positive = dt[dt > 0]
    good = len(t) > 1 and t.notna().all() and (dt > 0).all()
    return {'timestamp_valid': bool(good), 'timestamp_invalid_rows': int(t.isna().sum()),
            'timestamp_nonpositive_steps': int((dt <= 0).sum()),
            'sensor_seconds': float((t.iloc[-1] - t.iloc[0]).total_seconds()) if good else None,
            'sensor_rate_hz': float(1 / positive.median()) if len(positive) else None,
            'sensor_dt_min': float(positive.min()) if len(positive) else None,
            'sensor_dt_max': float(positive.max()) if len(positive) else None}


def inspect_sample(root, row):
    import cv2
    import soundfile as sf
    from PIL import Image
    folder = checked_path(root, str(row['SUBDIRS']))
    rec = dict(row, session_id=row['DIRECTORY'], sample_id=folder.name,
               sample_dir_exists=folder.is_dir())
    files = []
    for mod, ext in MODS.items():
        candidates = sorted(folder.glob('*' + ext))
        rec[mod + '_candidate_count'] = len(candidates)
        rec['has_' + mod] = bool(candidates)
        rec[mod + '_readable'] = False
        rec[mod + '_path'] = ''
        rec[mod + '_bytes'] = 0
        rec[mod + '_error'] = ''
        for p in candidates:
            files.append({'sample_id': row['SUBDIRS'], 'session_id': row['DIRECTORY'],
                          'modality': mod, 'path': str(p.relative_to(root)),
                          'bytes': p.stat().st_size, 'sha256': digest(p)})
        if len(candidates) != 1:
            rec[mod + '_error'] = 'missing' if not candidates else 'ambiguous multiple files'
            continue
        p = candidates[0]
        rec[mod + '_path'] = str(p.relative_to(root))
        rec[mod + '_bytes'] = p.stat().st_size
        try:
            if mod == 'audio':
                # Decode all blocks to verify FLAC readability without retaining audio.
                with sf.SoundFile(p) as f:
                    rec.update(audio_sr=f.samplerate, audio_channels=f.channels,
                               audio_seconds=len(f) / f.samplerate)
                    count = 0
                    for block in f.blocks(blocksize=65536):
                        if not np.isfinite(block).all():
                            raise ValueError('nonfinite decoded audio')
                        count += len(block)
                    if count != len(f):
                        raise ValueError('audio decoded length differs from header')
            elif mod == 'video':
                cap = cv2.VideoCapture(str(p))
                try:
                    if not cap.isOpened():
                        raise ValueError('video open failed')
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    rec.update(video_fps=fps, video_frames=n,
                               video_width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                               video_height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                               video_seconds=n / fps if fps > 0 else None)
                    if fps <= 0 or n <= 0:
                        raise ValueError('invalid video metadata')
                    # Bounded structural decode, explicitly not full-stream certification.
                    for index in sorted({0, n // 2, n - 1}):
                        cap.set(cv2.CAP_PROP_POS_FRAMES, index)
                        ok, image = cap.read()
                        if not ok or image is None:
                            raise ValueError(f'video probe failed at frame {index}')
                finally:
                    cap.release()
            else:
                frame = pd.read_csv(p)
                frame.columns = frame.columns.str.strip()
                numeric = frame.select_dtypes(include='number')
                rec.update(sensor_rows=len(frame), sensor_columns=json.dumps(list(frame.columns)),
                           sensor_missing_cells=int(frame.isna().sum().sum()),
                           sensor_numeric_columns=json.dumps(list(numeric.columns)),
                           sensor_constant_columns=json.dumps([c for c in numeric if numeric[c].nunique() <= 1]))
                rec.update(timing(frame))
                if frame.empty or not {'Primary Weld Current', 'Secondary Weld Voltage'}.issubset(frame.columns):
                    raise ValueError('empty or unexpected sensor schema')
            rec[mod + '_readable'] = True
        except Exception as exc:
            rec[mod + '_error'] = type(exc).__name__ + ': ' + str(exc)
    images = sorted(p for p in folder.rglob('*') if p.is_file() and p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'}) if folder.is_dir() else []
    image_paths, image_sizes, image_ok = [], [], []
    for p in images:
        image_paths.append(str(p.relative_to(root)))
        image_sizes.append(p.stat().st_size)
        try:
            with Image.open(p) as im:
                im.load()
            ok = True
        except Exception:
            ok = False
        image_ok.append(ok)
        files.append({'sample_id': row['SUBDIRS'], 'session_id': row['DIRECTORY'],
                      'modality': 'image', 'path': str(p.relative_to(root)), 'bytes': p.stat().st_size,
                      'sha256': digest(p), 'readable': ok})
    rec.update(image_paths=json.dumps(image_paths), image_sizes=json.dumps(image_sizes),
               image_readability=json.dumps(image_ok), n_images=len(images), n_readable_images=sum(image_ok))
    rec['complete_present'] = all(rec['has_' + m] for m in MODS)
    rec['complete_readable'] = all(rec[m + '_readable'] for m in MODS)
    return rec, files


def describe(series):
    s = pd.to_numeric(series, errors='coerce').dropna()
    return {str(k): float(v) for k, v in s.describe().items()} if len(s) else {}


def audit_split(inv, files, split):
    dev, test = set(split['development_sessions']), set(split['final_test_sessions'])
    checks = {'dev_test_session_disjoint': not bool(dev & test),
              'sample_paths_unique': not inv.SUBDIRS.duplicated().any(),
              'folds': []}
    for f in split['cv_folds']:
        tr, va = set(f['train_sessions']), set(f['val_sessions'])
        checks['folds'].append({'fold': f['fold'], 'disjoint': not bool(tr & va),
            'test_excluded': not bool((tr | va) & test), 'covers_dev': tr | va == dev,
            'train_categories': sorted(inv.loc[inv.session_id.isin(tr) & inv.complete_readable, 'CATEGORY'].unique()),
            'val_categories': sorted(inv.loc[inv.session_id.isin(va) & inv.complete_readable, 'CATEGORY'].unique())})
    cross = []
    for (mod, h), group in files.groupby(['modality', 'sha256']):
        ids = set(group.session_id)
        if len(group) < 2:
            continue
        crossed_folds = [f['fold'] for f in split['cv_folds'] if ids & set(f['train_sessions']) and ids & set(f['val_sessions'])]
        if (ids & dev and ids & test) or crossed_folds:
            cross.append({'modality': mod, 'sha256': h, 'paths': list(group.path),
                          'dev_test': bool(ids & dev and ids & test), 'cv_folds': crossed_folds})
    checks['cross_partition_duplicate_groups'] = cross
    checks['full_file_sha256'] = True
    checks['holdout_valid'] = False
    checks['reason'] = 'Existing context baseline evaluated all 2723 complete samples before the proposed holdout; no pristine holdout may be claimed.'
    return checks


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config', default='configs/intel_welding/foundations.json')
    args = ap.parse_args()
    cfg = json.loads(Path(args.config).read_text())
    root = Path(cfg['data_root']).resolve()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    out = Path(cfg['output_root']) / stamp
    out.mkdir(parents=True, exist_ok=False)
    save_json(out / 'config.json', cfg)
    manifest = root / 'manifest.csv'
    m = pd.read_csv(manifest)
    records, file_records = [], []
    import cv2
    cv2.setNumThreads(1)
    with ThreadPoolExecutor(max_workers=cfg['workers']) as pool:
        for i, (rec, files) in enumerate(pool.map(lambda row: inspect_sample(root, row), m.to_dict('records')), 1):
            records.append(rec); file_records.extend(files)
            if i % 400 == 0:
                print(f'{i}/{len(m)} structural inventory', flush=True)
    inv, files = pd.DataFrame(records), pd.DataFrame(file_records)
    inv.to_parquet(out / 'dataset_inventory.parquet', index=False)
    files.to_parquet(out / 'file_inventory.parquet', index=False)
    counts = inv.groupby('CATEGORY').agg(samples=('SUBDIRS', 'size'), sessions=('session_id', 'nunique'),
              audio=('has_audio', 'sum'), video=('has_video', 'sum'), sensor=('has_sensor', 'sum'),
              complete_present=('complete_present', 'sum'), complete_readable=('complete_readable', 'sum'),
              images=('n_images', 'sum'))
    counts.to_csv(out / 'category_missingness.csv')
    inv.groupby('session_id').agg(samples=('SUBDIRS', 'size'), category=('CATEGORY', 'first'),
        categories=('CATEGORY', 'nunique'), complete=('complete_readable', 'sum'),
        audio=('has_audio', 'sum'), video=('has_video', 'sum'), sensor=('has_sensor', 'sum'),
        images=('n_images', 'sum'), supplied_splits=('SPLIT', 'nunique')).to_csv(out / 'session_summary.csv')
    pd.crosstab(inv.session_id, inv.CATEGORY).to_csv(out / 'session_category.csv')
    for col in PROC:
        pd.crosstab(inv.CATEGORY, inv[col], dropna=False).to_csv(out / ('category_' + col.lower() + '.csv'))
    summary = {'manifest_sha256': digest(manifest), 'samples': len(inv), 'sessions': inv.session_id.nunique(),
        'categories': counts.to_dict('index'), 'complete_present': int(inv.complete_present.sum()),
        'complete_readable': int(inv.complete_readable.sum()),
        'samples_with_five_images': int(inv.n_images.eq(5).sum()), 'images': int(inv.n_images.sum()),
        'readable_images': int(inv.n_readable_images.sum()),
        'missing_percent': {mod: float((~inv['has_' + mod]).mean() * 100) for mod in MODS},
        'unreadable_present': {mod: int((inv['has_' + mod] & ~inv[mod + '_readable']).sum()) for mod in MODS},
        'audio_sample_rates': inv.audio_sr.value_counts().to_dict(), 'video_fps': inv.video_fps.value_counts().to_dict(),
        'session_size': describe(inv.groupby('session_id').size()),
        'sample_id_collisions': int(inv.sample_id.duplicated().sum()), 'sample_path_collisions': int(inv.SUBDIRS.duplicated().sum()),
        'mixed_label_sessions': int((inv.groupby('session_id').CATEGORY.nunique() > 1).sum()),
        'supplied_split_mixed_sessions': int((inv.groupby('session_id').SPLIT.nunique() > 1).sum()),
        'supplied_split_counts': inv.SPLIT.value_counts().to_dict(),
        'invalid_sensor_timing': int((inv.has_sensor & ~inv.timestamp_valid.fillna(False).astype(bool)).sum()),
        'sensor_schemas': inv.sensor_columns.value_counts().to_dict(),
        'sensor_rows': describe(inv.sensor_rows), 'sensor_rate_hz': describe(inv.sensor_rate_hz),
        'audio_seconds': describe(inv.audio_seconds), 'video_seconds': describe(inv.video_seconds),
        'sensor_seconds': describe(inv.sensor_seconds),
        'absolute_audio_video_duration_gap': describe((inv.audio_seconds - inv.video_seconds).abs()),
        'absolute_audio_sensor_duration_gap': describe((inv.audio_seconds - inv.sensor_seconds).abs()),
        'absolute_video_sensor_duration_gap': describe((inv.video_seconds - inv.sensor_seconds).abs()),
        'file_count': len(files), 'file_bytes': int(files.bytes.sum()),
        'duplicate_groups': int((files.groupby(['modality', 'sha256']).size() > 1).sum()),
        'unexpected_fps_vs_nominal30': int((inv.has_video & inv.video_fps.ne(30)).sum()),
        'unexpected_audio_rate_vs16000': int((inv.has_audio & inv.audio_sr.ne(16000)).sum()),
        'video_decode_scope': 'first/middle/last frames; full-file SHA256; not full-stream decode'}
    # Reconcile manifest paths against all on-disk sample directories and files.
    actual_dirs = {str(p.relative_to(root)) for session in root.iterdir() if session.is_dir() for p in session.iterdir() if p.is_dir()}
    summary['unmanifested_sample_dirs'] = sorted(actual_dirs - set(inv.SUBDIRS))
    summary['missing_sample_dirs'] = sorted(set(inv.SUBDIRS) - actual_dirs)
    actual_files = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p.suffix.lower() in {'.flac', '.avi', '.csv', '.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'} and p.name != 'manifest.csv'}
    summary['unmapped_modality_files'] = sorted(actual_files - set(files.path))
    dup = files[files.duplicated(['modality', 'sha256'], keep=False)]
    dup.to_csv(out / 'duplicate_files.csv', index=False)
    split_path = Path(cfg['existing_split'])
    split = json.loads(split_path.read_text())
    checks = audit_split(inv, files, split)
    save_json(out / 'leakage_tests.json', checks)
    save_json(out / 'dataset_summary.json', summary)
    # Preserve proposed IDs as historical evidence, explicitly invalid for final claims.
    save_json(out / 'split_disposition.json', {'existing_split_sha256': digest(split_path),
        'existing_id_hash': split['split_sha256'], 'status': 'INVALIDATED_FINAL_HOLDOUT',
        'allow_final_test': False, 'replacement_selected': False,
        'reason': checks['reason'], 'n_test_sessions': len(split['final_test_sessions']),
        'n_dev_sessions': len(split['development_sessions'])})
    provenance = {'timestamp_utc': stamp, 'command': ['ma_thesis_env/bin/python', '-B'] + sys.argv,
        'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'git_status': subprocess.check_output(['git', 'status', '--short'], text=True),
        'python': sys.version, 'packages': {p: importlib.metadata.version(p) for p in ['numpy', 'pandas', 'opencv-python', 'soundfile', 'pillow', 'pyarrow']},
        'manifest_sha256': digest(manifest), 'script_sha256': digest(__file__),
        'config_sha256': digest(args.config), 'models_trained': 0,
        'warnings': ['prior holdout exposure', 'video bounded decode only', 'alignment signal estimation blocked', 'local copy incomplete']}
    save_json(out / 'provenance.json', provenance)
    save_json(out / 'output_manifest.json', [{'path': p.name, 'bytes': p.stat().st_size, 'sha256': digest(p)} for p in sorted(out.iterdir()) if p.is_file()])
    print('OUTPUT=' + str(out), flush=True)
    print(json.dumps({k: summary[k] for k in ['samples', 'sessions', 'complete_readable', 'images', 'missing_percent', 'unreadable_present', 'duplicate_groups', 'supplied_split_mixed_sessions']}, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
