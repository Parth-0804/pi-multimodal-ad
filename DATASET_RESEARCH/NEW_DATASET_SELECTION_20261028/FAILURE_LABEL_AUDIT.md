# FAILURE / FINO-Net native-label and data audit

**Decision: GO FOR VISUAL PILOT for episode-level RGB-plus-audio classification.** Full architecture adaptation is conditional; this release supplies no robot proprioception or force/torque. No model result is inferred from this audit.

## Pinned original sources and release identity

The [author project](https://air.cs.itu.edu.tr/projects/finonet.html) links the [official repository](https://github.com/ardai/fino-net/tree/8196217bf52d17fdb7193e57619bd855b1723d4e) and `annotation.zip`. Repository revision: **8196217bf52d17fdb7193e57619bd855b1723d4e**. The annotation ZIP is **1,121 bytes** and contains five original text members. Their byte sizes and individual SHA-256 values are recorded in `SOURCE_PROVENANCE.json`.

The official data URL is `http://160.75.159.4/data/failure.zip`. Anonymous HEAD and bounded HTTP Range requests succeed. Its size is **10,197,520,375 bytes**; Last-Modified is `Fri, 12 Feb 2021 14:31:40 GMT` and ETag is `"25fd1cff7-5bb247e919470"`. This is an unversioned data URL: the ETag and central-directory digest are acquisition identifiers, not a publisher's semantic version or full ZIP SHA-256. The complete ZIP was not downloaded or hashed. Its **53,165** directory entries enumerate **20,267,899,623** uncompressed bytes. This listing was read using roughly 6.78 MB of ZIP64/central-directory ranges.

The repository includes MIT licensing. No explicit separate license for the externally hosted raw archive was located; verify data-use terms before redistribution/full study. There is no authentication bypass. The GitHub API was rate-limited; public Git and pinned raw files provided the same official repository evidence.

## Annotation schema and label meanings

The original ZIP contains `place_annotation.txt`, `pour_annotation.txt`, `push_annotation.txt`, `put_in_annotation.txt`, `put_on_annotation.txt`. Each is CSV text with **`name,label`** only. The native target is an entire action/recording outcome. Source notebook cell 4 explicitly treats `bag_label==0` as successful and `bag_label==1` as failed. Its source URL is pinned in the provenance.

The archive has **252 distinct labeled identities: 163 failure (1), 89 success (0)**. No duplicate composite `(action,name)` or invalid binary class was found. The actual complete-modality cohort has **229 recordings: 147 failure, 82 success**, positive prevalence **64.192140%**. This matches the original FINO-Net paper's 229-recording table, not the annotation ZIP's larger inventory.

| Action | All labeled: failed / success | Joined: failed / success | Joined total |
| --- | --- | --- | --- |
| place | 33 / 14 | 32 / 13 | 45 |
| pour | 42 / 25 | 42 / 25 | 67 |
| push | 20 / 12 | 19 / 12 | 31 |
| put_in | 33 / 23 | 33 / 23 | 56 |
| put_on | 35 / 15 | 21 / 9 | 30 |

The [original paper](https://arxiv.org/html/2011.05817v2) defines goal-oriented failure and treats small target deviations as success. It reports synchronized RGB/depth/audio and 16 kHz audio. The [extended paper](https://arxiv.org/html/2305.04639) discusses additional recordings and failure types; those results do not establish that the old downloadable ZIP contains the extension. The hosted file is dated 2021, and no extended failure-type or onset archive was located. Its 229 joined recordings must not be reported as the later extended dataset.

## Original-file join and missing records

The verified join is composite action and recording ID:

```text
annotation.zip!<action>_annotation.txt: name,label
failnet_dataset/rgb_imgs/<action>/<name>/frame*.png
failnet_dataset/rgb_imgs/<action>/<name>/frame*.txt
failnet_dataset/depth_imgs/<action>/<name>/frame*.tiff
failnet_dataset/audio/<action>/<name>.wav
```

For all 229 eligible labeled recordings, every stored RGB frame has a same-stem depth image and timestamp file, and a nonempty WAV is listed. The stored RGB sequences contain **34–138 frames**, so sixteen distinct source file positions exist for every joined recording. No RGB/depth or RGB/timestamp stem discrepancy occurs within this cohort. These are inventory checks, not full payload decodes, full audio validation or a duplicate-content scan.

There are **23** labeled IDs without complete modalities:

| Action | Labeled IDs missing a complete join |
| --- | --- |
| place | 6, 47 |
| push | 18 (depth present; RGB/audio absent) |
| put_on | 31–50 |

Two additional recordings, `place/28` and `put_in/28`, have payload entries but no original binary annotation. They are excluded. There are 231 WAVs and 229 RGB recording directories in the source listing. An identity is not labeled by its directory name or inferred from neighboring IDs.

All source rows and exceptions are preserved in `checks/failure_native_annotation_records.csv`, `failure_counts_by_action.csv`, `failure_counts.json`, and `failure_archive_inventory.json`.

## Audio, timestamps and numerical channels

Only **measured audio** is available as a suitable nonvisual numerical stream. A selectively extracted original `audio/push/5.wav` has **16,000 Hz**, one channel, 16-bit PCM, 1,075,840 samples and **67.24 seconds**. ZIP CRC verification and SHA-256 identify that exact payload. Counts do not assume all WAVs share its encoding; that remains a pilot check.

No force, torque, joint-state, kinematic or commanded-action files were found in the complete ZIP directory. RGB/depth image intensities are not substitutes for those measurements. PCM sample amplitude has digital units; calibration to acoustic pressure is not provided. Depth physical units/calibration were not verified.

First and last original RGB timestamp text files were read and CRC-checked for **all 229** eligible recordings. Endpoints are finite and strictly ordered, spanning **34.90–135.77 seconds**. This establishes endpoint ordering only; interior timestamps were not all retrieved. The sampled `push/5` RGB endpoints span 66.40 seconds while its audio spans 67.24 seconds. There is no corresponding absolute WAV start timestamp in the release listing. The 0.84-second difference cannot be assigned to either endpoint. Do not claim precise audio/video alignment or attach arbitrary local failure labels to full-action audio.

The public notebook expects an annotation `start` field and string-like recording names, while the linked original annotation ZIP has integer names and **no `start` column**. That loader cannot be reproduced unchanged from these released annotations. No event onset, failure mode, recovery interval or frame-level label is available in this ZIP. A valid initial target is **whole-action outcome**, using sixteen ordered frames covering that same recorded action and audio statistics from its paired WAV. A time-local failure classifier needs additional native onset and alignment evidence.

## Independent groups and observability

There are seven candidate UTC recording dates, obtained from original timestamp values; every date contains both outcomes. These are observed dates, not asserted author-provided session IDs. Several actions occur on only one date, so held-out date performance can conflate task and date shift. The robot is Baxter; operator and object-instance identity tables were not found.

Official successful and failed pour GIFs show a gripper, cups, interaction and spilled material. Their exact recording IDs and audio counterparts are not supplied. They show that the physical failure can be visible in some source demonstrations, not that all 147 failures are observable or that the released RGB camera matches these crops. Objects/backgrounds differ across these demonstrations and may confound outcome. Blinded corpus-linked review remains essential.

The next proposed pilot is ten complete recording identities (five successful/failed action pairs), matched on action, timestamp-derived day and endpoint duration. Object/view matching remains UNKNOWN until reviewed. Proposed files require **113,012,633 compressed member bytes** and **125,393,705 extracted bytes**; HTTP/local-header overhead and optional depth are additional. This pilot is planned only and was not acquired.
