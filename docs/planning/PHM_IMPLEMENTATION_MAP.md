# PHM 2026 implementation map

F0.1 status: **COMPLETE — REPOSITORY AUDIT ONLY**

Evidence date: `2026-08-13`

Scientific scope: PHM North America 2026, EXP-A Runs 1–5, EXP-B Runs 1–7,
and EXP-F Runs 1–8.

## 1. Executive finding

The repository does not yet contain the reusable PHM implementation described
by the backlog. It contains:

- complete high-frequency run coverage by filename for the approved EXP-A,
  EXP-B, and EXP-F scope;
- experiment-level low-frequency, condition-indicator, and photo archives;
- one protected historical EXP-A EDA study for HF Runs 1, 3, and 5;
- a historical EXP-B acquisition script and an incomplete local inspection
  helper;
- Intel welding loaders, manifests, configuration, documentation, and a
  placeholder notebook that are outside active PHM work.

There is no current PHM configuration, installable package, dataset adapter,
data contract, profiler, sample manifest, split implementation, RT-DETR
baseline, PatchTST baseline, test suite, or reproducible run infrastructure.
The historical EXP-A code is useful as behavioral evidence, but it is
monolithic, hard-coded to obsolete paths, narrower than the active scope, and
must remain untouched until selected behavior is covered by regression tests.

The safe implementation direction is a namespaced package under
`src/pi_multimodal_ad/`, with dataset-neutral components separated from a
PHM-specific adapter. No proposed implementation path was created in F0.1.

## 2. Audit boundary and evidence quality

### 2.1 Sources inspected

The map is based on the actual working tree and source text from:

- `AGENTS.md`;
- `docs/active_scope.md`, `docs/data_boundaries.md`, and
  `docs/output_policy.md`;
- `docs/planning/PHM_CODEX_IMPLEMENTATION_BACKLOG.md` in full;
- root configuration, requirements, Python, notebook, and documentation files;
- `configs/`, `src/`, `experiments/`, and the presence or absence of
  `scripts/` and `tests/`;
- path names, file counts, and file sizes below `gtc-data-experiment/`;
- function definitions and output writes in the two protected historical EDA
  scripts;
- Git tracking, ignore, and worktree metadata.

### 2.2 Safety boundary used for this audit

- `gtc-data-experiment/` was treated as immutable. Only path names and
  filesystem metadata were inspected; no ZIP, HDF5, or image payload was
  opened, extracted, or hashed.
- `data/Full Dataset/` was excluded. Only the existence of the boundary
  directory was checked; its contents were not scanned.
- `synology_cookies.txt` and all credential/session contents were not read.
- Protected historical output payloads were not regenerated or modified.
  Counts, sizes, names, source generators, and Git state were inspected.
- No repository Python, notebook, EDA, downloader, profiling, or model command
  was executed.

Consequently, raw-data statements in this map are filename-level evidence, not
archive-integrity, internal-schema, annotation, timestamp, or scientific-target
validation. Historical HDF5 paths and feature behavior are evidence from the
historical source, not proof that every current A/B/F member has the same
schema.

## 3. Current repository map

| Path | Observed state | Current role | PHM treatment |
|---|---|---|---|
| `gtc-data-experiment/` | Exists; ignored; 52 ZIPs plus one local Python helper | Immutable PHM raw root and dataset-adjacent helper | Read-only input; never use as a source-code destination |
| `experiments/exp_a_initial_eda_r1_r3_r5/` | Exists; 279 files in the complete tree | Protected historical EXP-A study | Leave untouched; use as evidence and regression oracle only |
| `experiments/exp_b_eda_expA&F/` | Exists but is completely empty and untracked | Ambiguous historical placeholder | Preserve the directory; do not treat it as an implementation or write new work into it |
| `download.py` | Exists and is tracked | Historical EXP-B HF acquisition script | Leave untouched; not a current safe pipeline entry point |
| `experiments/LARGE_DATASET_ACQUISITION_BEST_PRACTICES.md` | Exists and is tracked | Acquisition/integrity lessons | Keep as supporting guidance |
| `configs/dataset_paths.yaml` | Exists and is tracked | Intel welding paths only | Exclude from PHM commands; not a PHM registry |
| `src/` | Exists with three Intel-oriented modules | Historical Intel manifest/loading utilities | Do not reuse as PHM parsing; generic ideas require new contracts/tests |
| `scripts/` | Absent | Intended thin CLI entry points | Proposed, not implemented |
| `tests/` | Absent | Intended unit/integration/synthetic fixtures | Proposed, not implemented |
| `notebooks/01_data_exploration.ipynb` | Exists; placeholder pandas version check only | Old generic exploration stub | Out of active PHM implementation |
| `requirements.txt` | Exists; broad, unpinned stack | Environment declaration | Supporting only; no lock/package metadata and no direct `torch`/`torchvision` declaration |
| `README.md` | Exists; Intel welding is presented as the main dataset | Historical project overview | Outdated for active PHM scope; do not use as PHM configuration |
| `docs/dataset_instructions.md`, `docs/dataset_overview.md` | Exist; Intel-oriented | Historical dataset guidance | Exclude from PHM scanning logic |
| `data/Full Dataset/` | Boundary exists; ignored | Historical Intel raw dataset | Explicitly outside PHM scope; never scan from a PHM command |
| `docs/restructuring/`, `docs/repository_audit/` | Directories exist but are empty in the audited worktree | Referenced by some instructions/earlier workflow | Missing evidence that must not be invented |

The audit began on branch `main`, aligned with `origin/main`. The worktree
already contained a tracked `.gitignore` modification and untracked governance,
planning, archive, and tree documents. These pre-existing changes are not part
of F0.1 and must be preserved.

## 4. Active PHM data roots

The approved raw scope is present by directory and filename. Sizes below are
compressed file sizes from filesystem metadata.

| Modality | Validated raw root | Archives | Filename-level coverage | Size |
|---|---|---:|---|---:|
| High-frequency HDF5 | `gtc-data-experiment/high_frequency/EXP A/` | 5 | EXP-A Runs 1–5 | 95.279 GiB |
| High-frequency HDF5 | `gtc-data-experiment/high_frequency/EXP B/` | 7 | EXP-B Runs 1–7 | 122.895 GiB |
| High-frequency HDF5 | `gtc-data-experiment/high_frequency/EXP F/` | 8 | EXP-F Runs 1–8 | 136.334 GiB |
| Low-frequency, CIs, oil, environment | `gtc-data-experiment/low-frequency (CIs + Oil + Environment)/` | 3 | One aggregate LF ZIP each for EXP-A/B/F | 0.107 GiB |
| Condition indicators | `gtc-data-experiment/low-frequency (CIs)/` | 3 | One aggregate CI ZIP each for EXP-A/B/F | 0.079 GiB |
| Gear-tooth photos | `gtc-data-experiment/photos/EXP-A/` | 7 | Test start, break-in, Runs 1–5 | 0.196 GiB |
| Gear-tooth photos | `gtc-data-experiment/photos/EXP-B/` | 9 | Test start, break-in, Runs 1–7 | 0.264 GiB |
| Gear-tooth photos | `gtc-data-experiment/photos/EXP-F/` | 10 | Pre-run, break-in, Runs 1–8 | 0.129 GiB |
| **Total** | `gtc-data-experiment/` | **52** | A/B/F modalities above | **355.283 GiB** |

There is exactly one HF ZIP by filename for every approved experiment/run.
This does not establish archive readability or completeness. In particular,
EXP-B Run 7 (7,992,390,098 bytes) and EXP-F Run 7 (3,942,910,165 bytes) are
materially smaller than most neighboring HF archives (approximately 19–21
billion bytes). They are integrity-review candidates, not confirmed corrupt
files. No `.part`, symlink, or zero-byte file was observed under the PHM root.

### 4.1 Naming variants owned by the future PHM adapter

Raw paths must not be renamed to normalize these variants:

| Concept | Observed variants |
|---|---|
| Experiment directory | HF uses `EXP A`; photos use `EXP-A` |
| Filename prefix | `Exp-A`, `Exp-B`, `Exp-F` |
| Run token | `Run-1` for A/F photos; `Run 1` for B photos |
| Break-in | `Break-In` and `Break In` |
| Initial photo stage | `0 Hours - Test Start` for A/B; `Pre-Run` for F |
| LF/CI run identity | Aggregate experiment ZIP names contain no run number; internal mapping is unverified in F0.1 |

`pre-run`, `test start`, and `break-in` must remain distinct source labels until
their semantics are established. Experiment/run normalization must preserve the
original archive and member identity.

### 4.2 EXP-A Run-2 warning

The organizer-reported 311-file overlap between EXP-A Runs 1 and 2 remains
unverified. Run 2 is in scope. A future adapter/configuration must attach the
warning and use a configurable, reported, non-destructive policy. Raw files
must never be deleted or rewritten.

## 5. Existing PHM implementation and evidence

### 5.1 Acquisition support

`download.py` is an EXP-B-only Synology downloader, not a reusable acquisition
module. Relevant logic includes:

- `DownloadItem` and remote naming at lines 146–172;
- ZIP-signature validation at lines 207–227;
- URL construction at lines 234–266;
- session creation at lines 273–355;
- one-byte probe and size validation beginning at line 361;
- resumable `.part` download logic beginning at line 622;
- EXP-B discovery at lines 1063–1227.

It must be left untouched because it hard-codes this workstation at lines
72–85, writes into the immutable raw root, targets the old flat raw layout,
reads session content, and deletes/replaces cookie, invalid archive, and partial
files as part of its workflow. All approved EXP-B HF run filenames are already
present in the nested current layout. Reusable concepts (probe before download,
resume, exact size, signature, provenance) belong in a later separately
designed acquisition boundary, not in an imported copy of this script.

### 5.2 Dataset-adjacent inspection helper

`gtc-data-experiment/inspect_dataset.py` is ignored, untracked source located
inside the immutable raw root. Its top-level code immediately opens two
hard-coded EXP-A LF/CI archives (lines 5–49). Its
`inspect_nested_archive()` function (lines 51–158) references helpers/imports
that it does not define, including `natural_key`, `parse_run`, `io`,
`tempfile`, HDF member discovery, temporary extraction, and HDF inspection.
It is not a usable entry point. It duplicates historical advanced-EDA logic
and must remain untouched in the raw tree; later code should replace its useful
intent outside the data root.

### 5.3 Protected historical EXP-A study

`experiments/exp_a_initial_eda_r1_r3_r5/` is
`HISTORICAL_OUTPUT_PROTECT_UNTIL_REPRODUCED`.

| Component | Observed role |
|---|---|
| `EXPERIMENT_NOTES.md` | Historical question, R1/R3/R5 rationale, methods, results, limitations, and future directions |
| `basic_eda_phm2026.py` | Beginner descriptive monolith; representative Run-1 HF plus LF/photo overview |
| `eda_phm2026.py` | Advanced EXP-A monolith; inspect, LF/CI, photos, HF features, and plots modes |
| `configs/dataset_paths_snapshot.yaml` | Exact copy of the Intel-only root config, not a PHM config and not consumed by either EDA script |
| `scripts/` | Empty |
| `outputs/basic_eda/` | 19 files: 5 CSV, 11 PNG, 2 JPG, 1 TXT; 0.959 MiB |
| `outputs/advanced_eda/` | 256 files: 17 CSV, 29 PNG, 203 JPG, 7 JSON; 350.541 MiB |

The complete historical tree has 279 files. Git tracks 257; the 22 generated
CSV outputs are ignored. No historical worktree diff was present during the
audit.

#### Basic EDA stages and outputs

| Function | Historical responsibility | Preserved outputs |
|---|---|---|
| `dataset_inventory()` (169–209) | Selected archive inventory | `01_dataset_inventory.csv` |
| `inspect_representative_hdf5()` (216–234) | First-HDF tree for Run 1 | `02_hdf5_structure.csv` |
| `vibration_eda()` (260–351) | Raw axial/radial time and spectrum summaries | `03_*`, `04_*`, vibration-statistics CSV |
| `context_eda()` (358–404) | Speed, torque, temperature summaries | Three context plots and summary CSV |
| `ci_eda()` (411–460) | FM4, NA4, M6A, ALR summaries | Four CI plots and summary CSV |
| `inspect_low_frequency()` (467–507) | Direct-HDF search in LF/CI outer ZIPs | Intended `07_*` CSVs are not present |
| `photo_contact_sheet()` (514–611) | Test-start and Run-5 contact sheets | Two JPG sheets |
| `write_readme()` (618–703) | Basic interpretation guide | `README_BASIC_EDA.txt` |

#### Advanced EDA stages and outputs

The CLI at lines 2874–2969 exposes `inspect`, `lf`, `photos`, `hf`, `plots`,
and `all`.

| Stage | Historical functions | Preserved output classes |
|---|---|---|
| Inventory/schema | `zip_inventory()` (278–306), HDF inspection (336–424), nested inspection (427–492), `run_inspection()` (495–552) | Three inventory/schema JSON reports |
| HF features | sampling and streaming functions (559–823), `analyze_hf_h5()` (843–928), processors (931–1072) | R1/R3/R5 and combined feature CSVs |
| LF/CI ingestion | numeric extraction and flattening (1079–1321), keyword mapping/canonicalization (1324–1451) | Flattened/canonical CSVs and mapping JSONs |
| Photos | stage/tooth parsing (1458–1503), quality/contact-sheet helpers (1506–1660), `process_photos()` (1662–1809) | Cache JPGs, seven contact sheets, photo inventory and damage-score template |
| Distribution analysis | lifecycle shifts/ranking (1859–2009), context and sensor summaries (2012–2124) | Shift and summary CSVs, boxplots |
| Trajectory/PCA/context | plotting (2190–2260), PCA (2263–2477), Huber context residuals (2480–2582) | Trajectory/PCA plots, PCA tables/JSON, residual table/model JSON |
| LF visualization | `plot_low_frequency()` (2585–2672) | Observed RPM, torque, and temperature figures |
| Cross-modal placeholder | `create_cross_modal_template()` (2674–2751) | Run-level template with empty image-damage values |

This study is historical evidence only. Its HF scope is EXP-A Runs 1, 3, and
5; active PHM scope is all approved A/B/F runs. Lifecycle words in the study
must not be converted into health/damage labels.

## 6. Reusable behavior candidates

Nothing below should be imported directly from the monolith. Extract behavior
only after synthetic or deterministic regression tests establish what must be
preserved.

| Behavior candidate | Historical source | Proposed ownership | Required caution |
|---|---|---|---|
| Natural ordering and run parsing | advanced lines 207–216 | PHM adapter for raw naming; generic natural sort may live in `utils` | Preserve original text and detect ambiguous/missing run IDs |
| ZIP HDF/image member enumeration | advanced 238–264 | Dataset-neutral archive reader/profiler | Stream metadata; retain archive/member identity |
| Bounded ZIP/HDF inventory | advanced 278–424 | Generic profiling plus PHM path aliases | Do not assume a first member represents every schema |
| Nested LF/CI traversal | advanced 427–492 and 1170–1321 | Generic archive reader driven by PHM adapter | Existing code loads whole inner ZIPs into memory |
| Deterministic bounded HDF sampling | advanced 309–329 | Generic sensor profiler | Sampling policy and approximation must be recorded |
| Sampling-rate lookup | advanced 559–590 | Generic reader with PHM-configured fallback | Historical silent 102,400 Hz fallback requires validation/warning |
| Blockwise exact basic statistics | advanced 593–646 | Generic sensor features/profiling | Preserve dtype/numerical behavior in tests |
| Shape and spectral features | advanced 649–823 | Feature modules, not adapter | 28-tooth GMF and channel meanings are PHM-specific/configured |
| Fixed HDF aliases | advanced 158–171 | `PHM2026Adapter` only | `/CI` and `/CI_4s` variability must be explicit |
| LF array flattening/canonicalization | advanced 1079–1451 | Later generic time-series contract plus PHM aliases | Historical dropping/alignment behavior is not safe as a default |
| Photo stage/tooth parsing | advanced 1458–1503 | `PHM2026Adapter` only | Preserve raw stage labels and multiple views per tooth |
| Image quality primitives | advanced 1506–1565 | Generic image profiler | Add mode/dtype/error contracts and tests |
| Effect-size, summary, and plotting helpers | advanced 1816 onward | Generic analysis/visualization | Historical fixed comparisons are not generic defaults |
| Downloader probe/resume concepts | `download.py` | Optional later acquisition package | Current script conflicts with immutable-data policy and current layout |

The basic script duplicates HDF-tree, first-member, temporary extraction,
channel lookup, and signal-sampling behavior already represented in the
advanced script. It should not become a second canonical implementation.

## 7. Duplicate, conflicting, or unsafe logic

| Finding | Evidence and impact | F0.1 disposition |
|---|---|---|
| Historical HF paths are stale | Both EDA scripts expect `gtc-data-experiment/Exp-A_HDF5_Run-*.zip`; actual HF paths are nested under `high_frequency/EXP A/` | Leave history untouched; configuration/adapter must resolve current paths later |
| Historical output paths do not match preserved locations | Scripts write fixed root `basic_eda_outputs/` and `eda_outputs/`; preserved files are under the experiment tree | Do not rerun; use unique versioned outputs later |
| Narrow and fixed scope | Advanced HF is fixed to A Runs 1/3/5; no B/F or duplicate-policy support | Treat as historical only |
| Import side effect | Basic script creates its output directory at module import (line 51) | Never import as a library |
| Duplicate HDF/archive/photo helpers | Basic, advanced, and local inspector overlap | Select behavior once; extract into tested modules rather than copying files |
| Incomplete inspector | `gtc-data-experiment/inspect_dataset.py` has missing names/imports and top-level execution | Leave in raw root; do not consume |
| Whole nested ZIPs loaded in memory | Advanced lines 1218–1224 use `outer_zip.read()` | Future reader must be bounded/streaming |
| LF arrays lose alignment information | `arrays_to_dataframe()` selects the maximum array length, broadcasts scalars, and drops other lengths; `sample_index` resets for each HDF | Do not adopt as a generic sample contract; preserve only for historical regression |
| CI canonicalization conflict | Slash-to-`__` column names contain underscores, while `\bFM4\b`-style regexes treat `_` as a word character | Document defect; any correction must be separately reviewed/tested |
| Photo cache collisions | Cache filename uses stage plus tooth only and skips existing files; multiple source views can resolve to one cache path | Future image identity must include archive/member/view and avoid persistent extraction by default |
| Progress is not verified time | HF `progress_in_run` is normalized archive-member ordinal; LF sorting interleaves reset sample indices | Never use as a timestamp or target alignment without evidence |
| Cross-modal output is not alignment | Historical template aggregates by run and leaves damage values empty | Do not use as a sample manifest |
| Silent physical assumptions | Historical defaults include 102,400 Hz and 28 gear teeth | Put in validated PHM config with warnings/provenance |
| Fixed output names and incomplete provenance | No resolved config, input/output manifest, Git/software record, or collision-safe run ID | Implement later run infrastructure; never overwrite history |
| Downloader conflicts with immutable boundary | It deletes/replaces files and uses the old flat output root | Preserve as acquisition evidence; do not run in active pipeline |
| Two Intel manifest generators overlap | `src/generate_manifest.py` and `src/create_intel_manifest.py` scan Intel with incompatible schemas/defaults | Keep outside PHM; resolve Intel direction separately |
| Root/historical YAML duplication | Both Intel YAML files are byte-identical | Preserve snapshot for history; neither is a PHM config |

## 8. Current workflow reconstruction

| Pipeline stage | Current implementation | Status for active A/B/F PHM scope |
|---|---|---|
| Acquisition | `download.py` for EXP-B HF only | Historical/unsafe for current layout; all approved HF filenames already present |
| Integrity and asset inventory | Historical advanced inspection; incomplete local helper | Partial, A-only, path-stale; no current all-scope integrity manifest |
| HDF/schema inspection | Historical first-member and nested inspection | Partial historical evidence; no systematic A/B/F schema validation |
| LF/CI preprocessing | Historical EXP-A flatten/canonicalize code | Historical and scientifically/temporally unsafe as a generic contract |
| Photo preprocessing | Historical EXP-A extraction/cache/quality code | Historical, collision-prone, no timestamp/annotation contract |
| HF feature extraction | Historical EXP-A R1/R3/R5 streaming/sampled feature code | Valuable regression evidence; not active all-scope code |
| EDA/statistics | Historical shift, trajectory, PCA, context analyses | Descriptive history only; fixed comparisons and no split contract |
| Visualization | Historical basic/advanced plots and contact sheets | Preserved evidence; not reproducibly connected to current config |
| Cross-modal alignment | Run-level empty damage template | Not implemented at sample/timestamp level |
| Target definition | None | Blocked; six-hour meaning, source, unit, and horizon unresolved |
| Sample manifest and splits | None | Not implemented |
| RT-DETR | None | Not implemented; annotation/formulation unresolved |
| PatchTST | None | Not implemented; target/window/horizon unresolved |
| Evaluation/provenance | None beyond historical descriptive outputs | Not implemented as a reusable contract |

## 9. Proposed implementation destinations

These are destinations, not F0.1-created paths. Paths marked proposed were
confirmed absent during the audit.

```text
configs/
├── datasets/
│   └── phm2026.yaml
└── experiments/
    ├── phm2026_dataset_description.yaml
    ├── phm2026_rtdetr_baseline.yaml
    └── phm2026_patchtst_baseline.yaml

src/pi_multimodal_ad/
├── data_contracts/
├── datasets/
│   ├── base.py
│   └── phm2026.py
├── profiling/
├── preprocessing/
├── models/
├── evaluation/
├── visualization/
├── acquisition/              # only if separately approved
├── utils/
└── cli.py

scripts/
├── profile_dataset.py
├── build_sample_manifest.py
├── train_rtdetr.py
├── evaluate_rtdetr.py
├── train_patchtst.py
└── evaluate_patchtst.py

tests/
├── fixtures/                 # tiny synthetic data only
├── unit/
└── integration/

experiments/
├── phm2026_dataset_description/
├── phm2026_rtdetr_baseline/
└── phm2026_patchtst_baseline/
```

### 9.1 Ownership boundary

Dataset-neutral code may define records, archive/HDF/image interfaces,
profiling, transformations, splits, metrics, run metadata, and model
interfaces. It must not contain PHM filenames, experiment labels, raw HDF5
paths, gear semantics, stage parsing, or target formulas.

`PHM2026Adapter` should own:

- A/B/F experiment and run normalization;
- current raw root structure and archive patterns;
- original archive/member/source identity;
- `/Vibration`, `/Context`, `/CI`, and `/CI_4s` aliases after validation;
- photo experiment/stage/run/tooth/view parsing;
- the 28-tooth assumption if confirmed and configured;
- the EXP-A Run-2 warning and selected non-destructive duplicate policy;
- target construction only after the target is evidenced and versioned.

Thin scripts should only parse CLI arguments and call package APIs. Historical
monoliths must not be runtime dependencies of the new package.

### 9.2 Generated-output destination conflict

The current output policy and `.gitignore` make `/runs/` the safe default for
bulk, versioned execution output:

```text
runs/<study>/<unique-run-id>/
├── config/resolved_config.yaml
├── manifests/inputs.json
├── manifests/outputs.json
├── reports/warnings.json
├── reports/summary.md
├── tables/
├── figures/
├── logs/
└── provenance.json
```

Compact reviewed artifacts may later be promoted to `data/manifests/` or the
allow-listed `results/{final_tables,final_figures,reports,provenance}/`
locations.

The backlog diagram instead places generated files under
`experiments/phm2026_*/outputs/`. Current ignore policy does not uniformly
ignore arbitrary nested experiment outputs; for example a JSON file there
would be visible while a CSV may be globally ignored. Before a later task
writes output, the researcher must choose one of these approaches:

1. keep tracked experiment definitions under `experiments/` and place all bulk
   runs under ignored `/runs/` (current safest option); or
2. approve a tracking-policy change and define collision-safe nested
   `experiments/.../outputs/<run-id>/` behavior.

F0.1 does not resolve or implement that policy decision.

## 10. Proposed-path validation

| Proposed path | Audit state |
|---|---|
| `configs/datasets/` | Absent |
| `configs/experiments/` | Absent |
| `src/pi_multimodal_ad/` | Absent |
| `scripts/` | Absent |
| `tests/` and `tests/fixtures/` | Absent |
| `experiments/phm2026_dataset_description/` | Absent |
| `experiments/phm2026_rtdetr_baseline/` | Absent |
| `experiments/phm2026_patchtst_baseline/` | Absent |
| `/runs/` | Absent and ignored by policy |
| `/results/` | Absent; only approved curated subdirectories are allow-listed |
| `data/manifests/` | Absent and allow-listed for compact artifacts |

There is an architecture discrepancy to resolve before F0.2: the backlog's
illustrative tree uses flat `src/data_contracts/`, `src/datasets/`, and related
directories, whereas `AGENTS.md` requires an installable
`src/pi_multimodal_ad/` package. This map proposes the namespaced package as
the authoritative direction, but the researcher should explicitly confirm it.

## 11. Concrete blockers and decisions

These are gates; F0.1 does not resolve them by assumption.

1. **Package layout:** confirm `src/pi_multimodal_ad/...` rather than flat
   `src/...` subpackages before F0.2.
2. **Generated-output root:** choose ignored `/runs/` versus a later approved
   nested experiment-output policy.
3. **Scalar target:** identify exact source/member/HDF path or formula,
   physical meaning, unit, timestamp, and availability at inference.
4. **Six-hour statement:** determine whether it describes observation cadence,
   input history, or forecast horizon.
5. **Image formulation:** establish annotation availability before choosing
   standard RT-DETR detection versus an encoder-based regression adaptation.
6. **Cross-modal time:** establish timestamps/cadence and join cardinality for
   sensor records, LF/CI observations, photos, and targets.
7. **Raw integrity:** perform a later bounded validation across all A/B/F
   archives, including the unusually small B/F Run-7 HF files.
8. **LF/CI topology:** verify internal run/member mapping and schemas for each
   aggregate experiment ZIP without assuming EXP-A history generalizes.
9. **Photo-stage semantics:** decide how pre-run, test-start, and break-in
   relate while retaining their original labels.
10. **EXP-A Run-2 policy:** configure and report include/report/confirmed-
    duplicate treatment; never mutate raw data.
11. **Historical behavior versus correction:** decide which feature,
    sampling-rate fallback, LF flattening, CI mapping, and photo identity
    behaviors must first be reproduced and which corrections get separate
    reviewed tests.
12. **Acquisition boundary:** decide whether acquisition belongs in the active
    package; the existing downloader is not safe to reuse as-is.
13. **Dependency reproducibility:** choose package metadata, versions/lockfile,
    and explicit PyTorch/vision/time-series dependencies before model work.
14. **Empty historical placeholder:** clarify the intended research value and
    naming of `experiments/exp_b_eda_expA&F/`; do not repurpose it silently.
15. **Missing governance artifacts:** `AGENTS.md` references restructuring
    tasks, but `docs/restructuring/` and `docs/repository_audit/` are empty in
    the current worktree. Confirm whether those documents should exist before
    relying on their earlier decisions.
16. **Historical provenance:** no current command/config explains how root
    EDA outputs were moved into the protected experiment or which outputs are
    final thesis evidence.

## 12. F0.1 boundary

F0.1 creates this map only. It does not create configuration, package, script,
test, experiment, manifest, result, fixture, or run-output directories. It does
not implement the F0.2 contracts or `PHM2026Adapter`, profile the dataset,
define a target, train a model, or alter historical/raw material.

The next backlog item remains F0.2 and requires a separate explicit request
after the decisions above are reviewed.
