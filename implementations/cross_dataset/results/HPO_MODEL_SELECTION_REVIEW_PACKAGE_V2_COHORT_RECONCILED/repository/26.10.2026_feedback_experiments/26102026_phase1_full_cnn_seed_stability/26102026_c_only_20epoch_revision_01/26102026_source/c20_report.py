"""C-only reporting and F2-C analysis; no pending B fit is referenced."""
import json
import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

from c20_common import ARM, BASE, REVISION, RUN, REPORTS, EXEC, EVIDENCE
from c20_common import configuration, schedule, receipt_for, remaining_estimate, read, write, utc
from phase_training import folder_for
from phase_evaluation import evaluate_fold
from phase_metrics import metrics, aligned_keys
from phase_reporting import plot_fit


def put(name, text):
    path = REPORTS/name
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name+'.writing')
    temp.write_text(text)
    temp.replace(path)


def completed():
    return [read(receipt_for(seed, job)) for seed, job in schedule() if receipt_for(seed, job).exists()]


def refresh(state, final=None):
    fits = completed()
    write(RUN/'PHASE1_C_ONLY_COMPLETED_INDEX.json', fits)
    estimate = remaining_estimate()
    total_hours = sum(r['training_seconds'] for r in fits)/3600
    attempts=read(EXEC/'PHASE1_PROCESS_ATTEMPTS.json')
    job_hours=sum(r.get('elapsed_seconds',0) for r in attempts if r.get('arm')==ARM)/3600
    title = 'COMPLETE' if final is not None else 'PARTIAL'
    text = f'# Full CNN training results — {title}\n\nUpdated {utc()}. {len(fits)}/75 C fits complete. Each executes exactly20 epochs. Pending B fits:0.\n\n'
    text += '| Seed | Fit | Executed | Selected | Training hours | Mean GPU compute |\n|---|---:|---:|---:|---:|---:|\n'
    for seed, job in schedule():
        receipt = receipt_for(seed, job)
        if not receipt.exists():
            continue
        r = read(receipt)
        folder = folder_for(ARM, seed, job)
        history = read(folder/'PHASE1_LEARNING_CURVE.json')
        observed = [v['GPU_compute_percent'] for v in history if v['GPU_compute_percent'] is not None]
        gpu = f'{np.mean(observed):.2f}%' if observed else 'Unavailable'
        text += f"| {seed} | {job['job_index']} | 20 | {r['selected_epoch']} | {r['training_seconds']/3600:.4f} | {gpu} |\n"
        plot_fit(folder)
    text += '\nThe original per-fit folders retain every epoch loss, validation AP/AUROC, LR, time, VRAM, CPU memory, sampler hash, GPU telemetry, best model and two recovery generations. Checkpoint selection may precede20 even though20 epochs execute. Learning-curve JSON and PNG are retained per completed fit. Decreasing training loss with worsening validation AP is compatible with overfitting; an earlier selected checkpoint does not demonstrate a benefit from extra exposure.\n'
    if final:
        text += '\n## Held-out visual results\n\n| Seed | Outer fold | AP | AUROC | Prevalence |\n|---|---:|---:|---:|---:|\n'
        for r in final['fold_metrics']:
            if r['kind'] == 'visual':
                text += f"| {r['seed']} | {r['outer_fold']+1} | {r['AP']:.6f} | {r['AUROC']:.6f} | {r['prevalence']:.6f} |\n"
    put('PHASE1_TRAINING_RESULTS.md', text)
    low, high = estimate['remaining_planning_days_exclusive_GPU']
    review = f'''# C-only executive review — {title}

Updated {utc()}. User requested C only and explicitly selected20 epochs per fit.
The schedule is **3 seeds ×5 outer folds ×(4 inner fits +1 outer fit)=75 full-CNN fits**.
Pending B training and F2-B comparisons are removed. The one completed B fit is
preserved as prior work and excluded from this revised study.

Completed C fits: **{len(fits)}/75**. Current stage: {state['stage']}.
Measured completed-fit training GPU-hours: {total_hours:.3f}.
Recorded C child-process wall-hours, including retained/retried work: {job_hours:.3f}.
Remaining planning range: **{low:.2f}–{high:.2f} days**, assuming continuous
single-T4 availability. This uses measured full-CNN speed and20–40% overhead;
other GPU workloads add calendar time. Removing inexpensive cached-head fits
does not halve the original CNN-dominated runtime.

Initialization, labels, exact live16 input, FP32, effective batch8, optimizer,
fixed normalization running moments, trainable CNN affine/convolution weights,
group partitions and training-only selection/calibration remain unchanged.
The cosine learning-rate horizon remains50 for all fits so the completed
prefix of the active CNN can resume exactly. The execution cap is20, with
checkpoint candidates1–20 and no patience stop before20.

| Task | Status |
|---|---|
| Historical/input/GPU and gradient audit | completed; original evidence reused |
| C training | {'completed' if len(fits)==75 else 'partial'}; {len(fits)}/75 |
| Three-seed stability | {'completed' if final else 'pending'} |
| F2-C,15 stackers with25 reused sensors | {'completed' if final else 'pending'} |
| B training/comparison | removed by user; completed artifacts preserved |
| Phase2/3 | outside this execution scope |

'''
    if final:
        review += '| Seed | Visual AP | F2-C AP | Visual AUROC | F2-C AUROC |\n|---|---:|---:|---:|---:|\n'
        for seed in configuration()['seeds']:
            v = next(r for r in final['pooled'] if r['seed']==seed and r['kind']=='visual')
            f = next(r for r in final['pooled'] if r['seed']==seed and r['kind']=='fused')
            review += f"| {seed} | {v['AP']:.6f} | {f['AP']:.6f} | {v['AUROC']:.6f} | {f['AUROC']:.6f} |\n"
        review += '\nRecording-cluster uncertainty (common recording draws across fixed seeds):\n\n```json\n'+json.dumps(final['recording_bootstrap'], indent=2)+'\n```\n'
        review += '\nThese held-out metrics characterize the trained C models and their fusion. A new matched long-frozen comparison was withdrawn, so the experiment cannot isolate the benefit of full-CNN adaptation beyond longer classifier-only training. Historical Frozen16/F2 AP values are descriptive context. No robustness or cross-dataset transfer conclusion follows. The completed C checkpoints are technically available for separately authorized later studies.\n'
    else:
        review += 'Scientific verdict: full-backbone trainability/input identity/recovery are supported by existing gates. New visual accuracy, fusion benefit and seed stability remain unknown until all held-out analyses complete. No superiority conclusion is drawn from GPU utilization.\n'
        put('PHASE1_FUSION_RESULTS.md', '# F2-C results — PENDING\n\n15 C-only F2 models will use inner-held-out C probabilities and the25 existing matched sensor models. No B or A_r fit is scheduled.\n')
    review += '\nArtifacts remain in the original Phase1 execution directory; C-only execution receipts, status and final metrics are under this revision. Original configurations and selected/checkpointed weights are preserved.\n'
    put('PHASE1_EXECUTIVE_REVIEW.md', review)


def finalize():
    assert len(completed()) == 75
    cohort = read(EVIDENCE/'PHASE1_INPUT_IDENTITY_MANIFEST.json')
    keys = [r['sample_id'] for r in cohort]
    y = np.array([r['failure'] for r in cohort])
    banks, scores, fold_scores = {}, [], []
    for seed in configuration()['seeds']:
        all_rows = []
        for outer in range(5):
            rows = evaluate_fold(seed, outer, ARM)
            all_rows.extend(rows)
            for kind in ['visual', 'sensor', 'fused']:
                fold_scores.append({'seed': seed, 'outer_fold': outer, 'kind': kind,
                    **metrics([r['failure'] for r in rows], [r['p_'+kind] for r in rows])})
        lookup = aligned_keys(all_rows, keys)
        rows = [lookup[key] for key in keys]
        banks[seed] = {kind: np.array([r['p_'+kind] for r in rows]) for kind in ['visual', 'sensor', 'fused']}
        for kind in banks[seed]:
            scores.append({'seed': seed, 'kind': kind, **metrics(y, banks[seed][kind])})
        write(RUN/f'PHASE1_C_ONLY_POOLED_SEED{seed}.json', rows)
    groups = sorted({r['recording_id'] for r in cohort})
    indices = [np.array([i for i,r in enumerate(cohort) if r['recording_id']==g]) for g in groups]
    rng = np.random.default_rng(20261026)
    draws = {k: [] for k in ['visual_AP', 'fusion_AP', 'visual_AUROC', 'fusion_AUROC', 'F2_minus_sensor_AP']}
    for _ in range(2000):
        ix = np.concatenate([indices[i] for i in rng.integers(len(indices), size=len(indices))])
        if len(np.unique(y[ix])) < 2:
            continue
        for name, kind, function in [('visual_AP','visual',average_precision_score), ('fusion_AP','fused',average_precision_score),
                ('visual_AUROC','visual',roc_auc_score), ('fusion_AUROC','fused',roc_auc_score)]:
            draws[name].append(float(np.mean([function(y[ix], banks[seed][kind][ix]) for seed in configuration()['seeds']])))
        draws['F2_minus_sensor_AP'].append(float(np.mean([average_precision_score(y[ix],banks[s]['fused'][ix])-
            average_precision_score(y[ix],banks[s]['sensor'][ix]) for s in configuration()['seeds']])))
    uncertainty = {k: {'bootstrap_mean':float(np.mean(v)), 'lower95':float(np.quantile(v,.025)),
                       'upper95':float(np.quantile(v,.975)), 'valid_draws':len(v)} for k,v in draws.items()}
    stability = {kind:{'AP_mean':float(np.mean([r['AP'] for r in scores if r['kind']==kind])),
                       'AP_sample_SD':float(np.std([r['AP'] for r in scores if r['kind']==kind],ddof=1))}
                 for kind in ['visual','fused']}
    final = {'pooled':scores,'fold_metrics':fold_scores,'seed_stability':stability,'recording_bootstrap':uncertainty,
        'scope':'Recording draws shared across fixed seeds; conditional on fitted models; folds/seeds are not independent observations',
        'cohort_actions':4530,'failure_positive':509,'C_fits':75,'epochs_per_fit':20,'B_comparison_performed':False}
    write(RUN/'PHASE1_C_ONLY_FINAL_METRICS.json', final)
    text = '# F2-C fusion results — COMPLETE\n\n'
    text += '| Seed | Branch | Pooled AP | AUROC | Brier | Log loss | Prevalence |\n|---|---|---:|---:|---:|---:|---:|\n'
    for r in scores:
        text += f"| {r['seed']} | {r['kind']} | {r['AP']:.6f} | {r['AUROC']:.6f} | {r['Brier']:.6f} | {r['log_loss']:.6f} | {r['prevalence']:.6f} |\n"
    text += '\nSeed stability and recording uncertainty:\n\n```json\n'+json.dumps({'seed_stability':stability,'recording_bootstrap':uncertainty},indent=2)+'\n```\n'
    text += '\nF2-C was fitted separately for each seed/outer fold on the corresponding four inner OOF probability banks. Sensor models are matched and reused. Outer labels selected no checkpoint or fusion coefficient. Per-fold metrics, keyed pooled predictions and F2 coefficients remain available. Historical F2 AP0.4472985514 is context from a different protocol; no new B comparison or robustness claim is made.\n'
    put('PHASE1_FUSION_RESULTS.md', text)
    return final
