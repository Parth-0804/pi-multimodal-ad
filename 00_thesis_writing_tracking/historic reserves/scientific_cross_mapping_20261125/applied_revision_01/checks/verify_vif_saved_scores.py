"""Read-only verification of saved ViFailback evidence; no inference or fitting."""
from pathlib import Path
import json, hashlib, datetime, collections
import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score, brier_score_loss, log_loss
REPO=Path(__file__).resolve().parents[4]
STUDY=REPO/'VIFAILBACK/experiments/matched_cnn_20_100_f2_20261111'
CLOSE=STUDY/'18_fit_stop_and_analysis_20261124T1955Z'
manifest={}
def read(p):
 b=p.read_bytes();manifest[str(p.relative_to(REPO))]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)};return json.loads(b)
def sha(p):
 b=p.read_bytes();return hashlib.sha256(b).hexdigest()
r=read(STUDY/'11_metrics_and_statistics/CURRENT_RESULTS.json')
prior=read(CLOSE/'completed_scope_analysis/INDEPENDENT_VERIFICATION.json')
assert sha(STUDY/'11_metrics_and_statistics/CURRENT_RESULTS.json')==prior['current_results_sha256']
fits=read(STUDY/'11_metrics_and_statistics/FIT_COVERAGE.json')
counts=collections.Counter(x['condition'] for x in fits if x['complete']);assert sum(counts.values())==79 and len(fits)==111
for x in fits:
 if x['complete']:
  receipt=read(REPO/x['completion_receipt']);assert receipt['condition']==x['condition'];assert receipt['executed_epochs']==x['executed_epochs']
final=read(CLOSE/'FINAL_STATUS.json');receipt=read(STUDY/'04_full20/seed42/outer0_inner2/COMPLETE.json');assert final['target_completed_utc']==receipt['completed_utc'];assert final['target_complete']
checks=[];bykey={}
for c in r['cohorts']:
 rows=[]
 for fold in range(3) if str(c['outer'])=='pooled3' else [c['outer']]:
  root=STUDY/'09_f2_fusion'/c['condition']/f"seed{c['seed']}"/f'outer{fold}'
  rc=read(root/'COMPLETE.json');assert sha(root/'OUTER_PREDICTIONS.json')==rc['prediction_sha256'];assert sha(root/'metrics.json')==rc['metrics_sha256']
  lock=read(root/'FIT_LOCK.json');assert not lock['outer_prediction_records_loaded_before_fit'];assert not lock['outer_labels_used_in_fitting']
  rows.extend(read(root/'OUTER_PREDICTIONS.json'))
 assert len(rows)==c['assessment_N']==len({x['episode_index'] for x in rows})
 y=np.array([x['label'] for x in rows]);assert set(y)=={0,1}
 bykey[(c['condition'],c['seed'],str(c['outer']))]=rows
 for m in ['visual','sensor_LR','average','F2','historical_HGB','historical_V1']:
  p=np.array([x[m] for x in rows]);a=average_precision_score(y,p);b=average_precision_score(1-y,1-p)
  measured=dict(AP_failure=a,AP_success=b,macro_AP=(a+b)/2,AUROC=roc_auc_score(y,p),Brier=brier_score_loss(y,p),log_loss=log_loss(y,p,labels=[0,1]))
  err=max(abs(float(v)-c['metrics'][m][k]) for k,v in measured.items());assert err<1e-10
  checks.append({'condition':c['condition'],'seed':c['seed'],'fold':str(c['outer']),'model':m,'n':len(rows),'prevalence':float(y.mean()),'metrics':{k:float(v) for k,v in measured.items()},'max_error':err})
paired=[]
for c in r['matched_contrasts']:
 if c['treatment'] not in ['FULL20','FULL100']:continue
 a=bykey[(c['treatment'],c['seed'],str(c['fold']))];b={x['episode_index']:x for x in bykey[(c['control'],c['seed'],str(c['fold']))]}
 assert set(b)=={x['episode_index'] for x in a};assert all((x['label'],x['task_id'])==(b[x['episode_index']]['label'],b[x['episode_index']]['task_id']) for x in a)
 paired.append(c)
out={'classification':'VERIFIED current saved-score arithmetic, identity pairing, record/hash consistency; no training reproduction','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'completed':dict(counts),'planned':len(fits),'unfinished':32,'vectors':len(checks),'scalar_metric_checks':6*len(checks),'metric_checks':checks,'paired_FULL_contrasts':paired,'input_manifest':manifest,'limits':['No training or model inference. No checkpoint-byte verification.','Paired intervals remain the November 24 recorded checks; no new bootstrap run.','Receipt identity and fit-lock inspection do not reproduce every upstream training dependency.']}
p=Path(__file__).with_name('vif_saved_score_recheck.json');assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['completed','planned','unfinished','vectors','scalar_metric_checks']},indent=2))
