# REASSEMBLE cohort,split and seed reconciliation

The753-action evaluation is an exact strict subset of the4,530-action original cohort: original outer fold0 (legacy fold_01). All753 native recording/segment keys and labels match;there are77 failures across26 recordings. The larger cohort contains509 failures across148 recordings. The remaining3,777 actions are the original outer training pool.

The920 rows are a different,disjoint inner assessment bank inside that3,777-action pool. In the100-epoch pilot,the selected original inner-fit3 training recipe is retained (1,752 gradient-training,419 validation,686 calibration),but assessment is changed to the753 outer actions. Thus “fit3” does not mean “outer fold3”. The saved selected-job prediction_recordings field still lists28 inner-bank recordings while actual outer predictions cover26;this conflict is preserved in METADATA_CONFLICTS.csv. Actual IDs govern this reconciliation.

## Exact outer cohorts

| Original fold | Legacy name | Outer training actions | Held-out actions | Failures | Held-out recordings | Cohort ID |
|---|---|---|---|---|---|---|
| 0 | fold_01 | 3777 | 753 | 77 | 26 | C610d5ede0dfb79ad |
| 1 | fold_02 | 3566 | 964 | 109 | 31 | Ccda45dffcb5b0e75 |
| 2 | fold_03 | 3493 | 1037 | 125 | 32 | C6fafb679c8ee793f |
| 3 | fold_04 | 3624 | 906 | 99 | 29 | Ca7d910a99df4956a |
| 4 | fold_05 | 3660 | 870 | 99 | 30 | C05495727518894ec |

## Rules for direct comparisons

A direct descriptive performance comparison requires identical native action IDs,identical native labels,identical assessment role and the same corruption/observation condition. These are encoded in matched_comparison_group. Equal N alone is never evidence of equality. Pooled4,530-action AP must not be directly ranked against753-action AP;use matched fold0 results or separately report the pooled estimand. Inner validation,meta-training,permuted-label controls and diagnostic selected examples are not final held-out evaluations.

Within a matched group,model/seed differences can be described on those same actions. Different fitting rows,calibration/stacking banks,frame contracts,budgets or prior test-driven selection prevent an isolated causal attribution or a confirmatory superiority claim. AP/AUROC are recomputed only from existing probabilities;threshold-dependent metrics retain their original conventions in the historical audit and must not be mixed. No training or fitting occurred.

## Where to inspect identities

- [Every registered training run: exact role counts,seeds,folds and cohort IDs](ALL_TRAINING_RUN_COHORTS.csv).
- [Every experiment summary](EXPERIMENT_COHORT_SPLIT_SEED_SUMMARY.csv).
- [Every inspected saved evaluation and its matching passport](ALL_EVALUATION_COHORTS.csv).
- [Matched comparison groups](MATCHED_COMPARISON_GROUPS.csv).
- [Clean753/4,530-action performance,kept in separate cohort groups](MATCHED_CLEAN_PERFORMANCE.csv).
- [Every exact action membership](COHORT_ACTION_MEMBERSHIP.csv) and [recording lists](COHORT_REGISTRY.csv).
- [Canonical native keys](CANONICAL_ACTION_MANIFEST.csv) and [legacy sample-ID aliases](SAMPLE_ID_ALIAS_MAP.csv).
- [Subset proof](SMALLER_COHORT_SUBSET_PROOF.json),[metadata conflicts](METADATA_CONFLICTS.csv) and [unrecoverable identities](MISSING_IDENTITY_EVIDENCE.csv).

Row-index-only banks are linked to the original cohort after verifying its saved order and labels against the original source-manifest filter. Saved fit receipt IDs take precedence over stale human-readable recording summaries. Unknown identity evidence remains explicit;no sample/participant identity is invented. Every source path/hash is preserved.
