# pi-multimodal-ad
This repository contains the research work and experimental implementations developed as part of a Master’s thesis focused on physics‑informed multi‑modal transformer architectures for robust industrial anomaly detection.

## Possible Dataset Overview

| Dataset | Mechanical Domain | Modalities | Relevance for Uncertainty / Robustness Research | Labels / Annotations | Access / Notes | Link |
|--------|-------------------|-----------|-----------------------------------------------|----------------------|----------------|------|
| **Intel Robotic Welding Multimodal Dataset** | Robotic welding / production floor | Video, audio, time-series welding sensor data, post-weld images (5 per weld) | Synchronized multimodal data makes it suitable for studying **missing modalities**, **sensor misalignment**, and robustness under incomplete inputs | ~4,000 annotated samples; defect categories available in manifest | Hosted on Hugging Face; gated access, research-use conditions apply | [Dataset Link](https://huggingface.co/datasets/amr-lopezjos/Intel_Robotic_Welding_Multimodal_Dataset) |
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
