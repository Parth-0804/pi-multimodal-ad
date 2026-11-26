# Completed protected-root relocation — 26 November 2026

All eleven explicitly approved source groups are now physically under
`implementations/`; none of their old roots remains. The researcher approved the
exact location-only exception in [APPROVAL.json](APPROVAL.json). The earlier
[assessment](../README.md) remains historical evidence of the approval boundary.

## Executed movements

| Previous location | Canonical physical location |
|---|---|
| `HANDOVER/01_raw_dataset/` | `implementations/HANDOVER/01_raw_dataset/` |
| `REBOOT/01_raw_dataset/` | `implementations/REBOOT/01_raw_dataset/` |
| `REBOOT/runs/` | `implementations/REBOOT/runs/` |
| `VIFAILBACK/` | `implementations/VIFAILBACK/` |
| `MILLING DATASET/` | `implementations/MSM/experiments/legacy/` |
| `CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE/10_Visual_And_Sensor_Examples/` | `implementations/cross_dataset/results/INDEPENDENT_REVIEW_PACKAGE/10_Visual_And_Sensor_Examples/` |
| `DATASET_RESEARCH/VIFAILBACK_VERIFICATION/` | `implementations/VIFAILBACK/02_dataset_verification/independent_verification/` |
| `DATASET_RESEARCH/NEW_DATASET_SELECTION_20261028/source_evidence/` | `implementations/general/docs/dataset_research/NEW_DATASET_SELECTION_20261028/source_evidence/` |
| `26.10.2026_feedback_experiments/` | `implementations/REASSEMBLE/experiments/cnn_seed_stability/phase1_feedback/` |
| `parth_ws_bootstrap/` | `implementations/REASSEMBLE/experiments/bootstrap/` |
| `experiments/exp_a_initial_eda_r1_r3_r5/` | `implementations/PHM2026/experiments/exp_a_initial_eda_r1_r3_r5/` |

The [operation result](preflight_20261126T194611571870Z/APPLY_STATUS.json) records
38 same-filesystem renames, 15 verified browsing-proxy removals and 12 empty source
container removals. Two necessary destination parents were created. All **90,183
regular files** preserved their device, inode, size, mode and modification time;
no raw or result payload was read, hashed, copied, rewritten or deleted. Original
README/ignore-file collisions were preserved without overwriting independent
files. The original ViFailback workspace README is now
`implementations/VIFAILBACK/docs/WORKSPACE_BEFORE_CONSOLIDATION.md`.

The move repaired 11 links, including MSM's previously broken native-input link,
Handover's study input link, eight bootstrap-cache links and ViFailback's latest
analysis link. A separate [bounded repair](BROWSING_LINK_VALIDATION.json) restored
16 pre-existing broken core REASSEMBLE browsing links to the retained result files
identified by the reviewed historical run mapping. Their target metadata remained
unchanged; [original link text](BROWSING_LINK_REPAIRS_BEFORE.json) and an append-only
[journal](BROWSING_LINK_ACTIONS.jsonl) support reversal.

## Preservation, paths and scientific limits

- [REASSEMBLE verification](reassemble_adapter/POST_MOVE_VALIDATION.json): all 62
  selected frozen source/configuration/identity/stop-record hashes match; all 20
  configured path destinations and historical-key roundtrips pass.
- [ViFailback verification](vifailback_adapter/POST_MOVE_SOURCE_IDENTITIES.json):
  original identity functions match all 31 original, five reused REASSEMBLE and
  11 matched-study source/configuration entries, plus the frozen protocol hash.
- The [REASSEMBLE context](reassemble_adapter/README.md) and
  [ViFailback context](../../../../../VIFAILBACK/relocation/README.md) are additive.
  Frozen source, configuration, manifests and stop records retain their bytes.
  Each participating Python interpreter needs explicit activation; old shell and
  controller commands are not certified for direct replay.
- The pre-existing bootstrap AGENTS.md hash mismatch remains enforced. The two
  other policy files were [restored to their original bytes](POLICY_RESTORATION.json)
  after checking the preserved preimages.
  [Other legacy consumer limits](vifailback_adapter/LEGACY_CONSUMER_LIMITS.md)
  distinguish already-stale source/result paths from moved raw paths, including
  plain-string third-party I/O and child-process boundaries. No scientific replay,
  cache reconstruction, fitting, inference, preprocessing or resumption occurred.
- The current read-only `reassemble/cache_preflight.py` received a separate path
  repair for repository discovery and preserved prefix-manifest names. Its
  [preimage](preimages/implementations/REASSEMBLE/src/reassemble/cache_preflight.py)
  distinguishes this later utility change from historical experimental code.

## Validation and navigation

The [five move-tool tests](SELFTEST_RESULTS.json) cover conflict refusal, source
identity drift, ignore exposure, alternate-worktree policy and complete synthetic
apply/reversal. Six shared-adapter tests, seven ViFailback adapter tests and seven
cache-checker tests use tiny synthetic files only. Saved source checks are not
model reproduction.

The exact preflight and final policy checks found **zero ignored-to-exposed files**
and no destination ignore mismatches. Canonical raw/source exclusions and local
inventory/test-work exclusions are explicit in `.gitignore`. No new publication
allow-list, staging, commit, tag, push or access change occurred.

Current README/navigation, dataset guides, thesis-to-code browsing links and
active policy path guidance now point to canonical locations. Earlier manifests,
scientific reports and source snapshots keep historical identities; use this move
map and earlier mappings when interpreting them. The four absent historical
`docs/thesis_research_direction/` authority links in AGENTS predate this move and
are not fabricated or silently replaced.

The ten latest chapter files, including the citation cleanup, and the submitted
71-page review PDF are guarded by [MANUSCRIPT_GUARD.json](MANUSCRIPT_GUARD.json).
The [final integrated validation](VALIDATION.json) records these checks, current
link checks, source preservation, Git state and remaining execution limits.
No PDF was compiled, generated or previewed.

## Root resources retained

`00_thesis_writing_tracking/` holds writing/review material and `implementations/`
holds dataset work. Root `docs/` contains the requested thesis-code map and three
policies; `src/` contains four required packaging links. README, REPO_MAP, AGENTS,
license and packaging/dependency files remain at the root. The existing ignored
`ma_thesis_env/` has location-dependent executables and was left in place; private
ignored local state was not opened. These are operational resources, not remaining
dataset workspaces.

## Recovery and handoff

[PLAN.json](preflight_20261126T194611571870Z/PLAN.json) and
[ACTIONS.jsonl](preflight_20261126T194611571870Z/ACTIONS.jsonl) bind exact operations
to metadata identities. Large per-file before/after inventories and generated
synthetic repositories remain local/ignored. [RELOCATE.py](RELOCATE.py) refuses
replay of an applied plan. Its recovery path checks successful identities and
original-path vacancy, refusing conflicts; it must never overwrite later work.
The later browsing-link repairs have their own original-text journal. This is a
retention/recovery record, not authorization for another move or experiment.

[Scoped documentation and utility diff](PHASE_EDITS.diff) separates this phase
from pre-existing thesis and repository changes. [Tracked diff statistics](TRACKED_DIFF_STAT.txt)
include earlier unstaged moves: apparent old-path deletions have corresponding
untracked canonical files and are not a scientific-deletion claim. Publication
review remains pending; no commit or push was requested or performed.
