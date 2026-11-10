# REBOOT independent multimodal feasibility investigation

**CONDITIONAL GO for further curation and independent visual review. Training remains blocked.**

- [Research decision](07_research_decision/REBOOT_RESEARCH_DECISION.md)
- [Researcher handoff](07_research_decision/RESEARCHER_HANDOFF.md)
- [Blinded four-view gallery](04_visual_failure_review/galleries/blinded_pilot_v1/index.html)
- [Human review sheet](04_visual_failure_review/RESEARCHER_VISUAL_REVIEW_SHEET.csv)
- [Source/release audit](00_dataset_overview/REBOOT_SOURCE_AUDIT.md)
- [Label contract and limitations](02_labels_and_annotations/ANNOTATION_CONTRACT_AND_LIMITATIONS.md)
- [Video/state alignment](03_video_sensor_alignment/VIDEO_SENSOR_ALIGNMENT_REPORT.md)
- [Architecture compatibility](05_architecture_compatibility/REASSEMBLE_ARCHITECTURE_COMPATIBILITY.md)
- [Evaluation feasibility](06_evaluation_feasibility/EVALUATION_FEASIBILITY.md)
- [Shared dataset workspace](../DATASET_RESEARCH/README.md)

Metadata for38 pinned repositories and a bounded ten-demonstration diagnostic pilot were audited. Only one phase-annotation source was found; it needs clarification and contains defects.16 original camera files were downloaded and hash checked,640 frames decoded, and14-position feedback separated from commands. No force/torque was invented. No binary targets, training splits or model scores were fabricated.

Folder conventions follow the previous MSM/Handover work: numbered research stages, immutable versioned inputs under01, source and tests, a unique run with configuration/evidence/manifests/reports/logs and a final decision/handoff. Exact source commits/hashes, download manifests, range-projection limits and human-review status are retained. All earlier dataset folders remain canonical in place; DATASET_RESEARCH supplies relative links rather than moving historical work.

The final metadata audit confirms37 parseable episode indexes and flags one pinned USB-C recovery-install index whose published bytes lack a Parquet footer. Its source hashes match; its33 entries remain info-declared. See the source audit and handoff for the exact identity.
