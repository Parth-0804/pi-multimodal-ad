# Ten real MSM cutting examples — five matched pairs

Open [VIEWER.html](VIEWER.html) in a browser for synchronized frame stepping, full camera views and enlarged cutting-context crops. The viewer needs no server or internet. Keep the `frames/` and `figures/` folders beside it. Use [MATCHED_CUT_REVIEW.pdf](MATCHED_CUT_REVIEW.pdf) for the complete printable 22-page set.

**Exactly 10 cuts / 160 unique source frames: five label 0, five label 1.** Three pairs come from VM20i and two from VMX30Ui. Every pair is from one experiment; numerical settings and native tool/material descriptions match exactly. **All five pairs differ in native direction: normal DOWN, abnormal UP.** This is a real confound, not an exact all-factor match. No within-experiment complete match including direction was available in the eligible mixed-label pool. This is a descriptive inspection package, not a causal comparison, representative evaluation sample or new ground truth.

| Pair | Experiment | Normal row | Abnormal row | N rpm | ap mm | ae mm | F mm/s | Tool / material |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P01 | imi_vm20i/dataset16 | 25 | 24 | 9250 | 38.1 | 0.635 | 35.98333 | E / AISI 1018 |
| P02 | imi_vm20i/dataset25 | 9 | 8 | 9000 | 12.7 | 0.254 | 27.09333 | A / AA 6061 |
| P03 | imi_vm20i/dataset27 | 25 | 24 | 9250 | 38.1 | 0.635 | 38.1 | E / AISI 4140 |
| P04 | imi_vmx30ui/dataset14 | 41 | 40 | 9000 | 38.1 | 0.0635 | 22.01333 | A / AA 6061 |
| P05 | imi_vmx30ui/dataset9 | 13 | 14 | 4700 | 19.05 | 1.27 | 25.4 | D / AISI 1018 |

All parameter values are copied from the original `label.csv`. N is spindle speed, ap axial depth, ae radial depth, F feed rate, Z teeth and D tool diameter. Units follow the [publication's annotation schema](https://www.nature.com/articles/s41597-026-07255-7). Native Tool strings are categories, not verified unique physical tool IDs.

## Examine the examples

1. Open the viewer and choose P01–P05. Normal is on the left, abnormal on the right.
2. Step through frames 1–16 with the slider, buttons or arrow keys. The two cuts share relative within-cut frame position, not simultaneous physical time. Read each actual video/sensor timestamp.
3. Compare the full camera view with the orange fixed ROI and its enlarged crop. The same rectangle is used for both cuts in a pair and for every frame.
4. Review context visibility, tool/workpiece contact, occlusion and whether any visible distinction survives the direction difference. Use “uncertain” when appropriate. Do not infer a visible defect solely from the label.
5. Record notes in the viewer and download JSON, or fill [REVIEW_TEMPLATE.csv](REVIEW_TEMPLATE.csv). Browser notes are not persisted automatically.

Several images are heavily obscured by coolant/window droplets. They are retained because cuts were chosen by metadata, not by apparent class separability or clear views. ROIs are approximate tool/workpiece-context rectangles, not expert cutting-contact or anomaly localizations. Crops are literal pixel slices from the SAR-corrected full view, with a separate lossless unscaled crop and a threefold bilinear display enlargement. No contrast change, sharpening, deblurring, generated image content or model inference is used. Enlargement does not recover occluded detail.

Full display frames are 270×480, corrected from the delivered video's 720×480 coded pixels and 3:8 sample aspect ratio. Original source MP4 filenames/hashes remain in the manifest; raw media were not changed or copied into this review package. Exactly 160 source frames are represented as multiple views; full/crop copies do not create extra prediction examples.

## Files

- `VIEWER.html`: offline interactive comparison, actual timestamps and optional qualitative notes export.
- `MATCHED_CUT_REVIEW.pdf`: guide, parameter table and all 10 full-camera + 10 ROI contact sheets.
- `figures/P01_comparison.jpg` through `P05_comparison.jpg`: representative frame-08 pair previews.
- `figures/*_full_16frames.jpg` and `*_roi_16frames.jpg`: all 160 frames in each view.
- `frames/`: clean full images, lossless literal crops and enlarged display crops for all 160 frame identities.
- `CUT_MANIFEST.csv`, `PAIR_MANIFEST.csv`, `FRAME_MANIFEST.csv`: source identities, labels, settings, time mapping, frame order and hashes.
- `SENSOR_STATISTICS_90.csv`: previously verified 90-feature vectors for these ten matching sensor intervals; no new classifier.
- `REVIEW_TEMPLATE.csv`: qualitative review form. `config/roi_config.json`: fixed crop coordinates and rationale.

The native label applies to the whole annotated cut. It is not a frame-level defect annotation. All selected examples already passed the full-laboratory timing/16-frame/common-MTC gates. Exact source pixels and presentation times were checked against the saved frame manifest; frame uncertainty stays inside the native half-open interval. VMX30Ui/dataset9 retains the corrected +49.73 s mapping.

Version: `manufuturetoday/multi-sensor-for-metal-milling-anomaly/versions/2`. Authoritative cohort: `MILLING DATASET/runs/20261027T015205931708Z-stage5-full-lab-validated`. No download, training, CNN extraction, F2 evaluation or interaction with the Phase 1 job occurred. Previous reports/results and the tracked dirty working tree remain unchanged.
