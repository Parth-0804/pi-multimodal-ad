# Foundation audit commands and evidence

The contract was already committed at
`ea4a76f64887fd590fd1f93cc83a726192dcfecb`; no model comparison was run in this pass.

```bash
ma_thesis_env/bin/python -B scripts/intel_welding/04_foundations.py --config configs/intel_welding/foundations.json
ma_thesis_env/bin/python -B -m pytest -q tests/intel_welding/test_intel_foundations.py
ma_thesis_env/bin/python -B -m pip check
git diff --check
git diff --stat
git status --short --branch --untracked-files=all
```

`04_foundations.py` creates a new timestamped directory every time and reads raw
data without writing to it. It performs a complete byte-hash pass and bounded
video decode, so it is an inventory command, not a cheap metadata listing. The
config controls data/output roots and worker count. The population remains all
manifest rows. It never invokes training or creates a replacement partition.

Successful evidence is under
`artifacts/intel_welding/audits/foundation_runs/20260927T114705163655Z/`.
The earlier config-only directory records a failed invocation before inventory.
`dataset_inventory.parquet` and `file_inventory.parquet` contain row/file detail;
CSV crosstabs retain full label/session/process and missingness evidence.

The existing top-level `dataset_inventory.parquet` and `dataset_summary.json`
predate this pass and were preserved. Use the versioned files referenced above,
not the old prefix-hash inventory. The old fixed-path split and context scripts
remain unchanged as evidence and must not be run to resume model development.

`05_foundation_report.py --run <directory>` renders the reviewed snapshot only:
it verifies the summary hash and refuses a different measurement snapshot. Its
narrative must be reviewed for new measurements. It refuses existing report
paths, including top-level pointers; it is not a general overwrite command.
This run initially lacked optional `tabulate`; reporting was changed to a
built-in Markdown formatter and completed without installing dependencies.

Generated outputs remain uncommitted. Parquet/CSV are ignored by repository
policy; small reports/JSON remain untracked for review. Do not bulk-add the
artifacts tree. No new gitignore exception, package metadata or model training
entry point is introduced here. The final-test flag records a locked disposition;
a future final-evaluation command must still implement its own hard enforcement.

Review [PHASE_1_GATE_REPORT.md](../../artifacts/intel_welding/audits/PHASE_1_GATE_REPORT.md)
and [FOUNDATION_PROTOCOL_ADDENDUM.md](FOUNDATION_PROTOCOL_ADDENDUM.md) before
approving any next phase.
