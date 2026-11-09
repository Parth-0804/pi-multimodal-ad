# 100-epoch frozen versus full-CNN follow-up

This is the authorized temporary detour from the C-only 20-epoch study. It selects completed original fit 3, seed 42, by validation AP (0.287719), then trains two fresh models for 100 epochs each on its fixed training/validation/calibration groups. Both assess the same separately excluded outer recordings. This is a post-selected, single-split visual comparison; the broader 75-fit study continues afterward.

- [Frozen protocol](26102026_reports/PHASE1_100EPOCH_PROTOCOL.md)
- [Progress and eventual results](26102026_reports/PHASE1_100EPOCH_COMPARISON_REPORT.md)
- [GPU audit and timing evidence](26102026_reports/PHASE1_GPU_OPTIMIZATION_REPORT.md)
- [Live controller status](26102026_execution/PHASE1_COMPARISON_STATUS.json)
- [Pause checkpoint proof](26102026_evidence/PHASE1_PAUSE_COMPLETE.json)
- [Automatic original-study resumption receipt](26102026_execution/PHASE1_MAIN_STUDY_RESUMPTION_RECEIPT.json)

The original fit 4 pauses after its next completed epoch. Its full recovery checkpoint is copied and verified before this comparison starts. On comparison success the unchanged original controller resumes that checkpoint, retaining its 20-epoch cap, cosine-50 schedule prefix, three seeds and all folds. New 100-epoch checkpoints never replace the original ones. Stop/integrity failures remain visible and block unsafe continuation.

Expected detour duration: approximately 26–36 hours on the one allocated T4, subject to measured throughput and availability. There is no need to keep the chat open. The detached process survives this interaction; a machine reboot requires relaunching the recorded command. Commands, exact package versions, source/input hashes and checkpoint hashes are recorded in provenance and execution receipts.
