"""Honest live/final asymmetric-policy results and small replayable review ZIP."""
import datetime,os,subprocess,zipfile,hashlib,io,json
from pathlib import Path
import pandas as pd
from common import ROOT,REPO,CONDITIONS,config,read,write,sha,resources,check_originals,event
from budget import clock,remaining

def text(p,s):
 p=ROOT/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
def num(v):return '—' if v is None or pd.isna(v) else f'{v:.6f}'

def documents(final=False):
 state=read(ROOT/'progress.json');d=clock();ev=read(ROOT/'comparison/evaluation.json') if (ROOT/'comparison/evaluation.json').exists() else None
 folds=ev['paired_folds'] if ev else [];rows=ev['comparison'] if ev else []
 table='| Condition | Epochs | Visual AP | Sensor AP | F2 AP | Common folds |\n|---|---:|---:|---:|---:|---:|\n'
 for n in CONDITIONS:
  r=next((x for x in rows if x['condition']==n),{})
  table+=f"| {n} | {config()['epoch_budgets'][n]} | {num(r.get('visual_pooled_AP'))} | {num(r.get('sensor_pooled_AP'))} | {num(r.get('fused_pooled_AP'))} | {len(folds)}/5 |\n"
 paused=(ROOT/'STOP.json').exists()
 status=('PAUSED — PARTIAL' if paused else 'COMPLETE' if len(folds)==5 else 'PARTIAL') if final else 'RUNNING / INCOMPLETE'
 pause_note=''
 if paused and (ROOT/'checks/paused_checkpoint_validation.json').exists():
  pc=read(ROOT/'checks/paused_checkpoint_validation.json');pause_note=f"External workflow requested a safe priority stop for encoder/noise work. The sole GPU is occupied by that separate workflow. STOP.json remains intact; this run has no training process. Checkpoint: one full epoch plus {pc['next_position_in_epoch']}/{pc['G_segments_per_epoch']} segments in epoch two; {pc['optimizer_updates']} updates; two complete epochs have NOT finished. Its model/optimizer/RNG/order and source/config identities pass CPU validation. First-epoch BCE matches the original five-epoch recipe exactly (absolute difference {pc['first_epoch_loss_absolute_difference']}). See checks/external_priority_pause.json and paused_checkpoint_validation.json. The effective execution policy remains recorded in execution_policy.json." 
 w=read(ROOT/'worker_status.json') if (ROOT/'worker_status.json').exists() else {'status':'not launched'}
 left=remaining(reporting=True)
 if left is None:limits=f"Wall-time limit removed by the user's explicit amendment on {d['effective_policy_authorized_utc']}. There is no training cutoff or hard deadline. Frozen16/32 retain five epochs; fine-tuned16/32 use exactly two joint epochs. Cumulative GPU/CPU/storage/fit/diagnostic limits remain unchanged. The old24h clock/config fields are preserved as historical checkpoint provenance; execution_policy.json records the effective policy."
 else:
  limits=f"Fixed start: {d['accepted_utc']} ({d['accepted_Europe_Berlin']} Berlin). Hard deadline: {d['deadline_utc']} ({d['deadline_Europe_Berlin']} Berlin). Training cutoff: {d['training_cutoff_utc']}; last three hours reserved for reporting. Time remaining at this document write: {max(0,remaining(reporting=True))/3600:.2f} h. Prior study elapsed is separate, not subtracted from this amendment clock."
 coverage=f"Common completely assessed outer folds: {', '.join(folds) or 'none'}. Only this four-condition intersection supplies the primary comparison. Unmatched frozen coverage is listed separately in `comparison/unmatched_coverage.json`. A one-fold result is a pilot; no statement extends to the unobserved folds."
 limitation="This is an asymmetric epoch-budget comparison: frozen heads use five epochs, final-stage plus head use exactly two joint epochs. It is not an equal-epoch/equal-compute fine-tuning isolation, convergence study, optimal architecture claim, robustness test or completion of unobserved folds. Recording-cluster bootstrap uncertainty conditions on these fitted models; one observed fold cannot establish variation across unobserved folds. One seed family; previously exposed REASSEMBLE cohort; fixed0.5 threshold. No outer scores select settings, stopping, folds or batching. Historical Task4 remains excluded. Review is self-review; independent review is outstanding."
 unmatched_table=''
 if (ROOT/'comparison/unmatched_frozen_metrics.json').exists():
  extra=read(ROOT/'comparison/unmatched_frozen_metrics.json')
  if extra:
   unmatched_table='Unmatched frozen reference, excluded from the four-condition comparison:\n\n| Condition / fold | Epochs | Segments | Visual AP | Sensor AP | F2 AP |\n|---|---:|---:|---:|---:|---:|\n'
   for r in extra:unmatched_table+=f"| {r['condition']} / {r['fold']} | {r['epochs']} | {r['samples']} | {r['visual_AP']:.6f} | {r['sensor_AP']:.6f} | {r['F2_AP']:.6f} |\n"
 contrast='No paired result yet.'
 if ev and folds:
  q=pd.read_csv(ROOT/'comparison/paired_comparisons.csv');contrast=q.to_markdown(index=False) if __import__('importlib').util.find_spec('tabulate') else q.to_csv(index=False)
 recommendation='Review the matched pilot and its evidence before authorizing more outer-fold coverage.' if len(folds)==1 else 'Review the completed matched evidence before authorizing any additional scientific change.' if len(folds)>1 else 'Review the checkpoint and remaining-cost evidence before authorizing another bounded continuation of this same amended protocol.'
 if paused:recommendation='Resume the saved checkpoint when its explicit pause is resolved and the allocated GPU is free; retain the effective execution policy and all resource caps.'
 text('comparison/RESULTS_SUMMARY.md',f"# Asymmetric epoch-budget backbone study — {status}\n\n{coverage}\n\n{pause_note}\n\n{table}\n\nAP is sklearn average_precision_score on directly keyed outer assessment predictions. Mean-fold AP, AUROC, fixed-threshold metrics and Brier scores are separate numerical tables.\n\n{contrast}\n\n{unmatched_table}\n\n{limitation}\n\n{limits}\n\nNext decision: {recommendation}\n")
 text('README_FIRST.md',f"# Two-epoch fine-tuning / five-epoch frozen backbone comparison\n\n**{status}**. {coverage}\n\n[Results](comparison/RESULTS_SUMMARY.md) · [Protocol amendment](protocol_amendment.md) · [Performance](performance_report.md) · [Progress](progress.json) · [Worker](worker_status.json) · [Focused checks](checks/focused_checks.json).\n\n{table}\n\n{limits}\n\n{pause_note}\n\nWorker status: `{w.get('status')}`; supervisor PID `{w.get('supervisor_pid')}`, worker PID `{w.get('worker_pid')}`. See `logs/amended_training.log`. Resume only via `bash {ROOT.relative_to(REPO)}/source/study.sh supervise`; it reuses the stable clock and rejects a second writer. No other machine, future schedule or new deadline is created. An existing STOP.json blocks resumption; preserve it as provenance and clear only after the recorded priority dependency has completed. Do not bypass it to run a competing writer.\n\n{limitation}\n\nSingle next decision after stopping: {recommendation}\n")
 b=read(ROOT/'checks/performance_benchmark.json');b32=read(ROOT/'checks/prediction32_batch_check.json');completed=[];models=[]
 for n in CONDITIONS:
  for p in (ROOT/n).glob('fold_*/**/visual_fit/complete.json'):
   a=read(p);completed.append({'condition':n,'fold':a['job']['fold_name'],'role':a['job']['role'],'epochs':a['epochs_complete'],'training_seconds':a['training_wall_seconds'],'C_prediction_seconds':a['raw_prediction_cost_C']['seconds'],'V_prediction_seconds':a['raw_prediction_cost_V']['seconds'],'reused':a['identities'].get('config')!=sha(ROOT/'config/resolved_config.json'),'fit_id':a['fit_id'],'complete_path':str(p.resolve())})
   model=p.with_name('model.pt');models.append({'path':str(model.resolve()),'sha256':sha(model),'bytes':model.stat().st_size,'fit_id':a['fit_id'],'calibrator_path':str(p.with_name('calibrator.json').resolve())})
 write(ROOT/'provenance/fit_checkpoint_manifest.json',{'completed_fits':completed,'retained_models':models,'incomplete_checkpoints':[{'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)} for p in ROOT.glob('**/visual_fit/in_progress.pt')],'historical_inventory':'fit_provenance_inventory_initial.json and checkpoint_inventory_initial.json; old5epoch FT outputs excluded from new fit reuse','original_source_snapshot':'original_source_snapshot/','shared_cache_reference':str((REPO/config()['original_run']/'shared_cache').resolve())})
 write(ROOT/'budget_state.json',{'clock':d,'now_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'remaining_seconds':remaining(reporting=True),'training_remaining_seconds':remaining(),'full_fit_starts_cumulative':state['full_visual_fits_started'],'full_fit_cap':config()['full_visual_fit_cap'],'diagnostic_steps_cumulative':state['preflight_optimizer_steps'],'diagnostic_step_cap':config()['preflight_step_cap'],'technical_repairs_cumulative':state['technical_repairs'],'storage':resources(),'worker':w,'common_folds':folds,'status':status})
 measured=pd.DataFrame(completed);cost=measured.to_csv(index=False) if len(measured) else 'No completed amendment fits yet.'
 text('performance_report.md',f"# Measured performance and resource policy\n\n{limits}\n\nBounded benchmark: {b['wall_seconds']+b32['wall_seconds']:.2f} s total, zero optimizer steps. Both paths used identical warmed G-only segments; these warm-cache figures exclude cold video decoding. Two loader threads with worker-local video/processor state preserve order and exact pixel tensors; only two in-flight tensors. No worker changes global training RNG. CPU affinity stays0–3 because increased entitlement was not established. No pinning/nonblocking change, mixed precision, larger training microbatch, compilation or prefix activation cache. Frozen execution remains the authoritative original five-epoch cached-feature path. The frozen prefix already has no autograd history when its inputs and parameters do not require gradients, so no new graph boundary was introduced.\n\n```json\n{json.dumps(b['benchmarks'],indent=2)}\n```\n\n16-frame probability max absolute difference: {b['probability_max_abs']:.12g};32-frame: {b32['probability_max_abs']:.12g}. Fixed tolerance atol1e-6/rtol1e-5.32-frame benchmark is numerical inference checking, not observed32-frame fitting cost. No relaxed tolerance or assessment tuning. Baseline historical16-frame C/V prediction cost was {b['baseline_postfit_C_seconds']+b['baseline_postfit_V_seconds']:.1f}s. Actual amendment fit times (reused fitting time is historical):\n\n```csv\n{cost}\n```\n\nInitial full first-cycle projection was19.13hours before any32frame fit; it remains provisional. At the external pause, actual fine-tuned16 fitting consumed905.56seconds for3621segment presentations (one complete epoch plus part of epoch two), not a completed end-to-end fit. No measured two-epoch C/V/calibration or32frame fitting cost is available yet; do not present the benchmark as that cost.\n\nPer-fit admission includes raw training, C/V inference, sigmoid calibration, full saved-model replay, startup/checkpoints and F2; measured completed same-frame fits update estimates with35% margin. Unobserved32 costs remain provisional. The user removed wall-time admission limits; fixed epochs, fold order, cumulative fit/diagnostic caps and storage/free-space guards still apply. Runtime estimates remain descriptive. Exact updates and first-real-update loader/H2D/forward-backward timings are saved with each fit. Total disk accounting sums original and amendment regular files, without double-counting shared-cache symlinks; atomic write/ZIP peak bytes are reserved before write. No extra30GiB allocation.\n")

def finish():
 from evaluation import evaluate
 evaluate()
 # Add explicit condition/epoch/scope columns without changing authoritative frozen CSVs.
 combined=[];unmatched_metrics=[]
 from sklearn.metrics import average_precision_score
 paired=read(ROOT/'comparison/evaluation.json')['paired_folds']
 for n in CONDITIONS:
  for done in (ROOT/n).glob('fold_*/condition_complete.json'):
   path=done.parent/'assessment_predictions.csv';z=pd.read_csv(path,dtype={'recording_id':str,'segment_id':str});assert sha(path)==read(done)['assessment_sha256']
   z['condition']=n;z['model_epochs']=config()['epoch_budgets'][n];z['comparison_scope']='paired' if done.parent.name in paired else 'unmatched';z['source_predictions_path']=str(path.resolve());z['source_predictions_sha256']=sha(path);combined.append(z)
   if done.parent.name not in paired:unmatched_metrics.append({'condition':n,'fold':done.parent.name,'epochs':config()['epoch_budgets'][n],'samples':len(z),'visual_AP':float(average_precision_score(z.failure,z.p_visual)),'sensor_AP':float(average_precision_score(z.failure,z.p_sensor)),'F2_AP':float(average_precision_score(z.failure,z.p_fused)),'scope':'UNMATCHED; excluded from primary comparison','predictions_sha256':sha(path)})
 from common import save_csv
 save_csv(ROOT/'comparison/identified_assessment_predictions.csv',pd.concat(combined,ignore_index=True) if combined else pd.DataFrame(columns=['sample_id','recording_id','segment_id','failure','condition','model_epochs','comparison_scope']))
 write(ROOT/'comparison/unmatched_frozen_metrics.json',unmatched_metrics)
 unmatched={n:[p.parent.name for p in (ROOT/n).glob('fold_*/condition_complete.json')] for n in CONDITIONS};write(ROOT/'comparison/unmatched_coverage.json',unmatched)
 check_originals();old=REPO/config()['original_run'];unchanged=all(sha(p)==sha(ROOT/'provenance/original_source_snapshot'/p.name) for p in (old/'source').iterdir() if p.is_file())
 result={'original_sources_unchanged':unchanged,'original_config_unchanged':sha(old/'config/resolved_config.json')==sha(ROOT/'provenance/original_config_snapshot/resolved_config.json'),'git_diff_check':subprocess.run(['git','diff','--check'],cwd=REPO,capture_output=True,text=True).returncode,'review':'self-review; independent review outstanding'};assert all(result[k] for k in ['original_sources_unchanged','original_config_unchanged']);write(ROOT/'checks/preservation_review.json',result)
 event('PAUSED_EXTERNAL_PRIORITY' if (ROOT/'STOP.json').exists() else 'AMENDMENT_FINISHED',active_job=None,full_visual_fits_completed=sum(len(list((ROOT/n).glob('fold_*/**/visual_fit/complete.json'))) for n in CONDITIONS),completed_paired_folds=len(read(ROOT/'comparison/evaluation.json')['paired_folds']))
 documents(final=True)
 files=[];excluded=[]
 for p in sorted(ROOT.rglob('*')):
  if not p.is_file() or p.is_symlink():continue
  rel=p.relative_to(ROOT)
  if rel.parts[0] in ['shared_cache','temporary'] or p.suffix in ['.pt','.npz','.npy','.lock','.zip'] or '.writing' in p.name or p.name in ['archive_verification.json','review_payload_manifest.json']:
   excluded.append({'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p) if p.suffix=='.pt' else None});continue
  files.append(p)
 manifest={'included':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files],'excluded_large_or_temporary':excluded};write(ROOT/'provenance/review_payload_manifest.json',manifest);files.append(ROOT/'provenance/review_payload_manifest.json');resources(sum(p.stat().st_size for p in files)+16*1024**2)
 target=ROOT/'REVIEW_PACKAGE.zip';temp=ROOT/'REVIEW_PACKAGE.writing.zip'
 with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in files:z.write(p,str(p.relative_to(ROOT)))
 os.replace(temp,target);replays=[]
 with zipfile.ZipFile(target) as z:
  assert z.testzip() is None
  for a in manifest['included']:assert hashlib.sha256(z.read(a['path'])).hexdigest()==a['sha256']
  from sklearn.metrics import average_precision_score
  e=read(ROOT/'comparison/evaluation.json')
  for n in CONDITIONS:
   parts=[pd.read_csv(io.BytesIO(z.read(f'{n}/{fold}/assessment_predictions.csv'))) for fold in e['paired_folds']]
   if not parts:continue
   frame=pd.concat(parts,ignore_index=True);r=next(v for v in e['comparison'] if v['condition']==n)
   for branch in ['visual','sensor','fused']:
    actual=float(average_precision_score(frame.failure,frame['p_'+branch]));assert abs(actual-r[branch+'_pooled_AP'])<=1e-12;replays.append({'condition':n,'branch':branch,'AP':actual})
 write(ROOT/'checks/archive_verification.json',{'CRC_passed':True,'payload_hashes_verified':len(manifest['included']),'archived_predictions_AP_replay':replays,'zip_sha256':sha(target),'bytes':target.stat().st_size})
 print('FINAL REPORT AND VERIFIED REVIEW PACKAGE',ROOT,flush=True)
