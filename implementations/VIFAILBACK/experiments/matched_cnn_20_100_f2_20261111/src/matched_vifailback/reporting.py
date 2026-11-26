"""Evidence-driven reports: incomplete work stays incomplete; no training side effects."""
from __future__ import annotations
from pathlib import Path
import json
import os
import psutil
import numpy as np
from .common import (STUDY, REPO, PROJECT, protocol, read_json, write_json,
                     destination, fit_root, relative, utc, git_commit, sha256, resolve, signature)

REPORTS = STUDY / '14_final_research_reports'


def text_file(path, text):
    path = destination(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f'.writing.{os.getpid()}')
    temporary.write_text(text.rstrip()+'\n'); os.replace(temporary, path)


def table(headers, rows):
    esc = lambda x: str(x).replace('|', '/').replace('\n', ' ')
    return '\n'.join(['|'+'|'.join(headers)+'|', '|'+'|'.join('---' for _ in headers)+'|']+
                     ['|'+'|'.join(esc(x) for x in row)+'|' for row in rows])


def number(value, places=6):
    return f'{value:.{places}f}' if isinstance(value, (int, float)) else str(value if value is not None else 'NOT AVAILABLE')


def optional(path):
    return read_json(path) if Path(path).exists() else {'status': 'NOT YET RECORDED'}


def runtime_state():
    result = {}
    for name in ['CPU_CONTROLLER_STATUS', 'GPU_CONTROLLER_STATUS', 'WATCH_STATUS', 'GPU_TELEMETRY']:
        value = optional(STUDY / '13_reproducibility/runtime' / (name+'.json'))
        if 'pid' in value and 'create_time' in value:
            try:
                process = psutil.Process(value['pid'])
                value['same_process_alive'] = process.is_running() and process.status() != psutil.STATUS_ZOMBIE and abs(process.create_time()-value['create_time']) < .001
            except psutil.Error:
                value['same_process_alive'] = False
        result[name] = value
    return result


def fit_inventory(p, runtime=None, admission=None):
    runtime = runtime or runtime_state(); admission = admission or optional(STUDY/'01_protocol_and_source_evidence/RESOURCE_ADMISSION.json')
    rows = []
    for condition in p['epochs']:
        seeds = [p['pilot']['seed']] if condition.endswith('100') else p['seeds']
        jobs = [p['pilot']['base_job_id']] if condition.endswith('100') else [f'outer{k}_{role}' for k in p['outer_folds'] for role in ['final','inner0','inner1','inner2']]
        for seed in seeds:
            for job in jobs:
                root = fit_root(condition, seed, job); receipt = optional(root/'COMPLETE.json')
                history = read_json(root/'HISTORY.json') if (root/'HISTORY.json').exists() else []
                progress = optional(root/'BATCH_PROGRESS.json')
                complete = (root/'COMPLETE.json').exists()
                state = runtime['GPU_CONTROLLER_STATUS' if condition.startswith('FULL') else 'CPU_CONTROLLER_STATUS']
                active = state.get('condition') == condition and state.get('seed') == seed and state.get('fit_id') == job
                alive = active and state.get('same_process_alive', False)
                deferred = condition.endswith('20') and seed in admission.get('deferred_twenty_epoch_seeds', [])
                if complete: status = 'COMPLETE'
                elif alive and state.get('stage') == 'TRAINING': status = 'RUNNING'
                elif active and state.get('stage') in ['FAILED', 'WAITING_RESOURCES']: status = 'BLOCKED'
                elif history or 'epoch' in progress: status = 'PARTIAL'
                elif deferred: status = 'RESOURCE DEFERRED'
                elif admission.get('status') == 'ADMITTED': status = 'QUEUED'
                else: status = 'AWAITING RESOURCE ADMISSION'
                selected_epoch = receipt.get('selected_epoch')
                if selected_epoch is None and history:
                    selected_epoch = min(history, key=lambda h: (-h['V_macro_AP'], h.get('V_weighted_BCE_same_T_positive_weight', h.get('V_BCE', float('inf'))), h['epoch']))['epoch']
                selected = next((h for h in history if h['epoch'] == selected_epoch), {})
                rows.append({'condition': condition, 'seed': seed, 'fit_id': job, 'outer': int(job[5]),
                             'configured_epochs': p['epochs'][condition], 'executed_epochs': receipt.get('executed_epochs', len(history)),
                             'selected_epoch': selected_epoch, 'complete': complete, 'status': status,
                             'controller_stage': state.get('stage') if active else None,
                             'controller_process_alive': bool(alive), 'batch_progress': progress if 'epoch' in progress else None,
                             'training_seconds': receipt.get('training_seconds', sum(h.get('training_seconds', 0.) for h in history) if history else None),
                             'new_training_seconds': receipt.get('new_training_seconds'),
                             'historical_training_and_validation_seconds': receipt.get('historical_training_and_validation_seconds'),
                             'validation_seconds': receipt.get('validation_seconds', sum(h.get('validation_seconds', 0.) for h in history) if history else None),
                             'postfit_inference_seconds': receipt.get('postfit_inference_seconds'),
                             'optimizer_updates': sum(h.get('optimizer_updates', 0) for h in history),
                             'gpu_peak_bytes': max((h.get('peak_GPU_bytes', 0) for h in history), default=0),
                             'GPU_utilization_percent': [h.get('GPU_utilization_percent') for h in history if h.get('GPU_utilization_percent') is not None],
                             'history': relative(root/'HISTORY.json'), 'history_sha256': sha256(root/'HISTORY.json') if history else None,
                             'configuration': relative(root/'CONFIG.json'),
                             'checkpoint': receipt.get('best_checkpoint_path', relative(root/'BEST_MODEL.pt')),
                             'final_checkpoint': receipt.get('final_checkpoint_path', relative(root/f"FINAL_EPOCH{p['epochs'][condition]}.pt")),
                             'predictions': relative(root/'predictions.json'), 'outer_predictions': relative(root/'OUTER_PREDICTIONS.json') if condition.endswith('100') else relative(root/'predictions.json'),
                             'completion_receipt': relative(root/'COMPLETE.json'),
                             'best_checkpoint_sha256': receipt.get('best_checkpoint_sha256'), 'final_checkpoint_sha256': receipt.get('final_checkpoint_sha256'),
                             'best_V_macro_AP': selected.get('V_macro_AP'), 'last_V_macro_AP': history[-1]['V_macro_AP'] if history else None,
                             'last_minus_best_V_macro_AP': history[-1]['V_macro_AP']-selected['V_macro_AP'] if selected else None,
                             'validation_deteriorated_after_selected_epoch': bool(history and selected and history[-1]['V_macro_AP'] < selected['V_macro_AP']),
                             'reused': bool(receipt.get('reused', False))})
    return rows


def learning_curves(fits):
    """Standalone figures cached by history content; partial curves stay partial."""
    result = []
    for row in fits:
        if not row['history_sha256']:
            continue
        folder = STUDY/'12_learning_curves'/row['condition']/f"seed{row['seed']}"/row['fit_id']
        identity = signature({'history': row['history_sha256'], 'selected_epoch': row['selected_epoch']})
        stamp = folder/'CURVE_IDENTITY.json'; figure = folder/'learning_curve.png'
        if not stamp.exists() or read_json(stamp).get('identity') != identity or not figure.exists():
            cache = destination(STUDY/'13_reproducibility/runtime/matplotlib_cache')
            cache.mkdir(parents=True, exist_ok=True)
            os.environ['MPLCONFIGDIR'] = str(cache)
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            history = read_json(resolve(row['history'])); epochs = [h['epoch'] for h in history]
            fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
            for key, label, fallback in [('T_weighted_BCE','Training weighted BCE','T_loss'), ('V_weighted_BCE_same_T_positive_weight','Validation weighted BCE','V_BCE')]:
                values = [h.get(key, h.get(fallback, np.nan)) for h in history]
                axes[0].plot(epochs, values, label=label)
            axes[1].plot(epochs, [h['V_macro_AP'] for h in history], label='Validation macro AP')
            for ax in axes:
                ax.axvline(row['selected_epoch'], color='black', linestyle='--', linewidth=1, label='Selected epoch')
                ax.set_xlabel('Executed epoch'); ax.grid(alpha=.2); ax.legend(fontsize=8)
            axes[0].set_ylabel('Weighted BCE'); axes[1].set_ylabel('Macro AP')
            fig.suptitle(f"{row['condition']} / seed {row['seed']} / {row['fit_id']} / {row['status']}")
            fig.tight_layout(); destination(figure).parent.mkdir(parents=True, exist_ok=True)
            temporary = figure.with_name('learning_curve.writing.png'); fig.savefig(temporary, dpi=150); plt.close(fig); os.replace(temporary, figure)
            write_json(stamp, {'identity': identity, 'history_sha256': row['history_sha256'], 'selected_epoch': row['selected_epoch']})
        result.append({'condition': row['condition'], 'seed': row['seed'], 'fit_id': row['fit_id'],
                       'figure': relative(figure), 'history': row['history'],
                       'selected_epoch': row['selected_epoch'], 'executed_epochs': row['executed_epochs'],
                       'last_minus_best_V_macro_AP': row['last_minus_best_V_macro_AP'],
                       'interpretation': 'Validation deteriorated by the last observed epoch; this alone does not prove outer-test overfitting.' if row['validation_deteriorated_after_selected_epoch'] else 'No lower last-epoch macro AP than the selected epoch.',
                       'complete': row['complete']})
    write_json(STUDY/'12_learning_curves/INDEX.json', result)
    return result


def compact_admission(admission):
    keys = ['status','admitted_twenty_epoch_seeds','deferred_twenty_epoch_seeds','full_fit_count','full_fit_epoch_count','projected_additional_bytes','projected_free_after_bytes','estimated_full100_hours','estimated_full20_hours_per_seed','estimated_total_GPU_process_hours','estimate_uncertainty','selection_basis']
    return {k: admission[k] for k in keys if k in admission}


def format_interval(value):
    if not value:
        return 'UNTESTED / insufficient support'
    return f"delta {value['difference']:+.6f}, 95% [{value['lower95']:+.6f}, {value['upper95']:+.6f}]; {value['interpretation']}"


def answer_fusion_contrast(results, contrast):
    rows = []
    for r in results.get('cohorts', []):
        q = r.get('paired_contrasts', {}).get(contrast, {}).get('macro_AP')
        if q:
            rows.append(f"{r['condition']}, seed {r['seed']}, fold {r['outer']}: {format_interval(q)}")
    return '; '.join(rows)+'.' if rows else 'UNTESTED: no complete assessment cohort yet.'


def answer_contrast(results, treatment, control, branch='visual'):
    rows = []
    for r in results.get('matched_contrasts', []):
        if r['treatment'] == treatment and r['control'] == control:
            rows.append(f"seed {r['seed']}, fold {r['fold']}: {format_interval(r[branch].get('macro_AP'))}")
    return '; '.join(rows)+'.' if rows else 'UNTESTED: no complete paired assessment yet.'


def result_tables(results, fits):
    cohorts = results.get('cohorts', [])
    observed = [r for r in fits if r['complete'] or r['executed_epochs'] or r['status'] == 'RUNNING']
    tables = {}
    tables['A'] = table(['Model','Epochs configured/executed','CNN trainable?','Seed','Fold / fit role','Best epoch','Status'],
        [[r['condition'],f"{r['configured_epochs']}/{r['executed_epochs']}",r['condition'].startswith('FULL'),r['seed'],r['fit_id'],r['selected_epoch'],r['status']] for r in observed])
    tables['B'] = table(['Model','Seed','Fold','Assessment N','Visual macro AP','Sensor LR macro AP','F2 macro AP','HGB secondary macro AP'],
        [[r['condition'],r['seed'],r['outer'],r['assessment_N']]+[number(r['metrics'][m]['macro_AP']) for m in ['visual','sensor_LR','F2','historical_HGB']] for r in cohorts])
    intervals = []
    for r in results.get('matched_contrasts', []):
        for branch in ['visual','F2']:
            q=r[branch].get('macro_AP', {})
            intervals.append([f"{r['treatment']} minus {r['control']} / {branch}",r['seed'],r['fold'],number(q.get('difference')),f"[{number(q.get('lower95'))}, {number(q.get('upper95'))}]",q.get('interpretation','INSUFFICIENT SUPPORT')])
    for r in cohorts:
        for contrast,q in r.get('paired_contrasts',{}).items():
            m=q.get('macro_AP',{})
            intervals.append([r['condition']+' / '+contrast,r['seed'],r['outer'],number(m.get('difference')),f"[{number(m.get('lower95'))}, {number(m.get('upper95'))}]",m.get('interpretation','INSUFFICIENT SUPPORT')])
    tables['C'] = table(['Comparison','Seed','Fold','Paired macro AP difference','95% interval','Interpretation'],intervals)
    cost_rows=[]
    for r in observed:
        training=r['new_training_seconds'] if r['new_training_seconds'] is not None else r['training_seconds']
        util=r['GPU_utilization_percent']
        cost_rows.append([r['condition'],r['seed'],r['fit_id'],number(training/3600 if training is not None else None),number(r['validation_seconds']/3600 if r['validation_seconds'] is not None else None),number(r['historical_training_and_validation_seconds']/3600 if r['historical_training_and_validation_seconds'] is not None else None),number(sum(util)/len(util) if util else None),number(r['gpu_peak_bytes']/1024**3),r['executed_epochs'],r['optimizer_updates']])
    tables['D'] = table(['Model','Seed','Fit','New training hours','Validation hours','Reused historical train+validation hours','GPU utilization %','Peak GPU GiB','Completed epochs','Optimizer updates'],cost_rows)
    coverage=[]
    for condition in protocol()['epochs']:
        rows=[r for r in fits if r['condition']==condition]
        counts=[sum(r['status'] in states for r in rows) for states in [['COMPLETE'],['PARTIAL','RUNNING'],['BLOCKED'],['QUEUED'],['RESOURCE DEFERRED'],['AWAITING RESOURCE ADMISSION']]]
        requirement='None for declared fit scope' if all(r['complete'] for r in rows) else 'Finish/resume declared fits; admit prospective seeds only by resource gate; F2 needs complete meta-bank and outer predictions.'
        coverage.append([condition]+counts+[requirement])
    tables['E'] = table(['Experiment','Complete','Partial / running','Blocked','Queued','Resource deferred','Awaiting admission','Exact unresolved requirement'],coverage)
    return tables


def diagnostic_tables(cohorts, tasks):
    coef=table(['Condition','Seed','Fold','Meta N','Visual coefficient','Sensor coefficient','Intercept'],
        [[r['condition'],r['seed'],r['outer'],r['meta_N'],number(r['f2_coefficients']['coefficient'][0]),number(r['f2_coefficients']['coefficient'][1]),number(r['f2_coefficients']['intercept'])] for r in cohorts if 'f2_coefficients' in r])
    ranks=table(['Condition','Seed','Fold','Calibration slope','Raw macro AP','Calibrated macro AP','AP delta','Score Spearman'],
        [[r['condition'],r['seed'],r['outer'],number(r.get('visual_identity',{}).get('calibration_slope'))]+[number(r.get('calibration_ranking',{}).get(k)) for k in ['raw_macro_AP','calibrated_macro_AP','macro_AP_delta','score_spearman']] for r in cohorts])
    stability=[]
    for condition in sorted({r['condition'] for r in cohorts}):
        rows=[r for r in cohorts if r['condition']==condition and 'f2_coefficients' in r]
        if rows:
            matrix=np.array([r['f2_coefficients']['coefficient']+[r['f2_coefficients']['intercept']] for r in rows])
            stability.append([condition,len(rows),len({r['seed'] for r in rows}),len({r['outer'] for r in rows})]+[f"[{v.min():.6f}, {v.max():.6f}]" for v in matrix.T])
    stable=table(['Condition','F2 models','Seeds','Folds','Visual coefficient range','Sensor coefficient range','Intercept range'],stability)
    detailed=table(['Condition','Seed','Fold','Method','Failure AP','Success AP','AUROC','Balanced accuracy','Macro F1','Brier','Log loss','ECE10','Confusion [0,1]'],
        [[r['condition'],r['seed'],r['outer'],m]+[number(v.get(k)) for k in ['AP_failure','AP_success','AUROC','balanced_accuracy','macro_F1','Brier','log_loss','ECE10']]+[v.get('confusion_matrix_0_1')] for r in cohorts for m,v in r['metrics'].items()])
    corrections=table(['Condition','Seed','Fold','Task','N','Sensor errors corrected by vision','Sensor correct broken by vision','Sensor errors corrected by F2','Sensor correct broken by F2'],
        [[r['condition'],r['seed'],r['outer'],r['task_id'],r['N'],r.get('sensor_errors_corrected_by_visual'),r.get('sensor_correct_broken_by_visual'),r['sensor_errors_corrected'],r['sensor_correct_broken']] for r in tasks])
    return coef,ranks,stable,detailed,corrections


def gpu_sessions():
    rows=[read_json(path) for path in sorted((STUDY/'13_reproducibility/runtime').glob('GPU_SESSION_*.json'))]
    return {'session_count':len(rows),'observed_GPU_controller_process_hours':sum(r.get('observed_process_seconds',0) for r in rows)/3600,
            'interpretation':'Observed per-process elapsed time summed once per PID/creation identity; includes decoding, validation and checkpointing. A killed process may leave an observation lower bound. It is not pure GPU kernel time.',
            'paths':[relative(path) for path in sorted((STUDY/'13_reproducibility/runtime').glob('GPU_SESSION_*.json'))]}


def generate(results=None):
    p=protocol();results=results or optional(STUDY/'11_metrics_and_statistics/CURRENT_RESULTS.json')
    runtime=runtime_state();admission=optional(STUDY/'01_protocol_and_source_evidence/RESOURCE_ADMISSION.json')
    fits=fit_inventory(p,runtime,admission);curves=learning_curves(fits);tables=result_tables(results,fits)
    write_json(STUDY/'11_metrics_and_statistics/FIT_COVERAGE.json',fits)
    cohorts=results.get('cohorts',[]);tasks=optional(STUDY/'11_metrics_and_statistics/PER_TASK_DIAGNOSTICS.json')
    tasks=tasks if isinstance(tasks,list) else []
    coef,ranks,stability,detailed,corrections=diagnostic_tables(cohorts,tasks)
    complete=[r for r in fits if r['complete']];partial=[r for r in fits if not r['complete'] and r['executed_epochs']];running=[r for r in fits if r['status']=='RUNNING']
    sessions=gpu_sessions()
    status=f"Generated {utc()}. {len(complete)} completed fits; {len(partial)} partially trained fits; {len(running)} currently running fits (PID and creation time verified); {results.get('completed_fusion_cohorts',0)} complete F2 assessment cohorts. Unfinished planned work is not a negative scientific result."
    limitations=('All predictions concern complete native episodes. Canonical task separation is verified; session/operator independence remains unknown. This is development evidence on previously examined tasks. '
        'Intervals resample task clusters conditional on fixed fitted models; they exclude model refitting, seed variability, donor selection and unmeasured session/operator effects. '
        'Intervals crossing zero establish neither improvement nor equivalence. Pooled outer scores and mean-fold metrics are distinct; seeds are never pooled as additional examples. '
        'HGB remains a separate strong historical sensor baseline; beating LR does not imply beating HGB. No quality gate is introduced.')
    def report(name,title,parts):
        text_file(REPORTS/name,'# '+title+'\n\n'+'\n\n'.join(str(part) for part in parts))
    report('01_EXECUTIVE_SUMMARY.md','ViFailback matched CNN study',[status]+[f'## Table {key}\n\n{tables[key]}' for key in 'ABCDE']+[limitations])
    report('02_DATASET_AND_SPLIT_VERIFICATION.md','Dataset and split verification',[
        f"Frozen cohort: 4,382 episodes; 3,753 failures; 629 successes; 99 canonical tasks. Native failure=1. Existing quality exclusions remain intact. Cohort SHA `{p['cohort_sha256']}`; split SHA `{p['splits_sha256']}`.",
        'First predefined outer fold 0 has 1,107 assessment episodes / 33 tasks. First inner role has T 1,430 / V 534 / C 523 / meta 788 episodes and 26 / 9 / 9 / 22 tasks. These five roles partition the cohort and are task-disjoint. No held-out score selected the fold.',
        'The 20-epoch study uses three outer folds and three inner OOF roles per outer. The 100-epoch study uses seed 42, outer 0, base role outer0_inner0 only. Its complete 100-epoch fit is not a three-fold experiment.',
        'Verified source/frame identities and episode/task memberships: `../02_dataset_and_splits/`. Original splits: `VIFAILBACK/04_evaluation_splits/train_validation_test/20261029T004900Z/fit_partitions.json`. The 28 measured sensor channels are 14 positions, 12 nonplaceholder velocities and two gripper-effort fields; these are not calibrated force/torque.'])
    report('03_MODEL_ARCHITECTURES.md','Models',[
        f"Pinned RT-DETR ResNet18-vd CNN only, revision `{p['model']['revision']}`. Each of three cameras contributes 16 fixed timestamps, giving 48 frames per episode. Spatial means concatenate 128+256+512=896 features; equal temporal/camera means give one representation per episode. Head 896→128→ReLU→Dropout(0.1)→1 has 114,945 parameters.",
        'FULL conditions train all 11,199,968 CNN parameters, including normalization affine terms; running moments remain fixed. Frozen and donor CNNs have zero trainable backbone parameters. Encoder, detection decoder and box heads are excluded.',
        'Full CNN frame chunks propagate gradients through exact recomputation while preserving one episode-level pooled loss and an eight-episode head minibatch. Bounded numerical, gradient, frozen-buffer, save/reload and resume evidence: `../13_reproducibility/`. Successful checks do not establish external scientific validity.'])
    curve_table=table(['Condition','Seed','Fit','Executed','Selected epoch','Last minus best V macro AP','Curve'],[[r['condition'],r['seed'],r['fit_id'],r['executed_epochs'],r['selected_epoch'],number(r['last_minus_best_V_macro_AP']),f"[Figure](../{resolve(r['figure']).relative_to(STUDY)})"] for r in curves])
    report('04_TRAINING_CONFIGURATIONS.md','Frozen training protocol',[
        'AdamW: head LR 0.001, CNN LR 0.00001, weight decay 0.001, betas (0.9,0.999), epsilon 1e-8. Effective batch eight episodes, live microepisode one, frame chunks four, FP32, gradient norm clipping 1.0. T-only standardization and T negative/positive BCE weight. No augmentation or warmup.',
        'All 20-epoch arms execute the first 20 epochs of cosine50; all 100-epoch arms use cosine100. Every requested epoch runs. Highest V macro AP wins, then lower V BCE using the same T class weight, then earliest epoch. Macro AP is the declared ViFailback adaptation of REASSEMBLE failure-AP selection. Selected weights are sigmoid-calibrated on separate C tasks.',
        'FROZEN100 reuses the verified historical V1 outer0_inner0 trajectory only because the frozen selection rule selects the same epoch 11. Historical cost is retained separately. New 20-epoch fits are required because original V1 used cosine100.',
        'Immutable protocol: `../01_protocol_and_source_evidence/protocol.json`. Exact per-fit config/history/checkpoint references and hashes: `../11_metrics_and_statistics/FIT_COVERAGE.json`.',curve_table,
        'Figures show loss and validation macro AP with the selected epoch. A negative last-minus-best value documents validation deterioration by the last observed epoch; this alone does not prove outer-test overfitting. Partial curves are not final-epoch results.'])
    for epochs,name in [(20,'05_20_EPOCH_COMPARISON.md'),(100,'06_100_EPOCH_COMPARISON.md')]:
        subset=[r for r in cohorts if r['condition'].endswith(str(epochs))]
        small=table(['Condition','Seed','Fold','N','Visual macro AP','F2 macro AP'],[[r['condition'],r['seed'],r['outer'],r['assessment_N'],number(r['metrics']['visual']['macro_AP']),number(r['metrics']['F2']['macro_AP'])] for r in subset])
        report(name,f'{epochs}-epoch comparison',[
            'Visual: '+answer_contrast(results,f'FULL{epochs}',f'FROZEN{epochs}'),
            'F2: '+answer_contrast(results,f'FULL{epochs}',f'FROZEN{epochs}','F2'),small,
            'Every fold-level F2 needs all three inner OOF branches. Additional seeds require prospective resource admission.' if epochs==20 else 'Single seed, single predeclared fitting role, single outer assessment and separate 788-episode meta bank: exploratory, not complete nested cross-fitting.'])
    report('07_REASSEMBLE_WEIGHT_TRANSFER.md','REASSEMBLE CNN donor',[
        f"Source Full100 executed 100 epochs and selected epoch 47, seed 42. Donor SHA `{p['donor']['sha256']}`. Only 115 CNN tensor keys transfer; no source classifier, visual/sensor scaler, calibrator or F2 transfers.",
        'DONOR20 and DONOR100 freeze the learned source CNN and fit new target heads under the corresponding matched target budgets. No separate donor target-domain CNN fine-tuning condition was declared.',
        'DONOR20: '+answer_contrast(results,'DONOR20','FROZEN20'), 'DONOR100: '+answer_contrast(results,'DONOR100','FROZEN100'),
        'A valid learned-state load establishes mechanical transfer, not predictive benefit. The historical 25-epoch source validator was not weakened; this donor completed 100 epochs.'])
    report('08_STATIC_SENSOR_AND_F2_RESULTS.md','Static sensor and F2',[
        'Canonical sensor LR: 280 statistics; balanced L2 C=1/max_iter=2000, T-only standardization, unweighted C=1 sigmoid calibration on C. Historical HGB uses max_iter=200, learning rate 0.05, L2=0.1, min_samples_leaf=20, leaves 7/15/31 selected by V macro AP; it remains a secondary reference. Reused states, sources and prediction hashes are checked.',
        'F2 = sigmoid(b + w_visual*p_visual + w_sensor*p_sensor): unweighted L2 C=1/lbfgs/max_iter=2000, calibrated probability inputs in float64, no postfusion calibration, fixed threshold 0.5. New coefficients/meta bank/FIT_LOCK are persisted before outer scores are evaluated. The 20-epoch bank is complete three-inner OOF; the 100-epoch bank has 788 held-out meta episodes.',
        'The pilot intentionally preserves canonical source-pilot sensor refit semantics: outer0_inner0 supplies meta 788 and a different fitted outer0_final sensor supplies outer 1,107. Meta probabilities are held out from the generating sensor model’s fitting/calibration groups. This is not one common sensor checkpoint across meta/test. Every matched visual arm uses identical corresponding sensor vectors and model IDs.',
        tables['B'],'## Learned F2 coefficients\n\n'+coef,'## Coefficient variation\n\n'+stability,
        'One fit cannot establish coefficient stability. Ranges are descriptive and depend on branch calibration; coefficients are not causal modality percentages.',
        '## Raw versus calibrated visual ranking\n\n'+ranks,
        'Positive-slope calibration preserves within-fit ranks apart from numerical ties; negative slopes reverse ranks. Pooled3 uses separate fold calibration maps, which can change cross-fold ranking. Raw/calibrated AP and rank correlations are retained for every evaluated cohort.',
        '## Complete secondary metrics\n\n'+detailed,
        'Exact per-class precision/recall and calibration bins are in each saved metrics object. All required F2-minus-LR/vision/average/HGB/V1 intervals appear in Table C. HGB comparisons are secondary and never drive selection.',
        '## Held-out correction diagnostics\n\n'+corrections,
        'Exact episode IDs, probabilities and vision/F2 correction/new-error flags are in `../09_f2_fusion/{condition}/seed{seed}/outer{fold}/OUTER_PREDICTIONS.json`. Per-task metrics: `../11_metrics_and_statistics/PER_TASK_DIAGNOSTICS.json`.'])
    task_contrasts=table(['Comparison','Seed','Fold','Task','N','Visual macro AP delta','F2 macro AP delta'],[[r['treatment']+' minus '+r['control'],r['seed'],r['fold'],t['task_id'],t['N'],number((t['macro_AP_differences'] or {}).get('visual')),number((t['macro_AP_differences'] or {}).get('F2'))] for r in results.get('matched_contrasts',[]) if r['fold']!='pooled3' for t in r.get('task_changes',[])])
    report('09_SEED_AND_FOLD_STABILITY.md','Seed and fold coverage',[tables['E'],tables['C'],stability,task_contrasts,
        'Seed 42 is primary. Seeds 123 and 20261023 were named before training and require measured resource admission. Missing seeds are not stability evidence. No additional 100-epoch seed/fold matrix was declared. Pooled3 is produced only after all three disjoint outer sets complete; mean-fold metrics remain separate fields. Seeds repeat fits on the same examples and never increase sample size.'])
    report('10_UNCERTAINTY_AND_LEAKAGE_LIMITATIONS.md','Uncertainty and leakage limitations',[limitations,
        'Paired task-cluster percentile 95% intervals use 2,000 draws and seed 20261111. Models share task draws. Single-class draws are discarded and counted. Per-task macro AP is unavailable when only one native class is present. Multiple comparisons are exploratory without multiplicity adjustment.',
        'Each F2 meta record matches its branch assessment role and is disjoint from that branch T/V/C and outer task groups. Twenty-epoch meta coverage equals the complete outer-training set. Pilot 788 is excluded from visual gradient fitting, selection and calibration. Canonical sensor meta/test refit semantics are documented in report08. Exact meta and outer sensor vectors plus source model identities must match between paired arms.',
        'The cohort manifests already contain native labels. F2 fitting consumes only meta labels and probabilities; outer prediction records are opened only after the persisted coefficient lock. This is procedural protection against outer-result tuning, not a claim that existing dataset labels were inaccessible.'])
    report('11_GPU_RUNTIME_AND_STORAGE.md','Measured computation and resource admission',[tables['D'],
        'Training, validation, postfit inference, process duration and historical feature extraction are separate. New model training sums include committed completed epochs; active incomplete-epoch time is not yet in those sums. Reused historical fitting is never counted as new training. CPU head fits have no GPU utilization requirement.',
        'Resource admission (full source evidence remains linked in its JSON):\n\n```json\n'+json.dumps(compact_admission(admission),indent=2)+'\n```',
        'Observed GPU process sessions:\n\n```json\n'+json.dumps(sessions,indent=2)+'\n```',
        'Current GPU telemetry:\n\n```json\n'+json.dumps(runtime['GPU_TELEMETRY'],indent=2)+'\n```',
        'Benchmark: `../13_reproducibility/BOUNDED_GPU_BENCHMARK.json`. Admission: `../01_protocol_and_source_evidence/RESOURCE_ADMISSION.json`. Forecasts are estimates from bounded measured throughput. Existing videos/features are reused and 20 GiB free reserve is required. No historical data/checkpoint is deleted.'])
    f2_answers=[]
    for a,b in [('FULL20','FROZEN20'),('FULL100','FROZEN100')]:
        f2_answers.append(a+' minus '+b+': '+answer_contrast(results,a,b,'F2'))
    task_bad=[r for r in tasks if r['macro_AP'] and r['macro_AP']['F2']<r['macro_AP']['sensor_LR']]
    seeds=sorted({r['seed'] for r in cohorts});folds=sorted({str(r['outer']) for r in cohorts if r['outer']!='pooled3'})
    train_hours=sum((r['new_training_seconds'] if r['new_training_seconds'] is not None else r['training_seconds'] or 0) for r in fits)/3600
    answers=[
        '1. **Did 20-epoch full CNN training improve visual prediction?** '+answer_contrast(results,'FULL20','FROZEN20'),
        '2. **Did 100-epoch full CNN training improve visual prediction?** '+answer_contrast(results,'FULL100','FROZEN100'),
        '3. **Did either improvement translate into better F2 fusion?** '+' '.join(f2_answers),
        '4. **Did F2 beat static sensor LR?** '+answer_fusion_contrast(results,'F2_minus_sensor_LR'),
        '5. **Did F2 beat the strongest available unimodal reference?** Retained HGB: '+answer_fusion_contrast(results,'F2_minus_historical_HGB')+' Corresponding vision: '+answer_fusion_contrast(results,'F2_minus_visual')+' Historical V1: '+answer_fusion_contrast(results,'F2_minus_historical_V1')+' LR-only superiority does not establish this claim.',
        '6. **Did REASSEMBLE-trained CNN weights transfer successfully?** Mechanical learned-state compatibility is verified separately from predictive benefit. Donor20: '+answer_contrast(results,'DONOR20','FROZEN20')+' Donor100: '+answer_contrast(results,'DONOR100','FROZEN100'),
        f'7. **Were differences consistent across seeds and task groups?** Completed assessment seeds {seeds}, outer folds {folds}. {len(task_bad)} completed arm/seed/task cells have lower F2 macro AP than sensor LR. Across those separately fitted evaluations, {sum(r["sensor_correct_broken"] for r in tasks)} sensor-correct episode occurrences became F2 errors; these are not unique independent examples. Report08 retains all task directions. One seed cannot establish seed stability; missing matched coverage remains untested.',
        f'8. **What was the actual GPU cost?** Observed GPU-controller process time is {sessions["observed_GPU_controller_process_hours"]:.6f} hours (session definition in report11). Recorded new training across CPU/GPU arms is {train_hours:.6f} hours, separated per arm in Table D. Validation and incomplete-epoch elapsed time remain separate; absent GPU telemetry is UNKNOWN.',
        '9. **Which claims are supported, inconclusive or untested?** Verified identities, executed fit counts and independent saved-score arithmetic support reproducibility within completed scope. Positive/negative conditional intervals are identified numerically above; intervals crossing zero are inconclusive, not equivalence. Unfinished fits, missing pairs/seeds and new-task generalization remain untested. Successful tests alone do not establish scientific validity.',
        '10. **What remains necessary for independent confirmation?** Predeclared evaluation on new task/collection groups with verified session/operator identities, multiple refits/seeds, frozen donor/selection choices and adequate grouped uncertainty. Previously examined tasks do not provide pristine confirmation.'
    ]
    report('12_SCIENTIFIC_CONCLUSIONS.md','Scientific conclusions',[status]+answers+[tables['C']])
    provenance={'generated_utc':utc(),'git_HEAD_at_report':git_commit(),'protocol_sha256':sha256(STUDY/'01_protocol_and_source_evidence/protocol.json'),
        'completed_fits':len(complete),'partial_fits':len(partial),'running_fits':len(running),'completed_fusion_cohorts':results.get('completed_fusion_cohorts',0),
        'controller':runtime,'GPU_sessions':sessions,'historical_outputs_modified':False,'push_performed_by_reporter':False}
    write_json(STUDY/'13_reproducibility/REPORT_PROVENANCE.json',provenance)
    report('13_RESEARCHER_HANDOFF.md','Researcher handoff',[status,tables['E']]+answers+[
        'Exact trained/reused checkpoint paths and hashes, histories, configurations and predictions: `../11_metrics_and_statistics/FIT_COVERAGE.json`. F2 coefficients, locks, meta banks and outer predictions: `../09_f2_fusion/{condition}/seed{seed}/outer{fold}/`. Split manifests: `../02_dataset_and_splits/`. Results and task diagnostics: `../11_metrics_and_statistics/`. Learning curves: `../12_learning_curves/INDEX.json`. Scientific limitations: `10_UNCERTAINTY_AND_LEAKAGE_LIMITATIONS.md`.',
        f"Git HEAD at report: `{provenance['git_HEAD_at_report']}`. Commit receipts and reproducibility evidence: `../13_reproducibility/`. No push is authorized. Do not select a model merely because it scores highest on an already-examined outer fold."])
    text_file(STUDY/'VIFAILBACK_MATCHED_CNN_STUDY_STATUS.md','# VIFAILBACK_MATCHED_CNN_STUDY_STATUS\n\n'+status+'\n\n'+tables['E']+'\n\nReports: `14_final_research_reports/01_EXECUTIVE_SUMMARY.md` through `13_RESEARCHER_HANDOFF.md`. Exact checkpoint/history/configuration/prediction paths: `11_metrics_and_statistics/FIT_COVERAGE.json`; F2 coefficients: `09_f2_fusion/`; split manifests: `02_dataset_and_splits/`; results: `11_metrics_and_statistics/CURRENT_RESULTS.json`; limitations: `14_final_research_reports/10_UNCERTAINTY_AND_LEAKAGE_LIMITATIONS.md`; Git commit evidence: `13_reproducibility/`.\n\n```json\n'+json.dumps(provenance,indent=2)+'\n```')
    return provenance
