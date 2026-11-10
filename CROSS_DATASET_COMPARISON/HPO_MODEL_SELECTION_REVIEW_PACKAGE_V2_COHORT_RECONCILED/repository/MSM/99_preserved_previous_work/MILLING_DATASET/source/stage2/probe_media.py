#!/usr/bin/env python3
"""Inspect native video clocks and shared audio; no labels enter alignment."""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
from scipy import signal

sys.path.insert(0, str(Path(__file__).parents[2] / ".tools"))
import imageio_ffmpeg

cv2.setNumThreads(1)


def envelope(audio, sample_rate=4000, hop=40):
    """Log band energy at 100 Hz; independent of label intervals/classes."""
    _, _, spec = signal.stft(audio, fs=sample_rate, nperseg=256, noverlap=256-hop,
                             boundary=None, padded=False)
    freq = np.fft.rfftfreq(256, 1 / sample_rate)
    bands = []
    for lo, hi in ((100, 350), (350, 800), (800, 1800)):
        power = np.mean(np.abs(spec[(freq >= lo) & (freq < hi)])**2, axis=0)
        bands.append(np.log(np.maximum(power, 1e-12)))
    return np.asarray(bands, dtype=np.float64)


def lag_correlations(video_features, reference_features, min_fraction=0.7):
    """Mean overlap-normalized Pearson correlation over independent audio bands."""
    n, m = video_features.shape[1], reference_features.shape[1]
    lags = signal.correlation_lags(n, m, mode="full")
    count = signal.correlate(np.ones(n), np.ones(m), method="fft")
    correlations = []
    for x, y in zip(video_features, reference_features):
        xy = signal.correlate(x, y, method="fft")
        sx = signal.correlate(x, np.ones(m), method="fft")
        sy = signal.correlate(np.ones(n), y, method="fft")
        sxx = signal.correlate(x*x, np.ones(m), method="fft")
        syy = signal.correlate(np.ones(n), y*y, method="fft")
        denom = np.sqrt(np.maximum(sxx-sx*sx/np.maximum(count, 1), 0) *
                        np.maximum(syy-sy*sy/np.maximum(count, 1), 0))
        correlations.append((xy-sx*sy/np.maximum(count, 1))/np.maximum(denom, 1e-12))
    score = np.mean(correlations, axis=0)
    score[count < min(n, m)*min_fraction] = -np.inf
    return lags, score


def corrected_frame(frame, sar_num=3, sar_den=8):
    return cv2.cvtColor(cv2.resize(frame, (round(frame.shape[1]*sar_num/sar_den), frame.shape[0])), cv2.COLOR_BGR2RGB)


def main(run):
    config = json.loads((run / "config/resolved_config.json").read_text())
    root = Path(config["data_root"])
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    summaries = {}
    for group in config["selected_groups"]:
        folder = root / group
        video = next(folder.glob("*.mp4"), None)
        if video is None:
            summaries[group] = {"video": None}
            continue
        key = group.replace("/", "_")
        header = subprocess.run([ffmpeg, "-hide_banner", "-i", str(video)], capture_output=True, text=True).stderr
        (run / "evidence" / (key + "_media_header.txt")).write_text(header)
        command = [ffmpeg, "-nostdin", "-v", "error", "-threads", "1", "-i", str(video),
                   "-map", "0:a:0", "-vn", "-ac", "1", "-ar", "4000", "-f", "f32le", "pipe:1"]
        result = subprocess.run(command, capture_output=True, check=True)
        video_audio = np.frombuffer(result.stdout, dtype="<f4").copy()
        wav = next(folder.glob("*_s0.wav"))
        reference_audio, fs = sf.read(wav, dtype="float32")
        if reference_audio.ndim > 1:
            reference_audio = reference_audio.mean(axis=1)
        reference_audio = signal.resample_poly(reference_audio, 4000, fs)
        vf, rf = envelope(video_audio), envelope(reference_audio)
        lags, scores = lag_correlations(vf, rf)
        best = int(np.argmax(scores))
        shift = float(lags[best] / 100)
        alternate = scores.copy()
        alternate[np.abs(lags-lags[best]) < 100] = -np.inf
        second = int(np.argmax(alternate))
        anchors = []
        # Locations are defined only by reference recording length, never cutting/anomaly labels.
        for center in np.linspace(0.15, 0.85, 7) * (rf.shape[1]/100):
            half = min(6., rf.shape[1]/100/12)
            a = max(0, int((center-half)*100)); b = min(rf.shape[1], int((center+half)*100))
            candidates = np.arange(round(shift*100)-50, round(shift*100)+51)
            values = []
            for lag in candidates:
                if a+lag < 0 or b+lag > vf.shape[1]:
                    values.append(-np.inf)
                else:
                    values.append(float(np.mean([np.corrcoef(x[a+lag:b+lag], y[a:b])[0, 1] for x, y in zip(vf, rf)])))
            idx = int(np.argmax(values))
            anchors.append({"reference_center_s": float(center), "video_minus_sensor_s": float(candidates[idx]/100),
                            "correlation": values[idx]})
        np.savez_compressed(run / "cache" / (key + "_audio.npz"), video_audio=video_audio, reference_audio=reference_audio,
                            video_features=vf, reference_features=rf, lags=lags, scores=scores)
        cap = cv2.VideoCapture(str(video), cv2.CAP_FFMPEG, [cv2.CAP_PROP_N_THREADS, 1])
        fps = cap.get(cv2.CAP_PROP_FPS); count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        sar_num, sar_den = cap.get(cv2.CAP_PROP_SAR_NUM), cap.get(cv2.CAP_PROP_SAR_DEN)
        fig, axs = plt.subplots(1, 8, figsize=(16, 4.5), layout="constrained")
        overview_pts = []
        for ax, frame_index in zip(axs, np.linspace(0, count-1, 8).round().astype(int)):
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(frame_index)); ok, frame = cap.read()
            timestamp = cap.get(cv2.CAP_PROP_POS_MSEC)/1000
            if ok:
                ax.imshow(corrected_frame(frame, sar_num, sar_den))
            ax.set_title(f"v={timestamp:.2f}s\nframe {frame_index}", fontsize=8); ax.axis("off")
            overview_pts.append(timestamp)
        fig.suptitle(group + " — actual video overview (sample aspect ratio corrected)")
        fig.savefig(run / "figures" / (key + "_overview.jpg"), dpi=130); plt.close(fig)
        cap.release()
        summary = {"video": str(video), "reference_wav": str(wav), "fps": fps, "frame_count_header": count,
                   "video_duration_s": count/fps, "sensor_audio_duration_s": len(reference_audio)/4000,
                   "embedded_audio_duration_s": len(video_audio)/4000, "sample_aspect_ratio": [sar_num, sar_den],
                   "coarse_video_minus_sensor_s": shift, "correlation": float(scores[best]),
                   "alternative_lag_s": float(lags[second]/100), "alternative_correlation": float(scores[second]),
                   "anchors": anchors, "audio_decode_argv": command, "overview_pts_s": overview_pts}
        summaries[group] = summary
        print(group, json.dumps({k: summary[k] for k in ("video_duration_s", "sensor_audio_duration_s", "coarse_video_minus_sensor_s", "correlation", "anchors")}), flush=True)
    with (run / "manifests/media_probe.json").open("x") as output:
        json.dump(summaries, output, indent=2); output.write("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    main(parser.parse_args().run)
