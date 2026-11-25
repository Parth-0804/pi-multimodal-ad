# Independent literature task — prepared, not authorized by the audit prompt

Run this later only after the user authorizes this research task and any required
usage/access limits. Give it to a fresh context that has not received our project
results. Do not copy the current repository, score tables, hypotheses about our
achieved scores, or agent reports into that context. Verify the actual context/file
isolation mechanism; if it cannot be established, label the review NOT RESULTS-BLIND.
This is independence from our observed outcomes, not independent human review.

## Research brief

Prepare a critical literature-based research report on reliable multimodal fusion
for industrial monitoring and action-outcome prediction. Emphasize synchronized
visual and time-series modalities, unequal modality usefulness, degraded or missing
inputs, and process context. Discuss audio where it is relevant, but do not force
an audio modality into a dataset that does not support it.

Do not use, mention, or justify our existing architecture or achieved results.
Do not assume an adaptive gate, transformer, or fine-tuning is the answer.

Review foundational studies and developments through the actual search date.
Separate completed-action classification, online/early failure detection, anomaly
detection, and regression. Explain where comparison across tasks is invalid.

## Source and search method

Use original papers, official dataset documentation, and original code repositories
where relevant. Record search date, queries, search venues, inclusion/exclusion
criteria, and a limitation statement. Verify author/title/year/DOI or stable source
identity. Distinguish peer-reviewed publications, preprints, benchmarks, and claims
not reproducible from available evidence. Do not invent papers or use abstracts
as if you read the full study. Do not claim a systematic review without an adequate
search and screening protocol.

If a user-approved search/usage budget is absent, request authorization for a bounded
scope rather than beginning an open-ended literature campaign. No paid purchases,
private-project uploads, executable code downloads, or dataset acquisition.

## Questions

1. When does fusion outperform strong single-modality and static-fusion baselines?
   What evidence contradicts universal claims about adaptive fusion?
2. How are input quality, uncertainty, missingness, and process context represented?
   Can quality estimates distinguish corruption from informative rare events?
3. What is known about frozen versus fine-tuned encoders and unequal modality learning?
   How do studies separate feature improvements from fusion improvements?
4. What do spatial and temporal components contribute, and what ablations establish it?
5. How are corruption families/severities, known missingness, hidden failure,
   synchronization errors, and unseen corruption types evaluated?
6. Which studies compare clean-only training with corruption-aware training fairly?
   How are threshold/calibration choices, absolute scores, degradation, and uncertainty
   reported? Are results clustered at the true independent sampling unit?
7. How do external-dataset retraining, zero-shot transfer, and software portability
   differ? Which published experiments support each kind of claim?

## Deliverables

A research matrix with task, modalities, labels, synchronization, architecture,
training conditions, baselines, split unit, leakage protections, corruption protocol,
metrics, uncertainty, limitations, and code/data availability for each included study.

A synthesis of agreements and disagreements. Separate formal theoretical results,
measured empirical observations, and your interpretations. Do not equate a literature
review with a new theoretical contribution.

At most three candidate research opportunities. Each must identify the closest prior
work, what is already implemented, the remaining question, a falsifiable hypothesis,
a minimal fair experiment, plausible counter-results, and feasibility constraints.
Absence from search results is not proof of novelty. Avoid merely combining fashionable
components or defining a gap as something absent from our repository.

A dataset shortlist based on accessible official evidence: synchronized modalities
for matched samples, target provenance, independent split units, realistic task fit,
licensing/access, estimated acquisition requirements, and reproducible baselines.
Do not invent proxy labels to force compatibility. Do not compare published scores
as if they used identical protocols without checking.

Finish with a prioritized experimental agenda, source-verification ledger, and
unresolved evidence. No implementation or experiment execution.
