"""Label-independent interval alignment; no extrapolation or future samples."""
import re
import numpy as np


def action_from_text(text):
    match = re.match(r'^\s*(pick(?:ing)?(?:\s+up)?|insert(?:ing)?|remov(?:e|ing)|plac(?:e|ing))\b', text, re.I)
    if not match:
        return 'other'
    word = match.group(1).lower()
    return next(action for prefix, action in [('pick', 'pick'), ('insert', 'insert'), ('remov', 'remove'), ('plac', 'place')] if word.startswith(prefix))


def timestamps_1d(values):
    x = np.asarray(values, dtype=np.float64)
    if x.ndim == 2:
        if x.shape[1] == 0 or not np.allclose(x, x[:, :1], rtol=0, atol=1e-9, equal_nan=True):
            raise ValueError('Per-channel timestamps differ; cannot collapse them')
        x = x[:, 0]
    if x.ndim != 1:
        raise ValueError('Unsupported timestamp shape')
    if not np.all(np.isfinite(x)) or np.any(np.diff(x) <= 0):
        raise ValueError('Timestamps must be finite and strictly increasing')
    return x


def interval_indices(timestamps, start, end):
    if not np.isfinite(start + end) or end <= start:
        raise ValueError('Invalid segment interval')
    t = timestamps_1d(timestamps)
    return np.flatnonzero((t >= start) & (t <= end))


def interval_coverage(timestamps, start, end, gap_multiple=5):
    t = timestamps_1d(timestamps)
    indices = interval_indices(t, start, end)
    local = t[indices]
    if len(local) < 2:
        return {'count': len(local), 'coverage': 0.0, 'max_gap': None}
    # Estimate native rate from the stream, without using labels or test-fitted scaling.
    dt = float(np.median(np.diff(t)))
    gaps = np.diff(local)
    covered = float(gaps[gaps <= gap_multiple * dt].sum())
    return {'count': len(local), 'coverage': min(1.0, covered / (end - start)), 'max_gap': float(gaps.max())}


def resample_progress(timestamps, values, start, end, positions=512, gap_multiple=5):
    t = timestamps_1d(timestamps)
    x = np.asarray(values, dtype=float)
    if x.ndim == 1:
        x = x[:, None]
    if x.ndim != 2 or len(t) != len(x):
        raise ValueError('Sensor data/timestamp shape mismatch')
    indices = interval_indices(t, start, end)
    grid = np.linspace(start, end, positions)
    result = np.full((positions, x.shape[1]), np.nan)
    native_dt = np.median(np.diff(t)) if len(t) > 1 else 0
    for channel in range(x.shape[1]):
        valid = indices[np.isfinite(x[indices, channel])]
        if len(valid) < 2:
            continue
        tv = t[valid]
        y = np.interp(grid, tv, x[valid, channel], left=np.nan, right=np.nan)
        right = np.searchsorted(tv, grid, side='left')
        interior = (right > 0) & (right < len(tv))
        slots = np.flatnonzero(interior)
        r = right[interior]
        long_gap = (tv[r] - tv[r - 1] > gap_multiple * native_dt) & (grid[interior] != tv[r])
        y[slots[long_gap]] = np.nan
        result[:, channel] = y
    return result


def sensor_quality(timestamps, values, start, end, positions=512, gap_multiple=5):
    t = timestamps_1d(timestamps)
    x = np.asarray(values, dtype=float)
    if x.ndim == 1:
        x = x[:, None]
    if x.ndim != 2 or len(t) != len(x):
        raise ValueError('Sensor shape mismatch')
    indices = interval_indices(t, start, end)
    local = x[indices]
    valid = np.isfinite(local)
    missing = int((~valid.any(axis=0)).sum()) if len(local) else x.shape[1]
    constant = 0
    outliers = 0
    denominator = 0
    for channel in local.T:
        v = channel[np.isfinite(channel)]
        if len(v):
            constant += int(np.ptp(v) <= 1e-12)
            median = np.median(v)
            mad = np.median(np.abs(v - median))
            if mad > 0:
                outliers += int((np.abs(v - median) > 10 * 1.4826 * mad).sum())
                denominator += len(v)
    resampled = resample_progress(t, x, start, end, positions, gap_multiple)
    grid = np.linspace(start, end, positions)
    # Fraction of grid locations not exactly observed; descriptive, not a validity score.
    exact = np.zeros(positions, bool)
    if len(indices):
        local_t = t[indices]
        right = np.clip(np.searchsorted(local_t, grid), 0, len(local_t) - 1)
        left = np.maximum(right - 1, 0)
        exact = np.isclose(grid, local_t[right], rtol=0, atol=1e-9) | np.isclose(grid, local_t[left], rtol=0, atol=1e-9)
    return {**interval_coverage(t, start, end, gap_multiple), 'channels': x.shape[1], 'finite_fraction': float(valid.mean()) if valid.size else 0.0, 'missing_channels': missing, 'constant_channels': constant, 'within_segment_mad_outlier_fraction': outliers / denominator if denominator else None, 'interpolation_fraction': float((~exact).mean()), 'resampled_finite_fraction': float(np.isfinite(resampled).mean()), 'clipping_fraction': None}
