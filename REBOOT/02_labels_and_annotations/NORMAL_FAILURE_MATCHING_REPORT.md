# Normal/failure matching assessment

Investigation: `REBOOT/runs/20261028T192832Z-research-blockers-v2`. Snapshot: 2026-10-28T19:43:33.517787+00:00. Original pilot and published bytes remain unchanged.


No trustworthy matched normal/failure pair is currently established. The diagnostic pilot contains eight native-recovery candidates and two expert-collection candidates, all cylinder/install. Their source identities and exact windows are preserved in the original selection and separate review key; they are not ten binary-labelled examples.

| Matching variable | Evidence / remaining defect |
|---|---|
| Task and object | Cylinder-install is shared between sample recovery and expert candidates; other tasks lack machine-released phase/failure annotations |
| Phase | Recovery originating-phase candidates 1–4 have counts 14/13/4/14; onset-inside-phase diagnostic counts 2/12/3/5. Expert phase boundaries are absent; valid paired support is 0 in every phase |
| Camera | Same four camera keys, 640×480 and nominal 30 Hz for inspected examples; keys alone do not establish unchanged extrinsic calibration across sessions |
| Observation horizon | Diagnostic recovery windows include pre-induction and post-recovery-start context; expert candidates use whole episodes. Their durations differ and permit collection/phase/recovery-behaviour confounds |
| Physical collection / pairing | Recovery strings cover one dated session plus `initial`; expert sessions/pair IDs are absent. Equal episode numbers are not a matched pair |
| State measurements | Fourteen observed positions are available, distinct from fourteen commanded actions. Fixed feature extraction is technically possible but cannot create a target |

Do not train on the existing mismatched diagnostic windows. A future retrospective recognition protocol must freeze one window duration and index convention, compare the same object/task/phase/view and validate phase success for normal controls. If early warning is the intended endpoint, the observation horizon must end before the event and exclude recovery/future-action cues. Do not select per-class window lengths, camera crops or thresholds after examining holdout labels.

Exclude unresolved boundary/order records, unreviewed fine-contact or occluded events, missing expert phase controls, unresolved USB-C video offsets and unknown recording/pair bindings until corrected evidence is versioned. Record exclusion reasons rather than deleting source files. The original annotations are retained verbatim; no rejected record is silently repaired. Original-source absence and reviewer uncertainty are different statuses.

The human-derived alternative would require two independent reviewers, predefined normal/failure/uncertain criteria, time intervals with uncertainty, adjudication and agreement reporting. Negative windows must receive explicit clean phase-success verification. The prepared forty-row sheet collects visibility judgments; it is not by itself a complete binary event-annotation protocol or a replacement for physical-session metadata.
