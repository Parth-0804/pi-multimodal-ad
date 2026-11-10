#!/usr/bin/env python3
"""Render the Stage 2 feasibility reports from the validated artifact revision."""
import argparse
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd


def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join('---' for _ in headers)+' |']+
                     ['| '+' | '.join(map(str,row))+' |' for row in rows])


def write(path,text):
    with path.open('x') as f:f.write(text.rstrip()+'\n')


def main(run):
    cfg=json.loads((run/'config/resolved_config.json').read_text());summary=json.loads((run/'manifests/pilot_summary.json').read_text())
    sensor=json.loads((run/'manifests/sensor_audit.json').read_text());alignment=json.loads((run/'manifests/video_alignment_final.json').read_text())
    media=json.loads((run/'manifests/media_probe.json').read_text());native=json.loads((run/'manifests/native_video_audit.json').read_text())
    audio=json.loads((run/'manifests/additional_audio_audit.json').read_text());requirements=json.loads((run/'manifests/full_experiment_requirements.json').read_text())
    examples=json.loads((run/'manifests/diagnostic_examples.json').read_text());pilot=pd.read_csv(run/'MSM_PILOT_SAMPLE_MANIFEST.csv')
    acquired=Path(cfg['acquisition_run']);stamp=datetime.now(ZoneInfo('Europe/Berlin')).isoformat()
    count_table=table(['Experiment','Native intervals','16-frame timing pass','Common-MTC examples','Excluded','0 / 1 / 2','Separate video+ACC'],
                     [[g,v['native_intervals'],v['frame_contract_pass'],v['verified_multimodal_examples'],v['excluded'],
                       ' / '.join(str(v['class_counts'].get(str(k),0)) for k in (0,1,2)),v['separate_video_acc_examples']] for g,v in summary['by_group'].items()])
    sensor_table=table(['Experiment / modality','Rows','Time range (s)','Median row interval (s)','Largest gap (s)'],
                       [[g+' / '+m,v['rows'],f"{v['time_start_s']:.6f}–{v['time_end_s']:.6f}",f"{v['median_dt_s']:.9f}",f"{v['max_gap_s']:.6f}"]
                        for g,mods in sensor.items() for m,v in mods.items() if m in ('acc','mtc','ct') and v.get('available')])
    video_table=table(['Experiment','Video seconds','Frames','FPS','Consecutive identical native frames'],
                      [[g,f"{m['video_duration_s']:.6f}",native[g]['decoded_frames'],m['fps'],native[g]['consecutive_identical_decoded_frames']]
                       for g,m in media.items() if m.get('video')])
    audio_rows=[]
    for g,mods in sensor.items():
        for a in mods['audio']:
            if a['path'].endswith('_s0.wav'):audio_rows.append([g+' / S0',f"{a['duration_s']:.6f}",a['sample_rate'],a['channels'],f"{100*a['clipped_sample_fraction']:.4f}%"])
    for a in audio:audio_rows.append([a['group_id']+' / S2',f"{a['duration_s']:.6f}",a['sample_rate'],a['channels'],f"{100*a['clipped_sample_fraction']:.4f}%"])
    audio_table=table(['Reference sound file','Seconds','Sample rate','Channels','Samples at PCM clipping limit'],audio_rows)
    timing_table=table(['Experiment','Reference','Video = sensor + offset (s)','Empirical bound (s)','Calibration / validation anchors','Max validation residual (s)','Supported sensor regions (s)'],
                       [[g,m['reference'],f"{m['offset_s']:+.3f}",f"±{m['uncertainty_s']:.3f}",f"{m['calibration_anchors']} / {m['validation_anchors']}",
                         f"{m['max_validation_residual_s']:.3f}",'; '.join(f"{a:g}–{b:g}" for a,b in m['support_sensor_s'])]
                        for g,m in alignment.items() if m.get('accepted')])
    excluded=pilot[~pilot.verified_multimodal_example]
    exclusion_table=table(['Interval ID (native CSV row)','Label','Primary exclusion'],
                          [[r.interval_id,r.native_label,'no_video_provided (also different sensor schema)' if 'no_video' in r.primary_exclusion_reasons else r.primary_exclusion_reasons]
                           for _,r in excluded.iterrows()])
    requirement_table=table(['Potential scope / sensor choice','Total source bytes','Additional after this pilot','Additional GB'],
                           [[k,v['total_source_bytes'],v['additional_bytes_after_pilot'],f"{v['additional_bytes_after_pilot']/1e9:.3f}"]
                            for k,v in requirements.items() if k!='cohort_upper_bounds'])
    examples_list='\n'.join(f"- [{e['interval_id']}]({e['figure']}) — 16 frames plus mapped audio, sensor activity, and native label boundaries." for e in examples)
    timelines='\n'.join(f"- [{g}](figures/{g.replace('/','_')}_sensor_label_timeline.png)" for g in cfg['selected_groups'])
    total=sum(int(x['bytes']) for name in ('resolved_config.json','audio_alignment_addon.json','audio_alignment_validation_addon.json')
              for x in json.loads((acquired/'config'/name).read_text())['download_plan'] if x['acquisition_status']!='already_acquired')
    write(run/'MSM_STAGE2_MODALITY_AUDIT.md',f"""# MSM Stage 2 multimodal feasibility pilot

**Recommendation: LIMITED GO for a documented laboratory subset.** This task verified **{summary['verified_multimodal_examples']} examples** under a fixed construction contract: exactly 16 ordered RGB video frames plus 90 unscaled sensor statistics from the same 15 numerical MTConnect channels. There are **{summary['excluded_primary_examples']} exclusions out of 127 native pilot intervals**. Separately, **39 examples** support video plus raw high-rate VM20i accelerometer statistics. These sensor contracts overlap and must not be pooled as if they were identical.

This is an input-feasibility result, not evidence that a visual CNN predicts anomalies, that labels are visually recognizable, or that the pilot supplies an independent evaluation split. No model was fitted, no weights were downloaded, and no inference benchmark was used. Audit date: {stamp}.

## Sources, scope, and acquisition

The [official Kaggle dataset](https://www.kaggle.com/datasets/manufuturetoday/multi-sensor-for-metal-milling-anomaly), ID **8392825**, remains pinned to **`{cfg['handle']}`**. Stage 1 reports were reviewed before acquisition. The [data descriptor](https://www.nature.com/articles/s41597-026-07255-7) supplies native meanings and sensor acquisition context. Stage 2 measurements below come from actual pilot files, not publication guarantees.

Selected experiments: VM20i datasets **1, 4, 19**, VMX30Ui datasets **8, 9**, and VF10 dataset **1**. Actual labels give abnormal, stable defective-tool, and explicit normal controls. VM20i dataset5 is not a pure-normal control: Stage 1 found 5 abnormal and 4 normal intervals. Original candidates VM20i datasets7/8 each have one abnormal interval while their complete folders are approximately 975/744 MB. The revised sample is more informative per transfer. The acquired summary workbook contains 69 experiment rows and agrees with the 37/19/13 hierarchy; absence of a Remark is not a class label.

All six pilot folders initially contained only verified labels. The Stage 2 wrapper `source/stage2/download_msm.py` uses the verified Stage 1 path/handle validation and the same pinned official single-file API, adding bounded streaming and an exact plan instead of an entire-folder transfer. Every acquisition was previewed. Existing label sizes and hashes were checked and skipped; mismatches would stop rather than overwrite. **35 new source files**, totaling **{total:,} bytes** ({total/1e9:.3f} GB), were obtained: 5 MP4s, 11 WAVs, 3 ACC tables, 6 MTC tables, 1 CT table, 5 NC programs, 3 machine XML models, and the summary workbook. The six labels were already local. Three acquisition receipts preserve the original transfer and the two ambient-audio additions. No full dataset archive was requested.

The initial required pilot was 1,131,836,134 bytes. Weak/clipped near-tool audio motivated an additional 64,575,264 bytes of ambient S2 recordings, after size checks and previews. Data stay in `MILLING DATASET/data/raw/msm/versions/2/`, ignored by Git. Stage 1 inputs and outputs remain unchanged. FFmpeg 7.0.2 came from an isolated `imageio-ffmpeg==0.6.0` install in ignored `MILLING DATASET/.tools/`; the active research environment was not modified.

## Verified counts and exclusions

{count_table}

Primary admitted class counts are **{summary['primary_class_counts'].get('0',0)} label 0**, **{summary['primary_class_counts'].get('1',0)} label 1**, and **{summary['primary_class_counts'].get('2',0)} label 2**. Label 2 remains stable cutting with a defective tool; it was not converted to abnormal cutting. Every sample keeps machine, experiment, original CSV row, native class, native interval, input hash, mapped frame times, and quality gates in `MSM_PILOT_SAMPLE_MANIFEST.csv`.

{exclusion_table}

The industrial exclusion is structural: no MP4 is provided. Its controller schema also differs. The two extra laboratory sensor exclusions are VM20i dataset4 row12 (gap within the cut) and dataset19 row11 (no MTC rows during the cut). Both retain continuous ACC data and therefore remain eligible only for the separately specified video+ACC contract. Alignment/frame exclusions are never repaired with repeated frames or arbitrary experiment-wide images.

## Actual video and sound

{video_table}

All five MP4s decode to the declared frame count with strictly increasing 30-fps presentation timestamps. They contain H.264 video and 48-kHz stereo AAC audio, with decoded video and audio origins at zero. Coded images are **720×480 with sample aspect ratio 3:8**: their display is portrait **270×480 (9:16)**. Treating coded pixels as square stretches the scene. Container creation metadata records transcoding, not an acquisition clock. Native consecutive content duplicates exist in both VMX30Ui clips; the selected 16 frames in every admitted sequence have distinct decoded hashes. Regular container timestamps do not prove that no phone frames were dropped before transcoding.

{audio_table}

All downloaded WAVs are mono, 48 kHz, signed 16-bit PCM. CSV/audio numeric scans found no NaN/infinite samples in the inspected numerical channels. The dataset1 near-tool S0 waveform reaches the PCM clipping limit for approximately 14.23% of the whole recording; ambient S2 is much less clipped. This explains why treating all microphones as interchangeable is unsafe. No audio correction was written into raw files.

## Sensor records, channels, and temporal resolution

{sensor_table}

**VM20i raw branch:** `acc0` (spindle) and `acc1` (base column), measured at 51.2 kHz with continuous ~19.53125 µs steps. The publication specifies mm/s². This pilot scanned 17,302,564 raw accelerometer rows, without extracting or rewriting source tables. Native-cut mean, population standard deviation, RMS, minimum, maximum, and peak-to-peak yield a separate 12-value vector.

**Common laboratory MTC branch:** `watt`, `Spindle_Speed`, `S_Axis_Load`, `Feed_Rate`, `X_Axis_Load`, `Y_Axis_Load`, `Z_Axis_Load`, `smarms`, `xmarms`, `ymarms`, `zmarms`, `smvrms`, `xmvrms`, `ymvrms`, `zmvrms`. Six statistics per channel give a fixed **90-value vector**, stored in `manifests/common_mtc_statistics.csv`. No scaler or feature selector was fitted. The source XML supplies watts, rpm, load percent, acceleration RMS in mm/s², and velocity RMS in mm/s. The VM20i XML inconsistently types `S_Axis_Load` as ROTARY_VELOCITY while giving PERCENT units; it is preserved and flagged, not silently corrected.

MTC row intervals are not independent sensor sampling periods: many vibration/power values are held for roughly 1 s on VM20i and 1.6–3 s on VMX30Ui. The files contain already aggregated vibration features, not raw high-frequency waveforms. A 0.8–1.5 s cut may have several repeated MTC rows but very few fresh measurements. The sensor's internal aggregation window and update latency are not established here. Thus the common-MTC result verifies a coarse table-statistics contract; **39 video+ACC examples provide stronger evidence for true within-cut high-rate statistics**. Do not call MTC row counts raw acceleration samples or claim subsecond physical synchronization for those pre-aggregated features.

Primary sensor quality gates require all 15 channels finite, at least 5 rows per cut, and no coverage gap over 0.5 s, including interval edges. Empty/unavailable asset-event fields occur throughout and are excluded from the numerical branch. Lab controller/NC/program/tool IDs, free-text remarks, class fields, and stop outcomes are not predictor features.

**Industry:** MTC offers `s_load`, `s_speed`, `xpm/xpw`, `ypm/ypw`, `zpm/zpw` plus controller state fields. Its timing is bursty, with gaps up to 9.003 s. CT has only `time,value`, about one value per **10 s**; units are not declared in that CSV. The sole 2.304 s anomalous pilot interval contains **one CT sample**, so it cannot support meaningful within-cut CT variability statistics. No invented high-rate CT stream or interpolation was used.

## Synchronization, visibility, and scientific decision

{timing_table}

See `MSM_VIDEO_ALIGNMENT_REPORT.md` for calibration, held-out checks, the documented partial-overlap correction, empirical uncertainty, and exact 16-frame rules. The false exploratory dataset9 mapping is preserved outside this validated revision and is not used by these manifests. Camera and microphone filenames alone cannot establish offsets.

All accepted sequences were reviewed at all 16 sampled frame positions. Spindle/workpiece/milling context remains recognizable under a documented minimum context criterion. Coolant, droplets, reflections, and the machine window often obscure the actual tool–workpiece interface, especially in dataset4 and VMX30Ui footage. **Clear tool damage or fine contact visibility is not established.** The 80–100 ms bounds are empirical acoustic/clock-consistency allowances, not certified camera hardware timing or annotation-confidence intervals. Fixed phone audio/video muxing is corroborated by container PTS; no externally timed visual fiducial was available.

**LIMITED GO** applies to a filtered laboratory input construction, with either the common low-rate MTC contract or a separately declared VM20i-only ACC contract. A demand for unobscured cutting-edge imagery or fine damage visibility is not met by this pilot. Visual class information, incremental fusion value, causality, and cross-machine robustness remain untested.

The primary pilot has only **two positive-containing experiment groups**. That is insufficient for a three-way experiment-disjoint train/validation/test design with positives in each partition. Stage 1's complete lab set has 25 nominal positive folders, but only five laboratory calendar dates and unresolved shared tool/workpiece dependencies. Audit the remaining recordings and stronger physical groups before selecting folds. No random frame/window split is defensible.

## Audio-plus-sensor alternative

Audio+ACC on VM20i is a scientifically useful separate candidate: high-rate independent instruments share the dataset's sensor zero, and all 43 selected VM20i cutting intervals have source coverage. Prefer an explicitly audited microphone rather than clipped S0 by default. Industry audio+MTC may be explored separately, but CT sparsity and only 7 abnormal intervals in 5 full-dataset groups limit inference. This alternative was **not substituted** for the requested visual architecture; no alternative model was trained.

## Full-experiment requirements — estimates, not authorization

{requirement_table}

The minimal scopes above include MP4, ambient S2 audio for timing, MTC, labels, NC, workbook and appropriate XML; ACC is the separately listed option. All source sizes come from the pinned inventory. The maximum unfiltered lab cohort is 2,512 native intervals across 56 folders (1,585 on VM20i alone); industry contributes no visual examples. Actual admission must be measured per recording, not extrapolated from the pilot pass rate.

At 16×3×224×224, one uint8 tensor is 2,408,448 bytes and one float32 tensor is 9,633,792 bytes. Caching every possible lab tensor would use up to **6,050,021,376 bytes** (uint8) or **24,200,085,504 bytes** (float32). Prefer selective decoding or a bounded uint8 cache. The current main environment had roughly 75 GiB available after the pilot, so raw high-rate expansion plus a uint8 cache is plausible; reserve additional derived-output space and recheck storage before any acquisition.

Under the conditional assumption of the observed 30 fps and ±80 ms base timing bound, 15 lab intervals are shorter than the conservative 0.693333 s native-span screen. Their exact 16-frame outcome depends on native frame phase and measured uncertainty. Other recordings may differ. This is a planning screen, not an eligibility claim. No GPU memory/training-time estimate is claimed without a later declared architecture benchmark, which was not authorized here.

## Diagnostic artifacts and handoff

{examples_list}

Full recording timelines:

{timelines}

All 16-frame review atlases are retained locally under `figures/visibility_atlas/` and ignored as regenerable bulk. Configuration, raw/reused input identities, commands, software versions, output identities, and final checks are recorded alongside these reports. `METHODOLOGY_CORRECTION.md` explains the separately tested synchronization correction.

Exact next action: researcher review of these artifacts and the choice between coarse common-MTC and high-rate VM20i-only sensor statistics. A larger acquisition and final grouping/label protocol require a later instruction. **Stop here; no model training.**
""")
    write(run/'MSM_VIDEO_ALIGNMENT_REPORT.md',f"""# MSM video alignment and 16-frame contract

**Validated revision 2.** Dataset `{cfg['handle']}`. {summary['frame_contract_pass']} of 127 native intervals pass the camera timing/16-frame gate; {summary['verified_multimodal_examples']} additionally pass the fixed common-MTC gate. No neural network was used to estimate alignment or assess this contract.

## Time mapping and its evidence

For each clip, use **`video_time = sensor_time + offset`** only within the supported regions below. Label boundaries remain in the native sensor clock, with half-open intervals `[start,end)`.

{timing_table}

Both the WAV and the phone AAC contain the same physical machine sounds. Final fitting uses ambient **S2 for every laboratory clip**. Audio is downsampled to 4 kHz for diagnostics; 800–1800 Hz log-band energy is evaluated using a 256-sample STFT window and 40-sample hop (10 ms features). Even, nonoverlapping 8 s reference blocks are calibration data; odd blocks are held out of coarse fitting and offset estimation.

The corrected coarse estimator searches every possible video position for each calibration block, counts agreeing block matches with Pearson correlation at least 0.75, and breaks equal-count ties using summed correlation strength. It does not demand that most of the complete recordings overlap. A local ±0.5 s search refines each anchor. The offset is the median of calibration anchors consistent within 0.10 s. At least 3 calibration anchors, 3 nonoverlapping validation anchors, and 30 s of anchor span are required. Accepted calibration/validation windows define support; weak regions are not extrapolated into usable examples.

No class label, abnormal/normal distinction, expert remark, or label boundary enters the alignment functions. Only after fixing the mappings are native cutting intervals joined to video. Diagnostic label shading is for review and does not participate in fitting.

The base empirical bound is `max(0.08 s, maximum accepted validation residual + 0.04 s)`. The 0.04 s allowance covers feature resolution and residual acoustic timing, with an 0.08 s floor. Where a separately fitted S0 mapping is accepted, microphone disagreement plus 0.04 s also contributes. Dataset9's S0 and S2 estimates are +49.67 s and +49.73 s, giving a conservative **±0.10 s** bound. These are engineering tolerances, not confidence intervals or a proof of zero systematic phone AV skew. Camera AV and first AAC/video PTS both begin at zero in all five clips. Annotation uncertainty and internal MTC feature-window latency remain separate unknowns.

## Scientific correction: reject the earlier dataset9 alias

An exploratory whole-recording cross-correlation demanded at least 70% overlap. The true dataset9 mapping has approximately 71.87 s of physical overlap with a 121.6 s video, below that arbitrary rule. The rule excluded the true lag and selected a repeated-pattern alias near +16.04 s. A raw waveform check and calibration-only recheck exposed the problem before the final reports.

Revision 2 uses calibration-template consensus and independently withheld blocks. It finds **+49.73 s (S2)**, corroborated by **+49.67 s (S0)**. The other four mappings are unchanged. `test_partial_overlap_does_not_force_a_false_smaller_offset` failed before the correction and passed afterwards. The exploratory files and source preimages are preserved in `{acquired}`. The validated manifests and figures in this directory supersede exploratory counts and sequences. See `METHODOLOGY_CORRECTION.md`; no raw data or native label was corrected.

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

{video_table}

Every decoded PTS is strictly increasing with approximately 33.333 ms steps, and the decoded count equals the header count. Some VMX30Ui consecutive frames are byte-identical; all admitted 16-frame selections have 16 unique decoded hashes. This checks the delivered compressed videos, not unavailable original smartphone files. No deduplication or raw-file rewrite was performed.

## Visibility and representative diagnostics

All selected frames from all timing-eligible sequences were inspected in atlases. Milling context is recognizable, but coolant and window droplets often hide the exact cutting edge. Visual inspection verifies an intended milling scene, not the anomaly label or a precisely timed optical contact event. There is no externally timed visual fiducial in this pilot. Keep that limitation separate from the strong shared-audio evidence.

{examples_list}

The plots show all 16 actual frame positions above reference/phone audio and sensor activity, with native label boundaries and source-row identity. They make visible both useful pairs and the two MTC-gap exclusions. Full-recording sensor/label plots and rejected timing regions provide context. Earlier S2-only exploratory plots are not the source of this validated result.

**Decision:** LIMITED GO for a carefully filtered laboratory construction. Re-audit every additional recording using the corrected calibration method. Preserve physical experiment groups, and obtain researcher review before any larger acquisition, architecture substitution, or training.
""")
    print('Wrote Stage 2 reports in',run)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',type=Path,required=True);main(parser.parse_args().run)
