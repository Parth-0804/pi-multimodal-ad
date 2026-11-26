# Output and provenance policy

## Policy goals

Outputs must be traceable to declared inputs, configuration, code, commands,
and software versions. Raw data and historical evidence must remain unchanged,
and regenerable bulk must not be confused with thesis evidence.

## Output classes

| Class | Examples | Default treatment |
|---|---|---|
| Immutable raw input | PHM/Intel archives and payloads | Never write, move, rename, or commit |
| Protected historical output | `experiments/exp_a_initial_eda_r1_r3_r5/outputs/**` | Preserve unchanged until reproduced and approved |
| Temporary extraction/cache | extracted HDF5, decoded images, scratch arrays | Keep outside raw roots; ignore; clean only known temporary paths |
| Intermediate numerical output | full feature tables, flattened LF/CI tables, PCA scores | Regenerable and ignored by default; record in output manifest |
| Run report | integrity report, warning report, run summary | Store with the versioned run; small final reports may be versioned intentionally |
| Final thesis table | curated compact table used in the thesis | Allow-list explicitly after review |
| Final figure | curated figure used in the thesis | Allow-list explicitly after review |
| Test fixture | tiny synthetic ZIP/HDF5/image/CSV | Track only when demonstrably synthetic and small |

The current global `*.csv` rule is unchanged in Phase 1. Its replacement and
allow-list design belong to Phase 3.

## Historical-output rule

All existing outputs under
`experiments/exp_a_initial_eda_r1_r3_r5/outputs/**` are:

`HISTORICAL_OUTPUT_PROTECT_UNTIL_REPRODUCED`

Do not overwrite, normalize, rename, relocate, prune, or regenerate into that
directory. Existing paths embedded in historical files may be stale; preserve
them as evidence of the original run.

## New run layout

New analyses should write to a unique, non-overwriting run directory under a
configurable output root. The intended layout is:

```text
<output-root>/<experiment-or-study>/<run-id>/
├── config/
│   └── resolved_config.yaml
├── manifests/
│   ├── inputs.json
│   └── outputs.json
├── reports/
│   ├── warnings.json
│   └── summary.md
├── tables/
├── figures/
├── logs/
└── provenance.json
```

`run-id` should be unique and stable enough to prevent accidental overwrite,
for example a UTC timestamp plus a short configuration identifier. Code must
fail clearly if an output destination already contains a different run unless
an explicitly designed resume mode applies.

## Required provenance

Every analysis run must record:

- resolved configuration and configuration source;
- experiment, run, modality, duplicate policy, and run-identity policy;
- Git commit and dirty-working-tree indicator;
- exact command and timestamp with timezone;
- Python and relevant package versions;
- input archive paths relative to the configured data root;
- input identity available at that phase without altering raw data;
- warnings, skipped records, and failures;
- output paths, sizes, roles, and checksums where inexpensive;
- known methodology version and unresolved limitations.

Do not embed workstation-specific absolute paths when a repository-relative or
data-root-relative path can identify the source.

## Tracking policy

- Raw data and extracted source payloads are never tracked.
- Temporary caches and broad intermediates are ignored by default.
- Small manifests, reports, configuration snapshots, synthetic fixtures, final
  thesis tables, and final figures may be tracked only through explicit,
  narrowly scoped allow rules.
- A plot without its configuration and data lineage is not a reproducible final
  artifact.
- Generated outputs must not be called reproducible until a clean validation
  run demonstrates reproduction.

Phase 3 will propose the precise `.gitignore` implementation and show its diff
before uncertain tracking changes are applied.

## Scientific and retention constraints

- Preserve experiment/run/source identity in all tables and figures.
- Record Run-2 duplicate handling wherever EXP-A Run 2 contributes.
- Do not label lifecycle stages as ground-truth health classes.
- Separate refactoring differences from scientific-correction differences.
- Retain outputs used in submitted thesis material according to the final
  research-retention decision.
- Request explicit approval before deleting or moving any historical or
  versioned run output.
