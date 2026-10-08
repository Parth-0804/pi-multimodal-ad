# Canonical and legacy interface contract

The completed domain-first migration remains canonical. This follow-up supplies the old interfaces for external notebooks, historic commands and serialized Python references. Scientific implementation exists only under the canonical domain paths. No automatic compatibility deletion is scheduled.

## Canonical interfaces

- PHM: `phm2026.*`, source `src/phm2026/`, scripts `scripts/phm2026/<capability>/`, tests `tests/phm2026/`.
- Intel: `intel_welding.*`, `scripts/intel_welding/` and `tests/intel_welding/`.
- REASSEMBLE: existing `src/reassemble/`, `scripts/reassemble/`, configs/tests and evidence, unchanged.
- Shared: existing admission policy only; no scientific implementation is moved there.

New code should use canonical names. Source/script/test ownership, experiment configurations and research conclusions are unchanged.

## Supported legacy interfaces

All **53 original Python module/package names** under `pi_multimodal_ad` and **39 original script paths** under `scripts/{dataset,features,targets,training,results}/` are derived from `path_mapping.csv` and verified against `moves.jsonl`. `src/pi_multimodal_ad/_mapping.py` is the complete import mapping; `compatibility_matrix.csv` enumerates interfaces and validation scope.

Leaf imports return the canonical module object, so public/private helpers, classes, mutable module globals and serialization lookup retain identity. Package facades preserve the legacy package search path, forward exported attributes, and route old child names to their mapped module (including moved RT-DETR/PatchTST/fusion modules). No feature extraction, model logic, metric formula or data transformation is copied into the compatibility package.

Examples:

```python
from pi_multimodal_ad.models.patchtst import PatchTSTConfig
from pi_multimodal_ad.models.rtdetr_regression import RegressionHead
from pi_multimodal_ad.features.sensor_minutes import ChannelSpec
```

The exact names available are the canonical module's names; compatibility adds no substitute class or fabricated export. A former module removed from the migration inventory is outside the enumerated contract.

Legacy scripts execute their canonical file through `runpy` with unchanged user arguments and propagated `SystemExit`. `__file__` and `argv[0]` identify the canonical script; help output and argument-error behavior match. This preserves canonical source-relative imports and source identity in future provenance. Existing configs remain repository-relative.

```bash
ma_thesis_env/bin/python -B scripts/training/train_patchtst.py --help
ma_thesis_env/bin/python -B scripts/phm2026/training/train_patchtst.py --help
ma_thesis_env/bin/python -B -m scripts.training.train_patchtst --help
```

Both script paths work from repository root. Absolute script help invocation also works from another cwd; this does not expand support for running real workflows from arbitrary directories with relative config/input paths. Namespace script execution (`python -m scripts...`) remains repository-root based; scripts are not installed as distribution packages.

Original source modules have no `__main__` workflow. Legacy leaf `python -m` forwarding preserves passive module execution rather than adding a training/download CLI. Packages without a historical `__main__.py` remain non-executable as packages. The downloader's parser is checked directly: its `main(--help)` always writes provenance, so it is intentionally not invoked during this task.

## Historical references only

Frozen runs, artifacts, audit evidence, dated documentation, archived experiments and historical manifests are preserved. Their original source hashes, commands and paths describe the original run, not a promise that source bytes remain the same after refactoring. Use the original Git revision when exact historic source reproduction is required.

Former `tests/unit/*.py` locations are recorded as historical filesystem references to the canonical test files; old pytest filename selectors are not restored. Restoring duplicate tests would obscure domain ownership and duplicate collection. The matrix accounts for each former test path explicitly.

Ignored bytecode/cache relocation records are maintenance history, not public import interfaces. No raw-data path, run, output, tutorial, presentation asset or historical manifest is relocated by compatibility work.

## Packaging and paths

`pyproject.toml` provides minimal setuptools discovery for canonical packages and the compatibility namespace. It declares no scientific dependencies or version changes. Editable setup uses the existing environment:

```bash
PIP_NO_INDEX=1 ma_thesis_env/bin/python -B -m pip install --no-build-isolation --no-deps -e .
```

After installation, canonical and legacy imports work without `PYTHONPATH`, including outside repository cwd. Existing script source bootstraps remain available. A common dependency-free marker finder in `phm2026.repository_paths` serves configuration and acquisition. Configuration preserves its previous `ConfigError` contract; marker semantics stay `.git` plus `AGENTS.md`. The downloader no longer assumes a fixed source depth and gains no third-party dependency.

## Serialization and limitations

Legacy qualified-name lookup resolves canonical objects, tested with synthetic pickle GLOBAL references and a small PatchTST configuration instance. Audited PHM checkpoint writers store tensor state dictionaries and plain config/metadata dictionaries. No historical checkpoint is loaded or rewritten. This does not guarantee compatibility with arbitrary pickle/dependency version drift, removed external classes or unsupported serialized layouts.

Forwarding source files are not independent implementations: copied standalone wrapper files, custom `spec_from_file_location` execution that retains an unregistered wrapper object, and consumers relying on a former source-adjacent sidecar layout are outside the tested import/CLI contract. Use standard imports or the canonical standalone script and explicit workspace arguments (for example the inspection scorer's `--root`). These limits are disclosed rather than inferred away from repository-local tests.

## Regression gate

`tests/compatibility/` verifies every mapped import and script help path, object identity, package child routing, packaging without PYTHONPATH, thin-wrapper constraints, path resolution, representative module execution, error exits and synthetic serialization. The full pre-existing repository suite remains part of the gate. Compatibility tests never start a research workflow. Validation and task-specific preimages/manifests are linked in `COMPATIBILITY_VALIDATION.md`.
