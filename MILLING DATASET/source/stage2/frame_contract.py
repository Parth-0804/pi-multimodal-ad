#!/usr/bin/env python3
"""Verify 16 unique native frames per guarded interval using decoded presentation times."""
import argparse
import hashlib
import json
from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

from audit_sensors import dump, csv_output
from probe_media import corrected_frame

cv2.setNumThreads(1)


def select_frames(pts, start, end, offset, uncertainty, support, count=16):
    reasons = []
    if len(pts) < count or np.any(np.diff(pts) <= 0):
        return {"accepted": False, "reasons": ["invalid_or_insufficient_native_pts"]}
    step = float(np.median(np.diff(pts)))
    guard = uncertainty + step/2
    a, b = start+guard, end-guard
    if b <= a:
        return {"accepted": False, "reasons": ["interval_too_short_after_timing_guard"]}
    if not any(lo <= a and b <= hi for lo, hi in support):
        reasons.append("outside_validated_audio_support")
    targets = a+(np.arange(count)+.5)/count*(b-a)+offset
    indices = np.searchsorted(pts, targets)
    indices = np.clip(indices, 0, len(pts)-1)
    previous = np.maximum(indices-1, 0)
    use_previous = np.abs(pts[previous]-targets) < np.abs(pts[indices]-targets)
    indices = np.where(use_previous, previous, indices)
    actual = pts[indices]; sensor_pts = actual-offset
    if targets[0] < pts[0] or targets[-1] > pts[-1]: reasons.append("video_does_not_cover_interval")
    if len(np.unique(indices)) != count: reasons.append("fewer_than_16_distinct_native_frames")
    if np.any(sensor_pts-uncertainty < start) or np.any(sensor_pts+uncertainty >= end):
        reasons.append("frame_uncertainty_crosses_label_boundary")
    if np.max(np.abs(actual-targets)) > step*.55: reasons.append("native_pts_gap_near_selected_frame")
    return {"accepted": not reasons, "reasons": reasons, "guard_s": guard, "indices": indices.tolist(),
            "target_video_pts_s": targets.tolist(), "video_pts_s": actual.tolist(), "sensor_pts_s": sensor_pts.tolist(),
            "temporal_coverage_fraction": float((sensor_pts[-1]-sensor_pts[0])/(end-start)),
            "max_nearest_frame_error_s": float(np.max(np.abs(actual-targets)))}


def main(run):
    config = json.loads((run / "config/resolved_config.json").read_text()); root = Path(config["data_root"])
    mappings = json.loads((run / "manifests/video_alignment_final.json").read_text())
    media = json.loads((run / "manifests/media_probe.json").read_text())
    results, native_audit, frame_rows = [], {}, []
    atlas_dir = run / "figures/visibility_atlas"; atlas_dir.mkdir(exist_ok=False)
    for group in config["selected_groups"]:
        key = group.replace("/", "_"); labels = pd.read_csv(root / group / "label.csv"); mapping = mappings[group]
        if not mapping.get("accepted"):
            for i, label in labels.iterrows():
                results.append({"group_id": group, "source_row": i+2, "interval_id": f"{group}/row{i+2}", "native_label": int(label.label),
                                "start_s": label.start, "end_s": label.end, "accepted": False, "reasons": [mapping["reason"]]})
            continue
        video = Path(media[group]["video"]); cap = cv2.VideoCapture(str(video), cv2.CAP_FFMPEG, [cv2.CAP_PROP_N_THREADS,1])
        pts, repeat_count, last_hash = [], 0, None
        while True:
            ok, frame = cap.read()
            if not ok: break
            pts.append(cap.get(cv2.CAP_PROP_POS_MSEC)/1000)
            digest = hashlib.sha256(frame.tobytes()).digest()
            repeat_count += digest == last_hash; last_hash = digest
        pts = np.asarray(pts)
        native_audit[group] = {"decoded_frames": len(pts), "header_frames": media[group]["frame_count_header"],
                               "first_pts_s": float(pts[0]), "last_pts_s": float(pts[-1]),
                               "strictly_increasing_pts": bool(np.all(np.diff(pts)>0)), "median_step_s": float(np.median(np.diff(pts))),
                               "min_step_s": float(np.min(np.diff(pts))), "max_step_s": float(np.max(np.diff(pts))),
                               "consecutive_identical_decoded_frames": int(repeat_count)}
        np.save(run / "cache" / (key+"_native_pts.npy"), pts)
        candidates, required_indices = [], set()
        for i, label in labels.iterrows():
            record = {"group_id": group, "source_row": i+2, "interval_id": f"{group}/row{i+2}",
                      "native_label": int(label.label), "start_s": label.start, "end_s": label.end,
                      **select_frames(pts, label.start, label.end, mapping["offset_s"], mapping["uncertainty_s"], mapping["support_sensor_s"])}
            candidates.append(record)
            if record["accepted"]: required_indices.update(record["indices"])
        # Decode forward once more; do not rely on approximate random seeking for the final contract.
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0); images, hashes = {}, {}
        index = 0; sar_num, sar_den = media[group]["sample_aspect_ratio"]
        while True:
            ok, frame = cap.read()
            if not ok: break
            if index in required_indices:
                hashes[index] = hashlib.sha256(frame.tobytes()).hexdigest()
                image = corrected_frame(frame, sar_num, sar_den)
                images[index] = Image.fromarray(image).resize((90,160))
            index += 1
        cap.release()
        accepted = []
        for record in candidates:
            if record["accepted"]:
                unique_hashes = {hashes[j] for j in record["indices"] if j in hashes}
                record["unique_decoded_content"] = len(unique_hashes)
                if len(unique_hashes) != 16:
                    record["accepted"] = False; record["reasons"].append("repeated_or_missing_decoded_frame_content")
                else:
                    accepted.append(record)
                    for n, (j, tv, ts, target) in enumerate(zip(record["indices"],record["video_pts_s"],record["sensor_pts_s"],record["target_video_pts_s"])):
                        frame_rows.append({"interval_id": record["interval_id"], "group_id": group, "source_row": record["source_row"],
                                           "frame_order": n, "native_frame_index": j, "video_pts_s": tv, "mapped_sensor_time_s": ts,
                                           "target_video_pts_s": target, "alignment_uncertainty_s": mapping["uncertainty_s"],
                                           "decoded_frame_sha256": hashes[j], "native_label": record["native_label"]})
            results.append(record)
        for page, start_index in enumerate(range(0,len(accepted),8)):
            records = accepted[start_index:start_index+8]
            canvas = Image.new("RGB", (1660, 80+len(records)*200), "white"); draw = ImageDraw.Draw(canvas)
            draw.text((10,10), group+" — ALL 16 frames in each interval; pixels corrected to display aspect ratio", fill="black")
            draw.text((10,30), "Timing accepted; visual eligibility still requires explicit review. No training performed.",fill="black")
            for row_index, record in enumerate(records):
                y = 65+row_index*200
                draw.text((5,y+20),f"row {record['source_row']}\ny={record['native_label']}\n{record['start_s']:.3f}\n..{record['end_s']:.3f}s",fill="black")
                for order, (j, tv) in enumerate(zip(record["indices"],record["video_pts_s"])):
                    x = 130+order*95; canvas.paste(images[j], (x,y))
                    draw.text((x,y+162),f"{tv:.2f}s",fill="black")
            canvas.save(atlas_dir/(key+f"_page{page+1:02d}.jpg"),quality=90)
        print(group, "decoded",len(pts),"frame-contract accepted",len(accepted),"of",len(labels),flush=True)
    dump(run / "manifests/frame_contract.json", results)
    dump(run / "manifests/native_video_audit.json", native_audit)
    csv_output(run / "manifests/selected_frame_manifest.csv", frame_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--run",type=Path,required=True);main(parser.parse_args().run)
