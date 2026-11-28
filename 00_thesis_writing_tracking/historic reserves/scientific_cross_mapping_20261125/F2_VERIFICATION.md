# Independent F2 saved-score audit

**VERIFIED here:** saved-score arithmetic, AP/AUROC, branch parity within the available artifacts, coefficient signs, target/fold identities and recording separation. **Not performed:** training, calibration fitting, inference, new model selection or bootstrap reruns. The result is a post-hoc diagnostic on the existing cohort.

## Inputs and identity

All prediction inputs are existing derived artifacts under `implementations/REASSEMBLE/results/runs/`:

- `sensor_controls_f2_nested_stacking/stacking/oof.npz` and `outer0`–`outer4` NPZ/JSON files: F2 outputs, row indices, branch inputs and fitted metadata.
- `sensor_controls_f2_nested_stacking/assessment/stacker_coefficients.json` and `assessment/results.json`: coefficients and reported estimates.
- `sensor_controls_f2_nested_stacking/sensor_controls/predictions/sensor_statistics_perm00.npz`: independently saved sensor-control predictions.
- `fusion_method_comparison/predictions/oof.npz` and `assessment/results.json`: reused U1/U2, F1 and F2 comparisons.
- `unimodal_baselines_visual_sensor/cohort.parquet` and `nested_splits.json`: action identity, native outcome and recording partitions.

The audit checks 4,530 rows, 509 failures, 148 recordings, unique `(recording_id, segment_id)`, exact target/fold agreement, one-time assessment coverage, and outer train/test recording disjointness. The saved branch columns explicitly identify visual then sensor inputs; Section 2 maps U1 to sensor and U2 to vision. F1 equals their mean. F2 exactly matches the reused Section 2 output.

**Availability limit:** the original unimodal `predictions/` directory is empty at this location. Visual parity is verified between Section 1B's saved held-out branch columns and Section 2 U2, not against an unavailable original Section 1 prediction file. Sensor parity additionally matches its Section 1B control artifact. This is not a proof of raw-to-score replay or training lineage at every fit. The script records hashes of the inspected inputs, provenance/configuration files and source in [results.json](f2_verification/results.json).

## The diagnostic

For each fold k, the saved model is

`F2_k = sigmoid(b_k + a_v,k p_v + a_s,k p_s)`.

Define the arithmetic omission `q_k = sigmoid(b_k + a_s,k p_s)`. All five sensor coefficients are positive, so q preserves the sensor's ordering within that fold. Empirically, q reproduces both within-fold AP and AUROC to the audit tolerance. Reintroducing the visual term is therefore responsible for the observed within-fold ordering differences in this saved formula.

| Fold (zero-based) | Actions / failures / recordings | Visual coefficient | Sensor coefficient | Intercept |
|---|---:|---:|---:|---:|
| 0 | 753 / 77 / 26 | 3.114287 | 6.555474 | −3.462646 |
| 1 | 964 / 109 / 31 | 3.099190 | 6.709430 | −3.449531 |
| 2 | 1,037 / 125 / 32 | 3.414462 | 6.630403 | −3.427756 |
| 3 | 906 / 99 / 29 | 4.063499 | 6.574018 | −3.550415 |
| 4 | 870 / 99 / 30 | 3.730206 | 6.217766 | −3.565644 |

Saved coefficient metadata agrees across the two available records. Reconstructing F2 gives maximum absolute probability error `2.220446049250313e-16`. The audit independently implements threshold-group AP and verifies it against scikit-learn. Positive–negative pair changes independently reproduce the AUROC differences. No before/after positive–negative ties occur in these folds.

| Fold | Sensor AP | F2 AP | ΔAP | ΔAUROC | Incorrect→correct pairs | Correct→incorrect pairs |
|---|---:|---:|---:|---:|---:|---:|
| 0 | .327705 | .367155 | +.039451 | +.020691 | 2,951 | 1,874 |
| 1 | .471472 | .486088 | +.014616 | +.011674 | 3,082 | 1,994 |
| 2 | .496543 | .507872 | +.011329 | +.024430 | 5,222 | 2,437 |
| 3 | .485953 | .481265 | −.004689 | +.002891 | 3,051 | 2,820 |
| 4 | .379788 | .416211 | +.036423 | +.020045 | 5,422 | 3,892 |

Vision produces **beneficial net pair ordering in all five folds and AP improvement in four**, not uniform AP improvement. Fold 3 is numerically consistent: AUROC counts positive–negative ordering, while AP depends on precision at positive retrieval positions. Its AP decline does not by itself locate the deterioration at the very top of the score ranking. The pair counts are arithmetic diagnostics, not independent observations for inference.

## Pooled scores and the refined caveat

| Predictor | Pooled failure AP | Pooled AUROC | Brier |
|---|---:|---:|---:|
| Sensor | .429391869 | .779324558 | .080448148 |
| Visual | .230658315 | .697794829 | .094298777 |
| F1 probability average | .445742313 | .795061194 | .083373916 |
| Arithmetic q without visual term | .430921919 | .777037449 | .082279551 |
| F2 | .447298551 | .794968361 | .078443012 |

Although q preserves every within-fold sensor ranking, it changes pooled AP and AUROC. Each fold has its own intercept and slope, so comparisons between examples from different folds can change. Pooled AP rises by 0.001530 while pooled AUROC falls by 0.002287; this is a score-alignment effect, not evidence that “recalibration improved every metric.” Brier is a probability-quality score, not a pure calibration measure.

F2−sensor pooled AP is 0.017906682. The earlier reported recording-bootstrap interval is [0.008603, 0.028284]; F2−F1 is 0.001556239 with interval [−0.007607, 0.011165]. These intervals were read, **not independently rerun**. They condition on fitted models and do not incorporate new fitting, architectural selection or dataset-selection uncertainty. The five folds have overlapping training populations and are not five independent replications.

The omission q is **not an independently fitted sensor-only second-stage model**. Its intercept and slope were estimated jointly with the visual term; setting vision to zero defines a valid constant reference that is not uniquely privileged for pooled attribution. Even if the pooled difference is decomposed arithmetically through q, the two increments are not causal or uniquely attributable percentages. A different constant reference can change cross-fold alignment while retaining the same within-fold sensor ordering.

The scientifically justified correction is:

> The visual term supplies a verified incremental ordering contribution within the evaluated held-out folds. The absence of a matched sensor-only second-stage model still limits attribution of the full pooled pipeline gain. The observed contribution is neither uniform AP improvement nor an estimate of causal visual importance or population-level benefit.

This also distinguishes useful conditional complementarity of the evaluated representations from a claim about information content in the raw modalities. F2's coefficients are not reliability weights, and positive signs alone would not have established the ordering benefit.

## Reproduction of this arithmetic check

The actual successful command, from the repository root, was:

```bash
/home/student/Master_Thesis_WS/.venv/bin/python 00_thesus_writing_tracking/scientific_cross_mapping_20261125/f2_recompute.py --out 00_thesus_writing_tracking/scientific_cross_mapping_20261125/f2_verification
```

That output directory now exists; the script deliberately refuses to overwrite it. A later authorized audit should use a fresh output directory and an existing compatible environment. This recorded absolute interpreter is execution provenance, not a new portable configuration default. Python/package versions, timestamps, HEAD and input hashes are retained in the JSON. AP uses `average_precision_score`, not trapezoidal PR area. No new test dataset was created; this is analysis of the saved scientific assessment artifacts explicitly requested by the researcher.
