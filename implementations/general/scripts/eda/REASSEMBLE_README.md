# REASSEMBLE dataset walkthrough

Meeting handoff from the validated execution: [open the offline HTML](../../runs/reassemble/20261016T103522253690Z-dataset-walkthrough/01_dataset_walkthrough.html).

For current executions, use the links in [the EDA index](README.md).
The historical handoff above is preserved unchanged. Current runs use
`runs/reassemble/<UTC-timestamp>-dataset-eda/01_reassemble_eda.html`. It contains embedded real frames, sensor plots, a shape
ledger, and silent clips; no internet or kernel is required. The adjacent
`01_reassemble_eda.executed.ipynb` contains the executed code and outputs.
`01_reassemble_eda.ipynb` here is the reusable source, saved without outputs.

Run from the repository root with the existing environment:

```bash
ma_thesis_env/bin/python -B tutorials/EDA/run_eda.py 01_reassemble_eda.ipynb
```

The runner starts a fresh kernel using that same Python, fails on cell errors,
creates a unique UTC output directory, and exports static offline HTML. All
outputs, runtime files, manifests and media remain inside that new directory,
which has its own ignore-all rule. Do not stage, commit or publish raw-derived
outputs. Nothing installs packages, downloads models, trains or evaluates models.

The notebook demonstrates **Section 1 `20260927T154732Z-section1` only**, reading
its saved config and feature bank alongside its linked inventory. It does not
combine later feature banks or represent the latest modelling architecture.
The raw root is resolved from that config (`../datasets/REASSEMBLE`); override it
without editing research configs using:

```bash
ma_thesis_env/bin/python -B tutorials/EDA/run_eda.py 01_reassemble_eda.ipynb --data-root /path/to/REASSEMBLE
```

To change examples, edit the notebook's first parameter cell: change `ACTION`
(default `insert`) or set `MANUAL["success"]` / `MANUAL["failure"]` to a
`("recording_id", "segment_id")` pair. Each must match its requested outcome and
belong to the same saved cohort. Automatic selection is closest to the
within-action, within-outcome median duration, ties broken by recording then
segment ID; locally unavailable examples are excluded and counted. Selection
never consults predictions. Rerun the command to produce a separate output.

The helper exists to keep media encoding, bounded read/check logic, provenance,
and kernel/HTML plumbing out of the teaching flow. The actual cohort, alignment,
statistics and annotation reader functions are imported from `src/reassemble`.
Only two recording blocks are read; no full feature bank or dataset is decoded.

Limitations are visible in the notebook: physical sensor units unverified; audio
present but not verified as aligned or used; no backbone inference or fitted
normalization rerun; no browser playback verification. If the local encoder is
unavailable, static real-frame contact sheets remain. Missing local processor
configuration is reported without download. Raw/feature identity mismatch fails
rather than silently changing the demonstrated study. The selected samples can
involve different objects; annotated failure need not be visually obvious.

The output `reports/verification.json`, `provenance.json`, and `manifests/` contain the checks and source/output identities.
A fresh run never overwrites the source notebook or an earlier run.
