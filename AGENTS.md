# Repository working instructions

## Purpose

This repository supports a reproducible research pipeline for the PHM North
America 2026 Data Challenge. The active work covers configuration, read-only
data access, integrity checks, feature extraction, exploratory analysis,
visualization, and provenance. Model training is out of scope until explicitly
approved.

Detailed scope and policy live in:

- [Active scope](docs/active_scope.md)
- [Data boundaries](docs/data_boundaries.md)
- [Output policy](docs/output_policy.md)
- [Restructuring tasks](docs/restructuring/TASKS.md)

## Authoritative scope

- EXP-A: Runs 1–5
- EXP-B: Runs 1–7
- EXP-F: Runs 1–8

EXP-A Run 2 has a reported organizer warning concerning 311 files overlapping
Run 1. Preserve the files. Duplicate handling must be configurable, reported,
and non-destructive.

Run number and lifecycle stage are not ground-truth health or damage labels.

## Non-negotiable boundaries

- Treat `gtc-data-experiment/**` and `data/Full Dataset/**` as immutable.
- Never delete, move, rename, rewrite, extract in place, recompress, or
  deduplicate raw data.
- Never read or expose `synology_cookies.txt`, `.env` contents, tokens,
  credentials, private keys, or session contents.
- Never commit raw data, credentials, virtual environments, caches, extracted
  HDF5 files, or large temporary outputs.
- Preserve `experiments/exp_a_initial_eda_r1_r3_r5/**` until a validated
  replacement reproduces it and the researcher approves a later migration.
- Treat current generated outputs as
  `HISTORICAL_OUTPUT_PROTECT_UNTIL_REPRODUCED`.
- Stop and request confirmation before destructive or difficult-to-reverse
  operations.

## Expected architecture

New work should converge on:

- `configs/datasets/` and `configs/experiments/` for portable configuration;
- `src/pi_multimodal_ad/` for installable acquisition, data, feature,
  analysis, visualization, CLI, configuration, and provenance modules;
- `tests/unit/`, `tests/integration/`, and tiny synthetic
  `tests/fixtures/`;
- versioned run directories containing configuration, manifests, warnings,
  tables, figures, reports, and software provenance;
- `experiments/` and `archive/` for clearly labeled historical records.

Do not copy the historical monolith into multiple new modules.

## Configuration and paths

- Use configuration for experiment selection, channels, data roots, output
  roots, duplicate policies, and validation behavior.
- Use repository-relative paths by default, with environment-variable or CLI
  overrides where needed.
- Do not introduce absolute workstation or VM paths.
- Resolve paths without changing raw-data permissions or contents.

## Scientific behavior

- Preserve and regression-test historical feature behavior before refactoring.
- Document known defects; do not silently correct formulas or ingestion logic.
- Make scientific corrections separately reviewable with failing-then-passing
  regression tests and methodology notes.
- Retain experiment, outer archive, internal member/run, modality, and source
  identity throughout the pipeline.

## Outputs and provenance

- Never overwrite historical outputs.
- Write new analyses to unique, versioned run directories.
- Record the configuration snapshot, Git commit, command, timestamp, software
  versions, input manifest, output manifest, and warnings.
- Follow `docs/output_policy.md` before adding generated artifacts to Git.

## Validation

Use the repository environment when available:

```bash
git diff --check
git status --short --branch --untracked-files=all
ma_thesis_env/bin/python -B -m pip check
```

Once tests and package metadata exist, use the documented `pytest` and package
validation commands. Do not claim an unimplemented command succeeded.

Work one approved restructuring phase at a time. At each phase boundary, report
changed files, `git diff --stat`, checks performed, unresolved issues, and the
exact next action; then wait for approval.
