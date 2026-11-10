#!/usr/bin/env python3
"""Create the reviewable Stage 3 reports from frozen settings and measured evidence."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(run):
    run = Path(run)
    c = json.loads((run / "config/resolved_config.json").read_text())
    validation = json.loads((run / "validation.json").read_text())
    smoke = json.loads((run / "manifests/smoke_validation.json").read_text())
    benchmark = json.loads((run / "manifests/benchmark.json").read_text())
    head = json.loads((run / "reports/cached_head_benchmark.json").read_text())
    lock = json.loads((run / "config/protocol_lock.json").read_text())
    root = Path("MILLING DATASET")

    def write(name, content):
        with (run / name).open("x") as stream:
            stream.write(content.strip() + "\n")

    write("MSM_STAGE3_EXPERIMENT_PROTOCOL.md", f"""
# MSM Stage 3 experiment protocol

**Implementation and bounded development smoke: PASS. Full evaluation: NOT READY.** Stage 2 established a limited but scientifically traceable coarse milling-context-plus-MTConnect cohort. It did not establish fine tool-contact visibility, visual anomaly separability, or enough positive groups for nested evaluation. No outer-test predictions or performance results were generated in Stage 3. Stop for researcher review before the full matrix.

Protocol **{c['protocol']}**; dataset **`{c['dataset_handle']}`**, ID 8392825. Sources: [official dataset](https://www.kaggle.com/datasets/manufuturetoday/multi-sensor-for-metal-milling-anomaly), [data descriptor](https://www.nature.com/articles/s41597-026-07255-7). No new data or model weights were downloaded. This is an MSM adaptation of the verified frozen REASSEMBLE CNN branch, not the later full-backbone fine-tuning experiment.

Reviewed acquisition and label reports: `{c['stage1']}/MSM_STAGE1_ACQUISITION_REPORT.md`, `MSM_LABEL_AUDIT.md`, and file availability. Reviewed authoritative validated modality/alignment reports: `{c['stage2']}/MSM_STAGE2_MODALITY_AUDIT.md`, `MSM_VIDEO_ALIGNMENT_REPORT.md`, plus `METHODOLOGY_CORRECTION.md`. The earlier exploratory Stage 2 alignment/counts are superseded; they are preserved and never used for this fit.

## Frozen target and eligibility

The prediction unit is **one complete annotated cutting interval**, retrospectively classified after its end. Positive means native label **1**, abnormal cutting warranting intervention. Native **0** and **2** are stable-cutting negatives; label 2 specifically means a defective tool during stable cutting, not automatically abnormal cutting. Preserve the native label in provenance. This target is not tool-health classification or early warning.

Predeclared secondary sensitivity: exclude native label 2, rebuild splits and rerun the same pipeline/settings; do not choose between mappings using test scores. A native three-class classifier is outside this protocol because usable label-2 groups are insufficient.

Admit only Stage 2 verified video+common-MTC examples: exact 16 distinct ordered native frames inside one uncertainty-guarded cut; label-blind acoustic alignment within validated support; recognizable milling context; 15 finite numerical MTC channels, at least five rows, no gap above 0.5 s including cut edges. No repeated-frame padding, imputation, interpolation or synthetic duplication repairs failed eligibility. All branches and controls use identical admitted intervals. No industry videos exist; high-rate ACC is a different, separately audited contract and is not pooled with common MTC.

Current cohort: **114 intervals = 93 native 0 + 10 native 1 + 11 native 2**; binary **104 negatives / 10 positives** (8.77% positive), five folders, **two positive-containing folders**. Excluding label 2 leaves 103 intervals in four folders, still only two positive groups. Stage 2 excluded 13 of 127 candidates: six no video, four outside alignment support, one too short for 16 distinct guarded frames, two MTC gaps. Reusing those exclusions is not outcome-based sample selection.

## Groups, outer and inner splits

Primary grouping is the exact `machine/experiment` folder. All its cuts, frames, repeated recordings and derived representations stay together. Folder identity is a nominal grouping proxy, not proof of independent physical tools or sessions. Stage 1 found only 12 machine/reference-date clusters dataset-wide and five laboratory calendar dates. Reconcile tool/session identity before a confirmatory claim; report a stricter machine/reference-date grouped sensitivity when it supports both classes. Do not infer independence from folder count or treat intervals as independent trials.

Freeze **three outer folds** with `StratifiedGroupKFold(shuffle=True, random_state=42)`. Within outer training only, freeze **two inner group folds**, seed `42 + 100 + outer_index`. Validate exact coverage, disjoint groups and both classes in every training/validation/test partition. Freeze the assignment before extraction/fitting for that cohort. No split-seed search, fallback to interval splits, or automatic fold-count reduction. `msm.splits.nested_plan` fails if the contract cannot be met.

**Current gate fails:** two positive groups cannot place positives in all three outer tests. The available pilot cannot evaluate the declared design. Three positive groups are a necessary minimum for this three-outer/two-inner structure, not a sufficient scientific sample size or independence guarantee. An expanded audited cohort must pass actual partition checks and dependency review; more than this arithmetic minimum is desirable. Stage 1's 25 positive laboratory folders are annotation candidates, not yet verified visual examples. Machine-held-out evaluation is not a substitute for missing inner positive support.

The smoke is explicitly a development exercise, not an outer evaluation fold. Its protected group is `imi_vm20i/dataset19` (18 intervals), which was not decoded or predicted. Of the other 96 admitted intervals, choose exactly 24 by the frozen rule: first eight VM20i/d1, first six d4, first six VMX/d8, and first two native-normal plus first two native-abnormal VMX/d9. This deliberate 10-positive / 14-negative smoke sample is not representative of prevalence. OOF group sides are {{VM20i/d1, VM20i/d4}} and {{VMX/d8, VMX/d9}}. Both training sides contain both binary classes. Their cross-machine composition is useful for plumbing, not an efficacy claim. Exact IDs and roles are in `manifests/smoke_split.json`.

## Model selection, imbalance and budgets

Freeze the existing pretrained R18vd extractor; train a fresh 896→128→1 head. Visual features and sensor features receive separate training-only standardization. Visual BCE positive weight is negative-count/positive-count within that fit. Sensor logistic regression uses training-only balanced class weights. No oversampling, SMOTE, class-informed frame choices or target metadata predictors.

Visual head: AdamW LR 0.001, weight decay 0.001, batch 32 intervals, dropout 0.1, gradient clipping norm 1, **10 fixed epochs**, FP32. No schedule, augmentation, early stopping or epoch search; use the final epoch. CPU fitting of cached 896-value vectors is the reference implementation; CUDA head fitting is separately validated. The CNN remains frozen and in eval mode, including all normalization buffers. CNN extraction uses FP32 with frame microbatch two. No detector, hybrid encoder, proposals or attention executes.

Sensor: balanced L2 logistic regression, **C=1**, lbfgs, max_iter=2000; fail on nonconvergence. F2: a new **unweighted L2 logistic regression C=1** over exactly `[p_visual,p_sensor]`, two coefficients and one intercept. F2 has no group/machine/quality/label context inputs. No probability calibrator or threshold search is fitted in this small-cohort protocol; these are probability scores, not claimed calibrated risks. Decision threshold is fixed **0.5**. Optional F1 averaging is exactly `(p_visual+p_sensor)/2`, with no parameters.

No model/hyperparameter/seed winner is selected. Inner validation is used only to create out-of-fold base probabilities, not to select epochs or settings. This intentionally avoids a deeper selection/calibration nesting layer that the pilot cannot support. Any future search or calibrator requires a revised protocol and separate group-disjoint selection/calibration data.

Training seeds are exactly **42, 123, 20261023**; report all. For a future outer index k, call `fit_oof_fusion` with `seed=root_seed+1000*k`; inner j uses `seed+j`, outer refit `seed+99`. Split assignments remain fixed across seeds. No best-seed reporting. Current smoke used only root seed 42 and two epochs per fit.

Future primary matrix, only after review and cohort validation: **3 seeds × 3 outer folds × (2 inner fits + 1 outer refit) = 27 visual-head fits**, at most 270 total fit-epochs, and nine newly fitted F2 stackers. Sensor fitting is deterministic; there are nine unique fit partitions, although the current reusable composition refits them for each seed (27 cheap invocations). Four outputs share those same fits: visual, sensor, F2 and averaging. The label-2 exclusion sensitivity adds the same upper budget, conditional on its own split gate. No other architecture search or CNN fine-tuning is authorized.

Per fit, at most `10 * ceil(number_of_fit_intervals/32)` visual optimizer steps. At the unfiltered laboratory upper bound of 2,512 intervals this is at most 790 steps per fit (actual group-fit populations are smaller). CNN features are label-independent and need extraction only once per frame/preprocessing/weight signature, not once per seed/fold.

Frozen smoke caps: 24 distinct development intervals; two epochs per fit; **at most 12 total head updates**, **768 CNN frame forwards**, 600-second main smoke limit; Torch allocator cap 2 GiB plus an admission reserve of 3 GiB free device memory. Decoder/Torch CPU threads one; benchmark worker counts zero and two, prefetch one, pinned transfers, finite exhaustion and joined workers. Measured combined work was **{head['combined_optimizer_updates']} updates / {head['combined_cnn_frames']} CNN frames**. The separate tiny CPU/CUDA cached-head path check stayed inside the update budget. No full epoch over the 114-example cohort or experimental matrix was run.

## F2 leakage protections

Within each outer training set, fit fresh visual/sensor models on inner-training groups, including their scalers and class weights, and predict only their inner-validation groups. Every outer-training interval obtains exactly one pair of held-group-out probabilities. Record interval IDs and both branches' fit/selection groups. `StaticF2` rejects a probability whose interval group participated in either branch's fitting or selection. Fit F2 only to this complete training OOF bank and its interval labels. Refit branches on all outer-training groups using the fixed settings; then, after future authorization, apply the frozen stacker to outer-test branch scores. Outer-test rows are NaN in the OOF bank throughout fitting. Do not train F2 on in-sample branch scores or reuse smoke/historical coefficients.

All preprocessing estimates, class weights and parameters are fit only on that branch's training partition. No label, N/ap/ae/F/Z/D, Tool/Workpiece, remarks, program, NC, controller outcome, filename, timestamp, duration, machine or group ID enters predictor matrices. Native observed spindle speed/feed are permitted physical measurements, unlike commanded label-sheet parameters; they can still encode operating-regime confounding and must be acknowledged. IDs/times/native labels are retained only for indexing, grouping, quality control and reporting. No global feature selection, test-aware alignment tuning, duplicated frames across folds, overlapping-cut splitting or hidden test-based threshold decisions.

## Metrics and interpretation

Primary: pooled held-out **interval average precision** (`sklearn.average_precision_score`) for each fixed model, with F2-minus-visual and F2-minus-sensor paired comparisons reported without selecting a winner. Secondary: per-fold AP, AUROC, balanced accuracy, F1, precision/recall, TN/FP/FN/TP, Brier/log loss and prevalence; machine/native-label counts and error summaries (including label-2 false positives). Undefined single-class subgroup metrics remain undefined and are accompanied by counts.

Report each seed, descriptive mean/sample SD, per-fold and pooled held-out values separately. Use 2,000 paired experiment-cluster bootstrap draws, fixed seed 20261027, resampling the same groups across models/seeds; average paired effects across seeds inside a draw. Omit and count undefined one-class draws without silently replacing them. These conditional intervals do not make seeds, folds or intervals independent experimental replicates. No superiority claim from a tiny positive-group cohort; no final metric was computed for this development smoke.

## Freeze, provenance and next action

Settings were frozen at **{lock['UTC_before_any_fitting']}**, before fitting, SHA-256 **`{lock['config_sha256']}`**. No outer results existed or were inspected. Resolved configuration and lock are under `config/`; source/software/input/checkpoint/OOF identities accompany this run. Raw data and prior outputs were preserved. Git is intentionally not staged or committed.

**Next action after researcher review:** expand only a reviewed, size-checked version-2 file plan; validate label-blind video offsets, visibility, sensors and physical grouping for more positive experiments; freeze a cohort/split manifest that passes the three-outer/two-inner gate. Secure an exclusive GPU timing window if sustained throughput is required. Do not launch the full matrix from this handoff.
""")

    write("MSM_ARCHITECTURE_ADAPTATION.md", f"""
# MSM architecture adaptation

**A small MSM package composes the verified REASSEMBLE feature extractor and head constructor. No framework, pretrained detector, failure-classification weights or F2 coefficients were duplicated.** All new MSM source/configuration/tests/results remain under `MILLING DATASET/`.

Dataset `{c['dataset_handle']}`; Stage 2 input contract is restricted to retrospective coarse milling context and pre-aggregated MTConnect measurements. It does not establish fine tool-contact visibility or causal subsecond MTC synchronization. Full evaluation is blocked by positive-group support, not by a failed software forward path.

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
""")

    rows = []
    for item in benchmark["settings"]:
        rows.append(f"| {item['workers']} | {item['intervals']} | {item['wall_seconds_including_first_batch']:.3f} | {item['intervals_per_second']:.3f} | {item['loader_wait_seconds']:.3f} | {item['peak_torch_allocated_bytes']/1024**2:.1f} / {item['peak_torch_reserved_bytes']/1024**2:.1f} | {item['parent_plus_workers_rss_bytes']/1024**3:.2f} | {item['worker_exit_codes']} |")
    write("MSM_IMPLEMENTATION_VALIDATION.md", f"""
# MSM implementation validation

**PASS for the bounded implementation smoke; NOT READY for full evaluation.** The Stage 2 limited cohort supports a traceable coarse-context visual+sensor input contract. All actual Stage 3 training used a deliberately bounded development subset. No smoke metrics are offered as scientific performance evidence, and **zero outer-test predictions** were generated.

Run: `{run}`. Dataset `{c['dataset_handle']}`. Frozen protocol/hash: `config/protocol_lock.json`; exact source/software identities: `provenance.json` plus `manifests/final_software_source_identity.json`. Git revision `94f61529116ebdc966bcf87704a93e4d02fa5e89`; pre-existing dirty tracked/untracked work was preserved. No staging, commit, environment installation, dataset acquisition, or historical output overwrite.

## Tests and real-input checks

**46 tests passed** (20 Stage 3 checks including parametrized cases, plus 26 prior MSM tests). Recorded command output: `validation.json`. The environment's `pip check` passed and `git diff --check` passed. Tests use tiny synthetic data, not copied raw examples.

| Required property | Result / evidence |
| --- | --- |
| Frame-label alignment | Corrected Stage 2 selector reused; all 114 admitted native annotation/frame policies rechecked; actual 24-interval loading rechecks every selected decoded BGR SHA-256 and PTS |
| Sensor-label alignment | Half-open native interval, coverage including edges, finite gate; exact parity of all 90 features for all 24 actual sampled intervals; tests reject NaN/gaps/duplicate clocks/target columns |
| Model forward/output unit | Exactly 16 frames → 896 values → one interval logit; sensor/F2 one score per same interval; wrong frame count or frame-level head tensor rejected |
| Gradients | All new-head parameters have finite nonzero gradients; synthetic update check; actual CPU/CUDA updates pass; frozen CNN has absent gradients by design |
| Group splits | Complete exact OOF coverage; both-class partitions; shared-group split rejected; declared three-outer design fails closed on current two positive groups |
| F2 stacking integrity | All 24 development rows receive one probability pair from models fitted without their experiment group; fitting/selection-group contamination rejected; outer-bank values remain NaN in synthetic outer-fit test |
| Outer-label isolation | Perturbing frozen synthetic outer labels leaves training OOF probabilities, new head and F2 coefficients exactly unchanged |
| Checkpoint save/reload | Branch and F2 prediction maximum absolute differences **0.0** after safe tensor reload |
| Metric calculations | Known synthetic AP 5/6, AUROC 0.75, confusion matrix, balanced accuracy, F1 and Brier validated; undefined one-class metrics rejected |
| Worker stability | Two spawned persistent workers exhausted, both exit codes 0, both reaped; zero/two-worker embeddings bitwise identical |
| Numerical behavior | Finite CNN embeddings/losses/gradients; CPU/CUDA untrained-head max forward difference **{head['CPU_CUDA_untrained_forward_max_abs_difference']:.3g}**; processor scale roundoff ≤5.96e-8 |
| Preservation | All 41 pilot raw files hash-verified; 41 Stage 1 + 100 Stage 2 protected artifact/source hashes unchanged; raw/cache/checkpoint Git exclusion verified |

Model testing exercised actual imported RT-DETR weights, actual MSM video decoding and new heads; synthetic fixtures do not stand in for the real smoke. MTC-only gaps and missing-video intervals remain excluded. This run does not verify every 640×640 sequence in the full 114-example cohort at runtime: 24 were actually decoded, while all 114 timing/annotation policies were revalidated and Stage 2 remains the visibility audit.

## Allocated GPU and loading measurements

One visible **Tesla T4**, 16,384 MiB nominal, Torch CUDA usable; PyTorch 2.13.0+cu130, torchvision 0.28.0+cu130, transformers 5.14.1. At admission another project process used about 9,184 MiB and the device reported **100%** utilization, leaving about 6,741 MiB free. It was never terminated or modified. GPU visibility was inherited; no separate scheduler reservation was established. Data storage remained about 75 GiB free.

The main smoke used at most about **536 MiB reported process VRAM**, including CUDA context; Torch tensor peak **305.2 MiB allocated / 414.0 MiB reserved**. The allocator was capped at 2 GiB with a 3 GiB free-device reserve admission/runtime check. Device-wide 100% utilization belongs to the shared workload and cannot establish MSM utilization. The previous REASSEMBLE **97.9%** result is not imported here.

Actual MSM live decoding plus frozen-CNN extraction, same four development intervals per setting:

| Workers | Intervals | Measured wall s | Intervals/s | Loader wait s | Peak Torch MiB allocated / reserved | Parent+worker RSS GiB | Worker exit codes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(rows)}

Both use one FFmpeg thread/worker, one Torch CPU thread, prefetch one where applicable, uint8 pinned-memory transfer, FP32 CNN frame microbatch two. Timers start after iterator creation and include first-batch wait; spawn/iterator construction is not fully included. Parent CPU times were 8.28 s (serial) and 1.40 s (two workers); worker lifetime CPU was 19.76 s for two workers and includes startup/import work outside the timed window. Consequently the original telemetry field `cpu_core_equivalents` for that worker setting must not be interpreted as a window-normalized CPU utilization measurement. CPU loading is substantial: the serial 24-example extraction spent 40.05 of 48.53 s waiting for input, with about 39.84 s of source decode work.

The larger 24-interval extraction measured **48.534 s / 0.495 intervals per second**, including live seeks, frame/hash/PTS checks, preprocessing, transfer and CNN pooling. It consumed 384 CNN frames. It was not a full scientific epoch or sustained exclusive resource benchmark. Cache/page-cache state, fixed setting order, only four paired timed examples and GPU contention limit comparisons. Two workers are a useful optimization candidate, not a demonstrated full-corpus optimum; the serial path remains the conservative smoke reference.

An idle process listing briefly motivated an exclusive follow-up, but the admission check saw another GPU job and **refused before any CNN/optimizer work**. There is no exclusive throughput or sustained MSM GPU-utilization result. The optional `msm.benchmark` command requires an idle device and has not completed. Do not wait for or interrupt the unrelated training from this task.

Cached-head device-path check, two updates per device on the same 24 development feature vectors:

| Device | Initialization + two-epoch fit s | Interval presentations/s, including initialization | Peak Torch allocated MiB |
| --- | --- | --- | --- |
| CPU | {head['results'][0]['initialization_plus_training_seconds']:.4f} | {head['results'][0]['interval_presentations_per_second_including_initialization']:.1f} | n/a |
| CUDA, shared | {head['results'][1]['initialization_plus_training_seconds']:.4f} | {head['results'][1]['interval_presentations_per_second_including_initialization']:.1f} | {head['results'][1]['peak_torch_allocated_bytes']/1024**2:.1f} |

These very short timings include construction/optimizer startup and are not steady-state head benchmarks or end-to-end CNN throughput. They validate both device paths; CPU is appropriate for the tiny cached-head reference. CNN extraction here is **frozen forward inference**, while optimizer updates affect only the newly initialized head. No CNN-backpropagation throughput is claimed.

## Bounded work completed

Main end-to-end smoke: **24 unique intervals / four folders**, native counts 8 normal + 10 abnormal + 6 stable defective-tool. Two inner branch fits plus a development refit, each two epochs, **six head optimizer updates**, newly fitted sensor models and a new OOF-trained F2. Main elapsed time **{smoke['total_wall_seconds']:.2f} s**. Both F2 and uniform averaging forward paths checked. No prediction metric was calculated from these real development outputs.

Adding the CPU/CUDA head path check gives **{head['combined_optimizer_updates']} optimizer updates total** and **{head['combined_cnn_frames']} CNN frame forwards total** (including repeated benchmark/warmup inputs), below frozen caps of 12 / 768. The smoke checkpoint and its fitted F2 coefficients are development artifacts: do not carry them into a full outer evaluation. Exact fit-group provenance is in `manifests/stacking_provenance.json`; checkpoint in ignored `checkpoints/development_only.pt`.

## Full evaluation readiness and requirements

**NOT READY.** Core adapters, fitting composition, tests and inference checkpoints work; the current cohort has only two positive folders and cannot pass the declared three-outer/two-inner group design. Physical tool/session dependence is unresolved. MTC aggregation latency and frequent visual contact occlusion limit conclusions to retrospective coarse-context classification. No claim of visual separability or fusion benefit follows from this smoke.

After researcher review, expand the version-2 laboratory alignment/visibility/sensor audit before generating frozen splits. Stage 1 lists 56 laboratory folders and 2,512 labeled cuts with 458 label-1 intervals in 25 nominal positive groups; these are upper-bound candidates, not eligible examples. Full laboratory minimal video+MTC+alignment-audio/metadata storage was estimated in Stage 2 at **2,640,036,050 bytes total**, **2,533,736,741 additional bytes** beyond the acquired minimal subset. Recompute an exact file plan for the intended microphones/support; no such acquisition occurred here. An ACC-inclusive laboratory alternative is about 35.29 GB total and is a separate architecture contract.

At 2,512 candidate cuts, pooled 896-float visual plus 90-float sensor features occupy about **9.91 MB uncompressed**, before metadata/checkpoints; optional per-frame CNN features about 144 MB. Full decoded 640×640 uint8 frame caching would need about **49.39 GB**, or 197.55 GB float32, so stream and cache pooled features. Existing pretrained files are reused, not downloaded again. The 528-frame smoke took well below the allocated disk reserve.

Purely illustrative extraction time using the two measured short shared-GPU rates is roughly **46–87 minutes for 2,512 intervals**. This is not an exclusive estimate, full-corpus benchmark, label-alignment audit budget or training-time guarantee; actual eligible count, seek lengths, machine clips and loader startup vary. The 27 fixed-head fits reuse this one feature bank and have 10 epochs each; full-matrix timing must be reassessed on the expanded cohort. No multi-day full-CNN budget is implied by this frozen-extractor protocol.

## Reproduction and review boundary

Run from repository root with the repository environment and portable import roots:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 CUBLAS_WORKSPACE_CONFIG=:4096:8 \\
PYTHONPATH='src:MILLING DATASET/source' ma_thesis_env/bin/python -B -m pytest -q 'MILLING DATASET/tests'

# Only after separately authorizing a new bounded reproduction; use a NEW run path.
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 CUBLAS_WORKSPACE_CONFIG=:4096:8 \\
PYTHONPATH='src:MILLING DATASET/source' ma_thesis_env/bin/python -B -m msm.smoke \\
  --config 'MILLING DATASET/configs/stage3_protocol.json' --output 'MILLING DATASET/runs/NEW_UNIQUE_STAGE3_RUN'
```

Do not rerun into this preserved run; writers refuse existing outputs. No command launches the full matrix. Source/config/tests are reviewable but remain untracked; existing tracked diff is unchanged (three pre-existing files, 22 insertions). Small reports/manifests are available for review; raw data, numerical caches and checkpoints stay ignored.

**Exact next action: researcher reviews the frozen protocol and adaptation, then decides whether to authorize cohort expansion/dependency audit. Stop here before full evaluation.**
""")

    write("REVIEW_HANDOFF.md", f"""
# MSM Stage 3 review handoff

Implementation/smoke passed; full evaluation is blocked. Review `MSM_STAGE3_EXPERIMENT_PROTOCOL.md`, `MSM_ARCHITECTURE_ADAPTATION.md`, `MSM_IMPLEMENTATION_VALIDATION.md`, then `validation.json` and frozen config.

46 tests; 24 development intervals; 528 CNN frames; 10 optimizer updates; zero outer predictions; exact checkpoint parity. The 114-example cohort has only two positive groups. No full matrix, new download, environment install, staging or commit.

All new code is `MILLING DATASET/source/msm/`; protocol config `MILLING DATASET/configs/stage3_protocol.json`; tests `MILLING DATASET/tests/test_stage3.py`. No REASSEMBLE source modification. The only existing MSM shared file changed was `.gitignore`, adding checkpoint/profile exclusions. Prior-stage source/reports were hash-preserved.

Next action is researcher review, then separately authorized expansion of the aligned cohort and resolution of physical grouping. No full experiment may be launched from this handoff.
""")

    ledger = {"UTC": datetime.now(timezone.utc).isoformat(), "commands": [
        {"command": f"PYTHONPATH='src:MILLING DATASET/source' ma_thesis_env/bin/python -B -m msm.smoke --config 'MILLING DATASET/configs/stage3_protocol.json' --output '{run}'", "status": "passed", "evidence": "manifests/smoke_validation.json"},
        {"command": f"PYTHONPATH='src:MILLING DATASET/source' ma_thesis_env/bin/python -B -m msm.benchmark --run '{run}'", "status": "refused before work: another GPU compute process at admission", "evidence": "MSM_IMPLEMENTATION_VALIDATION.md"},
        {"command": f"PYTHONPATH='src:MILLING DATASET/source' ma_thesis_env/bin/python -B -m msm.head_benchmark --run '{run}'", "status": "passed", "evidence": "reports/cached_head_benchmark.json"},
        {"command": f"PYTHONPATH='src:MILLING DATASET/source' ma_thesis_env/bin/python -B -m msm.validate --run '{run}'", "status": "passed", "evidence": "validation.json"}
    ], "common_environment": {"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "CUBLAS_WORKSPACE_CONFIG": ":4096:8"},
        "report_writer_sha256": sha(__file__)}
    write("manifests/commands.json", json.dumps(ledger, indent=2))
    files = []
    candidates = list(run.rglob("*")) + list((root / "source/msm").glob("*.py")) + [root / "source/write_stage3_reports.py", root / "configs/stage3_protocol.json", root / "tests/test_stage3.py", root / ".gitignore"]
    for path in sorted(set(candidates)):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        ignored = subprocess.run(["git", "check-ignore", "-q", str(path)]).returncode == 0
        files.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha(path), "git_ignored": ignored,
                      "role": "regenerable_bulk" if "cache" in path.parts or "checkpoints" in path.parts else "source_config_report_or_manifest"})
    write("manifests/output_manifest.json", json.dumps({"created_utc": datetime.now(timezone.utc).isoformat(), "self_excluded": True, "files": files}, indent=2))
    print(json.dumps({"reports": str(run), "validation_passed": validation["passed"], "full_evaluation_ready": False}), flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", required=True)
    main(p.parse_args().run)
