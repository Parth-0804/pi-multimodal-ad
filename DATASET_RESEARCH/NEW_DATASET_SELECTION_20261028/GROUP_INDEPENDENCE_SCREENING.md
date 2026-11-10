# Group-independence screening

This is feasibility screening, not a frozen evaluation protocol. No frame-level random split is proposed. All source windows, crops, modalities and camera views of an action must share a group, and all preprocessing/model selection/fusion fitting must remain inside training groups.

## FAILURE

Use `(action, recording_id)` as the minimum source identity: numeric recording ID alone collides across actions. There are 229 labeled complete-modality recordings. Original first/last timestamp files were retrieved for every recording and verified against ZIP CRCs; seven observed UTC dates contain both classes:

| UTC date | Failed (1) | Successful (0) | Total |
| --- | --- | --- | --- |
| 2018-02-17 | 19 | 12 | 31 |
| 2018-02-18 | 37 | 15 | 52 |
| 2018-03-19 | 21 | 9 | 30 |
| 2018-07-04 | 14 | 6 | 20 |
| 2018-07-05 | 14 | 15 | 29 |
| 2018-07-11 | 20 | 13 | 33 |
| 2018-07-12 | 22 | 12 | 34 |

Seven-fold leave-date-out evaluation is class-defined on both sides in every fold: all held-out dates and their complements contain failures and successes. This is a possible outer sensitivity analysis; it does not establish seven independent operators or true sessions. Group-based inner validation must use only the remaining dates. Splits need no test-result inspection to define them.

Important confounding: push occurs only on 2018-02-17, place only on 2018-02-18, and put_on only on 2018-03-19. Pour covers 2018-07-11/12; put_in covers 2018-02-18 and 2018-07-04/05. Holding out some dates also holds out an action; report this explicitly. Leave-action-out across five actions has both classes in every fold but tests task shift, not same-task replication. Episode-disjoint stratified grouping is possible, but weaker concerning shared recording conditions. Object IDs, operator IDs and camera-session reset identities remain unavailable.

Avoid letting adjacent recordings from one session cross partitions when session boundaries can later be established. Timestamp dates are a transparent conservative proxy, not proof of absence of duplicates. All payload members must be hash-screened in the actual pilot before claiming duplicate-free examples. No full corpus payload hash scan occurred here.

## RoboFAC

Real data have 602 episode-path groups and two views per group. Every one of six task directories has both outcomes; counts are in ROBOFAC_LABEL_AUDIT.md. Keep views together. No corresponding real numerical recording exists in the audited release.

Simulation metadata reuse 326 UUIDs; 76 UUIDs have conflicting success flags. Scene, original reset seed, camera variations and related injected-error trajectories can create dependent examples. Union repeated UUIDs and original scene/reset lineage when available. Exact kinematic content hashes are distinct for all 679 HDF5 files, which does not prove independent resets. No defensible independent numerical cohort or class-support split is frozen for this candidate while the label/link issues remain unresolved.

The official training and test QA files overlap by 6,715 video paths. Reusing that division would leak source episodes into both partitions for this classifier.
