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
The [native-source review examples](results/INDEPENDENT_REVIEW_PACKAGE/10_Visual_And_Sensor_Examples/)
are now physically retained with the review package. Their content and provenance
remain protected; the [approved relocation receipt](../general/docs/repository_history/root_cleanup_20261126/approved_relocation/README.md)
records the location-only change.

Old source aliases were removed. The [earlier move mapping](../general/docs/repository_history/dataset_layout_cleanup.json)
and [legacy execution-path audit](../general/docs/repository_history/root_cleanup_20261126/approved_relocation/vifailback_adapter/LEGACY_CONSUMER_LIMITS.md)
identify remaining path dependencies in historical commands, manifest-string I/O
and child-process controllers. Explicit context adapters cover only their stated
interfaces; physical consolidation does not establish full replay compatibility.

## Thesis and evidence

Chapters 7–9 and Appendix F; existing evidence E068–E111 supplies dataset and synthesis records. The [thesis-to-code map](../../docs/THESIS_CODE_MAP.md) is the shared browsing route. Keep MSM, HANDOVER and ViFailback assessment units, eligible populations, positive-class definitions and AP aggregation separate. A historical review package or duplicated snapshot is provenance, not an additional independent experiment.

[All implementations](../README.md) · [Repository map](../../REPO_MAP.md)
