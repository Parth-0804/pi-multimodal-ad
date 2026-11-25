# Potential space recovery

Audit `20261028T114917Z` · 2026-10-28T12:49:17+01:00. Read-only assessment; no cleanup or downloads. GB/MB are decimal; GiB/MiB are binary. Directory sizes are allocated blocks, with hard links counted once per subtree and symlinks not followed.

All amounts below are estimates of allocated blocks that might be released after the stated gates. They are not cleanup authorization. Historical-output protection still applies. GREEN means likely regenerable convenience cache after verification; YELLOW needs researcher approval and explicit dependency/reproduction checks; RED must remain; UNKNOWN lacks sufficient lineage. Git-ignored status alone is not evidence of disposability.

| Path | Size | Purpose | Reproducible? | Dependencies / gate | Risk | Potential savings | Recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| .pytest_cache | 65,536 B | Pytest node IDs/convenience state | Yes, test cache; no scientific input | Marker/README identify pytest; no writer observed | GREEN | 65,536 B | Consider only after researcher review; no evidence chain affected |
| 28 source-matched .pyc files under src/ and scripts/ | 434,176 B | Import bytecode | Corresponding .py files exist; Python can compile again | Only enumerated untracked single-link files; retain .py and unmatched bytecode | GREEN | 434,176 B | Convenience caches; no model/feature generation needed |
| CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE/INDEPENDENT_REVIEW_PACKAGE.zip | 1.170 GB | Packed independent-review delivery | Payload can be repackaged; identical ZIP byte hash not guaranteed | Keep expanded package; independently verify content/manifest and delivery receipt first | YELLOW | 1.170 GB | One redundant delivery container; approval required |
| tutorials/rtdetr_storybook/rtdetr-l.pt | 0.067 GB | Pretrained tutorial weight copy | Fresh SHA-256 equals retained run copy | Keep canonical checkpoint; inspect tutorial path references and provide a reviewed restore/redirect plan | YELLOW | 0.067 GB | Only this copy counted; historical path still protected pending approval |
| MSM/03_processed_model_inputs/visual_features | 1.002 GB | Clean/corruption per-frame CNN feature cache | Frozen method documented; no fresh full regeneration demonstrated | Keep raw inputs, model revision, frame selections, per-file hashes, fit/prediction evidence; isolated parity validation | YELLOW | 1.002 GB | Conditional cache retirement; approval and retained recovery manifest needed |
| HANDOVER/experiments/common_support_v2/03_processed_model_inputs/visual_features | 0.308 GB | Handover v2 CNN feature cache | Frozen method documented; no fresh full regeneration demonstrated | Keep official data and v2 frame/label/alignment manifests; isolated parity validation | YELLOW | 0.308 GB | Conditional cache retirement; preserve split/model/prediction lineage |
| .cache/repository_restructure | 0.002 GB | Relocated old namespace bytecode | Not yet certified against preserved source/preimages | Migration maps/source correspondence and researcher retention review | YELLOW | 0.002 GB | Review after useful larger candidates |
| scratch plus unmatched src/scripts bytecode | 0.052 GB | Uncertified work and code-cache history | UNKNOWN | Establish original inputs and source counterparts; do not infer from names | UNKNOWN | 0 counted | Preserve pending lineage review |
| All other project paths (disjoint remainder) | 95.506 GB | Raw inputs, history, active runtime/jobs and protected scientific evidence | Varies; not established for cleanup | Raw-data and historical-output policies; current scientific dependency chain | RED | 0 | Preserve; no generic generated-run or environment pruning |
| ../datasets/REASSEMBLE (external) | 330.622 GB | Authoritative original/extracted recordings plus live encoded inputs | Originals authoritative; cache used by running workers | Same-UID live MP4 read descriptors; raw/source provenance | RED | 0 | Outside project total; do not treat raw ZIP/extraction or encoded cache as spare space |

## Nonoverlapping estimates

| Partition | Allocated / potential recovery |
| --- | --- |
| High-confidence convenience-cache potential | 499,712 bytes = 0.500 MB |
| Conditional duplicate/export recovery | 1.237 GB |
| Conditional cache retirement (requires independent verification) | 1.312 GB |
| Total conditional potential | 2,548,764,672 bytes = 2.549 GB (2.374 GiB) |
| UNKNOWN, excluded from recovery | 0.052 GB |
| Must-preserve project remainder | 95.506 GB |
| External REASSEMBLE must preserve (not in project partition) | 330.622 GB |
| Recovery actually performed | 0 bytes |

The project partition sums exactly to the measured project allocated total. The source-cache entry enumerates individual files rather than claiming entire source directories. Feature-directory estimates include directory blocks and assume the entire stated cache retires only after the manifest is retained elsewhere in a new small run. Savings can be slightly lower if metadata is retained in place; they are upper bounds, not guarantees. No parent directory overlaps its child in the conditional total. Other verified copies inside the expanded review package stay preserved and add no recovery to this estimate.

All 11,682 observed hard-link pairs share already allocated bytes: removing one name yields zero file-block savings. The three Handover train/validation/test `.part` aliases therefore do not offer another ~12.95 GB. Their nonzero logical file lengths must not be added to recovery. The raw/staging Milling copies use hard links as well. Symlink targets are also counted once. No reflink/shared-extent census was made; independent-copy block-release figures are upper bounds on ext4 and should be verified at cleanup time.

## Bounded duplicate verification

Three independent duplicate pairs were confirmed with fresh streaming SHA-256: the 66.5 MB pretrained checkpoint, 46.2 MB visual-review PDF and 43.2 MB raw-audio export copy. A same-sized pair of fitted fold models produced different SHA-256 values; both are required. The duplicate CSV records full digests, paths, inode evidence, risk and per-candidate upper bounds. Its upper-bound column is not an additive recovery plan. The review ZIP has 8,595 entries whose expanded names/sizes all match; content was not rehashed in full here. External REASSEMBLE data.zip has 149 members with matching extracted names/sizes, which verifies representation coverage but not fresh content equivalence.

The original PHM archive retirement and October cache eviction are completed historical actions, excluded from present recovery. No raw dataset, unique prediction, fitted model, source snapshot, native annotation or required provenance is recommended for removal in this audit.
