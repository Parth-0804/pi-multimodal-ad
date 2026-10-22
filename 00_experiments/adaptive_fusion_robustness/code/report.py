"""Evidence-based study reports and verified small-artifact package."""
import zipfile
import numpy as np,pandas as pd
from common import *
def table(frame):
 columns=list(frame.columns);lines=['| '+' | '.join(columns)+' |','| '+' | '.join(['---']*len(columns))+' |']
 for _,row in frame.iterrows():lines.append('| '+' | '.join(f'{v:.6f}' if isinstance(v,float) else str(v) for v in row)+' |')
 return '\n'.join(lines)
def audit_report():
 native=read(RUN/'checks/native_audit.json');fits=read(RUN/'checks/fitted_component_audit.json');images=read(RUN/'checks/native_cached_image_comparison.json');diag=pd.read_csv(RUN/'checks/encoder_training_diagnostics.csv');issues=pd.DataFrame(read(RUN/'checks/known_issue_actions.json'));last=issues.loc[issues.last_nonidle_action,['recording_id','segment_id','text','failure','included','official_note']];proc=read(RUN/'checks/image_processor.json')['config'];preflight=read(ENC/'checks/real_extractor_preflight.json')
 text=f'''# DATA_AUDIT — passed with semantic limitations

Native high-level actions, not low-level sub-actions. All {native['counts']['all_annotations']} success fields are scalar Boolean. The accepted parser permits Boolean or integer 0/1 only, rejects strings/missing/floats/unsupported values, and maps failure=1-success. Native start/end, text-derived action identity and target match the old inventory exactly. Labels are source annotations, not model or sensor-derived targets.

Counts: {native['counts']['primary_actions']} native primary actions, {native['counts']['primary_failures']} failures; the existing dual-complete cohort retains {native['counts']['included_actions']} actions, {native['counts']['included_failures']} failures from {native['counts']['recordings']} recordings. Exactly 21 primary actions were excluded upstream. No new relabeling or exclusions. Original eligibility requires a recognized action and valid interval, selected hand-camera usability and every selected sensor usable; the saved common cohort then requires >=32 interval frames while this experiment uses the unchanged 16-frame subset. The native/keyed reconciliation and each exclusion are in checks/native_annotation_audit.csv.

## Official issues reconciled against local native data

Official source read: https://github.com/TUWIEN-ASL/REASSEMBLE#%EF%B8%8F-file-comments (access record in provenance/official_dataset_notes.json). The source warns about final-action force/torque, camera coverage and hardware problems. Exact local final non-idle actions:

{table(last)}

The three warned force/torque final actions (31, 31 and 14 respectively) are already outside this cohort. In 2025-01-11-15-27-19 the preceding action 30 also lacks sufficient measured force/torque interval coverage and is excluded. Earlier actions remain. The gripper-break final action is excluded by the existing sensor-availability rule. The final missing-pose action is included: pose is not one of the five selected streams. Finite values never establish physical validity. Official warnings do not prove that every earlier action is unaffected; this residual uncertainty remains.

Camera warnings reconcile at action level: 2025-01-10-15-28-50 retains 16/18 actions, 2025-01-10-16-17-40 retains 0/2, and 2025-01-10-17-10-38 retains 31/33. No recording-wide exclusion was newly applied. Nonempty initial actions are keyed by native IDs, not assumed to start at segment 1.

## Images, time and sensor alignment

Camera: native hand MP4. All retained 16-frame lists match the exact native in-interval index formula: rounded linspace over eligible frame positions. This is uniform in frame index, not necessarily elapsed time. All selected timestamps are within native action bounds. The 16 predetermined fold_01/inner_fold_01 G examples span four action types, both outcomes and 16 distinct recordings, selected before viewing images or errors. Their native embedded MP4 payloads and cached files have identical SHA256; independently decoded same-codec frames have maximum pixel difference 0. All 32 original support-frame processed hashes match; the unchanged 16 are selected afterward. These bounded checks do not decode all videos again.

OpenCV BGR is explicitly converted to RGB. The exact installed processor configuration is checks/image_processor.json: resize={proc.get('size')}, rescale={proc.get('rescale_factor')}, normalize={proc.get('do_normalize')}. Native corruption is quantized back to uint8 by nearest integer before this same processor. Sensor timestamps use the native shared absolute-time action interval; each stream retains its own clock. The frozen branch uses 512-point within-interval interpolation, no extrapolation, with long gaps masked; explicit fault masks additionally prevent bridging missing time. Existing float32 statistics and saved imputation remain unchanged. Three training-only native replays reproduce sensor features exactly; image probability error is below the fixed 1e-5 bound (checks/end_to_end_benchmark.json).

See audit_examples/ for 16 contact sheets, selected timestamps/native annotations and aligned 22-channel summaries. Machine checks cover all 16. Assistant visual observations cover examples 1,8,10,15 only, recorded in checks/visual_observations.json. Independent human semantic adjudication remains outstanding; these checks do not prove every annotation correct.

## Fixed branches, splits and encoder diagnostics

All 75 saved CNN/encoder/sensor fits (25 roles for each) were verified by component SHA256 and reconstructed fit IDs against exact memberships. Five outer assessment partitions are disjoint and cover the cohort; four inner held-out partitions cover T separately within each outer fold. G/C/prediction recordings are disjoint; E is excluded from each relevant inner fit/calibration. CNN OOF banks have exact T coverage and hash-bound historical F2 stackers. Existing noise run_02's 51 prediction hashes and lock were verified, but those outer predictions are excluded from new fusion fitting and normalization.

Source inspection and recorded upstream runtime evidence show that the hybrid encoder receives spatial backbone maps via projections, executes AIFI and FPN/PAN, then spatial means per returned scale are concatenated and 16 frame vectors are arithmetically averaged. CNN width 896; encoder width 768. Frame averaging discards temporal order. The decoder/proposal/detection paths are guarded; the new experiment executes CNN only. Native map shapes and upstream trace are referenced by identity in checks/encoder_path_evidence.json.

Training-only cached encoder diagnostics across all 25 saved roles: finite values throughout; near-constant (SD<=1e-6) dimensions {int(diag.near_constant_sd_le_1e6.min())}–{int(diag.near_constant_sd_le_1e6.max())}; normalizer floors match saved G-only statistics; maximum absolute standardized values {diag.maximum_abs_standardized.min():.6f}–{diag.maximum_abs_standardized.max():.6f}. Final saved head evaluation-mode weighted G training BCE ranges {diag.eval_mode_final_checkpoint_weighted_BCE.min():.6f}–{diag.eval_mode_final_checkpoint_weighted_BCE.max():.6f}. This is not a retrained/tuned encoder or an assessment-score diagnostic.

## Decision

No concrete label-mapping, selected-frame alignment, cache identity or split defect was found in these bounded checks. Proceed under the locked resource and replay gates, retaining source-annotation/physical-validity uncertainty. No previous scientific file, cohort, result, deadline or STOP marker was changed.
'''
 (RUN/'DATA_AUDIT.md').write_text(text)
 write(RUN/'checks/encoder_path_evidence.json',{'source':str((ENC.parent.parent/'code/features.py').relative_to(REPO)),'source_sha256':sha(ENC.parent.parent/'code/features.py'),'recorded_runtime_evidence':str((ENC/'checks/real_extractor_preflight.json').relative_to(REPO)),'recorded_runtime_sha256':sha(ENC/'checks/real_extractor_preflight.json'),'runtime_keys':list(preflight),'results_with_shapes':preflight['results'], 'scope':'Upstream runtime evidence; new experiment CPU benchmark separately verifies CNN-only trace.'})
 write(RUN/'checks/audit_decision.json',{'passed':True,'scope':'Bounded native labels, frame/cache checks, source/fit identity, group disjointness and training-only diagnostics','semantic_certainty':'Not established for every label or physical sensor measurement','new_cohort_changes':False})
def report():
 progress=read(RUN/'progress.json');status=progress['status'];result='No new adaptive assessment result yet.'
 if (RUN/'comparison/model_comparison.csv').exists():
  m=pd.read_csv(RUN/'comparison/model_comparison.csv');ci=pd.read_csv(RUN/'comparison/paired_intervals.csv');primary=ci.loc[ci.primary].iloc[0];clean=ci.loc[ci.contrast=='quality_interaction_minus_historical_static_CLEAN'].iloc[0];additive=ci.loc[ci.contrast=='interaction_minus_additive_PRIMARY'].iloc[0]
  answer='supported improvement' if primary.lower95>0 else ('no demonstrated improvement' if primary.upper95<=0 else 'inconclusive')
  result=f"Direct answer: **{answer}**. Primary interaction-minus-augmentation-matched-static AP difference {primary.AP_difference:+.6f}, paired 95% interval [{primary.lower95:.6f}, {primary.upper95:.6f}]. Interaction-minus-additive: {additive.AP_difference:+.6f} [{additive.lower95:.6f}, {additive.upper95:.6f}]. Clean interaction-minus-historical-static: {clean.AP_difference:+.6f} [{clean.lower95:.6f}, {clean.upper95:.6f}]. A nonsignificant clean difference is not evidence of no harm; zero degradation is the conservative margin.\n\n"+table(m)+"\n\nAll predeclared contrasts, including clean versus both static baselines, appear in comparison/paired_intervals.csv. Augmentation, additive quality and coefficient interactions have separate controls; a primary improvement alone does not establish that interactions are necessary."
 text=f'''# {status} — controlled adaptive-fusion robustness

{result}

Coverage: {config().get('locked_folds')}. The fixed prefix is based on training-only end-to-end runtime, not scores. Five folds were the target; unavailable GPU ownership and bounded CPU runtime restricted this study to a prominently labeled pilot. No old workflow was stopped or restarted. Scientific cutoff and final deadline are in config/clock.json, with the recorded initial-audit allowance deducted; the final three hours are reserved for evaluation/reporting.

Question: for identical frozen 16-frame CNN and sensor branches, does quality interaction improve predefined corruption AP over augmentation-matched static F2? Branches and calibrators are fixed. Clean historical F2 is an additional reference. New models share identical inner OOF parent actions, deterministic augmentations and 0.5/0.25/0.25 weights. Eight observable input-quality proxies use no clean counterpart, injected severity/name/seed, identity, correctness or label as predictor inputs. Input-dependent coefficients are not trust percentages or causal modality importance.

Primary AP is calculated separately per fold/family/severity/realization, then averaged repeats -> severities -> two Gaussian families -> matched folds equally. Pooled outer AP is separately labeled. The 2,000 paired recording-cluster resamples stay within folds and retain every action/variant multiplicity. Intervals condition on fixed fits and three realizations; secondary intervals are unadjusted. Blur and sensor time loss are held-out fitting fault families, not an independent dataset. Complete absence uses an identical explicit surviving-branch fallback for all models; both absent is unavailable.

This is DEVELOPMENT-EXPOSED exploratory complete-action classification. It is not online/early detection, a validated reliability estimator, independent generalization or a result for every possible fault. See DATA_AUDIT.md for known issues and semantic limits. Historical Task4 is excluded.

Artifacts: PROTOCOL.md; config/; checks/; fusion_fits/ with identified OOF inputs and saved fusion components when complete; predictions/; comparison/coverage_and_prediction_index.csv; comparison/per_condition_metrics.csv; comparison/paired_intervals.csv; comparison/model_comparison.csv. Missing not-yet-produced results are explicitly incomplete, not zero effects. Independent saved-table recalculation: `ma_thesis_env/bin/python -B 00_experiments/adaptive_fusion_robustness/code/recalculate.py` after evaluation. Source, small tables, audit visuals and provenance are in REVIEW_PACKAGE.zip; raw videos, feature caches and upstream weight blobs are excluded and referenced by identity.

Next decision: require complete matched coverage and independent-recording validation before adopting a quality-conditioned fusion pipeline. No additional experiment is launched here.
'''
 (RUN/'RESULTS_SUMMARY.md').write_text(text);(RUN/'README_FIRST.md').write_text(f'# {status}\n\n'+result+'\n\n[Data audit](DATA_AUDIT.md) · [Results and limitations](RESULTS_SUMMARY.md) · [Protocol](PROTOCOL.md) · [Prediction paths/coverage](comparison/coverage_and_prediction_index.csv) · [Review package](REVIEW_PACKAGE.zip)\n\nOnly the fixed prefix is executed; broader coverage remains untested. The original visual workflow is untouched. See progress.json and config/clock.json for exact completion and time bounds.\n')
def package():
 files=[p for p in STUDY.rglob('*') if p.is_file() and not p.is_symlink() and 'cache' not in p.relative_to(STUDY).parts and '__pycache__' not in p.parts and p.suffix in ['.py','.md','.json','.csv','.txt','.png'] and '.writing' not in p.name and p.name not in ['package_manifest.json','package_verification.json']]
 manifest={str(p.relative_to(STUDY)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in files};write(RUN/'provenance/package_manifest.json',manifest);files.append(RUN/'provenance/package_manifest.json');guard(sum(p.stat().st_size for p in files),scientific=False)
 dest=RUN/'REVIEW_PACKAGE.zip';temp=RUN/'REVIEW_PACKAGE.writing.zip'
 with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
  for p in files:z.write(p,str(p.relative_to(STUDY)))
 os.replace(temp,dest)
 with zipfile.ZipFile(dest) as z:
  assert z.testzip() is None
  for name,d in manifest.items():assert len(z.read(name))==d['bytes'] and __import__('hashlib').sha256(z.read(name)).hexdigest()==d['sha256']
 write(RUN/'checks/package_verification.json',{'passed':True,'files_verified':len(manifest),'bytes':dest.stat().st_size,'sha256':sha(dest)})
