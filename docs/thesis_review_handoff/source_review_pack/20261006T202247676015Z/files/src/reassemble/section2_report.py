"""Paired clean-fusion comparison and a self-contained A–V research handoff."""
import json
from pathlib import Path
import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score
from .section1_report import METRICS, metrics, table
from .section1b import write_json

MODELS = ['U1', 'U2', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6']
NAMES = dict(zip(MODELS, ['statistical sensors', 'RT-DETR', 'uniform late', 'learned static late',
                         'feature concatenation', 'process gate', 'quality gate', 'process + quality gate']))
PAIRS = [('F1', 'U1'), ('F2', 'U1'), ('F3', 'U1'), ('F4', 'F2'), ('F5', 'F2'), ('F6', 'F2'), ('F6', 'U1')]
EXTRA_PAIRS = [('F6', 'F4'), ('F6', 'F5')]
ABLATIONS = {'F4': ['action_permuted', 'action_zero'], 'F5': ['quality_neutral'],
             'F6': ['action_permuted', 'action_zero', 'quality_neutral']}


def weight_summary(w):
    return {'visual_mean': float(w[:, 0].mean()), 'visual_std': float(w[:, 0].std()),
            'sensor_mean': float(w[:, 1].mean()), 'sensor_std': float(w[:, 1].std()),
            'entropy_mean': float(-(w * np.log(np.clip(w, 1e-12, 1))).sum(1).mean()),
            'visual_quantiles_05_25_50_75_95': np.quantile(w[:, 0], [.05, .25, .5, .75, .95]).tolist(), 'n': len(w)}


def assess(config, frame):
    from .section2 import progress
    run = Path(config['run_dir'])
    out = run / 'assessment'
    if (out / 'results.json').exists():
        return
    out.mkdir(exist_ok=True)
    with np.load(run / 'predictions/oof.npz') as z:
        predictions = {k: z[k] for k in z.files}
    y, fold = predictions['y'], predictions['fold']
    point = np.stack([metrics(y, predictions[m + '_p'], predictions[m + '_hard']) for m in MODELS])
    abkeys = [(m, a) for m, names in ABLATIONS.items() for a in names]
    abpoint = np.array([[roc_auc_score(y, predictions[m + '_' + a + '_p']),
                         average_precision_score(y, predictions[m + '_' + a + '_p'])] for m, a in abkeys])
    groups, gi = np.unique(frame.recording_id, return_inverse=True)
    rng = np.random.default_rng(config['seed'] + 50000)
    boot, abboot = [], []
    for b in range(config['bootstrap_replicates']):
        w = np.bincount(rng.integers(len(groups), size=len(groups)), minlength=len(groups))[gi]
        if not w[y == 1].sum() or not w[y == 0].sum():
            continue
        boot.append(np.stack([metrics(y, predictions[m + '_p'], predictions[m + '_hard'], w) for m in MODELS]))
        abboot.append([[roc_auc_score(y, predictions[m + '_' + a + '_p'], sample_weight=w),
                        average_precision_score(y, predictions[m + '_' + a + '_p'], sample_weight=w)] for m, a in abkeys])
        if (b + 1) % 250 == 0:
            progress(config, f'Paired recording bootstrap {b+1}/{config["bootstrap_replicates"]}')
    boot, abboot = np.stack(boot), np.asarray(abboot)
    def interval(estimate, values):
        low, high = np.quantile(values, [.025, .975], axis=0)
        return {'estimate': float(estimate), 'lower_95': float(low), 'upper_95': float(high)}
    scores = {m: {metric: interval(point[j, k], boot[:, j, k]) for k, metric in enumerate(METRICS)} for j, m in enumerate(MODELS)}
    paired = {}
    for a, b in PAIRS + EXTRA_PAIRS:
        i, j = MODELS.index(a), MODELS.index(b)
        values = boot[:, i] - boot[:, j]
        paired[a + '-' + b] = {metric: interval(point[i, k] - point[j, k], values[:, k]) for k, metric in enumerate(METRICS)}
        if a in ['F4', 'F5', 'F6'] and b == 'F2':
            paired[a + '-' + b]['AUPRC']['simultaneous_lower_95_three_gates'] = float(np.quantile(values[:, 1], .025 / 3))
    folds = {m: [] for m in MODELS}
    seeds = {}
    for m in MODELS:
        for k in range(5):
            ix = fold == k
            values = metrics(y[ix], predictions[m + '_p'][ix], predictions[m + '_hard'][ix])
            folds[m].append(dict(zip(METRICS, map(float, values))))
        if m + '_seed_p' in predictions:
            seed_values = []
            for p in predictions[m + '_seed_p']:
                seed_values.append({'AUROC': float(roc_auc_score(y, p)), 'AUPRC': float(average_precision_score(y, p))})
            seeds[m] = {'seed_metrics': seed_values, 'AUROC_std': float(np.std([v['AUROC'] for v in seed_values])),
                        'AUPRC_std': float(np.std([v['AUPRC'] for v in seed_values])),
                        'mean_sample_probability_std': float(predictions[m + '_seed_p'].std(0).mean())}
    weights, ablations = {}, {}
    for m in ['F4', 'F5', 'F6']:
        w = predictions[m + '_weights']
        weights[m] = {'all': weight_summary(w),
                      'by_action': {a: weight_summary(w[(frame.action == a).to_numpy()]) for a in config['actions']},
                      'by_fold': {str(k): weight_summary(w[fold == k]) for k in range(5)},
                      'by_recording': {g: weight_summary(w[(frame.recording_id == g).to_numpy()]) for g in groups},
                      'by_outcome_descriptive': {str(k): weight_summary(w[y == k]) for k in [0, 1]},
                      'mean_seed_weight_std': float(predictions[m + '_seed_weights'][:, :, 0].std(0).mean())}
    for index, (m, a) in enumerate(abkeys):
        j = MODELS.index(m)
        change = np.abs(predictions[m + '_' + a + '_weights'][:, 0] - predictions[m + '_weights'][:, 0])
        ablations[m + ':' + a] = {'mean_absolute_visual_weight_change': float(change.mean()),
                                  'max_absolute_visual_weight_change': float(change.max()),
                                  'ablated_AUROC': float(abpoint[index, 0]), 'ablated_AUPRC': float(abpoint[index, 1]),
                                  'ablated_minus_clean': {metric: interval(abpoint[index, k] - point[j, k], abboot[:, index, k] - boot[:, j, k]) for k, metric in enumerate(METRICS[:2])}}
    cost = {}
    details = [json.loads((run / 'predictions' / f'outer{k}.json').read_text()) for k in range(5)]
    for m in ['F3', 'F4', 'F5', 'F6']:
        fits = [d['models'][m]['final_fits'] for d in details]
        cost[m] = {'parameters_per_seed_by_fold': [f[0]['parameters'] for f in fits],
                   'final_training_seconds': sum(v['training_seconds'] for f in fits for v in f),
                   'inner_search_training_seconds': sum(d['models'][m]['inner_training_seconds'] for d in details),
                   'three_seed_inference_microseconds_per_row_by_fold': [1e6 * sum(v['inference_batch_seconds'] / v['inference_batch_rows'] for v in f) for f in fits],
                   'selected_config_by_fold': [d['models'][m]['selected_config'] for d in details]}
    # F2 is an exact reused reference, not a fresh independent replication.
    previous = json.loads((Path(config['section1b_run']) / 'assessment/results.json').read_text())
    reproduction = all(abs(scores['F2'][m]['estimate'] - previous['metrics']['minimal_late_fusion'][m]['estimate']) < 1e-12 for m in METRICS)
    assert reproduction
    qualifying, criteria = [], {}
    for m in ['F4', 'F5', 'F6']:
        d = paired[m + '-F2']
        checks = {'meaningful_AP_gain': d['AUPRC']['estimate'] >= .01,
                  'simultaneous_AP_lower_positive': d['AUPRC']['simultaneous_lower_95_three_gates'] > 0,
                  'AUROC_noninferiority': d['AUROC']['lower_95'] > -.01,
                  'fold_coherence': sum(folds[m][k]['AUPRC'] > folds['F2'][k]['AUPRC'] for k in range(5)) >= 3}
        if m in ['F4', 'F6']:
            checks['action_changes_weights'] = ablations[m + ':action_permuted']['mean_absolute_visual_weight_change'] >= .01
        if m in ['F5', 'F6']:
            checks['quality_changes_weights'] = ablations[m + ':quality_neutral']['mean_absolute_visual_weight_change'] >= .01
        criteria[m] = checks
        if all(checks.values()):
            qualifying.append(m)
    chosen = next((m for m in ['F4', 'F5'] if m in qualifying), None)
    if 'F6' in qualifying and (chosen is None or (paired['F6-' + chosen]['AUPRC']['estimate'] >= .01 and paired['F6-' + chosen]['AUPRC']['lower_95'] > 0 and paired['F6-' + chosen]['AUROC']['lower_95'] > -.01)):
        chosen = 'F6'
    if chosen:
        classification = {'F4': 'B. PROCESS GATING ADDS VALUE', 'F5': 'C. QUALITY GATING ADDS VALUE', 'F6': 'D. PROCESS + QUALITY GATING ADDS VALUE'}[chosen]
        decision = 'SECTION 3 GO — ADAPTIVE FUSION WARRANTS ROBUSTNESS TESTING'
    else:
        bounded = all(paired[m + '-F2']['AUPRC']['upper_95'] <= .01 for m in ['F4', 'F5', 'F6'])
        classification = 'E. COMPLEXITY DOES NOT HELP' if bounded else 'A. SIMPLE FUSION SUFFICIENT'
        decision = 'SECTION 3 GO — STATIC FUSION IS THE APPROPRIATE ROBUSTNESS REFERENCE'
    # Recommendation is bounded; an unsupported gate may enter as a mechanism control.
    adaptive_reference = chosen or max(['F4', 'F5', 'F6'], key=lambda m: scores[m]['AUPRC']['estimate'])
    result = {'metrics': scores, 'paired': paired, 'folds': folds, 'seed_variability': seeds,
              'ablations': ablations, 'cost': cost, 'qualification_checks': criteria,
              'qualifying_gates': qualifying, 'chosen_gate': chosen, 'adaptive_mechanism_reference': adaptive_reference,
              'classification': classification, 'section3_decision': decision, 'F2_exact_metric_reuse': reproduction,
              'bootstrap_replicates': len(boot), 'SQ3': 'NOT YET ANSWERED'}
    write_json(out / 'results.json', result)
    write_json(out / 'gate_weights.json', weights)
    write_json(out / 'selected_hyperparameters.json', {str(d['fold']): {m: {'selected_config': v['selected_config'], 'settings': v['settings'], 'inner_AP': v['inner_AP'], 'threshold': v['threshold']} for m, v in d['models'].items()} for d in details})
    report(config, result, weights, out)


def report(config, r, weights, out):
    run = Path(config['run_dir'])
    implementation = json.loads((run / 'implementation.json').read_text())
    fmt = lambda x: f"{x['estimate']:.4f} [{x['lower_95']:.4f}, {x['upper_95']:.4f}]"
    parts = ['# SECTION 2 — Clean fusion handoff\n\n**' + r['classification'] + '**\n\n']
    def section(letter, title, text):
        parts.append('## ' + letter + '. ' + title + '\n\n' + text + '\n\n')
    section('A', 'Scientific question', 'Given demonstrated visual/sensor complementarity, which small fusion strategy exploits it, and does process/quality gating add value beyond learned static fusion? This is an **adaptive exploratory study**: Sections 1 and 1B informed this design using these same folds. No new untouched dataset exists. Nested fitting prevents training leakage, not study-selection bias.')
    section('B', 'Evidence entering Section 2', 'Section 1B returned FUSION GO: sensor AUROC/AUPRC 0.7793/0.4294 increased to 0.7950/0.4473 with static logistic stacking; paired gains were 0.0156 [0.0060, 0.0255] and 0.0179 [0.0086, 0.0283]. RT-DETR rescued 97 sensor-missed failures across 61 recordings. The sensor conditional permutation p-value was 0.05 for both metrics (19 nulls). The old standalone visual intersection-union gate was not required. Section 1 and 1B remain frozen.')
    section('C', 'Why PatchTST was not the primary sensor branch', 'The tested PatchTST achieved about AUROC 0.7054 / AUPRC 0.2416, substantially below statistical sensors (0.7793/0.4294), with paired evidence favoring statistics. It remains the bounded SQ1 negative result for the tested temporal Transformer. No further epochs, tuning or substitution occurred; this says nothing universal about all temporal Transformers.')
    section('D', 'Why decision-level gating was adopted', 'The selected sensor model is logistic regression on engineered statistics. Inventing a deep sensor embedding for the primary gate would change that validated model. Decision-level gating instead preserves both calibrated branch models, modularity and interpretable modality allocation. This is a scientifically justified architecture adaptation. F3 explicitly tests feature concatenation as a separate comparator.')
    section('E', 'Evaluation protocol', 'Exactly 4,530 segments, 509 failures and 148 recordings; original five outer and four inner recording-disjoint folds, labels and grouping. No outer-test prediction or label fits any fusion parameter. F2 and final branch probabilities are reused from Section 1B. For gate hyperparameter assessment, strictly nested branch-training predictions use its saved four subfolds; at the additional depth selection uses the remaining three subfolds, with no regenerated partition. See the frozen protocol for this training-only depth. Every quality/scaling estimate uses the fitting subset. Primary metrics are AUROC and average precision (reported as AUPRC); ECE uses the original 15 equal-width probability bins. The 2,000 paired recording-cluster bootstrap replicates condition on fitted models, and seeds are not independent observations. Thresholds maximize inner-OOF balanced accuracy on 0.01–0.99, tie nearest 0.5; these threshold-training scores are not independent performance estimates.')
    section('F', 'Architecture definitions', table(['ID', 'Architecture'], [
        ['U1', 'Frozen 220 statistical features → standardized balanced logistic model; frozen C selection/calibration'],
        ['U2', 'Frozen RT-DETR backbone features → frozen fold-specific 128-dimensional head → calibrated probability'],
        ['F1', '0.5 × calibrated visual probability + 0.5 × calibrated sensor probability; training-only threshold'],
        ['F2', 'Exact Section 1B two-probability L2 logistic stacker, C=1; three scalar parameters'],
        ['F3', 'Frozen visual 128-vector + unchanged 220 statistics; separate 128 projections; LayerNorm; 256→32/64→1; trained fusion layers only'],
        ['F4', 'Action one-hot + availability → 8/16-unit MLP → masked softmax → weighted calibrated branch logits'],
        ['F5', 'Audited quality + availability → same small gate → weighted calibrated branch logits'],
        ['F6', 'Action + quality + availability → same small gate → weighted calibrated branch logits']]) + '\nGates have no context-to-classifier bypass, final bias or post-gate calibration. Three seed probabilities are averaged; reported weights average seed weights, so the ensemble probability is not exactly sigmoid of the mean-weight logit. All clean masks are [1,1]. Quality consists of six hand-camera measures and six measures for each of five sensor streams; no labels, IDs, annotation text or audio features. Quality may also reflect process/content. Constant quality fields: `' + ', '.join(implementation['constant_quality_fields']) + '`.')
    section('G', 'Hyperparameters and seeds', 'Config: `configs/reassemble/section2.json`. Exactly two predefined concatenation configurations and two gate configurations, shared across F4–F6; select by mean four-inner-fold AP of three-seed mean probabilities. Seeds: ' + str(config['seeds']) + '. F3 candidates: `' + json.dumps(config['concat_configs']) + '`. Gate candidates: `' + json.dumps(config['gate_configs']) + '`. Batch size 128, AdamW, gradient norm 1; F3 dropout 0.1 and class-balanced BCE, gates unweighted BCE. F3 alone receives sigmoid calibration fitted to selected inner-OOF raw logits for each seed. Frozen branch epochs/C grids and 16 BLAS threads are unchanged. Final configuration selections and threshold values are in `assessment/selected_hyperparameters.json`.\n\n' + table(['Model', 'Pooled AUROC by seed', 'Pooled AUPRC by seed', 'AP seed std'], [[m, ', '.join(f"{x['AUROC']:.4f}" for x in d['seed_metrics']), ', '.join(f"{x['AUPRC']:.4f}" for x in d['seed_metrics']), f"{d['AUPRC_std']:.4f}"] for m, d in r['seed_variability'].items()]))
    section('H', 'Clean results', table(['Model'] + METRICS, [[m + ' ' + NAMES[m]] + [fmt(r['metrics'][m][metric]) for metric in METRICS] for m in MODELS]))
    section('I', 'Paired comparisons', 'Differences are first model minus reference; lower Brier/ECE is better. Marginal paired 95% intervals:\n\n' + table(['Comparison'] + METRICS, [[a + '−' + b] + [fmt(r['paired'][a + '-' + b][metric]) for metric in METRICS] for a, b in PAIRS]) + '\nAdaptive claims additionally require the predeclared simultaneous Bonferroni percentile lower bound across three gates, AP gain ≥0.01, ≥3 positive folds, and AUROC lower 95% >−0.01. These exploratory criteria do not erase prior same-cohort selection.\n\n' + table(['Gate vs F2', 'Simultaneous AP lower', 'Checks'], [[m, f"{r['paired'][m+'-F2']['AUPRC']['simultaneous_lower_95_three_gates']:.4f}", json.dumps(r['qualification_checks'][m])] for m in ['F4', 'F5', 'F6']]))
    section('J', 'Fold-level consistency', table(['Model', 'Fold 0 AUROC/AP', 'Fold 1', 'Fold 2', 'Fold 3', 'Fold 4'], [[m] + [f"{v['AUROC']:.4f}/{v['AUPRC']:.4f}" for v in r['folds'][m]] for m in MODELS]))
    weight_rows = []
    for m in ['F4', 'F5', 'F6']:
        for name, w in [('all', weights[m]['all'])] + list(weights[m]['by_action'].items()) + [('fold ' + k, v) for k, v in weights[m]['by_fold'].items()]:
            weight_rows.append([m, name, f"{w['visual_mean']:.4f} ± {w['visual_std']:.4f}", f"{w['sensor_mean']:.4f} ± {w['sensor_std']:.4f}", f"{w['entropy_mean']:.4f}", ', '.join(f'{v:.3f}' for v in w['visual_quantiles_05_25_50_75_95'])])
    section('K', 'Gate-weight behaviour', table(['Gate', 'Subset', 'Visual mean ± std', 'Sensor mean ± std', 'Entropy (nats)', 'Visual 5/25/50/75/95%'], weight_rows) + '\nPer-recording and descriptive success/failure distributions are saved in `assessment/gate_weights.json`; per-sample and per-seed weights in `predictions/oof.npz`, aligned to frozen cohort row order. Entropy describes modality allocation, not predictive uncertainty. Success/failure differences are not causal.')
    def ablation_table(keys):
        return table(['Gate/context intervention', 'Mean |Δ visual weight|', 'Δ AUROC [95%]', 'Δ AP [95%]'], [[key, f"{r['ablations'][key]['mean_absolute_visual_weight_change']:.4f}", fmt(r['ablations'][key]['ablated_minus_clean']['AUROC']), fmt(r['ablations'][key]['ablated_minus_clean']['AUPRC'])] for key in keys])
    section('L', 'Process-context ablation', 'One fixed action permutation within each outer test fold, plus all-zero action; signals, quality, availability and trained parameters unchanged. Differences are ablated minus clean; negative values favor genuine context. These are context interventions, not signal-corruption experiments. A single permutation is a sensitivity diagnostic, not a permutation significance test. Zero one-hot context is outside the training support.\n\n' + ablation_table([key for key in r['ablations'] if 'action_' in key]))
    section('M', 'Quality-context ablation', 'Quality variables replaced by each final fit’s training means (zeros after its own normalization); availability and action unchanged. Differences are ablated minus clean. This measures clean-context sensitivity, not verified reliability awareness.\n\n' + ablation_table([key for key in r['ablations'] if 'quality_' in key]))
    section('N', 'Complexity versus benefit', 'Fusion parameters only: F1=0 and F2=3. U1 has 221 logistic coefficients/intercept plus calibration; U2 has 114,945 trained head parameters plus calibration; the shared frozen backbone is additional. F3–F6 costs below exclude shared feature extraction/branch inference. Neural deployment uses three models, so multiply per-seed parameter counts by three. Timing is hardware-specific, GPU warm-batch inference, not online end-to-end latency; normalization and transfer excluded. Device: `' + implementation['device'] + '`.\n\n' + table(['Model', 'Parameters/seed by fold', 'Inner training seconds', 'Final training seconds', '3-seed inference µs/row by fold'], [[m, str(d['parameters_per_seed_by_fold']), f"{d['inner_search_training_seconds']:.1f}", f"{d['final_training_seconds']:.1f}", ', '.join(f'{v:.2f}' for v in d['three_seed_inference_microseconds_per_row_by_fold'])] for m, d in r['cost'].items()]) + '\nSeed variability, calibration and fold consistency accompany point rankings. Reused F2 predictions require no new fitting. Additional nested branch generation is shared preprocessing, retained separately in inputs and execution log.')
    section('O', 'Failed attempts and corrections', 'See `failures_and_corrections.md` and final validation for every failed attempt or correction. Previous Section 1B BLAS mismatch remains in its original run; original 16-thread execution is retained here. No unsuccessful artifact is deleted, no outcome-driven architecture expansion is permitted, and no frozen evidence is overwritten.')
    explanation = ('The selected adaptive model passes the predeclared incremental criteria; clean context sensitivity supports functional allocation, not causal reliability.' if r['chosen_gate'] else 'No gate satisfies all predeclared incremental criteria. Prefer static fusion for this tested budget. If intervals admit a meaningful gain, this is a simplicity decision under uncertainty, not proof of equivalence or proof that all adaptive architectures fail.')
    section('P', 'Interpretation', '**' + r['classification'] + '**. ' + explanation + ' The exact Section 1B F2 metrics reproduce by reuse; that is a provenance/parity result, not new independent confirmation. A convex weighted-logit gate is a constrained family: failure to beat F2 does not rule out every form of adaptive fusion.')
    section('Q', 'Claims allowed', 'Frozen visual and statistical-sensor branches carry complementary information on this cohort. Static fusion retains its previously demonstrated incremental value. Model differences, context sensitivity and gate allocation may be described with their paired uncertainty. “Adaptive fusion improved clean predictive performance” is allowed only for a gate satisfying the stated incremental criteria. Restrict claims to the tested configurations, folds and cohort.')
    section('R', 'Claims NOT allowed', 'No claim of robustness to degraded modalities, reliability awareness, audio benefit, unseen-site/object generalization, causal process diagnosis, universal architectural superiority or independent confirmation. Quality can encode process/content. A non-significant interval does not establish equivalence. No raw-accuracy headline, no treating seeds as independent sample size, no deployable oracle claim.')
    section('S', 'SQ2 answer at this stage', r['classification'] + '. ' + explanation)
    section('T', 'SQ3 status', '**NOT YET ANSWERED**. No signal corruption, modality dropout, missing-modality experiment or audio analysis was run. Clean performance and context ablations cannot establish robustness.')
    section('U', 'Recommendation for Section 3', 'After researcher review, carry at most U1 statistical sensors, F2 learned static late fusion, and ' + r['adaptive_mechanism_reference'] + ' (' + NAMES[r['adaptive_mechanism_reference']] + ') into controlled mechanism testing. ' + ('The adaptive reference met the clean incremental criteria.' if r['chosen_gate'] else 'The adaptive reference is only the strongest tested gate by clean AP for mechanism testing; it is not declared superior to F2.') + ' Do not carry every architecture. Concatenation is optional only with a separate scientific rationale. This report recommends a future scope; no Section 3 experiment starts automatically.')
    section('V', 'Provenance', 'Run: `' + str(run) + '`. Config: `configs/reassemble/section2.json`; predeclared protocol: `docs/reassemble/SECTION_2_PROTOCOL.md`. Implementation commit: `' + implementation['git_commit'] + '`. Section 1 evidence `08d498d`; Section 1B implementation `06f93d1`, final evidence `4089b02`. Split SHA256: `' + implementation['split_sha256'] + '`. Input quality/feature/source identities are in `implementation.json` and unchanged prior manifests. Branch matrix hashes and all new output hashes are in `output_manifest.json`; training-only branches and fold memberships in `inputs/`; individual seed fits/checkpoints in `fits/`; final OOF scores/weights/ablations in `predictions/`; complete metrics and per-recording weights in `assessment/`. Final preservation, tests and environment checks: `validation.json`. IDE continuation: `docs/reassemble/SECTION_2_CONTINUATION.md`. No external master Reasoning Record was modified. The final result commit is discoverable with `git log -1 --format=%H -- artifacts/reassemble/reports/SECTION_2_FUSION_HANDOFF.md`.')
    parts.append(r['section3_decision'] + '\n')
    text = ''.join(parts)
    with (out / 'SECTION_2_FUSION_HANDOFF.md').open('x') as f:
        f.write(text)
    with Path('artifacts/reassemble/reports/SECTION_2_FUSION_HANDOFF.md').open('x') as f:
        f.write(text)
