# Group independence and leakage screening

## What is genuinely identified

5,202 native source episodes are uniquely indexed; each has one original HDF5 path and three converted views. All views, frames, crops, statistics and any future windows of one source episode must remain together. There are **100 canonical task groups**, not 109 independent tasks; all 100 have successes and failures. The canonical task mapping combines nine source-directory variants, including the `_ep1`/`_ep2` variants. Directory suffixes are not verified session IDs.

No original operator, collection-date, robot-serial, recording-session, scene-instance or object-instance identity field was found in the annotation/episode metadata. The checked original HDF5 attributes contain no such identifiers. Publication/repository timestamps must not be used as collection dates. The platform/setup and objects are shared across tasks, and demonstrations may be intentionally perturbed or collected in batches. Distinct filenames are not proof of statistically independent executions.

The [original paper, v3](https://arxiv.org/html/2512.02787v3) describes its own ALOHA collection: 4,995 teleoperated trajectories and 207 policy rollouts. These are author-reported collection totals; no reliable per-episode teleoperation/policy tag was found in the audited metadata. ViFailback's independent publication and original trajectory provenance support an external-dataset study, but an exhaustive cross-dataset near-duplicate comparison against REASSEMBLE was not performed. Do not claim independent operators, robots, or collection regimes from the source identity alone, or infer a policy/session from an `_ep2` suffix.

## Exact duplicate components

All 5,202 Parquet file hashes are different, partly because episode/global-index fields differ. The video inventory has 18 byte-identical pairs: the same six episode pairs repeat independently across all three views. The six complete published sensor-statistic signatures also repeat for these pairs. No conflicting native outcome was found in these components.

| Shared-video episode IDs | Canonical-source relationship |
| --- | --- |
| 372, 375 | same original task; same failed outcome; all three cameras identical |
| 851, 855 | same original task; same failed outcome; all three cameras identical |
| 2345, 2445 | same original task; same failed outcome; all three cameras identical |
| 2462, 2484 | same original task; same failed outcome; all three cameras identical |
| 2841, 2868 | same original task; same failed outcome; all three cameras identical |
| 4114, 4124 | same original task; same failed outcome; all three cameras identical |

Preserve all raw files. For a prospective evaluation, either retain a deterministic representative per fully verified duplicate component or give the entire component one group and explicitly avoid double-weighting duplicates in reported performance. Native counts remain 5,202. A file hash on the Parquet alone is not a sufficient leakage guard.

The provisional exclusion of the higher-index copy from each pair and quarantine of 173 constant-position episodes removes **179** rows, with no overlap between these two flags. It leaves **5,023** metadata candidates, **4,377 failed / 646 successful**, and both outcomes in **all 100 task groups**. These are planning counts pending complete raw-data QC; no model-ready full cohort is certified.

## Defensible prospective splits

The conversion supplies only `train: 0:5202`; it has no author-provided independent supervised train/validation/test partition. Do not treat the directory named train as a held-out protocol or select split settings from outer-test performance.

Primary proposal: freeze the eligible cohort and group map before model work, then use **five outer task-disjoint folds**, with **four inner task-disjoint folds** restricted to each outer-training partition. Canonical task IDs serve as grouping metadata only, not ordinary predictors. All directory variants, episode views and duplicate components stay together. Verify class support and every train/validation/test intersection by assertion. All outer-test outcomes remain assessment-only; any architecture/hyperparameter/calibration/threshold/fusion choice uses inner data.

Because every canonical task has both outcomes before and after the provisional screen, class support across reasonable multi-task folds is feasible. Exact fold assignments and cohort exclusions are **not frozen in this feasibility stage**. Low success counts in some tasks make within-task repeated nested folds fragile; avoid treating three camera views or sixteen frames as independent class support.

A secondary episode-disjoint, within-task analysis can estimate new-execution performance under similar tasks, but cannot establish new-task/session independence. A stronger object/scene-family split needs an independently curated, verified group map; natural-language task names are insufficient proof of object-instance identity. Neither design supports new-robot robustness or unrestricted cross-domain generalization on its own.

Use paired task-cluster uncertainty for model differences and report all seeds/folds. Do not count overlapping folds, seeds, video views or frames as independent replicates. This audit checked duplicate source identities and exact inventory hashes, not all near-duplicate trajectories or hidden session dependencies.
