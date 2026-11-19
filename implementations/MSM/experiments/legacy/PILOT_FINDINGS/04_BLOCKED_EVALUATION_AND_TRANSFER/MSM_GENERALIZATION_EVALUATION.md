# MSM generalization evaluation

**No independent held-out model evaluation was admissible under the frozen protocol.** This report measures label/group/modality support, not prediction accuracy. Dataset `manufuturetoday/multi-sensor-for-metal-milling-anomaly/versions/2`; exact group audit is `manifests/cohort_by_experiment.csv`.

## Actual eligible cohort

| Experiment | Label 0 | Label 1 | Label 2 | Binary positive prevalence |
| --- | ---: | ---: | ---: | ---: |
| imi_vm20i/dataset1 | 0 | 8 | 0 | 100% |
| imi_vm20i/dataset4 | 0 | 0 | 11 | 0% |
| imi_vm20i/dataset19 | 18 | 0 | 0 | 0% |
| imi_vmx30ui/dataset8 | 64 | 0 | 0 | 0% |
| imi_vmx30ui/dataset9 | 11 | 2 | 0 | 15.38% |
| TOTAL | 93 | 10 | 11 | 8.77% |

Native label 2 stays a stable-cutting negative for intervention-worthy cutting abnormality. The pure-positive VM20i/dataset1 and pure-negative folders illustrate why random interval/frame splits could learn experiment conditions. Holding complete experiments is necessary; it does not itself prove physical independence. Label-2 exclusion yields 103 intervals, four folders and the same two positive folders; it also fails the primary split gate.

Frozen three-outer/two-inner grouping cannot assign positives to three outer tests from two positive folders. Holding out one positive folder leaves only one positive training folder, which also prevents complete two-fold group-held-out branch probability construction for F2: one inner model would train without positives. Repeating seeds or bootstrapping intervals does not create independent anomalous experiments. Stage 3 smoke OOF fitting was development-only and is not a substitute for an outer test.

The five folders collapse to **three machine/reference-date clusters**, only **two positive clusters**. Physical tool/workpiece/session identities remain unresolved. Those dates are filename-reference proxies, not proven independent sessions; both the nominal and stricter grouping audit have insufficient support. Any future generalization claim must disclose that dependence.

## Cross-machine feasibility

Both laboratory machines have video and the same 15-channel MTC schema, but their class distributions differ sharply:

| Machine | Verified intervals | Experiment groups | Positive groups | Native 0 / 1 / 2 | Positive prevalence |
| --- | ---: | ---: | ---: | --- | ---: |
| imi_vm20i | 37 | 3 | 1 | 18 / 8 / 11 | 21.62% |
| imi_vmx30ui | 77 | 2 | 1 | 75 / 2 / 0 | 2.60% |

| Training → held-out machine | Train / test intervals | Both classes in each side? | Matching two-inner F2 bank? |
| --- | --- | --- | --- |
| VM20i → VMX30Ui | 37 / 77 | Yes | No: only one positive training group |
| VMX30Ui → VM20i | 77 / 37 | Yes | No: only one positive training group |

Thus technical input compatibility exists, but **matched full-architecture cross-machine evaluation fails in both directions**. No classifier or fusion scores were generated. A separately declared unimodal-only diagnostic would be a different question from the frozen matched full-model experiment and was not substituted. Prevalence, operating regimes, material distribution, tool condition and sensor update/aggregation rates can confound any eventual comparison; report them with model results and both-class denominators.

## Laboratory versus industry

Stage 1 counted 56 laboratory folders / 2,512 native intervals / 458 label-1 intervals in 25 nominal positive folders, but only the five laboratory folders above have a verified joint Stage 2 cohort. Candidate annotation counts are not aligned sample counts. Every added video requires the corrected label-blind alignment/support checks, unique 16-frame selection, camera-context review, native sensor gates and physical-group audit before its rows enter evaluation.

The 13 VF10 industrial folders have no provided video. The pilot industry MTC schema differs, CT is about one sample per 10 s, and material/machine conditions differ. **Zero industry visual-plus-sensor examples are eligible.** No industrial sensor-only score was produced or described as generalization of this visual architecture. Audio/sensor alternatives require their own explicit protocol and are not automatically substituted.

## Interpretation and required evidence

No experiment-disjoint AP/AUROC, seed stability, overfitting curve, transfer effect or confidence interval is available from Stage 4. Current positive prevalence and class-support counts are descriptive audit findings, not test results. The diagnostic CNN's compatible tensors establish software portability only. Frequent coolant occlusion and unknown MTC aggregation latency also restrict future interpretation to coarse retrospective milling-context classification unless separately resolved. Corrupted/missing-modality robustness is untested.

Before a resumed independent evaluation: obtain and audit more positive laboratory experiments under the same version, target and eligibility rules; reconcile dependency groups; freeze and validate the three-outer/two-inner partition; obtain the completed canonical REASSEMBLE full-CNN source; validate resumable P/R execution, then run all fixed seeds and report paired experiment-cluster uncertainty. No test-score-guided cohort/split/source selection is permitted.

All zero-prediction and blocked-result tables are preserved in this run. **Stop after Stage 4; no unsupported generalization or representation-transfer conclusion is drawn.**
