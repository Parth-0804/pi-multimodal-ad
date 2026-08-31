# pi-multimodal-ad

Master's thesis research repository for the **PHM North America 2026 Data
Challenge**: estimating gear-tooth / PAU degradation state from two
independent sensing modalities — post-run photos and high-frequency
vibration sensors — with no organizer-provided ground-truth labels for
either.

New to this repository? Start with **[`REPO_MAP.md`](REPO_MAP.md)** — a
one-page index of every top-level directory, what's active vs. historical,
and where to find things.

## What's actually being worked on

Two independent, unfused baseline models, one per modality:

- **RT-DETR** (image) — trained on heuristic, self-generated pseudo-boxes
  (`phm2026_image_damage_v2`), since no organizer bounding boxes exist.
- **PatchTST** (sensor) — a channel-independent Transformer regressor over
  per-minute vibration/context features, predicting the same provisional
  target.

Both are documented, honestly-reported **negative results** so far (see
`docs/planning/` and `tutorials/`). Model fusion is deliberately deferred
until each unimodal baseline is scientifically stable — see
`tutorials/patchtst_freq_baseline/` and `tutorials/final_baseline_rtdetr/`
for the most recent causal analysis of why each one currently underperforms,
and what would need to change before combining them.

## Governance — read this before changing anything structural

**[`AGENTS.md`](AGENTS.md)** is the repository's working contract: what's
immutable (raw data), what must never be overwritten (versioned run
outputs), and what requires explicit researcher approval before touching.
It is not optional reading — it is enforced by convention throughout this
codebase and by every prior restructuring effort recorded in
`docs/planning/`.

Related policy docs:
- [`docs/active_scope.md`](docs/active_scope.md) — what work is currently in scope.
- [`docs/data_boundaries.md`](docs/data_boundaries.md) — immutable raw-data rules.
- [`docs/output_policy.md`](docs/output_policy.md) — how generated outputs get committed.

## Quickstart

This project is not pip-installable (no `pyproject.toml`/`setup.py`
currently); scripts add `src/` to `sys.path` themselves.

```bash
# Activate the project environment (see requirements.txt for the full stack:
# numpy/pandas/scipy/scikit-learn, transformers/accelerate, PyTorch, etc.)
source ma_thesis_env/bin/activate   # or: python -m venv + pip install -r requirements.txt

# Run any pipeline stage from repo root, e.g.:
ma_thesis_env/bin/python -B scripts/dataset/profile_dataset.py --dry-run
ma_thesis_env/bin/python -B scripts/training/train_patchtst.py --config configs/experiments/phm2026_patchtst_baseline.yaml
```

Every run writes to a new, timestamped, non-overwriting directory under
`runs/<experiment_name>/<timestamp>-<hash>/` with its own config snapshot,
manifests, figures, and report — never in place, never overwriting history.

## Raw data

Raw PHM2026 archives (`gtc-data-experiment/**`) are **not** part of this
repository and are treated as immutable wherever they're mounted. See
`docs/data_boundaries.md` and `configs/datasets/phm2026.yaml`.

(`data/` in this repository is a leftover placeholder from an earlier,
superseded project phase — see below.)

## A note on repository history

This project originally started around a different dataset (the Intel
Robotic Welding Multimodal Dataset) before pivoting to PHM North America
2026. That earlier phase's code, configs, and docs are preserved — not
deleted — under
[`archive/legacy_intel_welding_dataset/`](archive/legacy_intel_welding_dataset/README.md)
for research-history traceability. It is historical only; nothing in the
active pipeline depends on it.

## License

See [`LICENSE`](LICENSE).
