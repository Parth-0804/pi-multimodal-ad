# Domain-first migration plan

Scope: structural refactoring authorized in full by the latest attached request. No experiments, raw data, existing runs/artifacts, scientific formulas, hyperparameters or conclusions will change. No external Reasoning Record changes. Preflight found no writable repository file descriptors; Task 4 terminal state is complete, and final queue is CLOSED. The status snapshot saying Task 1 paused is superseded by the preserved September 30 closure (discontinued by user).

## Current and proposed structure

- `src/pi_multimodal_ad/**` → `src/phm2026/**`. All  production consumers of these helpers are PHM; Intel foundations implement their own audit in scripts and REASSEMBLE has independent domain code. Do not invent a shared implementation.
- Preserve capability names `datasets`, `data_contracts`, `profiling`, `acquisition`, `targets`, `features`, `preprocessing`, `evaluation`, `reporting`, `utils`, `cli` within PHM.
- Separate RT-DETR into `models/rtdetr/{detection,feasibility,multitask,regression}.py`, PatchTST into `models/patchtst/{model,regression}.py`, fusion into `fusion/{late_fusion,modality_fusion}.py`.
- Generic PHM scripts `dataset`, `features`, `targets`, `training`, `results` → `scripts/phm2026/<capability>`.
- `tests/unit` → `tests/phm2026`, except Intel foundations → `tests/intel_welding` and maintenance → `tests/ops`.
- Keep Intel, REASSEMBLE, thesis validation, ops, presentation, Paderborn and raw-vibration supplementary areas; classify rather than mechanically merge them.
- `src/shared/README.md` is a policy/navigation document only: no Python shared package or speculative empty subdirectories. This fulfills the requested README without misclassifying PHM-only helpers.

## Complete per-file mapping

`path_mapping.csv` enumerates every source, script, test and config file with final destination, actual ownership justification and reference-file evidence. `baseline/source_identities.json` records source SHA256 identities; `/tmp/repository_restructure_preimages.tar.gz` holds small source/config/test preimages for local rollback. No credentials or raw payloads are in this archive. Baseline Git state and protected file identities are in `baseline/`.

## Sequenced migration and checks

1. Run the full existing test suite with importlib collection (duplicate test basenames occur across domains), CPU thread limits and no bytecode/cache writes. Record results before moving.
2. Rename the PHM package as an atomic import namespace group; update classified Python consumers and root downloader import. Run affected tests and import checks.
3. Split only PHM model capabilities and resolve relative imports; run model and evaluation tests.
4. Move PHM CLI scripts, update source-root discovery, module imports and live path references; test safe help entry points.
5. Move tests by domain, update navigation documents and AGENTS architecture references; run full suite and CLI/import checks.
6. Repository-wide reference audit; categorize historical, documentation, compatibility or errors. Verify protected file paths/stat identities and small-evidence hashes against baseline.

## Import and compatibility impact

Canonical imports start `phm2026`; model paths change as mapped. Root `download.py` and PHM tutorial source imports must change. No pip packaging metadata exists; preserve source-tree execution with explicit script bootstraps or `PYTHONPATH=src`. Do not install dependencies. No duplicate implementation or compatibility alias is planned unless concrete historical executable/checkpoint dependencies require one. Frozen manifests retain their original source paths and Git identities; historical reproduction uses the recorded revision.

## Configuration and documentation

Leave `configs/datasets/phm2026.yaml` and `configs/experiments/phm2026_*.yaml` in the intentional dataset/experiment-centric arrangement; existing pins and hashes must remain unchanged. Update live README, REPO_MAP, AGENTS architecture and source documentation/generators where necessary. Leave dated planning checkpoints, historical prompts, tutorials' generated reports and all evidence unchanged; explain old references in an audit. Missing `docs/restructuring/TASKS.md` in old guidance is pre-existing documentation debt; replace its navigation link with this plan.

## Risks and preservation

The working tree is already dirty: preserve every unrelated change, never reset/stash it, and do not commit. Use Git-aware file moves for tracked code; filesystem rename for untracked code. Protect source root resolution (some scripts already use incorrect parent depth), relative model imports, fixture paths, dynamic imports and subprocess commands. Document any pre-existing test/environment failure separately; do not silently fix scientific defects. Protected trees include `runs`, `artifacts`, `experiments`, `archive`, `data`, `gtc-data-experiment`. Full payload hashing is intentionally avoided; baseline stat identity plus hashes of small evidence files supports a bounded preservation check. No costly retraining or data regeneration is authorized by this migration.

## Post-move cache housekeeping

Retired directories contained only ignored `__pycache__/*.pyc` files. Each cache file was added to the migration CSV before reversible relocation into `.cache/repository_restructure/<timestamp>/`; empty old directories were then removed. This avoids misleading old namespace folders without deleting source, caches or evidence. The generated cache archive is not for Git.

## Completion

All phases completed; see FINAL_STRUCTURE.md and VALIDATION_REPORT.md. A durable workspace copy of the original source preimages is now `baseline/source_preimages.tar.gz` (ignored by Git); the `/tmp` copy is supplementary. All original test results and protected file checks are retained.
