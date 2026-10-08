# Structural validation report

Outcome: migration complete; no existing protected output changed.

| Check | Result | Evidence |
|---|---|---|
| Writer preflight | No open writable project file descriptors; no research worker active; Task 4 complete and final queue closed | `baseline/safety.json` |
| Baseline full suite, corrected environment | 272 passed; 6 warnings | `baseline/pytest_with_pythonpath.log` |
| Namespace group | 163 passed | `namespace_tests.log` |
| Model group | 163 passed | `model_tests.log` |
| Script group | 163 passed | `script_group_tests.log` |
| Final suite | 272 passed; same 6 warnings | `final_pytest.log` |
| Module imports / syntax | 57 imports; 291 files compiled in memory | `import_compile_check.json` |
| CLI smoke | 11 successful help invocations, no training | `cli_checks.json` |
| Executable AST comparison | 85/85 explained solely by imports, paths and entry-point bootstrap changes | `ast_equivalence.json` |
| Existing protected files | 40,500 stat identities, 12,552 evidence hashes unchanged | `preservation_check.json` |
| Known new file | One downloader parse/help provenance record, zero downloads | `CORRECTIONS.md` |
| Legacy references | No executable/config error in audited scope | `legacy_reference_audit.csv`, `reference_audit_scope.json` |
| Dependencies | No broken requirements | `pip_check.log` |
| Migration Git whitespace | Staged and unstaged pass | `git_checks.json` |
| Global staged whitespace | Existing protected evidence warnings preserved | `staged_diff_check.log`, baseline Git status |

Exact full-suite command:

```bash
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 ma_thesis_env/bin/python -B -m pytest tests -q --import-mode=importlib -p no:cacheprovider
```

Group checks used the same environment with `tests/unit` before test relocation. Importlib mode is used for full cross-domain collection because test filenames overlap across domains. No new data-dependent campaign was run. The repository interpreter and installed dependency versions are in `software_versions.json`.

Limits: no full payload rehashing, no checkpoint inference replay, no expensive model evaluation, no dependency installation and no claim that old scientific conclusions have been reevaluated. Existing tests exercised small synthetic forward/gradient checks only. Imports/path strings necessarily alter current source hashes; historical source/checkpoint identities and manifests remain unchanged. AST comparison ignores imports (separately checked), normalizes the classified paths, and permits the documented root bootstrap changes. It is not a formal behavioral proof.

The failed initial collection, transient PatchTST import issue, downloader help side effect and pre-existing staged whitespace are disclosed in `CORRECTIONS.md`; none was silently reconciled by editing historical outputs.
