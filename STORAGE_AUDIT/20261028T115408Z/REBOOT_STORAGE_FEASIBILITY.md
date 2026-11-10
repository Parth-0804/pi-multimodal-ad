# REBOOT storage feasibility

Audit `20261028T115408Z` · 2026-10-28T12:54:08+01:00. Read-only assessment; no cleanup or downloads initiated by this audit. Concurrent REBOOT work is identified separately. GB/MB are decimal; GiB/MiB are binary. Directory sizes are allocated blocks, with hard links counted once per subtree and symlinks not followed.

A 35 GB repository can fit the measured filesystem headroom after the reserve if no competing growth occurs; a fresh 40 GB repository cannot. Neither fits a conservative 40–50 GB total working allowance with a 15 GiB reserve. Some hosted repositories are much smaller. The working-budget calculation assumes that the stated 40–50 GB allowance covers all REBOOT inputs/outputs plus reserve, including the current pilot footprint; if it is a download-only allowance, the budget conclusion changes. No operating-system quota was verified.

## Capacity calculation

| Item | Measured fact or explicit planning assumption |
| --- | --- |
| Current filesystem availability | 53.503 GB (49.829 GiB) |
| Current REBOOT workspace | 3.590 GB (3.344 GiB); created by concurrent pilot work |
| High-confidence potential recovery | 0.500 MB; not executed |
| Availability after that recovery | 53.504 GB (49.829 GiB) |
| Conditional additional recovery | 2.549 GB (2.374 GiB); requires gates, not executed |
| Availability after all proposed recovery | 56.052 GB (52.203 GiB) |
| Recommended minimum reserve | 15 GiB = 16.106 GB; planning assumption for live checkpoints, transfer/processing scratch and concurrent growth |
| Filesystem additional-download headroom after only high-confidence recovery | 37.398 GB (34.829 GiB) |
| After conditional recovery too | 39.946 GB (37.203 GiB) |
| Additional budget-capped payload at 40 GB total allowance | 20.304 GB |
| Additional budget-capped payload at 50 GB total allowance | 30.304 GB |
| 35–40 GB whole repository | 35 GB physically fits narrowly; 40 GB does not with reserve. Both exceed conservative budget-capped payload. |
| Suggested bounded total REBOOT workspace | 10 GB initially, including existing pilot and new derivatives; about 6.410 GB remains before that cap |

The reserve is a floor, not a measured upper bound on the running job’s future writes. Do not promise a complete-task download while that growth and the quota remain unbounded. Recovery is small compared with full-task sizes and does not remove the need for selection under the working-budget assumption. A small task may fit in full; the entire collection does not. Exact remaining transfer bytes depend on the verified union of files already held for the chosen task; the existing pilot spans multiple repositories, so its full size must not be blindly subtracted from any one remote task.

## Measured remote inventory, not downloaded payload

The existing pinned public file-tree snapshots under `REBOOT/runs/20261028T113139848361Z-independent-feasibility-v1/evidence/file_trees/` describe 38 repositories totalling approximately 1,014.416 GB. These are sums of stored remote file-size metadata, not local payload usage, a new payload download, or a current guarantee for changing `main` branches. Pins are recorded below.

| Pinned repository | Episodes | Whole files | data/ Parquet | All RGB MP4 | cam_low only | Revision |
| --- | --- | --- | --- | --- | --- | --- |
| REBOOT26/16mm-cylinder_remove | 60 | 17.733 GB | 16.378 GB | 1.355 GB | 0.225 GB | 76aad32aa7aea67cadedd32c3ee57b21dfffd0ce |
| REBOOT26/M12-fastener_install | 60 | 34.001 GB | 31.338 GB | 2.663 GB | 0.508 GB | ab113d36c392c9f4ce1c397e56e22f07c3f6ae7d |
| REBOOT26/rj45-install | 63 | 38.518 GB | 35.510 GB | 3.007 GB | 0.464 GB | 1b5f443c62c70677610d06d7d223b830d090b884 |
| REBOOT26/16mm-bar_recovery_remove | 18 | 5.402 GB | 4.986 GB | 0.416 GB | 0.066 GB | 598b665d6e70f99050f4bbd64a7297b3ac2603a6 |

Four-view RGB selection is supported by separate `videos/observation.images.cam_{high,low,left_wrist,right_wrist}/` paths. Parquet is ~92% of the large examples, so excluding RGB cameras alone does not substantially shrink them. The concurrent pilot’s numerical-acquisition receipts identify four depth columns in expert Parquet, plus joint states/actions/timestamps; the sample recovery files instead list compact numerical-only schemas. No force/torque channel is established. This audit read those receipts, not the payload schemas independently.

The existing `REBOOT/03_video_sensor_alignment/NUMERICAL_ACQUISITION_MANIFEST.json` records 2 expert episodes extracted with exact HTTP 206 column-page/footer ranges: 225,771 transferred bytes for numerical projections from 1,078,422,618 bytes of depth-heavy source files. It also records eight fully downloaded small sample-recovery Parquet files. These concurrent receipts establish a practical selective-column route for those pinned examples; the storage audit did not execute or independently replay those transfers. The range fragments have recorded SHA-256 identities, but the original whole expert files were not downloaded or globally hash-verified. Filename filters alone cannot omit depth embedded in Parquet. Validate each repository/schema and preserve fragment/projection provenance before expanding this method.

## Concrete selective acquisition strategy for later approval

1. Keep task/revision, release card, `meta/info.json`, episode metadata, task definitions and every available native annotation/provenance file. Select a task and paired expert/recovery conditions based on the research question, with episode/group criteria fixed before looking at outcomes. Repository names such as “recovery” are not frame-level failure labels.
2. Use the episode metadata to choose required data shards and camera-video chunks. In the already-present `16mm-cylinder_remove` metadata, all 60 episodes map to 60 distinct Parquet data files. Episodes 0–2 map to data files 0–2 but share video file 0 at consecutive time offsets. Thus selected episode files reduce data transfer, while selected video chunks can still contain other episodes. Do not assume this mapping is identical for every repository.
3. Start with a few episodes from a small number of scientifically relevant tasks, one RGB camera, numerical states/actions/timestamps and native annotations. Budget the sum of the exact union of selected file sizes, not average episode length or a linear fraction of the whole task. The entire cylinder-remove Parquet plus cam_low is about 16.60 GB before tiny metadata, whereas the whole repository is 17.73 GB; episode selection has more effect than camera selection alone.
4. Treat depth as optional unless required scientifically. Reuse the demonstrated bounded column-page/footer method only after validating the selected repository layout, or use an official numerical-only export. Pin client/code version and validate types/timestamps. Save complete source/revision/column-selection and episode-offset manifests; never silently strip annotations.
5. Consider streaming bounded selected columns/frames when supported. Apply a strict cache limit and one reviewed destination; avoid an unbounded Hub cache plus copied local dataset and expanded frame cache. Decode frames on demand and keep compact numerical/CNN outputs in a new versioned run. Recheck free space and exact file-list bytes immediately before any future authorized transfer.

The official project describes phase/mode annotations. The concurrent `REBOOT/02_labels_and_annotations/LABEL_GATE_SUMMARY.json` reports one repository with released phase-annotation files and 60 native records, but zero strictly eligible binary training examples and zero verified matched pairs. This audit did not independently adjudicate those labels. Empty annotation-filename matches in other repository trees do not prove missing table fields. Preserve native records and resolve label alignment before treating storage feasibility as scientific readiness.

Public sources checked during this audit: the [official REBOOT project](https://nanayawoa.github.io/REBOOT/) describes the multimodal release; [LeRobot v3 format documentation](https://huggingface.co/docs/lerobot/lerobot-dataset-v3) explains shared-file episode offsets and streaming; [Hub download documentation](https://huggingface.co/docs/huggingface_hub/guides/download) documents revision pins and filename allow/ignore filters. The pinned Hugging Face dataset pages/API could not be opened through the web tool; size claims therefore rely on existing local pinned API snapshots and receipts, not a claimed fresh remote size verification. No REBOOT payload, model weight or episode was downloaded by this audit.

## Existing pilot and audit boundary

The final inventory contains 3.590 GB under REBOOT, including downloaded pilot videos and numerical inputs from a separate concurrent workflow. An earlier storage snapshot saw metadata only. This final report includes the new footprint and the receipts as research evidence; no payload acquisition, projection, decoding or gallery generation was initiated by the storage audit. The earlier storage snapshot is retained under `STORAGE_AUDIT/20261028T114917Z/`.
