# Dataset EDA notebooks

Start here for a meeting. **EDA** means exploratory data analysis: opening and
understanding observations before making modelling claims. Each notebook follows
one identified sample, explains unfamiliar terms, and connects the observations
to this repository's code. No training or evaluation is run.

| Dataset | Reusable source | Open for the meeting (offline HTML) | Executed notebook |
|---|---|---|---|
| REASSEMBLE | [01_reassemble_eda.ipynb](01_reassemble_eda.ipynb) | [REASSEMBLE walkthrough](../../runs/reassemble/20261016T105418770811Z-dataset-eda/01_reassemble_eda.html) | [Executed REASSEMBLE](../../runs/reassemble/20261016T105418770811Z-dataset-eda/01_reassemble_eda.executed.ipynb) |
| PHM 2026 | [02_phm_eda.ipynb](02_phm_eda.ipynb) | [PHM walkthrough](../../runs/phm2026/20261016T105310968729Z-dataset-eda/02_phm_eda.html) | [Executed PHM](../../runs/phm2026/20261016T105310968729Z-dataset-eda/02_phm_eda.executed.ipynb) |
| Intel Welding | [03_intel_welding_eda.ipynb](03_intel_welding_eda.ipynb) | [Intel walkthrough](../../runs/intel_welding/20261016T105310968587Z-dataset-eda/03_intel_welding_eda.html) | [Executed Intel](../../runs/intel_welding/20261016T105310968587Z-dataset-eda/03_intel_welding_eda.executed.ipynb) |

`tutorials/reassemble/` was renamed to `tutorials/EDA/` at the researcher's request.
Historical executed notebooks and reports remain in their original run folders.
The missing REASSEMBLE helper was restored as `reassemble_support.py` and checked
by fresh-kernel execution, including exact saved-feature comparisons.

## What each notebook shows

- **REASSEMBLE:** successful and failed insert actions; annotations, retained
  camera frames, timestamp-based clips, sensor traces, actual preprocessing
  shapes, and the preserved Section 1 saved-feature boundary.
- **PHM:** EXP-B Run 1, member `Run-1/Dyno Gear303Run1_00000.hdf5`; one real
  saved feature row, its extraction-log identity, run context, and a same-run
  retained inspection overlay. The configured `gtc-data-experiment` raw root is
  absent, so this is explicitly a **saved-evidence walkthrough**. No raw
  waveform is fabricated. The overlay is heuristic, not ground-truth damage,
  and same-run membership does not establish exact sensor/photo alignment.
- **Intel Welding:** development sample
  `10_crater_cracks_7_03-20-23_Fe410/04-03-23-0010-11`; actual video frames,
  CSV sensor observations, and a five-second audio excerpt. CATEGORY is the
  intended weld condition, not a verified physical defect. Cross-modal alignment
  remains unvalidated. No proposed final-test sample is inspected.

## Rerun or choose another sample

From the repository root, using the existing environment:

```bash
ma_thesis_env/bin/python -B tutorials/EDA/run_eda.py 01_reassemble_eda.ipynb
ma_thesis_env/bin/python -B tutorials/EDA/run_eda.py 02_phm_eda.ipynb
ma_thesis_env/bin/python -B tutorials/EDA/run_eda.py 03_intel_welding_eda.ipynb
```

Each command starts a fresh kernel and creates a unique
`runs/<domain>/<UTC-timestamp>-dataset-eda/` directory with an executed notebook,
embedded offline HTML, figures, input/output manifests and provenance. Source
notebooks remain free of outputs. Runtime caches stay inside the new run.
Never stage, commit or publish the raw-derived outputs; each new run ignores all
of its contents. No packages, data or weights are downloaded.

Edit the first parameter cell before rerunning:

- REASSEMBLE: `ACTION` or `MANUAL` composite recording/segment IDs.
- PHM: `EXPERIMENT`, `RUN_NUMBER`, or `MEMBER_NAME`. This notebook reads the
  pinned saved feature bank; raw-data availability does not trigger a rebuild.
- Intel: `SAMPLE_SUBDIR` must be an eligible local development sample;
  `AUDIO_SECONDS` controls the short excerpt. Keep it small.

Raw paths come from dataset configurations; overrides are
`REASSEMBLE_DATA_ROOT`, `PHM_DATA_ROOT`, and `INTEL_WELDING_DATA_ROOT`.
`--data-root` on the runner is a REASSEMBLE-only convenience.

HTML media are embedded without remote JavaScript or CDN dependencies. Static
figures remain available if a browser cannot play the embedded media. Decoding
and embedded assets are checked, but browser playback has not been manually
verified. Sensor units remain explicitly unverified where source metadata does
not establish them. For more REASSEMBLE-specific context, see
[REASSEMBLE_README.md](REASSEMBLE_README.md).

## REASSEMBLE saved-prediction player

[reassemble_prediction_player.py](reassemble_prediction_player.py) adds a desktop
player beside the notebooks. It replays a real **hand-camera** action interval,
native `measured_force[0]` observations, and saved visual/sensor/fusion outcomes.
It performs **no inference, training, evaluation or downloads**. Outcomes stay
hidden until the completed segment ends; the final frame pauses for discussion.
An annotated failure need not be visually obvious.

From the repository root:

```bash
# Default two-example demonstration (automatically exports if no desktop exists)
ma_thesis_env/bin/python -B tutorials/EDA/reassemble_prediction_player.py --demo

# Select one real sample by BOTH identifiers
ma_thesis_env/bin/python -B tutorials/EDA/reassemble_prediction_player.py --recording-id 2025-01-13-16-45-31 --segment-id 21

# Portable meeting videos and PNG fallbacks, without a desktop
ma_thesis_env/bin/python -B tutorials/EDA/reassemble_prediction_player.py --demo --headless --export

# Evidence checks and first/middle/final PNGs, without video encoding
ma_thesis_env/bin/python -B tutorials/EDA/reassemble_prediction_player.py --demo --validate-only

# Browse local cohort samples; --limit 0 prints all
ma_thesis_env/bin/python -B tutorials/EDA/reassemble_prediction_player.py --list-samples
```

Controls: **Space** pause/resume, **R** restart, **N/P** next/previous example,
**Left/Right** step native frames while paused, **Q/Escape** quit. Use
`--show-results-from-start` only for an explicitly retrospective discussion.
`--speed 0.5` slows playback; `--fps 15` controls export sampling, not alignment.
`--hold-seconds 4` sets the exported results-card hold. The raw root is resolved
from the frozen Section 1 config; `--data-root` or `REASSEMBLE_DATA_ROOT` can
override it. The existing inventory's encoded-media cache must be available;
the player does not extract new recording-sized video blobs into raw storage.

**Pinned evidence, not model selection by test score.** Default
`--run section2-clean --fusion F2` uses
`runs/reassemble/20260927T192852Z-section2`. F2 is the interpretable logistic
stacker on two saved branch probabilities, reused from
`20260927T175336Z-section1b`; branches come from
`20260927T154732Z-section1`. The visual branch uses frozen RT-DETR **backbone
features**, not displayed object detections. The sensor branch uses **statistics
and logistic regression**, not the separate PatchTST comparison. F2 has no
adaptive modality weights to display. Supported alternatives are `--fusion F1`
(the Section 2 uniform probability mean) and `--run section1b --fusion F2`.
Other fusion/gate banks are deliberately not exposed by this small player.
The original two EDA examples are reused: `2025-01-11-14-14-43/2` and
`2025-01-13-16-45-31/21`, selected nearest the insert action/outcome median
segment duration, with stable recording/segment ID tie-breaking. Predictions
never enter sample selection.

**Why the prediction belongs to this video.** Before enabling each result,
the player checks unique recording/segment IDs, raw bounds/action/outcome,
inventory size/mtime, the frozen cohort against the filtered audit table,
manifest hashes, the retained writer's source hashes, recording-disjoint folds,
explicit stacking outer-fold row indices, prediction labels and fold arrays,
per-fold versus aggregate arrays, and copies between the linked runs. Saved
hard decisions must agree with the exact retained threshold and `p >= threshold`;
no 0.5 default is used. Missing evidence disables the affected result and records
the reason. Full raw files and cached videos are not rehashed: cache lineage uses
the inventory's content-addressed path, HDF5 blob byte count and video/timestamp
frame-count agreement. This is not a fresh full integrity audit. Held-out means
excluded from that outer-fold fit; the study reused previously inspected folds
and is **exploratory**, not untouched confirmation.

Key code to follow (read, never executed by the player):

| Question | Existing implementation |
|---|---|
| Where do annotations and failure=1 originate? | `src/reassemble/inventory.py:53`, `audit_recording()`; `failure = int(not success)` |
| Which rows and visual frames were selected? | `src/reassemble/section1_features.py:24`, `cohort()`; selected block `row_index` / `frame_indices` |
| How do positional branch arrays map to the cohort? | `src/reassemble/section1_models.py:123`, `load_features()`; `evaluate_model()` writes `p[te]` and fold checkpoints |
| Where are explicit fusion row maps retained? | `src/reassemble/section1b.py:101`, `stacking()` writes `test_rows`, `train_rows` and fold results |
| Why can Section 2 reuse those predictions? | `src/reassemble/section2.py:152`, `collect()` copies U1/U2/F2 after label/fold agreement |
| How are timestamps interpreted? | `src/reassemble/alignment.py`, `timestamps_1d()` and inclusive `interval_indices()` |

Each execution creates a unique ignored
`runs/reassemble/<UTC-timestamp>-prediction-playback/` folder with three PNGs per
sample, `source_manifest.json`, `validation_summary.json` and an output manifest.
Export adds VP8 WebM videos and per-frame CSV mappings. Open a `.webm` for the
meeting; use its `_results.png` if video playback is unavailable. Media stay
local. The same layout renders the GUI and exports. Native Unix timestamps map
to a uniform output clock by holding the latest observed frame; the first frame
covers any leading gap, and the final results card is an explicit extra hold.
Duplicate/dropped frame counts and speed are recorded. Green timeline marks are
**retained historical** extraction frames, not a reconstruction. The sensor plot
shows native dots without interpolation, missing-value counts and unverified
units; no audio is attached.

The current project OpenCV build has **no GUI backend**, and this session has no
desktop display. Headless rendering/encoding/decoding can be tested here; desktop
keyboard interaction and browser playback cannot. No packages are changed.
Focused synthetic guard tests (separate from real-data checks):

```bash
ma_thesis_env/bin/python -B -m pytest -q -p no:cacheprovider tests/reassemble/test_prediction_player.py
```

Validated meeting backups from this implementation:

| Example | Video | Static results |
|---|---|---|
| `2025-01-11-14-14-43/2` | [Success-annotated example](../../runs/reassemble/20261016T111333786622Z-prediction-playback/2025-01-11-14-14-43_segment-2.webm) | [PNG](../../runs/reassemble/20261016T111333786622Z-prediction-playback/2025-01-11-14-14-43_segment-2_results.png) |
| `2025-01-13-16-45-31/21` | [Failure-annotated example](../../runs/reassemble/20261016T111333786622Z-prediction-playback/2025-01-13-16-45-31_segment-21.webm) | [PNG](../../runs/reassemble/20261016T111333786622Z-prediction-playback/2025-01-13-16-45-31_segment-21_results.png) |

[Validation and task file inventory](../../runs/reassemble/20261016T111333786622Z-prediction-playback/TASK_HANDOFF.md).
