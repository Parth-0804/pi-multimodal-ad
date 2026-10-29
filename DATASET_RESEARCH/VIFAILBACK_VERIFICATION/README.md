# ViFailback independent verification

**Decision: CONDITIONAL GO for episode-level visual plus measured robot-observation fusion.** ViFailback is a substantially better match to the requested modality contract than a video/audio dataset. Labels and episode joins pass; full-cohort telemetry QC and a second human visual review remain necessary before a full experiment. No model was trained or CNN features extracted.

Native labels independently counted in **109 original author annotation files** and the conversion: **5,202 episodes, 657 successes, 4,545 failures**, 100 canonical task instructions; all 100 have both outcomes. The 109 source directories include variants of nine canonical tasks. All 5,202 complete nested original annotations agree with the conversion.

The matched pilot contains **10 same-task success/failure pairs**, **20 executions**, **320 distinct temporal positions**, and **960 RGB images** across three cameras. All 60 videos and 20 sensor tables passed the pilot checks. The source identity key is separate from the label-free gallery. Two extra QC episodes are not counted as gallery examples.

## Start with the blinded gallery

Open [MATCHED_EXAMPLE_GALLERY/index.html](MATCHED_EXAMPLE_GALLERY/index.html). Each case provides all three full camera sequences, fixed-region enlargements, an interactive synchronized frame slider, sensor plots, frame indices and episode-relative times. Original identities/outcomes are in the separate `UNBLINDING/` key. Save your own observations before opening that key or reading our observability report. A blank human review form is included.

The initial masked-key analyst screen found clear physical failure evidence in **9/10** native failed examples; one drawing-task case remained uncertain. This is an AI-assisted descriptive screen, not independent human validation, a model score, or an estimate of corpus-wide observability.

## Material limitations

- Six pairs of distinct episode IDs share identical three-camera videos and identical published sensor-statistic signatures. Group/deduplicate derived evaluation units; preserve raw files.
- 173 episodes have completely constant position telemetry in published statistics. Two actual tables/videos confirm positions fixed while arms visibly move; bounded original HDF5 reads show the defect is already in the original recordings.
- Only the two gripper effort channels vary in the pilot; twelve arm-joint effort fields are zero. Two gripper velocity fields are zero. Corpus statistics show the same placeholder pattern. This is not wrist force/torque sensing.
- Converted timestamps agree by frame index; original checked HDF5 files have no per-device hardware timestamps. The sub-microsecond index agreement is not a hardware synchronization guarantee.
- Session/operator/date/object-instance identities are unavailable. Use canonical task groups for held-out-task evaluation; do not claim new-robot/session generalization.

The secondary Zenodo dataset is **NO-GO for supervised binary training under its published split**: training and validation contain only successful trials. Two original test annotations with frame intervals were actually retrieved; the complete archive label counts were not independently recounted.

## Reports

- [NATIVE_LABEL_AUDIT.md](NATIVE_LABEL_AUDIT.md)
- [MODALITY_AND_ALIGNMENT_AUDIT.md](MODALITY_AND_ALIGNMENT_AUDIT.md)
- [GROUP_INDEPENDENCE_AUDIT.md](GROUP_INDEPENDENCE_AUDIT.md)
- [VISUAL_OBSERVABILITY_REVIEW.md](VISUAL_OBSERVABILITY_REVIEW.md)
- [SECONDARY_CANDIDATE_AUDIT.md](SECONDARY_CANDIDATE_AUDIT.md)
- [FINAL_RESEARCH_DECISION.md](FINAL_RESEARCH_DECISION.md)
- [RESEARCHER_HANDOFF.md](RESEARCHER_HANDOFF.md)
- [SOURCE_PROVENANCE.json](SOURCE_PROVENANCE.json)

Pinned conversion: `619791b94f61667333fe179d471051e0bca0e06f`. Pinned original: `21df46c2585c52e5a62df5f4b946bae6cbc6fed7`. Source receipts preserve original URLs, paths, byte ranges, sizes and SHA-256 hashes. Reports and code are new files in this directory; existing project datasets/results and active REASSEMBLE jobs were not changed. Excluded datasets were not investigated. No files were staged or committed.
