"""Evidence-driven live reports; incomplete experiments stay explicitly partial."""
import json
from pathlib import Path
import shutil

import numpy as np

from phase_common import ROOT, EXEC, EVIDENCE, config, read, write, utc, sha

REPORTS = ROOT / '26102026_reports'


def put(name, text):
    path = REPORTS / name
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.writing')
    temporary.write_text(text)
    temporary.replace(path)


def gpu_integration():
    benchmark = read(EVIDENCE / 'PHASE1_FULL_CNN_BENCHMARK.json')
    gate = read(EVIDENCE / 'PHASE1_FULL_CNN_GATE.json')
    rows = benchmark['windows']
    utilization = np.mean([r['GPU_compute_percent'] for r in rows])
    epoch = np.mean([r['reference_2966_action_epoch_seconds'] for r in rows]) / 60
    low, high = gate['time_estimates']['planning_hours_with_20_to_40_percent_overhead']
    text = f'''# Phase 1 GPU integration — verification complete

Updated {utc()}. The fully trainable CNN performance gate passed. This is a
bounded training-side pilot, not a completed full-cohort epoch or experiment.

One allocated NVIDIA Tesla T4, 16 GB nominal VRAM, driver 580.167.08, CUDA driver
13.0, PyTorch 2.13.0+cu130, cuDNN 9.2; 16 available EPYC CPU cores and about
62.7 GiB system RAM. The exact hardware/software snapshots are in
`../26102026_execution/26102026_main_run_01/26102026_full_cnn_preflight_01/PHASE1_PREFLIGHT_PROVENANCE.json`.
GPU compute utilization below is sampled kernel-busy percentage. It measures
neither VRAM occupancy nor percentage of peak FLOPS.

| Measurement | Earlier optimized pilot | New fully trainable CNN pilot |
|---|---:|---:|
| Executed gradient scope | Final CNN stage and head | All executed CNN convolutions, normalization affine parameters, head |
| Precision | FP32 | FP32 |
| Sustained GPU compute utilization | 97.9% | {utilization:.2f}% |
| Actions/second | 6.637 | {benchmark['actions_per_second']:.4f} |
| Projected 2,966-action training epoch | 7.45 minutes | {epoch:.2f} minutes |
| Peak process VRAM | About 4.15 GiB | {max(r['peak_vram_MiB'] for r in rows)/1024:.3f} GiB |
| Peak tensor allocation | Different gradient scope | {max(r['peak_allocated_bytes'] for r in rows)/1024**3:.3f} GiB |

The columns have different computation and gradient coverage. They are not a
matched speedup comparison. Historical 18–20% utilization reflected input
starvation in the previous workload; the original report isolates decoding,
CPU preprocessing, decoder thread proliferation and loader stalls. Its earlier
serial live32 diagnostic was unstable and is not a valid selected baseline.
The original report and all benchmark evidence remain unchanged.

| Full-CNN window | Seconds | Actions | Actions/s | Updates/s | GPU compute | CPU loading wait | CUDA forward/backward time |
|---|---:|---:|---:|---:|---:|---:|---:|
'''
    for row in rows:
        text += (f"| {row['repetition']+1} | {row['seconds']:.2f} | {row['actions']} | "
                 f"{row['actions_per_second']:.4f} | {row['optimizer_updates_per_second']:.4f} | "
                 f"{row['GPU_compute_percent']:.2f}% | {row['CPU_loading_wait_seconds']:.3f}s | "
                 f"{row['forward_backward_cuda_event_seconds']:.3f}s |\n")
    text += f'''
Both windows exclude worker/model initialization and checkpoint writes and
follow two warm-up passes. Their training-side subset contains 24 actions;
full-cohort sustained performance is recorded separately per executed epoch.
About 6% of measured wall time was spent waiting for input, and CUDA work
occupied about 93% of wall time. These components overlap. The new dominant
cost is full forward/backward computation. There is no measured reason to
repeat the previous worker grid, increase effective batch size, or change
precision. Native BF16 is unavailable; FP16 and torch.compile are not enabled
or claimed equivalent. This preserves the validated FP32 scientific protocol.

The selected configuration uses exact whole-action 16-frame decoding, FFmpeg
two threads/video, four persistent workers, prefetch two, pinned memory and
nonblocking device transfer. Sixteen frames are batched in one CNN call per
action; eight actions are accumulated per update. The final partial group is
scaled by its actual number of actions. CPU thread limits prevent oversubscription.
No DDP is configured on the single allocated GPU. Independent fits run
sequentially; the controller waits when another GPU workload is detected.

All 4,530 actions from 148 recordings (509 failure targets) passed exact
selected-frame identity, dimensions, dtype, label/timestamp and recording
association validation. All 16 frames match the intended original FP32 input
reconstruction and uniform whole-action policy; no last-quarter substitution.
See `../26102026_evidence/PHASE1_INPUT_VERIFICATION_STATUS.json` and its manifest.

The real-CNN pilot verifies finite gradients for every intended parameter,
nonzero early/middle/final-stage and head gradients, actual updates in every
CNN stage, fixed running moments, identical resumed model/optimizer/scheduler/
RNG and epoch order, exact sample counts, and saved-model reload predictions.
Frozen normalization affine buffers become trainable parameters while their
forward formula and running moments remain unchanged. No detector decoder,
attention or proposal modules are executed. Cooperative shutdown records show
zero worker exit codes after complete, resumed and short prediction iterations.
Synthetic regressions also cover early exceptions and an interrupted selected-
checkpoint replacement before epoch commit. The latter retains selected
weights inside both resumable generations so recovery cannot select an
uncommitted future checkpoint.

`PHASE1_PREFLIGHT_SOURCE_RECONCILIATION.json` links all eight exact pilot source
files to their recorded hashes and retained copies. Model, loader, metric and
pilot source are unchanged. Subsequent crash-selection recovery, telemetry and
action-association checks are explicit additions covered by the final tests.

Measured full-CNN computation projects {gate['time_estimates']['full_CNN_training_hours_min25']:.1f}–
{gate['time_estimates']['full_CNN_training_hours_max50']:.1f} training GPU-hours
for 75 full-CNN fits at 25–50 epochs. A planning allowance for validation,
calibration, loader starts, checkpointing and 75 small frozen-head fits gives
**{low:.0f}–{high:.0f} GPU-job hours, approximately {low/24:.1f}–{high/24:.1f} days**
of exclusive single-T4 availability. This is a planning range, not measured
total runtime; early stopping, full-cohort locality and competing workloads
change the calendar duration. Actual completed training and GPU-job wall-hours
are updated in the executive report and controller status.

Evidence: `PHASE1_FULL_CNN_BENCHMARK.json`, `PHASE1_FULL_CNN_GATE.json`,
`PHASE1_FULL_CNN_GRADIENT_EVIDENCE.json`, `PHASE1_FULL_CNN_RESUME.json`,
`PHASE1_FULL_CNN_RELOAD.json`, and per-epoch telemetry under the new execution
directory. The old audit gate remains untouched; the new full-CNN gate is
specific to this newly authorized protocol.
'''
    put('PHASE1_GPU_INTEGRATION.md', text)


def plot_fit(folder):
    """Standalone exportable learning curves, generated only for completed fits."""
    target = folder / 'PHASE1_LEARNING_CURVES.png'
    if target.exists():
        return
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    history = read(folder / 'PHASE1_LEARNING_CURVE.json')
    done = read(folder / 'PHASE1_FIT_COMPLETE.json')
    epoch = [r['epoch'] for r in history]
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), constrained_layout=True)
    for key, label in [('training_loss', 'Training'), ('validation_loss', 'Validation')]:
        axes[0, 0].plot(epoch, [r[key] for r in history], label=label)
    axes[0, 0].set(ylabel='Weighted BCE'); axes[0, 0].legend()
    for key, label in [('validation_AP', 'AP'), ('validation_AUROC', 'AUROC')]:
        axes[0, 1].plot(epoch, [r[key] for r in history], label=label)
    axes[0, 1].set(ylabel='Validation metric'); axes[0, 1].legend()
    for group in range(len(history[0]['learning_rates'])):
        axes[1, 0].plot(epoch, [r['learning_rates'][group] for r in history], label=f'Parameter group {group}')
    axes[1, 0].set(ylabel='Learning rate', yscale='log'); axes[1, 0].legend()
    axes[1, 1].plot(epoch, [r['training_seconds']/60 for r in history], label='Training minutes')
    axes[1, 1].set(ylabel='Training minutes')
    for ax in axes.flat:
        ax.axvline(done['best']['epoch'], color='black', ls=':', label='Selected epoch')
        ax.set(xlabel='Executed epoch'); ax.grid(alpha=.2)
    fig.suptitle(f"{done['arm']} / seed {done['seed']} / fit {done['job_index']} / selected epoch {done['best']['epoch']}")
    fig.savefig(target, dpi=150)
    plt.close(fig)


def refresh(status, final=None):
    from phase_evaluation import summarize
    index = summarize(complete=False)
    fits = read(EXEC / 'PHASE1_COMPLETED_FIT_INDEX.json')
    for folder in EXEC.glob('26102026_seed*'):
        if (folder/'PHASE1_FIT_COMPLETE.json').exists():
            plot_fit(folder)
    hours = sum(r['training_seconds'] for r in fits)/3600
    attempts = read(EXEC/'PHASE1_PROCESS_ATTEMPTS.json') if (EXEC/'PHASE1_PROCESS_ATTEMPTS.json').exists() else []
    job_hours = sum(r.get('elapsed_seconds', 0) for r in attempts)/3600
    done_b = sum(r['arm'] == 'B_long_frozen16' for r in fits)
    done_c = sum(r['arm'] == 'C_full_finetuned16' for r in fits)
    complete = final is not None
    label = 'COMPLETE' if complete else 'PARTIAL — ' + status['stage']
    text = f'''# Phase 1 executive review — {label}

Updated {utc()}. This is a follow-up experiment on a repeatedly studied dataset.
Completed **{len(fits)}/150 visual fits**: B {done_b}/75, C {done_c}/75.
Completed-fit training totals {hours:.3f} GPU-hours. Recorded child-process
wall time totals {job_hours:.3f} GPU-job hours, including retries and inference;
an active child's elapsed time appears in `PHASE1_CONTROLLER_STATUS.json`.
CPU-only waiting and sensor analysis are excluded. Earlier audit/pilot GPU-hours
were not completely metered and are not invented or included in this total.

| Task | Status | Evidence |
|---|---|---|
| Historical audit | completed | PHASE1_HISTORICAL_AUDIT.md |
| Exact input / GPU integration | completed | PHASE1_GPU_INTEGRATION.md; full-cohort identity manifest |
| Full CNN gradients / updates | completed | Full-CNN preflight gradient evidence |
| Full-backbone benchmark / epoch recovery | completed | PHASE1_FULL_CNN_GATE.json |
| Long Frozen16 | {'completed' if done_b == 75 else ('partial' if done_b else 'not started')} | {done_b}/75 fit receipts |
| Full FineTuned16 | {'completed' if done_c == 75 else ('partial' if done_c else 'not started')} | {done_c}/75 fit receipts |
| Three-seed stability | {'completed' if complete else 'not started'} | Fixed seeds 42, 123, 20261023; final pooled predictions required |
| Matched F2 retraining | {'completed' if complete else 'not started'} | 25 shared sensor fits, 30 main F2 fits; 15 supplemental short-reference F2 fits |
| Final evaluation | {'completed' if complete else 'not started'} | Paired recording-cluster bootstrap; folds/seeds not independent samples |
| Reports | {'completed' if complete else 'partial'} | Six named reports; result reports remain partial until complete |

| Model | Seeds | Executed / selected epochs | Visual AP | F2 AP | Training GPU-hours |
|---|---|---|---|---|---|
| Historical original Frozen16 A | Original seed family 20260927 | Candidates 5/10; outer selections 5,5,10,10,5 | 0.2306583150 | 0.4472985514 historical F2 | Extraction excluded; original nested head 11.12 s |
'''
    if not complete:
        for arm, count in [('B_long_frozen16', done_b), ('C_full_finetuned16', done_c)]:
            selected = [r for r in fits if r['arm'] == arm]
            text += f"| {arm} | Three fixed seeds | {count}/75 fits complete | Pending complete held-out evaluation | Pending | {sum(r['training_seconds'] for r in selected)/3600:.3f} measured completed fits |\n"
        text += '''
Scientific verdict: supported — exact input equivalence, full executed-CNN
trainability and deterministic epoch-boundary recovery on the pilot.
Unknown — whether longer classifier training or full-CNN fine-tuning improves
visual AP or F2, and whether effects are stable across seeds. A partial run
cannot answer those questions. No accuracy hypothesis is contradicted or
supported by utilization measurements. Phase 2/3 execution is not authorized
here and no selected architecture is ready to recommend from new accuracy
evidence yet.

The protocol fixes 25–50 executed epochs, training-only validation selection,
recording-disjoint outer/inner folds and separate calibration records. All CNN
convolutions and normalization affine parameters train; normalization running
moments remain fixed. Head learning rate 1e-3 and CNN learning rate 1e-5 use
AdamW with fixed cosine scheduling. B reuses identical FP32 frozen features.
Historical A is preserved; supplemental A_r is a matched short-horizon
reconstruction from B's epoch-5/10 snapshots and is identified separately.
'''
        put('PHASE1_FUSION_RESULTS.md', '# Phase 1 fusion results — NOT COMPLETE\n\n'
            f'Updated {utc()}. {len(fits)}/150 visual fits complete. Final matched F2-B/C results, '
            'seed stability and uncertainty await complete branch predictions. Historical F2 AP '
            '0.4472985514 is a verified context value, not a new result. No missing result is imputed.\n')
    else:
        for method in config()['arms']:
            v = next(r for r in final['stability'] if r['method'] == method and r['kind'] == 'visual')
            f = next(r for r in final['stability'] if r['method'] == method and r['kind'] == 'fused')
            selected = [r for r in fits if r['arm'] == method]
            executed = sorted(set(r['executed_epochs'] for r in selected))
            picked = sorted(set(r['selected_epoch'] for r in selected))
            text += f"| {method} | 42,123,20261023 | Executed {executed}; selected {picked} | {v['AP_mean']:.6f} ± {v['AP_sample_sd_across3seeds']:.6f} seed SD | {f['AP_mean']:.6f} ± {f['AP_sample_sd_across3seeds']:.6f} | {sum(r['training_seconds'] for r in selected)/3600:.3f} |\n"
        text += '\n## Paired interpretation\n\n'
        for name, result in final['uncertainty'].items():
            verdict = ('positive paired difference supported conditionally on fitted models' if result['lower95'] > 0 else
                       'negative paired difference supported conditionally on fitted models' if result['upper95'] < 0 else
                       'inconclusive; interval includes zero')
            text += f"{name}, C minus B: bootstrap mean {result['mean']:.6f}, recording-cluster 95% interval [{result['lower95']:.6f}, {result['upper95']:.6f}]; {verdict}.\n\n"
        for name, result in final['longer_uncertainty'].items():
            text += f"{name}, long B minus matched short A_r: mean {result['mean']:.6f}, recording-cluster 95% interval [{result['lower95']:.6f}, {result['upper95']:.6f}].\n\n"
        text += 'Per-seed AP differences:\n\n```json\n' + json.dumps(final['paired_seed_differences'], indent=2) + '\n```\n\n'
        choice = 'C_full_finetuned16' if final['uncertainty']['fusion_AP']['lower95'] > 0 else 'B_long_frozen16'
        text += f'Provisional candidate for a separately authorized next phase: **{choice}**. '
        text += 'This uses the paired fusion result and favors the cheaper frozen control when a positive F2 difference is not established. It is not a robustness claim.\n\n'
        timing = read(EXEC/'PHASE1_MATCHED_INFERENCE_BENCHMARK.json')
        text += 'Matched live16 end-to-end inference windows (worker/model startup excluded):\n\n```json\n' + json.dumps(timing, indent=2) + '\n```\n\n'
        text += '''These intervals use the same recording resample across all fixed seeds.
They condition on fitted models; repeated dataset exposure, only three seeds,
and no unseen-site assessment limit generalization. No practical AP threshold
was preregistered. Training-cost increases must be considered alongside the
effect sizes, sign consistency and seed SD rather than declaring a winner from
the best seed. Historical A uses different precision/selection/calibration and
is descriptive; A_r supplies a separately labeled matched short-horizon contrast.
Full B-minus-A_r seed differences and calibration metrics are retained in the
final metrics artifact.

All completed checkpoints are technically usable for a separately authorized
Phase 2 robustness study. Scientific preference depends on the paired F2 and
visual evidence above; an interval crossing zero provides no established case
for the more expensive backbone. Phase 3 architecture replication remains a
new dataset experiment. No robustness or transfer superiority follows here.
'''
    text += '\nArtifacts: `../26102026_configuration/PHASE1_CONFIG.json`; '
    text += '`../26102026_evidence/PHASE1_FIT_PLAN.json`; `../26102026_execution/26102026_main_run_01/` '
    text += '(fit-specific logs, hashes, selected models, two epoch recovery generations, learning curves, '
    text += 'keyed predictions, F2 coefficients and final metrics). '
    text += f"Controller stage: {status['stage']}. Disk free: {shutil.disk_usage(ROOT).free/1024**3:.1f} GiB.\n"
    put('PHASE1_EXECUTIVE_REVIEW.md', text)
    return index


def output_manifest():
    files = []
    for path in ROOT.rglob('*'):
        if not path.is_file() or path.name.endswith('.writing'):
            continue
        relative = path.relative_to(ROOT)
        if str(relative) == '26102026_evidence/PHASE1_OUTPUT_MANIFEST.json':
            continue
        size = path.stat().st_size
        files.append({'path': str(relative), 'bytes': size,
                      'sha256': sha(path) if size < 64*1024**2 else None,
                      'role': 'recoverable/checkpoint bulk' if path.suffix == '.pt' else 'report/metric/provenance/evidence'})
    write(EVIDENCE/'PHASE1_OUTPUT_MANIFEST.json', {'utc': utc(), 'files': files,
        'large_checkpoint_hashes': 'Selected models and latest epoch slots have hashes in their own fit receipts/pointers'})
