"""Read-only, fail-closed adapters for the validated MSM Stage 2 contract."""
import hashlib
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset

from stage2.audit_sensors import COMMON_MTC, accumulate, finalize, new_accumulator

STATS = ("mean", "std", "rms", "min", "max", "peak_to_peak")
FEATURE_NAMES = tuple(f"{c}__{s}" for c in COMMON_MTC for s in STATS)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024**2), b""):
            h.update(block)
    return h.hexdigest()


def binary_target(native, label2="stable_negative"):
    """Target is intervention-worthy abnormal CUTTING, not tool health."""
    native = np.asarray(native)
    if not np.isin(native, [0, 1, 2]).all():
        raise ValueError("Unknown native label")
    if label2 not in ("stable_negative", "exclude"):
        raise ValueError("Unknown label-2 policy")
    return (native == 1).astype(np.int64), (native != 2 if label2 == "exclude" else np.ones(native.shape, bool))


def interval_statistics(table, start, end, channels=COMMON_MTC, min_rows=5, max_gap=.5):
    """No interpolation; half-open native sensor interval [start,end)."""
    if not channels or len(set(channels)) != len(channels) or not set(channels) <= set(COMMON_MTC):
        raise ValueError("Only declared numerical signal channels are allowed")
    t = table["time"].to_numpy(float)
    if not np.isfinite(t).all() or np.any(np.diff(t) <= 0) or not start < end:
        raise ValueError("Invalid sensor clock/interval")
    a, b = np.searchsorted(t, [start, end], side="left")
    times = t[a:b]
    gap = float(np.diff(np.r_[start, times, end]).max())
    x = table[list(channels)].iloc[a:b].to_numpy(float)
    if len(x) < min_rows or gap > max_gap + 1e-12 or not np.isfinite(x).all():
        raise ValueError("Sensor coverage/finite-value gate failed")
    result = []
    for column in x.T:
        accumulator = new_accumulator()
        accumulate(accumulator, column)
        values = finalize(accumulator)
        result.extend(values[s] for s in STATS)
    return np.asarray(result, dtype=np.float32), {"rows": len(x), "max_gap_s": gap, "start_s": start, "end_s": end}


def verify_frame_policy(row, stage2):
    # Reuse the scientifically corrected Stage 2 selector verbatim.
    source = Path(__file__).resolve().parents[1] / "stage2"
    if str(source) not in sys.path:
        sys.path.insert(0, str(source))
    from frame_contract import select_frames
    group = row["group_id"]
    pts = np.load(Path(stage2) / "cache" / (group.replace("/", "_") + "_native_pts.npy"))
    mapping = json.loads((Path(stage2) / "manifests/video_alignment_final.json").read_text())[group]
    result = select_frames(pts, row["start_s"], row["end_s"], mapping["offset_s"],
                           mapping["uncertainty_s"], mapping["support_sensor_s"])
    expected = json.loads(row["frame_indices_json"])
    if not result["accepted"] or result["indices"] != expected or len(set(expected)) != 16:
        raise ValueError("Frame-label policy mismatch: " + row["interval_id"])
    if not np.allclose(result["video_pts_s"], json.loads(row["video_pts_s_json"]), atol=1e-10, rtol=0):
        raise ValueError("Native frame PTS mismatch")
    return result


def load_cohort(stage2, label2="stable_negative", verify=True):
    """Return metadata separately from the 90 permitted numerical predictors."""
    stage2 = Path(stage2)
    frame = pd.read_csv(stage2 / "MSM_PILOT_SAMPLE_MANIFEST.csv", keep_default_na=False)
    if set(frame.dataset_version) != {2} or not frame.interval_id.is_unique:
        raise ValueError("Unverified dataset version/duplicate prediction units")
    frame = frame.loc[frame.verified_multimodal_example == True].copy().reset_index(drop=True)
    frame["target"], keep = binary_target(frame.native_label, label2)
    frame = frame.loc[keep].reset_index(drop=True)
    if verify:
        labels = {}
        for row in frame.to_dict("records"):
            path = row["label_file"]
            if path not in labels:
                if digest(path) != row["label_file_sha256"]:
                    raise ValueError("Label source hash changed")
                labels[path] = pd.read_csv(path)
            actual = labels[path].iloc[int(row["source_row"]) - 2]
            if int(actual.label) != row["native_label"] or not np.allclose([actual.start, actual.end], [row["start_s"], row["end_s"]], atol=1e-10, rtol=0):
                raise ValueError("Source interval/label mismatch")
            verify_frame_policy(row, stage2)
    return frame


def sensor_features(frame, data_root, channels=COMMON_MTC):
    arrays, evidence, loaded = [], [], {}
    for row in frame.to_dict("records"):
        group = row["group_id"]
        if group not in loaded:
            paths = list((Path(data_root) / group).glob("*_mtc.csv"))
            if len(paths) != 1:
                raise ValueError("Exactly one declared MTC source required")
            loaded[group] = (paths[0], pd.read_csv(paths[0], usecols=["time", *channels]))
        path, table = loaded[group]
        values, gate = interval_statistics(table, row["start_s"], row["end_s"], channels)
        arrays.append(values)
        evidence.append({"interval_id": row["interval_id"], "source": str(path), **gate})
    return np.stack(arrays), evidence


def letterbox_rgb(bgr, sar=(3, 8), size=640):
    """Honor non-square source pixels, then preserve display aspect ratio."""
    h, w = bgr.shape[:2]
    display_width = round(w * sar[0] / sar[1])
    scale = size / max(h, display_width)
    target_w, target_h = round(display_width * scale), round(h * scale)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    resized = cv2.resize(rgb, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
    canvas = np.zeros((size, size, 3), np.uint8)
    left, top = (size - target_w) // 2, (size - target_h) // 2
    canvas[top:top + target_h, left:left + target_w] = resized
    return canvas


@dataclass
class PixelItem:
    pixels: torch.Tensor
    interval_id: str
    decode_seconds: float


class IntervalPixels(Dataset):
    """Exactly 16 audited frames; handles are worker-local and explicitly closed."""
    def __init__(self, frame, stage2, decoder_threads=1):
        self.rows = frame.to_dict("records")
        selected = pd.read_csv(Path(stage2) / "manifests/selected_frame_manifest.csv")
        self.hashes = {(r.interval_id, int(r.native_frame_index)): r.decoded_frame_sha256 for r in selected.itertuples()}
        self.decoder_threads, self.captures = decoder_threads, {}

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        before = time.perf_counter()
        row = self.rows[index]
        path = row["video_file"]
        if path not in self.captures:
            cap = cv2.VideoCapture(path, cv2.CAP_FFMPEG, [cv2.CAP_PROP_N_THREADS, self.decoder_threads])
            if not cap.isOpened():
                raise ValueError("Video does not open: " + path)
            self.captures[path] = cap
        cap = self.captures[path]
        frames = []
        for native_index in json.loads(row["frame_indices_json"]):
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(native_index))
            ok, image = cap.read()
            if not ok or hashlib.sha256(image.tobytes()).hexdigest() != self.hashes[(row["interval_id"], native_index)]:
                raise ValueError("Missing/misaligned/changed decoded frame")
            timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
            expected = json.loads(row["video_pts_s_json"])[len(frames)]
            if abs(timestamp - expected) > 1e-6:
                raise ValueError("Decoded native timestamp mismatch")
            frames.append(letterbox_rgb(image))
        pixels = torch.from_numpy(np.stack(frames)).permute(0, 3, 1, 2).contiguous()
        return {"pixels": pixels, "interval_id": row["interval_id"], "decode_seconds": time.perf_counter() - before}

    def close(self):
        for cap in self.captures.values():
            cap.release()
        self.captures.clear()

    def __del__(self):
        self.close()


def worker_init(_):
    torch.set_num_threads(1)
    cv2.setNumThreads(1)
