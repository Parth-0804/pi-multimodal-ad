# Researcher handoff

Audit `20261028T115408Z` · 2026-10-28T12:54:08+01:00. Read-only assessment; no cleanup or downloads initiated by this audit. Concurrent REBOOT work is identified separately. GB/MB are decimal; GiB/MiB are binary. Directory sizes are allocated blocks, with hard links counted once per subtree and symlinks not followed.

| Requested conclusion | Assessment |
| --- | --- |
| Total filesystem capacity | 531.415 GB (494.919 GiB) |
| Current filesystem free | 53.503 GB (49.829 GiB); quota unverified |
| Project total | 101.674 GB (94.691 GiB); includes .git and environment |
| Five largest directories | data 26.939 GB; HANDOVER 17.335 GB; .git 15.899 GB; runs 9.102 GB; 00_experiments 7.235 GB |
| Verified duplicates | 3 fresh SHA-256 independent-copy pairs; 11,682 inode-confirmed hard-link pairs. Same-size fold checkpoints were different. |
| High-confidence recovery | 0.500 MB from pytest and 28 source-matched bytecode files |
| Conditional recovery | 2.549 GB (2.374 GiB); export ZIP, tutorial weight, two CNN caches and migration cache |
| Must preserve | 99.073 GB project remainder plus 330.622 GB external REASSEMBLE; also preserve UNKNOWN 0.052 GB pending lineage review |
| REBOOT recommendation | Use selected tasks/episodes/one RGB view and required numerical/native annotation files; 15 GiB reserve; whole 35–40 GB tasks exceed conservative 40–50 GB working budget |
| Changes made | Only new small audit reports/provenance; 0 bytes reclaimed; no data downloads, existing-file edits, staging or commits |

## Ten largest file paths

| Rank | Project-relative path | Logical size | Link note |
| --- | --- | --- | --- |
| 1 | .git/objects/pack/pack-387b3e682db456570101dff70e3fd01da5acace0.pack | 13.773 GB | Git history |
| 2 | HANDOVER/01_raw_dataset/official_dataset/archives/training_set.tar.gz | 9.186 GB |  |
| 3 | HANDOVER/01_raw_dataset/official_dataset/archives/training_set.tar.gz.part | 9.186 GB | Same inode as completed archive; 0 extra data blocks |
| 4 | HANDOVER/01_raw_dataset/official_dataset/archives/test_set.tar.gz | 2.212 GB |  |
| 5 | HANDOVER/01_raw_dataset/official_dataset/archives/test_set.tar.gz.part | 2.212 GB | Same inode as completed archive; 0 extra data blocks |
| 6 | .git/objects/pack/pack-76b8428a038adbd19dc55cc7f55d5e15c9cc41be.pack | 1.797 GB | Git history |
| 7 | HANDOVER/01_raw_dataset/official_dataset/archives/val_set.tar.gz | 1.553 GB |  |
| 8 | HANDOVER/01_raw_dataset/official_dataset/archives/val_set.tar.gz.part | 1.553 GB | Same inode as completed archive; 0 extra data blocks |
| 9 | CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE/INDEPENDENT_REVIEW_PACKAGE.zip | 1.170 GB |  |
| 10 | ma_thesis_env/lib/python3.12/site-packages/nvidia/cu13/lib/libcublasLt.so.13 | 0.542 GB |  |

`LARGEST_FILES.csv` contains all 100 full paths, exact byte/block sizes, formats, dates, Git status and purpose evidence. The nine requested reports are linked below; `AUDIT_PROVENANCE.json` additionally contains commands, configuration, input identities, warning limits and output checksums.

- [PROJECT_STORAGE_OVERVIEW.md](PROJECT_STORAGE_OVERVIEW.md)
- [COMPLETE_DIRECTORY_STRUCTURE.md](COMPLETE_DIRECTORY_STRUCTURE.md)
- [LARGEST_FILES.csv](LARGEST_FILES.csv)
- [DATASET_STORAGE_BREAKDOWN.md](DATASET_STORAGE_BREAKDOWN.md)
- [EXPERIMENT_ARTIFACT_AUDIT.md](EXPERIMENT_ARTIFACT_AUDIT.md)
- [DUPLICATE_FILE_CANDIDATES.csv](DUPLICATE_FILE_CANDIDATES.csv)
- [POTENTIAL_SPACE_RECOVERY.md](POTENTIAL_SPACE_RECOVERY.md)
- [REBOOT_STORAGE_FEASIBILITY.md](REBOOT_STORAGE_FEASIBILITY.md)
- [RESEARCHER_HANDOFF.md](RESEARCHER_HANDOFF.md)

## Review limits and exact next action

Active controller PID 2691799 and training PID 2823659 were left running; workers were observed reading sibling REASSEMBLE encoded videos. Free space and output sizes can change. No quota was established, no full scientific reproduction or archive-integrity scan ran, and the snapshot does not prove future safe capacity. October’s 66.9 GiB cache eviction and September’s PHM retirement are already reflected in current storage and excluded from recovery.

`git diff --check` and environment `pip check` passed. Audit artifact validation and metadata preservation checks are recorded in the provenance. The pre-existing tracked diff remains 3 files / 22 insertions; generated files here are untracked audit additions, not included by `git diff --stat`. Independently review the classifications and precise dependencies before proposing any named cleanup. This audit stops here and authorizes no deletion.

Concurrent REBOOT work grew its footprint to 3.590 GB while this audit ran. This final snapshot supersedes `STORAGE_AUDIT/20261028T114917Z/` for capacity and largest-file figures. The audit initiated no payload downloads. Recorded numerical-column ranges support a depth-optional pilot without full expert Parquet downloads; reuse remains subject to source/layout verification.
