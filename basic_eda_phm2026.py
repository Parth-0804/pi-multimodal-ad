#!/usr/bin/env python3
"""
PHM North America 2026 - Beginner / Basic EDA
=============================================

Goal:
Understand the dataset before doing advanced PHM analysis.

This script answers:
1. What files/modalities do I have?
2. What is high-frequency vs low-frequency data?
3. What does one HDF5 file contain?
4. What does raw vibration look like?
5. What are the basic vibration statistics?
6. What does the vibration spectrum look like?
7. How do speed, torque and temperature behave?
8. What do FM4, NA4, M6A and ALR look like?
9. What do the gear-tooth photos look like?

It is intentionally simple and descriptive.
No degradation claims are made here.

Expected project path:
    /home/student/Master_Thesis_WS/pi-multimodal-ad
"""

from __future__ import annotations

import io
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

import h5py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageOps, ImageDraw


# =============================================================================
# CONFIG
# =============================================================================

PROJECT_ROOT = Path("/home/student/Master_Thesis_WS/pi-multimodal-ad")
DATA_ROOT = PROJECT_ROOT / "gtc-data-experiment"

OUT = PROJECT_ROOT / "basic_eda_outputs"
OUT.mkdir(parents=True, exist_ok=True)

# Start with Run-1 because it represents the early lifecycle.
RUN = 1

HF_ZIP = DATA_ROOT / f"Exp-A_HDF5_Run-{RUN}.zip"

LF_ZIP = (
    DATA_ROOT
    / "low-frequency (CIs + Oil + Environment)"
    / "Exp-A_HDF5_LF.zip"
)

CI_ZIP = (
    DATA_ROOT
    / "low-frequency (CIs)"
    / "Exp-A_HDF5_CI.zip"
)

PHOTO_DIR = DATA_ROOT / "photos" / "EXP-A"

# Confirmed dataset paths from your HDF5 inspection.
AXIAL_PATH = "/Vibration/Accel 1"
RADIAL_PATH = "/Vibration/Accel 2"

RPM_PATH = "/Context/PAU Speed"
TORQUE_PATH = "/Context/PAU Torque"
TEMP_PATH = "/Context/Temperature"

DEFAULT_FS = 102_400.0


# =============================================================================
# HELPERS
# =============================================================================

def human_size(num_bytes: int) -> str:
    value = float(num_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if value < 1024:
            return f"{value:.2f} {unit}"
        value /= 1024
    return f"{value:.2f} PB"


def hdf5_tree(h5: h5py.File) -> list[dict]:
    rows = []

    def visitor(name, obj):
        if isinstance(obj, h5py.Dataset):
            rows.append(
                {
                    "path": "/" + name.lstrip("/"),
                    "shape": str(tuple(obj.shape)),
                    "dtype": str(obj.dtype),
                    "n_values": int(np.prod(obj.shape)),
                }
            )

    h5.visititems(visitor)
    return rows


def first_hdf5_member(zf: zipfile.ZipFile) -> str:
    members = [
        n for n in zf.namelist()
        if n.lower().endswith((".h5", ".hdf5", ".hdf"))
    ]
    if not members:
        raise RuntimeError("No HDF5 file found inside ZIP.")
    return sorted(members)[0]


def extract_one_hdf5(zip_path: Path) -> tuple[tempfile.TemporaryDirectory, Path, str]:
    if not zip_path.exists():
        raise FileNotFoundError(zip_path)

    temp = tempfile.TemporaryDirectory(prefix="phm_basic_eda_")
    temp_dir = Path(temp.name)

    with zipfile.ZipFile(zip_path) as zf:
        member = first_hdf5_member(zf)
        target = temp_dir / Path(member).name

        with zf.open(member) as src, target.open("wb") as dst:
            shutil.copyfileobj(src, dst, length=16 * 1024 * 1024)

    return temp, target, member


def get_ci_group(h5: h5py.File) -> str | None:
    if "CI" in h5:
        return "/CI"
    if "CI_4s" in h5:
        return "/CI_4s"
    return None


def read_1d(h5: h5py.File, path: str) -> np.ndarray:
    key = path.lstrip("/")
    if key not in h5:
        return np.array([], dtype=float)

    arr = np.asarray(h5[key][...], dtype=float).ravel()
    return arr[np.isfinite(arr)]


def sample_signal(ds: h5py.Dataset, n: int) -> np.ndarray:
    if ds.ndim != 1:
        arr = np.asarray(ds[...], dtype=float).ravel()
        return arr[:n]
    return np.asarray(ds[: min(n, ds.shape[0])], dtype=float)


# =============================================================================
# 1. DATASET INVENTORY
# =============================================================================

def dataset_inventory() -> pd.DataFrame:
    rows = []

    candidates = [
        ("High-frequency Run-1", DATA_ROOT / "Exp-A_HDF5_Run-1.zip"),
        ("High-frequency Run-3", DATA_ROOT / "Exp-A_HDF5_Run-3.zip"),
        ("High-frequency Run-5", DATA_ROOT / "Exp-A_HDF5_Run-5.zip"),
        ("Low-frequency LF", LF_ZIP),
        ("Low-frequency CI", CI_ZIP),
    ]

    for label, path in candidates:
        rows.append(
            {
                "dataset": label,
                "exists": path.exists(),
                "path": str(path),
                "size_bytes": path.stat().st_size if path.exists() else np.nan,
                "size": human_size(path.stat().st_size) if path.exists() else "missing",
            }
        )

    if PHOTO_DIR.exists():
        for p in sorted(PHOTO_DIR.glob("*.zip")):
            rows.append(
                {
                    "dataset": f"Photos: {p.stem}",
                    "exists": True,
                    "path": str(p),
                    "size_bytes": p.stat().st_size,
                    "size": human_size(p.stat().st_size),
                }
            )

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "01_dataset_inventory.csv", index=False)

    print("\n=== DATASET INVENTORY ===")
    print(df[["dataset", "exists", "size"]].to_string(index=False))

    return df


# =============================================================================
# 2. HIGH-FREQUENCY HDF5 STRUCTURE
# =============================================================================

def inspect_representative_hdf5() -> tuple[tempfile.TemporaryDirectory, Path, str]:
    if not HF_ZIP.exists():
        raise FileNotFoundError(
            f"\nHigh-frequency ZIP not ready:\n{HF_ZIP}\n"
            "Wait until .zip.part becomes the completed .zip file."
        )

    temp, h5_path, member = extract_one_hdf5(HF_ZIP)

    with h5py.File(h5_path, "r") as h5:
        tree = pd.DataFrame(hdf5_tree(h5))

    tree.to_csv(OUT / "02_hdf5_structure.csv", index=False)

    print("\n=== REPRESENTATIVE HDF5 FILE ===")
    print(member)
    print(tree.to_string(index=False))

    return temp, h5_path, member


# =============================================================================
# 3. BASIC VIBRATION EDA
# =============================================================================

def basic_signal_stats(x: np.ndarray) -> dict:
    x = x[np.isfinite(x)]

    if len(x) == 0:
        return {}

    rms = np.sqrt(np.mean(x**2))

    return {
        "n_samples": len(x),
        "mean": float(np.mean(x)),
        "std": float(np.std(x)),
        "min": float(np.min(x)),
        "max": float(np.max(x)),
        "peak_to_peak": float(np.ptp(x)),
        "rms": float(rms),
    }


def vibration_eda(h5_path: Path) -> None:
    with h5py.File(h5_path, "r") as h5:

        channels = {
            "Axial - Accel 1": AXIAL_PATH,
            "Radial - Accel 2": RADIAL_PATH,
        }

        stats_rows = []

        for label, path in channels.items():
            key = path.lstrip("/")

            if key not in h5:
                print(f"Missing vibration path: {path}")
                continue

            ds = h5[key]

            # -------------------------------------------------------------
            # Time-domain view: first 0.10 seconds
            # -------------------------------------------------------------
            n_time = int(DEFAULT_FS * 0.10)
            x = sample_signal(ds, n_time)
            t = np.arange(len(x)) / DEFAULT_FS

            fig, ax = plt.subplots(figsize=(10, 4.5))
            ax.plot(t, x)
            ax.set_title(f"{label}: first 0.10 seconds")
            ax.set_xlabel("Time [s]")
            ax.set_ylabel("Acceleration [dataset units]")
            fig.tight_layout()

            safe_label = label.lower().replace(" ", "_").replace("-", "")
            fig.savefig(
                OUT / f"03_time_domain_{safe_label}.png",
                dpi=180,
            )
            plt.close(fig)

            # -------------------------------------------------------------
            # Basic statistics: use first 10 seconds for beginner EDA
            # -------------------------------------------------------------
            n_stats = int(DEFAULT_FS * 10)
            xs = sample_signal(ds, n_stats)

            row = {
                "channel": label,
                "hdf5_path": path,
                **basic_signal_stats(xs),
            }
            stats_rows.append(row)

            # -------------------------------------------------------------
            # Frequency-domain view: first 2 seconds
            # -------------------------------------------------------------
            n_fft = int(DEFAULT_FS * 2)
            xf = sample_signal(ds, n_fft)

            xf = xf - np.mean(xf)

            frequencies = np.fft.rfftfreq(
                len(xf),
                d=1.0 / DEFAULT_FS,
            )

            amplitude = np.abs(
                np.fft.rfft(xf)
            ) / len(xf)

            # Beginner plot: first 5 kHz only.
            mask = frequencies <= 5000

            fig, ax = plt.subplots(figsize=(10, 4.5))
            ax.plot(
                frequencies[mask],
                amplitude[mask],
            )
            ax.set_title(f"{label}: frequency spectrum")
            ax.set_xlabel("Frequency [Hz]")
            ax.set_ylabel("Amplitude")
            fig.tight_layout()
            fig.savefig(
                OUT / f"04_frequency_domain_{safe_label}.png",
                dpi=180,
            )
            plt.close(fig)

        pd.DataFrame(stats_rows).to_csv(
            OUT / "03_basic_vibration_statistics.csv",
            index=False,
        )


# =============================================================================
# 4. CONTEXT VARIABLES
# =============================================================================

def context_eda(h5_path: Path) -> None:
    with h5py.File(h5_path, "r") as h5:

        variables = {
            "PAU Speed": RPM_PATH,
            "PAU Torque": TORQUE_PATH,
            "Temperature": TEMP_PATH,
        }

        summary_rows = []

        for label, path in variables.items():
            x = read_1d(h5, path)

            if len(x) == 0:
                continue

            summary_rows.append(
                {
                    "variable": label,
                    "n": len(x),
                    "mean": np.mean(x),
                    "std": np.std(x),
                    "min": np.min(x),
                    "median": np.median(x),
                    "max": np.max(x),
                }
            )

            fig, ax = plt.subplots(figsize=(9, 4.2))
            ax.plot(np.arange(len(x)), x)
            ax.set_title(f"Context variable: {label}")
            ax.set_xlabel("Sample index")
            ax.set_ylabel(label)
            fig.tight_layout()

            safe = label.lower().replace(" ", "_")
            fig.savefig(
                OUT / f"05_context_{safe}.png",
                dpi=180,
            )
            plt.close(fig)

        pd.DataFrame(summary_rows).to_csv(
            OUT / "05_context_summary.csv",
            index=False,
        )


# =============================================================================
# 5. CONDITION INDICATORS
# =============================================================================

def ci_eda(h5_path: Path) -> None:
    with h5py.File(h5_path, "r") as h5:

        ci_group = get_ci_group(h5)

        if ci_group is None:
            print("No /CI or /CI_4s group found.")
            return

        print(f"\nCondition Indicator group detected: {ci_group}")

        summary_rows = []

        for ci in ["FM4", "NA4", "M6A", "ALR"]:
            path = f"{ci_group}/{ci}"
            x = read_1d(h5, path)

            if len(x) == 0:
                continue

            summary_rows.append(
                {
                    "indicator": ci,
                    "path": path,
                    "n": len(x),
                    "mean": np.mean(x),
                    "std": np.std(x),
                    "min": np.min(x),
                    "median": np.median(x),
                    "max": np.max(x),
                }
            )

            fig, ax = plt.subplots(figsize=(9, 4.2))
            ax.plot(np.arange(len(x)), x)
            ax.set_title(f"Condition Indicator: {ci}")
            ax.set_xlabel("Sample index")
            ax.set_ylabel(ci)
            fig.tight_layout()

            fig.savefig(
                OUT / f"06_ci_{ci.lower()}.png",
                dpi=180,
            )
            plt.close(fig)

        pd.DataFrame(summary_rows).to_csv(
            OUT / "06_condition_indicator_summary.csv",
            index=False,
        )


# =============================================================================
# 6. LOW-FREQUENCY FILE OVERVIEW
# =============================================================================

def inspect_low_frequency() -> None:
    for label, zip_path in [
        ("LF", LF_ZIP),
        ("CI", CI_ZIP),
    ]:

        if not zip_path.exists():
            continue

        with zipfile.ZipFile(zip_path) as zf:
            members = [
                x for x in zf.namelist()
                if x.lower().endswith((".h5", ".hdf5", ".hdf"))
            ]

            print(
                f"\n{label} archive: {zip_path.name} "
                f"contains {len(members)} HDF5 files."
            )

            if not members:
                continue

            temp_dir = tempfile.TemporaryDirectory(
                prefix="phm_lf_"
            )

            target = Path(temp_dir.name) / Path(members[0]).name

            with zf.open(members[0]) as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)

            with h5py.File(target, "r") as h5:
                tree = pd.DataFrame(hdf5_tree(h5))

            tree.to_csv(
                OUT / f"07_{label.lower()}_hdf5_structure.csv",
                index=False,
            )

            temp_dir.cleanup()


# =============================================================================
# 7. PHOTO OVERVIEW
# =============================================================================

def photo_contact_sheet() -> None:
    if not PHOTO_DIR.exists():
        return

    # Use two intuitive stages for the beginner view.
    candidates = list(PHOTO_DIR.glob("*.zip"))

    selected = []

    for p in candidates:
        low = p.name.lower()

        if "0_hours" in low or "0 hours" in low or "test start" in low:
            selected.append(("Test Start", p))

        if "run-5" in low:
            selected.append(("Run-5", p))

    for stage, zip_path in selected:

        with zipfile.ZipFile(zip_path) as zf:

            image_members = [
                n for n in zf.namelist()
                if n.lower().endswith(
                    (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")
                )
            ]

            image_members = sorted(image_members)[:14]

            thumbs = []

            for member in image_members:

                with zf.open(member) as f:
                    raw = f.read()

                try:
                    img = Image.open(io.BytesIO(raw)).convert("RGB")
                except Exception:
                    continue

                img.thumbnail((220, 150))

                tile = Image.new(
                    "RGB",
                    (230, 180),
                    "white",
                )

                x = (230 - img.width) // 2
                tile.paste(img, (x, 5))

                draw = ImageDraw.Draw(tile)
                draw.text(
                    (5, 158),
                    Path(member).stem[:30],
                    fill="black",
                )

                thumbs.append(tile)

            if not thumbs:
                continue

            cols = 7
            rows = int(np.ceil(len(thumbs) / cols))

            sheet = Image.new(
                "RGB",
                (cols * 230, rows * 180 + 35),
                "white",
            )

            draw = ImageDraw.Draw(sheet)
            draw.text(
                (10, 10),
                f"EXP-A photos: {stage}",
                fill="black",
            )

            for i, tile in enumerate(thumbs):
                row, col = divmod(i, cols)

                sheet.paste(
                    tile,
                    (
                        col * 230,
                        35 + row * 180,
                    ),
                )

            safe_stage = stage.lower().replace("-", "_").replace(" ", "_")

            sheet.save(
                OUT / f"08_photos_{safe_stage}.jpg"
            )


# =============================================================================
# 8. SIMPLE README
# =============================================================================

def write_readme() -> None:
    text = """
PHM 2026 - BASIC EDA INTERPRETATION GUIDE
=========================================

1. HIGH-FREQUENCY DATA
Raw vibration is sampled extremely often.
It describes the fast mechanical motion of the gearbox.

In this dataset:
- Accel 1 = axial vibration
- Accel 2 = radial vibration

At this stage we only ask:
- What does the waveform look like?
- Is it centered around zero?
- How large is the vibration?
- Are there spikes?
- Are the two accelerometers different?


2. FREQUENCY DOMAIN
A vibration waveform is measured in time.
The FFT shows which repeating frequencies are present.

At beginner-EDA level we only inspect:
- where strong peaks exist
- whether axial/radial spectra look different
- whether later runs eventually show different frequency structure

Do not call a peak a fault before doing physics-aware analysis.


3. CONTEXT VARIABLES
PAU Speed, PAU Torque and Temperature describe HOW the machine was operated.

They are critical because:
a vibration increase can come from higher speed or higher load,
not necessarily from gear damage.


4. CONDITION INDICATORS
FM4, NA4, M6A and ALR are already-computed gear condition metrics.

Beginner EDA asks:
- what range do they have?
- are they stable or noisy?
- do they vary through time?

Advanced EDA later asks whether they separate Run-1, Run-3 and Run-5.


5. LOW-FREQUENCY DATA
Low-frequency data stores slowly changing / derived information at a much
lower data rate than raw vibration.

It is dramatically smaller and is useful for:
- machine operating condition
- condition indicators
- long-duration degradation trends


6. PHOTOS
The images show the physical gear teeth.

They provide a different modality from the sensor data:
sensor data = indirect machine response
photos      = direct visual evidence of tooth surface condition

The advanced project later connects these two.


7. IMPORTANT
Run-1, Run-3 and Run-5 should initially be described as:
- early lifecycle
- intermediate lifecycle
- late lifecycle

Do not automatically call them:
healthy / damaged / failed.
"""

    (OUT / "README_BASIC_EDA.txt").write_text(
        text.strip(),
        encoding="utf-8",
    )


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 72)
    print("PHM 2026 - BEGINNER / BASIC EDA")
    print("=" * 72)
    print(f"Data root : {DATA_ROOT}")
    print(f"Output    : {OUT}")

    dataset_inventory()
    inspect_low_frequency()
    photo_contact_sheet()
    write_readme()

    # High-frequency-specific analysis only runs after the completed ZIP exists.
    try:
        temp, h5_path, member = inspect_representative_hdf5()

        try:
            vibration_eda(h5_path)
            context_eda(h5_path)
            ci_eda(h5_path)
        finally:
            temp.cleanup()

    except FileNotFoundError as exc:
        print(exc)
        print(
            "\nThe inventory, low-frequency inspection and photo EDA were still created."
        )

    print("\n" + "=" * 72)
    print("BASIC EDA COMPLETE")
    print("=" * 72)
    print(f"Open this folder:\n{OUT}")


if __name__ == "__main__":
    main()
