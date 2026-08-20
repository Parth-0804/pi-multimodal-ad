"""From-scratch spectral feature extraction for one HF minute-member.

Strategy is documented and justified in PLAN.md. Summary: Welch PSD per
channel -> 32 log-spaced band-energy features (log1p-compressed) + 3
broadband time-domain stats (RMS, crest factor, spectral centroid) per
channel, for Accel 1 and Accel 2, plus 2 missingness flags = 72 features.
Uses numpy/scipy only (standard libraries) -- no pi_multimodal_ad imports.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import h5py
import numpy as np
from scipy.signal import welch

SAMPLE_RATE_HZ = 102_400.0  # confirmed from wf_increment in Phase 0; verified per-member below, not assumed blindly
N_BANDS = 32
BAND_EDGES_HZ = np.logspace(np.log10(20.0), np.log10(SAMPLE_RATE_HZ / 2), N_BANDS + 1)
CHANNEL_NAMES = ("Accel 1", "Accel 2")
STAT_NAMES = ("rms", "crest_factor", "spectral_centroid_hz")
WELCH_NPERSEG = 8192
WELCH_NOVERLAP = 4096

FEATURE_COLUMNS: list[str] = []
for _channel in CHANNEL_NAMES:
    _tag = _channel.replace(" ", "").lower()
    for _band_index in range(N_BANDS):
        FEATURE_COLUMNS.append(f"{_tag}_band{_band_index:02d}_log1p_energy")
    for _stat in STAT_NAMES:
        FEATURE_COLUMNS.append(f"{_tag}_{_stat}")
for _channel in CHANNEL_NAMES:
    FEATURE_COLUMNS.append(f"{_channel.replace(' ', '').lower()}_missing")
assert len(FEATURE_COLUMNS) == 2 * (N_BANDS + len(STAT_NAMES)) + 2 == 72


class VibrationReadError(RuntimeError):
    """A channel could not be read/decoded from an otherwise-open HDF5 file."""


def parse_wf_start_time(raw: bytes | str | None) -> datetime | None:
    """Parse only an explicit UTC ('...Z') timestamp; never infer a timezone."""
    if raw is None:
        return None
    text = raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)
    text = text.strip()
    if not text.endswith(("Z", "z")):
        return None
    normalized = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class ChannelFeatures:
    band_log1p_energy: np.ndarray  # (N_BANDS,)
    rms: float
    crest_factor: float
    spectral_centroid_hz: float


def _welch_psd(signal: np.ndarray, fs: float) -> tuple[np.ndarray, np.ndarray]:
    nperseg = min(WELCH_NPERSEG, len(signal))
    if nperseg < 16:
        raise VibrationReadError(
            f"signal too short for spectral estimation ({len(signal)} samples)"
        )
    noverlap = min(WELCH_NOVERLAP, nperseg // 2)
    freqs, psd = welch(
        signal, fs=fs, window="hann", nperseg=nperseg, noverlap=noverlap,
        detrend="constant", scaling="density",
    )
    return freqs, psd


def extract_channel_features(signal: np.ndarray, fs: float) -> ChannelFeatures:
    if signal.ndim != 1 or signal.size == 0:
        raise VibrationReadError("expected a non-empty 1-D signal")
    signal = signal.astype(np.float64, copy=False)

    freqs, psd = _welch_psd(signal, fs)
    band_energy = np.zeros(N_BANDS, dtype=np.float64)
    for index in range(N_BANDS):
        low, high = BAND_EDGES_HZ[index], BAND_EDGES_HZ[index + 1]
        in_band = (freqs >= low) & (freqs < high)
        band_energy[index] = float(psd[in_band].sum()) if in_band.any() else 0.0
    band_log1p_energy = np.log1p(band_energy)

    rms = float(np.sqrt(np.mean(np.square(signal))))
    peak = float(np.max(np.abs(signal)))
    crest_factor = peak / rms if rms > 0 else 0.0
    total_power = float(psd.sum())
    spectral_centroid_hz = (
        float(np.sum(freqs * psd) / total_power) if total_power > 0 else 0.0
    )

    return ChannelFeatures(
        band_log1p_energy=band_log1p_energy,
        rms=rms,
        crest_factor=crest_factor,
        spectral_centroid_hz=spectral_centroid_hz,
    )


@dataclass(frozen=True, slots=True)
class MemberResult:
    feature_row: dict[str, float] | None  # None if wf_start_time missing
    wf_start_time: datetime | None
    duration_seconds: dict[str, float]  # per channel, for the data summary
    sample_count: dict[str, int]
    sample_rate_hz: dict[str, float]
    channel_errors: dict[str, str]  # channel -> error message, empty if none
    exclusion_reason: str | None  # set (and feature_row=None) if the whole member is unusable


def extract_member_features(hdf5_path: Path) -> MemberResult:
    """Open one materialized HDF5 minute-member and compute its 72-dim feature row.

    A missing/unreadable channel is recorded as a missingness flag + median
    imputation happens later (train-only, in train.py) -- never invented
    here. A member with no parseable wf_start_time on any channel is
    excluded entirely (cannot be placed in a chronological sequence),
    exactly mirroring the LF baseline's own timestamp-exclusion principle,
    reimplemented independently.
    """
    channel_errors: dict[str, str] = {}
    per_channel: dict[str, ChannelFeatures | None] = {}
    durations: dict[str, float] = {}
    sample_counts: dict[str, int] = {}
    sample_rates: dict[str, float] = {}
    wf_start_time: datetime | None = None

    with h5py.File(hdf5_path, "r") as handle:
        vibration = handle.get("Vibration")
        if vibration is None:
            return MemberResult(
                feature_row=None, wf_start_time=None, duration_seconds={},
                sample_count={}, sample_rate_hz={}, channel_errors={},
                exclusion_reason="no_vibration_group",
            )
        for channel in CHANNEL_NAMES:
            dataset = vibration.get(channel)
            if dataset is None:
                channel_errors[channel] = "dataset_absent"
                per_channel[channel] = None
                continue
            try:
                wf_increment = float(dataset.attrs["wf_increment"])
                fs = 1.0 / wf_increment
                signal = dataset[()]
                sample_counts[channel] = int(signal.shape[0])
                sample_rates[channel] = fs
                durations[channel] = signal.shape[0] * wf_increment
                if wf_start_time is None:
                    wf_start_time = parse_wf_start_time(
                        dataset.attrs.get("wf_start_time")
                    )
                per_channel[channel] = extract_channel_features(signal, fs)
            except (KeyError, ValueError, VibrationReadError) as exc:
                channel_errors[channel] = f"{type(exc).__name__}: {exc}"
                per_channel[channel] = None

    if wf_start_time is None:
        return MemberResult(
            feature_row=None, wf_start_time=None, duration_seconds=durations,
            sample_count=sample_counts, sample_rate_hz=sample_rates,
            channel_errors=channel_errors, exclusion_reason="no_verified_utc_timestamp",
        )
    if all(value is None for value in per_channel.values()):
        return MemberResult(
            feature_row=None, wf_start_time=wf_start_time, duration_seconds=durations,
            sample_count=sample_counts, sample_rate_hz=sample_rates,
            channel_errors=channel_errors, exclusion_reason="both_channels_unreadable",
        )

    row: dict[str, float] = {}
    for channel in CHANNEL_NAMES:
        tag = channel.replace(" ", "").lower()
        features = per_channel[channel]
        missing = features is None
        if features is None:
            for band_index in range(N_BANDS):
                row[f"{tag}_band{band_index:02d}_log1p_energy"] = np.nan
            for stat in STAT_NAMES:
                row[f"{tag}_{stat}"] = np.nan
        else:
            for band_index in range(N_BANDS):
                row[f"{tag}_band{band_index:02d}_log1p_energy"] = float(
                    features.band_log1p_energy[band_index]
                )
            row[f"{tag}_rms"] = features.rms
            row[f"{tag}_crest_factor"] = features.crest_factor
            row[f"{tag}_spectral_centroid_hz"] = features.spectral_centroid_hz
        row[f"{tag}_missing"] = 1.0 if missing else 0.0

    return MemberResult(
        feature_row=row, wf_start_time=wf_start_time, duration_seconds=durations,
        sample_count=sample_counts, sample_rate_hz=sample_rates,
        channel_errors=channel_errors, exclusion_reason=None,
    )
