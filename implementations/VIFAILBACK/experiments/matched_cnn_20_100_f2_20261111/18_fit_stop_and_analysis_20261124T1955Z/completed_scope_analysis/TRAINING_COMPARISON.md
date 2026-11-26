# REASSEMBLE and VIFAILBACK training coverage

The approximately 47-day VIFAILBACK constraint is an INFERRED additional-runtime planning allowance, not measured elapsed time.

|Dataset / study|Training completed|Limited or unexecuted scope|
|---|---|---|
|REASSEMBLE core|Frozen CNN feature/head, statistical sensor and PatchTST baselines; fusion and controlled robustness studies closed|Audio and physical-object modelling excluded by feasibility gates; retained extension Task1 discontinued|
|REASSEMBLE later full CNN|25 full-CNN fits ×20 epochs, seed42, five outer folds and their inner fits; separate frozen/full100-epoch comparison|50 fits deferred under the researcher-approved25-fit cap; complete three-seed full-CNN stability not established|
|VIFAILBACK frozen/donor20|36 FROZEN20 and 36 DONOR20 fits; frozen donor CNN plus newly fitted target heads; existing sensor fits reused|These completed arms do not establish benefit from target-domain CNN fine-tuning|
|VIFAILBACK 100-epoch pilot|One FROZEN100, one FULL100 and one DONOR100 fit, seed42, predefined fold0 pilot|Single-split/single-seed exploratory evidence; frozen/donor CNNs are not target-domain CNN fine-tuning|
|VIFAILBACK FULL20|4 completed fits, seed42 outer0 roles|Remaining 32 fits not run after current completion; full three-fold/three-seed FULL20 comparison and full fusion coverage unachieved. Constraint: approximately 47 additional GPU days on the current T4.|

REASSEMBLE entries are REPORTED by the retained dated closure/stop records, not a new reproduction or checkpoint audit. VIFAILBACK counts are VERIFIED within the inspected saved completion-record scope. Sources: REASSEMBLE core closure in implementations/REASSEMBLE/results/artifacts/reports/REASSEMBLE_COMPLETION_STATUS.md; 25-fit stop receipt in 26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_c_only_20epoch_revision_01/02112026_stop_after25fits_01/STOP_AFTER_25_COMPLETE.json; separate 100-epoch report in implementations/REASSEMBLE/experiments/cnn_seed_stability/backbone_comparison/reports/PHASE1_100EPOCH_COMPARISON_REPORT.md; VIFAILBACK FIT_COVERAGE.json, per-fit histories/receipts and CURRENT_RESULTS.json. Earlier review validation statements remain attributed to those records.
