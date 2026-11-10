# Reproducibility assessment

Audit date: 2026-11-03. Read-only reconstruction; no new model fitting, feature extraction or experiment changes.

| Model/study | Code available | Config available | Checkpoint available | Predictions available | Split available | Overall status |
| --- | --- | --- | --- | --- | --- | --- |
| Phase1 C20/B and B/C100 | Yes,with provenance | Yes | Best + rotating resumable last states | Yes | Yes | COMPLETE saved chain; training replay not performed |
| Original REASSEMBLE branches | Yes | Yes | Selected outer states; many inner states absent | Yes | Yes | PARTIAL |
| Original F2 | Yes | Yes | JSON coefficients | Yes,OOF and held-out | Yes | COMPLETE fitted-state chain |
| 100-epoch F2 | Yes | Yes | Coefficients/calibrators | Yes,M1–M7 | Yes,920 stack and753 assessment | COMPLETE artifacts; limited design |
| MSM/Handover baselines | Yes | Yes | Fitted heads/LR/HGB | Yes | Yes;Handover participants absent | INFERENCE_ONLY / PARTIAL exact resume |
| MSM F2/gates | Yes | Yes | JSON/PT states | Yes,OOF/held-out | Yes | INFERENCE_ONLY |
| Handover F2/gates | Yes | Yes | No | No | Participant OOF unavailable | MISSING_ARTIFACTS; NOT EXECUTED |
| Vi frozen V1/high-only | Yes | Yes | BEST and FINAL_EPOCH100 | Yes | Yes,task groups | COMPLETE saved chain |
| Vi sensors/meta | Yes | Yes | Selected models; discarded HGB candidates absent | Yes | Yes | INFERENCE_ONLY / PARTIAL candidate replay |
| PHM canonical models | Yes,current/recorded revision | Yes | Present; some safe loaders decline | Yes | Yes | PARTIAL; provisional target |
| PHM aggregate fusions | Current source | Yes/source constants | Per-fit states not retained | Aggregate scores only | Source-defined | METRICS_ONLY |


Loading for inference,replaying evaluation,resuming optimization and reproducing from initialization are different capabilities. Selected model states may support inference while lacking optimizer/scheduler/RNG for exact resume. A last recovery slot does not replace the validation-selected best model. Current code bytes are not proof of historical execution: use preserved snapshots and recorded source hashes. Existing dirty worktree provenance is retained.

The audit hashed4,920 binary candidates and safely inspected3,828 on CPU. Declined weights-only Torch loads were not retried with unsafe pickle. Known study-owned small sklearn models were inspected only after receipt-hash verification. Twenty-eight Phase1/100-epoch AdamW states yielded literal betas/epsilon by static pickle-opcode inspection without execution. No checkpoint used GPU memory.

JSON_FITTED_STATE_REFERENCES.csv adds428 run-to-JSON-state references beyond the binary inventory; several can reference the same file. CHECKPOINT_INVENTORY records aliases and available optimizer/scheduler/RNG evidence. Complete training status does not automatically certify independent assessment,exact replay or all-state resume.
