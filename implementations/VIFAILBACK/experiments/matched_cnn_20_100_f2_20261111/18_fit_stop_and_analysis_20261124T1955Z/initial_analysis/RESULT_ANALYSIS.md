# Completed-scope result analysis

Stop guard armed: finish the current fit, then start no further CNN fits. This is a pre-completion snapshot.

Generated 2026-11-24T19:58:18.922720+00:00. 78 completed fit records; 33 unfinished planned fits. The original 111-fit protocol remains preserved; this administrative cap does not turn its unexecuted work into negative results.

## Training evidence and scope

|Condition|Original planned fits|Completed|Unfinished / not run|
|---|---|---|---|
|FROZEN20|36|36|0|
|FULL20|36|3|33|
|DONOR20|36|36|0|
|FROZEN100|1|1|0|
|FULL100|1|1|0|
|DONOR100|1|1|0|

VERIFIED: independent saved-score arithmetic, per-example identity checks, prediction/metric hashes, F2 fit-lock separation and two-class assessment support within the saved completed scope. Completion/checkpoint lineage is inspected evidence; training was not rerun. Original source/checkpoint hashes remain in FIT_COVERAGE and per-fit COMPLETE receipts.

## Assessment results

The native positive class is whole-episode failure (1). Both-class macro AP is the arithmetic mean of failure-class AP and success-class AP; it is average precision, not trapezoidal PR area. Prevalence varies by assessment fold and is recorded in INDEPENDENT_VERIFICATION.json. Each pooled3 row pools only that seed's three disjoint outer assessments; it is not mean-fold AP and is not a larger sample formed by pooling seeds.

|Condition|Seed|Fold / pooled|N|Visual macro AP|Sensor LR macro AP|F2 macro AP|Historical HGB macro AP|
|---|---|---|---|---|---|---|---|
|FROZEN100|42|0|1107|0.550995|0.707996|0.694219|0.757878|
|FULL100|42|0|1107|0.544332|0.707996|0.699260|0.757878|
|DONOR100|42|0|1107|0.571448|0.707996|0.696600|0.757878|
|FROZEN20|42|pooled3|4382|0.507865|0.648974|0.629280|0.700020|
|FROZEN20|123|pooled3|4382|0.495229|0.648974|0.627039|0.700020|
|FROZEN20|20261023|pooled3|4382|0.487612|0.648974|0.624555|0.700020|
|DONOR20|42|pooled3|4382|0.491368|0.648974|0.627750|0.700020|
|DONOR20|123|pooled3|4382|0.489011|0.648974|0.637852|0.700020|
|DONOR20|20261023|pooled3|4382|0.492185|0.648974|0.630936|0.700020|

HGB is a secondary historical sensor baseline and is not an input to original F2. The 100-epoch rows use their frozen single-bank pilot protocol; they must not be silently pooled with the 20-epoch nested-OOF study.

## Matched visual-training comparisons

|Treatment minus control|Seed|Fold|Visual delta [95% interval]|F2 delta [95% interval]|
|---|---|---|---|---|
|FULL100 minus FROZEN100|42|0|-0.006662 [-0.027982, +0.027078]; inconclusive; not equivalence|+0.005040 [-0.019473, +0.029255]; inconclusive; not equivalence|
|DONOR20 minus FROZEN20|42|0|-0.024263 [-0.083623, +0.026911]; inconclusive; not equivalence|+0.001263 [-0.002532, +0.003649]; inconclusive; not equivalence|
|DONOR20 minus FROZEN20|42|1|-0.010907 [-0.039810, +0.018839]; inconclusive; not equivalence|-0.000424 [-0.002108, +0.001337]; inconclusive; not equivalence|
|DONOR20 minus FROZEN20|42|2|-0.019905 [-0.056637, +0.022343]; inconclusive; not equivalence|+0.000684 [-0.000798, +0.002661]; inconclusive; not equivalence|
|DONOR20 minus FROZEN20|123|0|-0.004086 [-0.024444, +0.036454]; inconclusive; not equivalence|+0.000202 [-0.018798, +0.014141]; inconclusive; not equivalence|
|DONOR20 minus FROZEN20|123|1|-0.009456 [-0.036981, +0.020411]; inconclusive; not equivalence|+0.000936 [-0.002158, +0.004474]; inconclusive; not equivalence|
|DONOR20 minus FROZEN20|123|2|-0.005619 [-0.047814, +0.037791]; inconclusive; not equivalence|+0.001845 [-0.002096, +0.007374]; inconclusive; not equivalence|
|DONOR20 minus FROZEN20|20261023|0|-0.016995 [-0.048555, +0.016889]; inconclusive; not equivalence|+0.010141 [-0.002810, +0.024748]; inconclusive; not equivalence|
|DONOR20 minus FROZEN20|20261023|1|+0.002145 [-0.036688, +0.053587]; inconclusive; not equivalence|-0.001706 [-0.006168, +0.002966]; inconclusive; not equivalence|
|DONOR20 minus FROZEN20|20261023|2|+0.026008 [-0.032273, +0.088120]; inconclusive; not equivalence|+0.000541 [-0.001011, +0.002183]; inconclusive; not equivalence|
|DONOR20 minus FROZEN20|42|pooled3|-0.016497 [-0.032908, +0.001339]; inconclusive; not equivalence|-0.001530 [-0.002673, -0.000237]; negative conditional interval|
|DONOR20 minus FROZEN20|123|pooled3|-0.006219 [-0.025260, +0.012160]; inconclusive; not equivalence|+0.010813 [+0.006082, +0.015846]; positive conditional interval|
|DONOR20 minus FROZEN20|20261023|pooled3|+0.004573 [-0.021106, +0.035886]; inconclusive; not equivalence|+0.006381 [+0.003638, +0.009305]; positive conditional interval|
|DONOR100 minus FROZEN100|42|0|+0.020453 [-0.015122, +0.051843]; inconclusive; not equivalence|+0.002381 [-0.006076, +0.011112]; inconclusive; not equivalence|

Intervals resample paired canonical-task clusters conditional on fixed fitted models. They omit refitting, seed variability, donor/selection uncertainty and unverified session/operator dependence. These are exploratory marginal intervals without multiplicity adjustment. An interval crossing zero is inconclusive and does not establish equivalence.

## Limits and unfinished questions

FULL20 is limited to seed42, outer fold0 when the current inner2 fit completes. It cannot establish three-fold or three-seed full-CNN stability. FROZEN20 and DONOR20 retain their completed three-fold/three-seed coverage. Finishing inner2 permits the already specified outer0 F2 analysis only after all three inner OOF roles and the outer-final receipt pass the unchanged gates; in-sample replacements are prohibited. Any other uncompleted FULL20 assessments remain untested.

The study remains retrospective completed-episode classification on previously examined tasks. No new independent cohort, online early-warning, deployment readiness or general robustness claim follows. No new corruption/GPU experiment is launched under this stop instruction. Donor features reuse learned source CNN weights, whereas the other arms use their recorded original initialization; neither detector heads nor a full detector training path should be inferred.

INFERRED resource constraint: completing the remaining FULL20 matrix would require approximately 47 additional GPU days as a planning allowance on the current single T4 (approximately 43 days at the measured split-weighted central rate, with variation and overhead). This is estimated future runtime, not47 elapsed GPU days and not a model-performance result. The researcher therefore stopped new CNN training; this is not evidence that the unfinished models performed poorly.

## Independent arithmetic checks

162 model/cohort metric vectors (972 scalar AP/AUROC/Brier/log-loss checks) and 2 independently implemented paired task-bootstrap intervals agree within 1e-10. See INDEPENDENT_VERIFICATION.json. No raw payload scan, model inference or training is performed by this analysis script.

## Reproducibility and handoff

CONTROL_REQUEST.json retains the exact researcher authorization; STOP_RECEIPT.json records the intentional boundary stop. FINAL_STATUS.json records analysis exit status and the hard three-hour post-fit limit. before_stop/, after_training_stop/ and final_evidence/ preserve report/metric snapshots. The next-fit placeholder contains only FIT.lock; it is not a trained fit. Do not restart the original training lane without a new explicit instruction.
