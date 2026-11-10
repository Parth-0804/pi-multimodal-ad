# Model configuration audit — reviewer entry point

Audit date: 2026-11-03. Read-only evidence reconstruction; no new training, tuning or feature extraction.

This folder contains the requested model/configuration/results audit for REASSEMBLE, ViFailback, MSM and Handover, with separate historical PHM coverage. The original task is preserved in `provenance/USER_AUDIT_REQUEST.txt`. No new training, tuning, feature extraction, model changes or job signaling was performed.

1. Read [executive overview](01_executive_overview/EXECUTIVE_AUDIT_SUMMARY.md) for TablesA–H and explicit Q1–Q13 answers.
2. Check [current status](01_executive_overview/CURRENT_EXPERIMENT_STATUS.md) and [key limitations](01_executive_overview/KEY_FINDINGS_AND_LIMITATIONS.md).
3. Inspect [architecture inventory](02_model_architecture/COMPLETE_MODEL_INVENTORY.md),[all model configurations](03_hyperparameter_configuration/ALL_MODEL_CONFIGURATION_TABLE.md) and [tuning history](03_hyperparameter_configuration/HYPERPARAMETER_TUNING_HISTORY.md).
4. Use [complete results](05_results/ALL_MODEL_RESULTS_SUMMARY.csv),[long metrics](05_results/ALL_RECORDED_METRICS_LONG.csv),[comparability matrix](05_results/COMPARABILITY_MATRIX.csv) and the dataset reports/plots.
5. Read [missing evidence](07_scientific_validity/MISSING_EVIDENCE.md),[reproducibility](04_training_and_checkpoints/REPRODUCIBILITY_ASSESSMENT.md),[validation](09_reviewer_handoff/AUDIT_VALIDATION_RESULTS.md) and [researcher handoff](09_reviewer_handoff/RESEARCHER_HANDOFF.md).

The taxonomy has32 computational families. There are7,969 per-fit/configuration records:7,929 COMPLETE (7,755 individually corroborated plus174 legacy control-flow-inferred),40 REUSED. Counts include candidates, controls and reconstruction refits, not independent replications. Binary candidates number4,920 with4,438 distinct hashes; additional JSON fitted states are separately indexed. Extraction retains587,101 numeric metric records and93,278 epoch-history rows. The validation report supplies exact held-out-only counts.

Large checkpoints, raw datasets, caches and prediction banks remain at their original paths. This folder is self-contained as an audit of metadata/reports; full inference/data replay requires those original artifacts. Paths in machine-readable tables are relative to the repository root unless an external original path is explicitly recorded. Source SHA256s and output identities are in FILE_AND_SOURCE_MANIFEST.csv and the checkpoint inventory. NOT RECORDED and FRAMEWORK DEFAULT — NOT VERIFIED preserve uncertainty rather than filling absent values.

Audit utilities write only inside this new audit root and inspect saved evidence on CPU. Intermediate working states may be gzip-compressed with round-trip hash receipts; required CSV/JSON data remain unabridged. Start HEAD was `eb3888f5d23310aa097dbb1be14605e931190b4a`. The audit remains uncommitted; nothing was pushed. Existing historical evidence was preserved.
