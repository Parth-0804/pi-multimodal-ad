# Measured scientific verdict

This is an additive interpretation of the sealed complete evaluation. No model
was retrained or selected, no prediction was replaced, and no protocol was
changed. See `provenance/interpretation_v2_lineage.json` for input/report hashes.

**Architecture portability is established at the stated software/input-contract
level. A reliable external multimodal performance gain is not established.**

MSM's complete frozen P matrix has F2 AP0.756879 versus its sensor component
0.828616: ΔAP−0.071737, negative in all three seeds. The conditional date-proxy
bootstrap interval[−0.100356,−0.051477] also lies below zero, subject to five-date
support and unresolved physical tool/workpiece reuse. F2 trails sensor logistic
in mean AP under all six predefined cohort/grouping sensitivities. QG_clean's
small+0.008802 gain is mixed across seeds and its interval spans zero. The
stronger sensor control has the highest primary clean point AP0.901299.

Handover's averaging AP0.803102 improves on vision0.771647 but trails its sensor
component0.823624 in every seed; the stronger sensor control reaches0.906319.
Participant identities are unavailable, preventing participant-safe OOF F2 and
gate fitting. This is a completed official-split baseline comparison with a
documented identity limitation, not completed learned-fusion validation.

The source-domain core saved results still reproduce: REASSEMBLE F2 AP0.447299
versus sensor0.429392. That saved-result consistency check was not a new raw-data
training replication. A source-domain fusion gain did not reproduce as a primary
MSM F2 gain. Different tasks, prevalence, observation windows and fitting protocols
prevent a universal causal explanation or absolute cross-task score ranking.

The exact canonical REASSEMBLE full-CNN checkpoint remained unavailable. Therefore
**learned-weight transfer was not tested**. P denotes the original generic
pretrained CNN, with newly fitted domain heads, scalers and fusion parameters.

Named corruption tests do not establish general adaptive robustness. MSM's
augmented gate can improve on degraded F2 yet fail to beat an intact branch or
stronger sensor control, and it loses badly under some visual degradations.
Missing-modality recovery is an explicit deterministic fallback, rather than a
learned response. Handover has no validated adaptive fusion. All scenarios and
unfavorable outcomes remain in the tables.

Large train/held-out gaps, heterogeneous fold prevalence, camera occlusion,
unresolved physical identities and the incomplete participant/source gates belong
in the thesis's main interpretation. Report architecture reuse, new adapters,
traceable grouped evaluation and the negative/inconclusive fusion findings.
Avoid claims of multimodal superiority, learned cross-domain representations,
universal robustness or early warning.

Read the dataset-specific `SCIENTIFIC_INTERPRETATION_v2.md` addenda alongside the
original eight reports, `FINAL_RESEARCH_SUMMARY.md`, all per-seed/per-fold results
and the two real16-frame example galleries. Computational and provenance records
remain unchanged: all12,258 reported fold/model/condition metric sets reproduce,
MSM F2 coefficient refits match exactly, and a sealed-runner reuse check passes.
