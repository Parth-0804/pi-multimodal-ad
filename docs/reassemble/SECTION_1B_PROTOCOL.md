# Section 1B: frozen fusion-admissibility protocol

Authorized tasks only: statistical-sensor permutations, descriptive visual/sensor
complementarity, one logistic late-fusion stacker. Section1 code, models, reports,
configs, outputs and its hashed continuation file remain unchanged. PatchTST stays
an SQ1 negative result. No larger visual budget, fine-tuning, adaptive/quality gate,
corruption, audio work or full fusion architecture comparison.

Reuse the same4,530-row complete cohort, five outer/four inner recording folds,
features, branch architectures, candidate C/epoch grids, selection metric, scaling,
calibration and deterministic fitting seeds. The19 statistical-sensor controls use
the same circular shifts within recording/action and seed+10000+permutation.
Record both null AUROC/AP and plus-one p-values, including their0.05 resolution
and conditional cyclic-exchangeability assumptions. Run the true-label statistical
procedure in a new namespace and verify parity with its frozen predictions.
CPU BLAS uses one thread for bounded runtime; this changes execution parallelism,
not the estimator. Require same selected C and probability differences <=1e-5
for parity; stop and document any failure instead of silently replacing evidence.

One fixed L2 logistic stacker, C=1, unweighted likelihood, solver lbfgs, max_iter2000.
Only two input columns: calibrated RT-DETR and statistical-sensor failure probabilities.
No action, identity, quality, duration, masks or raw features enter the stacker.

For every frozen outer fold, regenerate branch predictions over its training rows
using its frozen inner folds. To prevent self-calibration/selection leakage in
these meta-features, each inner-training subset performs the SAME four-fold branch
procedure within itself (new deterministic recording-disjoint subfolds), then
refits and calibrates to predict its held-out inner subset. Those assessment labels
are never used in their branch selection, scaling, calibration or fitting.
Persist all new subfold identities and label-independent membership checks.

Fit the final fixed stacker on this complete outer-training OOF probability matrix.
No extra sigmoid calibrator: logistic likelihood supplies probabilities. Choose
its decision threshold from meta-cross-fitted stacker scores using the frozen
inner group memberships, grid0.01..0.99, maximizing balanced accuracy (tie nearest0.5).
These scores condition on the generated branch OOF matrix and are used only for
training-side threshold selection, not reported as unbiased validation results.
Outer-test data never choose coefficients, thresholds or settings. Refit both
branches using the exact original outer-training procedure and seeds, check their
probabilities against Section1, then apply the fitted stacker to outer-test branch
probabilities. Concatenate the five assessments. Existing outer-test OOF scores
are used only for descriptive complementarity and parity/comparison, never to
fit the stacker or choose its settings.

Complementarity uses the original branch hard decisions/thresholds and probabilities:
Pearson score correlation, binary error correlation, all four correctness cells,
oracle correct-if-either-correct. Report all rows, failures only, all four actions,
and failures within each action. Constant correlations are undefined, not zero.
Oracle accuracy/failure recall is a label-dependent upper-bound diagnostic, not
probability/ranking performance and not a deployable model.

Primary contrast: stacker minus statistical sensors. Same2,000 paired recording
cluster resamples as Section1, all8 metrics, per-fold primary differences and
leave-one-outer-fold-out pooled differences. Intervals condition on fitted models.
Predeclare meaningful AP gain >=0.01, paired95% AP lower bound>0, positive AP gain
in >=3/5 outer folds and all five leave-one-fold-out pooled estimates>0. Require
AUROC paired lower95% bound>-0.01 (noninferiority margin1 percentage point), plus
failure rescues in >=5 recordings with positive clustered lower bound and sensor
conditional permutation AP p<=0.05. This operationalizes the user's incremental
question; the old standalone RT-DETR intersection-union gate is NOT applied.
Unresolved improvement with complementarity gives CONDITIONAL. Essentially no
complementarity, or estimated nonpositive AP gain with upper95% <=0.01, gives NO-GO.
A material contradictory AUROC loss prevents GO. No post-result rule changes.

The follow-up question and selected sensor branch were informed by Section1
results on these same folds. Consequently this is exploratory admissibility
assessment, not independent confirmation or unrestricted architecture-search
permission. Report that selection limitation even if the new gate passes.

Implementation reference: scikit-learn stacking documentation requires cross-
validated base predictions for training the final estimator; calibration guidance
requires separation of base fitting and calibration data. Sources:
https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.StackingClassifier.html
https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV.html

Write SECTION_1B_FUSION_ADMISSIBILITY_HANDOFF.md with all13 requested sections;
STOP afterward for researcher review. No Section2 architectures are authorized.
