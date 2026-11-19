# Sensitivity and operating points

Question: does actual F2 gain depend on action or recording weighting, and what do the training-selected thresholds mean? Core sources: original sealed U1/U2/F2/F6, joined on recording+segment identity. No branch/model/threshold fitting in this task.

## Within-action actual fusion gain

| action | segments | recordings | failures | failure_recordings | successes | success_recordings | prevalence | metric | U1 | F2 | F2_minus_U1 | lower_95 | upper_95 | valid_replicates | undefined_replicates | support_flag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pick | 1190 | 91 | 98 | 55 | 1092 | 90 | 0.08235294117647059 | AUPRC | 0.20032842079304353 | 0.20916630649805357 | 0.00883788570501004 | -0.007961512779062999 | 0.02811549977310491 | 2000 | 0 | No prespecified support flag |
| pick | 1190 | 91 | 98 | 55 | 1092 | 90 | 0.08235294117647059 | AUROC | 0.7012222471406145 | 0.706567242281528 | 0.005344995140913467 | -0.020496754596634182 | 0.030800537873021457 | 2000 | 0 | No prespecified support flag |
| insert | 1156 | 82 | 243 | 70 | 913 | 79 | 0.2102076124567474 | AUPRC | 0.6320763463043689 | 0.6461603728489118 | 0.014084026544542882 | 0.0015752689138355232 | 0.026067552332003453 | 2000 | 0 | No prespecified support flag |
| insert | 1156 | 82 | 243 | 70 | 913 | 79 | 0.2102076124567474 | AUROC | 0.7776380493917308 | 0.7785936112576005 | 0.0009555618658697584 | -0.013532084556344423 | 0.01546096252667776 | 2000 | 0 | No prespecified support flag |
| remove | 1096 | 72 | 146 | 55 | 950 | 72 | 0.1332116788321168 | AUPRC | 0.32835458678364254 | 0.3309678506530121 | 0.002613263869369553 | -0.01196293342331156 | 0.018690423525051555 | 2000 | 0 | No prespecified support flag |
| remove | 1096 | 72 | 146 | 55 | 950 | 72 | 0.1332116788321168 | AUROC | 0.727267483777938 | 0.7386878154289834 | 0.01142033165104539 | -0.007877156593215983 | 0.03191028267808586 | 2000 | 0 | No prespecified support flag |
| place | 1088 | 129 | 22 | 21 | 1066 | 127 | 0.02022058823529412 | AUPRC | 0.18497407924113773 | 0.2364389004045485 | 0.05146482116341078 | -0.0008417436757352871 | 0.13297090554474716 | 2000 | 0 | No prespecified support flag |
| place | 1088 | 129 | 22 | 21 | 1066 | 127 | 0.02022058823529412 | AUROC | 0.767098754903633 | 0.8031724373187787 | 0.03607368241514575 | -0.03982551458858609 | 0.13076677953987448 | 2000 | 0 | No prespecified support flag |

These are actual F2−U1 prediction-score effects, distinct from the prior error-complementarity table. All four actions are retained. Shared whole-recording draws are filtered by action; invalid one-class/empty draws are counted, not replaced. Different APs reflect action-specific prevalence as well as ranking; no favorable macro-AP headline is created.

## Recording-balanced sensitivity analysis

| analysis | metric | weighted_positive_prevalence | U1 | F2 | F2_minus_U1 | lower_95 | upper_95 | valid_replicates | undefined_replicates |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| recording-balanced sensitivity analysis | AUPRC | 0.12382082163051569 | 0.431672146976423 | 0.4507323266570945 | 0.01906017968067153 | -0.000405174052196834 | 0.03678702587178713 | 2000 | 0 |
| recording-balanced sensitivity analysis | AUROC | 0.12382082163051569 | 0.7702004573043821 | 0.7780416831054865 | 0.007841225801104357 | -0.022256613044367844 | 0.029918172611703344 | 2000 | 0 |
| recording-balanced sensitivity analysis | Brier | 0.12382082163051569 | 0.0885376527578312 | 0.08613884750340003 | -0.0023988052544311605 | -0.004355359996989945 | -0.00039240854034509144 | 2000 | 0 |

Every segment in recording r has weight1/n_r; a recording drawn k times contributes weight k/n_r per segment. This is weighted pooled AP/AUROC/Brier, not a mean of per-recording AUROCs. Original segment-weighted estimates remain primary; changing the target-population weighting is a sensitivity analysis, not automatic invalidity.

## Established operating points

| model | TP | FP | TN | FN | failure_precision | failure_recall | specificity | false_positive_rate | flagged_fraction | false_flags_per_100_successes | true_failures_per_100_flags | misses_per_100_failures | flags_denominator | success_denominator | failure_denominator | segment_denominator |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U1 | 313 | 819 | 3202 | 196 | 0.2765017667844523 | 0.6149312377210217 | 0.7963193235513554 | 0.20368067644864463 | 0.24988962472406182 | 20.36806764486446 | 27.65017667844523 | 38.50687622789784 | 1132 | 4021 | 509 | 4530 |
| U2 | 337 | 1525 | 2496 | 172 | 0.18098818474758324 | 0.6620825147347741 | 0.6207411091768217 | 0.3792588908231783 | 0.411037527593819 | 37.92588908231783 | 18.098818474758325 | 33.791748526522596 | 1862 | 4021 | 509 | 4530 |
| F2 | 311 | 754 | 3267 | 198 | 0.292018779342723 | 0.6110019646365422 | 0.8124844566028351 | 0.1875155433971649 | 0.23509933774834438 | 18.75155433971649 | 29.2018779342723 | 38.89980353634578 | 1065 | 4021 | 509 | 4530 |
| F6 | 291 | 675 | 3346 | 218 | 0.30124223602484473 | 0.5717092337917485 | 0.8321313106192489 | 0.16786868938075106 | 0.21324503311258278 | 16.786868938075106 | 30.124223602484474 | 42.82907662082515 | 966 | 4021 | 509 | 4530 |

Counts use saved hard decisions, checked against retained fold-specific training-selected thresholds. True failures per100 flags is precision×100; misses per100 actual failures is (1−recall)×100; false flags per100 successful segments is FPR×100. The procedure may select different thresholds in different outer folds. These are retrospective completed-action classifications, not prospective warnings; no false alarms/hour is inferred without validated exposure time. No new test-outcome cutoff was chosen. Intervals remain conditional on fitted models and do not eliminate adaptive study selection.
