# pi-multimodal-ad
 while starting to work on code : source ~/thesis/.venv/bin/activate
This repository contains the research work and experimental implementations developed as part of a Master's thesis focused on physics-informed multi-modal transformer architectures for robust industrial anomaly detection.

## Dataset Information

### Overview

This project uses the **Intel Robotic Welding Multimodal Dataset** (~41 GB). The full dataset is **NOT stored in this GitHub repository** for practical and licensing reasons.

**Important:**
- The raw dataset is stored locally at: `data/Full Dataset/`
- The folder `data/Full Dataset/` is explicitly ignored by Git (see `.gitignore`)
- The file `data/DO_NOT_COMMIT_DATA_HERE.txt` is only a placeholder
- Small manifest samples and generated metadata are tracked in `data_sample/`

### Dataset Location

Download the dataset from:
```
https://huggingface.co/datasets/IntelLabs/Intel_Robotic_Welding_Multimodal_Dataset
```

**Local placement:**
After downloading, place the dataset in the `data/Full Dataset/` folder of this repository. The folder will be ignored by Git automatically.

### Expected Raw Dataset Structure

```
data/
├── Full Dataset/
│   ├── 3_good_weld_butt/
│   │   ├── 01-02-23-0022-00/
│   │   │   ├── images/
│   │   │   ├── 01-02-23-0022-00.avi
│   │   │   ├── 01-02-23-0022-00.csv or .xlsx
│   │   │   └── 01-02-23-0022-00.flac
│   │   ├── 01-02-23-0023-00/
│   │   └── 01-02-23-0024-00/
│   ├── burnthrough_weld_8_12-04-22_butt_joint/
│   ├── excessive_convexity_1_03-04-23_Fe410/
│   ├── excessive_penetration_1_02-19-23_Fe410/
│   └── ...
├── DO_NOT_COMMIT_DATA_HERE.txt
└── (other small samples in data_sample/)
```

**Interpretation:**
- Top-level folder: welding condition / defect class / experiment group
- Second-level folder: individual weld run / sample (one multimodal measurement)
- Inside each run: video (`.avi`), audio (`.flac`), sensor logs (`.csv` / `.xlsx`), and post-weld images

### Key Principles

1. **Do NOT manually rename or reorganize raw dataset folders.** The manifest generator scans in-place.
2. **Do NOT push the `data/Full Dataset/` folder to GitHub.** It will be ignored automatically.
3. **Use the manifest CSV** instead of copying/restructuring files. The manifest points to raw files; loaders open them at runtime.
4. **Keep code, docs, configs, and notebooks in the repo.** Only raw dataset files are external.

### Getting Started with the Dataset

#### Step 1: Download the Dataset
Download from Hugging Face and place in `data/Full Dataset/`.

#### Step 2: Generate the Manifest
Run the manifest generator script to create a CSV file that lists all samples and their file paths:

```powershell
# Navigate to repo root
cd <repo-root>

# Set environment variable (optional, defaults to data/Full Dataset/)
$env:INTEL_WELDING_DATA_ROOT = 'data/Full Dataset'

# Run the manifest generator
python src/create_intel_manifest.py

# Output: data_sample/intel_welding_manifest.csv
```

#### Step 3: Use the Manifest in Your Code
Your data loading code should read the manifest CSV and open files from the listed paths:

```python
import pandas as pd

# Load manifest
manifest = pd.read_csv('data_sample/intel_welding_manifest.csv')

# For each row, open video, audio, sensor, images from the listed paths
for idx, row in manifest.iterrows():
    video_path = row['video_path']
    audio_path = row['audio_path']
    sensor_path = row['sensor_path']
    image_dir = row['image_dir']
    # ... load and process files at runtime
```

### Configuration

See `configs/dataset_paths.yaml` for dataset path settings.

---

## Possible Dataset Overview

| Dataset | Mechanical Domain | Modalities | Relevance for Uncertainty / Robustness Research | Labels / Annotations | Access / Notes | Link |
|--------|-------------------|-----------|-----------------------------------------------|----------------------|----------------|------|
| **Intel Robotic Welding Multimodal Dataset** | Robotic welding / production floor | Video, audio, time-series welding sensor data, post-weld images (5 per weld) | Synchronized multimodal data makes it suitable for studying **missing modalities**, **sensor misalignment**, and robustness under incomplete inputs | ~4,000 annotated samples; defect categories available in manifest | Hosted on Hugging Face; gated access, research-use conditions apply | [Dataset Link](https://huggingface.co/datasets/IntelLabs/Intel_Robotic_Welding_Multimodal_Dataset) |
| **IMAD-DS: Industrial Multi-Sensor Anomaly Detection under Domain Shift** | Robotic arm + brushless motor | Microphone (16 kHz), 3-axis accelerometer (6.7 kHz), 3-axis gyroscope (6.7 kHz) | Designed for **domain shift research**, including environmental changes and background noise variation across source and target domains | Normal / abnormal labels; weak labels; machine classes include RoboticArm and BrushlessMotor | Available on Zenodo under CC BY-SA 4.0; includes train/test folders and parquet/csv mappings | [Dataset Link](https://zenodo.org/records/12665499) |
| **Paderborn Bearing Dataset (KAt DataCenter)** | Rolling bearings / rotating machinery | Motor current, vibration, speed, torque, radial load, temperature | Multiple operating conditions make it useful for **condition transfer**, **domain adaptation**, and robustness evaluation | Healthy and damaged bearing states with systematic fault descriptions | Official university dataset; data provided in MATLAB format | [Dataset Link](https://mb.uni-paderborn.de/en/kat/research/bearing-datacenter/data-sets-and-download) |
| **MAFAULDA (Machinery Fault Database)** | Rotating machinery fault simulator | Tachometer, multiple accelerometer axes, microphone (8 channels per sequence) | Supports testing across **different speeds**, **fault types**, and changing operating conditions | Includes normal, imbalance, misalignment, and bearing fault states | Official dataset page; also frequently mirrored on Kaggle | [Dataset Link](https://www02.smt.ufrj.br/~offshore/mfs/page_01.html) |
| **Bearing Ring Grinder Dataset (SKF SGB55 Grinding Machine)** | Grinding / bearing manufacturing | Vibration, acoustic emission, force, temperature, numerical controller parameters, quality measurements | Multi-sensor industrial process data enables experiments with **noisy sensors**, **missing streams**, and condition variability | Quality parameters and process measurements provided; suitable for failure classification use cases | Raw signals in TDMS format along with `process_data.csv` and quality CSV files | [Dataset Link](https://researchdata.se/en/catalogue/dataset/2022-136-1/1) |
| **Multi-Sensor CNC Tool Wear Dataset** | CNC machining / tool wear monitoring | Cutting force (Fx, Fy, Fz), triaxial vibration, acoustic emission (AE) | Wear progression makes it useful for studying **degradation**, **concept drift**, and predictive maintenance robustness | Includes continuous flank wear value (`VB_mm`) and categorical `Wear_Class` | Hosted on Kaggle | [Dataset Link](https://www.kaggle.com/datasets/ziya07/multi-sensor-cnc-tool-wear-dataset) |
| **CNC Machining Benchmark (Bosch Research)** | Brownfield CNC milling machines | Triaxial accelerometer vibration (2 kHz) | Useful as a strong **single-modality baseline** with anomaly labels across machines and processes | Binary labels: good (normal) vs bad (anomalous) | Mainly vibration-only, so less multimodal than other datasets | [Dataset Link](https://github.com/boschresearch/CNC_Machining) |
| **Open Milling Dataset (14 tools, 968 cycles)** | CNC milling / tool life monitoring | Vibration and current | Run-to-failure setup supports research on **tool degradation**, **uncertainty across lifecycle stages**, and prognostics | Includes metadata for cycles; intended for tool condition classification and tool life estimation | Described in a Scientific Data article | [Dataset Link](https://www.nature.com/articles/s41597-025-04923-y) |
| **Industrial Robotic Arm Anomaly Dataset** | Industrial robotic arm motion monitoring | IMU and quaternion streams | Suitable for testing robustness across different motion tasks and real-time anomaly scenarios | Anomalies described in the paper, including collisions and joint-velocity deviations | Dataset referenced in the associated paper | [Dataset Link](https://iotgarage.net/publications/pdfs/Kayan2025a.pdf) |

## Notes

- The main focus of this collection is on datasets relevant to:
  - **multimodal industrial sensing**
  - **anomaly detection**
  - **fault diagnosis**
  - **domain shift / robustness**
  - **uncertainty-aware learning in mechanical systems**

- Some datasets are fully multimodal, while others are partially multimodal or strong baselines for comparison.

## Possible Filtering for Thesis Use

### 1. Closest to the welding / multimodal manufacturing use case
- Intel Robotic Welding Multimodal Dataset
- IMAD-DS
- Bearing Ring Grinder Dataset
- Multi-Sensor CNC Tool Wear Dataset

### 2. Strong datasets for robustness / uncertainty experiments
- IMAD-DS
- Paderborn Bearing Dataset
- MAFAULDA
- Open Milling Dataset

### 3. Useful baseline datasets
- CNC Machining Benchmark (Bosch Research)
- Industrial Robotic Arm Anomaly Dataset
