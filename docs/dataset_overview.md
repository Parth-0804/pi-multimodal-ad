# Dataset Overview

Add a brief description of the dataset(s) used in this project, expected formats, and where to place raw files (see `data/`).

For the Intel Robotic Welding Multimodal Dataset, see `docs/dataset_instructions.md` for download and placement instructions, and set the `INTEL_WELDING_DATA_ROOT` environment variable to point to the dataset root.

Manifest-based pipeline guidance

- Generate a manifest CSV using `src/generate_manifest.py`. The manifest contains one row per run and lists paths to video, audio, sensor logs, and images.
- Training and evaluation code should read the manifest and load files on-the-fly using the listed paths. This avoids copying or restructuring raw files and keeps the repository small.
- Example data loader flow:
	1. Read manifest row (sample_id, run_path, video_path, ...).
 2. Open sensor CSV or XLSX, load audio file if needed, and sample frames from `video_path` or use `images` paths.
 3. Preprocess/augment in-memory and feed to model.

Advantages:
- Keeps raw data out of the repo.
- Reproducible experiments (manifest is a compact, versionable pointer to raw data).
- Easy to filter or create dataset splits by manipulating the manifest CSV.
