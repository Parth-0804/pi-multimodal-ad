# Foundation audit protocol and corrections

This addendum records methodological corrections before any new training. It does
not overwrite the committed research contract or historical generated outputs.
The current user request authorizes Intel foundation work in its own application
boundary; the PHM scope documents continue to govern PHM work.

The first execution is descriptive only: no context classifier, encoder, fusion
model, calibration, threshold fitting or permutation experiment is run.

## Holdout incident

The pre-existing `02_label_audit.py` has no development-partition filter. Its
`--complete-only` option selects all complete samples. The existing context
report describes 2,723 samples across 169 sessions, the entire population from
which `03_make_split.py` subsequently proposed development and final-test sets.
Consequently those reported model outcomes incorporate proposed final-test
sessions. The script also fits a session-identification probe over that population.
Those artifacts do not constitute development-only evidence. Model provenance and
OOF predictions are absent, so exact execution history is not independently
reconstructible; the saved code and population counts are sufficient to reject a
claim that this holdout is pristine.

Retain the original files as evidence. Mark the proposed final holdout invalid,
keep `allow_final_test` false, and do not repair contamination by reshuffling the
same exposed sessions. A compliant recovery needs genuinely unexposed physical
sessions with adequate Good and non-Good support, or an explicitly approved
change to a development-only/exploratory thesis protocol with no untouched-test
claim. Downloading missing files for an already exposed session does not make
that session new. No replacement is chosen in this audit.

## Grouping and label support

Use manifest DIRECTORY as the documented session grouping, subject to physical
identity checks. Label constancy is a leakage risk; it does not prove that any
sample-level model necessarily learns session identity. Compare full-population
support with complete-modality support. Never silently restrict the population,
merge categories, or count repeated welds as independent sessions.

Identifier collisions, full-file SHA256 matches and possible repeated session
names must be reported separately. Exact-byte nonduplication cannot exclude
re-encoding, near-duplicates or shared physical sessions.

## Integrity measurement

Enumerate all manifest rows and reconcile with disk sample directories and files.
Hash full file contents, including images. Decode all FLAC samples, parse all CSVs,
decode all available images, and probe first/middle/last video frames. Video
container duration and frame counts remain metadata estimates. Decoder error
concealment and unprobed frames mean this is not complete video certification.
Record decoder warnings even if OpenCV returns a frame. Missingness denominators
are all manifest samples, with class and session tables retained.

Sensor cadence is estimated from positive adjacent parsed Date+Time differences;
report nonpositive steps and invalid timestamps. Rows/span is not the sampling
rate. Duration agreement alone does not establish temporal alignment. Raw global
timestamps, Part No, Remarks and path identifiers must not enter predictors.

The >5% integrity rule triggers missingness analysis, not automatic exclusion or
a declaration that the entire public dataset is unusable. Findings concern this
local copy. Structural full-population integrity checks do not constitute model
evaluation; no holdout signal features are used to tune choices.

## Alignment feasibility

Structural timing can establish whether a later alignment experiment is feasible.
It cannot establish small, stable, identifiable cross-modal lag. Envelope
cross-correlation, lag distributions and confidence remain unmeasured while the
holdout/leakage gate is unresolved. After recovery, predeclare a development-only
alignment experiment and acceptance thresholds before viewing signal results.
Sample-level fusion remains a future option; temporal cross-attention is disabled.

## Claim corrections

There are six nonempty missing-modality conditions for three modalities. The
seventh subset removes all inputs and is a separately labelled prior-only fallback;
it is excluded from ordinary modality-dropout training.

Unexpected attribution direction is a hypothesis about confounding, not proof of
it. An interval including zero is inconclusive rather than proof of equivalence.
Equivalence or noninferiority requires a predeclared practical margin. Every
transformation is fitted inside the appropriate training fold; threshold and
calibration fitting require inner-fold/cross-fitted development predictions when
reporting unbiased outer-fold scores.

The prior inventory's four-megabyte prefix hashes are not full-content hashes.
Equal-prefix files can differ later. Distinct prefixes do rule out exact equality,
but a complete identity audit must still retain full hashes and inspect CV and
image crossings, which the old split script did not comprehensively certify.

## Scope boundary

Do not invoke the existing `02_label_audit.py` or `03_make_split.py` to resume this
study: the former trains outside a protected development set and the latter
rewrites its fixed output paths. Keep both unchanged as pre-existing work.
Use `04_foundations.py` for the non-overwriting descriptive audit. Model commands
and final-evaluation enforcement are not implemented by this phase and must not
be claimed to exist.
