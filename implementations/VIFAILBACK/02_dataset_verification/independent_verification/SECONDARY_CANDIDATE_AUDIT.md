# Secondary candidate: Zenodo 4578539

**NO-GO for the intended supervised binary comparison using the published partition.** This is not a blanket claim that the dataset cannot support other designs.

Official source: [A robot dataset of successful and failed placement executions](https://zenodo.org/records/4578539), DOI **10.5281/zenodo.4578539**, published version **v1**, CC BY 4.0 per the downloaded Zenodo metadata. The Toyota HSR places a book on a shelf; recorded modalities include RGB/depth, rendered robot images, force/torque and joint telemetry according to the publisher. No audio substitution is proposed.

## Published partition, not an independently recounted corpus

| Published split | Successful trials | Anomalous trials |
|---|---:|---:|
| Training | 48 | 0 |
| Validation | 6 | 0 |
| Test | 7 | 60 |
| Total | 61 | 60 |

The archive sizes from the record API are **3,387,726,028** training bytes, **365,983,836** validation bytes and **4,384,127,358** test bytes. Author MD5 values and URLs are preserved in `source_evidence/zenodo_api.json`. No full archive was downloaded; a full-archive SHA-256/MD5 was not computed. The numbers above are **author-reported trial counts**, not verified from every source member.

## Actual native annotations retrieved

Gzip has no random-access central directory. Bounded HTTP prefixes were preserved, totaling 256 MiB of the test stream plus smaller initial test/validation prefixes; the logical inspected test prefix contains 5,067 tar members. Expected premature end-of-stream reflects bounded acquisition, not an asserted corrupt archive. Two actual original `annotation.json` members were decoded and individually SHA-256 recorded:

| Original archive member | Native Outcomes | Native Anomalies |
| --- | --- | --- |
| test/trial_106/annotation.json | ['Object does not reach intended position', 'Robot is disturbed'] | [[90, 176]] |
| test/trial_048/annotation.json | ['Object falls to the ground'] | [[326, 368]] |

The native schema has a list of textual outcome/event descriptions and `Anomalies` frame-index intervals. Author source code, pinned at **204d91e1ea0f7012e27400fb0842e44debc035f2**, maps inclusive intervals onto the ordered RGB frames and marks anomaly frames 1. These are **frame-level anomaly/event labels**, not a native yes/no episode-success field. External collision or camera occlusion can be anomalous without being identical to final task failure. Do not silently collapse those concepts.

The two positive native examples support the existence/schema of annotations, not a complete positive/negative recount or a validated sensor/video cohort. No full numerical schema, synchronization, payload integrity or negative-label audit was completed for this secondary candidate; it was deprioritized after the published partition failed the intended supervised training contract.

## Why the original split does not support supervised binary training

Training and validation contain no anomalous trials under the published split. A binary discriminative visual/sensor classifier and learned probability fusion cannot be trained/selected on both classes using those partitions. Training on frames/labels from the published test set would compromise that benchmark. A nominal-only anomaly detector is a different experiment; a new trial-disjoint supervised partition would require explicit redesign, complete native label/sensor verification and preservation of the original split identity. Neither was performed here.

Actual source records, partial-stream limitations, original member filenames and hashes are in `checks/secondary_bounded_native_audit.json`; member inventory in `checks/secondary_256MiB_member_listing.json`; source code in `source_evidence/secondary_code.zip`. No file contents were inferred from directory names or supplied by an LLM.
