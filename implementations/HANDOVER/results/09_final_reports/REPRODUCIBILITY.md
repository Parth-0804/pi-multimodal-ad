# HANDOVER reproducibility and validation

Run from repository root using the existing environment:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
PYTHONPATH='src:MSM/99_preserved_previous_work/MILLING_DATASET/source:CROSS_DATASET_COMPARISON/src' \
ma_thesis_env/bin/python -B -m external_eval.run_all
```

The runner reuses immutable raw inputs, resumes per-example CNN caches and completed fits/cases, then automatically evaluates all fixed seeds and robustness scenarios. No additional GO is needed. Model-specific blockers do not silently replace a method. The active dataset root for this delivery is `HANDOVER/experiments/common_support_v2`. Handover's earlier full-video audit and its later common-support amendment remain separate preserved evidence.

Pinned configs/splits are under04_experiment_protocol and03_processed_model_inputs/split_manifests. Native sources/hashes, cache identities, source/model/config hashes, actual derived fit seeds, OOF group provenance, CPU/GPU times, FP32 parity check and checkpoint reload checks are preserved. The actual CNN cache reproduction maximum difference is0.0 on an outer-training-only example; no gradient flows through the frozen CNN. The new synthetic regression suite tests full outer composition, atomic integrity, labels, timestamps, dropout, OOF isolation, training gradients, exact reload, metrics and missing-modality semantics. Existing MSM tests are retained.

All reported fold metrics were independently recalculated from saved predictions. That checks saved-result consistency, not a separate rerun of every stochastic model. The full actual feature extraction and model matrix were executed here; raw-label/sensor/frame admission was also reproduced. Group bootstrap assumptions and unavailable Handover participant mapping remain explicit. No historical source dataset, PHM/Intel raw data or active REASSEMBLE experiment was modified; no staging/commit occurred.

The independent implementation_validation.json audit checks every planned case, native label/assessment identity, head-update budget, derived seed, checkpoint hash and exact reload receipt. On MSM it also refits the same fixed F2 estimator from saved clean OOF probabilities and checks its coefficients; it never uses assessment rows. A transient controller feature-polling race was corrected and regression-tested; the identical frozen MSM evaluator completed directly. Its correction receipt and original controller record remain preserved, with any resolved operational blocker documented separately from scientific gates.

Training is CPU FP32 for the small new heads/classifiers; real-image frozen CNN extraction uses the shared T4. The process memory cap is2GiB, measured peak tensor allocation about433MiB. Device-wide100% utilization belongs to the shared workload and is not an MSM/Handover utilization result. CNN caches store compact per-frame embeddings for clean plus real-image corruptions; no huge duplicated640×640 frame cache is retained. Runtime details: `HANDOVER/experiments/common_support_v2/06_evaluation_results/runtime_summary.json`.
