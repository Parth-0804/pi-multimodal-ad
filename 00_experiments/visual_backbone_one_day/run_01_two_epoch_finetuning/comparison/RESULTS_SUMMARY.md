# Asymmetric epoch-budget backbone study — COMPLETE

All five outer folds are completely assessed for every condition, using the same 4,530 held-out segments. All 100 visual fits and 20 condition/fold assessments are complete.



| Condition | Epochs | Visual AP | Sensor AP | F2 AP | Common folds |
|---|---:|---:|---:|---:|---:|
| frozen_16_frames | 5 | 0.221644 | 0.420803 | 0.440680 | 5/5 |
| fine_tuned_16_frames | 2 | 0.224466 | 0.420803 | 0.437521 | 5/5 |
| frozen_32_frames | 5 | 0.219427 | 0.420803 | 0.439584 | 5/5 |
| fine_tuned_32_frames | 2 | 0.230609 | 0.420803 | 0.438566 | 5/5 |


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


AP is sklearn average_precision_score on directly keyed outer assessment predictions. Mean-fold AP, AUROC, fixed-threshold metrics and Brier scores are separate numerical tables.

contrast,AP_difference,percentile_95_low,percentile_95_high,replicates_requested,valid_replicates,undefined_discarded,seed,primary,interpretation
visual:fine_tuned16_minus_frozen16,0.0028227133368223,-0.033562560592193,0.0378911278967617,2000,2000,0,314159,False,Conditional recording-cluster sampling uncertainty; secondary intervals unadjusted/exploratory; no repeated-training uncertainty
visual:frozen32_minus_frozen16,-0.0022165453469977,-0.0115034043738807,0.0068355952627195,2000,2000,0,314159,False,Conditional recording-cluster sampling uncertainty; secondary intervals unadjusted/exploratory; no repeated-training uncertainty
visual:fine_tuned32_minus_fine_tuned16,0.0061430112757328,-0.0048402254763355,0.0175236093761098,2000,2000,0,314159,False,Conditional recording-cluster sampling uncertainty; secondary intervals unadjusted/exploratory; no repeated-training uncertainty
visual:interaction,0.0083595566227305,-0.0060753468239324,0.0226556764218761,2000,2000,0,314159,False,Conditional recording-cluster sampling uncertainty; secondary intervals unadjusted/exploratory; no repeated-training uncertainty
fused:fine_tuned16_minus_frozen16,-0.0031590903884096,-0.0125727029231496,0.0080520036154493,2000,2000,0,314159,True,Conditional recording-cluster sampling uncertainty; secondary intervals unadjusted/exploratory; no repeated-training uncertainty
fused:frozen32_minus_frozen16,-0.0010962398579029,-0.0041132701253502,0.0018087909028193,2000,2000,0,314159,False,Conditional recording-cluster sampling uncertainty; secondary intervals unadjusted/exploratory; no repeated-training uncertainty
fused:fine_tuned32_minus_fine_tuned16,0.0010453887185452,-0.0023956230352414,0.0044653399442649,2000,2000,0,314159,False,Conditional recording-cluster sampling uncertainty; secondary intervals unadjusted/exploratory; no repeated-training uncertainty
fused:interaction,0.0021416285764481,-0.002804708420673,0.0067528273436474,2000,2000,0,314159,False,Conditional recording-cluster sampling uncertainty; secondary intervals unadjusted/exploratory; no repeated-training uncertainty
frozen_16_frames:F2_minus_sensor,0.0198772487613049,0.0074895040766011,0.031002556607696,2000,2000,0,314159,False,Conditional recording-cluster sampling uncertainty; secondary intervals unadjusted/exploratory; no repeated-training uncertainty
fine_tuned_16_frames:F2_minus_sensor,0.0167181583728953,0.0055161902476875,0.0289712787727456,2000,2000,0,314159,False,Conditional recording-cluster sampling uncertainty; secondary intervals unadjusted/exploratory; no repeated-training uncertainty
frozen_32_frames:F2_minus_sensor,0.018781008903402,0.0075178466822022,0.0290902129804703,2000,2000,0,314159,False,Conditional recording-cluster sampling uncertainty; secondary intervals unadjusted/exploratory; no repeated-training uncertainty
fine_tuned_32_frames:F2_minus_sensor,0.0177635470914406,0.0069238867999084,0.0294536897099567,2000,2000,0,314159,False,Conditional recording-cluster sampling uncertainty; secondary intervals unadjusted/exploratory; no repeated-training uncertainty




This is an asymmetric epoch-budget comparison: frozen heads use five epochs, final-stage plus head use exactly two joint epochs. It is not an equal-epoch/equal-compute fine-tuning isolation, convergence study, optimal architecture claim, robustness test or completion of unobserved folds. Recording-cluster bootstrap uncertainty conditions on these fitted models; one observed fold cannot establish variation across unobserved folds. One seed family; previously exposed REASSEMBLE cohort; fixed0.5 threshold. No outer scores select settings, stopping, folds or batching. Historical Task4 remains excluded. Review is self-review; independent review is outstanding.

Wall-time limit removed by the user's explicit amendment on 2026-10-21T07:34:32.050891+00:00. There is no training cutoff or hard deadline. Frozen16/32 retain five epochs; fine-tuned16/32 use exactly two joint epochs. Cumulative GPU/CPU/storage/fit/diagnostic limits remain unchanged. The old24h clock/config fields are preserved as historical checkpoint provenance; execution_policy.json records the effective policy.

Next decision: Review the completed matched evidence before authorizing any additional scientific change.
