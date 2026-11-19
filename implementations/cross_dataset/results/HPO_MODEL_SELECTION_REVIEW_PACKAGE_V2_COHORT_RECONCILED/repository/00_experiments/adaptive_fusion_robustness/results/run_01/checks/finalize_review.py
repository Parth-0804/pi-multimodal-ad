"""Finalize narrative from completed tables; never fit or infer."""
from pathlib import Path
import csv,json,datetime,shutil
R=Path(__file__).resolve().parent.parent
read=lambda p:json.loads(p.read_text())
def rows(p):return list(csv.DictReader(p.open()))
def table(headers,values):return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(str,row))+' |' for row in values])
def main():
 p=read(R/'progress.json');assert p['status']=='COMPLETE_ON_PILOT_COVERAGE';assert read(R/'checks/completion_integrity.json')['passed'];assert read(R/'checks/independent_recalculation.json')['passed']
 done=read(R/'predictions/fold_01/complete.json');assert done['parent_actions']==753 and done['realizations']==34 and done['failed_cases']==0
 models=rows(R/'comparison/model_comparison.csv');metrics=rows(R/'comparison/per_condition_metrics.csv');contrasts=rows(R/'comparison/paired_intervals.csv');extra=read(R/'checks/additive_quality_contribution.json')
 names={'historical_static':'Historical clean-trained F2','static_augmented':'A: Augmented static','quality_additive':'B: Additive quality','quality_interaction':'C: Quality interactions','visual':'Visual only','sensor':'Sensor only'}
 overview=table(['Model','Clean AP','Primary noise AP','Image noise AP','Sensor noise AP','Blur AP','Time-loss AP'],[[names[x['model']]]+[f"{float(x[k]):.6f}" for k in ['clean_mean_fold_AP','primary_mean_fold_AP','image_noise_AP','sensor_noise_AP','image_blur_AP','sensor_time_loss_AP']] for x in models])
 selected=[contrasts[0],contrasts[1],contrasts[2],extra]+[x for x in contrasts if x['contrast'] in ['quality_interaction_minus_static_augmented_CLEAN','quality_interaction_minus_historical_static_CLEAN','quality_additive_minus_static_augmented_CLEAN']]
 ctable=table(['Contrast','AP difference','95% paired interval'],[[x['contrast'],f"{float(x['AP_difference']):+.6f}",f"[{float(x['lower95']):+.6f}, {float(x['upper95']):+.6f}]"] for x in selected])
 clock=read(R/'config/clock.json');finished=datetime.datetime.fromisoformat(p['updated_utc']);start=datetime.datetime.fromisoformat(clock['started_utc'])-datetime.timedelta(seconds=clock['initial_audit_before_persist_seconds_allowance']);now=datetime.datetime.now(datetime.timezone.utc)
 monitor=rows(R/'provenance/assessment_monitor.csv');peak=max([int(x['peak_RSS_bytes']) for x in monitor]+[p['resource_observation']['VmHWM']]);training=read(R/'fusion_fits/fold_01/complete.json');transition=read(R/'provenance/fitting_transition_observation.json');first_assessment=datetime.datetime.fromtimestamp(transition['component_lock_mtime_ns']/1e9,datetime.timezone.utc);last_observed=datetime.datetime.fromisoformat(monitor[-1]['utc']);observed_active=training['seconds']+(last_observed-first_assessment).total_seconds()+done['seconds']
 resource={'final_review_utc':now.isoformat(),'automated_results_completed_utc':finished.isoformat(),'elapsed_seconds_to_automated_results_including_initial_allowance':(finished-start).total_seconds(),'elapsed_seconds_to_final_review_including_initial_allowance':(now-start).total_seconds(),'training_generation_and_fitting_seconds':training['seconds'],'resumed_assessment_seconds_including_cache_replay':done['seconds'],'observed_active_scientific_seconds_approximate':observed_active,'active_time_caveat':'Approximation combines training duration, first assessment lock to last live monitor, and resumed assessment duration. Exact initial termination time unavailable; not CPU-seconds.','maximum_observed_process_RSS_bytes_across_sessions':peak,'study_bytes_before_final_repack':sum(x.stat().st_size for x in R.parents[1].rglob('*') if x.is_file()),'GPU_used':False,'CPU_ids':list(range(4,12)),'report_before_original_deadline':now<datetime.datetime.fromisoformat(clock['deadline_utc'])-datetime.timedelta(seconds=120),'prediction_files':34,'assessment_actions':753,'assessment_action_realization_rows':753*34,'failed_cases':0,'bootstrap_valid':2000,'bootstrap_invalid':0,'new_models':3,'source_or_scientific_setting_repairs':0}
 assert resource['report_before_original_deadline'];(R/'provenance/final_runtime.json').write_text(json.dumps(resource,indent=2)+'\n')
 summary=f'''# Inconclusive — completed controlled adaptive-fusion pilot

The quality-interaction model did not demonstrate a reliable primary improvement over augmentation-matched static fusion. Its primary AP was 0.257009 versus 0.253996: difference **+0.003012**, paired 95% interval **[-0.026711, +0.032165]**. This interval includes both benefit and deterioration. Do not interpret the small positive point estimate as established superiority.

The predeclared one-fold pilot is complete: **753 actions, 77 failures, 26 recordings, 34 realizations per action**, giving 25,602 identified action-realization rows. All 34 prediction tables have exact matching coverage; failed cases = 0. The 753 both-absent rows are explicitly unavailable, not discarded failures. The other four outer folds remain untested because the training-only runtime admission locked fold_01 before assessment.

## Comparison

{overview}

Primary AP averages separately calculated AP across repeats, severities, the two Gaussian families and matched folds with equal weights. Repeated corruptions are not pooled as independent subjects, and probabilities are not averaged before AP. Pooled outer-fold AP is separately identified in per_condition_metrics.csv; with one fold it equals the corresponding fold AP. The table's family values average the prescribed severities and repeats.

## What augmentation, quality and interactions contributed

{ctable}

Augmentation alone showed no demonstrated primary benefit over historical clean-trained F2. Adding quality features without interactions reduced primary AP by 0.016636; its secondary interval is below zero. Interactions recovered performance relative to the additive model, but their +0.019649 contrast still includes zero. Consequently, these data do not establish that input-dependent modality coefficients improve the primary noise mixture.

For C versus A, average image-noise AP increased by 0.018627 and blur AP by 0.010656. Sensor-noise AP decreased by 0.012603 and time-loss AP by 0.010555. The worst family was sensor noise: C achieved 0.204040, below A's 0.216642. At strong sensor noise, C-A was -0.030310 with interval [-0.081866,+0.030406]. All individual C-A severity intervals include zero; these unadjusted secondary results describe the observed tradeoff, not universal superiority or established fault-specific effects.

C's clean AP increased by 0.004771 versus A and 0.004239 versus historical F2. Both clean intervals include meaningful losses: **no demonstrated absence of clean-performance cost** under the conservative zero-degradation margin. B's clean AP was lower than A's by 0.014432 (secondary interval [-0.029596,-0.000235]).

Unimodal outputs are included for context. Declared image absence routes every fusion model to the same sensor probability (AP 0.290531); sensor absence routes to the visual probability (AP 0.200401). Both absent produces unavailable/abstain. These fallback results are separate from the primary noise mixture.

## Fits, uncertainty and verification

Frozen 16-frame CNN and sensor branches, their original preprocessing, normalizers, calibrators and fitted components were retained. Three fusion models used exactly 3,777 inner-OOF parent actions and 11,331 rows, with per-action weights 0.5 clean, 0.25 image fault and 0.25 sensor fault. Each corrupted OOF prediction used the matching inner branch fit; assessment recordings were excluded from training, scales and quality normalization. Raw image pixels/native sensor signals were corrupted. Quality uses eight locked observable proxies, without fault identity, severity, seed, label or pristine counterpart as predictor inputs. All new components were locked before assessment. No branch training, tuning or new calibration occurred.

The 2,000 paired recording-cluster bootstrap draws were all valid, with zero invalid draws. Models, actions and realizations remain paired within recordings. Intervals condition on fixed fits and corruption realizations; secondary intervals are unadjusted. Additive-quality contrast was declared before assessment and uses the identical recording draw hash.

Fourteen focused tests passed. Independent saved-table recalculation reproduced 196 AP values and the hierarchical primary contrast. A separate arithmetic verifier replayed 70,029 new fusion probabilities from saved components and input columns, checked all 34 prediction files, training weights/normalization, source/configuration/clock locks, 296 raw-path metadata identities and protected previous artifact hashes. All passed. These are independent code-path checks, not external scientific review. See checks/completion_integrity.json and checks/independent_recalculation.json.

## Runtime and preservation

Automated inference, evaluation and the initial reports finished **22 October 2026 at 12:06 Berlin time**. Elapsed time to those results was {(finished-start).total_seconds()/3600:.2f} hours, including initial audit allowance and an interruption. Approximate observed active scientific execution was {observed_active/3600:.2f} hours; exact termination time of the initial worker is unavailable. Training-input generation and fitting took {training['seconds']/3600:.2f} hours; resumed assessment including cache replay took {done['seconds']/3600:.2f} hours. Final independent review was performed later, within the original 24-hour window.

The initial worker was absent after the interrupted chat session; the exact termination cause was not established. All 34 partial tables were preserved under provenance/interruption_01. Resume admission validated 29,907 cached arrays and the original locks, then reused the saved models without retraining or changing settings, seeds, folds or deadlines. The stale periodic checkpoint of 751 in progress.json is superseded by predictions/fold_01/complete.json and verified coverage of all 753 actions.

CPU only, eight threads on cores 4–11; no GPU used. Maximum observed process RSS across both sessions was {peak/2**30:.3f} GiB. Study storage before final repacking was {resource['study_bytes_before_final_repack']/2**30:.3f} GiB, far below 30 GiB. Exact resource observations and immutable deadline are in provenance/final_runtime.json and config/clock.json. Existing backbone workflow was not interrupted or restarted. Protected encoder/noise artifacts and governing scientific source identities are unchanged. No packages, datasets or weights were installed or downloaded; no additional experiment was launched.

## Limits and next decision

This is an exploratory, development-exposed **one-fold completed-action classification pilot**, not independent validation, online detection or an early-warning result. The cohort and earlier scores were already exposed to development. Held-out blur and time loss are excluded from augmentation fitting but remain part of the same dataset. Quality statistics are proxies; interaction coefficients are input-dependent coefficients, not trust percentages or causal importance.

DATA_AUDIT.md documents exact native labels, known force/torque and hardware issues, eligibility, frame sampling and sensor alignment. The bounded checks passed without relabeling or changing the cohort. Sixteen deterministic training examples have contact sheets and sensor summaries; assistant visual observations cover four, and human semantic adjudication remains outstanding. Finite sensor values do not establish physical validity. Four outer folds and independent-recording validation remain incomplete.

**Recommended next decision: retain historical F2 as the working baseline; do not adopt the adaptive model on this pilot evidence.** Any further confirmation would require separate authorization and broader matched coverage. No new experiment is launched here.

## Directly identified artifacts and recalculation

- [Prediction index with paths, SHA256 and coverage](comparison/coverage_and_prediction_index.csv)
- [Clean predictions](predictions/fold_01/clean/clean/repeat_00/predictions.csv)
- [Example corrupted table: strong sensor Gaussian, repeat 1](predictions/fold_01/sensor_noise/strong/repeat_01/predictions.csv)
- [All per-condition metrics, including AUROC, Brier and fixed-threshold confusion counts](comparison/per_condition_metrics.csv)
- [Paired intervals](comparison/paired_intervals.csv) and [additive-quality contrast](comparison/additive_quality_contribution.csv)
- [Saved fusion components](fusion_fits/fold_01/components.json) and [identified OOF training inputs](fusion_fits/fold_01/identified_OOF_training_inputs.csv)
- [Locked protocol](PROTOCOL.md), [resolved configuration](config/resolved_config.json), [quality definitions](config/quality_definitions.json), [native audit](DATA_AUDIT.md)
- [Runtime](provenance/final_runtime.json), [review ZIP](REVIEW_PACKAGE.zip), [package verification and SHA256](checks/package_verification.json)

Recalculate from saved prediction tables, from the repository root:

```bash
ma_thesis_env/bin/python -B 00_experiments/adaptive_fusion_robustness/code/recalculate.py
ma_thesis_env/bin/python -B 00_experiments/adaptive_fusion_robustness/results/run_01/checks/verify_completed_study.py
ma_thesis_env/bin/python -B 00_experiments/adaptive_fusion_robustness/results/run_01/checks/supplementary_quality_contrast.py
```

![Clean and primary-noise AP](comparison/fusion_ap_overview.png)

![Fault severity response](comparison/fault_family_ap.png)
'''
 archive=R/'provenance/automated_report_01';archive.mkdir(exist_ok=True)
 for name in ['README_FIRST.md','RESULTS_SUMMARY.md']:
  if not (archive/name).exists():shutil.copy2(R/name,archive/name)
 (R/'RESULTS_SUMMARY.md').write_text(summary)
 (R/'README_FIRST.md').write_text('''# Completed one-fold pilot — inconclusive

All **753 actions × 34 realizations** completed with zero failed cases. Quality-interaction fusion had primary AP **0.257009**, versus **0.253996** for augmentation-matched static fusion: **+0.003012**, paired 95% interval **[-0.026711,+0.032165]**. No reliable primary improvement was demonstrated.

Observed image-fault AP improved, while sensor-fault AP worsened. Clean AP was slightly higher, but clean-loss uncertainty remains. Additive quality alone reduced AP; interaction benefit versus additive quality is also uncertain. This is a development-exposed one-fold pilot; the other four folds remain untested.

**Decision: retain historical F2 as the working baseline.** No further experiment was launched.

[Full results and comparison](RESULTS_SUMMARY.md) · [Data audit](DATA_AUDIT.md) · [Locked protocol](PROTOCOL.md) · [All prediction paths and hashes](comparison/coverage_and_prediction_index.csv) · [Clean prediction table](predictions/fold_01/clean/clean/repeat_00/predictions.csv) · [Review package](REVIEW_PACKAGE.zip) · [ZIP checksum and verification](checks/package_verification.json)

Automated results finished at **12:06 Berlin time on 22 October 2026**; final independent review and repackaging followed within the unchanged 24-hour budget. Fourteen tests, 196 independent AP recalculations and 70,029 probability replays passed. Previous protected artifacts remain unchanged. See provenance/final_runtime.json for actual runtime, interruption and resource accounting.
''')
 print(json.dumps(resource,indent=2))
if __name__=='__main__':main()
