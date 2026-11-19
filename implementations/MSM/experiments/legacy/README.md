# MILLING DATASET

MSM Stage 1: selective annotation acquisition and native-label audit. No model
training or pilot media acquisition is authorized by this stage.

Verified Kaggle handle: `manufuturetoday/multi-sensor-for-metal-milling-anomaly/versions/2`
(dataset ID 8392825).

The [versioned acquisition report](runs/20261026T230520276818Z-stage1/MSM_STAGE1_ACQUISITION_REPORT.md)
records the sources, acquisition decisions, checks, and next proposed action.

- [Label audit](runs/20261026T230520276818Z-stage1/MSM_LABEL_AUDIT.md)
- [Interval manifest](runs/20261026T230520276818Z-stage1/MSM_INTERVAL_MANIFEST.csv)
- [File availability and exact pilot plan](runs/20261026T230520276818Z-stage1/MSM_FILE_AVAILABILITY.md)

All 69 native `label.csv` files are preserved under `data/raw/msm/versions/2/`
and excluded from Git. `source/` contains the supplied downloader with focused
acquisition safeguards, official inventory inspection, annotation auditing, and
report rendering. `tests/` uses tiny synthetic inputs.

The 2,575 intervals comprise 1,933 normal, 465 abnormal, and 177 stable
defective-tool cuts. There are 30 positive-containing experiment folders;
physical independence and video synchronization remain unverified.

Stage 1 proposed a five-experiment lab inspection requiring 106.130 MB, with an
optional industrial diagnostic adding 96.756 MB. Stage 2 was subsequently
authorized and is documented below.

## Stage 2 — validated feasibility pilot

**LIMITED GO:** 114 examples support 16 ordered video frames plus a fixed common
MTConnect statistics vector; 13 of 127 pilot intervals are excluded. The separate
video-plus-raw-accelerometer contract admits 39 VM20i examples. These cohorts
overlap and must not be added or pooled across different sensor schemas.

- [Modality audit](runs/20261027T001047876764Z-stage2-validated/MSM_STAGE2_MODALITY_AUDIT.md)
- [Video alignment report](runs/20261027T001047876764Z-stage2-validated/MSM_VIDEO_ALIGNMENT_REPORT.md)
- [Pilot sample manifest](runs/20261027T001047876764Z-stage2-validated/MSM_PILOT_SAMPLE_MANIFEST.csv)
- [Separately tested alignment correction](runs/20261027T001047876764Z-stage2-validated/METHODOLOGY_CORRECTION.md)

The earlier exploratory Stage 2 run is preserved. Its dataset9 offset and counts
are superseded by the validated revision, which fixes a partial-overlap alias.
Diagnostic figures and all-frame review atlases are retained locally and ignored
by Git. No model training was performed. Wait for researcher review before any
further acquisition or experimental stage.
