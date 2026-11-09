# Model comparison results

All M1–M7 rows use the same 753 held-out actions,77 failures,676 nonfailures,26 recordings and failure prevalence 0.102258. Higher AP/AUROC/precision/recall/F1 is better; lower Brier/log loss/ECE is better. Precision, recall and F1 use the predefined0.5 threshold. ECE uses15 fixed equal-width probability bins and is descriptive: bins can contain few failures and no calibration superiority claim follows from ECE alone.

| Model | AP | AUROC | Precision | Recall | F1 | Brier | Log loss | ECE15 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Frozen CNN only | 0.193776 | 0.664605 | 0.000000 | 0.000000 | 0.000000 | 0.089570 | 0.319693 | 0.035265 |
| Fine-tuned CNN only | 0.212585 | 0.675325 | 0.375000 | 0.038961 | 0.070588 | 0.089255 | 0.317383 | 0.028265 |
| Static sensor only | 0.327705 | 0.723680 | 0.666667 | 0.155844 | 0.252632 | 0.081479 | 0.292795 | 0.036268 |
| Frozen CNN + F2 | 0.334977 | 0.728675 | 0.615385 | 0.103896 | 0.177778 | 0.080453 | 0.289894 | 0.026295 |
| Fine-tuned CNN + F2 | 0.349094 | 0.740298 | 0.615385 | 0.103896 | 0.177778 | 0.080157 | 0.288338 | 0.028557 |
| Frozen CNN + averaging | 0.348007 | 0.721240 | 0.600000 | 0.038961 | 0.073171 | 0.081605 | 0.292859 | 0.037683 |
| Fine-tuned CNN + averaging | 0.358533 | 0.745985 | 0.750000 | 0.038961 | 0.074074 | 0.080793 | 0.288608 | 0.030672 |


All per-sample probabilities/labels/recording IDs are in06; every metric, confusion matrix and calibration-bin count is in `07_evaluation_results/ALL_MODEL_METRICS.json`. No result is averaged across seeds or folds. There is exactly one trained seed/fold context here.

## Historical M8, shown separately

On the verified same 753 IDs, historical Section1b F2 has AP0.367155, AUROC0.744371, and original training-selected threshold0.10. Its full metrics and saved probabilities are included separately. Historical pooled-all-fold AP0.447298551 is based on4530 actions and must not be compared as if it were a753-action score.

The test cohort/labels/frame count match, but visual branch selection, precision, visual calibration, seeds and full fusion OOF coverage differ; the canonical sensor test probabilities are identical. Therefore M8 is not a controlled treatment estimate against M4/M5 and is not placed into the primary paired-improvement table. Exact comparability findings are in `HISTORICAL_COMPARABILITY.json`.

## Visual evidence and plots

- [Primary sensor/F2 AP](../../../../../../../EXTERNAL_REFERENCES.md)
- [All seven models with conditional AP intervals](../../../../../../../EXTERNAL_REFERENCES.md)
- [Precision–recall curves](../../../../../../../EXTERNAL_REFERENCES.md)
- [Training-side versus outer branch behavior](../../../../../../../EXTERNAL_REFERENCES.md)
- [F2 apparent-fit/meta-crossfit/held-out behavior](../../../../../../../EXTERNAL_REFERENCES.md)
- [Paired differences](../../../../../../../EXTERNAL_REFERENCES.md)
- [Branch disagreements](../../../../../../../EXTERNAL_REFERENCES.md)
- [Calibration](../../../../../../../EXTERNAL_REFERENCES.md)

Every plotted number traces to a saved probability/metric/bootstrap artifact through `FIGURE_SOURCE_MANIFEST.json`. Training-side base scores are held out from base fitting; apparent F2 fitting scores reuse its fitting labels and are explicitly separated from meta-crossfit diagnostics. Different-cohort scores are not paired generalization gains.

## Original native training-only thresholds

The primary table uses the same0.5 convention for every model. These additional rows retain the original sensor and F2 training-selected decision thresholds. AP/AUROC/Brier/log loss are unchanged; precision/recall/F1 reflect the respective native rules. No test threshold was selected.

| Model | AP | AUROC | Precision | Recall | F1 | Brier | Log loss | ECE15 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Frozen CNN only | 0.193776 | 0.664605 | 0.000000 | 0.000000 | 0.000000 | 0.089570 | 0.319693 | 0.035265 |
| Fine-tuned CNN only | 0.212585 | 0.675325 | 0.375000 | 0.038961 | 0.070588 | 0.089255 | 0.317383 | 0.028265 |
| Static sensor only | 0.327705 | 0.723680 | 0.225000 | 0.467532 | 0.303797 | 0.081479 | 0.292795 | 0.036268 |
| Frozen CNN + F2 | 0.334977 | 0.728675 | 0.220000 | 0.428571 | 0.290749 | 0.080453 | 0.289894 | 0.026295 |
| Fine-tuned CNN + F2 | 0.349094 | 0.740298 | 0.349398 | 0.376623 | 0.362500 | 0.080157 | 0.288338 | 0.028557 |
| Frozen CNN + averaging | 0.348007 | 0.721240 | 0.600000 | 0.038961 | 0.073171 | 0.081605 | 0.292859 | 0.037683 |
| Fine-tuned CNN + averaging | 0.358533 | 0.745985 | 0.750000 | 0.038961 | 0.074074 | 0.080793 | 0.288608 | 0.030672 |


Native thresholds: Frozen CNN only=0.50, Fine-tuned CNN only=0.50, Static sensor only=0.14, Frozen CNN + F2=0.10, Fine-tuned CNN + F2=0.14, Frozen CNN + averaging=0.50, Fine-tuned CNN + averaging=0.50.
