# Original static F2 and100epoch follow-up

Audit date: 2026-11-03. Read-only reconstruction; no new model fitting, feature extraction or experiment changes.

Original pooled5outer F2 AP **0.447298551440**, AUROC **0.794968361094**; sensorAP **0.429391869368**, visualAP **0.230658315043**. F2−sensorAP **+0.017906682072**, paired recording95% interval **[0.008602699847,0.028284279537]**,2000draws conditional on saved models. This is the original canonical static F2 result, not C20 fusion. On originalouter1 alone F2AP0.367155245715, sensor0.327704564506.

| Same753assessment /seed42 | AP | AUROC | F1 at0.5 | Brier |
|---|---|---|---|---|
| Frozen100visual |0.193775577615|0.664604626143|0|0.089570168276|
| Full100visual |0.212584503339|0.675324675325|0.070588235294|0.089255169208|
| Canonical static sensor |0.327704564506|0.723680165988|0.252631578947|0.081479485480|
| Frozen100F2 |0.334977351562|0.728675170983|0.177777777778|0.080453165174|
| Full100F2 |0.349094220121|0.740298163375|0.177777777778|0.080157140841|
| Frozen100average |0.348006752040|0.721240298163|0.073170731707|0.081604536011|
| Full100average |0.358533402216|0.745984784446|0.074074074074|0.080793130568|

Follow-up F2 uses calibrated branch probabilities and saved signed logistic coefficients, fixedC1, lbfgs, max_iter2000, unweighted fit; no probability-to-logit transform or second fused calibrator. The static branch is the original canonical220statLR/calibrator. A genuine920-row base-held-out bank supports stacking, but this is not the original complete4inner-fold100epoch OOF design. Common0.5 metrics above are separate from native thresholds: sensor0.14, frozenF20.10, fullF20.14.

Paired recording intervals: fullF2−frozenF2AP **+0.014116868559**,95% **[-0.00077261755,0.02908933571]**; fullF2−sensor **+0.021389655616**,**[-0.00034530379,0.03635822909]**; frozenF2−sensor **+0.007272787057**,**[-0.00315139872,0.01537746535]**. Both F2 variants exceed their corresponding visual-only branch with positive conditional intervals, but the fusion-versus-fusion and fusion-versus-sensor gains are inconclusive. Averaging has a higher point AP in this pilot; no final architecture is selected on this reused test set.

Do not equate visual fine-tuning improvement with established fusion improvement. The follow-up supports a conditional point estimate, one seed/onefold; the original broader F2 is a different fitted protocol. C20 F2 finalization remains NOT EXECUTED. Every M1–M7 metric, subgroup/calibration/native-threshold table and bootstrap contrast is linked in COMPLETE_RESULTS/RESULTS_PROVENANCE; large prediction/draw banks stay at original paths.

## Evidence anchors

- [runs/reassemble/20260927T175336Z-section1b/assessment/results.json](../../../../runs/reassemble/20260927T175336Z-section1b/assessment/results.json) — metrics, paired recording intervals, complementation.
- [runs/reassemble/20260927T175336Z-section1b/assessment/stacker_coefficients.json](../../../../runs/reassemble/20260927T175336Z-section1b/assessment/stacker_coefficients.json) — five fitted F2 coefficient states.
- [src/reassemble/section1b.py](../../../../src/reassemble/section1b.py) — fit_stacker; nested calibrated probability inputs.
- [experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/07_evaluation_results/ALL_MODEL_METRICS.json](../../../../experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/07_evaluation_results/ALL_MODEL_METRICS.json) — M1–M7 common-threshold metrics.
- [experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/07_evaluation_results/PAIRED_RECORDING_BOOTSTRAP.json](../../../../experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/07_evaluation_results/PAIRED_RECORDING_BOOTSTRAP.json) — conditional paired recording intervals.
- [experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/07_evaluation_results/HISTORICAL_COMPARABILITY.json](../../../../experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/07_evaluation_results/HISTORICAL_COMPARABILITY.json) — canonical sensor identities and stacking-bank limitations.
