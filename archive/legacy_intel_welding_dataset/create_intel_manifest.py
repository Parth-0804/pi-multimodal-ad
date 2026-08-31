"""Generate a manifest CSV for the Intel Robotic Welding Multimodal Dataset.

Scans the dataset root (INTEL_WELDING_DATA_ROOT env var or data/Full Dataset/) 
and creates a comprehensive manifest CSV with paths and metadata for each weld run.

Usage:
  python src/create_intel_manifest.py
  python src/create_intel_manifest.py --root "data/Full Dataset"
  python src/create_intel_manifest.py --output "data_sample/custom_manifest.csv"

The script does NOT move or modify raw files.
"""

import os
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import csv
import re

try:
    import pandas as pd
except ImportError:
    pd = None


# File extension mappings
VIDEO_EXT = {".avi", ".mp4", ".mov", ".mkv"}
AUDIO_EXT = {".flac", ".wav", ".mp3"}
SENSOR_EXT = {".csv", ".xlsx", ".xls", ".json", ".txt", ".tdms"}
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

# Label normalization mapping: raw folder name patterns -> normalized label
LABEL_MAPPING = {
    r"(?:3_)?good_weld": "good_weld",
    r"(?:good|normal)": "good_weld",
    r"burnthrough|burn.?through": "burn_through",
    r"crater.?crack": "crater_cracks",
    r"excessive.?convexity|convexity": "excessive_convexity",
    r"excessive.?penetration|penetration": "excessive_penetration",
    r"porosity": "porosity",
    r"overlap": "overlap",
    r"undercut": "undercut",
    r"spatter": "spatter",
    r"warp|warping": "warping",
}


def normalize_label(folder_name: str) -> str:
    """Normalize a folder name to a standard label."""
    folder_lower = folder_name.lower()
    for pattern, label in LABEL_MAPPING.items():
        if re.search(pattern, folder_lower):
            return label
    return "unknown"


def find_first_with_ext(directory: Path, extensions: set) -> Optional[Path]:
    """Find first file in directory with one of the given extensions."""
    if not directory.exists() or not directory.is_dir():
        return None
    try:
        for item in sorted(directory.iterdir()):
            if item.is_file() and item.suffix.lower() in extensions:
                return item
    except (OSError, PermissionError):
        pass
    return None


def count_images(run_dir: Path) -> Tuple[Optional[str], int]:
    """
    Count images in the images/ subdirectory and return (image_dir_path, count).
    Returns (None, 0) if no images found.
    """
    images_dir = run_dir / "images"
    if images_dir.exists() and images_dir.is_dir():
        try:
            images = [f for f in images_dir.iterdir()
                     if f.is_file() and f.suffix.lower() in IMAGE_EXT]
            count = len(images)
            if count > 0:
                return str(images_dir), count
        except (OSError, PermissionError):
            pass
    return None, 0


def scan_dataset(root: Path) -> List[Dict]:
    """Scan dataset and return list of sample records."""
    rows = []
    
    if not root.exists():
        raise FileNotFoundError(f"Dataset root not found: {root}")
    
    # Iterate top-level class/condition folders
    try:
        condition_dirs = sorted([d for d in root.iterdir() if d.is_dir()])
    except (OSError, PermissionError) as e:
        print(f"Error reading dataset root: {e}")
        return rows
    
    for condition_dir in condition_dirs:
        condition_name = condition_dir.name
        label = normalize_label(condition_name)
        
        # Iterate run/sample folders inside condition folder
        try:
            run_dirs = sorted([d for d in condition_dir.iterdir() if d.is_dir()])
        except (OSError, PermissionError) as e:
            print(f"Warning: Could not read condition folder {condition_dir}: {e}")
            continue
        
        for run_dir in run_dirs:
            run_id = run_dir.name
            rel_path = str(run_dir.relative_to(root))
            
            # Detect file types
            video = find_first_with_ext(run_dir, VIDEO_EXT)
            audio = find_first_with_ext(run_dir, AUDIO_EXT)
            sensor = find_first_with_ext(run_dir, SENSOR_EXT)
            image_dir, num_images = count_images(run_dir)
            
            rows.append({
                "condition_folder": condition_name,
                "run_id": run_id,
                "label": label,
                "run_path": rel_path,
                "video_path": str(video) if video else "",
                "audio_path": str(audio) if audio else "",
                "sensor_path": str(sensor) if sensor else "",
                "image_dir": image_dir if image_dir else "",
                "num_images": num_images,
                "has_video": 1 if video else 0,
                "has_audio": 1 if audio else 0,
                "has_sensor": 1 if sensor else 0,
                "has_images": 1 if image_dir else 0,
            })
    
    return rows


def print_statistics(rows: List[Dict]) -> None:
    """Print summary statistics from manifest rows."""
    if not rows:
        print("No samples found.")
        return
    
    print(f"\n{'='*70}")
    print(f"Dataset Summary")
    print(f"{'='*70}")
    print(f"Total samples: {len(rows)}")
    
    # Label distribution
    label_counts = {}
    for row in rows:
        label = row["label"]
        label_counts[label] = label_counts.get(label, 0) + 1
    
    print(f"\nLabel distribution:")
    for label in sorted(label_counts.keys()):
        count = label_counts[label]
        pct = 100.0 * count / len(rows)
        print(f"  {label:30s}: {count:4d} ({pct:5.1f}%)")
    
    # Modality counts
    has_video = sum(1 for r in rows if r["has_video"])
    has_audio = sum(1 for r in rows if r["has_audio"])
    has_sensor = sum(1 for r in rows if r["has_sensor"])
    has_images = sum(1 for r in rows if r["has_images"])
    
    print(f"\nModality coverage:")
    print(f"  Video:  {has_video:4d} / {len(rows)} ({100.0*has_video/len(rows):5.1f}%)")
    print(f"  Audio:  {has_audio:4d} / {len(rows)} ({100.0*has_audio/len(rows):5.1f}%)")
    print(f"  Sensor: {has_sensor:4d} / {len(rows)} ({100.0*has_sensor/len(rows):5.1f}%)")
    print(f"  Images: {has_images:4d} / {len(rows)} ({100.0*has_images/len(rows):5.1f}%)")
    
    # Missing modality counts
    no_video = sum(1 for r in rows if not r["has_video"])
    no_audio = sum(1 for r in rows if not r["has_audio"])
    no_sensor = sum(1 for r in rows if not r["has_sensor"])
    no_images = sum(1 for r in rows if not r["has_images"])
    
    print(f"\nMissing modalities:")
    print(f"  No video:  {no_video:4d}")
    print(f"  No audio:  {no_audio:4d}")
    print(f"  No sensor: {no_sensor:4d}")
    print(f"  No images: {no_images:4d}")
    
    print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Generate manifest for Intel Robotic Welding Multimodal Dataset"
    )
    parser.add_argument(
        "--root",
        type=str,
        default=os.environ.get(
            "INTEL_WELDING_DATA_ROOT",
            "data/Full Dataset"
        ),
        help="Path to dataset root. Default: INTEL_WELDING_DATA_ROOT env var or data/Full Dataset"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data_sample/intel_welding_manifest.csv",
        help="Output CSV path (default: data_sample/intel_welding_manifest.csv)"
    )
    args = parser.parse_args()
    
    root = Path(args.root)
    output_path = Path(args.output)
    
    print(f"Scanning dataset root: {root}")
    
    # Scan dataset
    rows = scan_dataset(root)
    
    if not rows:
        print("No samples found in dataset. Exiting.")
        return
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write CSV
    fieldnames = [
        "condition_folder", "run_id", "label", "run_path",
        "video_path", "audio_path", "sensor_path", "image_dir",
        "num_images", "has_video", "has_audio", "has_sensor", "has_images"
    ]
    
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    
    print(f"Manifest written to: {output_path}")
    
    # Print statistics
    print_statistics(rows)
    
    # If pandas is available, optionally show a preview
    if pd is not None:
        df = pd.read_csv(output_path)
        print("\nManifest preview (first 5 rows):")
        print(df.head().to_string(index=False))
    else:
        print("\nNote: Install pandas for preview. Manifest CSV ready for analysis.")


if __name__ == "__main__":
    main()
