# PHM North America 2026

Canonical implementation for the PHM gear-degradation study. Existing scientific formulations, provisional target caveats, preprocessing, splits, models and evaluation behavior are unchanged by the domain migration.

| Capability | Source | Entry points |
|---|---|---|
| Archive acquisition | `acquisition/phm_download.py` | root `download.py` |
| Dataset handling and identities | `datasets/`, `data_contracts/` | `scripts/phm2026/dataset/` |
| Profiling and alignment | `profiling/`, `cli.py` | `scripts/phm2026/dataset/` |
| Target construction | `targets/` | `scripts/phm2026/targets/` |
| Sensor features | `features/`, `preprocessing/` | `scripts/phm2026/features/` |
| RT-DETR | `models/rtdetr/` | `scripts/phm2026/training/train_rtdetr_*.py` |
| PatchTST | `models/patchtst/` | `scripts/phm2026/training/train_patchtst.py` |
| Fusion | `fusion/` | `scripts/phm2026/training/train_late_fusion.py`, `scripts/phm2026/results/sq2_sq3_fusion.py` |
| Evaluation and reports | `evaluation/`, `reporting/` | `scripts/phm2026/results/`, `scripts/presentation/` |
| Configuration and provenance | `utils/` | Used by the PHM entry points above |

Paths in source column are relative to this directory; entry-point paths are repository-relative. Configs: `configs/datasets/phm2026.yaml`, `configs/experiments/phm2026_*.yaml`, `configs/phm2026/`. Tests: `tests/phm2026/`; synthetic fixtures remain `tests/fixtures/`. Evidence: existing `runs/phm2026_*`, `artifacts/phm2026/`, historical `experiments/` and supplementary `tutorials/`; never regenerate or relabel them merely because code moved.

There is no shared-package dependency: current production users of these utilities are PHM-specific. Intel and REASSEMBLE are separate domains. `pyproject.toml` supports an editable install in the existing environment without dependency changes; direct imports then need no PYTHONPATH. CLI scripts retain their source bootstrap. Old `pi_multimodal_ad.*` paths forward to this canonical implementation; see `docs/repository_restructure/COMPATIBILITY_CONTRACT.md`.
