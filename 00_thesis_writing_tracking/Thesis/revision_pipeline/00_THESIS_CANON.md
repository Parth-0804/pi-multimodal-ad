# Compact thesis reference — v0.3 (provisional)

This is a small set of scientific anchors for selective editing, not a complete global canon. All content below is **DRAFT-REPORTED** from the [professor-submitted November 20 v2 PDF](../PDFs/DRAFT_Thesis_2026-11-20_FULL.pdf). It is protected against silent editorial changes, but has not been newly verified against code, saved results, or cited papers. Consult only the entries relevant to the current passage, plus the source section and evidence it actually needs. Do not repeatedly inject the full thesis or a growing canon into every edit.

## Evidence precedence

Actual executed code, configurations, saved predictions/results and original publications establish scientific support. Registered research questions and documented author/supervisor decisions establish intended scope. The PDF establishes the original wording. None is automatically infallible: reconcile conflicting records. Mark suspected original errors `[VERIFY]` or `[CITE?]` in working notes and resolve them separately from stylistic editing. Upgrade DRAFT-REPORTED to VERIFIED only with the precise evidence path/locator, check and reviewer. No new verified claims were established in v0.3.

## Research questions and scope locks

Registered title: Physics-Informed Multi-Modal Transformer Architectures for Robust Industrial Welding Anomaly Detection.

Exact research questions as printed in §1.4, pp. 3–4:

- **Main:** How can a process-aware multimodal AI architecture be designed and evaluated for robust industrial anomaly detection using robotic welding data as a case study?
- **SQ1.** Which lightweight or pretrained Transformer-based representation components are suitable for visual, audio, and sensor time-series data in a multimodal industrial anomaly detection pipeline?
- **SQ2.** How do unimodal baselines, simple concatenation fusion, modular late fusion, and process-aware gated cross-modal fusion compare in terms of predictive performance?
- **SQ3.** Can a gated cross-modal fusion architecture improve robustness when one or more modalities are missing, degraded, or unreliable?
- **SQ4.** How can multimodal architecture performance be evaluated beyond accuracy, including robustness, interpretability, modularity, and practical usability?

Do not replace these registered questions with the findings of the completed experiments.

**Explicit non-claims and protected distinctions** (Abstract; §§1.3–1.6, 3.2–3.5, 4.5–4.11, 10.1–10.3):

- Independent weld-quality validation remains open following prior access to the proposed Intel Welding assessment recordings. Adjacent tasks are not welding-domain validation. Here, process-aware conditioning is not enforcement of physical equations or conservation laws.
- A completed-action/episode classifier is not an established prospective early-warning system. Evidence unavailable at a decision time is not necessarily physically nonexistent. Audio was not evaluated as a predictive REASSEMBLE branch.
- The PHM photograph-derived candidate-area statistic is a provisional target proxy; its independent physical validity is unresolved. The principal three-group sensor fusion is not joint camera–sensor inference.
- REASSEMBLE's frozen ResNet18-vd backbone inside RT-DETR-R18vd is a CNN; do not describe that core path as Transformer encoder execution. Keep the distinct hybrid-encoder comparison separate. Statistical sensor features and scratch-trained PatchTST are distinct representations.
- F1 averages calibrated probabilities. F2 stacks probabilities with a fixed C=1 logistic model and unconstrained coefficients. F3 fuses representations (128 visual dimensions and 220 sensor statistics; candidate widths 32/64 and epoch budgets 10/20). F4/F5/F6 gate calibrated branch logits using action, quality, or combined context. Preserve candidate versus executed settings. The weights do not establish causal modality reliability.
- F2 adds a fitted probability map; the matched sensor-only second-stage calibration control was not completed. Do not attribute the combined-pipeline gain solely to vision. Differences in losses, capacity, calibration and training exposure limit causal attribution to adaptation alone.
- Recording-disjoint outer assessment does not establish fully independent inner meta-validation, object-disjoint or machine-disjoint evaluation. Paired intervals condition on fitted models. Reused assessment cohorts and exploratory follow-ups are not untouched confirmation.
- Known absence with a supplied mask and unannounced corruption differ. Programmed fallback is not learned corruption recognition. Temporal offset, drift and domain shift also differ. Do not infer natural simultaneous-failure robustness from separate synthetic operators.

## Selected numerical anchors (not an exhaustive result ledger)

Preserve the source's metric, population, sign, uncertainty and exact reported precision. Retrieve the actual passage/table for all other values. Do not use this sheet to reconstruct missing results or revise research claims.

| ID | DRAFT-REPORTED anchor | Boundary / printed PDF locator |
|---|---|---|
| C01 | PHM: MAE 0.8238 vs 0.8042 percentage points (three-group fusion vs training mean) | Unresolved paired difference on a photographic proxy, not validated physical wear; Table 5.2, §5.7.4 |
| C02 | REASSEMBLE: 4,530 actions, 509 failures, 148 recordings; sensor AP .4294, F1 .4457, F2 .4473 | Matched fitted-pipeline comparison; Tables 6.1–6.2, §§6.7.1–6.7.4 |
| C03 | F2−sensor AP +0.017907 [.008603, .028284]; F2−F1 AP +0.001556 [−.007607, .011165] | The first interval excludes zero; the second establishes neither superiority nor equivalence; §6.7.4 |
| C04 | Original gates F4–F6: lower AUROC than F2; AP contrasts unresolved; numerically lower ECE | Metric-specific findings, not universal inferiority or significant ECE superiority; Table 6.2, §6.7.4 |
| C05 | Original F5/F6 did not establish consistent advantage under tested corruption | Do not extend to all gates or failure types; §6.8, §10.2 |
| C06 | MSM: 1,895 primary intervals; mean AP across three seeds .757 stacking vs .829 logistic sensing | Ranking differs from seed-42 Brier/F1; Table 7.2, §§7.7–7.8 |
| C07 | ViFailback: original stacking pooled macro-AP .621–.629 vs .649 logistic sensing across three seeds | Completed episodes, held-out tasks; donor-transfer findings mixed; Tables 8.2–8.3, §8.7 |
| C08 | HANDOVER: 151 official test trials; mean failure AP .803 averaging vs .824 logistic sensing | Missing participant mapping prevents learned-fusion assessment; Table H.1, Appendix H |
| C09 | Review reports 94 full-text works | Not an estimate of field-wide prevalence; distinguish discovery, screening and appraisal; §2.1, Appendix A |

**Terminology:** retain established terms, exact dataset/model identifiers, notation and metric distinctions (AP versus trapezoidal PR-AUC, AUROC, recall, Brier, ECE; pooled versus mean-fold or mean-seed results). Consistent terminology matters more than stylistic synonym variety.

### Exact-string locks for the source checker

The following starter list is read automatically by `scripts/verify_tex_integrity.py`. These are draft-reported identifiers and metric names, not a newly verified scientific glossary. Counts are case-sensitive; the checker flags changes, including legitimate approved moves/deletions. Add local exact source spellings when necessary using `--term` (including LaTeX macro forms). Do not automatically replace terms; verify their meaning and approve any intentional change.

<!-- BEGIN LOCKED TERMS -->
```text
REASSEMBLE
PHM
MSM
ViFailback
HANDOVER
Intel Welding
RT-DETR-R18vd
RT-DETR-L
ResNet18-vd
PatchTST
HGB
F1
F2
F3
F4
F5
F6
AP
AUROC
MAE
RMSE
Brier
ECE
```
<!-- END LOCKED TERMS -->

For citations, use the [released bibliography](../LaTeX_Project/references.bib), the [citation-to-PDF index](../References/CITATION_PDFS.csv), the existing registers and the original source on demand. Do not split grouped citations into specific paper-to-mechanism assignments on inference alone. Record source checks where consequential, not in a new exhaustive citation database.
