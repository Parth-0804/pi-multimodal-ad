# Repository map

Start with **[implementations/](implementations/README.md)** for a human-facing
view of every dataset, cross-dataset work and general tools. Each dataset guide
uses HANDOVER's stage order and links code, protocols and retained evidence.
Unaffected implementation files are stored under `implementations/`; old code
paths remain compatibility symlinks. Native data, run evidence and training-job
dependencies retain their original locations.

PHM experiment walkthrough: [RT-DETR Model 1, from data to saved results](experiments/phm2026/README.md). Follow the numbered 00–03 folders or the single-sample trace.

REASSEMBLE experiment walkthroughs: [RT-DETR, PatchTST and core fusion in numbered folders](experiments/reassemble/README.md). Start there to follow data → preprocessing → models → predictions → results.

Domain first, then capability. Detailed tree, old-to-new imports and validation: [FINAL_STRUCTURE.md](docs/repository_restructure/FINAL_STRUCTURE.md). Working boundaries: [AGENTS.md](AGENTS.md).

| Domain/purpose | Implementation | Scripts | Configs | Tests | Evidence |
|---|---|---|---|---|---|
| PHM 2026 | `implementations/PHM2026/src/phm2026/` | `implementations/PHM2026/scripts/{dataset,features,targets,training,results}/` | `implementations/PHM2026/configs/`, `configs/datasets/phm2026.yaml`, `configs/experiments/phm2026_*.yaml` | `implementations/PHM2026/tests/` | existing `runs/phm2026_*`, `artifacts/phm2026/` |
| Intel Welding | `implementations/INTEL_WELDING/src/intel_welding/` namespace; implemented audit in scripts | `implementations/INTEL_WELDING/scripts/` | `implementations/INTEL_WELDING/configs/` | `implementations/INTEL_WELDING/tests/` | existing Intel artifacts and historical archive |
| MSM | `implementations/MSM/src/` and shared external-evaluation code | dataset adapters | `MSM/04_experiment_protocol/` | `implementations/MSM/tests/` | `MSM/06_evaluation_results/`, `MSM/09_final_reports/` |
| HANDOVER | `implementations/HANDOVER/src/` and shared external-evaluation code | dataset adapters | `HANDOVER/04_experiment_protocol/` and study-local protocol | `implementations/HANDOVER/tests/` | `HANDOVER/experiments/common_support_v2/` |
| REBOOT | `implementations/REBOOT/src/` | feasibility and audit tools | retained feasibility records | `implementations/REBOOT/tests/` | `REBOOT/07_research_decision/`, `REBOOT/runs/` |
| VIFAILBACK | `VIFAILBACK/src/`, study-local source | `VIFAILBACK/scripts/`, study-local scripts | `VIFAILBACK/configs/` and study-local protocol | `VIFAILBACK/tests/` and study-local tests | `VIFAILBACK/experiments/` and numbered study stages |
| REASSEMBLE | `src/reassemble/` | `scripts/reassemble/` | `configs/reassemble/` | `tests/reassemble/` | `runs/reassemble/`, `artifacts/reassemble/` |
| Cross-dataset evaluation | `implementations/cross_dataset/src/external_eval/` | module entry points | `CROSS_DATASET_COMPARISON/configs/` | `implementations/cross_dataset/tests/` | `CROSS_DATASET_COMPARISON/`, dataset-specific workspaces |
| Thesis validation and synthesis | `implementations/general/scripts/thesis/` | same | audit prompts/config snapshots | `implementations/general/tests/thesis/` | `artifacts/thesis/` |
| Maintenance | `implementations/general/scripts/ops/` | same | CLI arguments | `implementations/general/tests/ops/` | task-specific manifests/reports |
| Presentation | PHM reporting plus presentation script | `implementations/general/scripts/presentation/` | experiment config | PHM reporting tests | `presentation_assets/`, tutorials |
| Supplementary PHM raw vibration | `implementations/general/scripts/rawvib/` | same | script-defined, preserved | existing checks | existing supplementary evidence |
| Paderborn transfer | `implementations/general/scripts/paderborn/` | same | existing transfer settings | existing checks | existing transfer evidence |

Ancillary reports, historical planning notes and workflow material: [reports/extras/](reports/extras/README.md).

PHM models: `implementations/PHM2026/src/phm2026/models/rtdetr/`, `implementations/PHM2026/src/phm2026/models/patchtst/`; fusion: `implementations/PHM2026/src/phm2026/fusion/`. Dataset adapters remain `datasets/`, typed identities `data_contracts/`, structural inspection `profiling/`. No speculative empty capability directories were added.

Scripts run from repository root and PHM entry points locate `src/` themselves. Direct imports work after the minimal editable install in `pyproject.toml`; legacy `pi_multimodal_ad.*` imports forward to the canonical implementation. `tests/fixtures/` contains tiny synthetic inputs and stays in place.

Preserved history: all `runs/`, `artifacts/`, `experiments/`, `archive/`, raw data and Task 4 recovery evidence. Dated `docs/planning/`, historical prompts, tutorial reports and run manifests can retain old source paths; use their original Git revision for historical reproduction. The compatibility namespace and legacy `scripts/{dataset,features,targets,training,results}/` contain forwarding only. The latest [relocation manifest](reports/extras/repository_organization_20261119/RELOCATION_MANIFEST.json) records physical locations and original hashes; the older migration CSV retains the earlier interface mapping.

Cache-retention exception (researcher approval, 2026-10-26): the September frozen-prefix
arrays and older shared pixel-cache arrays were evicted. Historical
metadata and research results remain preserved. Check the [current retention and
recovery record](docs/maintenance/REASSEMBLE_CACHE_RETENTION.md) before replaying
these studies; an old completion flag does not prove the arrays are still present.

For former paths such as `src/pi_multimodal_ad/`, `scripts/training/`, or `tests/unit/`, see [path_mapping.csv](docs/repository_restructure/path_mapping.csv). Current interface support is defined in [COMPATIBILITY_CONTRACT.md](docs/repository_restructure/COMPATIBILITY_CONTRACT.md); validation in [COMPATIBILITY_VALIDATION.md](docs/repository_restructure/COMPATIBILITY_VALIDATION.md).

Legacy forwarding locations: `src/pi_multimodal_ad/` and `scripts/{dataset,features,targets,training,results}/`. The former domain source/script/test directories are relative symlinks to the moved implementations; the REASSEMBLE dependency paths remain physical directories.
