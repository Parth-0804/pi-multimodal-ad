# Autonomous completion: resume guide

The user explicitly authorized all non-destructive phases in attachment
`510a4215-21ba-43d4-9fdf-dc00efac7ce4`. Negative results and failed optional gates
are results, not reasons to pause. Do not retune to make a gate win.

## Inspect before restarting

Live state: `docs/reassemble/AUTONOMOUS_CONTINUATION.md`.
Configuration and all unique run paths: `configs/reassemble/completion.json`.
Protocol: `docs/reassemble/SECTION_3_CORRUPTION_PROTOCOL.md`.

```bash
ps -eo pid,etime,args | rg 'reassemble/(12_|13_|15_|22_)'
tail -5 runs/reassemble/20260927T204649Z-section3/extraction_supervisor.log
tail -10 runs/reassemble/20260927T204649Z-final-synthesis/driver.log
df -h .
```

Do not launch duplicate supervisors/drivers. The supervisor runs three visual
and four sensor workers, claiming separate recording checkpoints. Extraction
must reach 148 valid NPZ/JSON pairs in each of `section3/visual` and
`section3/sensor`. Completed files are hash-checked on resume.

## Resume commands (only when corresponding process has stopped)

```bash
ma_thesis_env/bin/python -B scripts/reassemble/15_section3_extract_parallel.py
ma_thesis_env/bin/python -B scripts/reassemble/22_completion_driver.py
```

The driver waits for extraction, then executes:

1. `14_section3_evaluate.py`: frozen clean and corrupted predictions.
2. `16_section3_report.py`: paired clustered metrics and mechanism assessment.
3. `17_modality_dropout.py`: one fixed F6 variant; nested train-only thresholds.
4. `18_completion_gates.py`: audio clock/coverage and object feasibility.
5. `19_completion_efficiency.py`: repeated warm component measurements.
6. `20_completion_synthesis.py`: final tables, figures and narratives.
7. `21_completion_audit.py`: preservation, numeric, test and claim inventory.

Attempt JSON/log files record exact commands, source hashes and failures. If a
stage fails, inspect its latest attempt log, correct the specific software issue,
retain all completed evidence, document the correction, and resume. Do not
silently loosen parity or leakage guards. Synthetic report smoke outputs under
`/tmp/reassemble_SYNTHETIC_report_smoke_*` are not study results.

Audio is not automatically excluded merely for lacking per-sample timestamps;
reliable segment clock transfer suffices. A newly found possible clock anchor
requires actual inspection. The existing inventory has no verified audio clock
mapping. Physical-object feasibility must be assessed from identity and joint
recording/object support, not fabricated grouping.

## Final review and seal

After the driver completes, inspect every risky-word occurrence in
`final-synthesis/claim_inventory.json`, check generated figures, and reconcile all
claims to `results.json`. Record review with `status: passed` and a concrete
occurrence-level rationale in `final-synthesis/claim_review.json`. Then:

```bash
ma_thesis_env/bin/python -B scripts/reassemble/21_completion_audit.py --seal
```

Sealing rechecks preserved evidence and creates the completion status, final
continuation and per-phase SHA256 manifests. It is allowed only after actual
review and passing validation. Verify every new manifest, stage only the explicit
allowlisted outputs and relevant sources, and make a scoped local commit. No push.
Do not edit sealed outputs without a new, versioned correction artifact.

## Boundaries

Preserve Sections 1/1B/2 and their source/continuation files exactly. Preserve
historical PHM evidence, raw HDF5 data and credentials. No deletion, publication,
raw-data recovery, backbone fine-tuning, additional PatchTST epochs or new gate
architecture. Storage below 20 GiB stops new jobs; 20–29 GiB prohibits new large
caches. Numerical caches/checkpoints stay local and ignored.

Success requires `artifacts/reassemble/reports/REASSEMBLE_COMPLETION_STATUS.md`
to start `REASSEMBLE STUDY COMPLETE`, with all core questions answered and only
optional future work remaining. Main handoff is `FINAL_REASSEMBLE_HANDOFF.md` in
the same reports directory.
