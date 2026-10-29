# Complete release audit, conservative cohort and group independence

The whole pinned **metadata and numerical release** was audited, rather than
only the pilot. Every one of5,202 native labels matches original annotations;
episode/task/instruction/frame-length joins and all numerical row/global/frame
indices match. All15,606 published RGB paths exist in the pinned inventory.
Inventory presence and publisher SHA-256 identity are not whole-video decoding
or semantic proof that a camera sees the intended event. No source file was
removed or rewritten.

## Native semantics and counts

Native `annotation.failure_detection` yes/no is the primary target. The
conversion's `episode_success` is derived from that field. Do not equate it with
a separately mechanically measured end-state success label or frame-level fault
onset. Native counts are4,545 failures/657 no-failure episodes; categories are
2,771 gripper6D-pose,988 gripper-state,645 task-planning and141 human-intervention.
All100 canonical task instructions initially contain both labels;109 source
directories contain nine task variants. Source-directory suffixes are not
verified sessions.

## Eligibility versions and exclusions

All5,202 Parquet payloads match official release hashes and pass schema/identity/
finite-value checks. Scientific QC is stricter than valid parsing. V1 quarantines
173 fully constant position traces and six higher-ID exact duplicate copies,
then restricts away141 native human-intervention records:319 unique exclusions,
4,883 candidates. There is one overlap between the duplicate and native human
flags. This screen is retained unchanged.

V2 additionally quarantines canonical task55 (`pick_place_chem_ep1` and `_ep2`)
pending coordinate-convention clarification:500 native episodes,483 failures and
17 no-failure records. One was already a duplicate;499 additional V1 candidates
are removed. In498/500 episodes the median signed position-derivative/velocity
correlation is negative; group medians are approximately-0.91. This is a
systematic native-coordinate issue, not a conversion mismatch or established
bad-label finding. The input-derived rule requires at least20 diagnostics,
more than95% negative medians and group median below-0.5; it selects only task55.
Gross position/velocity spikes are also quarantined explicitly:3 position and6
velocity episodes,8 distinct. Those are already covered by task55 or a native
human flag. Threshold10 is in uncalibrated native units: a conservative
mixed-scale quarantine, not an asserted physical joint limit.

The proposed primary V2 core has **4,384 episodes:3,755 native failures/629
no-failure,99 tasks,all with both labels**. Its818 unique exclusions/quarantines
are enumerated with all overlapping reasons in
`V2_CONSERVATIVE_CORE/CORE_ELIGIBILITY_AND_EXCLUSIONS_V2.csv`.
`ELIGIBLE_CORE_EPISODES_V2.csv` gives every retained original identity. B02 is
retained: visual abstention does not invalidate an otherwise verified native label.

The native-human restriction explicitly uses outcome-derived annotation metadata.
It defines a restricted estimand, not label-blind QC, and cannot prove the
remaining clips have no people. The all-native and5,023-row sensor screen are
preserved for sensitivity planning; do not compare scores on different cohorts
as though they were paired architecture improvements.

## Exact duplicates and dependence

All three published camera hashes and all actual state/velocity/effort arrays
match for these six pairs:372/375,851/855,2345/2445,2462/2484,2841/2868,4114/4124.
Native labels agree within every pair. Keep the smaller original ID in derived
cohorts and preserve every raw copy. All Parquet files have distinct file hashes,
so per-file Parquet hashes alone would miss this duplication. The complete
numerical-content hash search finds exactly the same six components. A separate
32-position,3-decimal position-signature search yields additional candidates,
largely stationary/bad traces; it is not exhaustive near-duplicate detection.

Grouping transitively joins canonical task identities and exact numerical/video
components. No remaining cross-task exact component forces extra merges. There
are99 V2 task groups. Sessions/operators/dates/robot serials/object instances
are not supplied in the audited metadata; `_ep1`/`_ep2` are not session evidence.
Shared objects, setup and related instructions can cross task folds. This
protocol evaluates held-out tasks under the released setup, not new robots,
sites, operators, scenes or genuinely new physical object instances.

## Enumerated split plan

Five outer task-disjoint folds and four inner folds use a label-blind SHA-256
ordering of task-component IDs with seed20261029. Views, frames, sensor rows and
duplicates of an episode never split apart. Every fold has both labels. Actual
train/validation/test IDs are in `V2_CONSERVATIVE_CORE/OUTER_INNER_SPLITS_V2.json`;
all20 triples are complete, disjoint and independently asserted.

| Outer test fold | Test tasks | Test episodes | Failure | No failure |
| --- | --- | --- | --- | --- |
| 0 | 20 | 934 | 789 | 145 |
| 1 | 20 | 607 | 484 | 123 |
| 2 | 20 | 572 | 512 | 60 |
| 3 | 20 | 1475 | 1293 | 182 |
| 4 | 19 | 796 | 677 | 119 |


`BASE_FIT_T_V_C_ASSESSMENT_V2.json` enumerates25 base fits per visual condition/
seed:four inner OOF fits and one outer-assessment fit for each outer fold.
Within each fitting pool, hashed task groups are assigned60% T(model/scalers),
20% V(epoch/hyperparameter choice),20% C(calibration). Assessment groups are
excluded from all three roles. Every role has both outcomes. The same plans
apply to sensors, visual branches, initialization conditions and all seeds.
Only inner-assessment probabilities become final F2/gate training rows. Fixed
fusion hyperparameters avoid leaky meta-selection; any later tuning requires
an additional nested level of branch predictions, not just a split of already
computed OOF rows.

## Availability and immediate acquisition requirements

**Remote published missing paths:0.** Local whole-RGB verification is different:
only19 V2 episodes have already decoded all three pilot views. **4,365 V2 episodes
remain unverified as actual video payloads**. V2 is therefore an exact
acquisition/protocol core, not a certified whole-visual training set.

| Scope | Files | Published bytes | Additional local files | Additional bytes |
| --- | ---: | ---: | ---: | ---: |
| Primary high camera | 4,384 | 10,083,704,389 | 4,365 | 10,033,575,648 |
| All three cameras | 13,152 | 24,738,151,213 | 13,095 | 24,617,630,045 |

Every required filename/size/SHA-256/local verification state is in
`V2_CONSERVATIVE_CORE/REQUIRED_RGB_FILE_MANIFEST_V2.csv`. All5,202 numerical tables
are present;5,180 new tables used213,092,922 bytes,22 existing tables were reused.
No full-corpus videos were downloaded in this follow-up. Later acquisition must
use the pinned revision, verify checksum/frame count/PTS/16-frame decoding and
document human/overlay/visibility QC independently of outcomes. Any changed
eligibility produces a new version and preserves the current manifests; never
reshuffle splits in response to model/test performance.
