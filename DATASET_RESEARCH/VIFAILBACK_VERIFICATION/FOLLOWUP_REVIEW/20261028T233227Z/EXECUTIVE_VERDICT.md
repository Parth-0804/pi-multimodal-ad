# Executive verdict — ViFailback independent verification

**Scientific feasibility: GO for supervised RGB plus observed robot-state fusion
on an explicitly restricted cohort. Training readiness: NO-GO at this boundary.**
The remaining whole-video checks and researcher review are required before a
full experiment starts. This is not a dataset rejection, a trained result, or a
claim that fusion/weight transfer will help.

The independent AI-assisted visual review was locked byte-for-byte before key
comparison: SHA-256 `308b478c0a29d4601ed2446c95e0257ea932c9ed128f3bf5d75b7baeed5010d2`. All **19 decided judgments agree**
with the source labels; **zero decided disagreements**; **B02 remains uncertain**
and its native label is failure. Decision coverage is19/20. The selected pilot
does not estimate population accuracy, human annotation reliability or ML skill.

| Evidence level | Exact result |
| --- | --- |
| Native original annotation records and converted joins | 5,202; 4,545 native failures /657 no-failure records |
| Actual numerical payloads verified against source SHA-256 | 5,202 tables; 1,297,146 rows; no nonfinite measurements |
| Published RGB inventory and same-ID numerical joins | 15,606 videos; all three camera paths present per episode |
| Constant-position quarantine | 173 episodes, including11 no-failure records |
| Exact multimodal duplicate components | Six pairs; six higher-ID copies excluded from derived cohorts |
| Native human-intervention category | 141 episodes; restriction is outcome-derived, not independent human detection |
| New coordinate-convention quarantine | Entire canonical task55:500 episodes; 499 additional exclusions beyond V1 |
| Conservative V2 core | **4,384: 3,755 failure /629 no-failure;99 tasks, all with both labels** |
| Union of excluded/quarantined native episodes | **818**; individual reasons overlap |
| V2 episodes already covered by decoded three-camera pilot | **19**; B02 retained despite visual abstention |
| V2 episodes awaiting full RGB payload checks | **4,365** |

The original 4,883-row screen is preserved, but it missed gross finite spikes and
a task-dependent coordinate relationship. Values include position33070.77734375,
position-292.6617431640625 and velocity28.92799949645996 in native units. For
input-selected episodes2791,3034,5080, all nine original-HDF5/converted observation
array comparisons have maximum error zero. Only160,512 numerical/metadata bytes
were ranged from their original files; original videos were not downloaded.
No signs or values were silently corrected. The conservative500-episode
quarantine means unresolved calibration, not that these labels are wrong.

Fourteen position, twelve nonplaceholder velocity and two gripper-effort fields
provide28 candidate measured channels. They are **not force/torque**. Native
units/calibration and per-device hardware clocks remain unverified.

Five outer and four inner task-disjoint partitions and25 base-fit T/V/C/
assessment plans are enumerated for V2. Canonical task groups do not establish
independent operators, sessions, scenes, object instances or robots.

REASSEMBLE's original extractor is RT-DETR-R18VD's CNN only; stage-map spatial
means concatenate to896 features and sixteen frames are averaged. The completed
100-epoch source study has a valid full-backbone checkpoint selected at epoch47:
115 compatible CNN tensors,69 changed, with updates across the stem and all four
stages; running moments unchanged. Its selected-split AP is0.2125845033 versus
0.1937755776 for the frozen control. The saved paired AP interval includes zero.
The larger active full-CNN study has **3/75 completed fits** in
the timestamped snapshot. **No ViFailback weight transfer has been performed.**

The proposal includes visual-only; balanced sensor logistic; sensor HGB;
probability averaging; newly fitted static F2; quality-only F5 gating; frozen/
full-CNN25/50-epoch budgets; seeds42,123,20261023. All models use identical held-out
episodes and nested lineage. Native failure AP is primary, with success AP,
AUROC, calibration and grouped uncertainty because V2 failure prevalence is
85.652372%. No results were inspected to choose this proposal; no model was fit.
