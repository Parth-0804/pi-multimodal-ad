# Leakage-safe evaluation feasibility

**Current supervised evaluation gate: BLOCKED.** Zero phase-matched normal/failure pairs and zero training-eligible binary examples are certified. This means unverified support, not that the dataset contains no physical failures. There is no scientifically valid split to materialize yet.

The38 repository entries do not define38 independent groups. All18 sample video chunks duplicate the full cylinder-recovery release, and all60 sample/full episode video offsets/lengths match. They must share recording identity in future splitting. Raw files are preserved; only non-destructive alias evidence is recorded. Expert/recovery relationships and paired events cannot be inferred from matching episode numbers across different repositories.

The released annotation metadata has two operator strings and two session strings (one `initial`), heavily imbalanced. The selected recovery diagnostics all share the provided `op-01`/`2026-04-15` metadata. Expert/session assignments are missing. Operators are not automatically physical experimental independence; task/object and collection session can be confounded. Native `train` slices are not a published leakage-safe classification evaluation.

With only this annotated object/session support and no verified negatives, three outer/two inner folds cannot pass. Splitting windows from the same episode, distributing identical sample/full copies, treating all recovery frames as positive, or inventing session IDs would be invalid fixes. No split-seed search, group substitution or fold reduction was performed.

## Defensible next protocol after prerequisites

1. Obtain/correct native phase conventions, event intervals and clean same-phase controls; retain original annotations plus a separately versioned, reviewer-signed correction/admission table. Audit onset versus cause semantics and failure-resolution meaning.
2. Bind stable episode, physical recording, paired expert/recovery run, operator, collection session and task/object IDs. Collapse exact media aliases only in an analysis registry; preserve raw files.
3. Use this visually inspected pilot as development data. Freeze camera, preprocessing, observation horizon, target and feature allowlist before assessing new holdouts. The current mismatched diagnostic windows cannot become model inputs without a separately reviewed protocol.
4. If sufficient independently collected groups with both classes remain in every training/assessment partition, preregister3 outer×2 inner group folds, seeds42/123/20261023, new frozen-CNN heads, feedback-only sensor models, averaging and true OOF F2. Group every window of the same physical recording/recovery pair together; assess at the native event/phase unit, not repeated frames. Apply train-only standardizers and group-aware uncertainty.
5. If that support does not exist, continue a qualitative feasibility study or collect a fixed new-session/task/object holdout. A task/object-disjoint alternative requires labels for several objects and explicitly changes the generalization claim. An exploratory recording-disjoint study can only make within-collection claims after duplicate/pair binding and class support; it does not certify session/task generalization.
6. Add quality gating only after clean OOF fusion is defensible, with predefined label-free quality variables, missing-branch behavior, unimodal/strong-sensor controls and exposure-matched augmentation.

Report all blocked/negative outcomes, per-group/per-seed counts and prevalence. Do not call position/recovery-behavior discrimination physical force anomaly detection or early failure prediction. No hypothetical fold/model metric is reported as an executed experiment.

Known sample/full deduplication reduces the2,136 repository-entry sum to an upper bound of2076; remaining uniqueness, advertised-count reconciliation and full-release session binding remain open.
