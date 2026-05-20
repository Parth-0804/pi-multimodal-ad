# Intel Robotic Welding Multimodal Dataset (Access Instructions)

This repository does not contain the Intel Robotic Welding Multimodal Dataset because of its large size and license restrictions.

Official source:
https://huggingface.co/datasets/IntelLabs/Intel_Robotic_Welding_Multimodal_Dataset

Instructions
- Download the dataset from the Hugging Face dataset page (may require acceptance of terms).
- Place the dataset on your local machine or in Google Drive.

Environment variable
- Set the environment variable `INTEL_WELDING_DATA_ROOT` to point to the dataset root directory.

Examples
- Bash (Linux / macOS):

```bash
export INTEL_WELDING_DATA_ROOT=/path/to/intel_welding_dataset
```

- Windows PowerShell:

```powershell
$env:INTEL_WELDING_DATA_ROOT = 'C:\path\to\intel_welding_dataset'
```

Usage
- Update `configs/dataset_paths.yaml` or your experiment scripts to reference the `INTEL_WELDING_DATA_ROOT` environment variable.
- If using Google Drive, mount or sync the folder and set the env var to the mounted path.

Notes
- The dataset is large; keep it out of version control and respect license terms when sharing derived artifacts.
