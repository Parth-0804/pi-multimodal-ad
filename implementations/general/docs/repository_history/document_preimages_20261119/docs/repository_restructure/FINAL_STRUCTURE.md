# Final domain-first structure

Structural migration complete on 2026-10-05T13:14:18.109325+00:00. Baseline and final HEAD: `8d4e7a9378cb51ffc3cd7b9be1e2785efc02d792`. No commit was created; the pre-existing dirty working tree is preserved. No research reruns or changes to scientific formulations, budgets, evaluation methodology or historical conclusions.

## Directory tree

```text
src/
├── phm2026/
│   ├── acquisition/          PHM archive recovery
│   ├── data_contracts/       identities and typed records used by PHM
│   ├── datasets/             PHM adapter and its base protocol
│   ├── profiling/            archives, images, sensors, alignment
│   ├── targets/
│   ├── features/
│   ├── preprocessing/
│   ├── models/
│   │   ├── rtdetr/           detection, feasibility, multitask, regression
│   │   └── patchtst/         model, regression
│   ├── fusion/               late_fusion, modality_fusion
│   ├── evaluation/
│   ├── reporting/
│   ├── utils/
│   └── cli.py
├── intel_welding/            existing namespace; implementation in scripts
├── reassemble/               independent assembly-failure research domain
└── shared/README.md          admission policy only; no shared implementation
scripts/
├── phm2026/
│   ├── dataset/
│   ├── features/
│   ├── targets/
│   ├── training/
│   ├── results/
│   └── legacy_inspect_dataset.py
├── intel_welding/
├── reassemble/
├── thesis/
├── ops/
├── presentation/
├── rawvib/                   existing supplementary PHM analyses
└── paderborn/                existing transfer-study scripts
configs/
├── phm2026/
├── intel_welding/
├── reassemble/
├── datasets/phm2026.yaml
└── experiments/phm2026_*.yaml
tests/                       (repository root, alongside configs)
├── phm2026/
├── intel_welding/
├── ops/
├── reassemble/
├── thesis/
└── fixtures/
```

This is a capability tree, not a claim that placeholder Intel model packages contain implemented training. Its implemented inventory and foundation audits remain in `scripts/intel_welding/`. REASSEMBLE is an experimental domain with its own feature, model, fusion, corruption and evaluation code; the name also appears in recovery tooling but does not make the domain operational infrastructure. Its locations stay unchanged. Thesis validity checks remain under `scripts/thesis/`; maintenance under `scripts/ops/`.

## Ownership and entry points

PHM code is directly under `src/phm2026/`, including utilities currently consumed only by PHM. Shared admission requires actual consumers across domains, not generic filenames. `src/shared/README.md` records this rule; no shared implementation or speculative subdirectories were added. Existing Intel placeholders were preserved, not duplicated.

PHM scripts use `scripts/phm2026/<capability>/`. Their repository-root discovery was corrected for the extra directory depth; scripts that lacked a source bootstrap now locate `src/`. Presentation root discovery was also repaired. Use repository-root execution, for example:

```bash
ma_thesis_env/bin/python -B scripts/phm2026/dataset/profile_dataset.py --help
ma_thesis_env/bin/python -B scripts/phm2026/training/train_patchtst.py --help
PYTHONPATH=src ma_thesis_env/bin/python -B -c "import phm2026; import intel_welding"
```

Config files and pins remain unchanged: explicitly named PHM experiment configs stay under `configs/experiments/`, the dataset definition under `configs/datasets/`, recovery under `configs/phm2026/`. Tests mirror ownership; shared fixture paths retain their depth. Domain READMEs and root README/REPO_MAP provide traceability.

## Import migration

| Previous import | Canonical import |
|---|---|
| `pi_multimodal_ad.datasets.phm2026` | `phm2026.datasets.phm2026` |
| `pi_multimodal_ad.features.sensor_minutes` | `phm2026.features.sensor_minutes` |
| `pi_multimodal_ad.models.rtdetr_regression` | `phm2026.models.rtdetr.regression` |
| `pi_multimodal_ad.models.patchtst` | `phm2026.models.patchtst.model` (public classes also exported by `phm2026.models.patchtst`) |
| `pi_multimodal_ad.models.patchtst_regression` | `phm2026.models.patchtst.regression` |
| `pi_multimodal_ad.models.late_fusion` | `phm2026.fusion.late_fusion` |
| `pi_multimodal_ad.models.modality_fusion` | `phm2026.fusion.modality_fusion` |
| `pi_multimodal_ad.utils` | `phm2026.utils` |

The complete per-file mapping and ownership/reference justification is [path_mapping.csv](path_mapping.csv): 124 implementation/script/test moves ({'src': 53, 'scripts': 39, 'tests': 32}), plus 86 ignored bytecode files preserved under `.cache/repository_restructure/20261005T131103Z/` before removing empty retired directories. No permanent legacy import wrappers or duplicate implementations were needed. Canonical checkpoint writers use tensor state dictionaries plus plain metadata/config dictionaries; no old-package compatibility need was found in audited callers. Historical reproduction still uses its recorded Git revision.

## Preserved evidence and references

All 40,500 pre-existing files checked under `runs/`, `artifacts/`, `experiments/`, `archive/` and raw-data roots retain their path, size and modification time; 12,552 small evidence files also match SHA256. This includes Task 4 recovery, final validity audit evidence and historical outputs. Large raw payloads were not reread for hashing; see the scope in `preservation_check.json`.

One new zero-download parse-only provenance record was written by the downloader's existing `--help` logging behavior: `artifacts/phm2026/downloads/20261005T130258188699Z-a8b31e9c.json`. It is retained transparently; no existing output was overwritten. No network/download step was reached. See [CORRECTIONS.md](CORRECTIONS.md).

Frozen manifests, dated planning checkpoints, thesis evidence and generated tutorial reports retain historical paths. Current navigation, active recovery/Intel runbooks and executable tutorial imports were updated. [legacy_reference_audit.csv](legacy_reference_audit.csv) records 109 remaining hits: {'documentation reference': 49, 'valid historical reference': 60}. Zero executable/config errors and zero compatibility aliases remain in the audited text scope. Exclusions (raw data, environments, credential/session files, binary/large text) are explicit in `reference_audit_scope.json`. Migration documentation intentionally names old paths and is excluded from that count.

## Validation and remaining debt

- Baseline: **272 passed**, 6 existing Torch warnings, 19.58 seconds, with `PYTHONPATH=src`.
- After namespace move: **163 passed**; after model-family split: **163 passed**; after script move: **163 passed**.
- Final cross-domain suite: **272 passed**, same 6 warnings, 19.31 seconds.
- **57 imports** (56 PHM modules plus Intel namespace); **291 Python files** compiled in memory; **11 CLI help checks** passed without PYTHONPATH.
- **85 changed Python files** matched baseline executable ASTs after allowing only import/path/bootstrap changes. This is a bounded structural check, supported by tests; not a new scientific evaluation.
- `pip check`: no broken requirements. Migration-scoped staged and unstaged whitespace checks passed.
- Global staged whitespace check still flags already-staged historical evidence; those files match the pre-migration snapshot and were not changed to silence it.

The initial baseline without PYTHONPATH failed collection; a model-prefix rewrite briefly produced an incorrect PatchTST CLI import, then the post-group audit corrected it. Both are documented. Existing lack of packaging metadata remains: direct imports require `PYTHONPATH=src`. The empty Intel package subdirectories remain legacy placeholders. No hidden claim of full model retraining or numerical reevaluation is made.

## Handoff and audit files

- [MIGRATION_PLAN.md](MIGRATION_PLAN.md): classification, sequencing and preservation rules.
- [VALIDATION_REPORT.md](VALIDATION_REPORT.md): commands/results and limitations.
- [CORRECTIONS.md](CORRECTIONS.md): failed attempts and corrections.
- [CONTINUATION.md](CONTINUATION.md): completion state for another IDE.
- `provenance.json`, `software_versions.json`, `output_manifest.json`, `moves.jsonl`, `edits.jsonl`, `source_changes.json`, `ast_equivalence.json`.
- `baseline/`: original Git status/HEAD, source identities, protected identities, original source/config/test preimages and initial test logs. Large baseline records are deliberately ignored by Git, but remain in the workspace.
- `migration_commands.py` is a record of one-time phase execution, not a tool to rerun against this migrated tree. Corrections are separate in the log. `validate_migration.py` can recheck the frozen baseline while that workspace backup remains available.

Git-aware moves are staged, subsequent import/documentation edits remain unstaged/untracked, and unrelated pre-existing staged/unstaged work remains intact. No commit or push was performed. Review these changes together before committing.
