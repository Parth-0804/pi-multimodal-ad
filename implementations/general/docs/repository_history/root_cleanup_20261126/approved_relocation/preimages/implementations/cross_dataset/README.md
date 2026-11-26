# Cross-dataset work

External-evaluation implementation, study comparisons and scientific synthesis.
Dataset-specific protocols and eligibility decisions remain authoritative; these
files do not define a common leaderboard across different prediction tasks.

| Part | Location |
|---|---|
| Implementation | [src/external_eval](src/external_eval) |
| Configurations | [configs](configs) |
| Checks | [tests](tests) |
| Scientific summary | [results/FINAL_RESEARCH_SUMMARY.md](results/FINAL_RESEARCH_SUMMARY.md) |
| Performance | [results/PERFORMANCE_COMPARISON.md](results/PERFORMANCE_COMPARISON.md) |
| Robustness | [results/ROBUSTNESS_COMPARISON.md](results/ROBUSTNESS_COMPARISON.md) |
| Architectures | [results/ARCHITECTURE_COMPARISON.md](results/ARCHITECTURE_COMPARISON.md) |
| Eligibility and handoff | [results/REVIEW_HANDOFF.md](results/REVIEW_HANDOFF.md) |
| Authorization and lineage | [results/provenance](results/provenance) |
| Review packages and comparison tables | [results](results) |

[MSM](../MSM/README.md) and [HANDOVER](../HANDOVER/README.md) retain their own
cohorts, split requirements and failed-gate records. Independent dataset-specific
fitting, transfer of learned weights and zero-shot evaluation are distinct claims.
Frozen package copies remain historical evidence, not additional datasets.

The [model-configuration audit](results/MODEL_CONFIGURATION_AUDIT_20261103/README.md)
is physically located with these results. Its historical source/provenance paths
remain unchanged; a corrected current utility discovers the repository root.
The [relocation receipt](../general/docs/repository_history/root_cleanup_20261126/model_audit_and_handover/README.md)
records file-identity preservation and distinguishes path checks from audit replay.
Native-source review examples remain under `CROSS_DATASET_COMPARISON/`; their
raw-data protection is unchanged.

Old source aliases were removed. Source-path and packaging updates remain
unfinished; use the [move mapping](../general/docs/repository_history/dataset_layout_cleanup.json)
when following historical commands or source references.

## Thesis and evidence

Chapters 7–9 and Appendix F; existing evidence E068–E111 supplies dataset and synthesis records. The [thesis-to-code map](../../docs/THESIS_CODE_MAP.md) is the shared browsing route. Keep MSM, HANDOVER and ViFailback assessment units, eligible populations, positive-class definitions and AP aggregation separate. A historical review package or duplicated snapshot is provenance, not an additional independent experiment.

[All implementations](../README.md) · [Repository map](../../REPO_MAP.md)
