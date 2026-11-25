# Phase A/B gate report

2026-09-27T15:20:23.251296+00:00

| gate | status | evidence | artifact |
| --- | --- | --- | --- |
| G0 STORAGE | PASS | "403.36 GiB before download >=160" | runs/reassemble/20260927T141645Z-inventory/acquisition.json |
| G1 DOWNLOAD CHECKSUM | PASS | "All four official MD5 values matched; all three ZIP CRC tests passed before extraction" | runs/reassemble/20260927T141645Z-inventory/acquisition.json |
| G2 LABEL SUPPORT | PASS | {"segments": 4551, "failures": 516, "successes": 4035, "recordings": 149, "failure_recordings": 131, "success_recordings": 148} | label_audit.md |
| G3 MODALITY COMPLETENESS | PASS | {"selected": "visual_sensor", "segments": 4530, "failures": 509, "successes": 4021, "recordings": 148, "failure_recordings": 130, "success_recordings": 147, "audio": "CONDITIONAL; secondary only"} | modality_selection.json |
| G4 GROUP LEAKAGE | PASS | {"split_error": null, "overlapping_acquisition_pairs": 0, "exact_recording_duplicates": 0, "combined_sensor_duplicates": 0, "models_trained": 0} | leakage_audit.json |

Primary proposed cohort: **visual_sensor**; camera **hand**.

{
  "all_annotations": {
    "segments": 4863,
    "failures": 517,
    "successes": 4346,
    "recordings": 149,
    "failure_recordings": 131,
    "success_recordings": 149
  },
  "primary_actions": {
    "segments": 4551,
    "failures": 516,
    "successes": 4035,
    "recordings": 149,
    "failure_recordings": 131,
    "success_recordings": 148
  },
  "dual_complete": {
    "segments": 4530,
    "failures": 509,
    "successes": 4021,
    "recordings": 148,
    "failure_recordings": 130,
    "success_recordings": 147
  },
  "tri_complete": {
    "segments": 0,
    "failures": 0,
    "successes": 0,
    "recordings": 0,
    "failure_recordings": 0,
    "success_recordings": 0
  }
}

Audio is decoded and its nominal quality inventoried, but cross-modal timing
is not independently established by the stored schema. Audio therefore remains
secondary; a visual+sensor study is allowed by the master specification.
Physical F/T/gripper defects are conservatively excluded at the affected
segment/modality level based on the official README. Full issue evidence and
unresolved verification limits are in known_issues.json.

No model training or predictive-results search occurred. G5–G14 are not
evaluated; storage/label/coverage support is not evidence of useful modality
signal. Independent signal and permutation gates still precede fusion.

PHM runs, artifacts, checkpoints, configurations and Git history were preserved.
Official loader reference: 432cc15ce3e028edc2f98a786f28bf6baf31ac6f.
Dataset DOI: 10.48436/0ewrv-8cb44. Full acquisition, archive inventory, per-file
checksums and configuration are recorded in `runs/reassemble/20260927T141645Z-inventory`.

Next action: researcher review of this cohort, audio limitation, known-issue
handling and nested split manifest before approving baseline/modelling work.
AGENTS.md requires phase-boundary review; master specification section 71
explicitly preserves this requirement.

## Final validation and retained evidence

32 synthetic tests passed. The environment dependency check and Git whitespace
check passed. All 68,745 previously protected files matched their recorded
size, nanosecond mtime and mode; the historical Git blob remains present.
Remaining free space after extraction/media caches is 95.46 GiB. All original
archives are retained. See validation.json and storage_actual.md.

The official split is disjoint but omits one recording; see
grouping_leakage_audit.md for its identity, outer-fold support and exclusion counts.
The complete 5x4 split manifest is nested_splits.json. Audio remains conditional
and secondary, so this GO applies to the visual+sensor readiness decision.
No predictive signal or fusion-benefit claim has been established.

A missing optional Markdown formatter affected only the first report-generation
attempt. A dependency-free formatter and regression test resolved it. Original
partial evidence and the successful reports_v2/tables_v2 are retained in the run;
existing machine-readable evidence was byte-identical before publication.

The continuation handoff is docs/reassemble/CONTINUATION.md. Researcher review is
required before any baseline or model training under AGENTS.md.

GO FOR REASSEMBLE MODELLING
