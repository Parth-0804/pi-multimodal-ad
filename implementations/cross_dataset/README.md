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

The model-configuration audit and protected native-source subtrees under
`CROSS_DATASET_COMPARISON/` retain their original paths where required by
training dependencies or data protection. The
[approved move plan](../general/docs/repository_history/physical_restructure_20261119/BULK_MOVE_PLAN.md)
records those exceptions.

Old source aliases were removed. Source-path and packaging updates remain
unfinished; use the [move mapping](../general/docs/repository_history/dataset_layout_cleanup.json)
when following historical commands or source references.

[All implementations](../README.md) · [Repository map](../../REPO_MAP.md)
