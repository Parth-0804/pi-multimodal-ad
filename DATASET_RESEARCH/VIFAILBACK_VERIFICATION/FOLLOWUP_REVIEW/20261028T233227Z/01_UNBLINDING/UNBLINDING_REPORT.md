# Locked review versus native annotations

The supplied review is an AI-assisted independent interpretation, not a separate
human annotation. Its predictions were copied and hashed before opening the key
in this audit. Lock: `../00_LOCKED_REVIEW/REVIEW_LOCK.json`; source review hash:
`308b478c0a29d4601ed2446c95e0257ea932c9ed128f3bf5d75b7baeed5010d2`. The original review and its observation text are intact.

The preserved archive is
`DATASET_RESEARCH/VIFAILBACK_VERIFICATION/PORTABLE_REVIEW_EXPORTS/20261028T222841Z/VIFAILBACK_UNBLINDING.zip`.
Its SHA-256 is `e4ecf5315ff860c95a770833179500709c548a197fd07ea98399de9fe2b4b59c`. ZIP CRC, original export
receipt, and byte equality with the separate original key all pass. Every one
of20 key entries matches source episode identity, original HDF5 path, source
task/episode, native outcome and failure category in the pinned conversion.
All5,202 nested original annotations were separately rejoined to109 original
author JSON files and match exactly, with receipt hashes verified.

Conversion revision: `619791b94f61667333fe179d471051e0bca0e06f`.
Original revision: `21df46c2585c52e5a62df5f4b946bae6cbc6fed7`.
The comparison time and key/source hashes are in `UNBLINDING_VERIFICATION.json`;
the full original observations, confidence and identities are in
`LOCKED_PREDICTIONS_VS_NATIVE_LABELS.csv`.

| Case | Locked prediction | Native label | Comparison | Original episode | Native category |
| --- | --- | --- | --- | --- | --- |
| B01 | success | success | AGREEMENT | 775 | none |
| B02 | uncertain | failure | UNCERTAIN_RETAINED | 1827 | task planning |
| B03 | failure | failure | AGREEMENT | 4918 | gripper 6d-pose |
| B04 | success | success | AGREEMENT | 3666 | none |
| B05 | success | success | AGREEMENT | 3718 | none |
| B06 | failure | failure | AGREEMENT | 1574 | gripper state |
| B07 | failure | failure | AGREEMENT | 3723 | gripper 6d-pose |
| B08 | failure | failure | AGREEMENT | 789 | gripper state |
| B09 | failure | failure | AGREEMENT | 385 | gripper state |
| B10 | success | success | AGREEMENT | 1823 | none |
| B11 | success | success | AGREEMENT | 521 | none |
| B12 | success | success | AGREEMENT | 1453 | none |
| B13 | success | success | AGREEMENT | 371 | none |
| B14 | success | success | AGREEMENT | 4908 | none |
| B15 | failure | failure | AGREEMENT | 3467 | gripper 6d-pose |
| B16 | success | success | AGREEMENT | 4428 | none |
| B17 | success | success | AGREEMENT | 3456 | none |
| B18 | failure | failure | AGREEMENT | 532 | gripper 6d-pose |
| B19 | failure | failure | AGREEMENT | 3669 | task planning |
| B20 | failure | failure | AGREEMENT | 4570 | human intervention |


Among ten native no-failure episodes, ten locked predictions say success.
Among ten native failure episodes, nine locked predictions say failure and
one abstains. **19 agreements,0 disagreements,1 uncertain; decided agreement19/19,
coverage19/20.** B02's drawing ambiguity remains a low-confidence abstention;
the newly revealed failure/task-planning label does not retrospectively change
it. No20/20 accuracy claim is warranted. Sparse frames may miss transient events,
and native failure detection is not independently verified final mechanical success.

B20 independently noted a human hand and noncompletion; the native category is
human intervention. It remains an agreed case in this comparison, while its
original episode4570 is excluded from the restricted training/acquisition core.
Human involvement cannot automatically be inferred absent from other records.
No notes, object descriptions or confidence judgments were rewritten after
unblinding. No extra reviewer decision was invented for B02.
