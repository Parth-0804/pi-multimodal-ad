# REASSEMBLE continuation handoff

## Status: initial execution completed; researcher review next

Acquisition, extraction, full recording audit, labels, modality selection and
nested splits are complete. No jobs need resuming. No models were trained.
Read [MASTER_SPECIFICATION.md](MASTER_SPECIFICATION.md), sections 71–72, and
../../AGENTS.md before continuing. The user authorized this initial execution;
training requires the next phase approval. Preserve all raw archives and evidence.

## Results and limitations

- All four official downloads matched published MD5; all three ZIP CRC tests passed.
- All 149 H5 recordings and 153 pose JSON files extracted; all 149 H5 audited.
- Primary action annotations: 4,551; successes 4,035; failures 516.
- Primary visual+sensor cohort: 4,530 segments, 509 failures, 148 recordings.
- Selected camera: hand. Candidate microphone: hand_audio, secondary only.
- Audio decodes, but stored data do not establish independent offset/drift.
  No verified tri-modal cohort is available. Do not infer missing audio from that.
- Nested 5 outer / 4 inner folds, seed 20260927; recording-disjoint, both classes
  in every assessment partition. Same-day conditions remain a generalization limit.
- Official secondary split: 111 train / 37 test; omits 2025-01-10-16-17-40,
  whose hand camera is absent. Keep this recording in raw inventory.
- G0–G4 PASS for dual-modality readiness. G5–G14 are unassessed.
- 32 synthetic tests passed; pip check and whitespace checks passed.
- 68,745 protected files matched size, mtime and mode; historical Git blob retained.
- Approximately 95.46 GiB free after extraction/cache. Do not redownload or clean up.

## Paths (relative to repository root)

- Dataset: ../datasets/REASSEMBLE/{downloads,raw,cache}; all outside Git.
- Configuration: configs/reassemble/audit.json (data_root ../datasets).
- Frozen pre-download contract: docs/reassemble/RESEARCH_CONTRACT.md.
- Final report: artifacts/reassemble/audits/PHASE_A_B_GATE_REPORT.md.
- Other final evidence: grouping_leakage_audit.md, label_audit.md, known_issues.json,
  modality_selection.json, nested_splits.json, gates.json, storage_actual.md,
  validation.json, output_manifest.json in the same audit directory.
- Acquisition run: runs/reassemble/20260927T134437Z.
- Corrected full audit: runs/reassemble/20260927T141645Z-inventory.
- Full metadata: records/*.json and recordings.parquet / segments.parquet in full run.
- Successful aggregate reports/tables: reports_v2/ and tables_v2/ in full run.
- Portable input identities and final implementation hashes: input_manifest.json
  and final_provenance.json in full run. Bulk checkpoints/Parquet remain local, ignored.
- Dataset DOI: 10.48436/0ewrv-8cb44.
- Official reference: https://github.com/TUWIEN-ASL/REASSEMBLE at
  432cc15ce3e028edc2f98a786f28bf6baf31ac6f; reference only, no runtime dependency.

## Exact next action

Researcher reviews the final gate report, cohort exclusions, audio limitation and
nested splits, then approves the next phase. Only afterward implement the specified
baselines and independent-signal/permutation gates before fusion. Do not treat
GO FOR REASSEMBLE MODELLING as evidence of predictive signal or training approval.
AGENTS.md says: “At each phase boundary, report changed files, git diff --stat,
checks performed, unresolved issues, and the exact next action; then wait for approval.”

No further acquisition or inventory run is needed. To independently regenerate
aggregate reports if requested, choose fresh output directories (example):

```bash
ma_thesis_env/bin/python -B scripts/reassemble/02_audit.py \
  --run-dir runs/reassemble/20260927T141645Z-inventory \
  --output-dir runs/reassemble/20260927T141645Z-inventory/reports_review_01 \
  --derived-dir runs/reassemble/20260927T141645Z-inventory/tables_review_01
ma_thesis_env/bin/python -B -m pytest -q tests/reassemble
ma_thesis_env/bin/python -B -m pip check
git diff --check
```

Never regenerate into existing evidence paths. Final validation/storage additions
in the published report supplement the generated reports_v2; validation.json records
the checks separately. A clean independent reproduction has not been performed.

## Corrections and retained history

The pilot hand-audio header overestimated duration; final inventory counts decoded
samples to EOF, with regression coverage. Pilot JSON remains only in acquisition
run and is excluded from final aggregates. Official defect exclusions apply to the
last manipulation, not a trailing idle annotation. Physical sensor defects are
conservative official-warning masks, not claimed independent diagnoses.
The initial report attempt needed optional tabulate; a dependency-free formatter
resolved this without environment changes. Original partial outputs remain intact.
See AUDIT_METHODS.md for these corrections and alignment/quality limits.

The additive checkpoint is titled `feat: acquire and audit REASSEMBLE Study 2 prerequisites`.
Use git log to identify it. Earlier unrelated Intel and storage-triage files remain
unstaged; never sweep them into this checkpoint. PHM history is preserved.
