# Backward-compatibility validation

**COMPLETE** on 2026-10-06T18:39:00.323920+00:00. Canonical domain layout remains fixed. No architecture moves, research workflows, training, downloads, dataset regeneration or evaluation campaigns were executed. All validation used imports, parser/help execution, existing fixture tests and small synthetic serialization fixtures.

## Interfaces restored

- **53 legacy module/package interfaces**, derived from the frozen migration mapping and original source identities, now exist under `src/pi_multimodal_ad/` as forwarding only.
- **39 legacy script paths** now forward to their `scripts/phm2026/` counterparts. Every former PHM script in `path_mapping.csv` and `moves.jsonl` is accounted for.
- Canonical interfaces remain `phm2026.*` and `scripts/phm2026/*`; Intel, REASSEMBLE, shared admission policy and canonical domain tests remain in their existing locations.
- Leaf module aliases return the same canonical module object, including private helpers and module globals. Package facades retain the legacy child search path and forward canonical exports.
- No substantial scientific implementation is present in compatibility wrappers; an AST/import/call audit is part of the dedicated tests.

Contract: [COMPATIBILITY_CONTRACT.md](COMPATIBILITY_CONTRACT.md). Complete matrix: [compatibility_matrix.csv](compatibility_matrix.csv), with 274 rows and statuses in `docs/repository_restructure/compatibility_runs/20261006T182404Z/matrix_summary.json`. It records import, script, passive/module, config/filesystem and serialization interfaces. Every former source/script interface is explained; no public import or script path from the authoritative inventory is omitted.

## Packaging decision

Added minimal `pyproject.toml` with existing setuptools, source-layout discovery and **no scientific runtime dependency declarations or installed-version changes**. Successfully installed the project editable with index access and dependencies disabled:

```bash
PIP_NO_INDEX=1 PYTHONDONTWRITEBYTECODE=1 ma_thesis_env/bin/python -B -m pip install --no-build-isolation --no-deps -e .
```

The installed project is `pi-multimodal-ad==0.1.0`. All **279 previously installed distribution versions** remain unchanged; the project itself is the only added distribution. `pip check` reports no broken requirements. No environment recreation or dependency upgrade occurred.

Canonical/legacy/Intel/REASSEMBLE imports succeed without PYTHONPATH, tested from a directory outside the repository. Scripts retain their source bootstraps. The supported setup is an editable install in the existing repository; config/data are not bundled into a standalone wheel. Ignored generated project/environment metadata files are enumerated in `docs/repository_restructure/compatibility_runs/20261006T182404Z/editable_installation_files.json`.

## Path, subprocess and module execution

Reused the existing marker-based repository discovery semantics (`.git` plus `AGENTS.md`) in a dependency-free `phm2026.repository_paths` utility. Configuration still raises its public `ConfigError`; acquisition uses the same root utility instead of fixed `parents[3]`. Existing configuration/downloader tests passed. No feature, model or evaluation formula changed.

Tests cover canonical/legacy module and script locations, arbitrary synthetic source depth, path escape rejection, and resolution of `configs/`, `data/`, `runs/`, `artifacts/`, `tests/fixtures/` with an explicit repository root from another cwd. Absolute old/new script help also succeeds outside repository cwd. Real workflows with relative inputs remain repository-root based.

Existing fixed-depth script bootstraps remain working and are covered by every CLI help pair; they were not restyled or removed. `runpy` sets the canonical script's `__file__` and `argv[0]`, preserving canonical sibling loading and future provenance. Static subprocess review found Git/GPU metadata collection rather than stale pipeline launch paths. Representative old/new source and script `python -m` execution passed.

Source modules were historically passive (no module-main workflow). Package names without a historical `__main__.py` remain non-executable as package CLIs; the matrix marks this explicitly. Module execution is tested representatively, not falsely reported as an exhaustive second campaign over every passive module. `download.py --help` is excluded because its unchanged `main` writes provenance even on parse exit; both canonical and legacy parser help are checked without calling that function.

## Serialization

All mapped legacy object names remain importable. Four synthetic pickle GLOBAL fixtures resolve classes to the identical canonical object; one small PatchTST configuration instance with a legacy module reference roundtrips with identical fields. No model is trained or loaded for these checks.

Static inspection finds PHM checkpoint writes of tensor state dictionaries plus plain model-config/scaler/metadata dictionaries. No historical checkpoint was loaded, modified or rewritten. Arbitrary pickle format/dependency drift and removed external classes are outside this bounded check. Details: `docs/repository_restructure/compatibility_runs/20261006T182404Z/static_path_execution_serialization_audit.json`.

## Regression results

| Check | Result |
|---|---|
| Existing configuration/downloader tests | **32 passed** |
| Initial compatibility imports, identities, paths, serialization and thin audit | **69 passed** |
| Full repository suite without PYTHONPATH | **386 passed**, 6 existing Torch warnings, 119.43 seconds |
| Original tests retained | All **272** prior tests plus **114** new compatibility tests |
| Legacy/canonical CLI help | **39 pairs / 78 invocations**, exact stdout/stderr and zero exit equivalence |
| Argument-error behavior | Old/new PatchTST CLI both return **2**, identical output |
| Absolute-path help from other cwd | Old and new paths passed |
| Module execution | Two passive module pairs and one script module pair passed |
| Core Python syntax | **374** files compiled in memory, no bytecode output |
| Dependency consistency | `pip check` clean; existing versions unchanged |
| Protected file preservation | **40,645** identities unchanged; **12,608** small evidence SHA256 hashes unchanged; **zero new protected files** |
| Canonical source/config preservation | **317** pre-existing files checked; only the six declared task files changed |
| Git preservation | HEAD and staged index unchanged; no commit or push |
| Task whitespace | Scoped tracked diff and new-file checks passed |

Full-suite command:

```bash
env -u PYTHONPATH OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 COMPATIBILITY_AUDIT_DIRECTORY=docs/repository_restructure/compatibility_runs/20261006T182404Z ma_thesis_env/bin/python -B -m pytest tests -q --import-mode=importlib -p no:cacheprovider
```

Logs and identities are in `docs/repository_restructure/compatibility_runs/20261006T182404Z/`. Full-suite importlib mode retains the prior collection method for repeated test basenames across domains. The global staged whitespace check still reports pre-existing historical evidence warnings; the index and evidence hashes match baseline, and those outputs were preserved. No test failure or packaging failure occurred during this task. The six pre-existing task-modified files are:

- `src/phm2026/utils/config.py`
- `src/phm2026/acquisition/phm_download.py`
- `src/phm2026/README.md`
- `README.md`
- `REPO_MAP.md`
- `docs/repository_restructure/.gitignore`

Exact created files, audit paths and installation metadata are listed in `docs/repository_restructure/compatibility_runs/20261006T182404Z/task_manifest.json` and `editable_installation_files.json`. Scientific model, feature, preprocessing and evaluation implementations remain byte-identical to this task's baseline. The two canonical code edits concern repository location only.

## Remaining interface limits

Former **32 `tests/unit/*.py` filename selectors** are historical references to current domain-owned tests; they are not restored as duplicate tests. The matrix identifies each one. Source packages with no historical `__main__.py` gain no package CLI. Namespace script `-m` execution requires repository cwd.

Copied standalone wrapper files, custom file loaders that retain an unregistered stub module object, and source-adjacent sidecar layouts are outside the tested standard-import/CLI contract. Use canonical standalone tools and explicit workspace arguments for those cases. No guarantee is made about external paths absent from the original migration inventory or arbitrary serialized model/version drift. There is **no scheduled automatic removal** of supported legacy interfaces.

## Continuation and review

Read [COMPATIBILITY_CONTINUATION.md](COMPATIBILITY_CONTINUATION.md) for another-IDE handoff. Current task audit root: `docs/repository_restructure/compatibility_runs/20261006T182404Z`. Pre-task Git status/diffs/HEAD/index, source preimages, distribution versions and protected identities are in its ignored `baseline/`; they are separate from the original migration audit. Prior migration reports and manifests were not rewritten. No phase or research job remains queued. Changes are available for review; no commit or push was requested or performed.
