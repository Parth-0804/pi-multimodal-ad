# Inspection UI requirements — textual specification only

Status: PROPOSED; UI implementation NOT_RUN. Existing tutorials/EDA/reassemble_prediction_player.py is saved completed-segment playback evidence, not an automatically approved starting app.

- Dataset/run selector shows native task, version/licence, validated manifest and evidence status. List only accessible datasets/artifacts; never invent a dataset option with working predictions.
- Sample selector uses stable recording/segment identity and independent group. Show action interval and prediction timing. An anonymous bank cannot be presented as identified sample-level playback until its row binding is validated.
- Modality panel distinguishes available, missing, degraded and unknown. Show recorded video/signals only where actually linked, with units/time alignment and gaps. Camera-derived tracks must be labelled as such.
- Labels appear only where native/approved provenance exists; unknown/unavailable labels stay visibly unknown. Do not turn lifecycle stage or run number into health ground truth.
- Results panel identifies branch/fused probabilities, positive class, training-only threshold, model/config/run identity, and whether the result is saved prediction, verified rerun, reported or unknown. Missing branches abstain; no fabricated fallback probabilities.
- Corruption comparison is available only for existing validated paired condition outputs. State fault family/severity/insertion point/realization and evidence limits. UI selection never launches inference, corruption, extraction or training.
- Display gate/mixture coefficients as model quantities, not causal contribution percentages. Show clean/degraded absolute scores and uncertainty only if their computation and independent unit are validated.
- Provenance drawer links sample order/split/source/config/processor/calibration/threshold identities, exposure/selection history and known limitations. Separate reported from recomputed metrics and reproduced inference/training.
- Controls support filtering/inspection/export of small approved summaries. Export preview lists exact included identities/labels/conditions and excludes raw/private/credential content by default. No service/cloud upload or new account implied.
- Loading/error states name unsupported input, invalid manifest, incomplete history or missing media without substituting demo data. Precomputed outcomes must say “completed-action saved prediction”; no live/real-time promise.
- Later acceptance would use synthetic UI fixtures and validated saved artifacts for navigation/identity/error behavior; no scientific execution needed for an inspection interface. Scope/access/output/deployment require a separate later instruction.

A friendly UI is useful when its visible evidence is trustworthy. Its absence is not a reason to invent results; its implementation is deferred by this session's explicit boundary.
