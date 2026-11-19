# Cross-dataset work

The external-evaluation source and tests are stored here. Old source/test paths
remain compatibility symlinks. Configurations, provenance and scientific reports
retain their original locations in `CROSS_DATASET_COMPARISON/`.

This section links the implementation and cross-dataset synthesis. Dataset-specific protocols and eligibility decisions
remain authoritative; this index does not create a common leaderboard.

| Part | Canonical location | Purpose |
|---|---|---|
| Implementation | [External-evaluation source](src/external_eval) | Existing evaluation code used for the external studies. |
| Configuration | [Configurations](configs) | Frozen-core and execution-plan records. |
| Tests | [Tests](tests) | Existing validation checks for this implementation. |
| Provenance | [Provenance](provenance) | Source identities, authorisation and execution records. |
| Scientific summary | [Final research summary](../../CROSS_DATASET_COMPARISON/FINAL_RESEARCH_SUMMARY.md) | Cross-dataset interpretation with protocol boundaries. |
| Performance | [Performance comparison](../../CROSS_DATASET_COMPARISON/PERFORMANCE_COMPARISON.md) | Saved comparisons; inspect cohorts and metric definitions. |
| Robustness | [Robustness comparison](../../CROSS_DATASET_COMPARISON/ROBUSTNESS_COMPARISON.md) | Conditions and missing/degraded-input evidence. |
| Architecture | [Architecture comparison](../../CROSS_DATASET_COMPARISON/ARCHITECTURE_COMPARISON.md) | Reused and dataset-specific model components. |
| Handoff | [Review handoff](../../CROSS_DATASET_COMPARISON/REVIEW_HANDOFF.md) | Entry point for eligibility and interpretation limits. |

[MSM](../../implementations/MSM/README.md) and [HANDOVER](../../implementations/HANDOVER/README.md)
retain their own evidence. Reusing an architecture, transferring a pretrained
backbone, transferring source-study learned weights and achieving independent
predictive performance are separate claims.

Frozen review packages and configuration audits remain inside the canonical
cross-dataset workspace. Their copies and archives are preserved evidence, not
additional independent datasets or new implementation owners.

[All implementations](../../implementations/README.md)
