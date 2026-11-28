# Current approved25 versus historical75 fit status

**STOPPED_AFTER_25_COMPLETED_FITS** is the saved terminal cap state at2026-11-03T12:23:30Z, still supported by current receipts. All25 approved C20 fits completed20 epochs, seed42, four inner fits plus one outer refit per each of five outer folds. This is500 completed scientific epochs, not a25-epoch checkpoint threshold. The50 additional fits are **DEFERRED_NOT_EXECUTED**: seeds123 and20261023,25 jobs each. No restart,repair or extra fit is part of this audit.

The earliest protocol planned150 visual fits:75 long-frozen B and75 full-CNN C, three seeds, five outer folds and four inner roles. One B inner fit completed25 epochs (selected9). C job0 initially followed that protocol, then was continued from its saved complete epoch9 into the C-only20 revision. The revision removed the74 unstarted B fits, retained75 C fits with exactly20 epochs each, and kept cosine50 for continuation compatibility. The subsequent cap explicitly approved only seed42’s25 C fits and deferred50. Calling this a75-fit failure would misstate the approved scope.

The C20 controller still has a75-completion precondition for its original `finalize()` path; therefore `PHASE1_C_ONLY_ALL_COMPLETE.json` and `PHASE1_C_ONLY_FINAL_METRICS.json` are absent. C20 visual outer predictions exist, but complete F2 coefficient fitting/final evaluation has not run. A separately authorized25-fit analysis path could use the saved inner predictions; no additional CNN training is intrinsically required to compute those missing fusion models, but new CPU model fitting is outside this read-only audit.

| Seed | Inner fits complete | Outer refits complete | Epochs per fit | Actual status |
| --- | ---: | ---: | ---: | --- |
|42|20|5|20|approved cap complete |
|123|0|0|0 executed;20 planned|25 deferred |
|20261023|0|0|0 executed;20 planned|25 deferred |

| audit_fit_id | seed | job_index | outer_fold_zero_based | role | epochs | selected_epoch | fit_identity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R0002 | 42 | 0 | 0 | inner_fold_01 | 20 | 19 | 3978f843c00a1dafa2134887e6216116a5062b10c3fcc4378e32718c3f556d96 |
| R0003 | 42 | 1 | 0 | inner_fold_02 | 20 | 16 | 842c4590310d9432ca6ec2c0e34436e9f734824da3d8857528e75117fb6546db |
| R0004 | 42 | 2 | 0 | inner_fold_03 | 20 | 19 | fbe3e9184cfc05c9b9304937d1196d87648edf275815a5c475f6e734f5989c21 |
| R0005 | 42 | 3 | 0 | inner_fold_04 | 20 | 17 | 685c65da44272048f8132c405fbee5d9a1cafb0fac4618b5a06205b877162b35 |
| R0006 | 42 | 4 | 0 | outer_assessment | 20 | 19 | cabce6105f0647052bb0fcb86a54bc17f9a6faad1c6f4bce258cae66d91ae9ca |
| R0007 | 42 | 5 | 1 | inner_fold_01 | 20 | 19 | 2725b046ca2e5c2ccec6163c0a48f18eed64fcc2da45c467337a8f2f08994958 |
| R0008 | 42 | 6 | 1 | inner_fold_02 | 20 | 19 | dedf826164909de130374798ac4246a63a6a96580c5ac41549621077a3b92a55 |
| R0009 | 42 | 7 | 1 | inner_fold_03 | 20 | 20 | e525edd7823d6231359c4458fdbbd14658824523aefb4278eee626185cc1fabd |
| R0010 | 42 | 8 | 1 | inner_fold_04 | 20 | 2 | d3fab0e4e8bc99b222ba368791c68a901e0b240c2efe0ed8dac70223a514cba9 |
| R0011 | 42 | 9 | 1 | outer_assessment | 20 | 20 | c1c81f5c890df95a61b880cfff8e7bc57732a0076980c4718e9ebf8fa3a22d98 |
| R0012 | 42 | 10 | 2 | inner_fold_01 | 20 | 5 | a149228716c50eae07f8414ae509d5486d2191bd6823ed65218bcf0c002cfb98 |
| R0013 | 42 | 11 | 2 | inner_fold_02 | 20 | 19 | 3e8c3b5e88ceef0393febd716ed922c26eceb4fccbc73551c6a0522919bbb0f5 |
| R0014 | 42 | 12 | 2 | inner_fold_03 | 20 | 6 | 0d14682db6e795e9ab7e093c8b6e869bca474cb9f531f696b284466ccad5dff5 |
| R0015 | 42 | 13 | 2 | inner_fold_04 | 20 | 8 | 5a0332ed3a2b19ed30004806129ae23a1fef5fee49f44d87c2e621f5a1c88522 |
| R0016 | 42 | 14 | 2 | outer_assessment | 20 | 19 | 04885e4abda2e3531bf5c1982ccd1853258a5f416ceb460919b82cc298caf4f4 |
| R0017 | 42 | 15 | 3 | inner_fold_01 | 20 | 17 | f0c075c26cfd176d20c43b6f711eba4def49e729b2621cac7706d6aed2798936 |
| R0018 | 42 | 16 | 3 | inner_fold_02 | 20 | 1 | 8527bef7280da2e49c86c2b44b078fb34e29c262afc2ce64a438a3454a93a499 |
| R0019 | 42 | 17 | 3 | inner_fold_03 | 20 | 20 | 0288d5977cedcc095a7e6ea8ab6b55939d4aa62c68378206e5252c5a4c9e4f33 |
| R0020 | 42 | 18 | 3 | inner_fold_04 | 20 | 7 | 6d326bfcac27932c62fb1d2f15ee47ff6dfa75f4ed309753b5d7038f50cc33b7 |
| R0021 | 42 | 19 | 3 | outer_assessment | 20 | 20 | dcec9fbdfdf7b58af3d07e46f2b4651a3b9a77127938d8adc058b701550dea0b |
| R0022 | 42 | 20 | 4 | inner_fold_01 | 20 | 9 | 662699905b3c8a344f14ee562119c977e1ade627d555c2dcfe6f33b6abdd50ff |
| R0023 | 42 | 21 | 4 | inner_fold_02 | 20 | 6 | 3969fca6660ced3445e2fae0d17eed0416415d0524ea95818fbc93fb3c7c59de |
| R0024 | 42 | 22 | 4 | inner_fold_03 | 20 | 17 | 1ecb165ca9a6c650fbda9135fd853f58e84d2ee588ceb3dd20af24dabb30a7a6 |
| R0025 | 42 | 23 | 4 | inner_fold_04 | 20 | 5 | 0c648f0cc783591de2e26bc233d4c6b32af49abac7aceb50f56098de05ca30e4 |
| R0026 | 42 | 24 | 4 | outer_assessment | 20 | 20 | 4eae69709405f15d37fffe31d13c179b085a4a427a92f5e07f482d6dde08ed40 |


The C20 saved checkpoint count/receipt hash checks are separate from process-attempt status. MAIN retains one old RUNNING attempt row even though its fit subsequently completed and the cap controller stopped. This is stale bookkeeping, not evidence of current live training. The root audit records current process inspection separately. Source/hash consistency and recovery-slot status are reviewed in [11](11_CHECKPOINT_INVENTORY.csv); no checkpoint was repaired or promoted.

Preflight development checkpoints (including a full-CNN one-epoch smoke test),13 synthetic recovery directories,one C20 revision test at epoch8,and disposable bootstrap checks are non-study artifacts. They do not fill any of the50 deferred C20 slots. Retry attempts do not add independent completed fits. The donor validator’s25-source-epoch condition is a separate protocol mismatch: it can reject a legitimate completed20-epoch checkpoint and does not invalidate C20 completion.

Source paths and hashes are in [TRAINING_INPUT_MANIFEST.csv](support/TRAINING_INPUT_MANIFEST.csv), exact original fit paths in [TRAINING_FIT_PATHS.csv](support/TRAINING_FIT_PATHS.csv), and all50 planned role rows in [04](04_SEED_FOLD_AND_EPOCH_COVERAGE.csv). The unchanged source/hash audit and current discovery found no additional completed scientific C20/100 fit beyond these scopes.
