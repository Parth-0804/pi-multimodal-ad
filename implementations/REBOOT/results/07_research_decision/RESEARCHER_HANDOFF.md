# Researcher handoff — REBOOT

**Decision: CONDITIONAL GO for curation/visual review; training gate remains closed.**

The requested feasibility investigation is complete. All source data and earlier REASSEMBLE/MSM/Handover results are preserved. No training, CNN inference or fusion fitting occurred.

## Read/review in this order

- [Blind review gallery](../04_visual_failure_review/galleries/blinded_pilot_v1/index.html): ten neutral IDs, four cameras each, full/context16-frame views, actual motion clips and original numerical-state plots. Do not open the key first.
- [Blank human review sheet](../04_visual_failure_review/RESEARCHER_VISUAL_REVIEW_SHEET.csv):40 view/example rows; human review has not been filled by Codex.
- [Unblinding key after review](../04_visual_failure_review/UNBLINDED_LABEL_KEY.html) and [native annotation audit](../02_labels_and_annotations/NATIVE_PHASE_RECORD_AUDIT.csv).
- [Full research decision](REBOOT_RESEARCH_DECISION.md), [alignment findings](../03_video_sensor_alignment/VIDEO_SENSOR_ALIGNMENT_REPORT.md), [architecture changes](../05_architecture_compatibility/REASSEMBLE_ARCHITECTURE_COMPATIBILITY.md) and [evaluation gate](../06_evaluation_feasibility/EVALUATION_FEASIBILITY.md).

Real right-wrist imagery includes a promising physical drop, unlike a purely force-only hypothetical failure. That observation is preliminary and does not certify the annotation onset or every phase. Low/left-wrist views can be unhelpful; fine alignment remains uncertain. The native phase source has defects/semantic ambiguities, no verified phase-negative labels are available, and all sample video chunks duplicate the full cylinder-recovery repository. It would be invalid to assign all recovery frames positive labels or split sample/full copies apart.

The pilot therefore contains **10 diagnostic demonstrations, not20 verified normal/failure pairs**. Three-outer/two-inner group support is not established. Available sample operator/session metadata do not cover all collections. Numerical features are joint/gripper positions; force/torque is not present. Nominal clocks match, but hardware exposure synchronization is unverified.

Review the visible evidence, obtain authoritative label/group clarifications, then create a separately versioned corrected/admitted cohort before any approved modeling. All proposed models, gates and alternatives are documented; no synthetic labels, hidden positive claims, source rewrites or full dataset download were used.

## Published metadata limitation

The episode-index Parquet for `REBOOT26/usbc_recovery_install` at `0ef0b37f0601fbafcc3bab07195a1fb5e756c6b4` cannot be parsed: its196,608 published bytes lack the required Parquet footer. The local file exactly matches the official LFS size and SHA256 (`c2edd7790273c14ba3ff63d7dbb1d0368d8ca3086503e66277c0edd3de2af160`), and a second HTTP206 request confirms the same final8 bytes. It is a published-file limitation, not an unverified local truncation; the bytes remain unchanged. Episode indices and frame-length totals match native `info.json` for the other37 repositories (2,103 entries). The USB-C recovery-install collection's33 episodes/29,633 frames remain **info-declared, not independently index-verified**. None of the ten selected pilot demonstrations uses this file. Evidence: `runs/20261028T113139848361Z-independent-feasibility-v1/evidence/USBC_METADATA_SOURCE_IDENTITY_RECHECK.json` and the run's `manifests/REPOSITORY_METADATA_VALIDATION.json`.
