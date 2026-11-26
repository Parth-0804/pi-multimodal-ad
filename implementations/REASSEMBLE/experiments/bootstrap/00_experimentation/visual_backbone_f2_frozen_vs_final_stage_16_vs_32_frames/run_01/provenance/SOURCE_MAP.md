# Targeted source map for this study

These are direct source/object observations, not validation of historical scores. The original source bytes are retained in `source_snapshots/`; selected original hashes and the existing dirty status are in `initial_state.json`. No historical launcher was executed.

| Observed source | Relevant executed or inspected logic | Consequence for the new study |
|---|---|---|
| `src/reassemble/section1_features.py:32`, `statistics` | Ten channel statistics; progress slope and NaN handling | Small attributed pure implementation; direct synthetic regression against the original function |
| `src/reassemble/alignment.py:47`, `resample_progress` | 512 progress positions, no extrapolation, long-gap masking at five native intervals | Same formula, tested against the original pure functions |
| `src/reassemble/section1_features.py:43`, `load_visual` | Local RT-DETR weights; returned object is `.model.backbone.model`; unconditional `requires_grad_(False)` | A config flag alone cannot unfreeze this caller. New loader verifies original local file hashes and exposes only the CNN |
| `src/reassemble/section1_features.py:88`–99 | Uniform rounded 16-frame indices; selected feature-map spatial means concatenated and frame-mean pooled; historical autocast float16 | Preserve the 16 indices; add a deterministic 32-frame superset. New study uses float32 consistently and does not reuse the old float16 feature bank |
| `src/reassemble/section1_models.py:20`, `Standardizer`; `VisualHead:31` | G/local mean/std with floor `1e-6`; Linear(D,128), ReLU, dropout 0.1, Linear(128,1) | Same head and fixed normalizer policy in all arms |
| `src/reassemble/section1b.py:83`, `fit_stacker`; `stacking:101` | Unweighted logistic stacking of branch probabilities; historical threshold/subfold choices | Retain F2 probability formulation; use the newly authorized G/C calibration, fixed C and threshold 0.5 rather than treating this as historical score reproduction |
| `src/reassemble/additional_improvements/finetune.py:47`, `FineTunedVisual` | Unfreezes `encoder.stages[3]`, but constructs `TemporalHead` and uses a different existing training path | Do not import or continue that fit. New mean-pooled head starts independently from original weights |
| `src/reassemble/additional_improvements/prefix_cache.py:15`, `prefix`; `CachedFineTunedVisual:23` | Frozen spatial-prefix boundary before stage 3; wrapper coupled to the existing temporal head | Inspected only. No historical prefix cache or learned segment bank is used |
| Original local model object | `RTDetrResNetBackbone`, selected `stage2/stage3/stage4`, four encoder stages; final stage five convolution tensors totaling 8,388,608 parameters | Object construction is recorded in `executed_model_object.json`; actual forward/gradient evidence remains a separate preflight check |

The new forward is `processed pixels → CNN selected maps → spatial means → frame mean → fixed G normalizer → head → raw logit`. In the adapted arms, gradients reach only the final spatial stage. Its normalization affine quantities are buffers in this object, not additional trainable parameters. All CNN normalization buffers remain fixed. The full RT-DETR wrapper supplies local pretrained weights during construction; its encoder/decoder/detection caller is never forwarded.

Scientific differences from historical F2 include the common 32-frame eligibility cohort, new independent fixed five-epoch fits, original-feature normalizers fixed through adaptation, recording-disjoint calibration holdouts, fixed sensor C=1, float32 policy and threshold 0.5. Historical AP is not used as a required target or implementation proof. Previously examined data remain exposed.

Every new fit is tied to cohort, partition, original-weight, feature, config and source identities. Direct recording/segment keys are stored in predictions. Conditional recording-cluster uncertainty does not validate repeated-training reproducibility. A clean independent rerun and independent review remain outside this first execution's evidence.
