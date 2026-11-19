# Native annotation contract and limits

The authentic released file is preserved unchanged. It describes `phase_names`, six `tau_0..tau_5` boundaries, episode type/duration, `failure.originating_phase`, categorical `failure_mode`, `induced_at_frame`, `recovery_started_at_frame`, language descriptions, native operator and collection-session strings. It does not supply a certified negative interval, per-frame binary array, failure-resolution frame, explicit expert/recovery pair registry or annotation confidence.

A recovery demonstration is not failed throughout its duration. Neither induction-to-recovery-start nor the remainder of a phase is automatically a verified binary failure interval; recovery-start is not proof of failure-end. Expert-name membership also does not certify the temporal boundaries of a clean comparison phase. No binary target has been assigned to the diagnostic examples.

## Findings requiring resolution

- All60 `duration_frames` values are897; actual released lengths are898(54 episodes) or899(6). This may include a last-index versus count convention; that convention is not documented. It is reported, not silently corrected.
- The originating-phase values include0 and21 alongside1–5. No automatic0→1 or21→2 repair is applied.
-38 induction times lie outside the declared phase under a **tested one-based occurrence interpretation**. Because the field is named *originating* phase, it could refer to an earlier causal phase; this discrepancy requires an author definition and is **not proof that all38 labels are false**.
- Three records put recovery at/before induction under a shared-frame-clock interpretation, and one has nonmonotonic phase boundaries.
- The JSON names the plural `sample_recovery-demonstrations`, while the actual repository is singular `sample_recovery-demonstration`. The exact shared videos bind the sample to the full cylinder-recovery recording, but do not validate every annotation value or establish the undocumented plural alias.

Full per-record diagnostics, including original values, are in NATIVE_PHASE_RECORD_AUDIT.csv/JSON. All60 source annotations remain available. No frame-level labels, participant identities, success outcomes or corrected event times are invented.

## Requested pilot support

| Requested phase | Native candidate records | Onset inside phase under tested one-based interpretation | Verified pairs | Diagnostic recovery episodes |
|---|---:|---:|---:|---:|
| Align (pick) | 14 | 2 | 0/5 | 2 |
| Engage (pick) | 13 | 12 | 0/5 | 2 |
| Transport | 4 | 3 | 0/5 | 2 |
| Align (place) | 14 | 5 | 0/5 | 2 |

The onset consistency column is a diagnostic filter, not a certified-label count. Only four raw Transport-origin records exist in this annotation file before any validity checks, so even five positive candidates for that phase cannot be obtained here. Complete metadata inspection found no phase-matched negative labels. Therefore the requested20 verified pairs cannot be assembled from the verified release evidence.

Ten diagnostic examples were still inspected to assess cameras and measurements. Candidate recovery windows include context before induction and after recovery-start; expert candidates show whole episodes. They are **not phase-matched comparisons or training-ready examples**. Window lengths/source collections can affect blind-review difficulty; no diagnostic review accuracy or fusion efficacy is calculated.
