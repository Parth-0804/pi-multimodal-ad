# ViFailback independent multimodal evaluation

The researcher authorized full implementation, three-camera 16-timestamp inputs,
three model seeds and 100-epoch visual experiments. This project is currently
being implemented; no ViFailback neural result is established by this README.

Historical evidence remains under
`DATASET_RESEARCH/VIFAILBACK_VERIFICATION/`. The initial preservation commit is
`9414da8f8ecc73299e442609f6e41e437dce9ec7`. No original data was moved or copied.
The conservative starting manifest contains 4,384 episodes, 3,755 native failures,
629 native no-failure episodes and 99 canonical tasks. Final eligibility still
depends on actual three-camera video QC.

The domain folders follow the existing MSM organization. Implementation lives in
`src/vifailback/`; scripts bootstrap both this package and reusable repository
code. Configuration paths are repository-relative. Raw video payloads, live
training state and large generated arrays are ignored by Git.

Current commands, from repository root:

```bash
ma_thesis_env/bin/python -B -m pytest -q VIFAILBACK/tests
ma_thesis_env/bin/python -B VIFAILBACK/scripts/acquire_videos.py
```

`configs/experiment.json` fixes all three camera streams, sixteen synchronized
temporal positions per camera, 100 scheduled epochs, seeds 42/123/20261023 and
three outer task groups with three inner grouped OOF partitions. The new 3×3
design satisfies the current request's minimum and replaces the earlier draft
5×4 design; no epochs are reduced and no model results choose the split count.
The three-camera input means 48 RGB images at 16 times, not 32 timestamps.

The existing REASSEMBLE 75-fit study has priority. ViFailback must not use its GPU
until that study has completed and the GPU is idle. CPU acquisition, QC,
preprocessing, implementation and independently valid baseline work can proceed.
Long-run status and exact resumable commands will be recorded in
`RESEARCH_COMPLETION_STATUS.md` and `10_final_research_reports/` as stages finish.

## Evidence and execution flow

1. `01_original_dataset/acquired_videos/` contains only newly acquired, pinned,
   hash-verified source clips. Existing pilot clips and numerical tables are
   referenced in their immutable historical locations; they are not copied.
2. `02_dataset_verification/label_audit/20261029T004900Z/INDEPENDENT_NATIVE_RECOUNT.json`
   verifies all5,202 native joins. Video receipts live under
   `02_dataset_verification/video_audit/runs/20261029T004900Z/`. Episode2071's
   right-wrist and4784's left-wrist corruptions are confirmed by both libdav1d
   and libaom; source bytes are preserved. The final common cohort contains
   4,382 episodes:3,753failures/629no-failures,99tasks,820unique exclusions.
3. `03_preprocessing/processed_manifests/20261029T004900Z/eligible.json` and
   `exclusions.csv` define the common cohort once QC finishes. The data contract
   is under `03_preprocessing/data_contracts/20261029T004900Z/`.
4. `04_evaluation_splits/train_validation_test/20261029T004900Z/fit_partitions.json`
   records disjoint task T/V/C/assessment IDs. All inner assessment records are
   accounted for exactly once in each outer training pool.
5. `src/vifailback/reference.py` imports the actual REASSEMBLE primitives.
   `visual.py`, `sensors.py`, `training.py`, `baselines.py` and `fusion.py` own
   the dataset adapters and target-specific fitting. There is no copied model
   monolith. Original detector heads are not executed or transferred.
6. `06_training_experiments/*/runs/20261029T004900Z/` retains checkpoints,
   every-epoch histories/plots, calibration records, held-out probabilities,
   coefficients, OOF inputs and completion/hash receipts.
7. `07_robustness_experiments/combined_corruption/runs/20261029T004900Z/`
   records fixed label-blind input stresses. Learned gating and programmed
   availability fallbacks are distinguished; both modalities missing abstains.
8. `08_visual_examples_and_eda/` contains actual source views and eventually
   saved-prediction examples. Fixed central crops are explicitly labeled and
   never represented as detector boxes or verified manipulation regions.
9. `verification.py` recomputes saved results, checks native targets/OOF/calibration
   lineage and reports incomplete artifacts. Reports retain prior immutable
   versions under `10_final_research_reports/report_snapshots/`.

`configs/protocol.json` freezes prediction units, co-primary AP metrics, selection,
imbalance, budgets, fusion and robustness rules before held-out prediction.
V1/V2/V3 each require36 fits (3outer × [3inner+1final] ×3seeds); V2 and V3
therefore require72 full100-epoch CNN fits. The source donor has one fixed
REASSEMBLE training seed; target seeds do not replicate donor training.

A supplementary `visual_frozen_high_only/` branch retrains the same frozen-CNN
head using only16 high-camera frames, with the same cohort, splits, budgets and
three seeds. It reuses the existing per-camera feature bank; this adds36 cheap
head fits and no full-CNN fits. The high camera was fixed before held-out
predictions. It is a secondary camera ablation, separate from the primary
three-view comparison. A separately trained availability-only gate provides a
matched architecture/budget control for the quality-conditioned gate.

Supplemental matched corruption-training controls (`fusion_experiments/augmentation/runs/`)
give F2, the quality gate and its availability-only control the same clean plus
one label-blind corrupted OOF record per native meta episode. Each corrupted
record uses that episode's actual inner-held-out branch checkpoint/calibrator.
The gate uses20epochs over2N records to match the clean40N presentations; the
CNN schedules remain100epochs. Augmented records are repeated views, not new
independent episodes. Primary clean-trained and supplemental augmented results
remain separate in reports.

## Run and resume

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 CUBLAS_WORKSPACE_CONFIG=:4096:8 \
  ma_thesis_env/bin/python -B VIFAILBACK/scripts/run_pipeline.py

ma_thesis_env/bin/python -B VIFAILBACK/scripts/worker.py --help
```

The controller holds `logs/20261029T004900Z/pipeline.lock`; a second controller
must not run concurrently. It reuses verified artifacts, supervises this
project's workers by PID and creation time, and resumes epoch-boundary state.
It does not send signals to REASSEMBLE or other jobs. It checks the source
75-fit completion marker and its metric hash, plus absence of other GPU compute
processes. A temporarily idle GPU between source fits is insufficient.

`logs/20261029T004900Z/PIPELINE_STATUS.json`, `STAGE_HISTORY.json`,
`EXECUTION_PROVENANCE.json` and per-stage logs are the live records. The pipeline
fails closed on source/code drift or broken scientific lineage. A failed visual
or robustness condition does not silently remove examples or shorten epochs;
other independent conditions continue and the final status remains partial.

Completed stages may produce a narrowly scoped local evidence commit if the
branch is unchanged and the Git index contains no staged work. Unrelated work,
large artifacts and raw data are excluded. No push or PR is performed.

Do not edit frozen code/configuration during a live run. Scientific changes need
a new versioned run. Read `RESEARCH_COMPLETION_STATUS.md` and reports01,05,11,13
for actual completion and unresolved evidence; successful implementation tests
are not target-model performance results.

Read `10_final_research_reports/reproducibility/REPRODUCTION_SCOPE.md` for the
distinction between new source-level checks, historical HDF5 evidence, synthetic
tests and saved-result consistency. The three anomalous HDF5 cases referenced
by the current quarantine check are part of the larger preserved historical
comparison evidence; they are not its entire scope.
