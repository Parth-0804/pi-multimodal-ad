    #!/usr/bin/env python3
"""
PHM North America 2026 – EXP-A Advanced EDA
===========================================

Dataset scope
-------------
High-frequency:
    EXP-A Run-1 -> early lifecycle
    EXP-A Run-3 -> intermediate lifecycle
    EXP-A Run-5 -> late lifecycle

Low-frequency / CIs:
    EXP-A Run-1 ... Run-5 (cheap enough to keep full lifecycle)

Images:
    EXP-A 0h / Break-In / Run-1 ... Run-5 if present

Expected project path
---------------------
/home/student/Master_Thesis_WS/pi-multimodal-ad/

Expected dataset path
---------------------
/home/student/Master_Thesis_WS/pi-multimodal-ad/gtc-data-experiment/

Confirmed HDF5 schema
---------------------
/Vibration/Accel 1         -> axial vibration
/Vibration/Accel 2         -> radial vibration
/Context/PAU Speed         -> RPM / speed
/Context/PAU Torque        -> torque
/Context/Temperature       -> temperature

Condition indicators:
    Run-1 may use:
        /CI/FM4
        /CI/NA4
        /CI/M6A
        /CI/ALR

    Later runs may use:
        /CI_4s/FM4
        /CI_4s/NA4
        /CI_4s/M6A
        /CI_4s/ALR

Important scientific guardrail
------------------------------
Run-1 / Run-3 / Run-5 are called early / intermediate / late lifecycle.
Do NOT automatically interpret them as healthy / damaged / failed.

Usage
-----
1) Inspect structure:
    python eda_phm2026.py --mode inspect

2) Process low-frequency + CI:
    python eda_phm2026.py --mode lf

3) Process photos:
    python eda_phm2026.py --mode photos

4) Smoke-test HF (3 HDF5 files per selected run):
    python eda_phm2026.py --mode hf --max-files-per-run 3

5) Full HF processing:
    python eda_phm2026.py --mode hf

6) Generate advanced tables/figures:
    python eda_phm2026.py --mode plots

7) Everything:
    python eda_phm2026.py --mode all
"""

from __future__ import annotations

import argparse
import io
import json
import math
import re
import shutil
import tempfile
import warnings
import zipfile
from pathlib import Path
from typing import Any, Iterable, Sequence

import h5py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageOps
from scipy import signal, stats
from scipy.stats import wasserstein_distance
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import HuberRegressor
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore", category=RuntimeWarning)

# =============================================================================
# 1. PATHS / CONFIG
# =============================================================================

PROJECT_ROOT = Path("/home/student/Master_Thesis_WS/pi-multimodal-ad")
DATA_ROOT = PROJECT_ROOT / "gtc-data-experiment"
OUT_ROOT = PROJECT_ROOT / "eda_outputs"

TABLE_DIR = OUT_ROOT / "tables"
FIG_DIR = OUT_ROOT / "figures"
REPORT_DIR = OUT_ROOT / "reports"
CACHE_DIR = OUT_ROOT / "cache"
PHOTO_CACHE_DIR = CACHE_DIR / "photos"

SELECTED_HF_RUNS = [1, 3, 5]
RUN_STAGE = {
    1: "early",
    3: "intermediate",
    5: "late",
}

HF_ZIPS = {
    1: DATA_ROOT / "Exp-A_HDF5_Run-1.zip",
    3: DATA_ROOT / "Exp-A_HDF5_Run-3.zip",
    5: DATA_ROOT / "Exp-A_HDF5_Run-5.zip",
}

LF_OUTER_ZIP = (
    DATA_ROOT
    / "low-frequency (CIs + Oil + Environment)"
    / "Exp-A_HDF5_LF.zip"
)

CI_OUTER_ZIP = (
    DATA_ROOT
    / "low-frequency (CIs)"
    / "Exp-A_HDF5_CI.zip"
)

PHOTO_DIR = DATA_ROOT / "photos" / "EXP-A"

GEAR_TEETH = 28
DEFAULT_HF_FS = 102_400.0

# Bounded processing for huge vibration arrays.
MAX_STATS_SAMPLE_POINTS = 1_000_000
SPECTRAL_WINDOW_POINTS = 1_048_576       # 2^20 points
WELCH_NPERSEG = 65_536

GMF_RELATIVE_HALF_WIDTH = 0.05
GMF_MIN_HALF_WIDTH_HZ = 5.0

# Confirmed channel paths.
FIXED_PATHS = {
    "axial": "/Vibration/Accel 1",
    "radial": "/Vibration/Accel 2",
    "rpm": "/Context/PAU Speed",
    "torque": "/Context/PAU Torque",
    "temperature": "/Context/Temperature",
}

# CI paths vary by run; we resolve both variants.
CI_PATH_CANDIDATES = {
    "fm4": ["/CI/FM4", "/CI_4s/FM4"],
    "na4": ["/CI/NA4", "/CI_4s/NA4"],
    "m6a": ["/CI/M6A", "/CI_4s/M6A"],
    "alr": ["/CI/ALR", "/CI_4s/ALR"],
}

# =============================================================================
# 2. BASIC HELPERS
# =============================================================================

def ensure_dirs() -> None:
    for p in [
        OUT_ROOT,
        TABLE_DIR,
        FIG_DIR,
        REPORT_DIR,
        CACHE_DIR,
        PHOTO_CACHE_DIR,
    ]:
        p.mkdir(parents=True, exist_ok=True)


def save_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, default=str),
        encoding="utf-8",
    )


def human_bytes(value: int | float) -> str:
    value = float(value)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(value) < 1024:
            return f"{value:.2f} {unit}"
        value /= 1024
    return f"{value:.2f} PB"


def natural_key(text: str) -> list[Any]:
    return [
        int(token) if token.isdigit() else token.lower()
        for token in re.split(r"(\d+)", text)
    ]


def parse_run(text: str) -> int | None:
    m = re.search(r"run[-_\s]*(\d+)", text, flags=re.IGNORECASE)
    return int(m.group(1)) if m else None


def finite(x: np.ndarray | Sequence[float]) -> np.ndarray:
    arr = np.asarray(x, dtype=np.float64).ravel()
    return arr[np.isfinite(arr)]


def robust_median(x: np.ndarray | Sequence[float]) -> float:
    arr = finite(x)
    return float(np.median(arr)) if arr.size else np.nan


def get_h5_dataset(h5: h5py.File, path: str | None) -> h5py.Dataset | None:
    if not path:
        return None
    key = path.lstrip("/")
    if key in h5 and isinstance(h5[key], h5py.Dataset):
        return h5[key]
    return None


def find_h5_members(zf: zipfile.ZipFile) -> list[str]:
    extensions = (".h5", ".hdf5", ".hdf")
    return sorted(
        [
            name
            for name in zf.namelist()
            if not name.endswith("/")
            and name.lower().endswith(extensions)
        ],
        key=natural_key,
    )


def find_image_members(zf: zipfile.ZipFile) -> list[str]:
    extensions = (
        ".jpg", ".jpeg", ".png", ".bmp",
        ".tif", ".tiff", ".webp",
    )
    return sorted(
        [
            name
            for name in zf.namelist()
            if not name.endswith("/")
            and name.lower().endswith(extensions)
        ],
        key=natural_key,
    )


def extract_zip_member_to_temp(
    zf: zipfile.ZipFile,
    member: str,
    temp_dir: Path,
) -> Path:
    target = temp_dir / Path(member).name
    with zf.open(member) as src, target.open("wb") as dst:
        shutil.copyfileobj(src, dst, length=16 * 1024 * 1024)
    return target


def zip_inventory(path: Path) -> dict[str, Any]:
    info: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
    }

    if not path.exists():
        return info

    info["size_on_disk"] = path.stat().st_size
    info["size_on_disk_human"] = human_bytes(path.stat().st_size)

    try:
        with zipfile.ZipFile(path) as zf:
            members = [x for x in zf.infolist() if not x.is_dir()]
            info["member_count"] = len(members)
            info["hdf5_member_count"] = len(find_h5_members(zf))
            info["image_member_count"] = len(find_image_members(zf))
            info["nested_zip_count"] = sum(
                1 for x in members
                if x.filename.lower().endswith(".zip")
            )
            info["first_members"] = [
                x.filename for x in members[:20]
            ]
    except Exception as exc:
        info["error"] = repr(exc)

    return info


def bounded_stride_sample(
    ds: h5py.Dataset,
    max_points: int,
) -> np.ndarray:
    """Read a deterministic bounded sample without loading huge arrays."""
    if ds.size == 0:
        return np.array([], dtype=np.float64)

    if ds.ndim == 1:
        step = max(1, math.ceil(ds.shape[0] / max_points))
        return finite(ds[::step])

    if ds.size <= max_points:
        return finite(ds[...])

    # Generic fallback for multidimensional arrays.
    first_dim = ds.shape[0]
    points_per_row = max(1, int(np.prod(ds.shape[1:])))
    rows_needed = max(1, max_points // points_per_row)
    step = max(1, math.ceil(first_dim / rows_needed))
    return finite(ds[::step])


# =============================================================================
# 3. HDF5 STRUCTURE INSPECTION
# =============================================================================

def list_numeric_datasets(h5: h5py.File) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def visitor(name: str, obj: Any) -> None:
        if not isinstance(obj, h5py.Dataset):
            return
        try:
            numeric = np.issubdtype(obj.dtype, np.number)
        except Exception:
            numeric = False
        if not numeric:
            return

        attrs: dict[str, Any] = {}
        for key, value in obj.attrs.items():
            try:
                attrs[key] = np.asarray(value).tolist()
            except Exception:
                attrs[key] = str(value)

        rows.append({
            "path": "/" + name.lstrip("/"),
            "shape": [int(v) for v in obj.shape],
            "dtype": str(obj.dtype),
            "size": int(obj.size),
            "attrs": attrs,
        })

    h5.visititems(visitor)
    return sorted(rows, key=lambda r: (-r["size"], r["path"]))


def resolve_paths(h5: h5py.File) -> dict[str, str | None]:
    mapping: dict[str, str | None] = {}

    for name, path in FIXED_PATHS.items():
        mapping[name] = path if get_h5_dataset(h5, path) is not None else None

    for ci_name, candidates in CI_PATH_CANDIDATES.items():
        resolved = None
        for candidate in candidates:
            if get_h5_dataset(h5, candidate) is not None:
                resolved = candidate
                break
        mapping[ci_name] = resolved

    return mapping


def inspect_h5_file(path: Path) -> dict[str, Any]:
    with h5py.File(path, "r") as h5:
        return {
            "file": str(path),
            "datasets": list_numeric_datasets(h5),
            "auto_mapping": resolve_paths(h5),
        }


def inspect_zip_first_h5(zip_path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "zip": str(zip_path),
        "members": [],
    }

    if not zip_path.exists():
        result["error"] = "ZIP not found"
        return result

    with zipfile.ZipFile(zip_path) as zf:
        h5_members = find_h5_members(zf)
        result["hdf5_member_count"] = len(h5_members)

        if not h5_members:
            return result

        with tempfile.TemporaryDirectory(prefix="phm_inspect_") as td:
            temp_dir = Path(td)
            member = h5_members[0]
            extracted = extract_zip_member_to_temp(
                zf, member, temp_dir
            )
            try:
                report = inspect_h5_file(extracted)
                report["zip_member"] = member
                result["members"].append(report)
            finally:
                extracted.unlink(missing_ok=True)

    return result


def inspect_nested_archive(
    outer_zip_path: Path,
) -> dict[str, Any]:
    """
    Inspect:
        outer.zip
            -> per-run.zip
                -> HDF5
    """
    report: dict[str, Any] = {
        "outer_zip": str(outer_zip_path),
        "runs": {},
    }

    if not outer_zip_path.exists():
        report["error"] = "Outer ZIP does not exist"
        return report

    with zipfile.ZipFile(outer_zip_path) as outer_zip:
        inner_zips = sorted(
            [
                name for name in outer_zip.namelist()
                if name.lower().endswith(".zip")
                and not name.endswith("/")
            ],
            key=natural_key,
        )

        report["inner_zip_count"] = len(inner_zips)

        for inner_name in inner_zips:
            run = parse_run(inner_name)

            inner_bytes = outer_zip.read(inner_name)

            with zipfile.ZipFile(io.BytesIO(inner_bytes)) as inner_zip:
                h5_members = find_h5_members(inner_zip)

                run_info: dict[str, Any] = {
                    "inner_zip": inner_name,
                    "run": run,
                    "hdf5_count": len(h5_members),
                    "first_hdf5_members": h5_members[:10],
                }

                if h5_members:
                    with tempfile.TemporaryDirectory(
                        prefix=f"phm_nested_run{run}_"
                    ) as td:
                        temp_dir = Path(td)
                        extracted = extract_zip_member_to_temp(
                            inner_zip,
                            h5_members[0],
                            temp_dir,
                        )
                        try:
                            run_info["first_hdf5"] = inspect_h5_file(
                                extracted
                            )
                            run_info["first_hdf5"]["zip_member"] = h5_members[0]
                        finally:
                            extracted.unlink(missing_ok=True)

                report["runs"][f"Run-{run}"] = run_info

    return report


def run_inspection() -> None:
    ensure_dirs()

    inventory = {
        "high_frequency": {
            str(run): zip_inventory(path)
            for run, path in HF_ZIPS.items()
        },
        "low_frequency_outer": zip_inventory(LF_OUTER_ZIP),
        "ci_outer": zip_inventory(CI_OUTER_ZIP),
        "photos": {},
    }

    if PHOTO_DIR.exists():
        for p in sorted(
            PHOTO_DIR.glob("*.zip"),
            key=lambda x: natural_key(x.name),
        ):
            inventory["photos"][p.name] = zip_inventory(p)

    save_json(
        inventory,
        REPORT_DIR / "dataset_inventory.json",
    )

    h5_report: dict[str, Any] = {}

    for run, zip_path in HF_ZIPS.items():
        if zip_path.exists():
            try:
                h5_report[f"HF_Run_{run}"] = inspect_zip_first_h5(
                    zip_path
                )
            except Exception as exc:
                h5_report[f"HF_Run_{run}"] = {
                    "error": repr(exc)
                }

    save_json(
        h5_report,
        REPORT_DIR / "hdf5_structure_report.json",
    )

    nested_report = {
        "LF": inspect_nested_archive(LF_OUTER_ZIP),
        "CI": inspect_nested_archive(CI_OUTER_ZIP),
    }

    save_json(
        nested_report,
        REPORT_DIR / "nested_low_frequency_structure.json",
    )

    print("\n=== INSPECTION COMPLETE ===")
    print(f"Reports: {REPORT_DIR}")
    print("  dataset_inventory.json")
    print("  hdf5_structure_report.json")
    print("  nested_low_frequency_structure.json")


# =============================================================================
# 4. HIGH-FREQUENCY FEATURE EXTRACTION
# =============================================================================

def infer_sampling_rate(
    ds: h5py.Dataset | None,
    default: float = DEFAULT_HF_FS,
) -> float:
    if ds is None:
        return default

    attr_keys = {
        str(k).lower(): k
        for k in ds.attrs.keys()
    }

    for candidate in [
        "sampling_rate",
        "sample_rate",
        "samplerate",
        "fs",
        "frequency",
    ]:
        if candidate in attr_keys:
            try:
                value = float(
                    np.asarray(
                        ds.attrs[attr_keys[candidate]]
                    ).squeeze()
                )
                if value > 0:
                    return value
            except Exception:
                pass

    return default


def stream_basic_features(
    ds: h5py.Dataset,
    block_points: int = 2_000_000,
) -> dict[str, float]:
    """Exact mean/std/RMS/min/max for 1D signals using blocks."""
    if ds.ndim != 1:
        x = bounded_stride_sample(
            ds,
            MAX_STATS_SAMPLE_POINTS,
        )
        if x.size == 0:
            return {}
        return {
            "mean": float(np.mean(x)),
            "std": float(np.std(x)),
            "rms": float(np.sqrt(np.mean(x * x))),
            "min": float(np.min(x)),
            "max": float(np.max(x)),
            "peak_to_peak": float(np.ptp(x)),
        }

    count = 0
    sx = 0.0
    sx2 = 0.0
    minimum = np.inf
    maximum = -np.inf

    for start in range(0, ds.shape[0], block_points):
        x = finite(
            ds[start:start + block_points]
        )
        if x.size == 0:
            continue

        count += x.size
        sx += float(np.sum(x, dtype=np.float64))
        sx2 += float(np.sum(x * x, dtype=np.float64))
        minimum = min(minimum, float(np.min(x)))
        maximum = max(maximum, float(np.max(x)))

    if count == 0:
        return {}

    mean = sx / count
    variance = max(0.0, sx2 / count - mean * mean)

    return {
        "mean": mean,
        "std": math.sqrt(variance),
        "rms": math.sqrt(sx2 / count),
        "min": minimum,
        "max": maximum,
        "peak_to_peak": maximum - minimum,
    }


def sample_shape_features(
    ds: h5py.Dataset,
) -> dict[str, float]:
    x = bounded_stride_sample(
        ds,
        MAX_STATS_SAMPLE_POINTS,
    )

    if x.size < 8:
        return {
            "skewness": np.nan,
            "kurtosis": np.nan,
            "crest_factor": np.nan,
        }

    rms = float(
        np.sqrt(np.mean(x * x))
    )

    peak = float(
        np.max(np.abs(x))
    )

    return {
        "skewness": float(
            stats.skew(x, bias=False)
        ),
        # Pearson definition so Gaussian ~= 3
        "kurtosis": float(
            stats.kurtosis(
                x,
                fisher=False,
                bias=False,
            )
        ),
        "crest_factor": (
            peak / rms if rms > 0 else np.nan
        ),
    }


def centered_spectral_sample(
    ds: h5py.Dataset,
) -> np.ndarray:
    if ds.ndim != 1:
        return bounded_stride_sample(
            ds,
            SPECTRAL_WINDOW_POINTS,
        )

    n = ds.shape[0]
    take = min(n, SPECTRAL_WINDOW_POINTS)
    start = max(0, (n - take) // 2)

    return finite(
        ds[start:start + take]
    )


def band_energy(
    freq: np.ndarray,
    psd: np.ndarray,
    center_hz: float,
    half_width_hz: float,
) -> float:
    if not np.isfinite(center_hz) or center_hz <= 0:
        return np.nan

    mask = (
        (freq >= center_hz - half_width_hz)
        & (freq <= center_hz + half_width_hz)
    )

    if mask.sum() < 2:
        return np.nan

    return float(
        np.trapezoid(
            psd[mask],
            freq[mask],
        )
    )


def spectral_features(
    ds: h5py.Dataset,
    fs: float,
    rpm: float | None,
) -> dict[str, float]:
    x = centered_spectral_sample(ds)

    if x.size < 1024:
        return {}

    x = signal.detrend(
        x,
        type="constant",
    )

    nperseg = min(
        WELCH_NPERSEG,
        x.size,
    )

    freq, psd = signal.welch(
        x,
        fs=fs,
        nperseg=nperseg,
        scaling="density",
    )

    valid = (
        (freq > 0)
        & np.isfinite(psd)
    )

    if valid.sum() < 2:
        return {}

    f = freq[valid]
    p = psd[valid]

    dominant_hz = float(
        f[np.argmax(p)]
    )

    p_sum = float(
        np.sum(p)
    )

    centroid_hz = (
        float(np.sum(f * p) / p_sum)
        if p_sum > 0
        else np.nan
    )

    total_energy = float(
        np.trapezoid(p, f)
    )

    output = {
        "spectral_dominant_hz": dominant_hz,
        "spectral_centroid_hz": centroid_hz,
        "spectral_total_energy": total_energy,
    }

    if (
        rpm is not None
        and np.isfinite(rpm)
        and rpm > 0
    ):
        shaft_hz = rpm / 60.0
        gmf_hz = GEAR_TEETH * shaft_hz

        output["shaft_hz"] = shaft_hz
        output["gmf_hz"] = gmf_hz

        for harmonic in [1, 2, 3]:
            center = harmonic * gmf_hz

            half_width = max(
                GMF_MIN_HALF_WIDTH_HZ,
                GMF_RELATIVE_HALF_WIDTH * center,
            )

            output[
                f"gmf_h{harmonic}_energy"
            ] = band_energy(
                f,
                p,
                center,
                half_width,
            )

    return output


def scalar_from_dataset(
    h5: h5py.File,
    path: str | None,
) -> float:
    ds = get_h5_dataset(h5, path)

    if ds is None:
        return np.nan

    sample = bounded_stride_sample(
        ds,
        max_points=100_000,
    )

    return robust_median(sample)


def analyze_hf_h5(
    path: Path,
    run: int,
    member_index: int,
    member_name: str,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "run": run,
        "stage": RUN_STAGE[run],
        "member_index": member_index,
        "source_member": member_name,
    }

    with h5py.File(path, "r") as h5:
        mapping = resolve_paths(h5)

        for key, value in mapping.items():
            row[f"path_{key}"] = value

        rpm = scalar_from_dataset(
            h5,
            mapping["rpm"],
        )

        torque = scalar_from_dataset(
            h5,
            mapping["torque"],
        )

        temperature = scalar_from_dataset(
            h5,
            mapping["temperature"],
        )

        row["rpm"] = rpm
        row["torque"] = torque
        row["temperature"] = temperature

        for ci in ["fm4", "na4", "m6a", "alr"]:
            row[ci] = scalar_from_dataset(
                h5,
                mapping[ci],
            )

        for channel in ["axial", "radial"]:
            ds = get_h5_dataset(
                h5,
                mapping[channel],
            )

            if ds is None:
                continue

            fs = infer_sampling_rate(ds)

            row[f"{channel}_fs"] = fs
            row[f"{channel}_n"] = int(ds.size)

            features = {}

            features.update(
                stream_basic_features(ds)
            )

            features.update(
                sample_shape_features(ds)
            )

            features.update(
                spectral_features(
                    ds,
                    fs=fs,
                    rpm=(
                        rpm
                        if np.isfinite(rpm)
                        else None
                    ),
                )
            )

            for feature_name, value in features.items():
                row[
                    f"{channel}_{feature_name}"
                ] = value

    return row


def process_hf_run(
    run: int,
    max_files: int | None,
) -> pd.DataFrame:
    zip_path = HF_ZIPS[run]

    if not zip_path.exists():
        print(
            f"[HF Run-{run}] Missing: {zip_path}"
        )
        return pd.DataFrame()

    if zip_path.name.endswith(".part"):
        print(
            f"[HF Run-{run}] Still downloading: {zip_path}"
        )
        return pd.DataFrame()

    try:
        zf = zipfile.ZipFile(zip_path)
    except Exception as exc:
        print(
            f"[HF Run-{run}] Cannot open ZIP: {exc}"
        )
        return pd.DataFrame()

    rows: list[dict[str, Any]] = []

    with zf:
        members = find_h5_members(zf)

        if max_files is not None:
            members = members[:max_files]

        print()
        print("=" * 80)
        print(
            f"HF RUN-{run}: "
            f"{len(members)} HDF5 files selected"
        )
        print("=" * 80)

        with tempfile.TemporaryDirectory(
            prefix=f"phm_hf_run{run}_"
        ) as td:
            temp_dir = Path(td)

            for index, member in enumerate(members):
                print(
                    f"{index + 1:4d}/"
                    f"{len(members):4d}  "
                    f"{member}",
                    flush=True,
                )

                extracted = extract_zip_member_to_temp(
                    zf,
                    member,
                    temp_dir,
                )

                try:
                    rows.append(
                        analyze_hf_h5(
                            extracted,
                            run,
                            index,
                            member,
                        )
                    )
                except Exception as exc:
                    rows.append({
                        "run": run,
                        "stage": RUN_STAGE[run],
                        "member_index": index,
                        "source_member": member,
                        "error": repr(exc),
                    })
                finally:
                    extracted.unlink(
                        missing_ok=True
                    )

    df = pd.DataFrame(rows)

    if not df.empty:
        df["progress_in_run"] = (
            df["member_index"]
            / max(
                1,
                df["member_index"].max(),
            )
        )

        out = TABLE_DIR / f"hf_features_run{run}.csv"

        df.to_csv(
            out,
            index=False,
        )

        print(
            f"[HF Run-{run}] Saved: {out}"
        )

    return df


def process_all_hf(
    max_files_per_run: int | None,
) -> pd.DataFrame:
    ensure_dirs()

    frames: list[pd.DataFrame] = []

    for run in SELECTED_HF_RUNS:
        frame = process_hf_run(
            run,
            max_files_per_run,
        )

        if not frame.empty:
            frames.append(frame)

    if not frames:
        print(
            "No high-frequency feature tables were produced."
        )
        return pd.DataFrame()

    combined = pd.concat(
        frames,
        ignore_index=True,
        sort=False,
    )

    combined.to_csv(
        TABLE_DIR / "hf_features_all.csv",
        index=False,
    )

    return combined


# =============================================================================
# 5. LOW-FREQUENCY + CI NESTED ZIP EXTRACTION
# =============================================================================

def numeric_1d_arrays(
    h5: h5py.File,
) -> dict[str, np.ndarray]:
    arrays: dict[str, np.ndarray] = {}

    for meta in list_numeric_datasets(h5):
        ds = get_h5_dataset(
            h5,
            meta["path"],
        )

        if ds is None:
            continue

        if ds.ndim == 1:
            arrays[meta["path"]] = finite(
                ds[...]
            )

        elif ds.ndim == 2 and 1 in ds.shape:
            arrays[meta["path"]] = finite(
                ds[...]
            )

    return arrays


def arrays_to_dataframe(
    arrays: dict[str, np.ndarray],
    run: int | None,
    source_name: str,
) -> pd.DataFrame:
    if not arrays:
        return pd.DataFrame()

    lengths = [
        len(x)
        for x in arrays.values()
        if len(x) > 1
    ]

    if not lengths:
        return pd.DataFrame()

    # Most relevant time-series length.
    target_length = max(lengths)

    data: dict[str, np.ndarray] = {}

    for path, array in arrays.items():
        col = (
            path.strip("/")
            .replace("/", "__")
            .replace(" ", "_")
        )

        if len(array) == target_length:
            data[col] = array

        elif len(array) == 1:
            data[col] = np.repeat(
                array[0],
                target_length,
            )

    if not data:
        return pd.DataFrame()

    frame = pd.DataFrame(data)

    frame.insert(
        0,
        "run",
        run,
    )

    frame.insert(
        1,
        "sample_index",
        np.arange(len(frame)),
    )

    frame.insert(
        2,
        "source_file",
        source_name,
    )

    return frame


def extract_nested_low_frequency(
    outer_zip_path: Path,
    label: str,
) -> pd.DataFrame:
    """
    Reads:
        outer.zip
            -> per-run.zip
                -> HDF5
    """
    if not outer_zip_path.exists():
        print(
            f"[{label}] Missing: {outer_zip_path}"
        )
        return pd.DataFrame()

    all_frames: list[pd.DataFrame] = []

    with zipfile.ZipFile(
        outer_zip_path
    ) as outer_zip:

        inner_zips = sorted(
            [
                name
                for name in outer_zip.namelist()
                if name.lower().endswith(".zip")
                and not name.endswith("/")
            ],
            key=natural_key,
        )

        print()
        print("=" * 80)
        print(
            f"{label}: {len(inner_zips)} nested run archives"
        )
        print("=" * 80)

        for inner_name in inner_zips:
            run = parse_run(inner_name)

            print(
                f"[{label}] "
                f"{inner_name} "
                f"(Run {run})"
            )

            inner_bytes = outer_zip.read(
                inner_name
            )

            with zipfile.ZipFile(
                io.BytesIO(inner_bytes)
            ) as inner_zip:

                h5_members = find_h5_members(
                    inner_zip
                )

                print(
                    f"    HDF5 files: "
                    f"{len(h5_members)}"
                )

                with tempfile.TemporaryDirectory(
                    prefix=f"phm_{label}_run{run}_"
                ) as td:
                    temp_dir = Path(td)

                    for idx, h5_member in enumerate(
                        h5_members,
                        start=1,
                    ):
                        print(
                            f"    {idx:3d}/"
                            f"{len(h5_members):3d} "
                            f"{h5_member}"
                        )

                        extracted = extract_zip_member_to_temp(
                            inner_zip,
                            h5_member,
                            temp_dir,
                        )

                        try:
                            with h5py.File(
                                extracted,
                                "r",
                            ) as h5:
                                arrays = numeric_1d_arrays(
                                    h5
                                )

                            frame = arrays_to_dataframe(
                                arrays,
                                run,
                                (
                                    f"{inner_name}"
                                    f"::{h5_member}"
                                ),
                            )

                            if not frame.empty:
                                frame.insert(
                                    0,
                                    "dataset_type",
                                    label,
                                )
                                all_frames.append(
                                    frame
                                )

                        except Exception as exc:
                            print(
                                f"        WARNING: {exc}"
                            )

                        finally:
                            extracted.unlink(
                                missing_ok=True
                            )

    if not all_frames:
        print(
            f"[{label}] No usable rows extracted."
        )
        return pd.DataFrame()

    combined = pd.concat(
        all_frames,
        ignore_index=True,
        sort=False,
    )

    combined = combined.sort_values(
        ["run", "sample_index"]
    ).reset_index(drop=True)

    out = TABLE_DIR / f"{label.lower()}_flattened.csv"

    combined.to_csv(
        out,
        index=False,
    )

    print(
        f"[{label}] Saved: {out}"
    )

    return combined


def find_column_by_keywords(
    columns: Iterable[str],
    patterns: Sequence[str],
) -> str | None:
    candidates: list[tuple[int, str]] = []

    for column in columns:
        low = column.lower()

        score = sum(
            1
            for pattern in patterns
            if re.search(
                pattern,
                low,
                flags=re.IGNORECASE,
            )
        )

        if score > 0:
            candidates.append(
                (score, column)
            )

    if not candidates:
        return None

    candidates.sort(
        key=lambda x: (
            -x[0],
            len(x[1]),
        )
    )

    return candidates[0][1]


def canonicalize_low_frequency(
    df: pd.DataFrame,
    label: str,
) -> pd.DataFrame:
    if df.empty:
        return df

    out = df.copy()

    mapping_patterns = {
        "rpm": [
            r"pau[_\s]*speed",
            r"\brpm\b",
            r"speed",
        ],
        "torque": [
            r"pau[_\s]*torque",
            r"torque",
        ],
        "temperature": [
            r"temperature",
            r"\btemp\b",
        ],
        "fm4": [r"\bfm4\b"],
        "na4": [r"\bna4\b"],
        "m6a": [r"\bm6a\b"],
        "alr": [r"\balr\b"],
    }

    resolved: dict[str, str | None] = {}

    for target, patterns in mapping_patterns.items():
        source = find_column_by_keywords(
            out.columns,
            patterns,
        )

        resolved[target] = source

        if source is not None:
            out[target] = pd.to_numeric(
                out[source],
                errors="coerce",
            )

    save_json(
        resolved,
        REPORT_DIR
        / f"{label.lower()}_column_mapping.json",
    )

    return out


def process_low_frequency(
) -> tuple[pd.DataFrame, pd.DataFrame]:
    ensure_dirs()

    lf = extract_nested_low_frequency(
        LF_OUTER_ZIP,
        "LF",
    )

    ci = extract_nested_low_frequency(
        CI_OUTER_ZIP,
        "CI",
    )

    lf = canonicalize_low_frequency(
        lf,
        "LF",
    )

    ci = canonicalize_low_frequency(
        ci,
        "CI",
    )

    if not lf.empty:
        lf.to_csv(
            TABLE_DIR / "lf_canonical.csv",
            index=False,
        )

    if not ci.empty:
        ci.to_csv(
            TABLE_DIR / "ci_canonical.csv",
            index=False,
        )

    return lf, ci


# =============================================================================
# 6. PHOTO EDA
# =============================================================================

def photo_stage_from_name(
    name: str,
) -> tuple[str, int | None]:
    low = name.lower()

    if (
        "0_hours" in low
        or "0 hours" in low
        or "test start" in low
    ):
        return "0h_test_start", 0

    if "break" in low:
        return "break_in", None

    run = parse_run(name)

    if run is not None:
        return f"run_{run}", run

    return "unknown", None


def parse_tooth_id(
    name: str,
) -> int | None:
    for pattern in [
        r"tooth[-_\s]*(\d+)",
        r"teeth[-_\s]*(\d+)",
        r"\bt[-_\s]*(\d+)\b",
    ]:
        match = re.search(
            pattern,
            name,
            flags=re.IGNORECASE,
        )

        if match:
            tooth = int(
                match.group(1)
            )

            if 1 <= tooth <= 28:
                return tooth

    return None


def image_entropy(
    gray: np.ndarray,
) -> float:
    hist, _ = np.histogram(
        gray.ravel(),
        bins=256,
        range=(0, 255),
    )

    hist = hist.astype(
        np.float64
    )

    hist = hist[
        hist > 0
    ]

    hist /= hist.sum()

    return float(
        -np.sum(
            hist
            * np.log2(hist)
        )
    )


def image_quality_features(
    img: Image.Image,
) -> dict[str, float]:
    gray = np.asarray(
        ImageOps.grayscale(img),
        dtype=np.float32,
    )

    gx = np.diff(
        gray,
        axis=1,
    )

    gy = np.diff(
        gray,
        axis=0,
    )

    return {
        "width": float(img.width),
        "height": float(img.height),
        "brightness_mean": float(
            np.mean(gray)
        ),
        "brightness_std": float(
            np.std(gray)
        ),
        "entropy": image_entropy(gray),
        "edge_energy": float(
            np.mean(gx * gx)
            + np.mean(gy * gy)
        ),
    }


def make_contact_sheet(
    image_paths: Sequence[Path],
    title: str,
    output_path: Path,
    columns: int = 7,
) -> None:
    if not image_paths:
        return

    cards: list[Image.Image] = []

    for path in image_paths:
        try:
            with Image.open(path) as img:
                thumb = img.convert("RGB")
                thumb.thumbnail(
                    (220, 160)
                )

                card = Image.new(
                    "RGB",
                    (230, 190),
                    "white",
                )

                x = (
                    230 - thumb.width
                ) // 2

                card.paste(
                    thumb,
                    (x, 5),
                )

                drawer = ImageDraw.Draw(
                    card
                )

                drawer.text(
                    (8, 168),
                    path.stem[:32],
                    fill="black",
                )

                cards.append(card)

        except Exception:
            continue

    if not cards:
        return

    rows = math.ceil(
        len(cards) / columns
    )

    sheet = Image.new(
        "RGB",
        (
            columns * 230,
            rows * 190 + 40,
        ),
        "white",
    )

    drawer = ImageDraw.Draw(
        sheet
    )

    drawer.text(
        (10, 10),
        title,
        fill="black",
    )

    for index, card in enumerate(cards):
        row, col = divmod(
            index,
            columns,
        )

        sheet.paste(
            card,
            (
                col * 230,
                40 + row * 190,
            ),
        )

    sheet.save(
        output_path
    )


def process_photos() -> pd.DataFrame:
    ensure_dirs()

    if not PHOTO_DIR.exists():
        print(
            f"Photo directory missing: {PHOTO_DIR}"
        )
        return pd.DataFrame()

    all_rows: list[dict[str, Any]] = []

    for photo_zip in sorted(
        PHOTO_DIR.glob("*.zip"),
        key=lambda p: natural_key(p.name),
    ):
        stage, run = photo_stage_from_name(
            photo_zip.name
        )

        stage_dir = (
            PHOTO_CACHE_DIR / stage
        )

        stage_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        extracted_paths: list[Path] = []

        print(
            f"[PHOTO] {photo_zip.name}"
        )

        with zipfile.ZipFile(
            photo_zip
        ) as zf:
            members = find_image_members(
                zf
            )

            for index, member in enumerate(members):
                tooth_id = parse_tooth_id(
                    member
                )

                suffix = (
                    Path(member).suffix.lower()
                    or ".jpg"
                )

                if tooth_id is not None:
                    filename = (
                        f"tooth_{tooth_id:02d}"
                        f"{suffix}"
                    )
                else:
                    filename = (
                        f"image_{index + 1:03d}"
                        f"{suffix}"
                    )

                output_path = (
                    stage_dir / filename
                )

                if not output_path.exists():
                    with zf.open(member) as src, output_path.open(
                        "wb"
                    ) as dst:
                        shutil.copyfileobj(
                            src,
                            dst,
                        )

                extracted_paths.append(
                    output_path
                )

                try:
                    with Image.open(
                        output_path
                    ) as img:
                        features = image_quality_features(
                            img.convert("RGB")
                        )
                except Exception as exc:
                    features = {
                        "image_error": repr(exc)
                    }

                all_rows.append({
                    "stage": stage,
                    "run": run,
                    "tooth_id": tooth_id,
                    "source_zip": photo_zip.name,
                    "source_member": member,
                    "image_path": str(output_path),
                    **features,
                })

        make_contact_sheet(
            extracted_paths,
            title=stage,
            output_path=FIG_DIR / f"contact_sheet_{stage}.jpg",
        )

    photos = pd.DataFrame(
        all_rows
    )

    if photos.empty:
        return photos

    photos.to_csv(
        TABLE_DIR / "photo_inventory.csv",
        index=False,
    )

    damage_template = photos[
        [
            "stage",
            "run",
            "tooth_id",
            "image_path",
        ]
    ].copy()

    # Intentionally empty until manual annotation or RT-DETR.
    damage_template[
        "manual_or_model_damage_score"
    ] = np.nan

    damage_template[
        "damage_area_fraction"
    ] = np.nan

    damage_template[
        "damage_confidence"
    ] = np.nan

    damage_template.to_csv(
        TABLE_DIR
        / "image_damage_scoring_template.csv",
        index=False,
    )

    return photos


# =============================================================================
# 7. ADVANCED ANALYSIS
# =============================================================================

def numeric_feature_columns(
    df: pd.DataFrame,
) -> list[str]:
    excluded = {
        "run",
        "member_index",
        "progress_in_run",
        "rpm",
        "torque",
        "temperature",
    }

    columns: list[str] = []

    for column in df.columns:
        if column in excluded:
            continue

        if (
            column.startswith("path_")
            or column in {
                "stage",
                "source_member",
                "error",
            }
        ):
            continue

        if (
            pd.api.types.is_numeric_dtype(
                df[column]
            )
            and df[column].notna().sum()
            >= max(
                3,
                int(0.2 * len(df)),
            )
        ):
            columns.append(column)

    return columns


def standardized_effect(
    a: np.ndarray,
    b: np.ndarray,
) -> float:
    a = finite(a)
    b = finite(b)

    if len(a) < 2 or len(b) < 2:
        return np.nan

    pooled_std = math.sqrt(
        (
            np.var(a, ddof=1)
            + np.var(b, ddof=1)
        )
        / 2
    )

    if pooled_std <= 0:
        return np.nan

    return float(
        (
            np.mean(b)
            - np.mean(a)
        )
        / pooled_std
    )


def lifecycle_shift_table(
    df: pd.DataFrame,
) -> pd.DataFrame:
    features = numeric_feature_columns(
        df
    )

    comparisons = [
        (1, 3),
        (3, 5),
        (1, 5),
    ]

    rows: list[dict[str, Any]] = []

    for feature in features:
        for run_a, run_b in comparisons:
            a = finite(
                pd.to_numeric(
                    df.loc[
                        df["run"] == run_a,
                        feature,
                    ],
                    errors="coerce",
                )
            )

            b = finite(
                pd.to_numeric(
                    df.loc[
                        df["run"] == run_b,
                        feature,
                    ],
                    errors="coerce",
                )
            )

            if len(a) < 2 or len(b) < 2:
                continue

            rows.append({
                "feature": feature,
                "comparison": (
                    f"R{run_a}_vs_R{run_b}"
                ),
                "median_a": float(
                    np.median(a)
                ),
                "median_b": float(
                    np.median(b)
                ),
                "median_shift": float(
                    np.median(b)
                    - np.median(a)
                ),
                "wasserstein": float(
                    wasserstein_distance(
                        a,
                        b,
                    )
                ),
                "standardized_effect": (
                    standardized_effect(
                        a,
                        b,
                    )
                ),
                "n_a": len(a),
                "n_b": len(b),
            })

    result = pd.DataFrame(
        rows
    )

    if not result.empty:
        result.to_csv(
            TABLE_DIR
            / "lifecycle_distribution_shift.csv",
            index=False,
        )

    return result


def select_top_features(
    shift_df: pd.DataFrame,
    n: int = 12,
) -> list[str]:
    if shift_df.empty:
        return []

    r15 = shift_df[
        shift_df["comparison"]
        == "R1_vs_R5"
    ].copy()

    if r15.empty:
        return []

    r15["rank_metric"] = (
        r15["standardized_effect"]
        .abs()
    )

    r15 = r15.replace(
        [np.inf, -np.inf],
        np.nan,
    ).dropna(
        subset=["rank_metric"]
    )

    return (
        r15.sort_values(
            "rank_metric",
            ascending=False,
        )["feature"]
        .drop_duplicates()
        .head(n)
        .tolist()
    )


def operating_condition_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for run in SELECTED_HF_RUNS:
        sub = df[
            df["run"] == run
        ]

        for variable in [
            "rpm",
            "torque",
            "temperature",
        ]:
            if variable not in sub:
                continue

            x = finite(
                pd.to_numeric(
                    sub[variable],
                    errors="coerce",
                )
            )

            if x.size == 0:
                continue

            rows.append({
                "run": run,
                "variable": variable,
                "n": len(x),
                "mean": float(np.mean(x)),
                "std": float(np.std(x)),
                "median": float(np.median(x)),
                "q05": float(np.quantile(x, 0.05)),
                "q95": float(np.quantile(x, 0.95)),
                "min": float(np.min(x)),
                "max": float(np.max(x)),
            })

    result = pd.DataFrame(
        rows
    )

    if not result.empty:
        result.to_csv(
            TABLE_DIR
            / "operating_condition_summary.csv",
            index=False,
        )

    return result


def sensor_sensitivity_summary(
    shift_df: pd.DataFrame,
) -> pd.DataFrame:
    if shift_df.empty:
        return pd.DataFrame()

    r15 = shift_df[
        shift_df["comparison"]
        == "R1_vs_R5"
    ]

    rows: list[dict[str, Any]] = []

    for channel in [
        "axial",
        "radial",
    ]:
        sub = r15[
            r15["feature"].str.startswith(
                channel + "_",
                na=False,
            )
        ]

        if sub.empty:
            continue

        rows.append({
            "channel": channel,
            "n_features": len(sub),
            "median_abs_effect": float(
                sub["standardized_effect"]
                .abs()
                .median()
            ),
            "median_wasserstein": float(
                sub["wasserstein"]
                .median()
            ),
            "max_abs_effect": float(
                sub["standardized_effect"]
                .abs()
                .max()
            ),
        })

    result = pd.DataFrame(
        rows
    )

    if not result.empty:
        result.to_csv(
            TABLE_DIR
            / "sensor_sensitivity_summary.csv",
            index=False,
        )

    return result


def plot_feature_distributions(
    df: pd.DataFrame,
    features: Sequence[str],
) -> None:
    for feature in features:
        groups = []
        labels = []

        for run in SELECTED_HF_RUNS:
            x = finite(
                pd.to_numeric(
                    df.loc[
                        df["run"] == run,
                        feature,
                    ],
                    errors="coerce",
                )
            )

            if len(x) >= 2:
                groups.append(x)
                labels.append(
                    f"Run-{run}"
                )

        if len(groups) < 2:
            continue

        fig, ax = plt.subplots(
            figsize=(7.5, 4.8)
        )

        ax.boxplot(
            groups,
            tick_labels=labels,
            showfliers=False,
        )

        ax.set_title(
            f"Lifecycle distribution: {feature}"
        )

        ax.set_ylabel(
            feature
        )

        fig.tight_layout()

        safe_name = re.sub(
            r"[^A-Za-z0-9_]+",
            "_",
            feature,
        )

        fig.savefig(
            FIG_DIR
            / f"box_{safe_name}.png",
            dpi=180,
        )

        plt.close(fig)


def plot_temporal_trajectories(
    df: pd.DataFrame,
    features: Sequence[str],
) -> None:
    for feature in features:
        fig, ax = plt.subplots(
            figsize=(9, 4.8)
        )

        plotted = False

        for run in SELECTED_HF_RUNS:
            sub = (
                df[df["run"] == run]
                .sort_values("member_index")
            )

            y = pd.to_numeric(
                sub[feature],
                errors="coerce",
            )

            valid = y.notna()

            if valid.sum() < 2:
                continue

            ax.plot(
                sub.loc[
                    valid,
                    "progress_in_run",
                ],
                y[valid],
                label=f"Run-{run}",
            )

            plotted = True

        if not plotted:
            plt.close(fig)
            continue

        ax.set_xlabel(
            "Normalized progress within run"
        )

        ax.set_ylabel(
            feature
        )

        ax.set_title(
            f"Within-run trajectory: {feature}"
        )

        ax.legend()

        fig.tight_layout()

        safe_name = re.sub(
            r"[^A-Za-z0-9_]+",
            "_",
            feature,
        )

        fig.savefig(
            FIG_DIR
            / f"trajectory_{safe_name}.png",
            dpi=180,
        )

        plt.close(fig)


def run_pca(
    df: pd.DataFrame,
) -> pd.DataFrame:
    features = numeric_feature_columns(
        df
    )

    if len(features) < 2:
        return pd.DataFrame()

    X = df[features].replace(
        [np.inf, -np.inf],
        np.nan,
    )

    keep = [
        column
        for column in X.columns
        if (
            X[column].notna().sum()
            >= max(
                3,
                int(0.5 * len(X)),
            )
            and X[column].nunique(
                dropna=True
            ) > 1
        )
    ]

    if len(keep) < 2:
        return pd.DataFrame()

    X = X[keep]

    imputer = SimpleImputer(
        strategy="median"
    )

    scaler = StandardScaler()

    Xi = imputer.fit_transform(X)
    Xs = scaler.fit_transform(Xi)

    n_components = min(
        5,
        Xs.shape[1],
        Xs.shape[0],
    )

    pca = PCA(
        n_components=n_components,
        random_state=0,
    )

    Z = pca.fit_transform(
        Xs
    )

    scores = df[
        [
            "run",
            "stage",
            "member_index",
            "progress_in_run",
        ]
    ].copy()

    for idx in range(
        Z.shape[1]
    ):
        scores[
            f"PC{idx + 1}"
        ] = Z[:, idx]

    for context in [
        "rpm",
        "torque",
        "temperature",
    ]:
        if context in df:
            scores[context] = pd.to_numeric(
                df[context],
                errors="coerce",
            )

    scores.to_csv(
        TABLE_DIR / "pca_scores.csv",
        index=False,
    )

    loadings = pd.DataFrame(
        pca.components_.T,
        index=keep,
        columns=[
            f"PC{i + 1}"
            for i in range(n_components)
        ],
    )

    loadings["abs_PC1"] = (
        loadings["PC1"].abs()
    )

    loadings.sort_values(
        "abs_PC1",
        ascending=False,
    ).to_csv(
        TABLE_DIR / "pca_loadings.csv"
    )

    save_json(
        {
            "features": keep,
            "explained_variance_ratio":
                pca.explained_variance_ratio_.tolist(),
        },
        REPORT_DIR / "pca_metadata.json",
    )

    # Lifecycle-colored PCA.
    if "PC2" in scores:
        fig, ax = plt.subplots(
            figsize=(7.5, 5.5)
        )

        for run in SELECTED_HF_RUNS:
            sub = scores[
                scores["run"] == run
            ]

            if sub.empty:
                continue

            ax.scatter(
                sub["PC1"],
                sub["PC2"],
                s=18,
                alpha=0.65,
                label=f"Run-{run}",
            )

        ax.set_xlabel(
            f"PC1 "
            f"({pca.explained_variance_ratio_[0] * 100:.1f}%)"
        )

        ax.set_ylabel(
            f"PC2 "
            f"({pca.explained_variance_ratio_[1] * 100:.1f}%)"
        )

        ax.set_title(
            "Multivariate lifecycle feature map"
        )

        ax.legend()

        fig.tight_layout()

        fig.savefig(
            FIG_DIR / "pca_lifecycle.png",
            dpi=200,
        )

        plt.close(fig)

        for context in [
            "rpm",
            "torque",
            "temperature",
        ]:
            if (
                context not in scores
                or scores[context].notna().sum()
                < 5
            ):
                continue

            fig, ax = plt.subplots(
                figsize=(7.5, 5.5)
            )

            sc = ax.scatter(
                scores["PC1"],
                scores["PC2"],
                c=scores[context],
                s=18,
                alpha=0.7,
            )

            fig.colorbar(
                sc,
                ax=ax,
                label=context,
            )

            ax.set_xlabel("PC1")
            ax.set_ylabel("PC2")

            ax.set_title(
                f"Same PCA space colored by {context}"
            )

            fig.tight_layout()

            fig.savefig(
                FIG_DIR
                / f"pca_colored_{context}.png",
                dpi=200,
            )

            plt.close(fig)

    return scores


def context_normalized_residuals(
    df: pd.DataFrame,
    features: Sequence[str],
) -> pd.DataFrame:
    contexts = [
        context
        for context in [
            "rpm",
            "torque",
            "temperature",
        ]
        if (
            context in df
            and df[context].notna().sum()
            >= 10
        )
    ]

    if not contexts:
        return pd.DataFrame()

    X = df[contexts].apply(
        pd.to_numeric,
        errors="coerce",
    )

    Xi = SimpleImputer(
        strategy="median"
    ).fit_transform(X)

    Xs = StandardScaler().fit_transform(
        Xi
    )

    output = df[
        [
            "run",
            "stage",
            "member_index",
            "progress_in_run",
        ]
    ].copy()

    model_report: dict[str, Any] = {}

    for feature in features:
        if feature not in df:
            continue

        y = pd.to_numeric(
            df[feature],
            errors="coerce",
        ).to_numpy(
            dtype=float
        )

        valid = np.isfinite(y)

        if valid.sum() < 20:
            continue

        model = HuberRegressor()

        model.fit(
            Xs[valid],
            y[valid],
        )

        predicted = np.full(
            len(y),
            np.nan,
        )

        predicted[valid] = model.predict(
            Xs[valid]
        )

        output[
            f"{feature}__residual"
        ] = y - predicted

        model_report[feature] = {
            "contexts": contexts,
            "coef": model.coef_.tolist(),
            "intercept": float(
                model.intercept_
            ),
        }

    if output.shape[1] > 4:
        output.to_csv(
            TABLE_DIR
            / "context_normalized_residuals.csv",
            index=False,
        )

        save_json(
            model_report,
            REPORT_DIR
            / "context_normalization_models.json",
        )

    return output


def plot_low_frequency(
    df: pd.DataFrame,
    prefix: str,
) -> None:
    if df.empty:
        return

    variables = [
        variable
        for variable in [
            "rpm",
            "torque",
            "temperature",
            "fm4",
            "na4",
            "m6a",
            "alr",
        ]
        if variable in df
    ]

    for variable in variables:
        fig, ax = plt.subplots(
            figsize=(10, 4.8)
        )

        plotted = False

        for run in sorted(
            df["run"].dropna().unique()
        ):
            sub = (
                df[df["run"] == run]
                .sort_values("sample_index")
            )

            y = pd.to_numeric(
                sub[variable],
                errors="coerce",
            )

            valid = y.notna()

            if valid.sum() < 2:
                continue

            x = np.linspace(
                0,
                1,
                valid.sum(),
            )

            ax.plot(
                x,
                y[valid],
                label=f"Run-{int(run)}",
            )

            plotted = True

        if not plotted:
            plt.close(fig)
            continue

        ax.set_xlabel(
            "Normalized progress within run"
        )

        ax.set_ylabel(
            variable
        )

        ax.set_title(
            f"{prefix}: {variable}"
        )

        ax.legend()

        fig.tight_layout()

        fig.savefig(
            FIG_DIR
            / f"{prefix.lower()}_{variable}.png",
            dpi=180,
        )

        plt.close(fig)


def create_cross_modal_template(
    hf: pd.DataFrame,
    photos: pd.DataFrame,
) -> None:
    if hf.empty:
        return

    candidate_features = [
        column
        for column in numeric_feature_columns(hf)
        if any(
            token in column.lower()
            for token in [
                "rms",
                "kurtosis",
                "gmf_h1_energy",
                "fm4",
                "na4",
                "m6a",
                "alr",
            ]
        )
    ][:20]

    rows: list[dict[str, Any]] = []

    for run in SELECTED_HF_RUNS:
        sub = hf[
            hf["run"] == run
        ]

        if sub.empty:
            continue

        row: dict[str, Any] = {
            "run": run,
            "stage": RUN_STAGE[run],
        }

        for feature in candidate_features:
            values = finite(
                pd.to_numeric(
                    sub[feature],
                    errors="coerce",
                )
            )

            row[
                f"sensor_median__{feature}"
            ] = (
                float(np.median(values))
                if len(values)
                else np.nan
            )

        if not photos.empty:
            row["n_images"] = int(
                len(
                    photos[
                        photos["run"] == run
                    ]
                )
            )

        # To be filled later from manual labels / RT-DETR.
        row["image_damage_index_mean"] = np.nan
        row["image_damage_index_max"] = np.nan
        row["image_damage_index_top3_mean"] = np.nan

        rows.append(row)

    pd.DataFrame(
        rows
    ).to_csv(
        TABLE_DIR
        / "cross_modal_alignment_template.csv",
        index=False,
    )


def run_advanced_analysis() -> None:
    hf_path = (
        TABLE_DIR
        / "hf_features_all.csv"
    )

    if not hf_path.exists():
        print(
            "hf_features_all.csv not found. "
            "Run --mode hf first."
        )
        return

    hf = pd.read_csv(
        hf_path
    )

    if "progress_in_run" not in hf:
        hf["progress_in_run"] = (
            hf.groupby("run")[
                "member_index"
            ]
            .transform(
                lambda s:
                s / max(1, s.max())
            )
        )

    shift = lifecycle_shift_table(
        hf
    )

    top_features = select_top_features(
        shift,
        n=12,
    )

    print()
    print("Top early-to-late candidate shifts:")

    for feature in top_features:
        print(
            f"  - {feature}"
        )

    operating_condition_summary(
        hf
    )

    sensor_sensitivity_summary(
        shift
    )

    plot_feature_distributions(
        hf,
        top_features,
    )

    plot_temporal_trajectories(
        hf,
        top_features[:10],
    )

    run_pca(
        hf
    )

    context_normalized_residuals(
        hf,
        top_features[:8],
    )

    lf_path = (
        TABLE_DIR
        / "lf_canonical.csv"
    )

    ci_path = (
        TABLE_DIR
        / "ci_canonical.csv"
    )

    if lf_path.exists():
        plot_low_frequency(
            pd.read_csv(lf_path),
            "LF",
        )

    if ci_path.exists():
        plot_low_frequency(
            pd.read_csv(ci_path),
            "CI",
        )

    photo_path = (
        TABLE_DIR
        / "photo_inventory.csv"
    )

    photos = (
        pd.read_csv(photo_path)
        if photo_path.exists()
        else pd.DataFrame()
    )

    create_cross_modal_template(
        hf,
        photos,
    )

    print()
    print(
        f"Advanced analysis saved to: {OUT_ROOT}"
    )


# =============================================================================
# 8. CLI
# =============================================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "PHM 2026 EXP-A "
            "physics-aware advanced EDA"
        )
    )

    parser.add_argument(
        "--mode",
        choices=[
            "inspect",
            "lf",
            "photos",
            "hf",
            "plots",
            "all",
        ],
        default="all",
    )

    parser.add_argument(
        "--max-files-per-run",
        type=int,
        default=None,
        help=(
            "HF smoke-test limit. "
            "Example: --max-files-per-run 3"
        ),
    )

    return parser.parse_args()


def main() -> None:
    ensure_dirs()

    args = parse_args()

    print()
    print("=" * 80)
    print(
        "PHM NORTH AMERICA 2026 – EXP-A ADVANCED EDA"
    )
    print("=" * 80)

    print(
        f"Project root : {PROJECT_ROOT}"
    )

    print(
        f"Data root    : {DATA_ROOT}"
    )

    print(
        f"Output root  : {OUT_ROOT}"
    )

    print(
        f"Mode         : {args.mode}"
    )

    if args.mode == "inspect":
        run_inspection()
        return

    if args.mode == "lf":
        process_low_frequency()
        return

    if args.mode == "photos":
        process_photos()
        return

    if args.mode == "hf":
        process_all_hf(
            args.max_files_per_run
        )
        return

    if args.mode == "plots":
        run_advanced_analysis()
        return

    # ALL
    run_inspection()
    process_low_frequency()
    process_photos()
    process_all_hf(
        args.max_files_per_run
    )
    run_advanced_analysis()


if __name__ == "__main__":
    main()
