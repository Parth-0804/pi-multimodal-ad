# Section 1B completion and IDE handoff

Status: **COMPLETE — FUSION GO. STOP before Section 2.**

No computation remains running. Do not restart training or rerun the completed driver.
The next action is researcher review of the final report and explicit authorization
of a bounded Section 2 comparison. Full fusion architectures, adaptive gates,
corruptions, audio, RT-DETR backbone fine-tuning, and extended PatchTST are not authorized.

## Results

- Sensor permutation control: observed AUROC 0.779325 / AUPRC 0.429392;
  19 conditional nulls; plus-one p = 0.05 for each metric.
- RT-DETR correctly identifies 97 failures missed by sensor statistics, across
  61 recordings; failure-only diagnostic oracle recall = 0.8055.
- Static two-probability logistic stacking: AUROC 0.7950 / AUPRC 0.4473.
- Paired recording bootstrap: AUROC gain 0.0156 [0.0060, 0.0255];
  AUPRC gain 0.0179 [0.0086, 0.0283]. Four of five fold AP gains positive;
  all five leave-one-fold-out AP gains positive. Failure recall unresolved.
- This is an adaptive exploratory follow-up on the same cohort, not independent
  confirmatory evidence. The oracle is not deployable.

## Artifact map

- Final report: `artifacts/reassemble/reports/SECTION_1B_FUSION_ADMISSIBILITY_HANDOFF.md`
- Current run: `runs/reassemble/20260927T175336Z-section1b`
- Full numerical results: current run `assessment/results.json`
- Original / reviewed reports: `assessment/` / `finalization/`
- Audit / output identities: `validation.json` / `output_manifest.json`
- Inner OOF matrices, subfolds, refits and stacker coefficients: `stacking/`
- Observed/null sensor fits: `sensor_controls/predictions/`
- Config: `configs/reassemble/section1b.json`
- Protocol: `docs/reassemble/SECTION_1B_PROTOCOL.md`
- Runtime correction: `docs/reassemble/SECTION_1B_RUNTIME_CORRECTION.md`
- Source: `src/reassemble/section1b.py`, `src/reassemble/section1b_report.py`
- Entry point: `scripts/reassemble/07_section1b.py`
- Final audit: `scripts/reassemble/08_validate_section1b.py`
  (writes validation with exclusive-create; do not rerun over existing evidence).

## Preservation and validation

47 tests passed before execution. Final pip and whitespace checks passed.
All 857 Section 1 manifest entries and original implementation hashes remain unchanged.
All 68,745 protected metadata entries and 149 raw-recording metadata entries match.
Both branches exactly reproduce frozen Section 1 probabilities in every outer fold.
The original `docs/reassemble/CONTINUATION.md` belongs to frozen Section 1:
DO NOT EDIT IT. Use this new continuation file for this phase.

The initial one-thread BLAS attempt failed strict parity before controls/fusion.
Its files remain in `runs/reassemble/20260927T174424Z-section1b`. The corrected
16-thread run passed without changing scientific settings. No failed output was erased.

## Commits and continuation

Section 1 implementation `852a123`, evidence `08d498d`;
Section 1B predeclared protocol `30ec281`; corrected execution `06f93d1`.
The additive results commit is discoverable with
`git log -1 --format=%H -- artifacts/reassemble/reports/SECTION_1B_FUSION_ADMISSIBILITY_HANDOFF.md`.
Bulk numerical outputs stay ignored locally; do not commit raw data or environments.
Unrelated Intel/storage untracked files predate this phase and must not be swept into commits.

Exact next action: researcher reviews the report. No Section 2 work starts automatically.
