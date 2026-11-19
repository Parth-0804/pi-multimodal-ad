# MSM input validation

Native verified labels: **2512**. Eligible visual-plus-sensor examples: **1895**. Excluded: **617**; all exclusions retain the original native label.

| machine | native_label | eligible_examples |
| --- | --- | --- |
| imi_vm20i | 0 | 854 |
| imi_vm20i | 1 | 238 |
| imi_vm20i | 2 | 68 |
| imi_vmx30ui | 0 | 580 |
| imi_vmx30ui | 1 | 98 |
| imi_vmx30ui | 2 | 57 |


The following rows partition the excluded native units by their complete combination of failure reasons (no double counting):

| combined_technical_exclusion_reason | native_examples |
| --- | --- |
| outside_validated_audio_support | 434 |
| alignment_rejected:ambiguous_equal_calibration_consensus | 63 |
| alignment_rejected:insufficient_validation_support | 47 |
| mtc_time_gap_exceeds_0.5s | 22 |
| alignment_rejected:insufficient_validation_support;mtc_time_gap_exceeds_0.5s | 11 |
| mtc_time_gap_exceeds_0.5s;outside_validated_audio_support | 9 |
| fewer_than_16_distinct_native_frames | 8 |
| alignment_rejected:insufficient_validation_support;insufficient_mtc_rows | 7 |
| fewer_than_16_distinct_native_frames;insufficient_mtc_rows | 5 |
| insufficient_mtc_rows | 4 |
| insufficient_mtc_rows;mtc_time_gap_exceeds_0.5s | 3 |
| alignment_rejected:ambiguous_equal_calibration_consensus;mtc_time_gap_exceeds_0.5s | 1 |
| alignment_rejected:no_calibration_anchors | 1 |
| alignment_rejected:insufficient_validation_support;insufficient_mtc_rows;mtc_time_gap_exceeds_0.5s | 1 |
| insufficient_mtc_rows;mtc_time_gap_exceeds_0.5s;outside_validated_audio_support | 1 |


The corrected final Stage 2/5 audio calibration is reused, never refitted from labels. Video time = sensor time + offset, only inside accepted acoustic support. VMX9 remains +49.73 s (not the rejected +16.04 alias). Each native half-open cut has exactly 16 ordered unique source frames with content hashes, PTS and uncertainty guards. MTC uses the identical cut, finite 15-channel values, at least five rows and no gap over 0.5 s including edges; no interpolation or ACC substitution.

The allowed channels are `watt, Spindle_Speed, S_Axis_Load, Feed_Rate, X_Axis_Load, Y_Axis_Load, Z_Axis_Load, smarms, xmarms, ymarms, zmarms, smvrms, xmvrms, ymvrms, zmvrms`. Channel-major statistics are mean, population std (ddof 0), RMS, minimum, maximum and peak-to-peak: **90 values** per native example. No label, tool ID, program, direction, folder, robot, task or participant metadata enters the main predictors. Training-only means/standard deviations are fitted separately for every inner and final fit.

One prediction is one native cutting interval or completed trial. It is retrospective classification, not early warning. Technical decoding/alignment is distinct from optical anomaly observability. Native labels, raw data and all prior results remain unchanged.

The machine-readable validation gate and exclusion inventory are under `MSM/02_labels_and_alignment/`.
