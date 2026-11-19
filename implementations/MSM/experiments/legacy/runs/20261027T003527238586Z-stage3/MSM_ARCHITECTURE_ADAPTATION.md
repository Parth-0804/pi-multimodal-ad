# MSM architecture adaptation

**A small MSM package composes the verified REASSEMBLE feature extractor and head constructor. No framework, pretrained detector, failure-classification weights or F2 coefficients were duplicated.** All new MSM source/configuration/tests/results remain under `MILLING DATASET/`.

Dataset `manufuturetoday/multi-sensor-for-metal-milling-anomaly/versions/2`; Stage 2 input contract is restricted to retrospective coarse milling context and pre-aggregated MTConnect measurements. It does not establish fine tool-contact visibility or causal subsecond MTC synchronization. Full evaluation is blocked by positive-group support, not by a failed software forward path.

## Exact architecture and contracts

| Component | Verified contract |
| --- | --- |
| Annotation adapter | One immutable native CSV row, exact `[start,end)` sensor seconds, source hash and `machine/experiment/rowN` interval ID; native label retained |
| Frame adapter | Exactly 16 ordered distinct native indices selected by the corrected Stage 2 selector; native PTS, decoded BGR SHA-256 and uncertainty checked again when decoding |
| Geometry | Native coded 720×480, SAR 3:8 → displayed 270×480 portrait; aspect-preserving resize to 360×640, centered in black 640×640 canvas |
| Pixel tensor | Loader `uint8 [16,3,640,640]`; model `float32 [B,16,3,640,640]`, RGB scale 1/255, no ImageNet normalization |
| CNN | Existing local `PekingU/rtdetr_r18vd`, revision `ac77a11ff0170a41b771c03264987f8ce2b0d753`; ResNet CNN only, 11,190,112 frozen parameters; frozen eval-mode normalization |
| Pooling | FP32 spatial mean of final maps with 128/256/512 channels → concatenated 896-vector per frame; mean over exactly 16 frames → `[B,896]`; no learned temporal model |
| Visual branch | Training-only 896-value standardizer → NEW Linear(896,128), ReLU, dropout(0.1), Linear(128,1); 114,945 trainable parameters; one logit/probability per interval |
| Sensor adapter | Actual MTC rows in that same native `[start,end)` cut; finite values, ≥5 rows, no >0.5 s coverage gap; no interpolation |
| Statistics | Channel-major mean, population std (ddof=0), RMS, min, max, peak-to-peak; 15 configured channels → `[B,90]`; schema can select a permitted subset and does not require REASSEMBLE channels |
| Sensor branch | Independent training-only 90-value standardizer → NEW balanced L2 logistic C=1; 91 fitted coefficients including intercept; one probability score per interval |
| Static F2 | Exactly `[B,2]` paired visual/sensor OOF probabilities → NEW unweighted L2 logistic C=1, three fitted scalars; one probability score per interval |
| Averaging control | Nonlearned arithmetic mean of those same two branch scores |
| Outputs | Exactly one binary cutting prediction per source interval, probability score and fixed-threshold 0.5 decision; no frame-level labels or experiment-wide arbitrary windows |

The exact frame guard is `alignment_uncertainty + median_native_frame_step/2`. Equal-bin centers inside the guarded cut map through `video=sensor+offset`; nearest native frames must remain distinct, content-unique, inside validated acoustic support and wholly inside the original cut under the timing bound. Alignment is never optimized against anomaly labels. VMX dataset9 uses the corrected **+49.730 s ±0.100 s** mapping, not the discarded exploratory +16.04 s alias.

Stage 2's 224×224 tensors were feasibility prototypes, not the verified CNN input. Stage 3 explicitly changes the display-preserving canvas to 640×640 and validates actual raw-frame identities again. Using division by 255 versus the shipped float32 rescale multiplication differs by at most **5.96e-8**, within one float32 ULP; no ImageNet mean/std is applied. Geometry is an explicit MSM adapter, not a silent change to historical REASSEMBLE extraction.

MTC channels: `watt`, `Spindle_Speed`, `S_Axis_Load`, `Feed_Rate`, `X_Axis_Load`, `Y_Axis_Load`, `Z_Axis_Load`, `smarms`, `xmarms`, `ymarms`, `zmarms`, `smvrms`, `xmvrms`, `ymvrms`, `zmvrms`. `manifests/sensor_contract.json` records exact ordered feature names and each sampled cut's gates. Statistics match Stage 2 values exactly for all 24 sampled intervals. MTC rows contain held, already aggregated vibration/power measurements; their unknown aggregation latency is not repaired by row-level timestamps. These are coarse controller statistics, not fresh high-rate accelerometer samples. The separate 39-example raw-ACC cohort and industry CT are excluded from this model contract.

No native-label/context sheet column enters those 90 values. Spindle speed and feed are observed signal channels, not label-sheet `N/F`; possible regime confounding remains a limitation. Time, experiment, label, geometry parameters and IDs control selection/grouping only. Channel count/identity is configured for MSM, not inherited from the robot data. Missing branches stop the primary pipeline; there is no undocumented fallback or mixed-schema pooling.

## Reuse and ownership

| MSM source | Responsibility / reuse |
| --- | --- |
| `source/msm/data.py` | Native labels, interval identities, group metadata, MTC loading/gates, configured statistics, exact frame decode/hash/PTS, SAR letterbox; imports Stage 2 accumulators and corrected selector |
| `source/msm/models.py` | Thin CNN/head composition; imports `reassemble.section1_features.load_visual` and `reassemble.section1_models.VisualHead/Standardizer`; fresh milling sensor/F2 estimators; safe tensor checkpoint serialization and metric functions |
| `source/msm/splits.py` | Group-disjoint complete coverage, class-support gate, frozen nested folds and development-only partition |
| `source/msm/experiment.py` | Shared fitting and prediction composition, leakage-safe OOF bank and full-training branch refits; accepts no outer assessment results |
| `source/msm/smoke.py` | Bounded real-input smoke and loading timings, provenance, reserve/cap checks; never launches outer evaluation |
| `source/msm/head_benchmark.py` | Two-update CPU/CUDA development-head path check inside combined smoke caps |
| `source/msm/benchmark.py` | Optional strictly admitted exclusive timing follow-up; refused the occupied GPU before any work in this stage |
| `source/msm/validate.py` | Synthetic tests, prior-output preservation, frozen config, environment and Git bulk-exclusion checks |
| `configs/stage3_protocol.json` | Portable settings, dataset version, local model provenance, budgets, targets, splits and seeds |
| `tests/test_stage3.py` | Synthetic scientific-contract, leakage, forward/gradient/checkpoint and metric tests |

Nothing under `src/reassemble/`, its historical runs, raw PHM/Intel roots or active REASSEMBLE experiment sources was edited. Existing model files are read from the repository-relative location in the original REASSEMBLE configuration; missing or mismatching weights stop before the reused loader could download anything. No absolute workstation data path was added to configuration.

Pretrained SHA-256: `model.safetensors` = `fe87a5a30f5daf298d10794c7682a63b6107986f97d6a770ba948d89e4340093`; config and processor hashes are in `manifests/pretrained_model.json`. Only this pretrained CNN representation is reused. Every milling classification parameter is freshly initialized/fitted; no REASSEMBLE failure head, visual scaler, sensor scaler, calibrator or fusion coefficient is loaded.

## Runtime, gradient and checkpoint behavior

The frozen backbone intentionally receives no gradients. Tests require finite nonzero gradients and parameter updates through the new visual head. The sensor and F2 models are convex scikit-learn fits, not differentiable Torch branches, so their fitting integrity is checked through convergence, provenance and prediction/reload checks. CPU/CUDA new-head forwards and gradients are separately verified using actual MSM cached features. Tensor checkpoints include new head/scalers/sensor/F2 coefficients plus interval IDs and feature order; they reload with `weights_only=True`, without estimator pickle or copying pretrained weights. They are inference/development checkpoints, not long-run resumable optimizer/RNG snapshots.

Exactly the 16 consumed frames are decoded; handles are local to each worker, decoder threads bounded, uint8 pixels transferred with pinned memory and nonblocking CUDA copies, CNN frames microbatched, and pooled features cached. Persistent workers are exhausted and explicitly joined before shutdown. This borrows useful REASSEMBLE loading practices through a small MSM-native dataset; the historical HDF5/action decoding framework is not duplicated. The live benchmark checks actual MSM hashes/PTS, not synthetic loader timing.

For a future evaluator, the reusable composition is `nested_plan` → per-outer `fit_oof_fusion` → `branch_probabilities` → F2/averaging/metrics. It deliberately has no command that launches the full matrix. Reuse the frozen split manifest after review; do not regenerate folds per model or seed. Current `nested_plan` refuses the available cohort.
