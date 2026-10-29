# Researcher handoff — independent review

**Decision to review: CONDITIONAL GO for ViFailback whole-execution visual + measured robot-observation fusion.** No audio substitution. Excluded datasets were not accessed for this investigation. The secondary Zenodo release does not support supervised binary training under its published partition.

Before reading the native key or our observations, open [the blinded gallery](MATCHED_EXAMPLE_GALLERY/index.html) and complete `MATCHED_EXAMPLE_GALLERY/HUMAN_REVIEW_FORM.csv`. It contains twenty deidentified executions, all three cameras, sixteen uniform positions per camera, full views, fixed-region enlargements, timestamps and sensor plots. Then inspect `UNBLINDING/index.html` for original episode identities and native labels. The AI-assisted masked-key screen found clear physical evidence in 9/10 failed cases; B02 remains uncertain. This is not human validation or model evidence.

## What was independently checked

- All 5,202 native annotation records: original yes/no counts 4,545/657, complete nested object equality, unique joins, listed modalities, task mapping and valid normalized keyframes.
- All 100 canonical tasks have both outcomes; 109 source directory variants mapped explicitly.
- Actual 20-episode/60-video pilot: 5,255 measured rows, finite observation arrays, exact IDs/indices/flag joins and 960 distinct selected images; converted selected timestamp disagreement below 0.92 microseconds.
- Two original HDF5 files: exact qpos/qvel/effort matches; eighteen original/converted camera-frame comparisons. The absence of original hardware timestamps was explicitly checked in those files.
- Six exact duplicate episode components through video hashes and matching sensor-statistic fingerprints; repeated identities must remain grouped.
- Two extra QC tables/videos: frozen positions despite moving robot; bounded original HDF5 reads confirm the upstream defect. 173 cases flagged by published stats require quarantine/review, not invented repairs.
- Secondary: two actual test annotation records with textual Outcomes and frame-index Anomalies; published normal-only training/validation split inspected. Full secondary class recount and modality audit were not performed.

## Decisions still required before implementation

1. Confirm episode-level outcome as the target; sparse avoid/correct frames are not temporal ground truth.
2. Review twenty cases independently for visible failure, uncertain tasks and object/condition matching. Preserve B02 and all exclusions in the audit trail.
3. Freeze telemetry QC: quarantine 173 flags, deterministic duplicate treatment, structural-zero mask and any further full-input integrity checks. The proposed remaining 5,023 examples are not certified valid payloads.
4. Confirm that 14 positions, 12 velocities and 2 gripper effort observations meet the scientific goal; calibrated joint torque/wrist F/T is not available here.
5. Freeze canonical-task grouping, nested folds, camera policy, preprocessing, classifier/fusion selection rules, budgets, seeds, uncertainty estimates and intervention/planning strata before any outer-test evaluation.
6. Keep frame/crop selection label-blind and identical across both outcomes and all model comparisons. No annotation-guided positive-only improvement.
7. Independently acknowledge unquantified camera/robot hardware latency and missing session/operator/object-instance IDs. Do not call converted index agreement a hardware timing calibration.

## Artifact map and provenance

Reports: README.md, NATIVE_LABEL_AUDIT.md, MODALITY_AND_ALIGNMENT_AUDIT.md, GROUP_INDEPENDENCE_AUDIT.md, VISUAL_OBSERVABILITY_REVIEW.md, SECONDARY_CANDIDATE_AUDIT.md, FINAL_RESEARCH_DECISION.md and this handoff.

Source revisions: conversion `619791b94f61667333fe179d471051e0bca0e06f`, original `21df46c2585c52e5a62df5f4b946bae6cbc6fed7`, secondary Zenodo DOI 10.5281/zenodo.4578539 v1. Individual source URLs, original filenames, byte-range responses, publisher identities, sizes and SHA-256 hashes are in SOURCE_PROVENANCE.json and source receipts. Archive-prefix samples are partial, not complete-archive integrity verification. Actual sample exclusions and all 100-task counts are in `checks/`; gallery/native label key is separate from the label-free pages.

Core source checks can be recomputed from preserved inputs using the code in `code/`: `audit_labels.py`, `screen_groups_and_quality.py`, `verify_original_samples.py`, `inspect_secondary.py`, and `validate_delivery.py`. Acquisition scripts are bounded and reuse verified existing files; no source payload should be overwritten. The frozen initial blind screen is intentionally not rerun or rewritten. A fresh whole-dataset acquisition reproduction was not attempted.

All work is new under this folder. Existing raw data, historical reports, trained weights and active REASSEMBLE processes were not modified. No models were trained, no CNN embeddings extracted and no GPU tests run. No files were staged/committed. Stop for the requested four-eye review before full data acquisition or training.
