# Separately reviewable synchronization correction

This revision corrects an exploratory alignment implementation introduced during
Stage 2. It does not alter native labels, raw files, Stage 1 results, or feature
formulas.

The first estimator required overlap of at least 70% of the shorter complete
recording. VMX30Ui dataset9 contains a long video lead-in: the correct S2 mapping
is `video_time = sensor_time + 49.73 s`, leaving approximately 71.87 s of overlap
with a 121.6 s video. The rule rejected that valid overlap and selected a
periodic cutting-pattern alias near +16.04 s. The exploratory 112-example count
and dataset9 frame sequences are superseded.

Calibration-only checks and raw waveform matching exposed the error. The
corrected estimator searches full video positions with nonoverlapping 8-second
reference calibration templates. It maximizes the number of agreeing templates
with Pearson correlation at least 0.75; summed strength breaks ties. It does not
restrict complete-record overlap. Odd reference blocks are withheld from the
coarse search and offset median, then used for timing validation. Native class
labels and annotation boundaries are absent from all alignment inputs.

Both microphone channels support the corrected dataset9 timing: S2 +49.73 s,
S0 +49.67 s. Their 60 ms disagreement contributes to the explicit ±100 ms
empirical engineering guard. The four other video mappings remain unchanged.

`test_partial_overlap_does_not_force_a_false_smaller_offset` uses only a
synthetic recording with a known 49-second offset and insufficient overlap for
the old rule. It failed before the change and passed after it. Evidence:

- Before: `../20261026T233709740813Z-stage2/logs/partial_overlap_regression_before.log`.
- After: `logs/frame_regression_after.log`.
- Source preimages: `../20261026T233709740813Z-stage2/evidence/source_pre_correction/`.
- Corrected implementation: `../../source/stage2/calibration_consensus.py` and
  `../../source/stage2/align_audio.py` relative to the MILLING DATASET root.
- Configuration: `config/alignment_protocol_final.json`.

The final native frame scan admits 116 intervals for timing/16-frame review.
One 0.747-second dataset9 interval cannot supply 16 distinct native frames after
the timing guard, and is excluded without padding. Four dataset1 intervals lack
validated timing support; six industrial intervals have no video. Two further
laboratory intervals fail the common-MTC coverage gate, leaving **114 primary
construction examples**. The separate video+raw-ACC contract admits 39 examples;
these counts overlap and must not be added.

The exploratory run remains preserved. The final reports, CSV, and figures in
this validated revision are authoritative for Stage 2. The empirical acoustic
bounds are not externally certified camera timing or annotation confidence.
