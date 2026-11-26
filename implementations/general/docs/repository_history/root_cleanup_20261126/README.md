# Root cleanup — 26 November 2026

> **Completed after explicit approval:** all eleven groups listed below were
> relocated on 26 November 2026. See the [completed operation receipt](approved_relocation/README.md).
> The assessment and pending-decision wording below are retained as the record
> presented for approval, not the current filesystem state.

The thesis consolidation is complete in its recorded scope. The broader physical
consolidation is **partially complete**. `implementations/` is not yet the exclusive
physical location of dataset and study material. This receipt records the latest
root-cleanup request, completed moves and the exact remaining decision; it does
not amend the data policy or imply that permission has already been given.

## Completed in this cleanup

| Previous location | Current physical location |
|---|---|
| `CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/` | `implementations/cross_dataset/results/MODEL_CONFIGURATION_AUDIT_20261103/` |
| `docs/maintenance/` | `implementations/REASSEMBLE/docs/maintenance/` |
| `HANDOVER/experiments/common_support_v2/01_raw_dataset` (link only) | `implementations/HANDOVER/experiments/common_support_v2/01_raw_dataset` |

The two empty old Handover experiment containers were removed. The physical
Handover raw directory did not move. The [audit/Handover receipt](model_audit_and_handover/README.md)
and [maintenance receipt](reassemble_maintenance/README.md) contain exact actions,
preimages and preservation checks. Current navigation and the cache checker's
**guide URL only** were updated. The cache checker was not run or certified;
its pre-existing historical path dependencies remain outside this small repair.
No source data, model fitting, inference, preprocessing, submitted PDF, manuscript
chapter, commit, tag, push or repository permission changed.

## Exact remaining physical locations

All source paths and descendants in the table are included in the proposed
location-only exception. These are **not executed moves**.

| Current source | Destination | Reason it remains |
|---|---|---|
| `HANDOVER/01_raw_dataset/` | `implementations/HANDOVER/01_raw_dataset/` | Protected native dataset |
| `REBOOT/01_raw_dataset/` | `implementations/REBOOT/01_raw_dataset/` | Protected native dataset |
| `REBOOT/runs/` | `implementations/REBOOT/runs/` | Feasibility records include acquired source payloads |
| `VIFAILBACK/` | `implementations/VIFAILBACK/` | Whole frozen workspace, acquired raw data and source-identity gates |
| `MILLING DATASET/` | `implementations/MSM/experiments/legacy/` | Legacy native data, retained staging and decoder; no dataset-version merging |
| `CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE/10_Visual_And_Sensor_Examples/` | `implementations/cross_dataset/results/INDEPENDENT_REVIEW_PACKAGE/10_Visual_And_Sensor_Examples/` | Native visual/sensor source examples |
| `DATASET_RESEARCH/VIFAILBACK_VERIFICATION/` | `implementations/VIFAILBACK/02_dataset_verification/independent_verification/` | Reports interleaved with original source evidence |
| `DATASET_RESEARCH/NEW_DATASET_SELECTION_20261028/source_evidence/` | `implementations/general/docs/dataset_research/NEW_DATASET_SELECTION_20261028/source_evidence/` | Acquired discovery/source evidence |
| `26.10.2026_feedback_experiments/` | `implementations/REASSEMBLE/experiments/cnn_seed_stability/phase1_feedback/` | Frozen derived study; path adapter and stopped-job preservation required |
| `parth_ws_bootstrap/` | `implementations/REASSEMBLE/experiments/bootstrap/` | Frozen derived study; path adapter and stopped-job preservation required |
| `experiments/exp_a_initial_eda_r1_r3_r5/` | `implementations/PHM2026/experiments/exp_a_initial_eda_r1_r3_r5/` | Explicitly protected historical EDA; no replacement claimed |

The [fresh metadata-only inventory](REMAINING_PREFLIGHT.json) confirms all 11 source
groups exist and have destinations on the same filesystem. It does not certify
all destination merges or runtime dependencies. The two VIFAILBACK destinations
are ordered: move the original workspace first, then add independent verification.
The [existing exact operation plan](../final_consolidation_20261125/MOVE_OPERATIONS.json)
provides child-level merge operations. It must be refreshed before execution:
its old MSM operations are obsolete, and the audit/Handover-link operations above
are already complete. Do not run that old plan unchanged. The ordinary remaining
`HANDOVER/.gitignore`, `REBOOT/.gitignore` and
`CROSS_DATASET_COMPARISON/.gitignore` files must also be preserved or merged without
overwrite under the already authorized cleanup before their parents can be empty;
the existing operation plan records their destinations. Retain their current raw
ignore coverage until the corresponding raw move and destination coverage checks
pass. No root container is claimed removable merely because its listed payload
moved.

## Specific exception still required

Approve **same-filesystem renames of the exact sources above**, superseding only
the location/no-move restrictions in [AGENTS.md](../../../../../AGENTS.md) and
[data boundaries](../../../../../docs/data_boundaries.md), including the initial
PHM EDA's move restriction and replacement prerequisite **for relocation only**.
No validated replacement of that historical EDA is claimed. Content immutability
and original provenance remain in force at every mapped destination. No raw-data
deletion, deduplication, payload rewrite, extraction or experiment is authorized
by this proposal. Protected `gtc-data-experiment/**` and `data/Full Dataset/**`
are outside the proposed moves and retain their original protected identities.

The exception includes removal of positively identified destination browsing
proxies, repair of their links to the same targets, preservation of colliding
README/ignore files, and removal of source containers **only after empty checks**.
It does not permit overwriting independent files or removing scientific evidence.
Refresh exact merge collisions and ignore coverage before each affected rename.
Record file device/inode/size/mode/mtime before and after, plus append-only actions.
On failure, stop; reverse only identity-checked successful operations into absent,
conflict-free original locations. No raw-payload hashes are required for this move.
These safeguards and reversal procedure reuse the
[existing relocation plan](../final_consolidation_20261125/MOVE_PLAN.md).

The earlier [automatic review record](../final_consolidation_20261125/REQUEST_AND_REVIEW.json)
reports rejection of the broad move before execution because general structural
permission did not establish this exact protected-path exception. This record
makes that decision concrete; it is not permission to bypass the rejection.

## Frozen study dependency gate

The REASSEMBLE feedback/bootstrap studies and VIFAILBACK cannot be blindly
renamed even after the location exception. Their source uses resolved fixed-depth
paths, hard-coded historical roots and source-identity gates. An old-location
symlink alone does not fix `Path(__file__).resolve()`-based repository discovery.
Bootstrap shared-cache consumers also require eight verified link repairs.
No sufficient existing replay adapter was found in the inspected migration and
study modules. Preserve frozen source/configuration bytes and administrative stop
records; develop and validate separate location resolution before moving affected
studies. Approval of a location exception is not permission to weaken identity
checks, clear stops or resume fits. Until that gate passes, those rows remain
pending rather than becoming silently broken archives.

## Root resources that should remain

The requested root README, REPO_MAP, AGENTS, `.gitignore`, license and packaging
files remain. Root `docs/` now contains only the requested `THESIS_CODE_MAP.md`
and three repository policies. Root `src/` contains four package compatibility
links required by `pyproject.toml`. The existing ignored `ma_thesis_env/` is an
installed environment with location-dependent executables. Relocating it is not
ordinary file cleanup; no environment was changed. Private ignored local state
remains uninspected. These operational resources are not competing study copies.

## Validation boundary

The two operation receipts distinguish metadata preservation, bounded hashes of
small documents, link checks and ignore checks. None claims scientific replay.
[VALIDATION.json](VALIDATION.json) records the final integrated checks. Exact root
edits are compared with this phase's preimages so earlier manuscript work is not
misattributed to root cleanup. Historical thesis receipts and submitted snapshots
remain unchanged; this phase is an additional publication-content review item.
