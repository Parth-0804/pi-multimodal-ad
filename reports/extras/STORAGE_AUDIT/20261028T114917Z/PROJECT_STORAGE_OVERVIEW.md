# Project storage overview

Audit `20261028T114917Z` · 2026-10-28T12:49:17+01:00. Read-only assessment; no cleanup or downloads. GB/MB are decimal; GiB/MiB are binary. Directory sizes are allocated blocks, with hard links counted once per subtree and symlinks not followed.

| Measured item | Value |
| --- | --- |
| Actual project | /home/student/Master_Thesis_WS/pi-multimodal-ad |
| Filesystem | /dev/sda1 (df alias /dev/root), ext4, mount /; device 2049 |
| Total capacity | 531.415 GB (494.919 GiB); 531,415,142,400 bytes |
| Used filesystem blocks | 474.224 GB (441.656 GiB) |
| Available to filesystem caller | 57.174 GB (53.248 GiB); 57,174,077,440 bytes |
| Project allocated total | 98.107 GB (91.370 GiB); 98,107,322,368 bytes |
| Project apparent total (unique inodes, including directory metadata) | 97.450 GB (90.758 GiB) |
| .git allocated | 15.899 GB (14.807 GiB) |
| Referenced external REASSEMBLE root | 330.622 GB (307.916 GiB) |
| Filesystem used less project | 376.117 GB (350.286 GiB) |
| Unassigned residual after project and external REASSEMBLE | Approximately 45.495 GB (42.370 GiB) |
| Free inodes | 66431017 |
| User quota | UNVERIFIED: quota executable unavailable; mount options list no quota setting. Storage budget is not a measured quota. |

The residual is arithmetic, not a scan of other directories: it includes uninspected files, filesystem metadata, possibly open-unlinked files and snapshot/timing differences. The named sibling dataset alone was measured outside the project. No unrelated user directories, user-level caches, credentials, process arguments, environment values or private session contents were opened. No cross-root hard-link identity census was made, so the residual is approximate.

Inventory scan: 2026-10-28T11:35:14.817273+00:00 to 2026-10-28T11:37:57.493644+00:00; 251,541 regular path entries, 26,041 subdirectories, 74 symbolic links, 11,682 hard-link pairs. No traversal errors. `du -x -B1 -s .` independently matched the metadata total exactly. Directory accounting includes hidden paths and does not follow symlinks. The top-100 CSV ranks logical file sizes; its rows must not be summed as reclaimable storage. 10 entries exceed 500 MB. Git internals carry “Not applicable (Git internal)” because worktree status is undefined there.

## Five largest project directories

| Path | Allocated | Regular file paths | Subdirectories |
| --- | --- | --- | --- |
| data | 26.939 GB (25.089 GiB) | 8,296 | 8,319 |
| HANDOVER | 17.335 GB (16.144 GiB) | 17,370 | 1,311 |
| .git | 15.899 GB (14.807 GiB) | 3,400 | 294 |
| runs | 9.102 GB (8.477 GiB) | 27,316 | 1,408 |
| 00_experiments | 7.235 GB (6.738 GiB) | 96,779 | 1,234 |

## Limits and checks

Active writers/readers mean measurements are a point-in-time audit, not an atomic snapshot or guaranteed future capacity. The live CNN job and its shared encoded-video cache remain protected. The initial broad Git-ignore check was stopped because it consumed excessive CPU; a subsequent bounded check successfully classified every nontracked top-100 worktree file. Only that audit helper was signalled. No experiment was interrupted.

`git diff --check` and the environment’s `python -B -m pip check` passed. No pytest/training/inference command was run for a documentation-only audit. Existing Git changes were preserved; nothing was staged or committed. The full provenance file records commands, versions, metadata checks, configuration, warning limits, source identities and report hashes.

Existing tracked diff (unrelated to this audit):

```text
 README.md                                              |  4 ++++
 REPO_MAP.md                                            |  6 ++++++
 docs/thesis_research_direction/THESIS_EVIDENCE_GAPS.md | 12 ++++++++++++
 3 files changed, 22 insertions(+)
```

All audit additions are under this unique timestamped directory. `git diff --stat` excludes untracked audit reports. The sole next action is independent researcher review; cleanup requires a separately scoped authorization.
