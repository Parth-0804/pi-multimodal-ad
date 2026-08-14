# PHM 2026 dataset-description experiment

This directory defines the active dataset-description study introduced by
backlog task D1.1. Generated runs are intentionally stored below ignored
`runs/phm2026_dataset_description/<run-id>/` rather than inside this tracked
experiment definition.

Run a configuration and path dry run:

```bash
ma_thesis_env/bin/python -B scripts/profile_dataset.py --dry-run
```

Run a bounded smoke inventory:

```bash
ma_thesis_env/bin/python -B scripts/profile_dataset.py \
  --limit 2 \
  --output-dir runs/phm2026_dataset_description
```

Run the complete D1.1 archive inventory:

```bash
ma_thesis_env/bin/python -B scripts/profile_dataset.py \
  --output-dir runs/phm2026_dataset_description
```

The profiler reads filesystem metadata and ZIP central directories only. It
does not extract, decompress, or payload-hash archive members. Each versioned
run contains resolved configuration, input/output manifests, CSV and Parquet
tables, warnings, a Markdown/JSON summary, and provenance.

## D1.2 bounded sensor profiling

Validate the exact pinned D1.1 input and selection without opening raw payloads:

```bash
ma_thesis_env/bin/python -B scripts/profile_sensors.py \
  --mode metadata --dry-run --limit-per-modality 1
```

Run the representative one-source-per-modality metadata scan:

```bash
ma_thesis_env/bin/python -B scripts/profile_sensors.py \
  --mode metadata --limit-per-modality 1 \
  --output-dir runs/phm2026_dataset_description
```

Full statistics require an explicit positive source limit. The complete
metadata and full-value scans are intentionally not automatic. See
`docs/planning/D1_2_CHECKPOINT.md` for exact run IDs, coverage, validation,
and cost estimates.

## D1.3 image profiling

Validate the exact pinned D1.1 input without opening an image payload or
writing output:

```bash
ma_thesis_env/bin/python -B scripts/profile_images.py \
  --mode header --dry-run
```

Run the complete bounded header scan:

```bash
ma_thesis_env/bin/python -B scripts/profile_images.py \
  --mode header \
  --output-dir runs/phm2026_dataset_description
```

Run complete headers with the configured deterministic sampled-quality set:

```bash
ma_thesis_env/bin/python -B scripts/profile_images.py \
  --mode sampled --sample-size 104 \
  --output-dir runs/phm2026_dataset_description
```

Full pixel mode requires an explicit positive `--limit` and is not automatic.
See `docs/planning/D1_3_CHECKPOINT.md` for exact run IDs, structural and
timestamp evidence, validation, and cost estimates.
