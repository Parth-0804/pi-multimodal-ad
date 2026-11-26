# 02 DATASET AND LABEL VERIFICATION

Run `20261029T004900Z`. Published 2026-10-29T02:15:32.074020+00:00. Pipeline state: **FULL_VIDEO_QC_IN_PROGRESS**. Immutable report snapshot: `VIFAILBACK/10_final_research_reports/report_snapshots/20261029T004900Z/20261029T021531975083Z`.

Pinned converted source `sii-rhos-ai/vifailback-dataset-lerobot` revision `619791b94f61667333fe179d471051e0bca0e06f`. Original source `sii-rhos-ai/ViFailback-Dataset`, revision `21df46c2585c52e5a62df5f4b946bae6cbc6fed7`.

Native5202 episodes:4545 failure,657 no-failure across100 canonical tasks/109 source directories. Independently rejoined all native records, not README labels. Conservative provisional core4384:3755 failure,629 no-failure,99 tasks;818 unique excluded/quarantined. Final eligible count only exists after complete three-camera QC.

Acquisition: {'ACQUIRED_VERIFIED': 13095, 'VERIFIED_EXISTING': 57}. Camera QC: (10549, 10550). Final cohort: pending complete payload QC. Completed fits: {'visual_frozen': 0, 'visual_frozen_high_only': 0, 'visual_finetuned100': 0, 'reassemble_transfer': 0, 'sensor_baselines': 0}.

Exact native verification: `VIFAILBACK/02_dataset_verification/label_audit/20261029T004900Z/INDEPENDENT_NATIVE_RECOUNT.json`. Every original annotation hash and converted metadata identity is recorded there. Video QC includes source SHA/size, full decoding, count, dimensions, PTS, black frames, blur/repetition flags and selected RGB hashes. Semantic uncertainty is separate from technical validity; weak images are retained. Acquisition failures must be inspected/retried rather than silently called corrupt data.
