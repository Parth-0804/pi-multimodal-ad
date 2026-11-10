# Independent dataset selection — labels first, 2026-10-28

This is a source-level feasibility audit for Parth's REASSEMBLE-derived fusion study. Final active candidates: **RoboFAC and FAILURE**. The researcher withdrew CRIA during the audit. Previously acquired CRIA files are retained unchanged and excluded from the decision; no further CRIA inspection, acquisition or visual review was undertaken after that instruction. No CRIA report is produced.

**Recommended next step: a blinded FAILURE RGB-plus-audio visual pilot.** This is permission to propose a pilot, not evidence that fusion improves performance or approval to implement/train an audio architecture. If measured robot proprioception or force/torque is mandatory, neither remaining candidate currently passes.

| Candidate | Verified native counts | Same-example numerical data | Visual evidence | Verdict |
| --- | --- | --- | --- | --- |
| RoboFAC — real | 480 failed / 122 successful actions; 1,204 camera videos | None listed for these actions | Actual grasp failure/success pair inspected | NO-GO for current real-world fusion objective |
| RoboFAC — simulation | 9,890 false / 4,729 true success flags in 14,619 metadata rows; not a clean cohort | HDF5 actions and privileged simulated states; two files checked | One linked simulated video inspected | NO-GO now; label/identity resolution needed |
| FAILURE | 147 failed / 82 successful joined recordings; 252 annotation rows overall | Audio; RGB/depth/timestamps joined by action and recording ID | Official pour demonstrations inspected; corpus review pending | GO FOR VISUAL PILOT for RGB+audio; full study conditional |

Read [DATASET_COMPARISON.md](DATASET_COMPARISON.md), [ROBOFAC_LABEL_AUDIT.md](ROBOFAC_LABEL_AUDIT.md), [FAILURE_LABEL_AUDIT.md](FAILURE_LABEL_AUDIT.md), [GROUP_INDEPENDENCE_SCREENING.md](GROUP_INDEPENDENCE_SCREENING.md), [VISUAL_FEASIBILITY_SCREENING.md](VISUAL_FEASIBILITY_SCREENING.md), [FINAL_DATASET_RECOMMENDATION.md](FINAL_DATASET_RECOMMENDATION.md) and [RESEARCHER_HANDOFF.md](RESEARCHER_HANDOFF.md).

Original sources and HTTP range evidence are preserved in `source_evidence/` with individual SHA-256 receipts. Recounted tables and exceptions are in `checks/`. Inspect [NATIVE_LABEL_EXAMPLES.csv](NATIVE_LABEL_EXAMPLES.csv) and [SOURCE_PROVENANCE.json](SOURCE_PROVENANCE.json). Source-frame contact sheets are in `visual_screening/`; these are an unblinded source screen, not a blinded validation experiment.

No complete dataset or pilot was downloaded. No neural network, CNN feature extraction, training, or GPU experiment was run. Existing MSM, Handover, REBOOT, REASSEMBLE and historical pilot evidence were not changed. No files were staged or committed.
