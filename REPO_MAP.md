# Repository map

Domain first, then capability. Detailed tree, old-to-new imports and validation: [FINAL_STRUCTURE.md](docs/repository_restructure/FINAL_STRUCTURE.md). Working boundaries: [AGENTS.md](AGENTS.md).

| Domain/purpose | Implementation | Scripts | Configs | Tests | Evidence |
|---|---|---|---|---|---|
| PHM 2026 | `src/phm2026/` | `scripts/phm2026/{dataset,features,targets,training,results}/` | `configs/phm2026/`, `configs/datasets/phm2026.yaml`, `configs/experiments/phm2026_*.yaml` | `tests/phm2026/` | existing `runs/phm2026_*`, `artifacts/phm2026/` |
| Intel Welding | `src/intel_welding/` namespace; implemented audit in scripts | `scripts/intel_welding/` | `configs/intel_welding/` | `tests/intel_welding/` | existing Intel artifacts and historical archive |
| REASSEMBLE | `src/reassemble/` | `scripts/reassemble/` | `configs/reassemble/` | `tests/reassemble/` | `runs/reassemble/`, `artifacts/reassemble/` |
| Thesis validation and synthesis | `scripts/thesis/` | same | audit prompts/config snapshots | `tests/thesis/` | `artifacts/thesis/` |
| Maintenance | `scripts/ops/` | same | CLI arguments | `tests/ops/` | task-specific manifests/reports |
| Presentation | PHM reporting plus presentation script | `scripts/presentation/` | experiment config | PHM reporting tests | `presentation_assets/`, tutorials |
| Supplementary PHM raw vibration | `scripts/rawvib/` | same | script-defined, preserved | existing checks | existing supplementary evidence |
| Paderborn transfer | `scripts/paderborn/` | same | existing transfer settings | existing checks | existing transfer evidence |
| Shared | `src/shared/README.md` admission policy only | none | none | none | none |

PHM models: `src/phm2026/models/rtdetr/`, `src/phm2026/models/patchtst/`; fusion: `src/phm2026/fusion/`. Dataset adapters remain `datasets/`, typed identities `data_contracts/`, structural inspection `profiling/`. No speculative empty capability directories were added.

Scripts run from repository root and PHM entry points locate `src/` themselves. Direct imports work after the minimal editable install in `pyproject.toml`; legacy `pi_multimodal_ad.*` imports forward to the canonical implementation. `tests/fixtures/` contains tiny synthetic inputs and stays in place.

Preserved history: all `runs/`, `artifacts/`, `experiments/`, `archive/`, raw data and Task 4 recovery evidence. Dated `docs/planning/`, historical prompts, tutorial reports and run manifests can retain old source paths; use their original Git revision for historical reproduction and the migration CSV for current navigation. The compatibility namespace and old PHM script paths contain forwarding only.

For former paths such as `src/pi_multimodal_ad/`, `scripts/training/`, or `tests/unit/`, see [path_mapping.csv](docs/repository_restructure/path_mapping.csv). Current interface support is defined in [COMPATIBILITY_CONTRACT.md](docs/repository_restructure/COMPATIBILITY_CONTRACT.md); validation in [COMPATIBILITY_VALIDATION.md](docs/repository_restructure/COMPATIBILITY_VALIDATION.md).

Legacy forwarding locations: `src/pi_multimodal_ad/` and `scripts/{dataset,features,targets,training,results}/`. Canonical code remains in the domain-owned locations above.
