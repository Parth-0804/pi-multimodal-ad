# Full physical consolidation — pending exact approval

**PENDING: NO RELOCATION EXECUTED.** Prepared on 2026-11-25 in response to the researcher's request to move the remaining dataset and study folders into `implementations/` and update location documentation. Automatic approval review rejected the broad relocation before its command ran. This plan makes the protected-path exception, exact operations and preservation gates reviewable.

## Exact proposed locations

All paths below are relative to the repository root. Each row includes all descendants, hidden files and original raw/source payloads where present. Existing destination directories are merged only through the non-conflicting operations in [MOVE_OPERATIONS.json](MOVE_OPERATIONS.json). No independent file is overwritten.

| Current path | Proposed physical location | Protected material covered by the requested exception |
|---|---|---|
| `MSM/` | `implementations/MSM/` | `01_raw_dataset/` and its official-dataset link |
| `HANDOVER/` | `implementations/HANDOVER/` | `01_raw_dataset/` and remaining `experiments/common_support_v2/` material |
| `REBOOT/` | `implementations/REBOOT/` | `01_raw_dataset/` and retained investigation `runs/` |
| `VIFAILBACK/` | `implementations/VIFAILBACK/` | Complete raw, source, protocol, checkpoint, experiment and report workspace |
| `MILLING DATASET/` | `implementations/MSM/experiments/legacy/` | Separate legacy raw-source tree `data/`, decoder `.tools/` and remaining run material; raw versions are not merged with another dataset version |
| `CROSS_DATASET_COMPARISON/` | `implementations/cross_dataset/results/` | Remaining audit records and native visual/sensor review examples |
| `DATASET_RESEARCH/VIFAILBACK_VERIFICATION/` | `implementations/VIFAILBACK/02_dataset_verification/independent_verification/` | Independent verification, original source evidence and historical review records |
| Remaining `DATASET_RESEARCH/` | `implementations/general/docs/dataset_research/` | Remaining discovery source evidence; the preceding VIFAILBACK row is handled first |
| `26.10.2026_feedback_experiments/` | `implementations/REASSEMBLE/experiments/cnn_seed_stability/phase1_feedback/` | Frozen phase-one source/configuration and training evidence |
| `parth_ws_bootstrap/` | `implementations/REASSEMBLE/experiments/bootstrap/` | Original bootstrap source, fit records and shared caches |
| `experiments/exp_a_initial_eda_r1_r3_r5/` | `implementations/PHM2026/experiments/exp_a_initial_eda_r1_r3_r5/` | Protected historical PHM EDA, including its original generated outputs; the emptied root `experiments/` container is removed |

The exact machine-readable prefix and individual-file mapping is [PATH_MAPPING.json](PATH_MAPPING.json). No top-level dataset compatibility links are proposed: the old containers will be removed only when empty. Root `src/` import links, policy documents, the environment and Git metadata are outside these moves.

## Narrow exception to approve

For **this structural relocation only**, approve same-filesystem renames of the exact listed paths and descendants, superseding the **location/no-move** restrictions in [AGENTS.md](../../../../../AGENTS.md) and [data boundaries](../../../../../docs/data_boundaries.md), including the protected historical PHM EDA location. This approval does not waive content immutability, authorize deletion or overwrite of scientific files, or authorize new experiments.

Retain the old paths as historical identities in provenance and apply the same raw-data/historical protections at the mapped destinations. The PHM `gtc-data-experiment/**` and Intel `data/Full Dataset/**` identities are outside the move list and remain protected even when absent. Neither raw restoration nor deletion is proposed.

Permitted supporting operations are limited to:

- Remove the 15 inspected browsing symlinks in `implementations/VIFAILBACK/` that point to the source directories being moved, then put those actual directories in their place.
- Repair the 12 relative/absolute symlink references listed in [PLANNED_SYMLINK_REPAIRS.json](PLANNED_SYMLINK_REPAIRS.json), preserving their intended targets. This includes the MSM official-dataset link, VIFAILBACK latest-results link, bootstrap shared-cache references and audit utility links.
- Remove the 15 emptied source/merge containers listed in [MOVE_OPERATIONS.json](MOVE_OPERATIONS.json), after checking they contain nothing.
- Update current location guides, scoped source path adapters, applicable ignore rules and root discovery. Preserve frozen commands, scientific configurations, results and provenance as historical records, with relocation documentation beside the current guides.

The original VIFAILBACK `README.md` is retained at `implementations/VIFAILBACK/docs/WORKSPACE_BEFORE_CONSOLIDATION.md`; the current implementation guide remains separate. The two colliding original `.gitignore` files are retained in this phase's `preserved_collisions/` directory; the already present destination rules remain in force and are checked for coverage.

## Preflight evidence and gates

[STATUS.json](STATUS.json) records the metadata-only inspection of 94,939 source nodes, 42 proposed rename operations, 15 proxy removals and 15 empty-container removals. There are no unresolved destination conflicts, and the checked destinations are on the same filesystem. The local, ignored `FILE_METADATA_BEFORE.jsonl` records the old/new path, device, inode, size, mode, modification time and link text for each source node. No raw payload was read, hashed, copied, extracted or modified.

A tiny synthetic fixture checked directory merging, preservation of colliding files, verified proxy replacement, relative-link repair and file metadata identity. This does not establish execution or scientific reproduction of the real move. The repository currently has 16 pre-existing broken symlinks; execution must introduce no new broken links. Existing broken references may be repaired only where the retained target can be positively identified.

Before execution, refresh stopped-job/process checks, source/destination metadata and collision checks. Abort affected operations on any change, active dependency or identity mismatch. Record successful operations in an append-only action journal. Use `os.rename`, never cross-filesystem copy-and-delete or a destructive directory merge.

After each rename, check all relocated regular-file identities against their saved device/inode/size/mode/mtime values and confirm every expected relative path is accounted for. Check symlink text before repair, log each change, and verify intended targets afterwards. Source-directory identities can change when two containers are merged; their scientific files must retain their identities. Record deliberate guide/path-adapter edits separately with preimages.

## Recovery and completion

On failure, stop further moves and retain the successful-operation journal and all data. Reverse completed renames in reverse order only after checking expected destination identities and absent/conflict-free original locations. Restore changed link text from the symlink journal and recreate verified proxy links only after restoring their targets. Never overwrite a file that appeared at an original location; report the conflict instead. No scientific payload deletion is part of recovery.

Completion requires all listed old roots gone, full metadata preservation accounting, no new broken links, appropriate ignore coverage for relocated raw data/checkpoints, current guide/link checks, scoped imports and tiny synthetic tests, exact diff review, `git diff --check`, and a summarized full Git status. No training, inference, preprocessing, download, environment installation, commit or push is included.

Until the exact exception above is approved, the current mixed physical layout remains authoritative. The prepared relocation tool's entry point is disabled and also requires a separate approval record.
