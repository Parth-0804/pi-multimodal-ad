# REBOOT storage feasibility

Audit `20261028T114917Z` · 2026-10-28T12:49:17+01:00. Read-only assessment; no cleanup or downloads. GB/MB are decimal; GiB/MiB are binary. Directory sizes are allocated blocks, with hard links counted once per subtree and symlinks not followed.

A 35–40 GB repository can fit the measured filesystem headroom if no competing growth occurs, but does not fit a conservative 40–50 GB total working allowance after reserving 15 GiB. Some hosted repositories are much smaller; selected tasks/episodes/files are the practical first step. The working-budget calculation assumes that the stated 40–50 GB allowance covers downloads plus reserve; if it is a download-only allowance, the budget conclusion changes. No operating-system quota was verified.

## Capacity calculation

| Item | Measured fact or explicit planning assumption |
| --- | --- |
| Current filesystem availability | 57.174 GB (53.248 GiB) |
| High-confidence potential recovery | 0.500 MB; not executed |
| Availability after that recovery | 57.175 GB (53.248 GiB) |
| Conditional additional recovery | 2.549 GB (2.374 GiB); requires gates, not executed |
| Availability after all proposed recovery | 59.723 GB (55.622 GiB) |
| Recommended minimum reserve | 15 GiB = 16.106 GB; planning assumption for live checkpoints, transfer/processing scratch and concurrent growth |
| Filesystem download headroom after only high-confidence recovery | 41.068 GB (38.248 GiB) |
| After conditional recovery too | 43.617 GB (40.622 GiB) |
| Budget-capped payload at 40 GB total allowance | 23.894 GB |
| Budget-capped payload at 50 GB total allowance | 33.894 GB |
| 35–40 GB whole repository | Physical fit is narrow; exceeds conservative budget-capped payload at either allowance |
| Suggested initial payload cap | 5–10 GB, including required Parquet shards and selected RGB chunks; retain reserve |

The reserve is a floor, not a measured upper bound on the running job’s future writes. Do not promise a complete-task download while that growth and the quota remain unbounded. Recovery is small compared with full-task sizes and does not remove the need for selection under the working-budget assumption. A small existing task may fit in full; the entire collection does not.

## Measured remote inventory, not downloaded payload

The existing pinned public file-tree snapshots under `REBOOT/runs/20261028T113139848361Z-independent-feasibility-v1/evidence/file_trees/` describe 38 repositories totalling approximately 1,014.416 GB. These are sums of stored remote file-size metadata, not local payload usage, a new payload download, or a current guarantee for changing `main` branches. Pins are recorded below.

| Pinned repository | Episodes | Whole files | data/ Parquet | All RGB MP4 | cam_low only | Revision |
| --- | --- | --- | --- | --- | --- | --- |
| REBOOT26/16mm-cylinder_remove | 60 | 17.733 GB | 16.378 GB | 1.355 GB | 0.225 GB | 76aad32aa7aea67cadedd32c3ee57b21dfffd0ce |
| REBOOT26/M12-fastener_install | 60 | 34.001 GB | 31.338 GB | 2.663 GB | 0.508 GB | ab113d36c392c9f4ce1c397e56e22f07c3f6ae7d |
| REBOOT26/rj45-install | 63 | 38.518 GB | 35.510 GB | 3.007 GB | 0.464 GB | 1b5f443c62c70677610d06d7d223b830d090b884 |
| REBOOT26/16mm-bar_recovery_remove | 18 | 5.402 GB | 4.986 GB | 0.416 GB | 0.066 GB | 598b665d6e70f99050f4bbd64a7297b3ac2603a6 |

Four-view RGB selection is supported by separate `videos/observation.images.cam_{high,low,left_wrist,right_wrist}/` paths. However, Parquet is ~92% of the two large examples. Excluding camera MP4s alone cannot turn a 34–39 GB task into a tiny numerical dataset. The pinned schema declares four depth features plus 14-dimensional joint-position states/actions. No force/torque channel is established by that schema. Depth may be embedded in the large Parquet shards: this is an inference from the feature schema and file layout, not a payload-schema inspection. Do not credit depth-exclusion savings until the physical Parquet schema and remote selective-column transfer are verified. A local column projection after downloading whole shards saves retained size, not transfer/peak-disk requirements.

## Concrete selective acquisition strategy for later approval

1. Keep task/revision, release card, `meta/info.json`, episode metadata, task definitions and every available native annotation/provenance file. Select a task and paired expert/recovery conditions based on the research question, with episode/group criteria fixed before looking at outcomes. Repository names such as “recovery” are not frame-level failure labels.
2. Use the episode metadata to choose required data shards and camera-video chunks. In the already-present `16mm-cylinder_remove` metadata, all 60 episodes map to 60 distinct Parquet data files. Episodes 0–2 map to data files 0–2 but share video file 0 at consecutive time offsets. Thus selected episode files reduce data transfer, while selected video chunks can still contain other episodes. Do not assume this mapping is identical for every repository.
3. Start with a few episodes from a small number of scientifically relevant tasks, one RGB camera, numerical states/actions/timestamps and native annotations. Budget the sum of the exact union of selected file sizes, not average episode length or a linear fraction of the whole task. The entire cylinder-remove Parquet plus cam_low is about 16.60 GB before tiny metadata, whereas the whole repository is 17.73 GB; episode selection has more effect than camera selection alone.
4. Treat depth as optional unless required scientifically. If depth shares Parquet shards with states, investigate bounded remote column/row-group reads or an official numerical-only export before promising a depth-free transfer. Pin client/code version and validate types/timestamps. Save complete source/revision/column-selection and episode-offset manifests; never silently strip annotations.
5. Consider streaming bounded selected columns/frames when supported. Apply a strict cache limit and one reviewed destination; avoid an unbounded Hub cache plus copied local dataset and expanded frame cache. Decode frames on demand and keep compact numerical/CNN outputs in a new versioned run. Recheck free space and exact file-list bytes immediately before any future authorized transfer.

The official project describes failure-phase/mode and phase-boundary annotations, but the stored file-tree `annotation_candidates` arrays are empty for the examples above. Filename searches do not prove annotations are absent or present inside tables. Their accessibility, schema and alignment must be established before an anomaly-label study. Preserve existing native metadata and do not infer labels from task names or lifecycle order.

Public sources checked during this audit: the [official REBOOT project](https://nanayawoa.github.io/REBOOT/) describes the multimodal release; [LeRobot v3 format documentation](https://huggingface.co/docs/lerobot/lerobot-dataset-v3) explains shared-file episode offsets and streaming; [Hub download documentation](https://huggingface.co/docs/huggingface_hub/guides/download) documents revision pins and filename allow/ignore filters. The pinned Hugging Face dataset pages/API could not be opened through the web tool; size claims therefore rely on existing local pinned API snapshots and receipts, not a claimed fresh remote size verification. No REBOOT payload, model weight or episode was downloaded by this audit.
