# Completed-scope result analysis

The training controller is stopped; remaining CNN work is NOT RUN / PARTIAL — RESEARCHER STOP.

Generated 2026-11-24T22:05:02.666835+00:00. 79 completed fit records; 32 unfinished planned fits. The original 111-fit protocol remains preserved; this administrative cap does not turn its unexecuted work into negative results.

## Training evidence and scope

|Condition|Original planned fits|Completed|Unfinished / not run|
|---|---|---|---|
|FROZEN20|36|36|0|
|FULL20|36|4|32|
|DONOR20|36|36|0|
|FROZEN100|1|1|0|
|FULL100|1|1|0|
|DONOR100|1|1|0|

VERIFIED: independent saved-score arithmetic, per-example identity checks, prediction/metric hashes, F2 fit-lock separation and two-class assessment support within the saved completed scope. Completion/checkpoint lineage is inspected evidence; training was not rerun. Original source/checkpoint hashes remain in FIT_COVERAGE and per-fit COMPLETE receipts.

## Assessment results

The native positive class is whole-episode failure (1). Both-class macro AP is the arithmetic mean of failure-class AP and success-class AP; it is average precision, not trapezoidal PR area. Prevalence varies by assessment fold and is recorded in INDEPENDENT_VERIFICATION.json. Each pooled3 row pools only that seed's three disjoint outer assessments; it is not mean-fold AP and is not a larger sample formed by pooling seeds.

|Condition|Seed|Fold / pooled|N|Visual macro AP|Sensor LR macro AP|F2 macro AP|Historical HGB macro AP|
|---|---|---|---|---|---|---|---|
|FULL20|42|0|1107|0.492370|0.707996|0.697858|0.757878|
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

## Main findings within completed coverage

FULL20 versus FROZEN20, seed 42, fold 0: visual macro-AP +0.004946 [-0.027460, +0.040927]; inconclusive; not equivalence; F2 macro-AP -0.009260 [-0.026854, +0.005016]; inconclusive; not equivalence.

FULL100 versus FROZEN100, seed 42, fold 0: visual macro-AP -0.006662 [-0.027982, +0.027078]; inconclusive; not equivalence; F2 macro-AP +0.005040 [-0.019473, +0.029255]; inconclusive; not equivalence.

The original paired uncertainty results are independently rechecked for the available full-CNN comparisons. A higher point estimate alone does not establish an improvement when its paired interval crosses zero. The completed frozen/donor rows retain their full per-seed pooled results; no seed or fold is selected by the assessment scores.

## Calibration and class-specific trade-offs — seed42, fold0

|Condition|Model|Failure prevalence|AUROC|Success AP|Brier|ECE10|Failure recall@0.5|Success recall@0.5|
|---|---|---|---|---|---|---|---|---|
|FROZEN20|visual|0.8121|0.462239|0.180143|0.160883|0.086163|1.0000|0.0000|
|FROZEN20|sensor_LR|0.8121|0.838517|0.455876|0.151829|0.134535|0.9922|0.0144|
|FROZEN20|average|0.8121|0.815858|0.454688|0.153498|0.108392|1.0000|0.0000|
|FROZEN20|F2|0.8121|0.838298|0.453610|0.153928|0.093255|1.0000|0.0000|
|FROZEN20|historical_HGB|0.8121|0.861133|0.552103|0.139090|0.121841|0.9889|0.1106|
|FULL20|visual|0.8121|0.485652|0.174666|0.163498|0.100908|1.0000|0.0000|
|FULL20|sensor_LR|0.8121|0.838517|0.455876|0.151829|0.134535|0.9922|0.0144|
|FULL20|average|0.8121|0.819923|0.452525|0.155193|0.115692|1.0000|0.0000|
|FULL20|F2|0.8121|0.827928|0.456336|0.156238|0.096522|1.0000|0.0000|
|FULL20|historical_HGB|0.8121|0.861133|0.552103|0.139090|0.121841|0.9889|0.1106|
|DONOR20|visual|0.8121|0.395840|0.161159|0.162919|0.091792|1.0000|0.0000|
|DONOR20|sensor_LR|0.8121|0.838517|0.455876|0.151829|0.134535|0.9922|0.0144|
|DONOR20|average|0.8121|0.796638|0.435212|0.154675|0.111187|1.0000|0.0000|
|DONOR20|F2|0.8121|0.839234|0.456218|0.154447|0.089960|1.0000|0.0000|
|DONOR20|historical_HGB|0.8121|0.861133|0.552103|0.139090|0.121841|0.9889|0.1106|
|FROZEN100|visual|0.8121|0.579185|0.230225|0.161504|0.103025|1.0000|0.0048|
|FROZEN100|sensor_LR|0.8121|0.838517|0.455876|0.151829|0.134535|0.9922|0.0144|
|FROZEN100|average|0.8121|0.766252|0.356029|0.152824|0.108922|1.0000|0.0000|
|FROZEN100|F2|0.8121|0.821126|0.451169|0.143719|0.047361|0.9933|0.0144|
|FROZEN100|historical_HGB|0.8121|0.861133|0.552103|0.139090|0.121841|0.9889|0.1106|
|FULL100|visual|0.8121|0.577522|0.238427|0.158281|0.081011|0.9900|0.0000|
|FULL100|sensor_LR|0.8121|0.838517|0.455876|0.151829|0.134535|0.9922|0.0144|
|FULL100|average|0.8121|0.791879|0.389754|0.150935|0.101691|0.9989|0.0000|
|FULL100|F2|0.8121|0.833875|0.441626|0.143041|0.040342|0.9944|0.0192|
|FULL100|historical_HGB|0.8121|0.861133|0.552103|0.139090|0.121841|0.9889|0.1106|
|DONOR100|visual|0.8121|0.642867|0.264885|0.157289|0.097177|1.0000|0.0000|
|DONOR100|sensor_LR|0.8121|0.838517|0.455876|0.151829|0.134535|0.9922|0.0144|
|DONOR100|average|0.8121|0.816404|0.425664|0.151896|0.113795|1.0000|0.0000|
|DONOR100|F2|0.8121|0.824565|0.449493|0.143810|0.046692|0.9933|0.0144|
|DONOR100|historical_HGB|0.8121|0.861133|0.552103|0.139090|0.121841|0.9889|0.1106|

The threshold remains the predeclared 0.5; no outer-test threshold tuning is performed. Recall, class AP and calibration must be assessed alongside macro AP. ECE10 and threshold summaries in this table are the existing report's values; the independent checks below cover AP, AUROC, Brier and log loss. The same assessment episodes appear across matched model rows.

## F2 fitting — seed42, fold0

|Condition|OOF / pilot meta N|Visual probability coefficient|Sensor probability coefficient|Intercept|
|---|---|---|---|---|
|FROZEN20|3275|-0.562325|+2.735142|+0.152239|
|FULL20|3275|+1.368516|+2.575597|-1.359120|
|DONOR20|3275|-0.093941|+2.673136|-0.191523|
|FROZEN100|788|-0.420886|+3.999794|-1.574092|
|FULL100|788|+1.488361|+3.697490|-3.021647|
|DONOR100|788|-0.289808|+3.930916|-1.630662|

F2 is an L2 logistic model of calibrated visual and sensor-LR probabilities. Signed unrestricted coefficients are not convex weights, causal modality importance or percentages. The 20-epoch fit uses the complete three-inner OOF bank; the 100-epoch pilot uses its distinct predefined held-out meta bank. No assessment labels fit these coefficients.

## Matched visual-training comparisons

|Treatment minus control|Seed|Fold|Visual delta [95% interval]|F2 delta [95% interval]|
|---|---|---|---|---|
|FULL20 minus FROZEN20|42|0|+0.004946 [-0.027460, +0.040927]; inconclusive; not equivalence|-0.009260 [-0.026854, +0.005016]; inconclusive; not equivalence|
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

INFERRED resource constraint: completing the remaining FULL20 matrix would require approximately 47 additional GPU days as a planning allowance on the current single T4 (approximately 43 days at the measured split-weighted central rate, with variation and overhead). This is estimated future runtime, not47 elapsed GPU days and not a model-performance result. The researcher therefore requested stopping further CNN training; this is not evidence that the unfinished models performed poorly.

## Independent arithmetic checks

168 model/cohort metric vectors (1008 scalar AP/AUROC/Brier/log-loss checks) and 4 independently implemented paired task-bootstrap intervals agree within 1e-10. See INDEPENDENT_VERIFICATION.json. No raw payload scan, model inference or training is performed by this analysis script.

## Reproducibility and handoff

CONTROL_REQUEST.json retains the exact researcher authorization; STOP_RECEIPT.json records the intentional boundary stop. FINAL_STATUS.json records analysis exit status and the hard three-hour post-fit limit. before_stop/, after_training_stop/ and final_evidence/ preserve report/metric snapshots. The next-fit placeholder contains only FIT.lock; it is not a trained fit. Do not restart the original training lane without a new explicit instruction.
