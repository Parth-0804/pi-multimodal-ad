# Foundation-stage results review

**NO-GO for unimodal modelling.** This is a foundation review, not completed model
research. No new model was trained. See the [gate report](../../artifacts/intel_welding/audits/PHASE_1_GATE_REPORT.md)
for every gate's status, evidence, files, numbers and consequence.

1. **Dataset integrity.** All 4,040 samples / 236 sessions inventoried. Three
   deployable files exist for 2,723 samples; 2,707 pass structural readability
   probes. Missingness is class-dependent. Video certification is bounded.
2. **Label semantics and confounds.** Intended conditions, not verified physical
   defects. Each session has one category. Full-manifest process crosstabs exist;
   164 of 175 recipes map to one category. Recipe effects must be distinguished
   from physical signal in future work.
3. **Split validity.** Supplied SPLIT crosses 216 sessions. The prior proposed
   32-session holdout was included in the existing whole-population context audit;
   it is invalid for untouched-test claims. Its IDs and artifacts were preserved.
4. **Temporal alignment.** Duration/cadence feasibility measured, including 32
   invalid sensor timestamp series. No lag estimation completed; temporal
   cross-attention remains disabled.
5. **Unimodal signal.** Not evaluated; no claim of presence or absence.
6. **Representation comparison.** Not run; SQ1 remains open.
7. **Modality complementarity.** No valid development OOF predictions exist for
   the required comparison; not measured.
8. **Fusion results.** Not run; the two-informative-modality prerequisite is unmet.
9. **Gated architecture behaviour.** Not run; no adaptive-input-use evidence.
10. **Missing/degraded modality robustness.** Not run; no robustness claim.
11. **Calibration.** Not fitted or measured.
12. **Efficiency.** Model parameter count, memory, latency and throughput not
    measured. Audit runtime is not a model-efficiency result.
13. **Multiclass diagnosis.** Twelve manifest categories retained. Spatter,
    Undercut and Warping each have only one session with deployable files;
    group-disjoint evaluation cannot support all twelve classes in the local
    complete-case population. No silent nine-class substitution.
14. **Privileged image experiment.** Not run. Only 113 images across 24 samples;
    22 samples have five images and none of the Good samples has any. A binary
    teacher is unsupported by this local copy.
15. **Failed gates.** Gate 3 test protection fails and Gate 9 stays locked. Gates
    1/2/4 are conditional; Gates 5–8 are not evaluated, not provisional passes.
16. **Negative findings.** Incomplete local coverage, selective missingness,
    failed video probes, timestamp defects and prior holdout exposure. There are
    no negative model-performance results from this pass.
17. **Threats to validity.** Recipe confounding, nonexpert intended labels,
    session nesting, possible shared physical grouping, 20 colliding basenames,
    incomplete local data, video error concealment, unmeasured synchronization,
    under-supported classes and prior test exposure.
18. **Answers to SQ1–SQ4.** All empirical architectural questions remain
    unanswered. The audit supplies prerequisites and stopping evidence, not
    encoder, fusion, robustness or usability results.
19. **Answer to main RQ.** No empirical answer yet. A defensible study requires
    valid grouping, leakage-free evaluation, independently informative modalities
    and input-use controls before adaptive-fusion claims can be tested.
20. **Exact recommended thesis claims.** “The local dataset inventory contained
    4,040 intended-condition samples from 236 session directories. Only 2,723
    samples had all three deployable files, and 2,707 passed bounded structural
    readability checks. Missingness varied strongly by category. The supplied
    split crossed session boundaries, and a prior context study exposed the
    subsequently proposed holdout. Model comparison was therefore halted before
    new training.” Do not claim superiority, robustness, verified defect
    detection, or final-test performance.

Next action: researcher review of holdout recovery and the population/integrity
policy. Additional unexposed Good and non-Good sessions would support a new
preregistered final test. A development-only exploratory protocol is a separate
change requiring explicit approval; it has not been adopted.
