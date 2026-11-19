# REASSEMBLE: CNN100 + static-sensor F2 comparison

Completed exploratory single-split comparison.

- [EXPERIMENT_OVERVIEW.md](10_final_research_report/EXPERIMENT_OVERVIEW.md)
- [ARCHITECTURE_VERIFICATION.md](10_final_research_report/ARCHITECTURE_VERIFICATION.md)
- [DATA_SPLIT_AND_LEAKAGE_AUDIT.md](10_final_research_report/DATA_SPLIT_AND_LEAKAGE_AUDIT.md)
- [MODEL_COMPARISON_RESULTS.md](10_final_research_report/MODEL_COMPARISON_RESULTS.md)
- [PAIRED_STATISTICAL_COMPARISON.md](10_final_research_report/PAIRED_STATISTICAL_COMPARISON.md)
- [FUSION_COEFFICIENT_ANALYSIS.md](10_final_research_report/FUSION_COEFFICIENT_ANALYSIS.md)
- [REPRODUCIBILITY_REPORT.md](10_final_research_report/REPRODUCIBILITY_REPORT.md)
- [FINAL_SCIENTIFIC_CONCLUSION.md](10_final_research_report/FINAL_SCIENTIFIC_CONCLUSION.md)

| Model | AP | AUROC | Precision | Recall | F1 | Brier | Log loss | ECE15 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Static sensor only | 0.327705 | 0.723680 | 0.666667 | 0.155844 | 0.252632 | 0.081479 | 0.292795 | 0.036268 |
| Frozen CNN + F2 | 0.334977 | 0.728675 | 0.615385 | 0.103896 | 0.177778 | 0.080453 | 0.289894 | 0.026295 |
| Fine-tuned CNN + F2 | 0.349094 | 0.740298 | 0.615385 | 0.103896 | 0.177778 | 0.080157 | 0.288338 | 0.028557 |

[All keyed test probabilities](06_held_out_predictions/ALL_MODELS_IDENTICAL_OUTER_IDS.csv) · [Real disagreement examples](../../../../EXTERNAL_REFERENCES.md) · [Checkpoint verification](02_checkpoint_verification/VERIFICATION_REPORT.md).
