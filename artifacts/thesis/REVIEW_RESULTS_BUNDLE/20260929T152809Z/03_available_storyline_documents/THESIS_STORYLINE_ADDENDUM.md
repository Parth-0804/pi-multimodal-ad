# Thesis storyline addendum

Chronological reasoning narrative for later integration into the external master record. That record was not edited.

## PHM as the first study

**ASSUMPTION:** Multimodal architectures might support continuous damage estimation.

**QUESTION:** Are target validity and deployable sensor information sufficient?

**WHY IT MATTERED:** Fusion requires a defensible target and usable signals.

**METHOD:** Retained provisional target audits, fixed/grouped evaluations and LOEO summary.

**RESULT:** The grouped fusion comparison did not resolve benefit over a constant; only 20 runs support uncertainty.

**INTERPRETATION:** Target and independent-unit constraints precede architecture claims.

**STATUS:** [VERIFIED]

**CONSEQUENCE:** Keep PHM as Study 1; do not relabel its weak/uncertain evidence as success.

## Why a second study became useful

**ASSUMPTION:** A second task could separate architecture questions from PHM target/deployment restrictions.

**QUESTION:** Can explicit labels and simultaneously available modalities support a clearer fusion test?

**WHY IT MATTERED:** One constrained dataset cannot establish broad architecture suitability.

**METHOD:** Select a complementary study with explicit outcomes and recording groups.

**RESULT:** REASSEMBLE ultimately supplied these prerequisites.

**INTERPRETATION:** The second study complements rather than erases PHM.

**STATUS:** [VERIFIED]

**CONSEQUENCE:** Keep different task-appropriate metrics and avoid cross-task score rankings.

## Intel reconsideration

**ASSUMPTION:** The local robotic-welding dataset might support the second study.

**QUESTION:** Are labels, grouping, modality availability and holdout status defensible?

**WHY IT MATTERED:** Invalid foundations cannot be repaired by more training.

**METHOD:** Read-only foundation audit; artifacts/intel_welding/audits/PHASE_1_GATE_REPORT.md.

**RESULT:** The supplied split crossed 216/236 sessions; prior holdout exposure and selective missingness led to NO-GO.

**INTERPRETATION:** Do not present exposed/context-confounded results as clean validation.

**STATUS:** [NOT RUN — GATE FAILED]

**CONSEQUENCE:** Move to another foundation without rewriting Intel evidence.

## REASSEMBLE selection

**ASSUMPTION:** Execution segments may support visual/sensor failure prediction.

**QUESTION:** Do coverage, labels and recording identity permit grouped evaluation?

**WHY IT MATTERED:** Modality existence alone does not ensure usable multimodal support.

**METHOD:** Foundation inventory, source identities, sensor/video quality and label audit.

**RESULT:** The frozen primary cohort contains 4,530 segments, 509 failures, 148 usable recordings.

**INTERPRETATION:** Visual+sensor modelling is feasible; audio requires a separate clock gate.

**STATUS:** [VERIFIED]

**CONSEQUENCE:** Freeze cohort, labels and nested recording folds.

## Storage constraint and PHM retirement

**ASSUMPTION:** Keeping all large raw datasets locally exceeded available disk.

**QUESTION:** Could PHM raw payloads be retired without losing recoverability or research evidence?

**WHY IT MATTERED:** Storage pressure must not cause undocumented scientific data loss.

**METHOD:** Previously user-authorized recovery manifest, official-source validation, bounded range test and protected-file audit.

**RESULT:** Historical retirement recovered about 355.283 GiB; full SHA256 recovery specification and research outputs were preserved.

**INTERPRETATION:** This was a specific historical authorization, not permission for new deletion.

**STATUS:** [VERIFIED]

**CONSEQUENCE:** Retain recovery mechanism; current completion performs no deletion or redownload.

## Acquisition and foundation

**ASSUMPTION:** Downloaded data could differ from nominal documentation.

**QUESTION:** Does the local copy match audited identities and support the intended task?

**WHY IT MATTERED:** Reproducibility depends on local evidence, not assumed dataset claims.

**METHOD:** Versioned acquisition/inventory and complete source provenance.

**RESULT:** 149 raw recordings inventoried; 148 enter the fixed primary cohort.

**INTERPRETATION:** Use audited exclusions and exact source/run identity.

**STATUS:** [VERIFIED]

**CONSEQUENCE:** Preserve raw data and immutable foundation artifacts.

## Section 1 representations

**ASSUMPTION:** Named temporal/visual Transformers might be suitable primary branches.

**QUESTION:** Do their signals exceed context and simple statistical baselines?

**WHY IT MATTERED:** Architecture preference must not substitute for predictive evidence.

**METHOD:** Nested recording CV, action/prior baselines and group-compatible cyclic permutations.

**RESULT:** Sensor statistics outperform tested PatchTST; visual AP adds context-relative signal but standalone AUROC improvement is unresolved.

**INTERPRETATION:** The temporal Transformer hypothesis fails for this tested implementation, not all Transformers.

**STATUS:** [FALSIFIED]

**CONSEQUENCE:** Retain PatchTST as a bounded SQ1 negative result; select sensor statistics.

## Section 1B admissibility

**ASSUMPTION:** A weaker visual model could still add information beyond strong sensors.

**QUESTION:** Is visual information complementary and incrementally useful?

**WHY IT MATTERED:** Standalone model rank does not answer fusion value.

**METHOD:** Frozen OOF overlap plus strictly nested two-probability static stacking and clustered paired uncertainty.

**RESULT:** 97 visual-only correct failures across 61 recordings; positive static-fusion AP/AUROC increments.

**INTERPRETATION:** Fusion warranted without changing the original standalone gate.

**STATUS:** [VERIFIED]

**CONSEQUENCE:** Authorize a small clean-fusion comparison.

## Numerical reproduction correction

**ASSUMPTION:** One BLAS thread was expected to reproduce the frozen sensor fit.

**QUESTION:** Does execution match the original probabilities?

**WHY IT MATTERED:** Small numerical optimizer changes can invalidate claimed exact reuse.

**METHOD:** Strict parity guard before permutation/fusion results.

**RESULT:** The one-thread attempt failed; original 16-thread setting reproduced exactly.

**INTERPRETATION:** Restore execution fidelity, not relax the scientific guard.

**STATUS:** [CORRECTED]

**CONSEQUENCE:** Preserve failed attempt and use original threading.

## Section 2 clean fusion

**ASSUMPTION:** Process/quality adaptation might improve static fusion.

**QUESTION:** Does extra complexity produce meaningful clean incremental value?

**WHY IT MATTERED:** Mechanism plausibility requires an actual reference comparison.

**METHOD:** F1–F6, three neural seeds, nested selection, paired intervals and context ablations.

**RESULT:** No gate improves AP beyond F2; all lose AUROC. Context affects weights without proven clean benefit.

**INTERPRETATION:** Simple fusion is sufficient within the tested comparison.

**STATUS:** [FALSIFIED]

**CONSEQUENCE:** Retain static reference and bounded quality-capable gates for robustness testing.

## Shortlist interpretation correction

**ASSUMPTION:** Highest gate AP point estimate could define the next candidate.

**QUESTION:** Do uncertainty, calibration, cost and stability support that ranking?

**WHY IT MATTERED:** Point-only winner selection exaggerates weak differences.

**METHOD:** Post-hoc descriptive review contrasts; preserve original generator output.

**RESULT:** Section 2 reviewed shortlist preferred a simpler F4 mechanism control; current autonomous prompt explicitly authorizes F5/F6 for reliability testing.

**INTERPRETATION:** Different mechanism questions justify the declared shortlist, not a hidden retuning step.

**STATUS:** [CORRECTED]

**CONSEQUENCE:** Use current preregistered robustness shortlist; preserve both historical recommendations.

## Section 3 robustness

**ASSUMPTION:** Quality-capable gates may help when a modality degrades.

**QUESTION:** Do induced weight shifts coincide with better predictive resilience?

**WHY IT MATTERED:** Weight variability alone is not reliability awareness.

**METHOD:** Predeclared raw/pixel corruptions, frozen models, 2,000 paired recording bootstrap draws and missing-modality parity.

**RESULT:** No family/gate pair met both the predeclared weight-adaptation and smaller-degradation criteria at its highest severity. Absolute high-severity AP superiority over F2 was supported for none of these family/gate pairs. These are separate claims and marginal exploratory intervals; no universal reliability-awareness claim follows.

**INTERPRETATION:** Separate family-specific relative resilience from absolute corrupted performance.

**STATUS:** [VERIFIED]

**CONSEQUENCE:** Use only bounded claims supported by the mechanism/outcome table.

## Modality dropout

**ASSUMPTION:** Missingness training might improve gate robustness.

**QUESTION:** Can this exact architecture benefit without new branch information?

**WHY IT MATTERED:** A fixed surviving-branch output places a structural limit on training.

**METHOD:** One F6 variant, .15/.15/.70 masks, frozen architecture/branches, same folds and three seeds.

**RESULT:** Modality dropout changed clean AP by -0.0037 [-0.0085, 0.0003] versus ordinary F6. Under complete visual or sensor loss, predictions are exactly the surviving frozen branch for both variants; missing-condition improvement is structurally impossible for this masked scalar-logit gate. At marginal paired 95% intervals, degraded AP improved for S2_0.3 and worsened for V1_0.05; remaining comparisons were unresolved.

**INTERPRETATION:** Joint-present behavior may change; complete-loss outputs cannot.

**STATUS:** [VERIFIED]

**CONSEQUENCE:** Do not redesign the gate to rescue a negative hypothesis.

## Audio feasibility

**ASSUMPTION:** Audio might provide further complementary signal.

**QUESTION:** Can the correct waveform interval be assigned to each action segment?

**WHY IT MATTERED:** AST needs trustworthy segment boundaries, not frame-perfect synchrony.

**METHOD:** Clock/header/coverage audit using immutable full-decoding evidence.

**RESULT:** AUDIO NOT INCLUDED — SEGMENT-ALIGNMENT OR COVERAGE PRECONDITION FAILED

**INTERPRETATION:** This is a timing/coverage exclusion, not evidence that audio lacks signal.

**STATUS:** [NOT RUN — GATE FAILED]

**CONSEQUENCE:** Skip AST, tri-modal and audio-corruption training; continue synthesis.

## Object generalization

**ASSUMPTION:** Object annotations might support unfamiliar-object evaluation.

**QUESTION:** Are physical identities and disjoint groups reliable?

**WHY IT MATTERED:** A category label and repeated board context can masquerade as OOD evaluation.

**METHOD:** Object support and recording/object connectivity audit.

**RESULT:** Object annotations are categories/targets without verified physical-instance identity. Shared object categories connect recordings; a stress test preserving both recording and object disjointness lacks validated independent groups. Do not substitute a category label for physical object identity.

**INTERPRETATION:** Do not invent independent physical objects or degenerate folds.

**STATUS:** [NOT RUN — GATE FAILED]

**CONSEQUENCE:** No object-generalization claim; retain as optional future data-design work.

## Efficiency and practical use

**ASSUMPTION:** A small fusion head might make the whole system cheap.

**QUESTION:** Where do preprocessing, extraction and fusion costs actually occur?

**WHY IT MATTERED:** Cached-head latency is not complete system latency.

**METHOD:** Repeated warm component measurements after warmup; parameter/checkpoint/memory inventory.

**RESULT:** Machine-readable results separate branch preprocessing, visual extraction and small fusion overhead.

**INTERPRETATION:** VM sequential component sums are estimates, not production real-time certification.

**STATUS:** [VERIFIED]

**CONSEQUENCE:** Frame deployment claims around measured components and missingness behavior.

## Final synthesis

**ASSUMPTION:** The thesis should connect prerequisites, architecture and failure modes.

**QUESTION:** What do both studies jointly support?

**WHY IT MATTERED:** Negative results are part of the answer, not reasons to keep searching.

**METHOD:** Machine-linked tables/figures, SQ1–SQ4 answers, claim audit and preservation checks.

**RESULT:** Fusion is warranted when independently evaluated modalities provide complementary task information. In REASSEMBLE, simple calibrated late fusion captures this benefit; greater representation or gate complexity does not automatically help. Robustness must be judged jointly by induced allocation response, absolute degraded performance and change from clean performance, not by weight movement alone. No family/gate pair met both the predeclared weight-adaptation and smaller-degradation criteria at its highest severity. Absolute high-severity AP superiority over F2 was supported for none of these family/gate pairs. These are separate claims and marginal exploratory intervals; no universal reliability-awareness claim follows.

**INTERPRETATION:** Use task-appropriate evidence and retain uncertainty, adaptivity and generalization limits.

**STATUS:** [VERIFIED]

**CONSEQUENCE:** Close the study after final validation; leave only optional future work.

## Source history

- `artifacts/phm2026/PHM_RAW_RETIREMENT_REPORT.md` and `docs/phm2026/RAW_DATA_RECOVERY.md`.
- `artifacts/intel_welding/audits/PHASE_1_GATE_REPORT.md` (retained earlier foundation evidence).
- Original REASSEMBLE acquisition/foundation run `runs/reassemble/20260927T141645Z-inventory`.
- Frozen Section 1, 1B and 2 handoffs; new Section 3 and modality-dropout handoffs.
- `FINAL_REASSEMBLE_HANDOFF.md`, `FINAL_EVIDENCE_MAP.md` and the final output manifest.
