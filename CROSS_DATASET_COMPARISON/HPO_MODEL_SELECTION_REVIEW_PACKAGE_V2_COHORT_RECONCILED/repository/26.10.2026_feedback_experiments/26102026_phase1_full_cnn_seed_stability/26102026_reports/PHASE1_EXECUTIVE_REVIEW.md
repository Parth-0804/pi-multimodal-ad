# Phase 1 executive review — PARTIAL — STOPPED_AT_COMPLETED_BOUNDARY

Updated 2026-10-27T01:41:39.764946+00:00. This is a follow-up experiment on a repeatedly studied dataset.
Completed **1/150 visual fits**: B 1/75, C 0/75.
Completed-fit training totals 0.015 GPU-hours. Recorded child-process
wall time totals 2.610 GPU-job hours, including retries and inference;
an active child's elapsed time appears in `PHASE1_CONTROLLER_STATUS.json`.
CPU-only waiting and sensor analysis are excluded. Earlier audit/pilot GPU-hours
were not completely metered and are not invented or included in this total.

| Task | Status | Evidence |
|---|---|---|
| Historical audit | completed | PHASE1_HISTORICAL_AUDIT.md |
| Exact input / GPU integration | completed | PHASE1_GPU_INTEGRATION.md; full-cohort identity manifest |
| Full CNN gradients / updates | completed | Full-CNN preflight gradient evidence |
| Full-backbone benchmark / epoch recovery | completed | PHASE1_FULL_CNN_GATE.json |
| Long Frozen16 | partial | 1/75 fit receipts |
| Full FineTuned16 | not started | 0/75 fit receipts |
| Three-seed stability | not started | Fixed seeds 42, 123, 20261023; final pooled predictions required |
| Matched F2 retraining | not started | 25 shared sensor fits, 30 main F2 fits; 15 supplemental short-reference F2 fits |
| Final evaluation | not started | Paired recording-cluster bootstrap; folds/seeds not independent samples |
| Reports | partial | Six named reports; result reports remain partial until complete |

| Model | Seeds | Executed / selected epochs | Visual AP | F2 AP | Training GPU-hours |
|---|---|---|---|---|---|
| Historical original Frozen16 A | Original seed family 20260927 | Candidates 5/10; outer selections 5,5,10,10,5 | 0.2306583150 | 0.4472985514 historical F2 | Extraction excluded; original nested head 11.12 s |
| B_long_frozen16 | Three fixed seeds | 1/75 fits complete | Pending complete held-out evaluation | Pending | 0.015 measured completed fits |
| C_full_finetuned16 | Three fixed seeds | 0/75 fits complete | Pending complete held-out evaluation | Pending | 0.000 measured completed fits |

Scientific verdict: supported — exact input equivalence, full executed-CNN
trainability and deterministic epoch-boundary recovery on the pilot.
Unknown — whether longer classifier training or full-CNN fine-tuning improves
visual AP or F2, and whether effects are stable across seeds. A partial run
cannot answer those questions. No accuracy hypothesis is contradicted or
supported by utilization measurements. Phase 2/3 execution is not authorized
here and no selected architecture is ready to recommend from new accuracy
evidence yet.

The protocol fixes 25–50 executed epochs, training-only validation selection,
recording-disjoint outer/inner folds and separate calibration records. All CNN
convolutions and normalization affine parameters train; normalization running
moments remain fixed. Head learning rate 1e-3 and CNN learning rate 1e-5 use
AdamW with fixed cosine scheduling. B reuses identical FP32 frozen features.
Historical A is preserved; supplemental A_r is a matched short-horizon
reconstruction from B's epoch-5/10 snapshots and is identified separately.

Artifacts: `../26102026_configuration/PHASE1_CONFIG.json`; `../26102026_evidence/PHASE1_FIT_PLAN.json`; `../26102026_execution/26102026_main_run_01/` (fit-specific logs, hashes, selected models, two epoch recovery generations, learning curves, keyed predictions, F2 coefficients and final metrics). Controller stage: STOPPED_AT_COMPLETED_BOUNDARY. Disk free: 73.7 GiB.
