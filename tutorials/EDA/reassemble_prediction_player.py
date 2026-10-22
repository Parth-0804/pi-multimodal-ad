#!/usr/bin/env python3
"""Read-only REASSEMBLE replay. No model is imported, trained, or executed.

The frozen positional banks are accepted only when their writer source, cohort,
splits, manifests, explicit outer-fold rows, labels and copies agree. A failed
check disables that result, never substitutes another row. See README.md.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any

import cv2
import h5py
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from reassemble.alignment import action_from_text, interval_indices, timestamps_1d
from reassemble.inventory import scalar

S1 = ROOT / 'runs/reassemble/20260927T154732Z-section1'
S1B = ROOT / 'runs/reassemble/20260927T175336Z-section1b'
S2 = ROOT / 'runs/reassemble/20260927T192852Z-section2'
EDA = ROOT / 'runs/reassemble/20261016T105418770811Z-dataset-eda/tables/selected_samples.json'
WARNING = 'Replay of saved completed-segment predictions — not live inference'
SIZE = (1440, 900)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def relative(path: Path) -> str:
    return os.path.relpath(path, ROOT)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


class Sources:
    """Hash only relevant small artifacts; raw recordings get stat identities."""
    def __init__(self) -> None:
        self.files: dict[str, dict] = {}

    def note(self, path: Path, hashed: bool = True) -> Path:
        key = relative(path)
        if key not in self.files:
            stat = path.stat()
            self.files[key] = dict(path=key, bytes=stat.st_size, mtime_ns=stat.st_mtime_ns)
        if hashed and 'sha256' not in self.files[key]:
            self.files[key]['sha256'] = digest(path)
        return path

    def json(self, path: Path) -> Any:
        return json.loads(self.note(path).read_text())

    def verified(self, path: Path, manifest: Path) -> Path:
        entries = self.json(manifest)['files']
        match = [x for x in entries if x['path'] == relative(path)]
        require(len(match) == 1, f'Manifest has no unique entry: {relative(path)}')
        self.note(path)
        require(self.files[relative(path)]['sha256'] == match[0]['sha256'],
                f'Manifest hash mismatch: {relative(path)}')
        return path

    def unchanged(self) -> bool:
        return all((ROOT / k).stat().st_size == v['bytes'] and
                   (ROOT / k).stat().st_mtime_ns == v['mtime_ns']
                   for k, v in self.files.items())


def archive(path: Path, keys: list[str]) -> dict[str, np.ndarray]:
    # Named reads avoid loading unused embeddings or an entire feature bank.
    with np.load(path, allow_pickle=False) as bank:
        return {key: bank[key] for key in keys}


class Evidence:
    """The two supported runs have a retained, inspected row-writing contract."""
    def __init__(self, sources: Sources, run: str) -> None:
        self.s = sources
        self.run = S2 if run == 'section2-clean' else S1B
        self.m1 = S1 / 'final_output_manifest.json'
        self.mb = S1B / 'output_manifest.json'
        self.m2 = S2 / 'output_manifest.json'
        self.config = sources.json(S1 / 'config.json')
        self.audit = ROOT / self.config['audit_run']
        self.frame = pd.read_parquet(sources.note(S1 / 'cohort.parquet'))
        for col in ['recording_id', 'segment_id']:
            self.frame[col] = self.frame[col].astype(str)
        require(not self.frame.duplicated(['recording_id', 'segment_id']).any(),
                'Frozen cohort has ambiguous composite identifiers')
        self.recordings = pd.read_parquet(sources.note(self.audit / 'recordings.parquet'))
        self.base_error = None
        try:
            sources.verified(S1 / 'cohort.parquet', self.m1)
            self.splits = sources.json(sources.verified(S1 / 'nested_splits.json', self.m1))
            audited = pd.read_parquet(sources.note(self.audit / 'tables_v2/cohort.parquet'))
            audited = audited.loc[audited.primary_task & audited.dual_complete].reset_index(drop=True)
            for col in ['recording_id', 'segment_id']:
                audited[col] = audited[col].astype(str)
            pd.testing.assert_frame_equal(self.frame, audited[self.frame.columns], check_dtype=False)
            self.fold = np.full(len(self.frame), -1, dtype=int)
            for outer in self.splits['folds']:
                tr, te = set(outer['train_recordings']), set(outer['test_recordings'])
                require(not tr & te, 'Train/test recording overlap')
                require(tr | te == set(self.frame.recording_id), 'Incomplete fold population')
                rows = np.flatnonzero(self.frame.recording_id.isin(te))
                require(np.all(self.fold[rows] == -1), 'Recording assigned to multiple test folds')
                self.fold[rows] = outer['fold']
            require(np.all(self.fold >= 0), 'Missing held-out recording assignment')
            self.contract(S1, 'training_implementation.json', ['section1_features', 'section1_models'])
        except (OSError, ValueError, KeyError, AssertionError, IndexError, TypeError) as exc:
            self.base_error = str(exc)

    def contract(self, run: Path, name: str, modules: list[str]) -> None:
        impl = self.s.json(run / name)
        require(impl['split_sha256'] == self.splits['sha256'], 'Split identity mismatch')
        require(digest(self.s.note(run / 'config.json')) == impl['config_sha256'],
                'Frozen configuration hash mismatch')
        for key, expected in impl.get('frozen_manifests', {}).items():
            require(digest(self.s.note(ROOT / key)) == expected, f'Linked manifest differs: {key}')
        if run == S1B:
            require(ROOT / self.s.json(run / 'config.json')['section1_run'] == S1, 'Stacker linked run differs')
        for module in modules:
            key = f'src/reassemble/{module}.py'
            require(digest(self.s.note(ROOT / key)) == impl['source_sha256'][key],
                    f'Inspected positional writer differs from retained writer: {key}')

    def bank(self, path: Path, manifest: Path, keys: list[str]) -> dict:
        return archive(self.s.verified(path, manifest), keys)

    def check_global(self, bank: dict) -> None:
        require(np.array_equal(bank['y'], self.frame.failure.to_numpy()), 'Prediction labels/order differ')
        require(np.array_equal(bank['fold'], self.fold), 'Prediction folds/order differ')

    def rows(self, row: int) -> tuple[int, np.ndarray, int]:
        fold = int(self.fold[row])
        rows = np.flatnonzero(self.fold == fold)
        return fold, rows, int(np.flatnonzero(rows == row)[0])

    def prediction(self, row: int, branch: str, fusion: str) -> dict:
        """All returned numbers are saved values, after independent row checks."""
        try:
            require(self.base_error is None, self.base_error or '')
            fold, rows, slot = self.rows(row)
            if branch in ('visual', 'sensor'):
                kind = 'rtdetr' if branch == 'visual' else 'sensor_statistics'
                path = S1 / f'predictions/{kind}_perm00.npz'
                bank = self.bank(path, self.m1, ['p', 'hard', 'y', 'fold'])
                self.check_global(bank)
                checkpoint = self.bank(S1 / f'predictions/{kind}_perm00_fold{fold}.npz',
                                       self.m1, ['p', 'hard'])
                for key in ['p', 'hard']:
                    require(np.array_equal(bank[key][rows], checkpoint[key]), 'Fold checkpoint/order mismatch')
                logpath = S1 / f'predictions/{kind}_perm00_fold{fold}.json'
                log = self.s.json(self.s.verified(logpath, self.m1))
                require(log['fold'] == fold and log['kind'] == kind and log['permutation'] == 0, 'Branch log identity mismatch')
                threshold = log['calibration']['threshold']
                p, hard = bank['p'], bank['hard']
                model = 'RT-DETR backbone + visual head' if branch == 'visual' else 'Sensor statistics + logistic'
                if self.run == S2:
                    self.contract(S2, 'implementation.json', ['section2'])
                    prefix = 'U2' if branch == 'visual' else 'U1'
                    copied = self.bank(S2 / 'predictions/oof.npz', self.m2,
                                       ['y', 'fold', prefix + '_p', prefix + '_hard'])
                    self.check_global(copied)
                    require(np.array_equal(p, copied[prefix + '_p']) and
                            np.array_equal(hard, copied[prefix + '_hard']), 'Section 2 branch copy mismatch')
            else:
                self.contract(S1B, 'implementation.json', ['section1_features', 'section1_models', 'section1b'])
                outerpath = S1B / f'stacking/outer{fold}.npz'
                outer = self.bank(outerpath, self.mb, ['test_rows', 'train_rows', 'p', 'hard', 'test_branch_probabilities'])
                require(np.array_equal(outer['test_rows'], rows), 'Stacking explicit test_rows mismatch')
                require(np.array_equal(outer['train_rows'], np.flatnonzero(self.fold != fold)),
                        'Stacking explicit train_rows mismatch')
                logpath = S1B / f'stacking/outer{fold}.json'
                log = self.s.json(self.s.verified(logpath, self.mb))
                require(log['fold'] == fold, 'Stacker log fold mismatch')
                require(log['meta_columns'] == ['p_rtdetr', 'p_sensor_statistics'], 'Stacker column identity mismatch')
                # These are refits of the same frozen branches, not another feature run.
                for j, kind in enumerate(['rtdetr', 'sensor_statistics']):
                    original = self.bank(S1 / f'predictions/{kind}_perm00.npz', self.m1, ['p', 'y', 'fold'])
                    self.check_global(original)
                    require(np.allclose(outer['test_branch_probabilities'][:, j], original['p'][rows],
                                        atol=1e-5, rtol=0), 'Stacker branch refit differs from frozen branch')
                bank = self.bank(S1B / 'stacking/oof.npz', self.mb, ['p', 'hard', 'y', 'fold'])
                self.check_global(bank)
                for key in ['p', 'hard']:
                    require(np.array_equal(bank[key][rows], outer[key]), 'Stacker aggregate/order mismatch')
                p, hard = bank['p'], bank['hard']
                path = S1B / 'stacking/oof.npz'
                threshold = log['stacker']['threshold']
                model = 'F2 logistic stacker (two probabilities)'
                if self.run == S2:
                    self.contract(S2, 'implementation.json', ['section2', 'section2_data'])
                    cfg = self.s.json(S2 / 'config.json')
                    require(ROOT / cfg['section1b_run'] == S1B, 'Section 2 linked run differs')
                    copied = self.bank(S2 / 'predictions/oof.npz', self.m2,
                                       ['y', 'fold', fusion + '_p', fusion + '_hard'])
                    self.check_global(copied)
                    path = S2 / 'predictions/oof.npz'
                    if fusion == 'F2':
                        require(np.array_equal(p, copied['F2_p']) and np.array_equal(hard, copied['F2_hard']),
                                'Section 2 stacker copy mismatch')
                    else:
                        foldbank = self.bank(S2 / f'predictions/outer{fold}.npz', self.m2,
                                             ['test_rows', 'y', 'F1_p', 'F1_hard'])
                        require(np.array_equal(foldbank['test_rows'], rows), 'Section 2 explicit rows mismatch')
                        require(np.array_equal(foldbank['y'], self.frame.failure.to_numpy()[rows]), 'Section 2 fold labels mismatch')
                        for key in ['F1_p', 'F1_hard']:
                            require(np.array_equal(foldbank[key], copied[key][rows]), 'Section 2 fold/aggregate mismatch')
                        p, hard = copied['F1_p'], copied['F1_hard']
                        require(np.allclose(p[rows], outer['test_branch_probabilities'].mean(axis=1),
                                            atol=1e-12, rtol=0), 'Uniform fusion definition mismatch')
                        logpath = S2 / f'predictions/outer{fold}.json'
                        log = self.s.json(self.s.verified(logpath, self.m2))
                        require(log['fold'] == fold, 'Uniform fusion log fold mismatch')
                        threshold = log['uniform_threshold']
                        model = 'F1 uniform mean of two probabilities'
            validate_scores(p, hard, rows, threshold, len(self.frame))
            return dict(available=True, model=model, probability=float(p[row]), decision=int(hard[row]),
                        threshold=float(threshold), comparison='p >= threshold', threshold_source=relative(logpath),
                        source=relative(path), row=row, fold=fold, fold_slot=slot,
                        held_out='Recording excluded from this outer-fold fit; adaptive exploratory study, not untouched confirmation')
        except (OSError, ValueError, KeyError, AssertionError, IndexError, TypeError) as exc:
            return dict(available=False, reason=str(exc), model=branch)


def validate_scores(p: np.ndarray, hard: np.ndarray, rows: np.ndarray, threshold: float, n: int) -> None:
    require(p.shape == hard.shape == (n,), 'Unexpected prediction array shape')
    require(np.all(np.isfinite(p)) and np.all((p >= 0) & (p <= 1)), 'Invalid P(failure)')
    require(np.all(np.isin(hard, [0, 1])), 'Invalid saved decision')
    require(np.isfinite(threshold) and 0 <= threshold <= 1, 'Invalid retained threshold')
    require(np.array_equal(hard[rows], (p[rows] >= threshold).astype(int)), 'Saved decision/threshold mismatch')


def choose_samples(evidence: Evidence, args: argparse.Namespace) -> tuple[list[int], str]:
    frame = evidence.frame
    if args.recording_id:
        found = np.flatnonzero((frame.recording_id == args.recording_id) & (frame.segment_id == args.segment_id))
        require(len(found) == 1, 'Unknown/ambiguous recording + segment. Use --list-samples.')
        return found.tolist(), 'Manual composite identifier; no predictions used for selection'
    if EDA.exists():
        selected = evidence.s.json(EDA)
        rows = []
        for item in selected:
            matches = np.flatnonzero((frame.recording_id == item['recording_id']) & (frame.segment_id == item['segment_id']))
            require(len(matches) == 1, 'EDA sample identity is not unique')
            row = int(matches[0]); sample = frame.iloc[row]
            require(row == item['cohort_row_index'] and int(sample.failure) == item['model_failure_target'], 'EDA row/label mismatch')
            require(sample.start == item['start_unix_seconds'] and sample.end == item['end_unix_seconds'], 'EDA boundaries mismatch')
            rows.append(row)
        return rows, 'Reused EDA manifest: nearest insert action/outcome median duration; recording_id, segment_id tie-break'
    rows = []
    for label in [0, 1]:
        group = frame.loc[(frame.action == 'insert') & (frame.failure == label)].copy()
        group['distance'] = abs((group.end - group.start) - (group.end - group.start).median())
        group = group.sort_values(['distance', 'recording_id', 'segment_id'])
        require(len(group) > 0, 'No insert examples for both outcomes; select an explicit sample')
        rows.append(int(group.index[0]))
    return rows, 'Insert action/outcome median duration; recording_id, segment_id tie-break; local availability checked after selection'


def load_sample(evidence: Evidence, row: int, root: Path, fusion: str) -> dict:
    sample = evidence.frame.iloc[row]
    s = evidence.s
    rid, sid = sample.recording_id, sample.segment_id
    matches = evidence.recordings.loc[evidence.recordings.recording_id == rid]
    require(len(matches) == 1, 'No unique inventory recording identity')
    rec = matches.iloc[0]
    raw = s.note(root / 'raw/data' / f'{rid}.h5', hashed=False)
    rawstat = raw.stat()
    warnings = []
    verified = rawstat.st_size == int(rec.size_bytes) and rawstat.st_mtime_ns == int(rec.mtime_ns)
    if not verified:
        warnings.append('Raw file size/mtime differs from inventory; prediction mapping disabled')
    with h5py.File(raw, 'r') as h:
        group = h['segments_info'][sid]
        annotation = {k: scalar(group, k) if k in group else None for k in ['start', 'end', 'success', 'text']}
        annotation['text'] = annotation['text'] or ''
        start, end = float(annotation['start']), float(annotation['end'])
        require(np.isfinite(start + end) and end > start, 'Invalid raw segment interval')
        outcome = annotation['success']
        label_ok = isinstance(outcome, (bool, int, np.bool_, np.integer)) and outcome in (0, 1)
        verified = bool(verified and label_ok and int(not outcome) == int(sample.failure) and
                        start == sample.start and end == sample.end and action_from_text(annotation['text']) == sample.action)
        if not verified:
            warnings.append('Raw annotation/cohort identity not fully verified; model results disabled')
        clock = timestamps_1d(h['timestamps/hand'][...])
        indices = interval_indices(clock, start, end)
        require(len(indices) > 0, 'No hand-camera frames in this segment')
        encoded_bytes = h['hand'].dtype.itemsize
        sensor_t, sensor_x = np.array([]), np.array([])
        try:
            st = timestamps_1d(h['timestamps/measured_force'][...])
            si = interval_indices(st, start, end)
            if len(si):
                sensor_t = st[si]
                sensor_x = h['robot_state/measured_force'][int(si[0]):int(si[-1]) + 1, 0]
                require(sensor_x.shape == sensor_t.shape, 'Sensor time/value shape mismatch')
        except (KeyError, ValueError, OSError) as exc:
            sensor_t, sensor_x = np.array([]), np.array([])
            warnings.append(f'Optional sensor unavailable: {exc}')
    cache = s.note(root / 'cache/encoded_media' / str(rec.sha256) / 'hand.mp4', hashed=False)
    require(cache.stat().st_size == encoded_bytes, 'Cached encoded camera size differs from HDF5 blob')
    selected = []
    try:
        blockpath = S1 / f'features/{rid}.npz'
        block = evidence.bank(blockpath, evidence.m1, ['row_index', 'frame_indices'])
        expected = np.flatnonzero(evidence.frame.recording_id == rid)
        require(np.array_equal(block['row_index'], expected), 'Feature block row map mismatch')
        fi = block['frame_indices'][int(np.flatnonzero(expected == row)[0])]
        require(np.issubdtype(fi.dtype, np.integer) and np.all(np.isin(fi, indices)), 'Retained frames outside raw interval')
        require(verified and evidence.base_error is None, 'Retained-frame raw/cohort mapping unverified')
        selected = fi.tolist()
    except (OSError, KeyError, ValueError) as exc:
        warnings.append(f'Historical model-frame indicator omitted: {exc}')
    predictions = {name: evidence.prediction(row, name, fusion) if verified else
                   dict(available=False, reason='Raw annotation/inventory mapping not verified', model=name)
                   for name in ['visual', 'sensor', 'fusion']}
    for name, pred in predictions.items():
        if not pred['available']:
            warnings.append(f'{name}: {pred["reason"]}')
    return dict(recording_id=rid, segment_id=sid, row=row, start=start, end=end, duration=end-start,
                action=action_from_text(annotation['text']), annotation=annotation,
                outcome=('SUCCESS' if outcome else 'FAILURE') if label_ok else 'UNAVAILABLE',
                raw=relative(raw), camera='hand', cache=cache, clock=clock, indices=indices,
                selected=selected, sensor_t=sensor_t, sensor_x=sensor_x, predictions=predictions,
                verified=verified, warnings=warnings, run=relative(evidence.run), fusion=fusion)


class FrameReader:
    """Seek to the segment; thereafter decode sequentially, retaining one frame."""
    def __init__(self, sample: dict) -> None:
        self.cap = cv2.VideoCapture(str(sample['cache']))
        self.index = -1
        self.frame: np.ndarray | None = None
        if not self.cap.isOpened() or int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) != len(sample['clock']):
            self.close()
            raise ValueError('Video cannot open or frame count differs from timestamp count')

    def read(self, index: int) -> np.ndarray:
        if self.index != index:
            if index != self.index + 1:
                require(self.cap.set(cv2.CAP_PROP_POS_FRAMES, index), 'Cannot seek source frame')
            ok, frame = self.cap.read()
            require(ok and frame is not None, f'Cannot decode recording-relative frame {index}')
            self.frame, self.index = frame, index
        return self.frame

    def close(self) -> None:
        self.cap.release()


def frame_at(sample: dict, elapsed: float) -> int:
    """Latest observed frame at clock time; hold first only for leading gap."""
    ids = sample['indices']
    slot = int(np.searchsorted(sample['clock'][ids], sample['start'] + elapsed, side='right') - 1)
    return int(ids[max(0, min(slot, len(ids)-1))])


def results_visible(sample: dict, elapsed: float, show_from_start: bool) -> bool:
    return show_from_start or elapsed >= sample['duration']


def text(canvas: np.ndarray, value: str, xy: tuple[int, int], scale: float = .6,
         color: tuple = (225, 230, 235)) -> None:
    cv2.putText(canvas, value, xy, cv2.FONT_HERSHEY_SIMPLEX, scale, color, 1, cv2.LINE_AA)


def banner() -> np.ndarray:
    # Pillow supports the exact Unicode warning; OpenCV's built-in font does not.
    im = Image.new('RGB', (SIZE[0], 48), (38, 46, 66))
    font = ImageFont.truetype('DejaVuSans.ttf', 24)
    ImageDraw.Draw(im).text((20, 8), WARNING, font=font, fill=(255, 230, 165))
    return np.asarray(im)[:, :, ::-1].copy()


BANNER: np.ndarray | None = None


def render(sample: dict, frame: np.ndarray, index: int, elapsed: float,
           args: argparse.Namespace, end_card: bool = False) -> np.ndarray:
    """One layout shared by desktop playback, PNG fallback and video export."""
    global BANNER
    if BANNER is None:
        BANNER = banner()
    canvas = np.full((SIZE[1], SIZE[0], 3), (25, 22, 20), np.uint8)
    canvas[:48] = BANNER
    text(canvas, f"{sample['recording_id']} / segment {sample['segment_id']}   |   camera: hand", (20, 77), .68)
    text(canvas, f"Action: {sample['action'].upper()} - dataset annotation", (20, 107), .68)
    text(canvas, f"{sample['annotation']['text']}   |   illustrative example, not performance evidence", (20, 134), .54)
    scale = min(900 / frame.shape[1], 505 / frame.shape[0])
    image = cv2.resize(frame, (round(frame.shape[1]*scale), round(frame.shape[0]*scale)))
    y, x = 150 + (505-image.shape[0])//2, 20 + (900-image.shape[1])//2
    canvas[y:y+image.shape[0], x:x+image.shape[1]] = image
    timestamp = sample['clock'][index]
    text(canvas, f"Source frame {index} | Unix seconds {timestamp:.6f} | elapsed {elapsed:.2f}/{sample['duration']:.2f} s", (20, 681), .55)
    retained = 'RETAINED MODEL FRAME' if index in sample['selected'] else 'Native preview frame'
    text(canvas, f"{retained} | aspect-preserving resize | playback {args.speed:g}x | no audio", (20, 707), .54, (150, 220, 160))
    # Cache the static native observations; only the cursor moves each frame.
    if '_sensor_panel' not in sample:
        panel = np.full((88, 901, 3), (25, 22, 20), np.uint8)
        st, sx = sample['sensor_t'], sample['sensor_x']
        cv2.rectangle(panel, (0, 26), (900, 87), (75, 75, 75), 1)
        finite = np.isfinite(sx)
        if len(st) and finite.any():
            lo, hi = float(sx[finite].min()), float(sx[finite].max())
            xx = (st-sample['start']) / sample['duration']*900
            yy = 82 - (sx-lo)/max(hi-lo, 1e-12)*50
            for px, py in zip(xx[finite], yy[finite]):
                cv2.circle(panel, (round(px), round(py)), 1, (210, 175, 85), -1)
            text(panel, f"measured_force[0], units unverified | native dots {lo:.3g}..{hi:.3g} | missing {int((~finite).sum())}", (0, 17), .5)
        else:
            text(panel, 'Optional sensor channel unavailable', (0, 17), .5)
        sample['_sensor_panel'] = panel
    canvas[718:806, 20:921] = sample['_sensor_panel']
    cursor = 20 + round(min(1, elapsed/sample['duration'])*900)
    cv2.line(canvas, (cursor, 744), (cursor, 806), (80, 210, 255), 2)
    cv2.line(canvas, (20, 833), (920, 833), (110, 110, 110), 2)
    for idx in sample['selected']:
        pos = 20+round((sample['clock'][idx]-sample['start'])/sample['duration']*900)
        cv2.line(canvas, (pos, 825), (pos, 841), (150, 220, 160), 1)
    cv2.circle(canvas, (cursor, 833), 5, (80, 210, 255), -1)
    text(canvas, 'Segment progress (seconds); green ticks = retained hand frames', (20, 859), .51)
    x = 945
    text(canvas, 'COMPLETED-SEGMENT RESULTS', (x, 80), .65)
    text(canvas, f"Start: {sample['start']:.6f} Unix s", (x, 112), .52)
    text(canvas, f"End:   {sample['end']:.6f} Unix s", (x, 139), .52)
    text(canvas, f"Cohort row: {sample['row']} | positive class: failure", (x, 166), .51)
    text(canvas, sample['run'].split('/')[-1], (x, 194), .51)
    visible = results_visible(sample, elapsed, args.show_results_from_start)
    if not visible:
        text(canvas, 'Outcome and predictions hidden.', (x, 255), .65)
        text(canvas, 'They will appear at the segment end.', (x, 290), .6)
        text(canvas, 'No model is running during playback.', (x, 337), .55)
    else:
        text(canvas, f"Recorded outcome: {sample['outcome']}", (x, 241), .68, (150, 220, 255))
        text(canvas, 'Dataset annotation (separate from predictions)', (x, 268), .48)
        for j, name in enumerate(['visual', 'sensor', 'fusion']):
            pred = sample['predictions'][name]; y = 317 + j*129
            text(canvas, name.upper(), (x, y), .65, (150, 220, 160))
            if pred['available']:
                text(canvas, pred['model'], (x, y+25), .49)
                text(canvas, f"P(failure): {pred['probability']:.6f}", (x, y+52), .63)
                text(canvas, f"Saved decision: {'FAILURE' if pred['decision'] else 'SUCCESS'}", (x, y+78), .58)
                text(canvas, f"p >= {pred['threshold']:.8g} | outer fold {pred['fold']}", (x, y+101), .5)
            else:
                text(canvas, 'Prediction unavailable:', (x, y+30), .58)
                text(canvas, 'sample mapping not verified', (x, y+57), .54)
                text(canvas, 'See validation summary for missing evidence.', (x, y+83), .44)
        if any(p['available'] for p in sample['predictions'].values()):
            text(canvas, 'Held out for this fit; exploratory reuse of folds.', (x, 740), .49)
        text(canvas, 'An annotated failure may not look obvious.', (x, 766), .5)
    if end_card:
        text(canvas, f'END CARD | results hold {args.hold_seconds:g} s in export', (x, 810), .5, (150, 220, 255))
    if sample['warnings']:
        text(canvas, 'Evidence limitations: see validation_summary.json', (x, 841), .46, (100, 160, 255))
    text(canvas, 'Space pause/resume | R restart | N/P next/previous | Left/Right step (paused) | Q/Esc quit', (20, 887), .59)
    return canvas


def gui_available() -> bool:
    return bool(os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY')) and not any(
        'GUI:' in line and 'NONE' in line for line in cv2.getBuildInformation().splitlines())


def playback(samples: list[dict], args: argparse.Namespace) -> None:
    current, elapsed, paused = 0, 0.0, False
    reader = FrameReader(samples[current])
    name = 'REASSEMBLE - saved completed-segment replay'
    try:
        cv2.namedWindow(name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(name, *SIZE)
        previous = time.monotonic()
        while True:
            sample = samples[current]
            now = time.monotonic()
            if not paused:
                elapsed = min(sample['duration'], elapsed+(now-previous)*args.speed)
                paused = elapsed >= sample['duration']
            previous = now
            index = frame_at(sample, elapsed)
            cv2.imshow(name, render(sample, reader.read(index), index, elapsed, args, elapsed >= sample['duration']))
            key = cv2.waitKeyEx(15)
            if key in (27, ord('q'), ord('Q')) or cv2.getWindowProperty(name, cv2.WND_PROP_VISIBLE) < 1:
                break
            if key == 32:
                paused = not paused
            elif key in (ord('r'), ord('R')):
                elapsed, paused = 0.0, False
            elif key in (ord('n'), ord('N'), ord('p'), ord('P')):
                current = (current+(1 if key in (ord('n'), ord('N')) else -1)) % len(samples)
                reader.close(); reader = FrameReader(samples[current]); elapsed, paused = 0.0, False
            elif paused and key in (81, 83, 65361, 65363, 2424832, 2555904):
                delta = -1 if key in (81, 65361, 2424832) else 1
                slot = int(np.flatnonzero(sample['indices'] == index)[0])
                slot = max(0, min(slot+delta, len(sample['indices'])-1))
                elapsed = float(sample['clock'][sample['indices'][slot]]-sample['start'])
                if slot == len(sample['indices'])-1 and delta > 0:
                    elapsed = sample['duration']
    finally:
        reader.close()
        cv2.destroyAllWindows()


def export_sample(sample: dict, args: argparse.Namespace, out: Path) -> dict:
    stem = f"{sample['recording_id']}_segment-{sample['segment_id']}"
    reader = FrameReader(sample)
    report: dict[str, Any] = dict(sample=stem, source_frame_checks=[], previews=[])
    try:
        for label, elapsed in [('start', 0.0), ('middle', sample['duration']/2), ('results', sample['duration'])]:
            index = frame_at(sample, elapsed)
            frame = reader.read(index)
            report['source_frame_checks'].append(dict(position=label, index=index, shape=list(frame.shape), dtype=str(frame.dtype)))
            path = out / f'{stem}_{label}.png'
            require(cv2.imwrite(str(path), render(sample, frame, index, elapsed, args, label == 'results')), 'PNG export failed')
            require(cv2.imread(str(path)).shape == (SIZE[1], SIZE[0], 3), 'PNG decode failed')
            report['previews'].append(path.name)
        if not args.export:
            return report
        count = math.ceil(sample['duration']/args.speed*args.fps)
        hold = math.ceil(args.hold_seconds*args.fps)
        path = out / f'{stem}.webm'
        writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*'VP80'), args.fps, SIZE)
        require(writer.isOpened(), 'Installed OpenCV cannot encode VP8 WebM; PNG previews remain available')
        used = []
        try:
            with (out / f'{stem}_frame_mapping.csv').open('w', newline='') as stream:
                table = csv.writer(stream)
                table.writerow(['output_frame', 'output_seconds', 'segment_elapsed_seconds', 'source_frame', 'source_unix_seconds', 'results_visible', 'end_card'])
                final = None
                for k in range(count+hold):
                    end = k >= count
                    elapsed = sample['duration'] if end else k/args.fps*args.speed
                    index = frame_at(sample, elapsed)
                    if not end or final is None:
                        rendered = render(sample, reader.read(index), index, elapsed, args, end)
                        if end:
                            final = rendered
                    else:
                        rendered = final
                    writer.write(rendered)
                    table.writerow([k, k/args.fps, elapsed, index, sample['clock'][index], results_visible(sample, elapsed, args.show_results_from_start), end])
                    if not end:
                        used.append(index)
        finally:
            writer.release()
        cap = cv2.VideoCapture(str(path)); decoded = 0; actual_fps = cap.get(cv2.CAP_PROP_FPS)
        try:
            while True:
                ok, image = cap.read()
                if not ok:
                    break
                require(image.shape == (SIZE[1], SIZE[0], 3), 'Export resolution mismatch')
                decoded += 1
        finally:
            cap.release()
        require(decoded == count+hold and abs(actual_fps-args.fps) < .01, 'Export frame count/FPS mismatch')
        report['video'] = dict(path=path.name, decoded_frames=decoded, fps=actual_fps,
                               duration_seconds=decoded/actual_fps, expected_duration_seconds=sample['duration']/args.speed+args.hold_seconds,
                               native_interval_frames=len(sample['indices']), unique_preview_frames=len(set(used)),
                               duplicate_preview_frames=count-len(set(used)), dropped_native_frames=len(set(sample['indices'])-set(used)),
                               end_card_frames=hold, source_leading_hold_seconds=float(sample['clock'][sample['indices'][0]]-sample['start']),
                               mapping='Uniform output clock -> latest source timestamp (sample-and-hold); first frame held over leading gap; final result card appended',
                               speed=args.speed, aspect_preserving_resize=list(SIZE), audio=False, browser_playback_verified=False)
        return report
    finally:
        reader.close()


def serial_sample(sample: dict) -> dict:
    result = {key: value for key, value in sample.items() if not key.startswith('_') and key not in ['clock', 'indices', 'sensor_t', 'sensor_x', 'cache']}
    result.update(cache=relative(sample['cache']), native_frame_count=len(sample['indices']),
                  sensor_shape=list(sample['sensor_x'].shape), sensor_units='unverified',
                  sensor_time_basis='Unix seconds, same raw annotation interval',
                  raw_identity='Inventory size/mtime + annotations; entire raw recording not rehashed',
                  cache_identity='Preexisting content-addressed inventory cache; blob byte count and timestamp/frame count checked, cache not rehashed')
    return result


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--demo', action='store_true', help='Play both EDA examples (default)')
    p.add_argument('--recording-id'); p.add_argument('--segment-id')
    p.add_argument('--list-samples', action='store_true', help='List locally available cohort recordings/segments; no video decoding')
    p.add_argument('--limit', type=int, default=20, help='Sample listing rows; 0 means all')
    p.add_argument('--run', choices=['section2-clean', 'section1b'], default='section2-clean', help='Pinned coherent saved run; see README')
    p.add_argument('--fusion', choices=['F2', 'F1'], default='F2', help='F2 logistic stacker; F1 uniform mean (Section 2 only)')
    p.add_argument('--data-root', type=Path, help='Override configured REASSEMBLE root; no raw writes')
    p.add_argument('--headless', action='store_true'); p.add_argument('--export', action='store_true', help='Write timestamp-mapped VP8 videos and static previews')
    p.add_argument('--validate-only', action='store_true', help='Check evidence and decode/render first, middle, final frames, without GUI/video export')
    p.add_argument('--show-results-from-start', action='store_true', help='Show retrospective whole-segment results throughout')
    p.add_argument('--speed', type=float, default=1.0); p.add_argument('--fps', type=float, default=15.0, help='Export FPS only; source alignment uses native timestamps')
    p.add_argument('--hold-seconds', type=float, default=4.0, help='Final results card hold in exported video')
    return p


def main(argv: list[str] | None = None) -> int:
    p = parser(); args = p.parse_args(argv)
    if bool(args.recording_id) != bool(args.segment_id):
        p.error('--recording-id and --segment-id must be supplied together')
    if args.run == 'section1b' and args.fusion != 'F2':
        p.error('section1b supports F2 only')
    if not (.1 <= args.speed <= 4 and 1 <= args.fps <= 60 and 1 <= args.hold_seconds <= 30):
        p.error('Use speed 0.1..4, fps 1..60 and hold-seconds 1..30')
    if args.validate_only and args.export:
        p.error('--validate-only and --export are separate modes')
    try:
        sources = Sources(); evidence = Evidence(sources, args.run)
        root = (args.data_root or Path(os.environ.get('REASSEMBLE_DATA_ROOT', evidence.config['data_root'])))
        root = root if root.is_absolute() else ROOT / root
        if args.list_samples:
            local = {rid for rid in evidence.frame.recording_id.unique() if (root / 'raw/data' / f'{rid}.h5').is_file()}
            table = evidence.frame.loc[evidence.frame.recording_id.isin(local)].copy()
            table['duration_seconds'] = table.end-table.start
            print(f'{len(table)} cohort samples in locally present raw recordings; cache/frame availability verified on opening.')
            print(table[['recording_id', 'segment_id', 'action', 'failure', 'duration_seconds']].head(args.limit or len(table)).to_string(index=False))
            return 0
        rows, rule = choose_samples(evidence, args)
        samples = [load_sample(evidence, row, root, args.fusion) for row in rows]
        gui = gui_available()
        if not gui and not (args.headless or args.validate_only):
            print('Desktop unavailable (display/OpenCV GUI); exporting meeting backups instead.')
            args.headless = args.export = True
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        out = ROOT / 'runs/reassemble' / f'{stamp}-prediction-playback'
        out.mkdir(parents=True, exist_ok=False)
        (out / '.gitignore').write_text('*\n')
        for source in [Path(__file__), ROOT/'src/reassemble/inventory.py', ROOT/'src/reassemble/alignment.py']:
            sources.note(source)
        reports = []
        for sample in samples:
            print(f"Validating {sample['recording_id']}/{sample['segment_id']} (cohort row {sample['row']})", flush=True)
            report = export_sample(sample, args, out)
            reports.append(report)
            for name, pred in sample['predictions'].items():
                print(f'  {name}: {pred}', flush=True)
        if gui and not (args.headless or args.validate_only):
            playback(samples, args)
        require(sources.unchanged(), 'A source artifact changed during playback; investigate before using results')
        manifest = dict(timestamp_utc=stamp, command=[sys.executable, str(Path(__file__).relative_to(ROOT)), * (argv if argv is not None else sys.argv[1:])],
                        git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                        git_dirty=bool(subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=normal'], cwd=ROOT, text=True)),
                        resolved_options={k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()},
                        data_root=relative(root),
                        software=dict(python=sys.version, opencv=cv2.__version__, numpy=np.__version__, pandas=pd.__version__, h5py=h5py.__version__),
                        warning=WARNING, selection_rule=rule, run=relative(evidence.run), fusion=args.fusion,
                        samples=[serial_sample(s) for s in samples], sources=list(sources.files.values()),
                        media=reports, inputs_unchanged=True, gui_available=gui,
                        interactive_session_opened=bool(gui and not (args.headless or args.validate_only)),
                        interactive_controls_verified=False, no_training_or_inference=True,
                        config_snapshots={relative(r/'config.json'): json.loads((r/'config.json').read_text()) for r in [S1, S1B, evidence.run]})
        (out/'source_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
        summary = dict(real_data_checks=['unique composite IDs', 'raw bounds/annotation checks', 'first/middle/final frame decode',
                                         'static render/decode', 'input stat identities unchanged'],
                       predictions={f"{s['recording_id']}/{s['segment_id']}": s['predictions'] for s in samples},
                       warnings=[w for s in samples for w in s['warnings']],
                       gui_controls='NOT VERIFIED: no automated desktop interaction', browser_playback='NOT VERIFIED',
                       video_exports=[r.get('video') for r in reports], status='partial' if any(s['warnings'] for s in samples) else 'available read-only checks passed')
        (out/'validation_summary.json').write_text(json.dumps(summary, indent=2)+'\n')
        outputs = [dict(path=f.name, bytes=f.stat().st_size, sha256=digest(f)) for f in out.iterdir() if f.is_file()]
        (out/'output_manifest.json').write_text(json.dumps(outputs, indent=2)+'\n')
        print(f'Output: {relative(out)}', flush=True)
        return 0
    except (OSError, ValueError, KeyError, AssertionError, cv2.error) as exc:
        print(f'Player: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
