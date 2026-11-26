# Model-audit and Handover root cleanup — 2026-11-26

This is the completed nonraw portion of the researcher-requested root cleanup.
No commit, push, model run, evaluation, download or raw-data relocation was performed.

| Original location | Current location | Operation |
|---|---|---|
| `CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/` | `implementations/cross_dataset/results/MODEL_CONFIGURATION_AUDIT_20261103/` | Same-filesystem directory rename |
| `HANDOVER/experiments/common_support_v2/01_raw_dataset` | `implementations/HANDOVER/experiments/common_support_v2/01_raw_dataset` | Browsing symlink moved and retargeted to the same raw directory |
| `HANDOVER/experiments/common_support_v2/`, `HANDOVER/experiments/` | Removed | Both containers checked empty immediately before removal |

The audit's 191 filesystem nodes, including 170 regular files, retained their
device, inode, size, mode and modification time immediately after the rename.
Its two synthetic-test convenience links were repaired to relative targets.
All 169 scientific/report/other regular files remain unchanged by metadata;
`audit_utilities/discover.py` received only repository-root discovery repair.
Its complete original bytes are retained under `preimages/audit_utilities/`.
This metadata check does not claim a new content-hash audit or reproduction.

The Handover raw tree was not moved, renamed, read or edited. Its new study link
resolves to the same original `HANDOVER/01_raw_dataset/` device/inode identity.
Only the link and verified empty ordinary containers changed.

Historical machine-readable paths and frozen source references remain evidence
of their original locations. The audit's older source references already include
paths changed by previous restructuring; audit replay was not run or certified.

[Action journal](ACTIONS.jsonl), [before metadata](METADATA_BEFORE.json),
[after metadata](METADATA_AFTER.json) and [validation](VALIDATION.json) record
exact operations and checks. Current cross-dataset and Handover navigation was
updated, with preimages retained here. No other root policy or guide was edited
by this scoped operation.
