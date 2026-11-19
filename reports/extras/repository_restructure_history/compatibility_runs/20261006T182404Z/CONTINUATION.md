# Backward compatibility handoff

**COMPLETE — no compatibility phase or research run remains queued.**

Canonical code remains `src/phm2026/`; legacy namespace `src/pi_multimodal_ad/` contains forwarding only. 53 old module/package paths and 39 old script paths are supported, derived from the frozen mapping. No source directories were moved. Editable installation in `ma_thesis_env` succeeded with no index/dependency access; direct imports work without PYTHONPATH.

Full suite: 386 passed (272 prior + 114 new), six existing Torch warnings. Every CLI help pair matches stdout/stderr/exits. 40,645 protected files and 12,608 small hashes are unchanged; zero protected files added. All 279 prior dependency versions are unchanged. Git HEAD/index unchanged; no commit/push.

Read `COMPATIBILITY_CONTRACT.md`, `COMPATIBILITY_VALIDATION.md`, `compatibility_matrix.csv`, and `docs/repository_restructure/compatibility_runs/20261006T182404Z/task_manifest.json`. Audit baseline/preimages remain in `docs/repository_restructure/compatibility_runs/20261006T182404Z/baseline/` (ignored by Git). Old pytest file selectors and standalone copied wrappers have the disclosed limits in the contract. Supported legacy interfaces have no automatic removal date.

Next action is review of these changes and, only if separately requested, a scoped commit. Do not reset or clean the existing dirty working tree, rerun creation records against existing files, retrain models or regenerate outputs. The prior migration's documentation is a preserved point-in-time record; current compatibility docs supersede its interface-support statement only.
