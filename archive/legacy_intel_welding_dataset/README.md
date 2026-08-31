# Legacy: Intel Robotic Welding Multimodal Dataset

**Status: historical. Not part of the active PHM North America 2026 pipeline.**

## What this was

Before the project settled on the PHM North America 2026 Data Challenge
(gear-tooth / PAU degradation prediction from images and vibration sensors —
the subject of the rest of this repository), the thesis started around a
different dataset: the **Intel Robotic Welding Multimodal Dataset**
(~41 GB, video + audio + sensor logs + post-weld images of robotic welds,
hosted on Hugging Face). The project pivoted away from it before any model
training happened here; only exploratory scaffolding was ever built.

This directory preserves that scaffolding as a historical record, per the
archive policy below. It is not maintained and should not be run against the
current codebase.

## What's in here

| File | Original location | What it did |
|---|---|---|
| `create_intel_manifest.py` | `src/create_intel_manifest.py` | One of two overlapping manifest generators for the raw welding archive. |
| `generate_manifest.py` | `src/generate_manifest.py` | The other manifest generator (incompatible schema/defaults from the one above — never reconciled). |
| `load_dataset.py` | `src/load_dataset.py` | Manifest-based loader for video/audio/sensor/image files. |
| `dataset_paths.yaml` | `configs/dataset_paths.yaml` | Path configuration for the welding dataset (`INTEL_WELDING_DATA_ROOT`). |
| `dataset_instructions.md` | `docs/dataset_instructions.md` | Download/placement instructions for the welding dataset. |
| `dataset_overview.md` | `docs/dataset_overview.md` | Pointer doc to the instructions above. |
| `01_data_exploration.ipynb` | `notebooks/01_data_exploration.ipynb` | A single-cell placeholder notebook (prints the pandas version; nothing else). |

## Why the project moved on

The root `README.md` used to open with a survey of candidate datasets for
physics-informed multimodal anomaly detection research. That survey is
preserved below, since it's genuine research context for why PHM North
America 2026 was chosen over the alternatives — it just no longer belongs at
the top of the project's front door now that PHM2026 is the active work.

### Dataset survey (moved from the original root README)

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

Of these, PHM North America 2026 (gear-tooth PAU degradation, real
challenge data, an active competition with organizer-defined scope) became
the actual thesis vehicle. See the root `README.md` and `AGENTS.md` for the
active project.

## Archive policy this move follows

This directory's contents are governed by the general archive policy — see
[`../README.md`](../README.md). In short: archiving is not deletion, this
material is not to be presented as part of the active pipeline, and nothing
here should be imported by or run against current PHM2026 code.
