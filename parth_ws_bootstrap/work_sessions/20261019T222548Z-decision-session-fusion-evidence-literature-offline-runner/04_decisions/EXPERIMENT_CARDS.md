# Experiment and validation cards — PROPOSED / NOT AUTHORIZED

These cards describe ideas, including deferred ones. They do not approve execution, numerical settings or protocol state. Only A1 is recommended as the immediate next user decision; A2/A3 are conditional/later. Historical Task4 exclusion includes repair, extension, restart and renamed equivalents.

## Card A1 — retained-evidence / protocol reconciliation (FIRST)

Question: which existing matched constant/adaptive comparisons have sufficient producing-row/fit lineage to support interpretation, and is any clean-trained corrupted-control comparison genuinely missing?

Evidence: source formula/caller trace; four bounded bank SHA bindings;15 AP estimates exactly reconciled; current saved cohort/split vectors agree. Counter-evidence: banks lack direct recording/segment/row keys; complete producing-fit/source chain and higher-order independence remain unestablished. Those limitations survive numerical agreement.

Smallest action: inspect existing row/order/input manifests and selected per-fold fit/config/calibration metadata, then mark each link VERIFIED/INFERRED/UNKNOWN. Resolve control overlap before deciding on any new study. No new metrics, raw payloads or scientific modules need execute. Success means a bounded honest reconciliation and lock-ready or blocked protocol, even if original row binding is irrecoverable.

Proposed budget:60min wall,CPU only,2 computational threads,2GiB RAM aim,64MiB maximum text/metadata input,64MiB new outputs,zero downloads/model calls/fits/inference/corruptions/new uncertainty/project tests; at most2 technical retries. Inspect at most5 outer summaries and10 representative A-CONSTANT/A-ADAPTIVE refit metadata records plus their named input/row/split/source identities; sampling does not certify all deeper fits. Save unresolved coverage instead of expanding the job. No automatic dependent action.

## Card1 — fine-tuning / visibility (DEFERRED)

Question: with the same16-frame observation support and temporal head, does adapting only the last spatial stage improve held-out clean AND degraded predictions enough to justify cost? This is distinct from changing frame coverage or training from scratch.

Available evidence: core unconditional freeze; implemented final-stage path; reported gradient count8636033; incomplete V-FT and discontinued Task1. A source path or gradient count does not establish completed results. Any restart requires explicit new permission about the discontinued study and must preserve the old closure.

Smallest future comparison if selected: frozen backbone plus the same TemporalHead versus last-stage adaptation plus that head, same pinned initialization/processor/frames/pooling/candidate head initialization; no full-unfreeze or from-scratch arm initially. Existing V-TEMP and fine-tuning artifacts require validation before reuse. All feature/encoder/head/calibration fits must be partition-specific; a bank learned on an assessment recording cannot be reused in that recording's test path.

**Numeric settings below are PROPOSED discussion defaults, not measured optimal settings or approved budgets.** Layer list: only backbone.encoder.stages[3] and temporal head train; other spatial stages frozen; running normalization statistics stay eval initially, with affine-parameter membership stated. Head rate1e-3 and pretrained-stage rate1e-5, AdamW betas(0.9,0.999), decay1e-3, gradient clip1. These are conservative design suggestions; source already supports separate groups and P06 supports care with pretrained-feature distortion, not these exact numbers.

Observation: same16 unique in-segment frames and fixed640 processor behavior; same spatial pooling/per-frame sequence. No new augmentation in first paired comparison; later augmentation requires a separate physical/label-preservation rationale. Loss: same BCE-with-logits in both arms; if positive weighting retained, compute negative/positive ratio on fitting subset only and record it. Calibrate using training-only cross-fitted logits.

Proposed effective batch32 using documented microbatch/accumulation, no automatic memory-driven device/config changes; seeds3 fixed before fitting, shared between arms; max20 epochs/inner fit, min5/patience5 with inner AP only; outer duration from a prespecified training-only selection. These counts do NOT bound GPU time without profiling. Exact device, hard per-fit/total time, folds, storage and admission budget remain UNAPPROVED; no job can start with those fields missing. No score-based extra seeds/epochs.

Report total loaded/forward-active/trainable/head/fusion parameters, exact trainable names, normalization state, optimizer groups, observed batch, peak memory, wall/device time and effective number of fits. Do not substitute detector-wide public parameter counts for this path. Full-backbone counts and feasibility are UNKNOWN and not measured here.

What counts against it: no paired improvement over frozen shared-head reference, unstable group effects, clean deterioration beyond an agreed margin, or cost disproportionate to effect. A null does not require adding a full-unfreeze arm.

## Card2 — transformer components (REUSE / DEFER)

Question must select one information loss: temporal order versus spatial detail/object relationships. The source has an implemented temporal TransformerEncoder and reported V-TEMP/V-NOPOS/V-MEAN controls. Repeating this under a new name adds no novelty. Source core returns backbone maps; detector hybrid-encoder/decoder representations remain a distinct proposed path.

If temporal question persists, first validate retained sequence/position/order controls and parameter/compute comparability. A fixed-weight reversal/permutation diagnostic alone is not a new independently trained order ablation. If spatial use is later justified, specify which tensor is returned, what spatial information it preserves beyond mean pooling, and compare against a matched capacity pooling/head baseline. Attention weights are not causal evidence.

No spatial extraction, detector forward, new temporal training or selected winning encoder combination is recommended now. What counts against it: improvements explained by capacity/support, absent added spatial information, or no robust generalization under the predefined question. Checkpoint naming never supplies motivation.

## Card3 — empirical contribution (PROPOSED QUESTION)

Nearest work: QMF/P03 conditional uncertainty-weighting theory; Willibald/P18 confidence-selected visual-language and force/pose robot experts; P01/P02 modality-learning imbalance; P04/P15 robustness evaluation.

Remaining question: under fixed representations, output link/calibration and clean-only training exposure, does input-dependent quality/context improve absolute completed-action failure prediction under realistic hidden single-modality faults beyond a matched constant rule and strong unimodal/static references?

Falsifiable hypothesis: the locked adaptive-minus-constant primary contrast exceeds a user-agreed practically relevant AP margin while satisfying a declared clean-performance constraint, and survives independent-unit uncertainty. Margin, aggregation/condition weights and multiplicity are UNDECIDED. No gap or effect is promised; closest prior overlap must be reviewed first.

Minimal fair study is Card5/A2 only if existing evidence does not already answer it and the work is distinct from excluded Task4. A plausible conclusion is that adaptation reacts but does not help, or that a simpler static system is preferable under these conditions. This is empirical scope; no new theoretical theorem is claimed.

## Card4 — inspection UI (DEFERRED)

Question: can a researcher trace a saved prediction to sample, actual modalities, target and validated provenance without executing a model? Smallest useful action is the textual UI_REQUIREMENTS.md already delivered. Runtime implementation is NOT_RUN. Saved replay cannot demonstrate live operation. Reject any UI behavior that fabricates missing model output, exposes unavailable data or hides evidence/selection limits.

## Card5/A2 — robustness and matched controls (CONDITIONAL)

Existing source covers imageGaussian/blur/frame loss and sensorGaussian/channel/block/stuck plus declared absence; additional historical training interventions also exist. The new arithmetic reconciles selected arrays, not physical field realism. First inspect existing corrupted constant/adaptive coverage. If complete, reuse and validate it; do not generate new conditions simply because the answer is unfavorable.

Any genuinely distinct future comparison must share branch banks/representation, probability or logit link, calibration, intercept capacity, train partitions, seed/training-exposure policy and availability/fallback. Include the best unimodal branches, probability mean, a strong static stacker and a matched constant counterpart. Report practical baselines separately from exact adaptivity controls.

Predefine a short physically motivated fault panel, raw insertion points, severities in interpretable units, realization seeds and sample pairing BEFORE assessment. Use clean and one impaired modality at a time. Distinguish known absence/masks from hidden faults; declare both-absent abstention. Recompute features/quality consistently after a physical input fault; perturbing cached vectors is a different experiment. No field-realism claim from arbitrary Gaussian scales, and no implicit permission to generate those faults now.

Keep clean-trained weights/calibrators/thresholds frozen. Report absolute failure AP and paired clean-to-corrupted degradation, clean constraint, failure recall at saved training-only thresholds, calibration and cost. A smaller drop from a worse baseline does not establish benefit. Record gate/quality movement as mechanism evidence without assigning causal percentages. Independent-unit uncertainty, training/realization variance, multiplicity, tolerances and exact primary contrast need an approved protocol.

No unseen holdout is available by assertion; exposed cohort follow-ups remain exploratory. Historical Task4 is not an admissible way to supply this comparison. If the proposed work is a Task4 extension/repair/restart/equivalent, REJECT that branch under current exclusion; do not relabel it. Device/time/trials/storage/input/output/command budgets for A2 remain UNAPPROVED.

## Card6/A3 — external data and reproducibility (LATER)

Original discussed pair UNKNOWN. New candidates: first metadata feasibility for IndustReal native procedure/error task; second conditional InspecSafe-V1 inspection safety task. No approval/winner/download. HA4M action identity, AURSAD numeric-only evidence and Paderborn vibration/current cannot silently replace the intended task.

A metadata gate requires native target and timing, actual synchronized paired streams, independent split unit, usable development data, release/version/licence and suitable original baseline. Reject a candidate if it needs invented outcome labels or an artificial image modality. A newly defined task requires explicit scope, not an unnamed proxy.

If later selected, lock method and all chosen optional-study dispositions before external assessment. Retrain both proposed method and dataset-appropriate strong baselines under one native split/protocol. This is dataset-specific retraining, not zero-shot weight transfer. No unmatched published AP comparison.

Portability measures: adapter-only versus shared-core changes, changed lines/modules, person-hours, schema/channel/unit assumptions, dependencies, synthetic interface checks and explicit failure behavior. Reproducibility measures: environment/source/config/split/input/output identities, commands/dirty snapshot, saved-metric agreement, later fixed-weight inference tolerances and separately repeated-training variability. None establishes universal compatibility from one dataset. Current session tests only synthetic orchestration; external execution is NOT_RUN.
