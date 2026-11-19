# MSM Stage 2 multimodal feasibility pilot

**Recommendation: LIMITED GO for a documented laboratory subset.** This task verified **114 examples** under a fixed construction contract: exactly 16 ordered RGB video frames plus 90 unscaled sensor statistics from the same 15 numerical MTConnect channels. There are **13 exclusions out of 127 native pilot intervals**. Separately, **39 examples** support video plus raw high-rate VM20i accelerometer statistics. These sensor contracts overlap and must not be pooled as if they were identical.

This is an input-feasibility result, not evidence that a visual CNN predicts anomalies, that labels are visually recognizable, or that the pilot supplies an independent evaluation split. No model was fitted, no weights were downloaded, and no inference benchmark was used. Audit date: 2026-10-27T01:19:13.325897+01:00.

## Sources, scope, and acquisition

The [official Kaggle dataset](https://www.kaggle.com/datasets/manufuturetoday/multi-sensor-for-metal-milling-anomaly), ID **8392825**, remains pinned to **`manufuturetoday/multi-sensor-for-metal-milling-anomaly/versions/2`**. Stage 1 reports were reviewed before acquisition. The [data descriptor](https://www.nature.com/articles/s41597-026-07255-7) supplies native meanings and sensor acquisition context. Stage 2 measurements below come from actual pilot files, not publication guarantees.

Selected experiments: VM20i datasets **1, 4, 19**, VMX30Ui datasets **8, 9**, and VF10 dataset **1**. Actual labels give abnormal, stable defective-tool, and explicit normal controls. VM20i dataset5 is not a pure-normal control: Stage 1 found 5 abnormal and 4 normal intervals. Original candidates VM20i datasets7/8 each have one abnormal interval while their complete folders are approximately 975/744 MB. The revised sample is more informative per transfer. The acquired summary workbook contains 69 experiment rows and agrees with the 37/19/13 hierarchy; absence of a Remark is not a class label.

All six pilot folders initially contained only verified labels. The Stage 2 wrapper `source/stage2/download_msm.py` uses the verified Stage 1 path/handle validation and the same pinned official single-file API, adding bounded streaming and an exact plan instead of an entire-folder transfer. Every acquisition was previewed. Existing label sizes and hashes were checked and skipped; mismatches would stop rather than overwrite. **35 new source files**, totaling **1,196,411,398 bytes** (1.196 GB), were obtained: 5 MP4s, 11 WAVs, 3 ACC tables, 6 MTC tables, 1 CT table, 5 NC programs, 3 machine XML models, and the summary workbook. The six labels were already local. Three acquisition receipts preserve the original transfer and the two ambient-audio additions. No full dataset archive was requested.

The initial required pilot was 1,131,836,134 bytes. Weak/clipped near-tool audio motivated an additional 64,575,264 bytes of ambient S2 recordings, after size checks and previews. Data stay in `MILLING DATASET/data/raw/msm/versions/2/`, ignored by Git. Stage 1 inputs and outputs remain unchanged. FFmpeg 7.0.2 came from an isolated `imageio-ffmpeg==0.6.0` install in ignored `MILLING DATASET/.tools/`; the active research environment was not modified.

## Verified counts and exclusions

| Experiment | Native intervals | 16-frame timing pass | Common-MTC examples | Excluded | 0 / 1 / 2 | Separate video+ACC |
| --- | --- | --- | --- | --- | --- | --- |
| imi_vm20i/dataset1 | 12 | 8 | 8 | 4 | 0 / 8 / 0 | 8 |
| imi_vm20i/dataset4 | 12 | 12 | 11 | 1 | 0 / 0 / 11 | 12 |
| imi_vm20i/dataset19 | 19 | 19 | 18 | 1 | 18 / 0 / 0 | 19 |
| imi_vmx30ui/dataset8 | 64 | 64 | 64 | 0 | 64 / 0 / 0 | 0 |
| imi_vmx30ui/dataset9 | 14 | 13 | 13 | 1 | 11 / 2 / 0 | 0 |
| tmf_vf10/dataset1 | 6 | 0 | 0 | 6 | 0 / 0 / 0 | 0 |

Primary admitted class counts are **93 label 0**, **10 label 1**, and **11 label 2**. Label 2 remains stable cutting with a defective tool; it was not converted to abnormal cutting. Every sample keeps machine, experiment, original CSV row, native class, native interval, input hash, mapped frame times, and quality gates in `MSM_PILOT_SAMPLE_MANIFEST.csv`.

| Interval ID (native CSV row) | Label | Primary exclusion |
| --- | --- | --- |
| imi_vm20i/dataset1/row6 | 1 | outside_validated_audio_support |
| imi_vm20i/dataset1/row7 | 1 | outside_validated_audio_support |
| imi_vm20i/dataset1/row12 | 1 | outside_validated_audio_support |
| imi_vm20i/dataset1/row13 | 1 | outside_validated_audio_support |
| imi_vm20i/dataset4/row12 | 2 | mtc_time_gap_exceeds_0.5s |
| imi_vm20i/dataset19/row11 | 0 | insufficient_mtc_rows;mtc_time_gap_exceeds_0.5s |
| imi_vmx30ui/dataset9/row2 | 0 | fewer_than_16_distinct_native_frames |
| tmf_vf10/dataset1/row2 | 0 | no_video_provided (also different sensor schema) |
| tmf_vf10/dataset1/row3 | 0 | no_video_provided (also different sensor schema) |
| tmf_vf10/dataset1/row4 | 0 | no_video_provided (also different sensor schema) |
| tmf_vf10/dataset1/row5 | 1 | no_video_provided (also different sensor schema) |
| tmf_vf10/dataset1/row6 | 0 | no_video_provided (also different sensor schema) |
| tmf_vf10/dataset1/row7 | 0 | no_video_provided (also different sensor schema) |

The industrial exclusion is structural: no MP4 is provided. Its controller schema also differs. The two extra laboratory sensor exclusions are VM20i dataset4 row12 (gap within the cut) and dataset19 row11 (no MTC rows during the cut). Both retain continuous ACC data and therefore remain eligible only for the separately specified video+ACC contract. Alignment/frame exclusions are never repaired with repeated frames or arbitrary experiment-wide images.

## Actual video and sound

| Experiment | Video seconds | Frames | FPS | Consecutive identical native frames |
| --- | --- | --- | --- | --- |
| imi_vm20i/dataset1 | 109.633333 | 3289 | 30.0 | 0 |
| imi_vm20i/dataset4 | 94.800000 | 2844 | 30.0 | 0 |
| imi_vm20i/dataset19 | 122.166667 | 3665 | 30.0 | 0 |
| imi_vmx30ui/dataset8 | 237.000000 | 7110 | 30.0 | 69 |
| imi_vmx30ui/dataset9 | 121.600000 | 3648 | 30.0 | 45 |

All five MP4s decode to the declared frame count with strictly increasing 30-fps presentation timestamps. They contain H.264 video and 48-kHz stereo AAC audio, with decoded video and audio origins at zero. Coded images are **720×480 with sample aspect ratio 3:8**: their display is portrait **270×480 (9:16)**. Treating coded pixels as square stretches the scene. Container creation metadata records transcoding, not an acquisition clock. Native consecutive content duplicates exist in both VMX30Ui clips; the selected 16 frames in every admitted sequence have distinct decoded hashes. Regular container timestamps do not prove that no phone frames were dropped before transcoding.

| Reference sound file | Seconds | Sample rate | Channels | Samples at PCM clipping limit |
| --- | --- | --- | --- | --- |
| imi_vm20i/dataset1 / S0 | 111.756000 | 48000 | 1 | 14.2271% |
| imi_vm20i/dataset4 / S0 | 96.640000 | 48000 | 1 | 5.6815% |
| imi_vm20i/dataset19 / S0 | 129.544708 | 48000 | 1 | 0.4085% |
| imi_vmx30ui/dataset8 / S0 | 207.556000 | 48000 | 1 | 1.6507% |
| imi_vmx30ui/dataset9 / S0 | 127.160000 | 48000 | 1 | 0.6590% |
| tmf_vf10/dataset1 / S0 | 1003.429375 | 48000 | 1 | 0.0000% |
| imi_vm20i/dataset1 / S2 | 111.756000 | 48000 | 1 | 0.0482% |
| imi_vm20i/dataset4 / S2 | 96.640000 | 48000 | 1 | 0.0161% |
| imi_vm20i/dataset19 / S2 | 129.544708 | 48000 | 1 | 0.0021% |
| imi_vmx30ui/dataset8 / S2 | 207.556000 | 48000 | 1 | 2.3944% |
| imi_vmx30ui/dataset9 / S2 | 127.160000 | 48000 | 1 | 1.8787% |

All downloaded WAVs are mono, 48 kHz, signed 16-bit PCM. CSV/audio numeric scans found no NaN/infinite samples in the inspected numerical channels. The dataset1 near-tool S0 waveform reaches the PCM clipping limit for approximately 14.23% of the whole recording; ambient S2 is much less clipped. This explains why treating all microphones as interchangeable is unsafe. No audio correction was written into raw files.

## Sensor records, channels, and temporal resolution

| Experiment / modality | Rows | Time range (s) | Median row interval (s) | Largest gap (s) |
| --- | --- | --- | --- | --- |
| imi_vm20i/dataset1 / mtc | 750 | 0.000000–111.706922 | 0.145976000 | 0.229890 |
| imi_vm20i/dataset1 / acc | 5721907 | 0.000019–111.755995 | 0.000019531 | 0.000020 |
| imi_vm20i/dataset4 / mtc | 632 | 0.000000–96.630037 | 0.145459000 | 3.139367 |
| imi_vm20i/dataset4 / acc | 4947968 | 0.000006–96.639986 | 0.000019531 | 0.000020 |
| imi_vm20i/dataset19 / mtc | 839 | 0.000000–129.414364 | 0.146978500 | 3.166111 |
| imi_vm20i/dataset19 / acc | 6632689 | 0.000007–129.544695 | 0.000019531 | 0.000020 |
| imi_vmx30ui/dataset8 / mtc | 1387 | 0.000000–207.400250 | 0.145033000 | 0.502764 |
| imi_vmx30ui/dataset9 / mtc | 839 | 0.000000–127.014505 | 0.147838500 | 0.511759 |
| tmf_vf10/dataset1 / mtc | 2769 | 0.000000–1003.429368 | 0.064786500 | 9.002853 |
| tmf_vf10/dataset1 / ct | 101 | 0.000000–998.377297 | 10.000000000 | 10.000000 |

**VM20i raw branch:** `acc0` (spindle) and `acc1` (base column), measured at 51.2 kHz with continuous ~19.53125 µs steps. The publication specifies mm/s². This pilot scanned 17,302,564 raw accelerometer rows, without extracting or rewriting source tables. Native-cut mean, population standard deviation, RMS, minimum, maximum, and peak-to-peak yield a separate 12-value vector.

**Common laboratory MTC branch:** `watt`, `Spindle_Speed`, `S_Axis_Load`, `Feed_Rate`, `X_Axis_Load`, `Y_Axis_Load`, `Z_Axis_Load`, `smarms`, `xmarms`, `ymarms`, `zmarms`, `smvrms`, `xmvrms`, `ymvrms`, `zmvrms`. Six statistics per channel give a fixed **90-value vector**, stored in `manifests/common_mtc_statistics.csv`. No scaler or feature selector was fitted. The source XML supplies watts, rpm, load percent, acceleration RMS in mm/s², and velocity RMS in mm/s. The VM20i XML inconsistently types `S_Axis_Load` as ROTARY_VELOCITY while giving PERCENT units; it is preserved and flagged, not silently corrected.

MTC row intervals are not independent sensor sampling periods: many vibration/power values are held for roughly 1 s on VM20i and 1.6–3 s on VMX30Ui. The files contain already aggregated vibration features, not raw high-frequency waveforms. A 0.8–1.5 s cut may have several repeated MTC rows but very few fresh measurements. The sensor's internal aggregation window and update latency are not established here. Thus the common-MTC result verifies a coarse table-statistics contract; **39 video+ACC examples provide stronger evidence for true within-cut high-rate statistics**. Do not call MTC row counts raw acceleration samples or claim subsecond physical synchronization for those pre-aggregated features.

Primary sensor quality gates require all 15 channels finite, at least 5 rows per cut, and no coverage gap over 0.5 s, including interval edges. Empty/unavailable asset-event fields occur throughout and are excluded from the numerical branch. Lab controller/NC/program/tool IDs, free-text remarks, class fields, and stop outcomes are not predictor features.

**Industry:** MTC offers `s_load`, `s_speed`, `xpm/xpw`, `ypm/ypw`, `zpm/zpw` plus controller state fields. Its timing is bursty, with gaps up to 9.003 s. CT has only `time,value`, about one value per **10 s**; units are not declared in that CSV. The sole 2.304 s anomalous pilot interval contains **one CT sample**, so it cannot support meaningful within-cut CT variability statistics. No invented high-rate CT stream or interpolation was used.

## Synchronization, visibility, and scientific decision

| Experiment | Reference | Video = sensor + offset (s) | Empirical bound (s) | Calibration / validation anchors | Max validation residual (s) | Supported sensor regions (s) |
| --- | --- | --- | --- | --- | --- | --- |
| imi_vm20i/dataset1 | audio_s2 | -2.315 | ±0.080 | 4 / 6 | 0.035 | 8–48; 56–96 |
| imi_vm20i/dataset4 | audio_s2 | -2.340 | ±0.080 | 5 / 6 | 0.010 | 8–96 |
| imi_vm20i/dataset19 | audio_s2 | -1.570 | ±0.080 | 5 / 6 | 0.010 | 8–96 |
| imi_vmx30ui/dataset8 | audio_s2 | +19.890 | ±0.080 | 12 / 12 | 0.020 | 8–200 |
| imi_vmx30ui/dataset9 | audio_s2 | +49.730 | ±0.100 | 4 / 4 | 0.010 | 0–64 |

See `MSM_VIDEO_ALIGNMENT_REPORT.md` for calibration, held-out checks, the documented partial-overlap correction, empirical uncertainty, and exact 16-frame rules. The false exploratory dataset9 mapping is preserved outside this validated revision and is not used by these manifests. Camera and microphone filenames alone cannot establish offsets.

All accepted sequences were reviewed at all 16 sampled frame positions. Spindle/workpiece/milling context remains recognizable under a documented minimum context criterion. Coolant, droplets, reflections, and the machine window often obscure the actual tool–workpiece interface, especially in dataset4 and VMX30Ui footage. **Clear tool damage or fine contact visibility is not established.** The 80–100 ms bounds are empirical acoustic/clock-consistency allowances, not certified camera hardware timing or annotation-confidence intervals. Fixed phone audio/video muxing is corroborated by container PTS; no externally timed visual fiducial was available.

**LIMITED GO** applies to a filtered laboratory input construction, with either the common low-rate MTC contract or a separately declared VM20i-only ACC contract. A demand for unobscured cutting-edge imagery or fine damage visibility is not met by this pilot. Visual class information, incremental fusion value, causality, and cross-machine robustness remain untested.

The primary pilot has only **two positive-containing experiment groups**. That is insufficient for a three-way experiment-disjoint train/validation/test design with positives in each partition. Stage 1's complete lab set has 25 nominal positive folders, but only five laboratory calendar dates and unresolved shared tool/workpiece dependencies. Audit the remaining recordings and stronger physical groups before selecting folds. No random frame/window split is defensible.

## Audio-plus-sensor alternative

Audio+ACC on VM20i is a scientifically useful separate candidate: high-rate independent instruments share the dataset's sensor zero, and all 43 selected VM20i cutting intervals have source coverage. Prefer an explicitly audited microphone rather than clipped S0 by default. Industry audio+MTC may be explored separately, but CT sparsity and only 7 abnormal intervals in 5 full-dataset groups limit inference. This alternative was **not substituted** for the requested visual architecture; no alternative model was trained.

## Full-experiment requirements — estimates, not authorization

| Potential scope / sensor choice | Total source bytes | Additional after this pilot | Additional GB |
| --- | --- | --- | --- |
| vm20i_only_video_mtc_ambient | 1633874939 | 1586357481 | 1.586 |
| vm20i_only_with_acc | 34286773918 | 33310306668 | 33.310 |
| all_laboratory_video_mtc_ambient | 2640036050 | 2533736741 | 2.534 |
| all_laboratory_with_acc | 35292935029 | 34257685928 | 34.258 |

The minimal scopes above include MP4, ambient S2 audio for timing, MTC, labels, NC, workbook and appropriate XML; ACC is the separately listed option. All source sizes come from the pinned inventory. The maximum unfiltered lab cohort is 2,512 native intervals across 56 folders (1,585 on VM20i alone); industry contributes no visual examples. Actual admission must be measured per recording, not extrapolated from the pilot pass rate.

At 16×3×224×224, one uint8 tensor is 2,408,448 bytes and one float32 tensor is 9,633,792 bytes. Caching every possible lab tensor would use up to **6,050,021,376 bytes** (uint8) or **24,200,085,504 bytes** (float32). Prefer selective decoding or a bounded uint8 cache. The current main environment had roughly 75 GiB available after the pilot, so raw high-rate expansion plus a uint8 cache is plausible; reserve additional derived-output space and recheck storage before any acquisition.

Under the conditional assumption of the observed 30 fps and ±80 ms base timing bound, 15 lab intervals are shorter than the conservative 0.693333 s native-span screen. Their exact 16-frame outcome depends on native frame phase and measured uncertainty. Other recordings may differ. This is a planning screen, not an eligibility claim. No GPU memory/training-time estimate is claimed without a later declared architecture benchmark, which was not authorized here.

## Diagnostic artifacts and handoff

- [imi_vm20i/dataset1/row2](figures/examples/imi_vm20i_dataset1_row2_16frames.png) — 16 frames plus mapped audio, sensor activity, and native label boundaries.
- [imi_vm20i/dataset4/row2](figures/examples/imi_vm20i_dataset4_row2_16frames.png) — 16 frames plus mapped audio, sensor activity, and native label boundaries.
- [imi_vm20i/dataset4/row12](figures/examples/imi_vm20i_dataset4_row12_16frames.png) — 16 frames plus mapped audio, sensor activity, and native label boundaries.
- [imi_vm20i/dataset19/row2](figures/examples/imi_vm20i_dataset19_row2_16frames.png) — 16 frames plus mapped audio, sensor activity, and native label boundaries.
- [imi_vm20i/dataset19/row11](figures/examples/imi_vm20i_dataset19_row11_16frames.png) — 16 frames plus mapped audio, sensor activity, and native label boundaries.
- [imi_vmx30ui/dataset8/row2](figures/examples/imi_vmx30ui_dataset8_row2_16frames.png) — 16 frames plus mapped audio, sensor activity, and native label boundaries.
- [imi_vmx30ui/dataset9/row3](figures/examples/imi_vmx30ui_dataset9_row3_16frames.png) — 16 frames plus mapped audio, sensor activity, and native label boundaries.
- [imi_vmx30ui/dataset9/row12](figures/examples/imi_vmx30ui_dataset9_row12_16frames.png) — 16 frames plus mapped audio, sensor activity, and native label boundaries.

Full recording timelines:

- [imi_vm20i/dataset1](figures/imi_vm20i_dataset1_sensor_label_timeline.png)
- [imi_vm20i/dataset4](figures/imi_vm20i_dataset4_sensor_label_timeline.png)
- [imi_vm20i/dataset19](figures/imi_vm20i_dataset19_sensor_label_timeline.png)
- [imi_vmx30ui/dataset8](figures/imi_vmx30ui_dataset8_sensor_label_timeline.png)
- [imi_vmx30ui/dataset9](figures/imi_vmx30ui_dataset9_sensor_label_timeline.png)
- [tmf_vf10/dataset1](figures/tmf_vf10_dataset1_sensor_label_timeline.png)

All 16-frame review atlases are retained locally under `figures/visibility_atlas/` and ignored as regenerable bulk. Configuration, raw/reused input identities, commands, software versions, output identities, and final checks are recorded alongside these reports. `METHODOLOGY_CORRECTION.md` explains the separately tested synchronization correction.

Exact next action: researcher review of these artifacts and the choice between coarse common-MTC and high-rate VM20i-only sensor statistics. A larger acquisition and final grouping/label protocol require a later instruction. **Stop here; no model training.**
