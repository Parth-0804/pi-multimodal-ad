# PHM coding-agent instructions

1. Read, in this order:
   1. [`AGENTS.md`](../AGENTS.md)
   2. [`docs/planning/PROJECT_STATE.md`](../docs/planning/PROJECT_STATE.md)
   3. the exact authorized task in
      [`docs/planning/PHM_CODEX_IMPLEMENTATION_BACKLOG.md`](../docs/planning/PHM_CODEX_IMPLEMENTATION_BACKLOG.md)
2. Treat `PROJECT_STATE.md` as the latest project-status handoff. Verify cited
   artifact paths and configuration pins before relying on them.
3. Inspect existing code, tests, configuration, and Git status before creating
   abstractions. Extend the existing namespaced package; do not copy historical
   EDA monoliths or create a parallel framework.
4. Reuse `PHM2026Adapter`, dataset contracts, archive/profiling modules,
   configuration loading, provenance, versioned runs, and synthetic fixtures.
   Keep PHM-specific naming, paths, aliases, and target rules in the adapter or
   PHM YAML—not generic modules.
5. Work on one explicitly authorized backlog task at a time. Stop at a
   scientific gate rather than filling missing evidence with a guess.
6. `gtc-data-experiment/**` is immutable raw PHM input. Never scan
   `data/Full Dataset/**` for PHM work. Preserve the protected historical
   `experiments/exp_a_initial_eda_r1_r3_r5/**` record and unrelated files.
7. Never invent timestamps, timezone conversion, target, label, unit,
   six-hour horizon, damage meaning, annotation, or temporal join. Archive
   members are source evidence, not automatically model samples.
8. Use explicit repository-relative paths and validated YAML. Write generated
   outputs only to unique versioned run directories with config, input/output
   manifests, warnings, and provenance. Never modify `.gitignore` incidentally.
9. Preserve source identity (experiment, outer archive, member, internal run,
   modality) through every table. Use leakage-safe persisted split assignments;
   never generate random neighboring-window/image splits inside a loader or
   trainer.
10. Use tiny synthetic fixtures for tests. Run focused tests, formatting,
    compilation, and relevant dry-runs; report commands, evidence, limitations,
    changed files, and Git status.
11. Do not commit, push, delete, move, rename, or alter raw/historical files
    unless the user explicitly authorizes that exact action.

Current gate and organizer-corrected target semantics live in `docs/planning/PROJECT_STATE.md`. Missing organizer labels alone are not a blocker: the challenge requires a versioned image-derived target. Stop downstream work if that measurement fails its scientific/provisional gate.

R4 image runs and the initial P4.1–P4.5 sensor-only PatchTST baseline are complete. All targets and pseudo-box metrics remain provisional rather than physical-spall truth. The canonical PatchTST did not beat constant baselines on EXP-F; never retune it against EXP-F. The next gate is expert target review plus separately authorized, pre-registered train/validation-only decisions before complex PatchTST or fusion.
