# Final cleanup and storage decision

2026-10-28T20:18:47+01:00 · Project: `/home/student/Master_Thesis_WS/pi-multimodal-ad`. GB/MB are decimal; GiB is binary.

**Intel retirement completed. Retain all REASSEMBLE data for now; no further cleanup is necessary for the stated storage budget at this snapshot.** The only deletion was the specifically authorized `data/Full Dataset` directory. No REASSEMBLE file was deleted or modified, no training process was interrupted, no REBOOT file was downloaded, and nothing was staged or committed.

## Intel deletion: exact scope and evidence

| Item | Verified result |
| --- | --- |
| Absolute resolved target | /home/student/Master_Thesis_WS/pi-multimodal-ad/data/Full Dataset |
| Original allocation | 26,877,308,928 bytes = 26.877 GB (25.031 GiB) |
| Original logical file bytes | 26,813,483,096 |
| Exact removal | 8,286 regular files and 8,317 directories including the target root |
| Payload / metadata disposition | 8,284 raw payload files removed; original manifest.csv and LICENSE.txt copied and hash-verified outside raw root before their original paths were removed |
| Fresh payload hashing | All 8,284 payload SHA-256 values exactly match the preserved September foundation inventory; the two original metadata files were also freshly hashed |
| Git status | 0 tracked target files; target metadata explicitly Git-ignored |
| Path safety | Exact resolved directory/device/inode; no symlinks, special files, nested mounts or hard links; file/directory sets and identities rechecked immediately before descriptor-based removal |
| Active dependencies | No Intel target file descriptors, mappings or working directories found in same-user processes; current modelling is a documented Intel foundation NO-GO |
| Dormant consumers | Intel inventory/label/foundation scripts and historical configs remain intact; a future raw-data replay requires restoration |
| Parent/siblings | data/ and all pre-existing sibling paths preserved |
| Deletion execution | 2026-10-28T19:12:34.930950+00:00 to 2026-10-28T19:12:40.134280+00:00 |

The latest researcher instruction is the narrow authorization overriding the normal raw-data immutability/deletion-confirmation rule for this target only. The root matched the Intel manifest: 4,040 sample rows, 236 session identities and 12 intended-condition categories. It contained 2,723 AVI files, 2,723 FLAC files, 2,726 CSV files (including the original manifest), 113 post-weld JPGs and one licence. No code, model checkpoint, report or other unexpected research file was found inside it.

All exact removed relative paths, byte counts, fresh SHA-256 values, inode identities and source references are in [INTEL_REMOVED_FILES.csv](cleanup_20261028T190906Z/INTEL_REMOVED_FILES.csv). The directory inventory is [INTEL_REMOVED_DIRECTORIES.csv](cleanup_20261028T190906Z/INTEL_REMOVED_DIRECTORIES.csv). These are complete enumerations, not samples. The deletion result is [INTEL_DELETE_RESULT.json](cleanup_20261028T190906Z/INTEL_DELETE_RESULT.json) and its execution gate is [INTEL_DELETE_EXECUTION_GATE.json](cleanup_20261028T190906Z/INTEL_DELETE_EXECUTION_GATE.json).

Preserved unchanged: `src/intel_welding/`, `scripts/intel_welding/`, `docs/intel_welding/`, `runs/intel_welding/` where present, `artifacts/intel_welding/`, `configs/intel_welding/`, `archive/legacy_intel_welding_dataset/`, historical configurations/results, and existing scientific documentation. **All 86 existing Intel evidence files match their before-cleanup SHA-256 identities.** Other existing project files were checked by size/mtime/inode/mode, with concurrent changes recorded separately rather than attributed to this deletion.

### Original labels, licence and recovery

- [manifest.csv](cleanup_20261028T190906Z/intel_retained_metadata/manifest.csv): 587,626 bytes; SHA-256 `9c4fb4df70bb137fc851dd858ac22d53eed86ba08c3806d7177e40b300406826`.
- [LICENSE.txt](cleanup_20261028T190906Z/intel_retained_metadata/LICENSE.txt): 3,646 bytes; SHA-256 `ba9ae1787e84cb8fd8f75cc362880a4087a05ca1c67526f765658795c3558908`.

The retained original manifest preserves CATEGORY, SPLIT, session/sample identities and process fields. Existing foundation inventories, label audits, split records and source/download instructions remain unchanged. No raw payload backup was created, so the permanent deletion has no local undo. **Recovery is conditional on authorized redownload from the [official Intel dataset](https://huggingface.co/datasets/IntelLabs/Intel_Robotic_Welding_Multimodal_Dataset), whose public card is reachable but whose files require accepted access conditions.** No credentials were inspected and no access request/download was made. The historical remote revision was not recorded; exact recovery is established only if restored file hashes match the retained manifest. Public availability is not proof of continuing account access or byte-identical future content.

## Measured space recovery and final decision

| Measurement / calculation | Bytes | Decimal GB |
| --- | --- | --- |
| Filesystem capacity | 531415142400 | 531.415 |
| Available immediately before deletion | 52997627904 | 52.998 |
| Available immediately after deletion | 79874924544 | 79.875 |
| Actual measured availability increase | 26877296640 | 26.877 |
| Original target allocated blocks | 26877308928 | 26.877 |
| Current available at final check | 79870943232 | 79.871 |
| Planned REBOOT allowance, conservatively all additional | 40000000000 | 40.000 |
| Remaining after full additional allowance | 39870943232 | 39.871 |
| Desired minimum reserve | 20000000000 | 20.000 |
| Margin beyond allowance and reserve | 19870943232 | 19.871 |

The observed increase was 26,877,296,640 bytes, 12,288 bytes below the target allocation; ongoing filesystem writes explain why these point-in-time values need not be identical. Current availability can continue changing as authorized jobs write. This calculation conservatively reserves a fresh 40 GB in addition to REBOOT files already present. Even a 20 GiB reserve would fit. A user quota was not verified; figures describe filesystem availability.

**Recommendation: retain the entire 330.622 GB REASSEMBLE dataset and its caches now.** Current measured capacity exceeds the 40 GB additional REBOOT allowance plus 20 GB reserve, with the margin above for other growth. Additional REASSEMBLE cleanup is unnecessary for this snapshot. Recheck capacity immediately before a separately authorized download, including new experiment-output growth; no transfer or experiment was started here.

## REASSEMBLE usage and retention review

The external resolved root is `/home/student/Master_Thesis_WS/datasets/REASSEMBLE`: 330,622,394,368 allocated bytes (330.622 GB), 827 files. All 827 files retained the same size, modification time, inode and mode throughout and after review; the file set is unchanged. There are no hard-linked aliases or symlinks in this external root. The project’s previously observed hard-link duplicates do not provide additional REASSEMBLE savings.

Completed REASSEMBLE model studies use **4,530 segments from 148 recordings**. Each uses the embedded `hand` video and five sensor streams—`measured_force`, `measured_torque`, `gripper_positions`, `joint_efforts`, `joint_velocities`—forming 22 channels. The current Phase 1 input manifest has the same 4,530 samples and 148 source/hand-video identities; all source hashes recorded there agree with the historical recording manifest, and every current source/video size and mtime matches. Current full-CNN training reads hand MP4s directly; its automatic continuation also requires the full protected cohort, pretrained files and project sensor/feature manifests.

All 149 original recordings were used in acquisition/integrity/schema/modality/alignment audits. The one excluded from model fitting is `raw/data/2025-01-10-16-17-40.h5`, because hand-camera data are missing; its source/native-label evidence remains REQUIRED. It is not an unreferenced raw duplicate. Audio, event/capture streams, alternative RGB cameras and other robot-state channels are not fitted branches in the completed hand-plus-sensor model protocol, but some support modality/quality audits and negative findings. They share authoritative HDF5 containers, so removing those members would rewrite originals and is not proposed. No entire raw recording was certified unused by every existing or planned audit.

### Retention and candidate table

REQUIRED means retain authoritative/scientific evidence; ACTIVE adds protection while jobs or their scheduled continuation depend on it; OPTIONAL means a conditional future review candidate, not permission to remove; UNKNOWN means insufficient lineage. No file remained unmapped/UNKNOWN in this bounded inventory, although current full-content verification has the limits stated below.

| Exact path / enumerated set under external root | Allocated size | Class | Original purpose, observed use and decision |
| --- | --- | --- | --- |
| raw/data/*.h5 (149 exact paths in recording table) | 263.984 GB | REQUIRED | Original sensors/videos/native labels; all audited, 148 fitted/current-cohort sources; preserve all, including the excluded recording |
| cache/encoded_media/<source-SHA256>/hand.mp4 (148 exact paths) | 2.759 GB | ACTIVE | Completed and ongoing 16/32-frame CNN input; cannot remove during current job or automatic continuation |
| cache/section1_models/ac77a11ff0170a41b771c03264987f8ce2b0d753/ (3 files) | 0.081 GB | ACTIVE | Pinned pretrained model, processor and config; fresh SHA256 identities match; preserve initialization/recovery source |
| cache/final_validity_audit/20260928T032231Z/ (70 files) | 0.065 GB | REQUIRED | Blinded clips, reviewer sheets/instructions, label keys and encoding provenance are retained scientific evidence despite cache name |
| raw/poses/, raw/train_split1.txt, raw/test_split1.txt, and small downloads/ files | 0.001 GB | REQUIRED | Native geometry, official split and source/licence context; tiny footprint; archive/extracted metadata byte equality verified |
| downloads/data.zip | 58.881 GB | OPTIONAL | 58.881 GB original restore archive; used acquisition/integrity, not current model reads. Removing it loses local offline backup. Preserve now; any future retirement needs complete verified extracted sources and researcher review |
| cache/encoded_media/<source-SHA256>/hama1.mp4 (149 exact paths) | 2.493 GB | OPTIONAL | 2.493 GB auxiliary RGB cache: used initial multi-view audit, not any reviewed completed/current model branch; can be recopied from native HDF5 hama1 bytes. Future full audit or alternate-view work requires regeneration |
| cache/encoded_media/<source-SHA256>/hama2.mp4 (149 exact paths) | 2.357 GB | OPTIONAL | 2.357 GB auxiliary RGB cache: same audit use, no reviewed model consumer; can be recopied from HDF5 hama2. Preserve originals, manifests and regeneration identity first |

For **every one of the 299 OPTIONAL files**, [REASSEMBLE_FILE_RETENTION.csv](cleanup_20261028T190906Z/REASSEMBLE_FILE_RETENTION.csv) provides the exact absolute path, logical/allocated size, original purpose, completed/current use, dependency evidence, deletion consequence, restore/regeneration route, hash scope, inode/link count and conditional block estimate. This is the complete per-file candidate table behind the grouped rows above. [REASSEMBLE_RECORDING_USAGE.csv](cleanup_20261028T190906Z/REASSEMBLE_RECORDING_USAGE.csv) enumerates all 149 original sources with recorded hashes, 148 model memberships, segment counts and active references.

Conditional file-block upper bound: 63.731 GB = 58.881 GB archive + 4.850 GB auxiliary-camera caches. These are disjoint files and no hard-link savings were added. Directory metadata is excluded from that estimate. **No bytes were removed from these candidates, and none is recommended for removal now.** No stray temporary transfer files, additional full dataset copies or duplicate full-recording SHA256 groups were found.

### Hash evidence, restore routes and limits

- All 149 current HDF5 sizes/mtimes match their existing full-file SHA256 inventory; all 148 current Phase 1 source/video identities also match. This is current metadata agreement with historical full hashes, not a fresh 264 GB payload hash pass.
- The retained data.zip central directory has all 149 expected members with matching extracted names and sizes. Current full local archive MD5 was not recomputed. The acquisition receipt and the freshly checked [official TU Wien v1.0.0 release](https://researchdata.tuwien.ac.at/records/0ewrv-8cb44) agree on `md5:812103a652ca9201e87a3bcecfee4ef3` and original archive size 58,881,334,586 bytes. Before any future archive retirement, independently verify all extracted contents; names/sizes alone do not prove integrity.
- Fresh MD5 matches were obtained for README.txt, poses.zip and splits.zip. All 153 pose files and both supplied split texts match their archive-member contents by SHA256. The three pinned pretrained files match their recorded full SHA256 values.
- Three bounded representative MP4s—one for each camera—match the embedded HDF5 encoded byte stream by fresh SHA256. The extraction source copies encoded bytes rather than transcoding. This verifies the mechanism and samples, not all 446 files or a complete isolated cache regeneration. Cache-directory names are HDF5 hashes, not video hashes.
- Restore data.zip by the official v1.0.0 download link and verify published MD5; restore a recording from the retained archive and verify its saved SHA256. Regenerate a retired auxiliary MP4 only by a separately reviewed cache-only byte-copy route from the retained native HDF5; avoid rerunning full audits/training drivers that write historical run state. Nothing was restored, extracted to disk, regenerated or downloaded during this review.

## Preservation and validation

Intel scientific preservation: 86/86 SHA256 matches. External REASSEMBLE preservation: 827/827 metadata identities and the complete file set unchanged. Outside the removed target, 245,110 existing project file metadata records were rechecked; 0 paths were absent and 8 changed during the continuing workflows. Their exact paths and limits are recorded in [FINAL_VALIDATION.json](cleanup_20261028T190906Z/FINAL_VALIDATION.json). All Intel evidence and other data/ siblings remain intact; no missing/change is silently presented as content proof. Process inspection covered same-user names, cwd, open paths and mappings; inaccessible systemd/PAM/SSH service state was recorded. No command lines, environments, credentials or private session contents were read.

`git diff --check` passed. `ma_thesis_env/bin/python -B -m pip check` passed. No pytest suite, model fit, inference, decoder run or scientific regeneration was performed for this storage task. Existing tracked diff:

```text
 README.md                                              |  4 ++++
 REPO_MAP.md                                            |  6 ++++++
 docs/thesis_research_direction/THESIS_EVIDENCE_GAPS.md | 12 ++++++++++++
 3 files changed, 22 insertions(+)
```

New audit-only files are this report and the timestamped evidence directory `STORAGE_AUDIT/cleanup_20261028T190906Z`. Existing tracked changes remain unrelated, and untracked audit manifests are not included in `git diff --stat`. The complete output identities and commands are in [CLEANUP_PROVENANCE.json](cleanup_20261028T190906Z/CLEANUP_PROVENANCE.json).

**Final recommendation: keep all REASSEMBLE originals, derived media and review evidence. Intel retirement alone provides sufficient current headroom. Reassess only if actual planned growth exceeds the measured margin; any REASSEMBLE removal requires separate authorization.**
