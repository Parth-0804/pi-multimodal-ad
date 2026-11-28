# Chapter 4 editorial consolidation

Scope: only `working/LaTeX_Project/chapters/04_methodology.tex`, compared with the unchanged November 26 source in `state_A/source/chapters/04_methodology.tex`. No builds, experiments, bibliography changes, figure redesigns or protected-chapter edits were performed by this subtask.

## Structural consolidation

All eleven principal section titles, section labels and their order are unchanged. Thirty subsections become seven:

| Original subsections | Retained location |
|---|---|
| 4.1.1–4.1.2 | Continuous prose in 4.1, retaining the five study roles and R1–R5 methodology references. |
| 4.5.1–4.5.2 | Continuous prose in 4.5: target provenance, observation horizon, contextual shortcuts. |
| 4.6.1 and 4.6.4 | 4.6.1, **Training-Side Preprocessing and Model Selection**. The PHM preprocessing exception moves here verbatim. |
| 4.6.2 | 4.6.2, **Out-of-Fold Predictions and Learned Fusion**, retaining the full substantive procedure and shared-bank qualification. |
| 4.6.3 and 4.6.5 | 4.6.3, **Assessment Cohorts and Repeated Exposure**. |
| 4.7.1–4.7.4 | Continuous prose in 4.7, following fitting/selection → calibration → within-fold/pooled ranking → threshold determination. |
| 4.8.1–4.8.3 and 4.8.5 | 4.8.1, **Regression, Classification, and Probability Metrics**. Existing probability-metric paragraphs move before aggregation. |
| 4.8.4 and 4.8.6 | 4.8.2, **Aggregation and Uncertainty**. |
| 4.9.1–4.9.3 | 4.9.1, **Controlled Interventions, Absence, and Degradation**. |
| 4.9.4–4.9.5 | 4.9.2, **Matched Exposure and Robustness Interpretation**. |
| 4.10.1–4.10.3 | Continuous prose in 4.10. |
| 4.11.1–4.11.3 | Continuous prose in 4.11; the redundant methodological synthesis is deleted, and the original transition to the empirical chapters remains. |

No removed subsection carried a label. A literal search for former subsection numbers in chapter, appendix and frontmatter sources found no dependencies. The stacker figure remains in 4.6.2.

## Removed duplication and retained counterparts

The full source diff records the exact deletions. This ledger identifies the principal deletion groups and where their substantive content remains.

| Location | Removed or reduced material | Retained counterpart |
|---|---|---|
| Chapter opening | The repeated paragraph beginning “The methods follow the five criteria…” | The explicit R1–R5 mapping in 4.1 and the original Chapter 2 requirements. |
| 4.1 | Repeated introductions to the study mapping; repeated representations/metric lists in the five study descriptions; the five-study limitations recap beginning “Several consequential boundaries remain”; the closing programme summary. The original study descriptions are shortened by retaining selected complete original sentences. | Study roles remain in 4.1, Figure `fig:research-workflow` is unchanged, target definitions remain in 4.5, detailed architecture configuration remains in Chapter 3, and the specific limitations remain in 4.5–4.10. The original REASSEMBLE sensor-only-control limitation sentence is relocated verbatim to 4.7. |
| 4.2 | Generic examples of dataset suitability, the repeated unchanged-question statement, and the repeated reporting-cutoff paragraph. | The actual admission criteria and chronology remain in 4.2; restriction examples remain in 4.4; the dated cutoff and verification distinction remain in 4.10. |
| 4.3 | Repeated original welding-proposal sentence and repeated statement that the transition preserved the questions. | Welding motivation remains in Chapter 1 and 4.2; the four-question alignment record remains in 4.2. The audit, prior exposure, partition/session overlap, researcher-reported supervisor agreement and welding-validation limits remain in 4.3. |
| 4.4 | Generic introductory sentence; the second manifest-description sentence; “Each admitted pair therefore requires…”; the closing checklist repeating eligibility criteria. | Manifest fields, visual readability versus target visibility, sensor checks, resampling, correspondence, exclusions, MSM/ViFailback preparation issues, restricted eligibility and R1 remain in 4.4. General admission criteria remain in 4.2. |
| 4.5 | Generic observations/targets bridge sentences, the repeated explicit statement that retrospective experiments do not measure warning time, and contextual-variable closing reminders. | The complete proxy qualification, each prediction unit/target, MSM mapping sensitivity, completed-window versus prospective distinction, decision-time requirements, acquisition delay, PHM latency covariate, action-prevalence shortcut and relevant controls remain in 4.5. |
| 4.6 | Repeated generic grouping/leakage reminders; the recording-group reminder; short lead-ins and conclusions repeating the shared-bank dependency; the generic two-result cohort example; the standalone PHM fold-isolation conclusion; a repeated future-confirmatory description and uncertainty-history reminder. | Complete grouping limitations remain before 4.6.1; preprocessing and leakage citations remain in 4.6.1; full outer/inner/OOF/shared-bank distinctions and unchanged figure/caption remain in 4.6.2; exact cohort counts and repeated exposure remain in 4.6.3. PHM diagnostic separation and the need for an unexecuted repeat remain in 4.6.1. Uncertainty-history limits remain in 4.8; the full future-confirmatory specification remains in 4.11. |
| 4.7 | Generic introductory/programme sentences; repeated textbook calibration introductions; repeated statements that fitting/selection differ and transformations influence outputs; generic ranking and threshold lead-ins/conclusions. | The four distinct operations, actual fitting/selection fields and budget comparison, calibration citation and exact core calibrator procedures, F2/gate probability-transform differences, full monotonic/within-fold/pooled reasoning, the absent independently fitted sensor-only control, exact threshold grid and operational-cost caveat remain. |
| 4.8 | Duplicate MAE/RMSE explanation, duplicate PHM proxy warning, repeated classification/metric introductions, duplicate macro-AP/Brier/ECE overview, repeated macro-AP explanation, generic fold-aggregation introductions, duplicate cross-fold alignment sentence and ViFailback metric list, generic paired-difference sign explanation, and closing uncertainty reminders. | The concise metric definitions remain; PHM target validity remains in 4.5; AP implementation versus trapezoidal PR area, prevalence, ViFailback >85% failure, class-specific and macro AP, constant baselines and target-specific naming remain in 4.8.1. Within-fold versus pooled alignment remains fully in 4.7. Actual fold/seed aggregation and all bootstrap counts, grouping restrictions, fixed-model conditioning and non-equivalence caveats remain in 4.8.2. |
| 4.9 | Generic robustness introductions; duplicate processing-stage and broad-reliability conclusions; repeated availability/fallback definitions; the generic adaptive-weighting definition; repeated weight-change and clean/degraded summaries. | Specific regimes, intervention stage/severity/realisations, descriptor consistency, the exact surviving-branch/threshold and all-absent rejection policy, the static/unimodal comparisons, modality-dropout qualification, quality-fusion citation, matched exposure and remaining confounds, clean versus absolute/relative degraded performance and untested natural-fault limits remain. Chapter 3 retains the mathematical fusion mechanisms. |
| 4.10 | Generic reproducibility introduction; repeated frozen-backbone/fitted-head explanation; software-reference reminder; introductory verification-level sentence; repeated descriptions of manuscript inspection and selected recomputation; repeated evidence-register reminders. | All software citations and implementation evidence remain. Chapter 3 retains the executed frozen/head architecture. Verification levels, historical missing-artifact limits, original commit and hashes, 24 November cutoff, completed/incomplete ViFailback configurations, 25 November saved-prediction checks and their limits, original provenance calls and Appendix F/G cross-references remain in 4.10. |
| 4.11 | Generic computational-feasibility introductions, repeated rapid-forward-pass/observation-window warning, repeated exploratory-purpose introduction, generic statements about the value of comparisons and a full repeated methodological synthesis. | Resources and budgets, computational non-optimality, restricted-budget interpretation, unfinished-versus-negative distinction, measurement workloads/hardware boundaries, assessment-exposure limits and the detailed future-confirmatory design remain in 4.11. Acquisition-versus-computation delay remains in 4.5; R1–R5 remain mapped in 4.1. The original empirical-chapter transition remains. |

## Wording and layout adjustments

- Retained prose sentences remain verbatim, including those relocated or joined into related paragraphs.
- The sole changed prose sentence is the first sentence of 4.7: **“Each empirical comparison therefore identifies…” → “Each empirical comparison identifies…”**. Only the dangling “therefore” is removed after deleting its generic introductory paragraph.
- Shortened study-role paragraphs and the paired-comparison paragraph use selected complete original sentences; no substitute prose is generated.
- Related consecutive single-sentence paragraphs are joined without changing their words. Unrelated methodological topics remain separate.
- The seven retained subsection titles above consolidate the original headings. Main-section titles are unchanged.
- The local `\enlargethispage{\baselineskip}` before the final transition is removed. No other float definition, figure source, caption or local typography setting changes.
- Existing CRLF line endings are retained.

## Checks performed

- Main sections: **11 → 11**; subsections: **30 → 7**.
- Simple regex word/token count, including LaTeX command text: **8,636 → 6,137**, a reduction of **2,499 (28.9%)**. The root report should use its consistent manuscript word-count method for the A/B/C comparison.
- All **14 citation commands**, including their keys and any postnotes, preserved as an exact multiset.
- All **16 `\EvidenceRef` calls**, including source locators, preserved as an exact multiset.
- All **12 labels** and both figure include paths preserved as exact multisets. There are no equation environments in the original or consolidated Chapter 4.
- All distinct scientific numerical values remain. The only distinct standalone numeric token no longer present is the introductory literal “Chapter 2”; the relevant chapter and R1–R5 mapping remain unchanged elsewhere.
- No compilation was run by this subtask. The root task owns state A/B/C builds, global formatting, visual inspection and complete-manuscript integrity checks.

Remaining concern: scientific preservation is checked against the current authored manuscript and its existing evidence references, not by rerunning experiments or independently revalidating all underlying sources. The full build and rendered-page inspection remain required before publication.
