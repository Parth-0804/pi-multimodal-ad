# PHM raw retirement report

Completed 2026-09-27T13:36:14.932333+00:00. **D1 PASS; D2 PASS; retirement successful.**
The user's controlled-retirement instruction expressly authorized this one raw
tree after recovery verification, superseding the normal immutable-data rule
for this operation only.

## Deletion and measured storage

Exact deletion target: `/home/student/Master_Thesis_WS/pi-multimodal-ad/gtc-data-experiment`.
The target was resolved immediately before removal, was not a symlink, had no
nested mounts, and matched the gated device/inode and all frozen file metadata.
Only this tree was recursively removed; its absence was verified afterward.

| Measurement | Value |
|---|---:|
| Raw logical bytes | 381,481,909,715 |
| Raw allocated bytes | 381,482,188,800 (355.283 GiB) |
| Deleted regular files | 53 |
| Free immediately before | 51,630,166,016 bytes (48.084 GiB) |
| Free immediately after | 433,112,154,112 bytes (403.367 GiB) |
| Measured free-space increase | 381,481,988,096 bytes (355.283 GiB) |
| Subsequent storage recheck | 403.367 GiB available |

The 53 files comprise 52 official ZIP archives and the local helper
`inspect_dataset.py`. Before deletion the helper was preserved byte-for-byte as
tracked `scripts/phm2026/legacy_inspect_dataset.py`; recovery restores its
historical location from that copy. No research code was lost. Small differences
between allocated bytes and measured capacity gains reflect concurrent filesystem
activity. Exact measurements: [execution](retirement_execution.json) and
[storage commands](post_retirement_storage.json).

## Reproducible recovery

- Tracked root entry point: `download.py`.
- Implementation: `src/pi_multimodal_ad/acquisition/phm_download.py`.
- Recovery specification: `configs/phm2026/download_manifest.json` (53 entries).
- Frozen full-file SHA256 manifest: [JSON](raw_data_manifest.json) and
  [CSV](raw_data_manifest.csv), covering all 53 former raw-tree files.
- Raw JSON manifest SHA256: `669b5c897662d0f33ed8800fab57db630ee87a5c8ed2345517079c84f6d8662f`.
- Instructions: [RAW_DATA_RECOVERY.md](../../docs/phm2026/RAW_DATA_RECOVERY.md).
- Initial tooling commit: `d634251`; final pre-deletion checkpoint:
  `78394d7f9349f5f6858dabe1f3a796a48911bb57` (CSV line-ending normalization only).

The official [PHM Society challenge page](https://data.phmsociety.org/phm-north-america-2026-conference-data-challenge/)
resolved at validation time to the public training share
[gtc-data.synology.me:51111/sharing/uIrAvzqEh](https://gtc-data.synology.me:51111/sharing/uIrAvzqEh).
The downloader resolves the Training Data link at runtime and supports an
explicit HTTPS share override. Discovery uses the public sharing API and exact
server-returned paths, with TLS verification enabled and no embedded credentials.
The 52 official archive paths and sizes matched. The additional helper comes
from tracked repository code. Historical destination names are preserved.

High-frequency coverage is A runs 1–5, B runs 1–7 and F runs 1–8. Each experiment
also retains one condition-indicator archive and one oil/environment archive;
photo archives number 7, 9 and 10 respectively. No duplicate removal or scientific
label changes were made.

## Validation evidence and limits

- Offline downloader suite: **22 passed**, using
  `ma_thesis_env/bin/python -B -m pytest -q tests/unit/test_phm_download.py`.
- Live `--help`, `--list`, and A/B/F `--dry-run`: exit 0.
- Exact recovery coverage: **53/53**, including the preserved helper.
- Real HTTP Range test: **206**, **1,048,576 bytes** from EXP-A Run 1;
  fragment SHA256 matched the local archive prefix. The fragment was bounded
  in memory and left no disk payload. Full raw-file SHA256 values were computed
  locally before removal.
- Post-deletion A/B/F dry run: exit 0; **53/53 MISSING / AVAILABLE FOR DOWNLOAD**,
  zero payload bytes downloaded, raw root remains absent. See
  [post-deletion invocation](downloads/20260927T133707284347Z-4aa6a583.json).
- `git diff --check` passed; repository environment `pip check` passed.

This validates the user-prescribed recoverability gate, not a full 355 GiB
round-trip redownload. Future downloads verify every expected size and SHA256;
continued recovery depends on official-source availability and unchanged content.
See [D1 evidence](recovery_validation.json), [CLI checks](cli_validation.json),
and [final D2 gate](retirement_gate_D2.json). D1 evidence records the earlier
pre-checkpoint D2 state; the separate final D2 record is authoritative for deletion.

## Research preservation and next phase

All **68,745** pre-existing protected files passed existence, size, nanosecond
mtime and mode checks against the pre-operation snapshot. This is metadata
verification, not a second full content hash of research outputs. Retained items
include all 17 `runs/phm2026_*` directories, RT-DETR checkpoints/results,
PatchTST results, target artifacts, raw-vibration derived material, historical
experiments, thesis figures/tables, code, documentation, environment and scratch.
The historical 14,047,735,808-byte Git blob remains present. No Git history
rewrite, pruning or garbage collection occurred. See
[preservation evidence](retained_artifact_verification.json).

REASSEMBLE decision: **PREFERRED STORAGE PASS** (403.37 GiB free,
threshold 200 GiB). See the
[dated storage preflight](../reassemble/audits/STORAGE_PREFLIGHT_AFTER_PHM_RETIREMENT_20260927T133716Z.md).
No PHM redownload or REASSEMBLE download/training was started. The next action is
a separately authorized REASSEMBLE acquisition phase. Existing unrelated audit
files remain untouched and outside this operation's commits.

PHM RAW DATA RETIRED — REPRODUCIBLE RECOVERY VERIFIED — REASSEMBLE STORAGE GO
