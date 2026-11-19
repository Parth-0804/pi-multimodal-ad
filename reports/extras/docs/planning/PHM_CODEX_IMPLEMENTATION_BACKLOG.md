# PHM 2026 Baseline Implementation Backlog

## Purpose

This backlog translates the professor's requested next-meeting scope into implementation-ready tasks for the Codex extension in VS Code.

The immediate scientific scope is **PHM North America 2026 only**:

1. Describe the dataset at a basic but defensible structural level.
2. Define, preprocess, train, and evaluate an RT-DETR baseline.
3. Define, preprocess, train, and evaluate a PatchTST baseline.
4. Explain the input, target computation, output, performance, and real-world meaning of both baselines.

Multimodal fusion is explicitly deferred until the two unimodal baselines and the sample/target contract are understood.

The engineering objective is broader: common profiling, manifest, preprocessing, splitting, evaluation, and run-tracking code must be reusable for a future dataset containing images and sensor signals. PHM-specific paths and semantics must remain isolated in a dataset adapter.

## Repository interpretation from the supplied folder tree

### Active PHM raw-data roots

```text
gtc-data-experiment/
├── high_frequency/
│   ├── EXP A/
│   ├── EXP B/
│   └── EXP F/
├── low-frequency (CIs + Oil + Environment)/
├── low-frequency (CIs)/
└── photos/
    ├── EXP-A/
    ├── EXP-B/
    └── EXP-F/
```

### Existing PHM work to preserve and use as evidence

```text
experiments/exp_a_initial_eda_r1_r3_r5/
├── configs/
├── scripts/
└── outputs/
    ├── basic_eda/
    └── advanced_eda/

experiments/exp_b_eda_expA&F/
```

The existing EXP-A work is historical/reproduction evidence. New tasks may read it, compare against it, or reuse validated logic after tests are added, but must not silently overwrite its outputs.

### Explicitly outside active scope

```text
data/Full Dataset/
```

This is the earlier Intel welding dataset. No PHM command may scan, profile, copy, move, rename, or modify it. Generic code may later support a separate adapter for it, but that adapter is not part of the present work.

## Target architecture for reusable code

Codex must inspect the real repository before creating paths. If compatible structures already exist, extend them instead of creating duplicates. The intended separation is:

```text
configs/
├── datasets/phm2026.yaml
└── experiments/
    ├── phm2026_dataset_description.yaml
    ├── phm2026_rtdetr_baseline.yaml
    └── phm2026_patchtst_baseline.yaml

src/
├── data_contracts/       # dataset-neutral schemas and validation
├── datasets/             # BaseDatasetAdapter + PHM2026Adapter
├── profiling/            # generic image/sensor/inventory profilers
├── preprocessing/        # reusable transforms and windowing
├── models/               # RT-DETR and PatchTST experiment code
├── evaluation/           # common metrics, slicing and reports
└── utils/                # configuration, provenance, logging, seeds

scripts/
├── profile_dataset.py
├── build_sample_manifest.py
├── train_rtdetr.py
├── evaluate_rtdetr.py
├── train_patchtst.py
└── evaluate_patchtst.py

tests/
├── fixtures/
├── unit/
└── integration/

experiments/
├── phm2026_dataset_description/outputs/
├── phm2026_rtdetr_baseline/outputs/
└── phm2026_patchtst_baseline/outputs/
```

Generated outputs must follow the repository's existing output and `.gitignore` policies. Raw data and large derived arrays must never be committed.

## Rules embedded in every Codex task

Each prompt below is designed to be pasted independently into a new Codex chat. Every task requires Codex to:

- work from the open repository root;
- read `AGENTS.md` and relevant scope/output/restructuring documentation before changing files;
- inspect existing code and `git status` first;
- preserve unrelated and pre-existing changes;
- treat `gtc-data-experiment/` as read-only raw PHM data;
- exclude `data/Full Dataset/` from every PHM scan;
- use configuration and `pathlib`, never machine-specific absolute paths;
- isolate PHM parsing in `PHM2026Adapter` rather than generic modules;
- support `--config`, `--output-dir`, `--limit`, and `--dry-run` where meaningful;
- stream ZIP/HDF5 content and avoid unnecessary extraction or full-array loading;
- create deterministic, testable outputs with schema version and provenance;
- run focused tests or smoke checks before stopping;
- report files changed, commands run, results, assumptions, and blockers;
- not commit, push, delete, move raw data, or begin a later task unless explicitly requested.

## Dependency order

```text
Epic 0: foundation
        ↓
Epic 1: dataset description
        ↓
Epic 2: target, samples, splits, evaluation contract
        ↓
     ┌──┴─────────────┐
     ↓                ↓
Epic 3: RT-DETR   Epic 4: PatchTST
     └──┬─────────────┘
        ↓
Epic 5: reproducibility, portability, meeting package
```

---

# Epic 0 — Scope-safe, reusable foundation

## F0.1 — Audit the repository and write the PHM implementation map

**Outcome:** An evidence-based map of existing reusable code, historical code, active raw-data paths, and safe destinations for new work.

**Codex prompt:**

```text
Work from the currently open repository root. Before editing, read AGENTS.md and all relevant files under docs/ that define active scope, data boundaries, output policy, restructuring, or reproduction constraints. Inspect git status and the existing configs/, src/, scripts/, tests/, experiments/, and gtc-data-experiment/ structures.

Scope is PHM North America 2026 only. Treat gtc-data-experiment/ as read-only raw input. Explicitly exclude data/Full Dataset/ because it is the historical Intel welding dataset. Preserve experiments/exp_a_initial_eda_r1_r3_r5 and experiments/exp_b_eda_expA&F; do not overwrite their outputs.

Create a PHM implementation map under docs/ that records:
1. Existing PHM-related scripts, configs, outputs, and reusable functions.
2. Active PHM data roots for high-frequency HDF5, low-frequency data, condition indicators, oil/environment data, and photos.
3. Historical or out-of-scope components that new commands must exclude.
4. Proposed locations for shared dataset-neutral code, the PHM adapter, three new experiment directories, tests, and generated outputs.
5. Duplicate or conflicting logic that should be reused, refactored, or left untouched.
6. Concrete blockers and decisions, without resolving them by assumption.

Do not implement profiling or models in this task. Validate every referenced path against the real repository. Report the created/changed file, git diff, and unresolved decisions. Do not commit or push.
```

## F0.2 — Define reusable dataset contracts and the PHM adapter boundary

**Outcome:** A common interface that another image+sensor dataset can implement without changing profiling, training, or evaluation code.

**Codex prompt:**

```text
Work in the open repository and inspect AGENTS.md, scope/data/output policies, git status, and the PHM implementation map before editing. Preserve all unrelated work. Raw data under gtc-data-experiment/ is read-only; data/Full Dataset/ is out of scope and must not be scanned.

Implement a minimal dataset-neutral contract plus a PHM2026Adapter. Reuse compatible existing abstractions if present. The common contract must define typed records or validated schemas for:
- AssetRecord: file/archive identity, modality, experiment, run, size and checksum metadata.
- ImageRecord: width, height, channels, dtype, timestamp, tooth/inspection identity and annotations.
- SensorRecord: HDF5 path, shape, dtype, sampling rate, duration, unit, timestamps and channel role.
- TargetRecord: target name, physical meaning, unit, timestamp, horizon, source and computation version.
- SampleRecord: stable sample_id, input cutoff, sensor window references, image references, target reference and group/split keys.

Separate generic interfaces from PHM-specific rules. The PHM2026Adapter may contain archive naming, EXP-A/B/F normalization, run parsing, HDF5 dataset-path aliases such as /Vibration, /Context, /CI or /CI_4s, photo/timestamp parsing, and six-hour target rules. Generic modules must not contain PHM filenames or HDF5 paths.

Add schema_version fields, deterministic ID generation, validation errors, and small unit tests using synthetic metadata only. Add or update configs/datasets/phm2026.yaml with relative roots and include/exclude rules, but do not assert unverified target semantics.

Run focused tests. Return files changed, the adapter API, test commands/results, assumptions, and blockers. Do not build full manifests, train models, commit, or push.
```

## F0.3 — Add deterministic run metadata and smoke-test infrastructure

**Outcome:** Every later command records how its result was produced and can be tested without scanning the complete dataset.

**Codex prompt:**

```text
Inspect the open repository, its instructions, git status, existing utilities, and the dataset contracts before changing files. Scope is PHM only; never scan data/Full Dataset/ and never modify raw files under gtc-data-experiment/.

Implement reusable experiment infrastructure for profiling and model scripts:
1. YAML configuration loading with clear validation and relative-path resolution from the repository root.
2. Reproducible random seed handling for Python, NumPy, and PyTorch when available.
3. A run manifest that records schema version, UTC timestamp, git commit and dirty-state flag, command, config path and hash, Python/package versions, seed, input roots, output root, and produced artifacts.
4. --dry-run and --limit support for data commands.
5. A tiny synthetic multimodal fixture containing a few images, short sensor arrays, timestamps, groups, and scalar targets. Do not copy proprietary/raw PHM data into tests.
6. Unit tests proving deterministic IDs, split reproducibility, and config validation.

Integrate with existing utilities rather than duplicating them. Do not implement dataset profiling or model training. Run the focused test suite and report changed files, commands, results, and any dependency changes. Do not commit or push.
```

---

# Epic 1 — Basic PHM dataset description

## D1.1 — Build the complete PHM asset and archive inventory

**Outcome:** Exact counts and storage structure for the in-scope PHM dataset.

**Codex prompt:**

```text
Work from the open repository root. Read project instructions and scope/output policies, inspect git status, and reuse the dataset contracts and PHM2026Adapter. Treat gtc-data-experiment/ as read-only and exclude data/Full Dataset/ from all scans. Do not overwrite historical experiment outputs.

Implement a configuration-driven PHM asset profiler that inventories:
- high_frequency/EXP A, EXP B, and EXP F;
- low-frequency (CIs + Oil + Environment);
- low-frequency (CIs);
- photos/EXP-A, EXP-B, and EXP-F.

For files and archives, report relative path, normalized experiment/run, modality, file type, compressed/uncompressed size where available, nested member count, naming pattern, and lightweight checksum/duplicate evidence. Detect unreadable archives, empty files, unexpected extensions, missing expected experiment/run combinations, and exact duplicate members. Stream archive metadata; do not extract entire archives.

Create a generic CLI such as scripts/profile_dataset.py with a PHM config, --dry-run, --limit, and explicit output directory. Write versioned machine-readable inventory output (Parquet when supported plus CSV/JSON summary) and a concise Markdown summary under a new PHM dataset-description experiment directory. Include totals by experiment, run, and modality.

Add focused tests using the synthetic fixture and run a limited PHM smoke scan before any full scan. Do not profile signal values or image pixels yet. Report changed files, exact commands, output paths, smoke results, and blockers. Do not commit or push.
```

## D1.2 — Profile HDF5 and sensor structure

**Outcome:** A defensible description of every sensor channel and array shape.

**Codex prompt:**

```text
Inspect project instructions, git status, existing EDA code, dataset contracts, the PHM adapter, and the completed asset inventory. Scope is PHM only. Raw gtc-data-experiment/ content is read-only, data/Full Dataset/ is excluded, and historical EDA outputs must not be overwritten.

Implement a reusable sensor/HDF5 structural profiler. Dataset-neutral logic must traverse HDF5 groups and produce SensorRecord-compatible rows; PHM-specific path aliases and experiment/run parsing must stay in PHM2026Adapter.

For each accessible HDF5 dataset, capture:
- archive/member and relative source identity;
- normalized experiment and run;
- full internal HDF5 path;
- modality/role: vibration, operating context, condition indicator, oil, environment, timestamp, or unknown;
- array rank and exact shape;
- dtype, byte order, chunks, compression, HDF5 attributes and units;
- sample count, channel count, sampling rate, estimated duration, and timestamp coverage when evidence exists;
- lightweight chunked statistics: min, max, mean, standard deviation, NaN/Inf count, empty and constant flags;
- variability of shapes and sampling rates across files.

Do not load complete high-frequency signals into memory. Support metadata-only and sampled-statistics modes. Record unknown units/frequencies as unknown rather than guessing.

Produce a versioned sensor_profile table, HDF5 schema JSON, and professor-facing Markdown summary with shapes written explicitly, e.g. [n_samples] or [n_samples, n_channels]. Add fixture tests and run a limited PHM smoke test. Report files, commands, results, resource behavior, assumptions, and blockers. Do not commit or push.
```

## D1.3 — Profile the gear-tooth image structure and quality

**Outcome:** Exact image counts, shapes, formats, grouping, and usable annotation evidence.

**Codex prompt:**

```text
Inspect repository instructions, git status, existing photo caches/EDA logic, dataset contracts, the PHM adapter, and asset inventory. Work only on PHM. Never scan data/Full Dataset/, never modify gtc-data-experiment/, and do not overwrite experiments/exp_a_initial_eda_r1_r3_r5.

Implement a reusable image profiler whose common logic works for ordinary files and images stored inside archives. Keep PHM experiment/run/tooth/inspection/timestamp parsing in PHM2026Adapter.

For every readable PHM image, report:
- source archive/member or relative path;
- experiment, run, inspection/stage, tooth identifier, sequence, and parsed timestamp when available;
- width, height, channels, array layout, color mode, bit depth, dtype, file format, file size, and aspect ratio;
- intensity min/max/mean/std and optional lightweight blur, darkness, saturation, and perceptual-hash measures;
- presence and format of image-level labels, bounding boxes, masks, keypoints, or no annotations;
- exact and likely near duplicates;
- unreadable/corrupt images and unusual shape/mode outliers.

Generate versioned image_profile output, resolution/mode distributions, annotation-availability summary, and a deterministic contact sheet of representative samples and anomalies. Never modify or resize source images; transformed previews belong only in the new output directory.

Add tests with synthetic RGB/grayscale/corrupt samples and perform a limited PHM smoke scan before full execution. Report files, commands, output paths, results, assumptions, and blockers. Do not commit or push.
```

## D1.4 — Audit cross-modal timelines and candidate sample alignment

**Outcome:** Evidence showing whether sensors, photos, and six-hour observations can form model samples.

**Codex prompt:**

```text
Read project instructions and inspect git status, completed asset/sensor/image profiles, existing PHM EDA outputs, and the PHM adapter. Scope is PHM only; all raw sources are read-only and Intel data is excluded.

Implement a reusable alignment-audit pipeline. Build canonical event tables for sensor recordings, photos/inspections, operating context, condition indicators, and candidate targets. PHM-specific timestamp parsing and lifecycle labels belong in PHM2026Adapter.

For each experiment and run, report:
- earliest/latest timestamp and event cadence by modality;
- counts and coverage gaps;
- candidate joins between images, sensor recordings, and scalar observations;
- nearest-neighbor time delta and one-to-one/one-to-many/many-to-one cardinality;
- cases with missing modalities or ambiguous matches;
- whether six-hour spacing is observed in the actual records;
- at least five traceable raw-source-to-candidate-sample examples.

Compare candidate sample units: one image, one tooth inspection, all images from an inspection, one sensor recording, and one historical sensor window ending at an inspection/target time. Do not choose a final sample or interpolate values yet.

Write alignment_audit and sample_definition_options outputs with stable IDs and source provenance. Add synthetic tests for exact, nearest, ambiguous, and missing alignment. Report files, commands, findings, uncertainties, and blockers. Do not commit or push.
```

## D1.5 — Generate the basic professor-facing dataset description

**Outcome:** A short, factual answer to “What is the dataset and what are its shapes?”

**Codex prompt:**

```text
Inspect project instructions, git status, and the completed PHM asset, sensor, image, and alignment outputs. Do not rescan raw data unless a validation check is necessary. Do not use the historical Intel data.

Create a reproducible report generator that builds a professor-facing PHM dataset description from machine-readable profiling outputs. Every numerical claim must be computed from those outputs and cite its source artifact.

Include:
1. In-scope experiments and runs.
2. File/archive counts and storage by modality.
3. Image counts, H x W x C shapes, formats, color modes, bit depth, inspection/tooth grouping, annotation availability, and quality limitations.
4. Sensor channels, internal HDF5 paths, tensor shapes, sampling frequencies, durations, units, and shape variability.
5. Low-frequency CI/oil/environment structure.
6. Timeline coverage and observed six-hour cadence evidence.
7. One end-to-end candidate sample example.
8. Missingness, duplicates, inconsistencies, and unresolved target questions.

Produce Markdown plus CSV tables and slide-friendly PNG/SVG figures under the new dataset-description experiment output. Keep the report descriptive; do not claim model suitability or degradation causality. Add a test that the report regenerates from fixture profiles and that required sections exist. Report outputs and validation results. Do not commit or push.
```

---

# Epic 2 — Target, sample, split, and evaluation contract

## Organizer-authoritative correction (2026-08-14)

The original T2 prompts below remain as historical traceability, but their missing-organizer-scalar assumption is superseded by the official PHM North America 2026 challenge description. Participants measure spall size or severity for 28 post-run tooth images, define a scalar run aggregate, and later learn sensor-to-damage mapping; the organizer separately retains an undisclosed evaluation trajectory.

T2.1 now derives a versioned per-tooth image measurement, raw top-3 run mean and causal monotonic candidate. Masks stay provisional until human review. Six hours is typical run/inspection/output cadence, with shorter exceptions, not automatically a forecast horizon. Verified experiment/run/tooth identity is the association key. T2.2 uses strict EXP-B train, EXP-A validation and untouched EXP-F test partitions with no run/inspection/tooth/near-duplicate crossing. T2.3 fits baselines/scaling on training only and evaluates tooth/run trajectories. Current evidence is in `T2_TARGET_FORMULATION_DECISION.md` and the T2 checkpoints; historical prompts below must not override it.

## T2.1 — Audit and specify the six-hour scalar target

**Outcome:** One precise target definition—or a documented blocker if the evidence is insufficient.

**Codex prompt:**

```text
Work in the open repository. Read project instructions, official/local PHM documentation available in the repository, profiling outputs, alignment audit, and existing EDA code. Inspect git status first. Scope is PHM only; raw data is read-only and data/Full Dataset/ is excluded.

Audit every candidate scalar target. For each candidate, document exact source file/member/HDF5 path, physical meaning, unit, timestamp, observed cadence, direct measurement versus derived formula, missingness, distribution, and whether it would exist at real inference time.

Resolve explicitly:
- Is “six hours” the spacing between target observations, the sensor input-window length, or the forecast horizon?
- Is the task current-state estimation y_t, future forecasting y_(t+6h), or another horizon?
- Is the target one scalar, a vector of condition indicators, damage extent, or RUL?
- How is one target associated with one image or image set and one sensor history?

Implement target computation only after evidence supports it. Put dataset-specific formula/path logic in PHM2026Adapter and assign a target_definition_version. Preserve raw and transformed target values and include leakage checks. Do not silently interpolate, bin, average, or select a convenient condition indicator.

Produce target_audit, target_definition.md, and tested target-construction code. If evidence is insufficient, stop with ranked options and exact questions for the professor rather than inventing a target. Report changed files, tests, decision, and blockers. Do not commit or push.
```

## T2.2 — Freeze the model sample manifest and leakage-safe splits

**Outcome:** Both models train against compatible, traceable observations without cross-run leakage.

**Codex prompt:**

```text
Inspect repository instructions, git status, dataset contracts, alignment outputs, and the approved target definition. Do not proceed if the target remains unresolved; report the gate instead. Scope is PHM only and raw data is read-only.

Implement a configuration-driven canonical sample-manifest builder. Each row must contain a stable sample_id, experiment, run, lifecycle/inspection group, input cutoff timestamp, sensor window start/end and source references, image/image-set references, target timestamp/value/unit, forecast horizon, availability flags, grouping keys, and exclusion reason.

Define leakage-safe split strategies appropriate to the available PHM data:
1. chronological within-run evaluation where defensible;
2. group/run holdout;
3. leave-one-run-out or leave-one-experiment-out when sample counts permit.

Never randomly split neighboring sensor windows or images from the same inspection across train and validation/test. Fit normalization only on training partitions. Persist split assignments and a split manifest; never recompute them implicitly during model training.

Add validations for modality/target timestamps, overlapping windows across splits, duplicate assets, missing targets, class/target coverage, and minimum group sizes. Add fixture tests and build a limited PHM manifest before a full one. Report files, counts, exclusion reasons, split evidence, tests, and blockers. Do not train models, commit, or push.
```

## T2.3 — Define shared metrics, naive baselines, and real-world validity criteria

**Outcome:** RT-DETR-derived regression and PatchTST are judged with the same regression contract where applicable.

**Codex prompt:**

```text
Inspect project instructions, git status, approved target definition, sample manifest, and split manifest. Reuse existing evaluation code where valid.

Implement a reusable evaluation specification for the PHM scalar-regression task. Include MAE, RMSE, R2 only when statistically valid, median absolute error, bias, normalized error with an explicitly documented denominator, prediction intervals or bootstrap confidence intervals where feasible, and per-run/experiment/lifecycle/operating-condition slices.

Implement simple comparison baselines:
- training-set mean or median;
- persistence/last-observation when the target history is available at inference;
- a small linear/tree feature baseline only if its input information matches the deep model's cutoff time.

Define real-world validation questions: physical unit of error, useful lead time, inference-data availability, stability, false-alarm implications, robustness across speed/torque/temperature, unseen-run generalization, and computational cost. Define success relative to naive baselines, not an arbitrary R2 threshold.

Support a common prediction-result schema so both models emit sample_id, y_true, y_pred, split, target unit, timestamps, group fields, model/config/run IDs, and latency. Add tests using synthetic predictions. Do not train deep models. Report files, tests, formulas, and unresolved acceptance thresholds. Do not commit or push.
```

---

# Epic 3 — RT-DETR image baseline

## Organizer-corrected RT-DETR rule (2026-08-14)

Use standard detection only with verified spall boxes/classes. With scalar tooth targets but no boxes, use image → RT-DETR backbone/hybrid encoder → multi-scale aggregation → scalar head and call it an RT-DETR-derived image-regression baseline. Never repeat one run scalar across 28 teeth. Provisional pseudo-targets permit only a visibly provisional engineering baseline. Training is one deterministic bounded run, at most 30 epochs, patience about 5, no test tuning/sweep, best/last checkpoints only, with frozen/precomputed encoder first. See `R3_RTDETR_CHECKPOINT.md`.

## R4 pseudo-box/detection extension completed (2026-08-14)

A later explicitly authorized R4 extension derived traceable provisional boxes from the already versioned `phm2026_image_damage_v2` masks; it did not create or claim organizer/manual ground truth. The canonical pseudo-box run is `20260814T040854991567Z-3fa0f794` (995 images, 30,628 boxes, all images positive under the heuristic). Human review remains pending; see `R4_PSEUDO_BOX_CHECKPOINT.md`.

Two bounded image-only models used the unchanged EXP-B train / EXP-A validation / EXP-F test split. The genuine detector run `20260814T043751107678Z-7f1e13af` had effectively failed pseudo-box agreement. The genuine multitask detection-plus-scalar run `20260814T050026535618Z-9b00f099` was mechanically complete, with weak detection and mixed scalar results across aggregation levels. See the R4 checkpoints and final package `20260814T051127631836Z-18a96ee3`. These results remain pseudo-label agreement, not physical-damage validation. PatchTST, sensor processing, fusion, leaderboard work, and official test modelling were not started.


## R3.1 — Select a scientifically valid RT-DETR formulation

**Outcome:** A documented decision between detection, encoder-based scalar regression, or a blocked experiment.

**Codex prompt:**

```text
Inspect repository instructions, git status, image profile, annotation audit, target definition, sample/split manifests, and existing RT-DETR experiments. Scope is the PHM image modality only for this baseline; do not add sensor input or multimodal fusion.

Evaluate three formulations against actual PHM evidence:
A. Standard RT-DETR object detection, requiring boxes and classes.
B. RT-DETR backbone/hybrid-encoder feature extraction with a scalar regression head.
C. Image-level regression using a simpler vision backbone as a sanity baseline, while RT-DETR adaptation remains the architecture-learning experiment.

For each, state input, required annotations, target, model output tensor, loss, pretrained components, metrics, and scientific limitations. Standard RT-DETR output is boxes/classes/confidences, not automatically the six-hour scalar target. Do not call an encoder-regression adaptation an unchanged RT-DETR detector.

Create an architecture decision record and a tensor-flow table from raw image H x W x C through preprocessing, batch tensor B x 3 x H x W, backbone/encoder features, pooling/query aggregation, and final output. Select a formulation only if supported by the data; otherwise document the exact blocker.

Do not implement training in this task. Report the decision, evidence, changed file, and professor questions. Do not commit or push.
```

## R3.2 — Implement RT-DETR preprocessing and the image dataset loader

**Outcome:** Reproducible image tensors and correctly aligned scalar/detection targets.

**Codex prompt:**

```text
Read project instructions, inspect git status, and load the approved RT-DETR architecture decision, sample manifest, split manifest, and PHM adapter. Stop if the formulation or target is unresolved. Raw PHM files are read-only; Intel data is excluded.

Implement reusable image preprocessing plus a PHM image dataset loader for the approved formulation. Specify and code image/image-set selection, color conversion, orientation, aspect-ratio-preserving resize/padding or justified alternative, normalization matching pretrained weights, train-only safe augmentation, target association, and batch collation. If boxes are used, transform and validate them correctly.

Keep generic transforms dataset-neutral and PHM parsing in PHM2026Adapter. The loader must use persisted split/sample manifests and return tensors, target, sample_id, timestamps, experiment/run, and source metadata. It must never create random splits internally.

Add assertions and documented shape tracing after every stage. Create deterministic visual QA showing original and transformed samples with target metadata. Test grayscale/RGB, corrupt images, missing targets, different resolutions, multiple images per inspection, and split isolation with synthetic fixtures. Run a small PHM loader smoke test only.

Report changed files, returned batch schema, tensor shapes, QA output, tests, and blockers. Do not train the model, commit, or push.
```

## R3.3 — Implement the RT-DETR-derived regression/detection baseline

**Outcome:** A model whose output exactly matches the approved target contract.

**Codex prompt:**

```text
Inspect project instructions, git status, approved RT-DETR decision, preprocessing loader, target contract, metrics, and existing model utilities. Scope is the PHM image-only baseline; do not introduce sensor features.

Implement the approved RT-DETR formulation. Prefer a well-maintained library implementation and document model/version/pretrained weights. If scalar regression is approved, expose the RT-DETR backbone/hybrid encoder, define deterministic feature aggregation across scales/images, and add a regression head that outputs B x 1 (or the approved output shape). If detection is approved, preserve standard decoder/query outputs and detection losses.

Document frozen versus trainable layers, loss function, target scaling/inverse scaling, parameter counts, expected input/output tensors, and how multiple tooth images are aggregated if applicable. Add a forward-pass smoke test and tests for output shape, finite loss, gradient flow in trainable layers, checkpoint save/load, and inverse target transform.

Do not run full training. Report files, architecture, tensor shapes, tests, pretrained dependency details, and blockers. Do not commit or push.
```

## R3.4 — Train a reproducible RT-DETR baseline

**Outcome:** A small but complete, traceable PHM image experiment.

**Codex prompt:**

```text
Inspect project instructions and git status. Verify that the RT-DETR loader/model tests, target contract, persisted splits, and naive baselines are complete. Scope is PHM image-only. Do not alter raw data or historical EDA outputs.

Implement a configuration-driven RT-DETR training entry point with fixed seeds, persisted run manifest, training-only normalization/augmentation, checkpointing, early stopping, learning-rate history, train/validation losses, resume support, and CPU/GPU device reporting. Use a small smoke configuration first, then only run the approved baseline budget.

Prevent leakage by consuming the existing split manifest exactly. Save the resolved config, preprocessing state, target scaler, best checkpoint, last checkpoint, epoch history, and environment/provenance metadata under a new RT-DETR experiment output directory. Never store raw images in outputs.

Compare training behavior with the defined naive or simpler image baseline where feasible. Do not tune on the test split. Run smoke tests and report commands, runtime, hardware, sample counts, best validation result, outputs, warnings, and blockers. Do not commit or push.
```

## R3.5 — Evaluate RT-DETR performance and real-world validity

**Outcome:** Quantitative results, failure cases, and an honest answer about usefulness.

**Codex prompt:**

```text
Inspect project instructions, git status, the completed RT-DETR run manifest/checkpoint, target/evaluation contract, and persisted test split. Do not retrain or change the split in this task.

Implement/evaluate the RT-DETR baseline with the appropriate contract. For scalar regression, emit the common prediction schema and compute MAE, RMSE, median absolute error, bias, R2 when valid, confidence intervals, and performance slices by experiment, run, lifecycle stage, tooth/inspection grouping, and available operating conditions. For detection, report mAP/precision/recall and separately explain whether/how detections relate to the scalar health target.

Compare with naive and simple image baselines. Produce predicted-vs-actual plots, residual plots, worst/best cases, representative image failure cases, inference latency, parameter count, and resource use. Test whether errors or uncertainty change under blur, exposure, unusual resolutions, or unseen runs without fabricating perturbation claims.

Write a real-world validity section covering physical meaning, required image acquisition, timing/lead time, actionability, generalization, and limitations. Distinguish statistical fit from maintenance usefulness.

Save metrics, predictions, figures, and Markdown report under the RT-DETR experiment output. Report exact checkpoint/config, commands, metrics, outputs, and blockers. Do not commit or push.
```

---

# Epic 4 — PatchTST sensor baseline

## P4.1–P4.5 initial baseline completed (2026-08-14)

The explicitly authorized initial sensor-only baseline is complete. Bounded LF extraction run `20260814T121146792755Z-4016432b` produced 7,124 traceable minute rows, 7,119 timestamp-verified sequence inputs, and 20 independent experiment/run samples. Canonical model run `20260814T121641338050Z-433d4154` used EXP-B train, EXP-A validation, and EXP-F test without random splitting. Professor package `20260814T122147349749Z-44877f9f` reports a retained negative result: raw-target EXP-F PatchTST MAE 1.011 pp (N=8), worse than training mean/median at 0.680 pp. Target version `phm2026_image_damage_v2` remains provisional. See `P4_PATCHTST_BASELINE_CHECKPOINT.md`.

The prompts below remain the historical task specifications. Do not rerun or tune the initial baseline against EXP-F. Any complex PatchTST follow-up requires a separate authorization, expert target review, and pre-registered EXP-B/EXP-A-only choices.


## P4.1 — Select the PatchTST regression/forecasting formulation — COMPLETE

**Outcome:** A precise definition of sensor input, temporal horizon, and scalar output.

**Codex prompt:**

```text
Inspect repository instructions, git status, sensor profile, alignment audit, target definition, sample/split manifests, and any earlier PatchTST experiments. Scope is PHM sensor-only for this baseline; do not use image features or multimodal fusion.

Compare at least these formulations against actual data cadence and inference availability:
A. Current-state regression: sensor history ending at t predicts y_t.
B. Six-hour-ahead forecasting: sensor history ending at t predicts y_(t+6h).
C. Multi-step forecasting: sensor history predicts a future target sequence.

For each, specify selected raw/derived channels, input history duration, resampling/aggregation, cutoff time, target timestamp, forecast horizon, expected input B x C x L, patch length/stride, number of patches, output shape, loss, and leakage risks. Explain whether high-frequency raw vibration can be used directly within compute limits or requires physically meaningful window features/downsampling.

Write an architecture decision record plus a tensor-flow table from HDF5 signals through synchronization, windowing, normalization, patching, Transformer encoder, and regression/forecast head. Choose the simplest scientifically valid baseline supported by evidence. Do not implement training. Report decision, evidence, changed file, and unresolved questions. Do not commit or push.
```

## P4.2 — Implement sensor preprocessing and window construction — COMPLETE

**Outcome:** Leakage-safe PatchTST inputs that preserve relevant temporal information.

**Codex prompt:**

```text
Read project instructions and inspect git status, approved PatchTST decision, sensor profile, PHM adapter, target definition, and sample/split manifests. Stop if the formulation is unresolved. Raw PHM files are read-only and Intel data is excluded.

Implement reusable sensor preprocessing for the selected PatchTST formulation:
- channel selection and canonical ordering;
- timestamp synchronization;
- resampling/downsampling or feature aggregation with documented anti-aliasing/physics rationale;
- missing/irregular timestamp handling;
- window length, stride, cutoff and horizon enforcement;
- training-only fitted normalization with persisted parameters;
- PatchTST patch length/stride validation;
- masks when missing values are supported.

Keep HDF5 paths and PHM channel aliases in PHM2026Adapter. The generic windowing code must operate on canonical time/value arrays. Preserve raw source references and never use data after the input cutoff. Avoid materializing huge raw-signal tables; use streaming/chunked processing and cache only policy-approved derived data.

Create deterministic plots comparing representative raw, resampled, normalized, and patched windows. Add synthetic tests for irregular timestamps, missing channels, NaN/Inf, insufficient history, boundary/horizon leakage, variable sample rates, and deterministic windows. Run a limited PHM smoke build. Report files, shapes, memory/runtime behavior, tests, and blockers. Do not train, commit, or push.
```

## P4.3 — Implement the PatchTST dataset loader and model output contract — COMPLETE

**Outcome:** A tested B x C x L input and approved regression/forecasting output.

**Codex prompt:**

```text
Inspect project instructions, git status, PatchTST architecture decision, preprocessing/window code, persisted sample/split manifests, target scaler, and evaluation contract. Scope is PHM sensor-only.

Implement the PatchTST dataset loader and baseline model using a documented implementation/version. The loader must consume persisted sample and split assignments and return input tensor B x C x L, target tensor in the approved shape, masks when needed, sample_id, input/target timestamps, experiment/run, and source metadata.

Configure and document patch_len, stride, padding, number of patches, embedding dimension, channel-independence behavior, Transformer depth/heads, pooling/flattening, and final regression/forecast head. Add shape tracing from B x C x L to patched/embedded tensors and final output. Preserve target inverse transformation into the physical unit.

Add tests for loader determinism, split isolation, output shape, finite forward loss, gradient flow, checkpoint save/load, mask behavior, and inverse target transform. Run only a small forward-pass smoke test on PHM samples.

Report files, batch/model tensor shapes, parameter count, tests, dependency details, and blockers. Do not run full training, commit, or push.
```

## P4.4 — Train a reproducible PatchTST baseline — COMPLETE

**Outcome:** A traceable PHM sensor experiment with comparison against persistence.

**Codex prompt:**

```text
Inspect project instructions and git status. Verify the PatchTST loader/model tests, approved target/horizon, persisted splits, normalization state, and naive baselines. Scope is PHM sensor-only; raw data remains read-only.

Implement a configuration-driven PatchTST training entry point with deterministic seeds, run manifest, checkpointing, early stopping, train/validation histories, resume support, device reporting, and bounded data caching. Consume the saved split manifest exactly; do not create random windows or splits inside the trainer.

Run a very small smoke configuration first. Then run only the approved baseline budget. Save resolved config, channel list/order, resampling/window/patch parameters, normalization state, target scaler, best/last checkpoints, history, and provenance under a new PatchTST experiment output directory.

During validation, compare against mean/median and persistence baselines using the same samples and cutoff information. Never tune on the test split.

Report commands, runtime, hardware, sample/window counts, best validation result, output files, warnings, and blockers. Do not commit or push.
```

## P4.5 — Evaluate overall PatchTST performance and real-world validity — COMPLETE

**Outcome:** The professor can see actual model performance and whether it translates into a plausible maintenance use case.

**Codex prompt:**

```text
Inspect project instructions, git status, the completed PatchTST run/checkpoint, target/evaluation contract, and persisted test split. Do not retrain or alter preprocessing/splits in this task.

Generate predictions in the common result schema. Compute MAE, RMSE, median absolute error, bias, R2 when valid, confidence intervals, and error slices by experiment, run, lifecycle stage, operating regime, target range, and forecast horizon. Compare directly with mean/median, persistence, and approved simple feature baselines.

Produce actual-vs-predicted timelines, scatter/residual plots, error over lifecycle, largest failure windows, stability analysis, inference latency, model size, and resource use. Evaluate unseen-run/experiment generalization only for splits that were frozen before training. Do not over-interpret EXP-A Run-1/3/5 distribution shifts as ground-truth degradation without target evidence.

Write a real-world validity assessment covering required sensor history, acquisition/sampling burden, six-hour lead time or cadence, physical-unit error, actionability, robustness to operating conditions/missing channels, false-alarm implications, and deployment limitations. Distinguish forecasting skill from merely reconstructing a contemporaneous condition indicator.

Save metrics, predictions, plots, and Markdown report under the PatchTST output directory. Report exact config/checkpoint, commands, metrics, outputs, conclusions, and blockers. Do not commit or push.
```

---

# Epic 5 — Reproducibility, portability, and professor package

## C5.1 — Prove the pipeline is reproducible

**Outcome:** A second run from saved configuration reproduces manifests, splits, and metrics within declared tolerances.

**Codex prompt:**

```text
Inspect repository instructions, git status, completed PHM profiling/manifest code, RT-DETR and PatchTST run artifacts, and existing reproducibility policies. Do not modify raw data or retrain unless the reproduction protocol explicitly requires it.

Create and execute a bounded reproduction check:
1. Rebuild dataset profiles/manifests from the same config and compare schema, row counts, stable IDs, checksums, and split assignments.
2. Reload both saved checkpoints and regenerate predictions for a fixed evaluation subset.
3. Compare predictions and metrics with stored artifacts using explicitly documented deterministic or numerical tolerances.
4. Verify all artifacts reference config hash, code revision/dirty state, seed, data roots, schema version, preprocessing state, and target definition version.
5. Provide one command per stage plus an optional orchestration command; no notebook-only step may be required.

Produce a reproducibility report listing exact matches, tolerated differences, failures, environment limitations, and recovery commands. Add automated regression tests where runtime is reasonable. Report changed files, commands, results, and blockers. Do not commit or push.
```

## C5.2 — Prove reusable components work beyond PHM-specific parsing

**Outcome:** Reuse is demonstrated, not merely claimed.

**Codex prompt:**

```text
Inspect project instructions, git status, BaseDatasetAdapter, PHM2026Adapter, synthetic fixture, profiling, preprocessing, manifest, and evaluation modules. The scientific scope remains PHM; do not import or scan data/Full Dataset/ and do not build a real second-dataset model.

Demonstrate portability using a second synthetic adapter/fixture with deliberately different directory names, image resolutions/modes, sensor channel names, sampling rate, and target column naming. Do not add second-dataset semantics to generic code.

Prove that, without changing generic profiler/manifest/evaluation modules, the second adapter can:
- enumerate image and sensor assets;
- emit contract-valid ImageRecord, SensorRecord, TargetRecord, and SampleRecord rows;
- run image and sensor profiling;
- construct leakage-safe splits/windows;
- emit a batch compatible with a generic image-regression and time-series interface;
- evaluate synthetic predictions through the common result schema.

Add contract/integration tests. Document the minimum adapter methods and configuration a future image+sensor dataset must supply, as well as which choices cannot be generic because they depend on physical meaning.

Produce a portability report. Report changed files, tests, proof results, and limitations. Do not train a second real model, touch Intel data, commit, or push.
```

## C5.3 — Generate the next-meeting evidence package

**Outcome:** A concise package answering the professor's three requested inputs.

**Codex prompt:**

```text
Inspect project instructions, git status, and all completed machine-readable reports/results for PHM dataset description, target definition, RT-DETR, PatchTST, reproducibility, and portability. Do not recompute or invent missing results; mark incomplete evidence explicitly.

Generate a professor-facing next-meeting package with three main sections:

1. PHM dataset description
- experiments/runs/modalities in scope;
- image and sensor shapes, counts, sampling/cadence, grouping and quality;
- observed alignment and one model-sample example;
- exact scalar target and six-hour interpretation, or the unresolved decision.

2. RT-DETR baseline
- preprocessing from raw image to tensor;
- architecture/tensor flow;
- how the target is computed;
- exact output and physical unit;
- performance versus baseline;
- real-world validation and limitations.

3. PatchTST baseline
- preprocessing from HDF5 signals to B x C x L and patches;
- architecture/tensor flow;
- target/horizon and output;
- overall performance versus persistence;
- real-world validation and limitations.

Add a final slide/page on reproducibility and portability: config-driven runs, immutable manifests/splits, adapter boundary, provenance, and synthetic second-adapter proof. Add a compact table of decisions/questions requiring professor confirmation. Every number must link back to a generated result artifact/config/checkpoint.

Produce a concise Markdown report plus slide-ready tables/figures, not a final thesis chapter. Report created files, source artifacts, missing evidence, and validation checks. Do not commit or push.
```

---

# Definition of done

## Next-meeting definition of done

The meeting package is complete only when the following can be answered with generated evidence rather than assumptions:

### Dataset

- Which PHM experiments/runs/modalities are actually present?
- How many assets and usable records exist?
- What are the image shapes, modes, bit depths, formats, grouping, and annotation types?
- What are the sensor/HDF5 paths, array shapes, channels, dtypes, sampling frequencies, durations, and units?
- How do images, sensor histories, operating context, and scalar observations align?
- What exactly does the six-hour statement mean?

### RT-DETR

- Is it detection or an RT-DETR-derived image-regression architecture?
- What raw image(s) form one sample?
- What preprocessing produces the input tensor?
- How is the target computed without leakage?
- What is the exact model output and unit?
- How does it perform against a simple baseline and on unseen groups?
- Is the output actionable and available at the required time?

### PatchTST

- Which sensor channels and history enter one sample?
- What synchronization, resampling, windowing, normalization, and patching are used?
- Is it current-state regression or future forecasting?
- What is the exact output shape, horizon, and unit?
- What is its overall and per-run performance versus persistence?
- Does it generalize and provide useful lead time in a plausible real setting?

## Reproducibility definition of done

- No machine-specific absolute paths exist in code/configs.
- Raw PHM and Intel data are never modified or committed.
- Every stage is runnable by CLI from the repository root.
- Config, schema, target definition, preprocessing state, split assignments, seeds, environment, code revision, and artifact inventory are saved.
- Stable manifests/splits regenerate identically, or differences are explained.
- Model predictions regenerate from checkpoints within declared tolerances.
- Tests cover adapters, schemas, transforms, leakage, shapes, checkpoint loading, and metrics.
- Historical EXP-A outputs remain reproducible and unmodified.

## Reusability definition of done

- Generic modules contain no PHM archive names, experiment labels, HDF5 paths, or target formulas.
- PHM-specific knowledge exists only in `PHM2026Adapter` and PHM configuration.
- A second synthetic adapter with different naming, image, sensor, and target structure passes the same profiling/manifest/evaluation contract tests without modifying generic code.
- A future real dataset can be supported by implementing the documented adapter methods and configuration.
- Dataset-specific scientific choices—target meaning, temporal horizon, safe augmentations, resampling, grouping, and validity criteria—remain explicit rather than hidden behind “automatic” defaults.

## Explicit non-goals for this backlog

- Multimodal fusion of RT-DETR and PatchTST.
- Leaderboard/test submission.
- Final thesis architecture selection.
- Large hyperparameter searches.
- Treating FM4/NA4/M6A/ALR trends as ground-truth degradation without verification.
- Creating bounding boxes or damage labels by assumption.
- Refactoring or archiving the historical Intel dataset as a side effect.

## Recommended execution slices

To control Codex usage and professor-meeting risk, execute tasks in these slices:

1. **Meeting-critical foundation:** F0.1–F0.3, D1.1–D1.5, T2.1–T2.3.
2. **RT-DETR baseline:** R3.1–R3.5.
3. **PatchTST baseline:** P4.1–P4.5.
4. **Closure:** C5.1–C5.3.

Do not begin a later slice if the target/sample gate is unresolved.
