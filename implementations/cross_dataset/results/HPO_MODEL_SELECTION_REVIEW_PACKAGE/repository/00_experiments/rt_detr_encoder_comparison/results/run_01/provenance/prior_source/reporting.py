"""Local, evidence-based handoff and metric-recomputable archive; never uploads."""
import datetime,json,os,subprocess,zipfile
from pathlib import Path
import pandas as pd
from common import ROOT,REPO,CONDITIONS,read,write,sha,utc,event,resources,check_originals
def textfile(path,value):
 path=ROOT/path;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(value)
def number(value):return 'NOT_RUN' if value is None or pd.isna(value) else f'{value:.6f}'
def preservation():
 check_originals();before=read(ROOT/'provenance/initial_state.json');prefix=str(ROOT.relative_to(REPO))+'/'
 status=subprocess.run(['git','status','--porcelain=v1','--untracked-files=all'],cwd=REPO,text=True,capture_output=True,check=True).stdout
 clean=lambda value:sorted(s for s in value.splitlines() if prefix not in s)
 diff=subprocess.run(['git','diff','--stat'],cwd=REPO,text=True,capture_output=True,check=True).stdout
 check=subprocess.run(['git','diff','--check'],cwd=REPO,text=True,capture_output=True)
 result={'utc':utc(),'selected_original_hashes_unchanged':True,'outside_study_git_status_unchanged':clean(status)==clean(before['status']),'outside_study_diff_stat_unchanged':diff==before['diff_stat'],'git_diff_check_returncode':check.returncode,'git_diff_check_output':check.stdout+check.stderr,'initial_status_scope':'Existing dirty changes preserved; selected original files hashed, no full raw checksum sweep','current_diff_stat':diff}
 write(ROOT/'checks/preservation_final.json',result)
 assert result['outside_study_git_status_unchanged'] and result['outside_study_diff_stat_unchanged'],'OUTSIDE_STUDY_CHANGE_REQUIRES_REVIEW'
 return result
def documents():
 state=read(ROOT/'progress.json');evaluation=read(ROOT/'comparison/evaluation.json');rows=evaluation['comparison'];folds=evaluation['paired_folds'];status=evaluation['status'];cost_path=ROOT/'comparison/fit_costs_and_parameters.csv';cost=pd.read_csv(cost_path) if cost_path.exists() and cost_path.stat().st_size>2 else pd.DataFrame()
 table='| Condition | Visual pooled AP | Shared sensor AP | F2 pooled AP | Paired coverage |\n|---|---:|---:|---:|---|\n'
 for row in rows:table+=f"| {row['condition']} | {number(row['visual_pooled_AP'])} | {number(row['sensor_pooled_AP'])} | {number(row['fused_pooled_AP'])} | {row['completed_paired_folds']}/5 folds; {row['samples']} segments |\n"
 mean_table='| Condition | Visual mean fold AP | Sensor mean fold AP | F2 mean fold AP |\n|---|---:|---:|---:|\n'
 for row in rows:mean_table+=f"| {row['condition']} | {number(row['visual_mean_fold_AP'])} | {number(row['sensor_mean_fold_AP'])} | {number(row['fused_mean_fold_AP'])} |\n"
 paired=pd.read_csv(ROOT/'comparison/paired_comparisons.csv');contrast='No common completed outer folds: no four-condition ranking is supported.\n'
 if len(paired):
  contrast='| Contrast | AP difference | Conditional 95% percentile interval |\n|---|---:|---|\n'
  for d in paired.to_dict('records'):contrast+=f"| {d['contrast']} | {number(d['AP_difference'])} | [{number(d['percentile_95_low'])}, {number(d['percentile_95_high'])}] |\n"
  contrast+='\nPrimary contrast: F2 fine_tuned16 minus frozen16. Other intervals are unadjusted and exploratory. No automatic winner or significance threshold is used.\n'
 gradient=read(ROOT/'checks/gradient_preflight.json') if (ROOT/'checks/gradient_preflight.json').exists() else None
 stage='Dynamic final-stage checks have not completed.'
 if gradient:
  stage='The executed module is `backbone.encoder.stages.3`. Disposable training-only checks observed finite nonzero final-stage gradients and weight changes for both adapted arms, with earlier parameters and all BatchNorm running buffers unchanged. Frozen arms changed only their head. The final-stage exact changed tensor names, trainable counts and observed CNN module classes are saved in `checks/gradient_preflight.json`. Hooks observed no attention, transformer or detector decoder execution. All scientific fits start afresh after these disposable checks.'
 count='No complete visual fits.'
 if len(cost):
  count=f"{len(cost)} complete visual fits; {int(cost.optimizer_updates.sum())} optimizer updates; summed raw fitting wall time {cost.training_wall_seconds.sum()/3600:.3f} h. Total elapsed time additionally includes cohort preparation, original-feature extraction, calibration, branch inference, implementation and evaluation."
 limitations='This is completed-action failure classification on previously examined REASSEMBLE data. It is exploratory and is not online warning or robustness evidence. Eligibility requires 32 distinct decodable interval frames; see cohort counts before/after in `data_manifests/cohort_coverage.csv`. Raw models use only G, excluding a recording-disjoint 20% calibration subset C; this reduces gradient training data and differs from historical F2. Five epochs, one seed family and a fixed learning rate policy are controlled settings, not optimized settings. Original-feature normalizers are fitted on G and remain fixed during adaptation. The sensor method is unchanged across conditions, while its fitted parameters depend on each G/C partition. Equal epochs and segments do not imply equal computation. Threshold metrics use 0.5 without assessment tuning. Recording-cluster intervals condition on the fitted models and exposed data; they omit training-seed and repeated-training uncertainty. No independent reviewer was run; this is self-review. No historical anonymous prediction bank supplies these new results.'
 if status!='COMPLETE':limitations+=f" Only {len(folds)}/5 common paired outer folds are complete. Unpaired predictions do not enter the comparison. Missing results cannot support a study-wide ranking. Current recorded blocker: {state.get('blocker','none; inspect progress for active/incomplete work')}."
 observations='No common completed assessment rows are available; the scientific comparison is not yet answerable.'
 if folds:
  by={d['condition']:d for d in rows};a,b,c,d=[by[n] for n in CONDITIONS]
  observations=f"On these identical held-out rows, final-stage adaptation at 16 frames changed visual AP by {b['visual_pooled_AP']-a['visual_pooled_AP']:+.6f} and F2 AP by {b['fused_pooled_AP']-a['fused_pooled_AP']:+.6f}. Adapted-16 F2 minus the unchanged sensor AP was {b['fused_pooled_AP']-b['sensor_pooled_AP']:+.6f}. Increasing frozen input from 16 to 32 changed visual AP by {c['visual_pooled_AP']-a['visual_pooled_AP']:+.6f} and F2 AP by {c['fused_pooled_AP']-a['fused_pooled_AP']:+.6f}; increasing adapted input changed visual AP by {d['visual_pooled_AP']-b['visual_pooled_AP']:+.6f} and F2 AP by {d['fused_pooled_AP']-b['fused_pooled_AP']:+.6f}. These are measured fixed-fit differences; inspect their conditional intervals before interpreting a small change."
 if len(cost):
  observations+=' Raw training wall times by condition: '+', '.join(f"{n}: {z.training_wall_seconds.sum()/3600:.3f} h" for n,z in cost.groupby('condition'))+'. Frozen-head times exclude the separately measured original CNN extraction; full pixel-path replay timings are saved for both backbone policies.'
 recommendation='Have an independent reviewer verify the keyed predictions, partition lineage and fixed-protocol conclusions before authorizing any further scientific variant.' if status=='COMPLETE' else 'Resolve the recorded prerequisite or resource blocker and resume this same fixed-protocol study; do not rank unpaired conditions.'
 summary=f"""# Visual backbone comparison: {status}

Generated {utc()}. Completed paired folds: {', '.join(folds) or 'none'}. Failure class is the positive class. Pooled AP uses `sklearn.metrics.average_precision_score`, not trapezoidal PR area.

{table}

Pooled AP combines the held-out predictions; mean fold AP averages the completed fold APs. These are different summaries.

{mean_table}

## Paired contrasts

{contrast}

Intervals use 2,000 paired recording-cluster draws, seed 314159, retaining segment multiplicity. The exact draws, recording order, valid and undefined counts are in the comparison folder. One-class resamples are marked undefined and discarded without replacement draws. These are descriptive sampling intervals, conditional on these fits.

## Code and concept walkthrough

Input: native recording/segment keys, success-derived failure labels and full action intervals; saved recording-group outer/inner folds, restricted to one cohort before fitting. Representation: local original pretrained CNN selected spatial maps, spatial means concatenated then frame means; 32 selected frames are a deterministic superset of the original 16. Sensors use attributed progress-resampled statistics. Training: fixed G-only normalizer, five-epoch mean-pooled visual head and optional final-stage adaptation; raw sensor logistic fit on G; disjoint C sigmoid calibration. Branch predictions: inner-held recordings yield one calibrated pair per outer-training sample. F2: unweighted two-probability logistic stacking fitted on those OOF pairs; independently fitted outer raw branches and calibrators predict outer E. Evaluation: directly keyed outer predictions only, same paired folds for every condition, fixed threshold and paired cluster bootstrap. Conclusions apply to these controlled fits and this restricted exposed cohort.

{stage}

## Computation and fit coverage

{count}

See `fit_costs_and_parameters.csv`, individual learning curves and `checks/training_resource_estimate.json`. Training uses a single available Tesla T4, float32, microbatch one segment, effective batch eight. A 32-frame segment is distinct from a 32-segment optimizer batch. Cached original features accelerate frozen heads; adapted fits retain a live final-stage gradient path. Inference timings state whether decoding is included and distinguish frozen cached-feature timing from full image-to-prediction timing. These timings do not establish real-time performance. The latest launch removed the wall-hour limit; the 30 GiB new-storage and other fixed study caps remain. CPU affinity caps simultaneous computational CPU use at four; host memory is monitored rather than represented as a proven OS memory hard limit.

## Interpretation and limitations

{observations}

{limitations}

The measured contrasts above answer whether final-stage adaptation helped visual AP, whether it helped F2 relative to its frozen reference and the shared sensor, and whether 32 observations changed either arm. An AP decrease is a valid negative finding. Small changes or intervals spanning zero are inconclusive about a repeatable population effect. F2 coefficients are predictive coefficients, not causal percentage contributions. No scientific setting was selected by assessment scores.

## One recommended next decision

{recommendation}
"""
 textfile('comparison/RESULTS_SUMMARY.md',summary)
 textfile('how_to_resume.md',f"""# Resume this exact study

Latest recorded state: `{state['status']}`. Complete visual fits started including attempts: {state.get('full_visual_fits_started',0)}/110. Disposable optimizer steps: {state.get('preflight_optimizer_steps',0)}/20.

From the repository root, inspect state without starting work:

```bash
bash {ROOT.relative_to(REPO)}/source/study.sh status
```

Supported stages are `prepare`, `preflight`, `train`, `resume`, `evaluate`, `package`, `status`, `stop`. `preflight` performs actual disposable gradient/replay checks, then extracts original pretrained features. `resume` requires matching fit/source/config/cohort identities and retains optimizer, RNG, epoch and data-order position. It reuses completed predictions only when their identities and hashes match. Never run a second writer. An explicit STOP marker blocks resume until its recorded request is resolved; preserve the marker in provenance before clearing it. Stop requests and SIGTERM checkpoint only this study.

For interrupted training after successful preparation/preflight:

```bash
bash {ROOT.relative_to(REPO)}/source/study.sh resume
```

For completed training, the remaining stages are `evaluate` and then `package`; they do not train additional models. No command is scheduled. Original data/weights must still be accessible; no downloads or package installation are performed. Do not edit scientific sources/configuration after fits are locked and then silently resume.
""")
 textfile('checks/SELF_REVIEW.md',f"""# Self-review, not independent review

Generated {utc()}. Reviewed new source and directly keyed output manifests. Synthetic tests: `checks/unit_test_results.json`. Dynamic CNN checks: `checks/gradient_preflight.json`; checkpoint replay: `checks/checkpoint_resume_preflight.json`. Every complete visual fit has G/C/held-recording membership and compact saved-model probability replay evidence in its `complete.json`; every completed condition also has F2 arithmetic replay. Evaluation requires common completed folds and verifies matching sample keys/truth/shared sensor probabilities and prediction hashes. Original-file preservation is checked against the initial selected hashes and dirty Git status. No raw checksum sweep is claimed.

Status: {status}. Complete paired folds: {len(folds)}. Incomplete files or fits are not evidence of completed assessment. Static inspection, synthetic checks, disposable gradient checks, full scientific fits and saved-prediction evaluation are distinct evidence categories. A self-review cannot establish freedom from every implementation or scientific-design error; independent review remains outstanding. No conclusion depends on an earlier AI completion report or checkpoint name. Historical Task4 and all unrequested experiments remain excluded.
""")
 textfile('README_FIRST.md',f"""# F2 frozen versus final-stage adaptation, 16 versus 32 frames

**Status: {status}; {len(folds)}/5 common paired outer folds.** Generated {utc()}.

[Results and limitations](comparison/RESULTS_SUMMARY.md) · [Resolved settings](config/resolved_config.json) · [Progress](progress.json) · [Resume commands](how_to_resume.md) · [Self-review](checks/SELF_REVIEW.md).

{table}

{stage}

{count} Partial or unpaired predictions are excluded from the comparison. No desired score was imposed or used to alter the study.

This new study lives entirely under `{ROOT.relative_to(REPO)}`. The local `REVIEW_PACKAGE.zip` contains the new implementation, tests/config, cohort/frame/fit evidence, directly identified outer predictions and numerical tables sufficient to recompute the reported assessment metrics. It excludes raw data, caches and weight blobs; their local identities and hashes are retained. Nothing is uploaded or scheduled. Existing scientific files, historical outputs and dirty changes are preserved.

Next decision: {recommendation}
""")
def package():
 assert (ROOT/'comparison/evaluation.json').exists(),'EVALUATION_REQUIRED_BEFORE_PACKAGE'
 preservation();documents();evaluation_state=read(ROOT/'comparison/evaluation.json')['status'];event('STUDY_COMPLETE' if evaluation_state=='COMPLETE' else 'STUDY_PARTIAL_OR_BLOCKED',active_job=None,review_package='REVIEW_PACKAGE.zip',remaining_work_authorized_launched=False)
 excluded=[];files=[]
 for p in sorted(ROOT.rglob('*')):
  if not p.is_file() or p.is_symlink():continue
  rel=p.relative_to(ROOT);name=str(rel)
  if rel.parts[0] in ['shared_cache','temporary'] or p.suffix in ['.pt','.npy','.npz','.lock'] or '.writing' in p.name or p.name in ['REVIEW_PACKAGE.zip','review_payload_manifest.json','archive_verification.json']:
   excluded.append({'path':name,'bytes':p.stat().st_size,'sha256':sha(p) if p.suffix=='.pt' else None});continue
  files.append(p)
 manifest={'utc':utc(),'included':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files],'excluded':excluded,'original_pretrained_weights_identity':'provenance/original_pretrained_identity.json','scope':'All archive contents are new study files; no data/weight/cache blobs; no upload'}
 write(ROOT/'provenance/review_payload_manifest.json',manifest);files.append(ROOT/'provenance/review_payload_manifest.json')
 size=sum(p.stat().st_size for p in files);resources(size+16*1024**2);target=ROOT/'REVIEW_PACKAGE.zip';tmp=target.with_name('REVIEW_PACKAGE.writing.zip')
 with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in files:z.write(p,str(p.relative_to(ROOT)))
 os.replace(tmp,target)
 with zipfile.ZipFile(target) as z:
  assert z.testzip() is None
  assert len(z.namelist())==len(files) and len(set(z.namelist()))==len(files)
  for d in manifest['included']:
   import hashlib
   assert hashlib.sha256(z.read(d['path'])).hexdigest()==d['sha256']
  # Recompute AP directly from archived CSV bytes, without importing evaluation.
  # This catches an archive that omitted the small keyed assessment payloads.
  import io
  from sklearn.metrics import average_precision_score
  evaluation=read(ROOT/'comparison/evaluation.json');metric_replays=[]
  for name in CONDITIONS:
   parts=[]
   for fold in evaluation['paired_folds']:
    q=pd.read_csv(io.BytesIO(z.read(f'{name}/{fold}/assessment_predictions.csv')),dtype={'recording_id':str,'segment_id':str});assert not q[['recording_id','segment_id']].isna().any().any();parts.append(q)
   if not parts:continue
   predictions=pd.concat(parts,ignore_index=True)
   for branch in ['visual','sensor','fused']:
    actual=float(average_precision_score(predictions.failure,predictions['p_'+branch]));expected=next(row for row in evaluation['comparison'] if row['condition']==name)[branch+'_pooled_AP'];error=abs(actual-expected);assert error<=1e-12;metric_replays.append({'condition':name,'branch':branch,'AP':actual,'absolute_difference':error})
 write(ROOT/'checks/archive_verification.json',{'utc':utc(),'path':target.name,'bytes':target.stat().st_size,'sha256':sha(target),'CRC_passed':True,'included_payload_hashes_verified':len(manifest['included']),'archived_prediction_AP_replay':metric_replays,'archive_AP_tolerance':1e-12,'manifest_path':'provenance/review_payload_manifest.json','outside_archive_receipt':True})
 print('Review package verified:',target,flush=True)
