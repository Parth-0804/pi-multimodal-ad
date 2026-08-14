# Cross-modal timeline and candidate-alignment audit

Status: **PARTIALLY_COMPLETE_BLOCKED_BY_UNVERIFIED_IMAGE_CLOCK_DOMAIN**

## Evidence coverage

- Canonical events: 22928
- Timeline groups: 56
- Image-to-sensor/scalar audit rows: 9177
- Verified comparable image-to-sensor joins: 0
- Images with verified UTC timestamps: 0
- Images with local-naive timezone-unknown timestamps: 640
- Images with missing timestamps: 671
- Candidate scalar targets: 0
- Blocked raw-source traces: 5

## Six-hour cadence evidence

- Reference interval for observed comparison: 21600.0 seconds
- Configured comparison tolerance: 60.0 seconds
- Timeline groups with at least one observed matching interval: 0
- Interpretation: observed adjacent-timestamp cadence evidence only; no target-horizon claim.
- Coverage-gap count: not inferable because no expected cadence contract is established.

## Scientific blockers

- Image timestamps may be local-naive or missing and cannot be joined to UTC sensor time without evidenced clock comparability.
- The candidate scalar target name, physical meaning, unit, scope, and timestamp are unresolved.
- The six-hour statement has not been established as cadence, history length, or forecast horizon.

No interpolation, target synthesis, model sample, or damage/health label was produced.
