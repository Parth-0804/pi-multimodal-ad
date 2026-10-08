# Proposed split disposition and holdout incident

The existing proposal has 137 development sessions
(2,191 samples) and 32 final-test sessions
(532 samples), based on complete-present data. Its ID hash is
`e72d907291304487a53e040c1080f03dc4d3361b27256c69fb3056527a7e0c2d`. Its full JSON SHA256 is
`6f713721424feab9d1d5cb9f6d3dd3245f4227ca8e63c774fcc2f48bf96725d3`. Original files remain unchanged.

Membership is session-disjoint; all five folds exclude proposed final sessions,
cover development, and separate train/validation groups. Full-content hashes
show no exact duplicate crossings. Multiclass coverage fails for single-session
categories: Spatter, Warping and Undercut each occur in a validation fold without
training support. No performance-based split search was performed by this audit.

**Disposition: INVALIDATED_FINAL_HOLDOUT.** The pre-existing context report
and code cover all 2,723 complete samples across all 169 eligible sessions,
including the 32 subsequently proposed final-test sessions. OOF predictions and
complete provenance are missing, so this is a conservative exposure finding from
saved evidence, not a reconstructed execution trace. No pristine-test claim is
credible. The new configuration and disposition keep `allow_final_test: false`.
This is an audit lock status; no general-purpose final-evaluation CLI is implemented.

A fresh random partition of the exposed sessions cannot restore independence.
All 55 Good sessions in the manifest already belong to that exposed population.
The 67 sessions without complete data contain no additional Good sessions;
finishing this local download alone cannot produce a pristine binary test cohort.
A clean test requires genuinely unexposed physical sessions with both classes,
or a researcher-approved development-only protocol that abandons untouched-test
claims. Do not silently choose the latter or claim an immutable valid split now.

Recommended exact next action: review the exposure record and decide whether to
obtain independent Good/non-Good sessions. Resolve the physical grouping of
colliding sample IDs and the missing/corrupt-file policy, then freeze a new
preregistered evaluation contract before training. Until then all modelling stays
blocked. No replacement split or new model was created.
