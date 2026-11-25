# Proposed study protocol — not approved for execution

Protocol version: UNSET
Protocol hash after finalization: UNSET
User approval reference and date: UNSET
Approved code snapshot including dirty/untracked source: UNSET
Approved dataset(s) and versions: UNSET
Status: PROPOSED / NOT APPROVED

This template asks for decisions; it does not supply or silently approve them.
A later controller must protect the approval record from implementation agents.
Changes after approval create a new version; never overwrite historical decisions.

## 1. Research question and scope

Primary goal reported by the user: independently test adaptive-fusion robustness.
Operational research question: TO SPECIFY.
Task, prediction timing, target provenance, evaluation unit, and available process
context: TO VERIFY AND SPECIFY.

Define what will count as evidence for robustness, what would contradict the
hypothesis, and what cannot be claimed. A valid negative result is acceptable.
State whether each study is exploratory, confirmatory, or replication, based on
actual prior exposure and selection—not a desired label.

## 2. Evidence baseline

List verified current components, historical producing sources, existing studies,
and remaining validity issues. Distinguish source inspection from historical
execution and from independent metric reconstruction. List existing corruption
studies before authorizing any duplicate.

Name previously exposed assessment data and how further reuse will be described.
Do not declare a repeatedly inspected cohort a fresh confirmation set.

## 3. Sampling, data, and split contract

Dataset version/licence; native target or derived target and validation; unique
sample key; grouping unit; recording/subject/object/environment boundaries;
train/validation/test assignments; leakage checks; temporal support; modality
synchronization and missing-data handling. All fit operations must respect these
boundaries, including encoder fine-tuning, quality estimators, scalers, calibration,
thresholds, feature selection, and fusion training.

For a second dataset, distinguish method retraining from weight transfer. Lock the
method before final assessment. Screen feasibility using documentation and allowed
development data, not hidden test outcomes.

## 4. Minimal comparisons

Specify single-modality models, competitive static fusion, adaptive fusion, and a
constant-weight version of the same mixing rule to isolate adaptivity where valid.
State shared representations, classifier/calibration differences, capacity and
training-budget differences, and fairness limitations.

Optional fine-tuning: identify pretrained initialization and exact trainable layers,
normalization-layer state, learning rates by parameter group, weight decay, loss,
class weighting, batch size, augmentation, stopping criterion, seeds, and cost.
Compare static and adaptive fusion under each encoder condition. Rebuild learned
feature banks within the correct training partitions. Do not treat a cached-feature
freeze flag as an end-to-end gradient path.

Optional transformer: choose a spatial representation or temporal modelling
hypothesis, exact representations and pooling, and a control that isolates that
change. Full detector use is not required merely to justify a checkpoint name.

## 5. Robustness protocol

Predefine corruption families, raw-input insertion points, severities, seeds,
physical units, train-only scale estimates, and label-preservation rationale.
Start with one corrupted modality and one clean modality; separate degradation
from known total absence and silent failure. Do not use evaluation-label-derived
quality signals or oracle corruption severity in ordinary deployment models.

Keep the same held-out samples across paired model/condition comparisons. Check
that raw corruption is followed by the correct feature and quality recomputation.
Freeze models and thresholds for clean-trained robustness tests. Corruption-aware
training requires a distinct approved study, including unseen-condition assessment.
The historically excluded Task 4 is not authorized by completing this template.

## 6. Outcomes and interpretation

Define positive class and exact AP/AUPRC convention. Specify primary outcome,
absolute corrupted performance, clean-to-corrupted difference, recall and calibration,
uncertainty method using the independent sampling unit, paired comparisons, seeds,
multiplicity/exploratory qualification, and stopping rule.

A small AP drop is not enough to establish superior performance. Gate movement is
not sufficient evidence of useful adaptivity or causal attribution. Include modality
sensitivity analysis without equating it to an exact percentage contribution.
Do not select favorable conditions or thresholds after looking at held-out outcomes.

## 7. Portability and reproducibility

Record shared-core changes versus dataset-adapter changes, data-schema checks,
configuration differences, dependency/environment lock, code and artifact hashes,
commands, trainable/total parameters, cost, device/determinism limitations, and
expected reproduction tolerances. Separate repeatable inference, training reruns,
metric reconstruction, and successful installation.

## 8. Authorization and resource limits

Allowed writable paths: UNSET
Protected raw-data, historical-artifact, and approval locations: UNSET
Permitted data access and approved external services: UNSET
Model/API allowance or hard spend ceiling: UNSET
Compute device; GPU-hour and wall-time limits: UNSET
Maximum trials, seeds, retries, concurrency, and storage: UNSET
Maximum downloads, licences and permitted publication: UNSET
Actual enforcement mechanism and stop/resume tests: UNSET

No missing budget means unlimited budget. No model can sign its own approval.
Require one implementation writer, a separate evidence verifier, fail-closed
permission/budget gates, durable state, and logs of every attempted run.

## 9. Completion and exceptions

Acceptance tests cover validity and evidence, not a desired score. A failed validity
check blocks interpretation. A negative result with a sound protocol completes the
study. Block dependent tasks when required evidence is absent; continue only unrelated
authorized tasks. Escalate material task/label/protocol changes and resource overruns.

UI remains a separate, later inspection task. It must show actual saved outcomes,
provenance, uncertainty, and corruption conditions; playback is not live detection.
