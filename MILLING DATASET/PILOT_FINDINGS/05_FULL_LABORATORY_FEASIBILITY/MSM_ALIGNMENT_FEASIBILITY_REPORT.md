# Full laboratory alignment feasibility

Dataset `manufuturetoday/multi-sensor-for-metal-milling-anomaly/versions/2` (ID 8392825), [official dataset](https://www.kaggle.com/datasets/manufuturetoday/multi-sensor-for-metal-milling-anomaly), [publication](https://www.nature.com/articles/s41597-026-07255-7). Version 2 was reverified against the official public API and all 481 paths/sizes match Stage 1. All native labels and historical outputs were preserved.


**45 of 56 recordings pass synchronization; 1924 intervals pass the exact 16-frame contract.** 1895 additionally pass common MTC. Native labels never choose or improve a clock mapping.

Reuse the corrected final Stage 2 algorithm: S2 and AAC downsampled to 4 kHz; fixed 800–1800 Hz log-energy, 256-point STFT and 40-sample hop. Even nonoverlapping 8 s blocks alone determine calibration consensus and median offset. Odd blocks are withheld anchors. Require correlation >=0.75, >=3 calibration and >=3 validation anchors, >=30 s anchor span and consistency within 0.10 s. Supported regions are the union of accepted 8 s blocks; no unsupported extrapolation. The map is `video_time = sensor_time + offset`. No affine warp was fitted.

An extra conservative rejection check flags distant (>1 s) alternatives with equal maximum calibration votes and sufficient independent validation support. Validation never changes the selected offset; it only accepts/rejects. This is a documented data-quality rejection extension, not a performance-selected protocol relaxation. Rejected equal-consensus cases are retained with their alternative offsets in `manifests/alignment_results.json`.

The engineering uncertainty is max(0.08 s, held-out residual +0.04 s). Existing pilot microphone disagreement bounds are preserved, including **VMX9 +49.73 ±0.10 s**. No additional microphone variant was acquired. New bounds lack cross-microphone corroboration. Phone systematic audio/video skew, acoustic path delay and annotation uncertainty remain unresolved; empirical bounds are not calibrated confidence intervals. First native AAC PTS was checked for every new clip; nonzero/unverified origins are rejected. Native video PTS and actual display SAR are separately checked.

The earlier +16.04 s VMX9 alias was caused by a minimum-whole-record-overlap condition and is permanently superseded. The corrected estimator permits partial overlap and independent validation. Original correction: [MILLING DATASET/runs/20261027T001047876764Z-stage2-validated/METHODOLOGY_CORRECTION.md](../20261027T001047876764Z-stage2-validated/METHODOLOGY_CORRECTION.md).

| Experiment | Accepted | Offset s | Bound s | Cal/val | Max val residual s | Support sensor s | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| imi_vm20i/dataset1 | True | -2.315 | 0.08 | 4/6 | 0.03500000000000014 | [[8.0, 48.0], [56.0, 96.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset10 | True | -2.78 | 0.08 | 7/5 | 0.020000000000000018 | [[16.0, 104.0], [288.0, 296.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset11 | True | -2.44 | 0.08000000000000004 | 20/20 | 0.040000000000000036 | [[8.0, 208.0], [216.0, 232.0], [248.0, 256.0], [264.0, 280.0], [288.0, 328.0], [336.0, 352.0], [368.0, 392.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset12 | False | -3.86 | 0.09000000000000027 | 16/17 | 0.050000000000000266 | [[8.0, 152.0], [168.0, 192.0], [200.0, 248.0], [256.0, 304.0]] | ambiguous_equal_calibration_consensus |
| imi_vm20i/dataset13 | True | -2.66 | 0.08000000000000004 | 17/17 | 0.040000000000000036 | [[8.0, 280.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset14 | True | -3.99 | 0.10000000000000006 | 22/24 | 0.06000000000000005 | [[8.0, 216.0], [232.0, 256.0], [272.0, 320.0], [328.0, 416.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset15 | False | -1.65 | 0.08 | 1/2 | 0.010000000000000009 | [[8.0, 32.0]] | insufficient_validation_support |
| imi_vm20i/dataset16 | True | -2.14 | 0.10000000000000006 | 15/14 | 0.06000000000000005 | [[8.0, 200.0], [208.0, 248.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset17 | False | -2.56 | 0.08 | 2/2 | 0.0 | [[8.0, 40.0]] | insufficient_validation_support |
| imi_vm20i/dataset18 | False | -3.5149999999999997 | 0.08 | 2/2 | 0.0050000000000003375 | [[8.0, 40.0]] | insufficient_validation_support |
| imi_vm20i/dataset19 | True | -1.57 | 0.08 | 5/6 | 0.010000000000000009 | [[8.0, 96.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset2 | False | -35.82 | None | 2/0 | None | [[48.0, 56.0], [64.0, 72.0]] | insufficient_validation_support |
| imi_vm20i/dataset20 | True | -2.06 | 0.08 | 18/18 | 0.029999999999999805 | [[8.0, 296.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset21 | True | -5.07 | 0.09000000000000072 | 28/27 | 0.05000000000000071 | [[8.0, 328.0], [336.0, 456.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset22 | False | — | — | 0/0 | — | [] | no_calibration_anchors |
| imi_vm20i/dataset23 | True | -1.795 | 0.08 | 6/6 | 0.015000000000000124 | [[8.0, 88.0], [96.0, 112.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset24 | True | -1.11 | 0.12000000000000008 | 24/23 | 0.08000000000000007 | [[8.0, 16.0], [24.0, 104.0], [112.0, 176.0], [184.0, 264.0], [272.0, 376.0], [384.0, 392.0], [400.0, 432.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset25 | True | -3.92 | 0.08000000000000004 | 23/21 | 0.040000000000000036 | [[8.0, 16.0], [24.0, 232.0], [240.0, 248.0], [256.0, 272.0], [280.0, 328.0], [360.0, 376.0], [384.0, 392.0], [400.0, 440.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset26 | True | -2.36 | 0.08 | 18/19 | 0.03000000000000025 | [[8.0, 304.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset27 | True | 0.1 | 0.09 | 18/18 | 0.04999999999999999 | [[8.0, 296.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset28 | True | 9.33 | 0.13999999999999965 | 27/11 | 0.09999999999999964 | [[0.0, 24.0], [32.0, 104.0], [112.0, 152.0], [160.0, 168.0], [176.0, 184.0], [192.0, 216.0], [224.0, 232.0], [240.0, 248.0], [256.0, 280.0], [288.0, 296.0], [304.0, 328.0], [336.0, 344.0], [352.0, 360.0], [368.0, 376.0], [392.0, 400.0], [416.0, 424.0], [432.0, 440.0], [464.0, 472.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset29 | True | -3.27 | 0.12000000000000008 | 24/25 | 0.08000000000000007 | [[8.0, 32.0], [40.0, 152.0], [160.0, 168.0], [176.0, 184.0], [192.0, 232.0], [240.0, 272.0], [288.0, 312.0], [320.0, 416.0], [424.0, 440.0], [456.0, 464.0], [472.0, 480.0], [488.0, 496.0], [504.0, 512.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset3 | True | -2.19 | 0.08 | 5/6 | 0.020000000000000018 | [[8.0, 96.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset30 | True | -6.11 | 0.09000000000000072 | 27/10 | 0.05000000000000071 | [[8.0, 72.0], [80.0, 88.0], [96.0, 104.0], [112.0, 120.0], [128.0, 136.0], [144.0, 152.0], [160.0, 168.0], [176.0, 184.0], [192.0, 200.0], [208.0, 264.0], [272.0, 328.0], [336.0, 344.0], [352.0, 360.0], [400.0, 408.0], [416.0, 424.0], [432.0, 440.0], [448.0, 456.0], [464.0, 472.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset31 | True | -2.03 | 0.09000000000000027 | 24/25 | 0.050000000000000266 | [[8.0, 208.0], [224.0, 416.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset32 | True | -1.5 | 0.08000000000000004 | 25/26 | 0.040000000000000036 | [[8.0, 416.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset33 | False | 9.67 | 0.08 | 2/1 | 0.009999999999999787 | [[0.0, 24.0]] | insufficient_validation_support |
| imi_vm20i/dataset34 | True | -2.74 | 0.09000000000000027 | 23/24 | 0.050000000000000266 | [[8.0, 216.0], [224.0, 232.0], [240.0, 256.0], [264.0, 320.0], [328.0, 416.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset35 | True | -2.06 | 0.08000000000000004 | 28/28 | 0.040000000000000036 | [[8.0, 456.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset36 | True | -3.92 | 0.08000000000000004 | 27/26 | 0.040000000000000036 | [[8.0, 72.0], [80.0, 88.0], [96.0, 112.0], [120.0, 456.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset37 | True | -2.49 | 0.08 | 28/28 | 0.03999999999999959 | [[8.0, 456.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset4 | True | -2.34 | 0.08 | 5/6 | 0.010000000000000231 | [[8.0, 96.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset5 | True | 7.59 | 0.08 | 4/5 | 0.019999999999999574 | [[8.0, 16.0], [24.0, 88.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset6 | True | -3.11 | 0.1300000000000003 | 28/12 | 0.0900000000000003 | [[8.0, 16.0], [32.0, 80.0], [88.0, 128.0], [136.0, 152.0], [160.0, 168.0], [176.0, 184.0], [192.0, 200.0], [208.0, 216.0], [224.0, 272.0], [288.0, 296.0], [304.0, 312.0], [336.0, 360.0], [368.0, 376.0], [384.0, 392.0], [400.0, 408.0], [416.0, 424.0], [432.0, 440.0], [448.0, 456.0], [480.0, 488.0], [496.0, 504.0], [512.0, 520.0]] | accepted_with_bounded_support |
| imi_vm20i/dataset7 | False | 20.99 | 0.08 | 1/1 | 0.00999999999999801 | [[8.0, 24.0]] | insufficient_validation_support |
| imi_vm20i/dataset8 | False | 34.95 | 0.11000000000000029 | 1/1 | 0.07000000000000028 | [[8.0, 24.0]] | insufficient_validation_support |
| imi_vm20i/dataset9 | False | -21.5 | 0.09999999999999873 | 2/2 | 0.05999999999999872 | [[32.0, 64.0]] | insufficient_validation_support |
| imi_vmx30ui/dataset1 | False | -6.38 | 0.09999999999999962 | 3/2 | 0.05999999999999961 | [[8.0, 40.0], [48.0, 56.0]] | insufficient_validation_support |
| imi_vmx30ui/dataset10 | True | 7.85 | 0.08 | 18/17 | 0.020000000000000462 | [[0.0, 280.0]] | accepted_with_bounded_support |
| imi_vmx30ui/dataset11 | True | 12.52 | 0.12999999999999987 | 23/24 | 0.08999999999999986 | [[8.0, 24.0], [32.0, 56.0], [64.0, 80.0], [88.0, 256.0], [264.0, 416.0]] | accepted_with_bounded_support |
| imi_vmx30ui/dataset12 | True | 6.64 | 0.08000000000000004 | 15/14 | 0.040000000000000036 | [[0.0, 224.0], [288.0, 296.0]] | accepted_with_bounded_support |
| imi_vmx30ui/dataset13 | True | 6.08 | 0.11000000000000029 | 22/22 | 0.07000000000000028 | [[8.0, 32.0], [40.0, 48.0], [56.0, 72.0], [80.0, 88.0], [96.0, 184.0], [192.0, 200.0], [208.0, 224.0], [232.0, 240.0], [248.0, 256.0], [264.0, 280.0], [288.0, 296.0], [304.0, 336.0], [344.0, 456.0]] | accepted_with_bounded_support |
| imi_vmx30ui/dataset14 | True | 6.22 | 0.08000000000000004 | 23/23 | 0.040000000000000036 | [[0.0, 8.0], [16.0, 264.0], [280.0, 288.0], [296.0, 336.0], [344.0, 368.0], [376.0, 384.0], [392.0, 400.0], [416.0, 424.0], [432.0, 440.0], [448.0, 456.0]] | accepted_with_bounded_support |
| imi_vmx30ui/dataset15 | True | 6.3 | 0.08999999999999983 | 30/25 | 0.04999999999999982 | [[0.0, 8.0], [16.0, 176.0], [184.0, 264.0], [272.0, 352.0], [360.0, 424.0], [432.0, 440.0], [448.0, 456.0], [480.0, 488.0], [496.0, 520.0]] | accepted_with_bounded_support |
| imi_vmx30ui/dataset16 | True | -4.96 | 0.08000000000000004 | 13/14 | 0.040000000000000036 | [[8.0, 80.0], [88.0, 200.0], [224.0, 256.0]] | accepted_with_bounded_support |
| imi_vmx30ui/dataset17 | True | -3.3 | 0.08 | 7/6 | 0.020000000000000018 | [[8.0, 72.0], [80.0, 120.0]] | accepted_with_bounded_support |
| imi_vmx30ui/dataset18 | True | -2.7 | 0.09000000000000027 | 16/16 | 0.050000000000000266 | [[8.0, 264.0]] | accepted_with_bounded_support |
| imi_vmx30ui/dataset19 | True | -6.64 | 0.08 | 13/13 | 0.020000000000000462 | [[8.0, 216.0]] | accepted_with_bounded_support |
| imi_vmx30ui/dataset2 | True | -3.2 | 0.08 | 5/6 | 0.03000000000000025 | [[8.0, 96.0]] | accepted_with_bounded_support |
| imi_vmx30ui/dataset3 | True | -3.19 | 0.08 | 5/6 | 0.020000000000000018 | [[8.0, 96.0]] | accepted_with_bounded_support |
| imi_vmx30ui/dataset4 | True | -4.2 | 0.08 | 5/7 | 0.020000000000000462 | [[8.0, 32.0], [40.0, 112.0]] | accepted_with_bounded_support |
| imi_vmx30ui/dataset5 | True | 21.66 | 0.08 | 6/7 | 0.03999999999999915 | [[8.0, 56.0], [72.0, 80.0], [88.0, 104.0], [112.0, 120.0], [128.0, 144.0], [232.0, 240.0]] | accepted_with_bounded_support |
| imi_vmx30ui/dataset6 | True | 8.74 | 0.13999999999999965 | 25/25 | 0.09999999999999964 | [[0.0, 400.0]] | accepted_with_bounded_support |
| imi_vmx30ui/dataset7 | True | 8.65 | 0.11000000000000029 | 34/36 | 0.07000000000000028 | [[8.0, 16.0], [24.0, 88.0], [96.0, 320.0], [328.0, 592.0]] | accepted_with_bounded_support |
| imi_vmx30ui/dataset8 | True | 19.89 | 0.08 | 12/12 | 0.019999999999999574 | [[8.0, 200.0]] | accepted_with_bounded_support |
| imi_vmx30ui/dataset9 | True | 49.73 | 0.1 | 4/4 | 0.010000000000005116 | [[0.0, 64.0]] | accepted_with_bounded_support |

## Exact interval/frame association

The frozen selector trims by uncertainty plus half a native frame, places 16 equal-bin centers inside the guarded native [start,end) cut, maps to video time and selects nearest native PTS. It rejects insufficient support/coverage, duplicate indices, nonmonotonic or gapped PTS, boundary-crossing uncertainty and fewer than 16 unique decoded-content hashes. New videos are decoded once forward, with the header-CFR optimization independently checked against every native PTS; the selector is rerun on the actual decoded clock. A failed clock confirmation is a rejection, not approximate recovery. Every admitted frame preserves order, actual PTS, source row, label and content hash.

SAR correction preserves source display geometry; no stretching to square pixels and no arbitrary experiment-wide images are substituted. Only compact contact sheets are saved; no 640×640 cache or CNN features were generated.

## Observability remains unresolved

All 1895 joint candidates require independent interval visibility review. 1808 new frame-valid sequences lack even the earlier pilot-style context judgement. The original pilot only established recognizable coarse milling context under coolant/window occlusion; it did not prove optical anomaly separability. A representative contact sheet per experiment is in `manifests/metadata_relationships.json` and the consolidated diagnostic index; it does not certify all cuts in that experiment. Rejected clips have clearly marked unlabeled overview sheets. Expert/researcher review must separate context visibility, cutting-edge visibility and anomaly observability. No anomaly labels were used to optimize synchronization.
