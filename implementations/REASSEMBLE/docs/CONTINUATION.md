# REASSEMBLE continuation — Section 1 complete

## Stop point

**FUSION CONDITIONAL — EVIDENCE REQUIRES REVIEW**

All authorized Section 1 computation is complete. No jobs remain running. Do not
restart extraction/training or start fusion. The researcher must review conditional
unimodal evidence and explicitly approve the next phase. Sections2–4 are future work.

## Read first

- artifacts/reassemble/reports/SECTION_1_UNIMODAL_HANDOFF.md (required A–N report).
- docs/reassemble/SECTION_PLAN.md (user's full new request).
- docs/reassemble/SECTION_1_PROTOCOL.md (frozen before outcomes).
- configs/reassemble/section1.json (exact configuration).
- AGENTS.md (preservation and phase review rules).

## Results

4,530 segments /509 failures /148 recordings; same frozen 5outer/4inner folds,
seed20260927. All44 OOF model/control runs and220 outer assessments completed.
Nineteen full nested permutation refits per deep branch; 2,000 recording-cluster
bootstrap replicates. Failure is positive; AUPRC means average precision.

| Model | AUROC | AUPRC |
| --- | --- | --- |
| Action-only logistic | 0.6851 | 0.1808 |
| Statistical sensor logistic | 0.7793 | 0.4294 |
| Frozen RT-DETR + learned head | 0.6978 | 0.2307 |
| PatchTST | 0.7054 | 0.2416 |

Both deep branches improve AP over action-only with positive paired intervals,
but their AUROC-difference intervals include zero. Both permutation p-values=.05
(minimum resolution), conditional on within-recording/action cyclic exchangeability.
Both primary branch gates CONDITIONAL. The simple sensor model significantly
outperforms PatchTST on both primary metrics. No fusion advantage or absence of
sensor information can be claimed. Complementarity was not computed because both
primary gates did not PASS. No fusion, corruption or audio models were trained.

## Exact evidence and checkpoints

Run: runs/reassemble/20260927T154732Z-section1

- features/:148 ignored per-recording representation caches with hashes.
- predictions/:44 complete OOF NPZs,220 fold NPZs, JSON tuning/control records.
- checkpoints/:5 real RT-DETR heads and5 real PatchTST weights with training scalers.
- assessment/:original generated report, results.json, metrics.md, tuning.json.
- finalization/:reviewed handoff and validation.json.
- config.json, nested_splits.json, provenance.json, environment.json,
  pretrained_model.json, training_implementation.json.
- output_manifest.json: original completed assessment evidence.
- final_output_manifest.json: final evidence, including completed logs.
- failures_and_corrections.md and preservation_validation.json.

Acquisition/audit checkpoint:6721414. Frozen Section1 implementation:852a123.
Final evidence checkpoint: find git log subject `results: record conditional REASSEMBLE unimodal signal gate`.
Actual inputs: ../datasets/REASSEMBLE, outside Git. Preserve raw archives and files.
Pretrained RT-DETR revision:ac77a11ff0170a41b771c03264987f8ce2b0d753.
Prior full input identities: runs/reassemble/20260927T141645Z-inventory/input_manifest.json.

## Validation and limitations

41 tests passed; pip check passed; all prediction labels/folds, frozen protocol,
config, splits, source hashes and output identities verified. 68,745 protected
entries and149 raw H5 metadata unchanged; historical Git blob retained. Roughly
95GiB free. Initial preservation verification mistakenly followed3 Python symlinks;
lstat matching the original snapshot resolved this, with zero changes. No model
training/decoder warnings or errors. No independent full retraining reproduction.

Epochs: RT-DETR heads5,5,10,10,5; PatchTST6 in every outer fold. All PatchTST folds
selected the maximum budget. Longer training/fine-tuning remains untested; do not
silently extend budgets based on these test results. Audio still has unverified
segment clock alignment. Results are retrospective segment classification, not
online early-warning validation. Shared-day/scene/object confounds remain.

## Exact next action

Researcher reviews the report, especially SectionK and paired uncertainty, and
chooses whether to authorize another predeclared unimodal phase or explicitly
approve conditional Section2. Until then STOP. No additional permission is needed
for the completed Section1 work. Do not ask again to rerun already completed jobs.

If Section2 is later approved, keep identical encoders across fusion methods and
fit fusion/calibration/thresholds inside training/inner folds. Do not fit fusion
on the current outer-test OOF predictions and then claim held-out performance.
Inner branch fits may need regenerating in a new run; only final outer neural
weights were retained. Preserve current evidence and checkpoint paths unchanged.
Earlier unrelated Intel and storage-triage files remain unstaged.
