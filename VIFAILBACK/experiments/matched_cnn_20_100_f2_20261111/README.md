# Matched ViFailback CNN, donor and F2 study

This isolated experiment was created on **11 November 2026 (Europe/Berlin)**, using the actual local date rather than the suggested November 10 directory name. The user explicitly authorized training, evaluation, local commits and scientific reporting. No push is authorized.

A concise [initial completed-results snapshot](14_final_research_reports/00_INITIAL_COMPLETED_RESULTS.md) summarizes the completed frozen/donor stage.

Start with [current study status](VIFAILBACK_MATCHED_CNN_STUDY_STATUS.md) and [executive report](14_final_research_reports/01_EXECUTIVE_SUMMARY.md). These reports describe completed evidence and running or pending work separately. Long GPU fits are resumable and retain every requested epoch.

## Scientific scope

- FROZEN20 versus FULL20: original pretrained CNN, matched target head, 20 executed epochs using the first 20 steps of the original cosine50 schedule; three outer folds and three inner roles plus final refit per outer.
- FROZEN100 versus FULL100: seed42, first predefined outer fold0, base role outer0_inner0, 100 executed epochs with cosine100. The verified historical frozen fit is reused; selected epoch11, final epoch100 retained at its original path.
- DONOR20 and DONOR100: verified REASSEMBLE Full100 epoch47 CNN features, frozen CNN, new ViFailback heads and training-only target scalers. No target-domain donor CNN fine-tuning is declared.
- Both-class validation macro AP, lower validation weighted BCE, then earliest epoch select checkpoints. Every scheduled epoch executes.
- All arms use the same 4,382 eligible native episodes and the same three cameras ×16 timestamps. The prediction unit is one completed episode.
- F2 uses calibrated visual and canonical static LR probabilities. The20-epoch fits require complete three-inner OOF banks; the100-epoch pilot uses a separate788-episode meta bank and1107-episode outer assessment.
- The pilot retains distinct inner and outer sensor refits, identically across visual arms. HGB and historical V1 are retained secondary references.

The immutable [protocol](01_protocol_and_source_evidence/protocol.json), [dataset and split evidence](02_dataset_and_splits/README.md), and resource admission determine the exact scope. Seeds42,123,20261023 were declared before new scores; actual admission is recorded independently of performance. Running jobs do not establish predictive improvement.

## Reproducible commands

Run from the repository root with its existing environment. Use separate terminals for the CPU, GPU and reporting lanes. The launched background processes already own these locks; do not start duplicate lanes while they are alive.

```bash
ma_thesis_env/bin/python -B VIFAILBACK/experiments/matched_cnn_20_100_f2_20261111/scripts/study.py status
ma_thesis_env/bin/python -B VIFAILBACK/experiments/matched_cnn_20_100_f2_20261111/scripts/study.py verify
ma_thesis_env/bin/python -B VIFAILBACK/experiments/matched_cnn_20_100_f2_20261111/scripts/study.py run --lane cpu
ma_thesis_env/bin/python -B VIFAILBACK/experiments/matched_cnn_20_100_f2_20261111/scripts/study.py run --lane gpu
ma_thesis_env/bin/python -B VIFAILBACK/experiments/matched_cnn_20_100_f2_20261111/scripts/study.py watch
ma_thesis_env/bin/python -B VIFAILBACK/experiments/matched_cnn_20_100_f2_20261111/scripts/study.py evaluate
```

A resumed lane validates the same protocol, implementation, input and completed artifact hashes. An unfinished epoch replays from its committed model, optimizer, scheduler and RNG state. The selected checkpoint is embedded in each committed recovery generation. Final checkpoints and selected weights remain retained. Only an unreferenced temporary rolling recovery generation created by the new fitter is released after completion; prior scientific artifacts remain untouched.

Before the first scientific fit, the `benchmark`, `benchmark8`, `admit` and `freeze` commands were executed and their evidence saved. Bounded benchmarks are disposable training-side verification, not scientific fit epochs. The existing source-study75-fit gate was preserved. This new study separately verifies the approved25-fit source stop and absence of competing work.

## Layout and retention

Folders03–07 hold condition-specific configurations, histories, checkpoint journals and probabilities. Folder09 holds fitted target F2 coefficients and exact meta/outer predictions. Folder11 holds metrics, paired task-cluster uncertainty and coverage. Folder12 holds learning curves. Folder13 holds test evidence, software and Git provenance, launch identities and runtime journals. Folder14 holds the13 requested research reports.

Large checkpoints, caches and runtime logs stay local and ignored by Git. Historical dataset/video/feature/sensor and model artifacts are referenced by portable paths and hashes, never duplicated or overwritten. The final report is evidence conditional on observed task groups; session/operator independence and pristine independent confirmation are not established.
