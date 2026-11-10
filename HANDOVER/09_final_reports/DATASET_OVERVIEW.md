# HANDOVER dataset overview

A human–robot interaction domain with successful and failed completed trials, RGB and wrist wrench observations tests a second task and sensor contract.

589 native trials on Toyota HSR and Kinova Gen3, with 17 participants reported by the datasheet. Native participant IDs are not released.

All official archives, labels, class mapping and datasheet were downloaded from pinned Zenodo record 10708763, version v1. Official MD5 and independent SHA-256 hashes are recorded. Only required video/wrench/time/metadata members were extracted; unused flow/I3D data remain preserved in the complete checked archives. The sample is a training subset and is never an independent model test.

Released outcome IDs are verified from class_names.json: 0 success, 1 no approach, 2 no grasp (robot-to-human) or no release (human-to-robot), 3 drop. Binary failure is any native nonzero outcome. Trial IDs restart in each split, so identities are official-split-qualified; this is not a participant mapping. Native counts are 156 success, 131 no approach, 140 outcome-2 and 162 drop. The datasheet table has two more outcome-2 and two fewer drop cases; the released native files govern, and the binary failure total is unchanged.

Official source: [10.5281/zenodo.10708763](https://zenodo.org/records/10708763).
