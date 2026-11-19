# Final dataset recommendation

**Recommend FAILURE for the next small blinded visual-plus-audio pilot.** This recommendation is based on independently verified original labels and same-action modality inventories, not publication performance. No candidate currently establishes a real-world visual-plus-force/joint-state cohort. CRIA was removed at the researcher's request.

RoboFAC is NO-GO for the current real-world multimodal target because numerical counterparts are absent. Its simulation data have unresolved label/identity issues and contain simulator states rather than the required real observations. FAILURE receives **GO FOR VISUAL PILOT** for a clearly declared RGB+audio question; the eventual experiment remains CONDITIONAL GO until visual observability, modality completeness, licensing and group design are reviewed.

## Proposed prediction target

One prediction per complete original manipulation recording: native **1=failed action, 0=successful action**. Use sixteen ordered RGB frames from that same action and statistical summaries of its paired measured audio. An outcome label must not be propagated as a time-local failure label to arbitrary partial windows. There is no valid released failure-onset timestamp in the annotation ZIP. The detector target differs from failure-mode classification, anomaly anticipation and robot-sensor fusion.

This is an explicit audio adaptation to be reviewed, not an automatic replacement of the numerical modality. If the thesis requires measured proprioception/force as its second modality, the recommendation is **NO-GO for both remaining candidates pending new data**, and this audio pilot should not be represented as fulfilling that requirement.

## Minimum corpus-linked review

Five successful/failed pairs, one per action, chosen by same date and nearest endpoint duration, with lower numeric IDs breaking ties. This uses no model performance and makes no assumption that objects or views match:

| Pair | Action | Success ID (0) | Failure ID (1) | UTC date | RGB endpoint span s: success / failure |
| --- | --- | --- | --- | --- | --- |
| 1 | push | 36 | 22 | 2018-02-17 | 63.69 / 63.69 |
| 2 | place | 19 | 27 | 2018-02-18 | 118.75 / 118.71 |
| 3 | pour | 24 | 5 | 2018-07-11 | 80.37 / 80.37 |
| 4 | put_in | 43 | 47 | 2018-07-05 | 98.34 / 98.31 |
| 5 | put_on | 24 | 30 | 2018-03-19 | 98.03 / 98.03 |

For each of these ten identities obtain sixteen uniformly spaced existing RGB frame files, the same-stem original timestamp files, and the corresponding WAV. There are **160 RGB images, 160 timestamp text files and 10 WAVs**. All proposed original members and byte sizes are enumerated in `checks/FAILURE_PROPOSED_PILOT_MEMBERS.json`. Proposed compressed member bytes total **113,012,633 (113.013 MB)**; extracted bytes total **125,393,705 (125.394 MB)**. Allow about **0.25 GB** for payload plus retained compressed ranges, additional small metadata, and diagnostic contact sheets; all estimates exclude optional depth. Fetching the complete ZIP is unnecessary if byte ranges remain supported.

Required supporting source files are the already preserved original annotation ZIP, original central-directory inventory and timestamp-derived identity table. Preserve original CRCs and compute per-member SHA-256 on acquisition. Verify every decoded image and WAV, distinct frame positions, ordering, timestamps, audio duration, object/view matching, and duplicate-content hashes. Do not label-reorder frames or optimize offsets against outcomes.

Object identity is currently UNKNOWN; closest duration does not establish scene matching. A blinded reviewer should explicitly rate it. The sample is for diagnosing feasibility, not estimating accuracy: it has 50% failures by design whereas the joined cohort has 64.192% failures. If the sparse frames miss the failure, add a declared denser sequence from the same action rather than changing its ground truth.

Before a full experiment, confirm data-use terms, characterize alignment uncertainty, choose a group-disjoint design accounting for task/date confounding, freeze the training-only selection/fusion protocol, and obtain researcher review. This audit does not authorize acquisition of that pilot or any training.
