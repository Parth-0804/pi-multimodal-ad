## Findings and practical decision

All 100 planned visual fits and all 20 condition/fold assessments are complete. Every comparison uses the same 4,530 held-out segments across all five outer folds. Failure is the positive class; AP is sklearn average precision, with higher values better.

Frozen16 has the highest observed pooled F2 AP (0.440680). The shared sensor-only AP is 0.420803; frozen16 fusion adds +0.019877 AP (about 1.99 percentage points). Its exploratory recording-bootstrap 95% interval for F2 minus sensor is [0.007490,0.031003]. The gain is consistent with complementary image information under these fixed fits. This comparison does not isolate that mechanism from the extra stacking/calibration stage, and F2 coefficients do not measure causal modality percentages.

The predeclared primary contrast, fine-tuned16 minus frozen16 F2, is -0.003159, with recording-cluster 95% interval [-0.012573,0.008052]. The interval includes zero. These results do not demonstrate a fusion benefit from the two-epoch fine-tuning recipe, and they do not establish that frozen16 is universally superior.

Fine-tuned32 has the highest observed visual-only AP (0.230609), but its F2 AP (0.438566) remains below frozen16's point estimate. Using 32 rather than 16 frames changes frozen F2 AP by -0.001096 and fine-tuned F2 AP by +0.001045; the predeclared intervals for both frame contrasts include zero. A visual-only point improvement did not yield a demonstrated fusion improvement.

Recommended next decision: retain frozen16 as the practical reference for discussion with the professor, given its observed fusion performance and lower fitting cost. Obtain independent review of the keyed predictions, leakage controls and interpretation before authorizing another scientific variant. This report does not launch further work.

## What was held fixed

The four recipes share the eligible cohort, recording-group outer/inner partitions, sensor representation, sensor fitted branches within each partition, recording-disjoint calibration, F2 probability-level logistic stacking, preprocessing, frame lists, head architecture, mean pooling, seed family and FP32. Frozen recipes train the classifier for five epochs. Fine-tuned recipes train the head and final CNN stage for exactly two epochs. Earlier CNN weights and normalization buffers remain fixed. No detector decoder or temporal transformer is part of the executed image forward path.

Each outer fold uses four inner OOF visual fits and one separate final visual fit per condition. Raw branches train only on G; C contains disjoint recordings for sigmoid calibration. The F2 stacker learns from one held-out calibrated visual/sensor probability pair per outer-training sample. Outer assessment recordings are excluded from raw fitting, calibration and stacking. No model is refit on all data in this study.

## Uncertainty and interpretation limits

The comparison is an asymmetric epoch-budget comparison of five frozen epochs versus two fine-tuned epochs. It is not a pure equal-epoch or equal-compute isolation of backbone adaptation, a convergence study, or evidence of architectural optimality. There is one seed family and the REASSEMBLE data had already been examined. The target is completed-action failure classification, rather than online warning.

All 2,000 predeclared paired recording-cluster bootstrap draws were valid; none were discarded. Recordings are the resampling unit and all conditions share each draw. These intervals condition on the fitted models/data and do not include repeated-training or seed uncertainty. Secondary intervals are exploratory and unadjusted. Pooled AP and mean-fold AP are distinct and are both supplied in the numerical tables. Threshold metrics use 0.5 throughout. The12 changed-prediction examples are deliberately selected illustrations, not independent evidence.

## Cost, evidence and handoff

The original shared 16/32-frame feature extraction took 2.84h, including 2.35h of pixel loading/cache/transfer. Frozen-head fit timings exclude this original CNN extraction; cached-feature prediction timings do not represent deployment latency from raw images. The measured extraction costs and full pixel-to-probability replay costs are retained separately.

Across 25 completed fits per condition, summed raw fitting and C/V prediction wall times were:

| Condition | Raw fitting hours | C/V prediction hours |
|---|---:|---:|
| frozen_16_frames | 0.164 | 0.000 |
| fine_tuned_16_frames | 9.086 | 3.424 |
| frozen_32_frames | 0.160 | 0.000 |
| fine_tuned_32_frames | 12.456 | 5.118 |

The final training-complete event was 22 October 2026 at 15:50 Berlin time. The supervised resumed run began 21 October at 09:37 Berlin, about 30h 13m earlier. These calendar times differ from summed component timings because some frozen work and a partial checkpoint predate the resumption, and timing scopes differ. Earlier preparation, the superseded five-epoch fine-tuned outputs and the external priority pause remain separate historical evidence.

Final validation covers100 fit epochs/coverage/update counts, all compact-model and prediction hashes,20 assessment/OOF lineages, direct F2 coefficient arithmetic and all 12 pooled AP values. Saved-model full pixel replays passed for all 100 fits. The archive is checked for CRC, payload hashes and AP reproduction directly from its20 keyed assessment CSVs. Large weights/caches remain local with absolute-path/checksum references. Compact models, calibrators and F2 coefficients are retained. Completed optimizer checkpoints were released only after verified prediction replay under the recorded retention rule; the paused-checkpoint snapshot and historical checkpoints were preserved. Raw data, historical outputs, governing files and preexisting tracked dirty changes were preserved.

This is an assistant self-review. Independent human or separate-agent scientific review remains pending. The implementation, training, final evaluation, plots, reports and review package are complete; professor discussion and thesis writeup are the next research activities. No new experiment is authorized or launched by this handoff.

One proposed later research question, requiring a separate decision: **Is the frozen16 versus fine-tuned16 fusion difference repeatable across training seeds?** The present recording-bootstrap intervals do not answer that question. No repeat-seed runs were launched.
