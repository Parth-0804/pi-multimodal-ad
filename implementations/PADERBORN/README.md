# PADERBORN

Historical ARCH-VAL-PB bearing-dataset study for mechanism and feasibility
checks. The retained protocol proposes privileged-modality rank distillation,
subject to study-specific signal and evaluation gates.

| Part | Location |
|---|---|
| Feature and gate implementations | [scripts](scripts) |
| Derived bearing features | [results/processed/bearing_features](results/processed/bearing_features) |
| Historical study report | [ARCHITECTURE_VALIDATION_RESULTS.md](docs/ARCHITECTURE_VALIDATION_RESULTS.md) |
| Gate 3 preregistration | [ARCHITECTURE_VALIDATION_PREREGISTRATION.md](docs/ARCHITECTURE_VALIDATION_PREREGISTRATION.md) |
| Ownership and relocation record | [dataset_layout_cleanup.json](../general/docs/repository_history/dataset_layout_cleanup.json) |

Use the historical report for its stated outcomes, protocol fork and limitations.
Code and preregistration establish implementation and proposed methodology;
they do not establish that every gate or comparison ran. Keep the bearing-study
targets and assessment units separate from the PHM gear-condition studies.

This overview navigates retained source and records. No new training, evaluation
or reproduction was performed for the reorganisation. Source-path and packaging
updates remain unfinished; saved commands may refer to former paths. The move
record locates the preserved study documents and scripts.

## Thesis and evidence

Evidence IDs below follow the researcher-requested 28 November renumbering. The [complete mapping](../../00_thesis_writing_tracking/final_thesis_prep/evidence_publication_20261128/manifest.json) relates them to the prior IDs retained in historical records.

Appendix G research chronology and the methodological context of Chapter 5; current evidence E115. The [historical report](docs/ARCHITECTURE_VALIDATION_RESULTS.md) records Gates 1 and 2 as executed: the bearing-held-out Gate 2 failed, while the requested condition-only protocol gave a different outcome. Preserve that protocol fork. Gate 3 was not run, even though its implementation and preregistration exist; there is no completed four-arm distillation comparison.

The same report records dataset source/license, fact-sheet target provenance, selected sensor channels, preparation and assessment units. Its results are REPORTED here, not newly reproduced. The [thesis-to-code map](../../docs/THESIS_CODE_MAP.md) points to the executed gate scripts and marks unresolved source lineage.

[All implementations](../README.md) · [Repository map](../../REPO_MAP.md)
