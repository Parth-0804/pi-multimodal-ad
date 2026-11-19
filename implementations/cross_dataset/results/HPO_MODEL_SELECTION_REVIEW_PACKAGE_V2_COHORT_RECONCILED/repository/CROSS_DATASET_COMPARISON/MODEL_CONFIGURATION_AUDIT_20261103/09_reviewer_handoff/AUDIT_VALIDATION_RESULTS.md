# Audit validation results

Validated: 2026-11-03T18:05:27.714065+00:00.

- All required reports/tables are present (final list checked below).
- 6,070 original evidence inputs rehashed: SHA256s unchanged; no conflicting input hashes across extraction ledgers.
- All4,920 binary candidates were fully hashed at audit discovery; all retain identical size and mtime at the end. Important fitted/source inputs above were rehashed. Full secondary6-minute binary rehash was not repeated.
- 763 independent saved-prediction/history/hash checks passed;94 additional split/native-label checks passed. No training/inference replay was performed.
- All CSV rows parse; JSON/JSONL documents parse; all11 PNG figures decode; 285 local Markdown links resolve. Exact row counts are in OUTPUT_CSV_ROW_COUNTS.csv.
- 7,969 unique configuration/run IDs;7,929 COMPLETE/40 REUSED,with174 completed legacy calls inferred from aggregate/source control flow. All required configuration keys are retained,including explicit unknowns.
- 281,268 numeric metric rows have a HELD-OUT scope. This includes recorded aggregate/subgroup/robustness/seed-summary rows; it is not a count of independent model evaluations. Complete long metrics contain587,101 rows,including epochs and intervals.
-360 official Handover validation rows are explicitly VALIDATION OFFICIAL,not inner OOF.
- All10 MSM review-table AP values agree with the saved primary mean-seed pooled summary (absolute tolerance1e-12). Mean-fold AP is separately retained in AP_AGGREGATION_RECONCILIATION.csv.
- CPU-only audit tests: see PYTEST_RESULTS.txt. All test fixtures are synthetic and remain inside the new audit folder.
- Work-state compression was round-trip SHA256-verified; only redundant scratch JSON created by this audit was replaced by gzip. Required CSV/JSON configuration/metric data were not truncated.
- Git HEAD remains eb3888f5d23310aa097dbb1be14605e931190b4a. No staging,commit,push or changes to historical evidence were performed. Existing unrelated changes remain documented.

## Command outcomes

- `git rev-parse HEAD`: 0; output `provenance/GIT_HEAD_AT_END.txt`.
- `git status --short --branch --untracked-files=all`: 0; output `provenance/GIT_STATUS_AT_END.txt`.
- `git diff --stat`: 0; output `provenance/GIT_DIFF_STAT_AT_END.txt`.
- `git diff --check`: 0; output `provenance/GIT_DIFF_CHECK.txt`.
- `/home/student/Master_Thesis_WS/pi-multimodal-ad/ma_thesis_env/bin/python -B -m pip check`: 0; output `provenance/PIP_CHECK.txt`.
- `nvidia-smi --query-gpu=index,name,uuid,memory.total,memory.used,utilization.gpu,driver_version --format=csv`: 0; output `provenance/GPU_RESOURCE_SNAPSHOT.txt`.
- `ps -u 1001 -o pid,comm,etimes`: 0; output `provenance/USER_PROCESS_SNAPSHOT.txt`.

## Audit test output

```text
...............................                                          [100%]
31 passed in 3.08s
```

## Limits

Readability and hash checks do not certify missing participant/tool/session identities,unrecorded optimizer states,unlogged/deleted historical fits or pristine assessment after research post-selection. No expensive feature extraction or model replay was performed. Legacy PHM source-flow-inferred fits have no per-fit epoch/state receipt. Historical total GPU-hours are NOT RECORDED. The audit is uncommitted.
