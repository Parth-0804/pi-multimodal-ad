# Matched REASSEMBLE comparison and interpretation

**The753-action cohort is exactly original outer fold0 (legacy fold_01), a strict subset of the4,530-action cohort.** The intersection has753 actions,77 failures and26 recordings; no unmatched smaller-cohort action or label was found. The full cohort has509 failures and148 recordings. Native keys, timestamps, action names and labels were checked; legacy hashed sample IDs are retained as aliases.

## Exact outer partitions

| Zero-based outer fold | Legacy fold | Training N | Held-out N | Failures | Held-out recordings |
|---|---|---:|---:|---:|---:|
| 0 | fold_01 | 3777 | 753 | 77 | 26 |
| 1 | fold_02 | 3566 | 964 | 109 | 31 |
| 2 | fold_03 | 3493 | 1037 | 125 | 32 |
| 3 | fold_04 | 3624 | 906 | 99 | 29 |
| 4 | fold_05 | 3660 | 870 | 99 | 30 |

Every exact recording list is in [ORIGINAL_OUTER_FOLDS.csv](ORIGINAL_OUTER_FOLDS.csv); every exact action membership is in [COHORT_ACTION_MEMBERSHIP.csv](COHORT_ACTION_MEMBERSHIP.csv). All five outer test sets partition4,530 actions and148 recordings without overlap.

## Clean comparisons on the identical753 outer actions

| Model and recipe | AP | Evaluation ID |
|---|---:|---|
| Original frozen visual (original recipe) | 0.2328051167 | E000082 |
| C20 full CNN outer refit, seed42 | 0.2153209263 | E000006 |
| Frozen CNN100 (M1) | 0.1937755776 | E000030 |
| Full CNN100 (M2) | 0.2125845033 | E000031 |
| Static sensor (M3; original sensor scores) | 0.3277045645 | E000032 |
| Original static F2, restricted to fold0 | 0.3671552457 | E000115 |
| Frozen CNN100 + F2 (M4) | 0.3349773516 | E000033 |
| Full CNN100 + F2 (M5) | 0.3490942201 | E000034 |
| Frozen CNN100 + averaging (M6) | 0.3480067520 | E000035 |
| Full CNN100 + averaging (M7) | 0.3585334022 | E000036 |

These point estimates were recomputed from saved probabilities. All rows use the same native failure labels and clean held-out actions. They permit descriptive comparison on this fold; training and selection differences prevent treating every pair as a controlled intervention. The original sensor row and M3 are the same saved score vector, not independent sensor replications. M1/M2 also alias their standalone100-epoch visual outputs.

**Fine-tuning improves the100-epoch visual recipe from0.1937756 to0.2125845 on this fold.** That statement compares frozen100 with full100. The original frozen recipe scores0.2328051 on these same actions, so the result does not establish superiority over that original recipe. Full100 F2 improves its point AP over frozen100 F2 (0.3490942 versus0.3349774); the existing paired uncertainty interval crosses zero. No new significance test was performed. Original F2 scores0.3671552 on the same fold, but uses a different nested stacking protocol. Do not attribute differences across those recipes solely to CNN fine-tuning.

## Separate4,530-action pooled comparisons

| Model | Pooled AP | Evaluation ID |
|---|---:|---|
| Original frozen visual | 0.2306583150 | E000081 |
| Original static sensor | 0.4293918694 | E000092 |
| Original static F2 | 0.4472985514 | E000114 |
| C20 full CNN, seed42 | 0.3121270257 | E000029 |

**Do not rank these pooled AP values against the753-action table.** Use the matched fold0 results above for a common-action comparison, or compare complete five-fold pooled outputs separately. The smaller subset has failure prevalence77/753; the larger cohort has509/4530. There is no100-epoch prediction bank for the other3,777 outer-assessment actions.

## What selected “fit3” means

| Run | Gradient train | Validation | Calibration | Assessment |
|---|---:|---:|---:|---|
| C20 job_index2, inner fit3 | 1,752 | 419 | 686 | 920 inner actions |
| Frozen100 / full100 selected job2 | 1,752 | 419 | 686 | 753 outer actions |
| C20 outer refit job_index4 | 2,385 | 581 | 811 | Same753 outer actions |

The100-epoch pilot retained the selected C20 inner fit’s exact T/V/C identities and order, then changed assessment to the original outer fold0. Its reserved920 inner actions later form the single holdout fusion-fitting bank. That920-action bank is inside the original3,777 outer-training pool and is disjoint from the753 outer test actions. “Fit3” is an inner job name, not outer fold3. The saved partition seed and estimator RNG seed are separate fields; validation_split_seed for original job2 and its100-epoch copy is20261028.

The100-epoch selected-job JSON has a stale prediction_recordings list:28 inner-bank recordings, while actual predict indices, executed sample IDs and outer_E_recordings identify26 outer test recordings. The two lists are disjoint. The original JSON remains unchanged; [METADATA_CONFLICTS.csv](METADATA_CONFLICTS.csv) gives the exact differing identities.

## Coverage and reviewer workflow

This supplement reconciles 6,894 saved fit records across 20 training groups, plus 6,592 saved evaluation records, including inference-only and robustness workflows. It does not assert that every fit is a distinct independent model: reused sensor fits, repeated seed families and identical saved scores are explicitly retained. Zero assessment-identity rows remain unresolved in the completed audit inventory. This is a cohort reconciliation, not a rerun of the comprehensive audit.

1. Start with [EXPERIMENT_COHORT_SPLIT_SEED_SUMMARY.csv](EXPERIMENT_COHORT_SPLIT_SEED_SUMMARY.csv) and [ALL_PREDICTION_WORKFLOW_SUMMARY.csv](ALL_PREDICTION_WORKFLOW_SUMMARY.csv).
2. Find a fit in [ALL_TRAINING_RUN_COHORTS.csv](ALL_TRAINING_RUN_COHORTS.csv); resolve each role cohort through [COHORT_REGISTRY.csv](COHORT_REGISTRY.csv) and [COHORT_ACTION_MEMBERSHIP.csv](COHORT_ACTION_MEMBERSHIP.csv).
3. Find an evaluation in [ALL_EVALUATION_COHORTS.csv](ALL_EVALUATION_COHORTS.csv). Direct descriptive comparisons require the same permitted matched_comparison_group. Non-clean observations are source-specific: a shared corruption name alone does not prove equal corrupted inputs.
4. Consult [COMPARABILITY_MATRIX.csv](COMPARABILITY_MATRIX.csv) for the explicit key comparisons, and [MATCHED_COMPARISON_GROUPS.csv](MATCHED_COMPARISON_GROUPS.csv) for lossless grouping of every evaluation.
5. Recalculate from [ALL_CLEAN_HELD_OUT_PREDICTIONS.csv](ALL_CLEAN_HELD_OUT_PREDICTIONS.csv), joined by evaluation_id to the evaluation table and by native_key to the action manifest. Scores are exported without threshold changes. [IDENTICAL_PREDICTION_ALIASES.csv](IDENTICAL_PREDICTION_ALIASES.csv) identifies repeated evidence.
6. Inspect [SOURCE_PROVENANCE.csv](SOURCE_PROVENANCE.csv) for original source paths and SHA256 hashes. Larger source probability banks remain external; the clean held-out score rows used here are included.

Exact fit-level estimator seed fields unresolved by this adapter: 0. Nominal seed families, split/role seeds, validation seeds, estimator random_state and reused-fit provenance remain separate. A pooled outer result may have a different actual training seed per fold; per-run seed records govern. A seed-mean row is an ensemble, not one extra seed. Original audit fields are preserved alongside recovered values.
