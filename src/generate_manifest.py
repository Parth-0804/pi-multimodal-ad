"""Generate a manifest CSV for the Intel Robotic Welding Multimodal Dataset.

Scans the dataset root (pointed to by INTEL_WELDING_DATA_ROOT or --root) and writes
one row per run/sample with paths to video, audio, sensor, and images.

Usage examples:
  python src/generate_manifest.py --output manifests/intel_welding_manifest.csv
  python src/generate_manifest.py --root "G:/My Drive/00_Masterarbeit/02_Git_WS/Full Dataset" --output manifests/manifest.csv

The script does NOT move or modify raw files.
"""
from pathlib import Path
import os
import argparse
import csv
from typing import Optional, List

VIDEO_EXT = {".avi", ".mp4", ".mov"}
AUDIO_EXT = {".flac", ".wav", ".mp3"}
SENSOR_EXT = {".csv", ".xlsx", ".tdms"}
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}


def find_first_with_ext(p: Path, exts: set) -> Optional[Path]:
    for child in p.iterdir():
        if child.is_file() and child.suffix.lower() in exts:
            return child
    return None


def collect_images(p: Path) -> Optional[str]:
    images_dir = p / "images"
    if images_dir.exists() and images_dir.is_dir():
        return str(images_dir)
    # fallback: collect image files in run folder
    imgs = [str(x) for x in sorted(p.iterdir()) if x.is_file() and x.suffix.lower() in IMAGE_EXT]
    if imgs:
        return ";".join(imgs)
    return None


def scan_dataset(root: Path) -> List[dict]:
    rows = []
    if not root.exists():
        raise FileNotFoundError(f"Dataset root not found: {root}")
    # iterate top-level class/condition folders
    for class_dir in sorted([d for d in root.iterdir() if d.is_dir()]):
        for run_dir in sorted([d for d in class_dir.iterdir() if d.is_dir()]):
            sample_id = run_dir.name
            class_name = class_dir.name
            rel_path = str(run_dir.relative_to(root))
            video = find_first_with_ext(run_dir, VIDEO_EXT)
            audio = find_first_with_ext(run_dir, AUDIO_EXT)
            sensor = find_first_with_ext(run_dir, SENSOR_EXT)
            images = collect_images(run_dir)
            rows.append({
                "sample_id": sample_id,
                "class": class_name,
                "run_path": rel_path,
                "video_path": str(video) if video is not None else "",
                "audio_path": str(audio) if audio is not None else "",
                "sensor_path": str(sensor) if sensor is not None else "",
                "images": images or "",
            })
    return rows


def ensure_parent(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Generate manifest for Intel Robotic Welding dataset")
    parser.add_argument("--root", type=str, default=os.environ.get("INTEL_WELDING_DATA_ROOT"),
                        help="Path to dataset root. If omitted, reads INTEL_WELDING_DATA_ROOT env var.")
    parser.add_argument("--output", type=str, default="manifests/intel_welding_manifest.csv",
                        help="Output CSV path")
    args = parser.parse_args()
    if not args.root:
        parser.error("Dataset root not specified. Set INTEL_WELDING_DATA_ROOT or pass --root.")
    root = Path(args.root)
    rows = scan_dataset(root)
    outp = Path(args.output)
    ensure_parent(outp)
    fieldnames = ["sample_id", "class", "run_path", "video_path", "audio_path", "sensor_path", "images"]
    with outp.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"Wrote manifest with {len(rows)} rows to {outp}")


if __name__ == "__main__":
    main()
