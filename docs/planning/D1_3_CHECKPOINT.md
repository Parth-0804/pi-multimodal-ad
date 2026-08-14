# D1.3 checkpoint — gear-tooth image structure and quality

Status: **COMPLETE WITH FULL HEADER COVERAGE AND BOUNDED PIXEL COVERAGE**  
Evidence date: `2026-08-13`

## Exact source

D1.3 consumes only the exact D1.1 run
`20260813T202043619114Z-ad7f9832`. The source artifact hashes are validated
before selection:

- `tables/asset_inventory.parquet`:
  `3e6b1c488fab9faa5b3700187d3b789469b8020ff04c6f4c5f4239da11d9ab4e`
- `tables/archive_members.parquet`:
  `01bfc91ed669f93502f9bb2225e58bc4069184fae16242964758809881c3ae3d`

No “latest run” discovery is used. The inventory listing contains 1,311 JPG
members in 26 photo archives. The 37 `Thumbs.db` members are not images and
are excluded from the image profile.

## Generated D1.3 runs

- Complete header run: `20260813T215718624432Z-bd9395ad`
- Complete-header plus deterministic sampled-quality run:
  `20260813T215756728445Z-bd9395ad`

The complete header run covered all 1,311 discovered images and all 26 photo
archives. All 1,311 headers were readable. The observed structural schema was
uniform: 1,440 × 2,560 × 3, RGB, `uint8`, 8-bit JPEG. The run processed
645,111,595 encoded image bytes. CSV and Parquet contain the same image IDs
and row count, and every output-manifest hash was revalidated.

The sampled-quality run repeated the complete 1,311-image header scan and
decoded a deterministic archive-stratified subset of 104 images. All 104
selected pixel streams were readable. Quality metrics are normalized luma
statistics, a four-neighbour Laplacian-variance sharpness proxy, darkness,
overexposure/clipping fractions, SHA-256 of covered encoded files, and a
versioned 64-bit difference hash. They are acquisition-quality evidence, not
damage labels.

The 104-image hash-covered subset contained no exact SHA-256 duplicate group.
It produced 127 dHash/Hamming near-duplicate candidate pairs at the configured
threshold. These are candidates within the sampled subset, not proof of
semantic or dataset-wide duplication.

## Counts and annotation evidence

| Experiment | Images | Inspection archives |
|---|---:|---:|
| EXP-A | 455 | 7 |
| EXP-B | 576 | 9 |
| EXP-F | 280 | 10 |
| **Total** | **1,311** | **26** |

All image names yielded a tooth identifier. EXP-A and EXP-B archives contain
both canonical `Tooth NN` views and timestamp-like camera-sequence views for
teeth 1–4; EXP-F contains canonical tooth views. Inspection grouping is the
source photo archive and does not imply a health state or precise acquisition
session.

No JSON, XML, text, mask, or other obvious annotation sidecar was discovered
in the exact D1.1 archive listing for these photo archives. Accordingly, all
rows are marked `none_discovered_in_archive_listing`. This is bounded listing
evidence, not a claim that undocumented external annotations cannot exist.
No bounding box, segmentation mask, keypoint, continuous target, or verified
image-level damage label is established by this profile.

## Timestamp evidence and D1.4 gate

- 640 camera-sequence filenames contain a local-naive timestamp token.
- 671 images have no timestamp token.
- 0 image rows have a verified UTC timestamp.

The local-naive tokens have no evidenced timezone. They remain in
`timestamp_raw` and `timestamp_local_naive` with
`timestamp_status=timezone_unknown`; they are never coerced to UTC. ZIP member
times, archive order, inspection stage, and run order are not substitutes for
event time. A cross-modal temporal join is therefore blocked unless a
comparable camera clock or timezone relationship can be established.

## Resource and cost decision

The complete header scan was bounded and therefore executed. Its profiling
phase took 3.97 s; the complete CLI run, including reports and traceable
preview sheets, took about 15 s. Materialization is one image at a time. The
largest inventory-listed encoded JPG is about 0.64 MB, and the configured
member guard is 8 MiB.

The sampled-quality profiling phase took 21.56 s for 104 decoded images and
about 30 s end to end. A 1,440 × 2,560 RGB raster is about 10.55 MiB before
metric workspace. Complete decoding would represent about 14.5 GB decimal of
aggregate RGB raster work, plus encoded reads, hashing, metrics, and
near-duplicate comparison. Extrapolating from the bounded run gives a rough
3–10 minute planning range, but pairwise hashing and cache effects make that
uncertain. Complete pixel-quality mode was not launched automatically.

Generated output storage was about 3.9 MB for the complete header run and
5.1 MB for the sampled-quality run. Preview EXIF transforms and thumbnails
exist only in generated contact sheets; source images are never modified,
rotated, resized, or persistently extracted.

## Validation

- D1.3 focused synthetic image/adapter/archive suite: `30 passed`
- Complete unit suite after D1.3: `73 passed in 8.54s`
- Focused Black check: `32 files would be left unchanged`
- `pip check`: no broken requirements
- Dry run: 1,311 images selected; 645,111,595 encoded bytes; no raw archive
  opened and no output written
- Complete header artifact: 1,311 CSV rows = 1,311 Parquet rows
- Sampled-quality artifact: 104 successful pixel rows of 104 selected
- Generated output-manifest SHA-256 values: all revalidated
- Temporary cleanup: no `pi_multimodal_archive_*` directory remained

The repository-wide Black invocation also reported the two pre-existing Intel
scripts `src/generate_manifest.py` and `src/create_intel_manifest.py`; those
historical, out-of-scope files were not modified. The focused implementation
tree is Black-clean.

## Limitations carried forward

- Header success does not prove complete pixel-stream integrity for the 1,207
  images not decoded by the sampled-quality run.
- Exact and perceptual duplicate evidence is complete only for the 104
  hash-covered images.
- Image-quality measures are descriptive proxies, never target or health
  labels.
- No verified image UTC clock exists, so image-to-sensor temporal differences
  cannot currently be calculated honestly.
- D1.2 sensor coverage is representative rather than complete across all
  experiments and runs.

No raw file, Intel data, historical output, or `.gitignore` content was
modified. D1.4 may proceed only as an evidence-preserving alignment audit; it
must report the clock-domain blocker rather than inventing timestamps.
