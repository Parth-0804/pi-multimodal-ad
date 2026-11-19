# MSM video alignment and 16-frame contract

**Validated revision 2.** Dataset `manufuturetoday/multi-sensor-for-metal-milling-anomaly/versions/2`. 116 of 127 native intervals pass the camera timing/16-frame gate; 114 additionally pass the fixed common-MTC gate. No neural network was used to estimate alignment or assess this contract.

## Time mapping and its evidence

For each clip, use **`video_time = sensor_time + offset`** only within the supported regions below. Label boundaries remain in the native sensor clock, with half-open intervals `[start,end)`.

| Experiment | Reference | Video = sensor + offset (s) | Empirical bound (s) | Calibration / validation anchors | Max validation residual (s) | Supported sensor regions (s) |
| --- | --- | --- | --- | --- | --- | --- |
| imi_vm20i/dataset1 | audio_s2 | -2.315 | ±0.080 | 4 / 6 | 0.035 | 8–48; 56–96 |
| imi_vm20i/dataset4 | audio_s2 | -2.340 | ±0.080 | 5 / 6 | 0.010 | 8–96 |
| imi_vm20i/dataset19 | audio_s2 | -1.570 | ±0.080 | 5 / 6 | 0.010 | 8–96 |
| imi_vmx30ui/dataset8 | audio_s2 | +19.890 | ±0.080 | 12 / 12 | 0.020 | 8–200 |
| imi_vmx30ui/dataset9 | audio_s2 | +49.730 | ±0.100 | 4 / 4 | 0.010 | 0–64 |

Both the WAV and the phone AAC contain the same physical machine sounds. Final fitting uses ambient **S2 for every laboratory clip**. Audio is downsampled to 4 kHz for diagnostics; 800–1800 Hz log-band energy is evaluated using a 256-sample STFT window and 40-sample hop (10 ms features). Even, nonoverlapping 8 s reference blocks are calibration data; odd blocks are held out of coarse fitting and offset estimation.

The corrected coarse estimator searches every possible video position for each calibration block, counts agreeing block matches with Pearson correlation at least 0.75, and breaks equal-count ties using summed correlation strength. It does not demand that most of the complete recordings overlap. A local ±0.5 s search refines each anchor. The offset is the median of calibration anchors consistent within 0.10 s. At least 3 calibration anchors, 3 nonoverlapping validation anchors, and 30 s of anchor span are required. Accepted calibration/validation windows define support; weak regions are not extrapolated into usable examples.

No class label, abnormal/normal distinction, expert remark, or label boundary enters the alignment functions. Only after fixing the mappings are native cutting intervals joined to video. Diagnostic label shading is for review and does not participate in fitting.

The base empirical bound is `max(0.08 s, maximum accepted validation residual + 0.04 s)`. The 0.04 s allowance covers feature resolution and residual acoustic timing, with an 0.08 s floor. Where a separately fitted S0 mapping is accepted, microphone disagreement plus 0.04 s also contributes. Dataset9's S0 and S2 estimates are +49.67 s and +49.73 s, giving a conservative **±0.10 s** bound. These are engineering tolerances, not confidence intervals or a proof of zero systematic phone AV skew. Camera AV and first AAC/video PTS both begin at zero in all five clips. Annotation uncertainty and internal MTC feature-window latency remain separate unknowns.

## Scientific correction: reject the earlier dataset9 alias

An exploratory whole-recording cross-correlation demanded at least 70% overlap. The true dataset9 mapping has approximately 71.87 s of physical overlap with a 121.6 s video, below that arbitrary rule. The rule excluded the true lag and selected a repeated-pattern alias near +16.04 s. A raw waveform check and calibration-only recheck exposed the problem before the final reports.

Revision 2 uses calibration-template consensus and independently withheld blocks. It finds **+49.73 s (S2)**, corroborated by **+49.67 s (S0)**. The other four mappings are unchanged. `test_partial_overlap_does_not_force_a_false_smaller_offset` failed before the correction and passed afterwards. The exploratory files and source preimages are preserved in `MILLING DATASET/runs/20261026T233709740813Z-stage2`. The validated manifests and figures in this directory supersede exploratory counts and sequences. See `METHODOLOGY_CORRECTION.md`; no raw data or native label was corrected.

Filename arithmetic also fails: VM20i dataset19 suggests +75.487 s and VMX30Ui dataset8 suggests +62.777 s if the naming clocks are treated as comparable, whereas measured offsets are -1.57 s and +19.89 s. Container creation times reflect HandBrake transcoding. Neither source can replace acoustic verification.

## Exactly 16 frames per eligible interval

1. Decode every native frame in order and record presentation timestamps; compare decoded counts with the container declaration.
2. Trim a native cut by `uncertainty + half a native frame` at each end. Require that this guarded range lie wholly inside validated timing support.
3. Place 16 equally spaced **bin centers** in that guarded range, map them to the video clock, and choose the nearest native presentation times.
4. Reject duplicate indices, nonmonotonic timestamps, native gaps, insufficient distinct frame content, incomplete video coverage, or any frame whose ±uncertainty range crosses the original label boundary.
5. Decode selected frames forward, hash their original RGB/BGR pixel content, and preserve frame order, native index, actual PTS, mapped sensor time, source row and class in `manifests/selected_frame_manifest.csv`.
6. Correct 3:8 pixel aspect ratio, then prototype aspect-preserving letterboxing to RGB 224×224. The demonstrated tensor is **`[16,3,224,224] uint8`**; this is a data transform, not a trained network. Any later crop/augmentation policy must retain the cutting context.

No frame was borrowed from another interval, repeated to pad a sample, or assigned an experiment-wide label. `MSM_PILOT_SAMPLE_MANIFEST.csv` includes every admitted and excluded native interval. The selected frames cover the interior of cuts; the coverage fraction and timing guard are recorded rather than described as observing every boundary instant.

## Native-video integrity

| Experiment | Video seconds | Frames | FPS | Consecutive identical native frames |
| --- | --- | --- | --- | --- |
| imi_vm20i/dataset1 | 109.633333 | 3289 | 30.0 | 0 |
| imi_vm20i/dataset4 | 94.800000 | 2844 | 30.0 | 0 |
| imi_vm20i/dataset19 | 122.166667 | 3665 | 30.0 | 0 |
| imi_vmx30ui/dataset8 | 237.000000 | 7110 | 30.0 | 69 |
| imi_vmx30ui/dataset9 | 121.600000 | 3648 | 30.0 | 45 |

Every decoded PTS is strictly increasing with approximately 33.333 ms steps, and the decoded count equals the header count. Some VMX30Ui consecutive frames are byte-identical; all admitted 16-frame selections have 16 unique decoded hashes. This checks the delivered compressed videos, not unavailable original smartphone files. No deduplication or raw-file rewrite was performed.

## Visibility and representative diagnostics

All selected frames from all timing-eligible sequences were inspected in atlases. Milling context is recognizable, but coolant and window droplets often hide the exact cutting edge. Visual inspection verifies an intended milling scene, not the anomaly label or a precisely timed optical contact event. There is no externally timed visual fiducial in this pilot. Keep that limitation separate from the strong shared-audio evidence.

- [imi_vm20i/dataset1/row2](figures/examples/imi_vm20i_dataset1_row2_16frames.png) — 16 frames plus mapped audio, sensor activity, and native label boundaries.
- [imi_vm20i/dataset4/row2](figures/examples/imi_vm20i_dataset4_row2_16frames.png) — 16 frames plus mapped audio, sensor activity, and native label boundaries.
- [imi_vm20i/dataset4/row12](figures/examples/imi_vm20i_dataset4_row12_16frames.png) — 16 frames plus mapped audio, sensor activity, and native label boundaries.
- [imi_vm20i/dataset19/row2](figures/examples/imi_vm20i_dataset19_row2_16frames.png) — 16 frames plus mapped audio, sensor activity, and native label boundaries.
- [imi_vm20i/dataset19/row11](figures/examples/imi_vm20i_dataset19_row11_16frames.png) — 16 frames plus mapped audio, sensor activity, and native label boundaries.
- [imi_vmx30ui/dataset8/row2](figures/examples/imi_vmx30ui_dataset8_row2_16frames.png) — 16 frames plus mapped audio, sensor activity, and native label boundaries.
- [imi_vmx30ui/dataset9/row3](figures/examples/imi_vmx30ui_dataset9_row3_16frames.png) — 16 frames plus mapped audio, sensor activity, and native label boundaries.
- [imi_vmx30ui/dataset9/row12](figures/examples/imi_vmx30ui_dataset9_row12_16frames.png) — 16 frames plus mapped audio, sensor activity, and native label boundaries.

The plots show all 16 actual frame positions above reference/phone audio and sensor activity, with native label boundaries and source-row identity. They make visible both useful pairs and the two MTC-gap exclusions. Full-recording sensor/label plots and rejected timing regions provide context. Earlier S2-only exploratory plots are not the source of this validated result.

**Decision:** LIMITED GO for a carefully filtered laboratory construction. Re-audit every additional recording using the corrected calibration method. Preserve physical experiment groups, and obtain researcher review before any larger acquisition, architecture substitution, or training.
