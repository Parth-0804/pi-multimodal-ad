# Handover: scientific interpretation of the completed evaluation

This additive interpretation changes no model, prediction, split, observation
window or sealed report. Active inputs/results remain in
`HANDOVER/experiments/common_support_v2/`.

**The five permissible baselines completed; learned-fusion validation remains
partial.** There are587 aligned trials:335 training,101 validation and all151
official test trials. The test contains41 successes and110 failures, so positive
prevalence is72.85%. Participant identities are absent; official participant
separation is the publisher's claim and cannot be independently certified.

| Primary model | Test AP, mean of three seeds |
| --- | ---: |
| Training-prevalence baseline | 0.728477 |
| Visual | 0.771647 |
| Sensor logistic | 0.823624 |
| Sensor HistGradientBoosting | 0.906319 |
| Averaging | 0.803102 |

Averaging adds+0.031455 AP over vision but loses **−0.020522 AP** against its
logistic sensor component. The latter seed differences are −0.027592, −0.028971
and −0.005003. Thus a gain over the weaker modality does not establish multimodal
improvement over both components. The stronger sensor control has the highest
clean primary point AP. No participant-based uncertainty interval is available;
three optimization seeds are not independent test populations.

F2/F2_aug/QG_clean/QG_aug were not fitted because participant-disjoint OOF
probabilities cannot be certified. No trial-ID proxy, face grouping, in-sample
stack or validation-set substitution was used. REASSEMBLE-learned CNN transfer
also remains unmeasured at the source-checkpoint gate.

Robustness is condition-specific. Under strongest blur, averaging AP is0.779066
versus intact sensor logistic0.823624. At highest sensor noise, averaging reaches
0.796955 versus noisy sensor logistic0.824952; the stronger sensor model drops
from0.906319 to0.731344. Clean model rankings therefore do not apply to every
corruption. Completely missing branches use explicit deterministic fallback,
giving0.823624 without vision and0.771647 without sensors. No adaptive mechanism
was validated on Handover.

Visual training AP averages0.954964 versus test0.771647, and sensor logistic
0.933785 versus0.823624. These gaps are compatible with overfitting and/or
distribution shift, without establishing its cause. Robot configuration, measured
versus estimated wrench, unknown participant mapping and native zero traces
remain limitations. The shared observation window can omit unsupported tail
outcome evidence; the target still describes the completed trial. This is not
full-video early-warning evaluation.

For the thesis, include the aligned RGB/wrench adapter, all five baseline results,
negative averaging-versus-sensor comparison and explicit grouping blocker. Do
not call this an independently verified participant-generalization result or an
external validation of learned F2/adaptive fusion.

Sources: the active `06_evaluation_results/metrics/` tables,
`07_robustness_experiments/robustness_metrics.csv`, `validation_gate.json` and
`implementation_validation.json`; all native labels and both horizon audits are
preserved.
