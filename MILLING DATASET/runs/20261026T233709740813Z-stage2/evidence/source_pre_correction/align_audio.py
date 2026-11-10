#!/usr/bin/env python3
"""Calibrate video clocks using ambient audio, withholding nonoverlapping windows."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
from scipy import signal

from audit_sensors import dump, csv_output, new_accumulator, accumulate, finalize
from probe_media import envelope, lag_correlations


def merged_support(windows):
    merged = []
    for a, b in sorted(windows):
        if merged and a <= merged[-1][1] + 1e-8:
            merged[-1][1] = max(b, merged[-1][1])
        else:
            merged.append([a, b])
    return merged


def estimate_mapping(video_features, reference_features, protocol):
    # Fixed 800–1800 Hz band; the function has no label/interval inputs.
    vf, rf = video_features[2:3], reference_features[2:3]
    lags, scores = lag_correlations(vf, rf)
    best = int(np.argmax(scores)); coarse = int(lags[best])
    window = round(protocol["local_window_s"]*100)
    stride = round(protocol["anchor_stride_s"]*100)
    radius = round(protocol["local_lag_search_half_width_s"]*100)
    anchors = []
    for index, a in enumerate(range(0, rf.shape[1]-window+1, stride)):
        b = a+window; candidate_lags = np.arange(coarse-radius, coarse+radius+1)
        correlations = []
        for lag in candidate_lags:
            if a+lag < 0 or b+lag > vf.shape[1]:
                correlations.append(-np.inf)
            else:
                x, y = vf[0, a+lag:b+lag], rf[0, a:b]
                correlations.append(float(np.corrcoef(x, y)[0, 1]) if x.std() and y.std() else -np.inf)
        best_local = int(np.argmax(correlations))
        score = correlations[best_local]
        anchors.append({"anchor_index": index, "start_sensor_s": a/100, "end_sensor_s": b/100,
                        "center_sensor_s": (a+b)/200, "role": "calibration" if index % 2 == 0 else "validation",
                        "video_minus_sensor_s": float(candidate_lags[best_local]/100) if np.isfinite(score) else None,
                        "correlation": score if np.isfinite(score) else None,
                        "high_correlation": bool(np.isfinite(score) and score >= protocol["local_min_correlation"])})
    calibration = [a for a in anchors if a["role"] == "calibration" and a["high_correlation"]]
    if not calibration:
        return {"accepted": False, "reason": "no_calibration_anchors", "anchors": anchors}
    initial = float(np.median([a["video_minus_sensor_s"] for a in calibration]))
    calibration = [a for a in calibration if abs(a["video_minus_sensor_s"]-initial) <= protocol["inlier_tolerance_s"]]
    offset = float(np.median([a["video_minus_sensor_s"] for a in calibration]))
    for anchor in anchors:
        anchor["accepted"] = bool(anchor["high_correlation"] and abs(anchor["video_minus_sensor_s"]-offset) <= protocol["inlier_tolerance_s"])
        anchor["residual_s"] = anchor["video_minus_sensor_s"]-offset if anchor["video_minus_sensor_s"] is not None else None
    validation = [a for a in anchors if a["role"] == "validation" and a["accepted"]]
    used = [a for a in anchors if a["accepted"]]
    span = max(a["center_sensor_s"] for a in used)-min(a["center_sensor_s"] for a in used) if used else 0.
    accepted = (len(calibration) >= protocol["min_calibration_anchors"] and
                len(validation) >= protocol["min_validation_anchors"] and span >= protocol["min_anchor_span_s"])
    residual = max([abs(a["residual_s"]) for a in validation], default=float("inf"))
    return {"accepted": bool(accepted), "reason": "accepted_with_bounded_support" if accepted else "insufficient_validation_support",
            "offset_s": offset, "uncertainty_s": max(.08, residual+.04),
            "calibration_anchors": len(calibration), "validation_anchors": len(validation), "anchor_span_s": span,
            "max_validation_residual_s": residual, "support_sensor_s": merged_support([(a["start_sensor_s"], a["end_sensor_s"]) for a in used]),
            "coarse_offset_s": coarse/100, "coarse_correlation": float(scores[best]), "anchors": anchors}


def main(run):
    config = json.loads((run / "config/resolved_config.json").read_text())
    protocol = json.loads((run / "config/alignment_protocol_final.json").read_text())
    root = Path(config["data_root"]); mappings, anchor_rows, extra_audio = {}, [], []
    for group in config["selected_groups"]:
        key = group.replace("/", "_"); folder = root / group
        if not list(folder.glob("*.mp4")):
            mappings[group] = {"accepted": False, "reason": "no_video_provided"}; continue
        cache = np.load(run / "cache" / (key+"_audio.npz"))
        wav = next(folder.glob("*_s2.wav")); audio, fs = sf.read(wav, dtype="float32")
        clipped = float(np.mean(np.abs(audio) >= 32767/32768))
        state = new_accumulator(); accumulate(state, audio.astype(float))
        extra_audio.append({"group_id": group, "path": str(wav), "sample_rate": fs, "frames": len(audio),
                            "duration_s": len(audio)/fs, "channels": 1 if audio.ndim == 1 else audio.shape[1],
                            "clipped_sample_fraction": clipped, "sample_stats": finalize(state)})
        reference = signal.resample_poly(audio, 4000, fs); rf = envelope(reference); vf = cache["video_features"]
        mapping = estimate_mapping(vf, rf, protocol); mapping["reference"] = "audio_s2"; mappings[group] = mapping
        anchor_rows.extend({"group_id": group, **a} for a in mapping["anchors"])
        np.savez_compressed(run / "cache" / (key+"_alignment_audio.npz"), reference_audio=reference,
                            video_audio=cache["video_audio"], reference_features=rf, video_features=vf)
        fig, axs = plt.subplots(3, 1, figsize=(13, 9), layout="constrained")
        offset = mapping.get("offset_s", 0.)
        axs[0].plot(np.arange(rf.shape[1])/100+.032, rf[2], label="ambient S2", lw=.6)
        axs[0].plot(np.arange(vf.shape[1])/100+.032-offset, vf[2], label="video AAC, mapped to sensor clock", lw=.6, alpha=.7)
        axs[0].set(ylabel="800–1800 Hz log energy", xlabel="Sensor time (s)"); axs[0].legend()
        for role, marker in (("calibration", "o"), ("validation", "s")):
            anchors = [a for a in mapping["anchors"] if a["role"] == role and a["correlation"] is not None]
            axs[1].scatter([a["center_sensor_s"] for a in anchors], [a["video_minus_sensor_s"] for a in anchors],
                           c=["tab:green" if a["accepted"] else "tab:red" for a in anchors], marker=marker, label=role)
            axs[2].scatter([a["center_sensor_s"] for a in anchors], [a["correlation"] for a in anchors], marker=marker, label=role)
        axs[1].axhline(offset, color="black", lw=1); axs[1].set(ylabel="Video − sensor offset (s)", xlabel="Sensor time (s)"); axs[1].legend()
        axs[2].axhline(.75, color="tab:red", ls="--"); axs[2].set(ylabel="Local Pearson r", xlabel="Sensor time (s)", ylim=(-.3,1.05)); axs[2].legend()
        fig.suptitle(f"{group}: label-blind audio alignment; offset {offset:+.3f}s; accepted={mapping['accepted']}")
        fig.savefig(run / "figures" / (key+"_audio_alignment.png"), dpi=140); plt.close(fig)
        print(group, json.dumps({k: v for k, v in mapping.items() if k != "anchors"}), flush=True)
    dump(run / "manifests/audio_alignment.json", mappings)
    dump(run / "manifests/additional_audio_audit.json", extra_audio)
    csv_output(run / "manifests/audio_alignment_anchors.csv", anchor_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--run", type=Path, required=True)
    main(parser.parse_args().run)
