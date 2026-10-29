# ViFailback follow-up verification and experiment proposal

Recorded 2026-10-29T01:02:29.068233+01:00 (Europe/Berlin). No model training or neural inference was performed.

Read [EXECUTIVE_VERDICT.md](EXECUTIVE_VERDICT.md) first. This is a new versioned
analysis; previous evidence, review predictions, exports and training runs remain
unchanged. Recommendations inside the supplied review were treated as review
content, not as authorization to execute experiments.

- [Locked review](00_LOCKED_REVIEW/INDEPENDENT_REVIEW_LOCKED.md) and [lock](00_LOCKED_REVIEW/REVIEW_LOCK.json).
- [Unblinding report](01_UNBLINDING/UNBLINDING_REPORT.md) and [all20 comparisons](01_UNBLINDING/LOCKED_PREDICTIONS_VS_NATIVE_LABELS.csv).
- [Cohort, grouping and availability](02_COHORT_AND_SPLITS/COHORT_READINESS_AND_GROUPING.md).
- [Conservative V2 episode list](02_COHORT_AND_SPLITS/V2_CONSERVATIVE_CORE/ELIGIBLE_CORE_EPISODES_V2.csv), [all exclusions](02_COHORT_AND_SPLITS/V2_CONSERVATIVE_CORE/CORE_ELIGIBILITY_AND_EXCLUSIONS_V2.csv), and [splits](02_COHORT_AND_SPLITS/V2_CONSERVATIVE_CORE/OUTER_INNER_SPLITS_V2.json).
- [Sensor quality](03_SENSOR_QUALITY/SENSOR_QUALITY_AUDIT.md) and [diagnostics](03_SENSOR_QUALITY/SENSOR_ANOMALY_DIAGNOSTICS.png).
- [REASSEMBLE implementation and checkpoint audit](04_REASSEMBLE_REFERENCE/REASSEMBLE_IMPLEMENTATION_AND_CHECKPOINT_AUDIT.md).
- [Reproducible experiment proposal](05_EXPERIMENT_PROPOSAL/REPRODUCIBLE_EXPERIMENT_PROPOSAL.md), [matrix](05_EXPERIMENT_PROPOSAL/EXPERIMENT_MATRIX.csv), and [configuration](config/EXPERIMENT_PROPOSAL.json).
- [Remaining blockers](UNRESOLVED_BLOCKERS.md). Generated validation/provenance records are under `provenance/`.

All episode lists retain original identities. V1 planning artifacts remain under
`02_COHORT_AND_SPLITS/`; proposed primary analyses refer specifically to the V2
subdirectory. A CSV saying eligible for acquisition is not proof that every
remote RGB payload has been decoded or checked for incidental human involvement.
