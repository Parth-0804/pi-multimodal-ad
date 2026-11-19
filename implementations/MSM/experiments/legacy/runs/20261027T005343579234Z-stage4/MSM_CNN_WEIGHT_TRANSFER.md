# MSM CNN weight transfer

**Transfer efficacy is not evaluated: the required trained source checkpoint is unavailable.** A CPU-only state compatibility audit and strict transfer adapter are complete. No diagnostic or active checkpoint was used as condition R, and no source-domain classification/fusion weights were applied to MSM.

## Source selection fixed without MSM performance

Original P: verified local `PekingU/rtdetr_r18vd`, revision **ac77a11ff0170a41b771c03264987f8ce2b0d753**. Original safetensors SHA-256 **fe87a5a30f5daf298d10794c7682a63b6107986f97d6a770ba948d89e4340093**, with matching config/preprocessor hashes in `manifests/CNN_transfer_compatibility.json`. Only the executed ResNet CNN would initialize MSM; no hybrid encoder/decoder/detection outputs are used.

Canonical R rule, locked in `config/resolved_config.json`: Phase 1 arm **C_full_finetuned16**, source seed **42**, original outer fold **0** (human fold 1), role **outer_assessment**, job index **4**. Use that role's completed, source-validation-selected best checkpoint. It is a fixed source identity, not an MSM AP-based choice. All three MSM seeds would reuse this same R source, testing MSM fitting variability, not source-training-seed variability. There is no implicit permission to choose a better source from MSM test results.

Expected folder: `26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_execution/26102026_main_run_01/26102026_seed42_C_full_finetuned16_outer1_outerassessment`. A completed individual canonical C fit is sufficient after provenance verification; completing all 150 Phase 1 fits is **not** an arbitrary additional gate.

At snapshot **2026-10-27T00:56:02.004172+00:00**:

| Source candidate | Observed state | Admissibility |
| --- | --- | --- |
| Original pretrained P | Hashes match; 11,190,112 executed-CNN parameters | P initialization available |
| Completed B_long_frozen16 inner fit | One completion receipt; head-only checkpoint, original CNN stayed frozen | Cannot establish REASSEMBLE-trained CNN transfer |
| Active C_full_finetuned16 inner fit | Best/recovery checkpoint filenames exist; no completion receipt | Unfinished training/selection; not an admissible source |
| Canonical C outer-assessment fit | No completed selected checkpoint | R dependency missing |
| Full-CNN preflight reload file | Hash-verified diagnostic; numeric/recovery tests passed | Architecture/state audit only, never condition R |

Phase 1's **numeric gate PASSED** proves executed-CNN gradients/updates/reload/recovery on its pilot. It does not turn the diagnostic into a completed, validation-selected source fit. `PHASE1_COMPLETED_FIT_INDEX.json` recorded one B and **zero C** completions; `PHASE1_ALL_COMPLETE.json` was absent. Active snapshots are point-in-time observations and may change as the independent Phase 1 controller runs. No active `.pt` payload was read or copied. Stable completed B and diagnostic hashes were checked; source-domain held-out performance did not choose R.

## Measured compatible tensor scope

CPU structural audit used the immutable preflight reload payload solely to verify Phase 1 serialization compatibility with the original CNN. It was never loaded for MSM prediction/training:

- Original backbone has **115 state tensors**, **11,190,112 parameters**.
- Diagnostic serialization provides exactly **115 compatible CNN tensors**, no missing/extra names and no shape/dtype/nonfinite errors.
- **69 tensors differ from original pretrained P** in that diagnostic. This confirms changed values exist in the serialization, not transfer efficacy or learned generality.
- Six source-domain entries are explicitly excluded: four visual-head weights/biases and `mean`, `std`. Sensor parameters, calibrators, F2 coefficients, optimizer/RNG and labels are not transferable input state.
- Diagnostic hash **176c2e418560a8a79fd288bc1dddf655370d053028178f88d6abc0b609eb1301**; exact path and exclusions are recorded in `manifests/CNN_transfer_compatibility.json`.

Phase 1 promotes FrozenBatchNorm affine weight/bias buffers into trainable Parameters. Their **state-dict names/shapes do not change**. Transfer must include their learned values along with all convolutions and preserved normalization running buffers, then load into the new frozen MSM backbone with `strict=True`. Discarding affine values or loading only the final stage would change the defined source condition. Both P and R then execute the same frozen/eval CNN and identical pooling/input transform; only initialization values differ.

## Reusable implementation and tests

`MILLING DATASET/source/msm/transfer.py` adds three focused functions:

1. `validated_source`: require final completion receipt, exact C arm/seed/predefined job, at least 25 completed source epochs, selected epoch/identity consistency, checkpoint SHA-256 before/after safe `weights_only=True` CPU loading.
2. `compatible_cnn_state`: select only exact `backbone.*` state and require complete target names/shapes/dtypes/finite values, including normalization buffers. Reject partial, detector, head-only and invalid states before modifying a target.
3. `transfer_completed_cnn`: load only the verified CNN into a supplied new MSM backbone and freeze it. It never loads source heads/scalers/fusion.

Fifteen new synthetic tests cover valid CNN-only state including buffers, head/scaler exclusion, incomplete/extra/shape/dtype/nonfinite tensors, absent completion, wrong source arm/seed/role/hash/identity/epoch and premature source completion. All 61 MSM tests pass. No executed operation mutated the active source fit, model framework or historical outputs.

## What the comparison can eventually support

After both cohort and canonical-source gates pass, fit new MSM heads with the same three seeds and fixed budget, compare held-experiment AP and other frozen metrics, and refit F2 independently from P/R group-OOF predictions. Use paired group-cluster uncertainty, not best-fold/seed selection. Additional source pretraining exposure and source checkpoint identity are part of condition R and must be reported. One fixed source checkpoint does not establish robustness over all REASSEMBLE training seeds.

Present conclusion: **CNN serialization compatibility is verified; positive or negative transfer, F2 benefit and a cross-domain representation claim are unmeasured.** Selected R source and selected MSM Stage 4 checkpoints remain empty in `manifests/selected_checkpoints.json`.
