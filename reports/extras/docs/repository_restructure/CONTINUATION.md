# Repository restructuring handoff

**COMPLETE — no research run or migration phase remains queued.**

PHM code is `src/phm2026/`; PHM scripts `scripts/phm2026/`; tests `tests/phm2026/`, `tests/intel_welding/`, `tests/ops/`. Intel and REASSEMBLE remain separate. No shared implementation was justified. Canonical model paths are in `FINAL_STRUCTURE.md` and the complete mapping is `path_mapping.csv`.

272 baseline and 272 final tests passed. Imports, CLI checks and executable AST checks passed. All 40,500 pre-existing protected files are unchanged. Downloader help added a disclosed zero-download parse provenance record; no training, downloads or Task 4 reruns occurred. Global staged whitespace warnings belong to pre-existing protected evidence and were preserved.

Read `FINAL_STRUCTURE.md`, `VALIDATION_REPORT.md`, `CORRECTIONS.md`, `provenance.json` and `output_manifest.json`. Original uncommitted work remains intact. `baseline/source_preimages.tar.gz` and baseline identities support workspace-local inspection/rollback; they are intentionally ignored by Git. Do not reset or restore the whole working tree. One-time migration helper phases must not be rerun on the migrated tree.

Current Git HEAD did not change. Moves are staged; edits/new docs remain unstaged/untracked. Next action is human review of this structural change and, if separately requested, a scoped commit. No experiment execution is needed to finish this request.
