# Section 2 completion and IDE handoff

**COMPLETE — A. SIMPLE FUSION SUFFICIENT. STOP before Section 3.**

No training or bootstrap process remains running. Do not rerun the completed driver.
Section 1 and Section 1B, including their continuation files, remain frozen.

## Scientific result

- F2 learned static fusion: AUROC 0.79497, AUPRC 0.44730; exact Section 1B reuse.
- F1 uniform: 0.79506 / 0.44574, with poorer Brier/ECE than F2.
- F3 concatenation: 0.78558 / 0.41223; no demonstrated advantage over U1.
- F4 process gate: 0.78151 / 0.44373.
- F5 quality gate: 0.77599 / 0.44455.
- F6 process+quality gate: 0.77552 / 0.44136.
- All gates have lower AUROC than F2 with paired intervals excluding zero;
  their AP differences are unresolved and all point estimates lower.
- Context changes weights, but no clean predictive benefit is established.
- Same-cohort adaptive exploratory study; no independent confirmation.
- SQ3: NOT YET ANSWERED. No corruption/audio/modality-dropout was run.

## Authoritative artifacts

Final report: `artifacts/reassemble/reports/SECTION_2_FUSION_HANDOFF.md`.
Run: `runs/reassemble/20260927T192852Z-section2`.
Config / protocol: `configs/reassemble/section2.json`, `docs/reassemble/SECTION_2_PROTOCOL.md`.
Implementation commit: `e65d1da`; Section 1B final evidence: `4089b02`.

- `assessment/results.json`: all primary metrics, comparisons, folds and seed variability.
- `assessment/gate_weights.json`: action/fold/recording/outcome weight distributions.
- `assessment/review_comparisons.json`: explicitly post-hoc descriptive paired contrasts.
- `assessment/review_decision.json`: final reviewed shortlist U1/F2/F4.
- `finalization/SECTION_2_FUSION_HANDOFF.md`: final reviewed copy.
- `assessment/SECTION_2_FUSION_HANDOFF.md`: original generated report, retained.
- `inputs/`: strictly nested training branch probabilities and fold memberships.
- `fits/`: candidates, seed outputs and final checkpoints.
- `predictions/oof.npz`: every model, seed, gate weight and context ablation.
- `validation.json`, `output_manifest.json`: checks and artifact identities.

Original automated recommendation selected F5 by AP point rank; final review
corrects it to F4 using uncertainty, cost and stability. Original outputs retain
that automatic suggestion. Use the reviewed report and review_decision.json.

## Validation and preservation

55 tests passed in 8.75 seconds; dependency and whitespace checks passed.
857 Section 1 and 330 Section 1B frozen manifest entries remain unchanged.
68,745 protected metadata entries and 149 raw-recording metadata entries match.
20 inner matrices, 80 additional subfold partitions and 60 final seed fits audited.
U1/U2/F2 exact reuse and gate/ablation arithmetic verified. All numerical caches
stay local and ignored; no raw data, credentials or environments committed.

Scripts: `09_section2.py` (completed driver), `10_validate_section2.py` (completed
audit), `11_review_section2.py` (preserved post-hoc calculation; originally executed
as identical inline code). These scripts refuse to overwrite final evidence.
Pre-modelling patch sandbox error and final recommendation correction are logged.
No architecture/epoch/seed budget was expanded after observing outcomes.

## Exact next action

Researcher reviews the final handoff and separately authorizes a frozen Section 3
protocol. Suggested maximum: U1, F2 and F4 as a mechanism control. F4 has no quality
input; if quality-awareness falsification is the priority, explicitly substitute
F5 for F4 in that future protocol. Do not automatically add models or run corruption.
Find the final results commit with:
`git log -1 --format=%H -- artifacts/reassemble/reports/SECTION_2_FUSION_HANDOFF.md`.
Leave unrelated pre-existing Intel/storage untracked files untouched.

SECTION 3 GO — STATIC FUSION IS THE APPROPRIATE ROBUSTNESS REFERENCE
