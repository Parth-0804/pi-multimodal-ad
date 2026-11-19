"""Validate only the new addendum, preserve existing packets, and build a small review ZIP."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import re
import subprocess
import zipfile
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

OUT=Path(__file__).resolve().parents[1]
REPO=Path(__file__).resolve().parents[4]
cfg=json.loads((OUT/'config.json').read_text())
STUDY=REPO/cfg['study_root'];PRIOR=REPO/cfg['prior_diagnostics']
assert dt.datetime.now(dt.timezone.utc)<dt.datetime.fromisoformat(cfg['deadline_utc'])
assert not (OUT/'REVIEW_PACKAGE.zip').exists(),'Do not overwrite a completed review archive'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read_csv(path):return pd.read_csv(path,dtype={'sample_id':str,'recording_id':str,'segment_id':str})

# New table-consistency checks reuse metric receipts instead of repeating metric/model suites.
metrics=read_csv(PRIOR/'tables/assessment_metrics.csv')
overlaps=read_csv(OUT/'tables/cross_modality_error_overlap_at_0_5.csv')
for (condition,branch,truth),g in overlaps.groupby(['condition','branch','failure']):
    old=metrics[(metrics.condition==condition)&(metrics.branch==branch)&(metrics.scope=='pooled')].iloc[0]
    assert int(g.samples.sum())==(509 if truth else 4021)
    count=int(g[g.branch_correct].samples.sum())
    assert count==(int(old.TP_at_0_5) if truth else int(old.TN_at_0_5))
ranks=read_csv(OUT/'tables/failure_rank_direction_combinations.csv')
prior_changes=read_csv(PRIOR/'tables/paired_AP_and_Brier_changes.csv')
for (frames,scope),g in ranks.groupby(['frames','rank_scope']):
    assert int(g.failures.sum())==509
    for branch,field in [('visual','visual_global_AP_contribution_change_reused'),('F2','fusion_global_AP_contribution_change_reused')]:
        target=prior_changes[(prior_changes.frames==frames)&(prior_changes.scope=='pooled')&(prior_changes.branch==branch)].AP_change.iloc[0]
        assert abs(g[field].sum()-target)<1e-12

# Validate the new weighted-AP computation against sklearn for one actual saved draw.
draw=read_csv(STUDY/'comparison/bootstrap_draws.csv').iloc[0]
order=json.loads((STUDY/'comparison/bootstrap_recording_order.json').read_text())
lookup={name:i for i,name in enumerate(order)};counts=np.array(json.loads(draw.recording_multiplicities))
actual_values={}
for cond in ['frozen_16_frames','fine_tuned_32_frames','frozen_32_frames']:
    block=pd.concat([read_csv(STUDY/cond/f'fold_{i:02}'/'assessment_predictions.csv') for i in range(1,6)],ignore_index=True).sort_values('sample_id')
    weights=counts[block.recording_id.map(lookup).to_numpy(int)]
    assert int(weights.sum())==int(draw.weighted_samples) and int(weights@block.failure.to_numpy())==int(draw.weighted_failures)
    for branch,col in [('visual','p_visual'),('fused','p_fused')]:
        actual_values[(cond,branch)]=average_precision_score(block.failure,block[col],sample_weight=weights)
rep=read_csv(OUT/'tables/missing_contrast_replicates_from_original_draws.csv')
for right,tag in [('frozen_32_frames','fine_tuned32_minus_frozen32'),('frozen_16_frames','fine_tuned32_minus_frozen16')]:
    for branch in ['visual','fused']:
        expected=actual_values[('fine_tuned_32_frames',branch)]-actual_values[(right,branch)]
        actual=rep[(rep.replicate==int(draw.replicate))&(rep.contrast==branch+':'+tag)].AP_difference.iloc[0]
        assert abs(expected-actual)<1e-12

# Include numerical source artifacts, never raw data, feature caches or model weights.
input_manifest=json.loads((OUT/'provenance/input_manifest.json').read_text())
bundle=[]
original_files=[]
for cond in ['frozen_16_frames','fine_tuned_16_frames','frozen_32_frames','fine_tuned_32_frames']:
    for i in range(1,6):
        fold=f'fold_{i:02}'
        original_files.extend([STUDY/cond/fold/'assessment_predictions.csv',STUDY/cond/fold/'F2_stacker.json',STUDY/cond/fold/'outer_assessment/visual_fit/calibrator.json'])
original_files.extend(STUDY/x for x in ['comparison/bootstrap_draws.csv','comparison/bootstrap_recording_order.json','execution_policy.json','config/resolved_config.json','source/evaluation.py'])
for p in original_files:
    data=p.read_bytes();key=str(p.relative_to(REPO));identity=hashlib.sha256(data).hexdigest()
    if key in input_manifest:assert input_manifest[key]['sha256']==identity
    else:input_manifest[key]={'bytes':len(data),'sha256':identity}
    target=OUT/'original_inputs'/p.relative_to(STUDY);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    bundle.append({'source':key,'packet_path':str(target.relative_to(OUT)),'sha256':identity})
(OUT/'provenance/input_manifest.json').write_text(json.dumps(input_manifest,indent=2)+'\n')
(OUT/'provenance/bundled_original_input_index.json').write_text(json.dumps(bundle,indent=2)+'\n')

before=json.loads((OUT/'provenance/existing_file_metadata_before.json').read_text())
after={str(p):{'size':p.stat().st_size,'mtime_ns':p.stat().st_mtime_ns} for name in ['run_01_two_epoch_finetuning','fine_tuning_diagnostics_01'] for p in (Path('00_experiments/visual_backbone_one_day')/name).rglob('*') if p.is_file()}
assert before==after,'An earlier packet changed'
for key,meta in input_manifest.items():assert sha(REPO/key)==meta['sha256'],key
status=subprocess.check_output(['git','status','--short','--branch','--untracked-files=all'],cwd=REPO)
stat=subprocess.check_output(['git','diff','--stat'],cwd=REPO)
prefix=str(OUT.relative_to(REPO))+'/'
def unrelated(s):return [line for line in s.decode().splitlines() if prefix not in line]
assert unrelated(status)==unrelated((OUT/'provenance/git_status_before.txt').read_bytes())
assert stat==(OUT/'provenance/git_diff_stat_before.txt').read_bytes()
(OUT/'provenance/git_status_after.txt').write_bytes(status)
(OUT/'provenance/git_diff_stat_after.txt').write_bytes(stat)
finished=dt.datetime.now(dt.timezone.utc)
elapsed=(finished-dt.datetime.fromisoformat(cfg['started_utc'])).total_seconds()
assert elapsed<1800
state={'status':'COMPLETE','scope':'Missing saved-artifact diagnostics and review packaging only','finished_utc':finished.isoformat(),
       'elapsed_session_seconds_before_archive':elapsed,'previous_study_preserved':True,'previous_diagnostic_packet_preserved':True,
       'new_training_fits':0,'new_inference':0,'new_model_variants':0,'new_exploratory_intervals':4,'mechanism':'UNRESOLVED',
       'review':'Self-review','follow_up_launched':False,'historical_Task4':'EXCLUDED'}
(OUT/'STATE.json').write_text(json.dumps(state,indent=2)+'\n')
receipt={'passed':True,'new_overlap_counts_reconcile_with_reused_threshold_metrics':True,'rank_cells_sum_to_509_failures':True,
         'reused_AP_contributions_reconcile_in_new_rank_groups':True,'new_missing_intervals_verified_on_one_actual_saved_draw':True,
         'source_input_hashes_checked':len(input_manifest),'earlier_packet_files_metadata_unchanged':len(before),
         'unrelated_dirty_tree_unchanged':True,'no_completed_model_suite_or_plot_regeneration':True,
         'plain_language_summary_words':len((OUT/'README_FIRST.md').read_text().split()),
         'elapsed_session_seconds_before_archive':elapsed,'review_type':'Self-review; independent scientific review not claimed'}
assert receipt['plain_language_summary_words']<=200
(OUT/'checks/packet_verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
for path in [OUT/'README_FIRST.md',OUT/'DIAGNOSTIC_REPORT.md']:
    for link in re.findall(r'\]\(([^)]+)\)',path.read_text()):
        target=path.parent/link
        assert target.exists() or target==OUT/'REVIEW_PACKAGE.zip',(path,link)
files=[]
for p in sorted(OUT.rglob('*')):
    if p.is_file() and p.name not in ['output_manifest.json','REVIEW_PACKAGE.zip','archive_verification.json']:
        files.append({'path':str(p.relative_to(OUT)),'bytes':p.stat().st_size,'sha256':sha(p)})
manifest={'files':files,'exclusions':['This output manifest excludes itself','REVIEW_PACKAGE.zip','checks/archive_verification.json'],
          'payload_bytes':sum(x['bytes'] for x in files),'created_utc':dt.datetime.now(dt.timezone.utc).isoformat()}
(OUT/'provenance/output_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
archive=OUT/'REVIEW_PACKAGE.zip'
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for row in files:z.write(OUT/row['path'],row['path'])
    z.write(OUT/'provenance/output_manifest.json','provenance/output_manifest.json')
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for row in files:assert hashlib.sha256(z.read(row['path'])).hexdigest()==row['sha256']
guard_finished=dt.datetime.now(dt.timezone.utc)
assert guard_finished<dt.datetime.fromisoformat(cfg['deadline_utc'])
verification={'passed':True,'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),'CRC_passed':True,
              'payload_hashes_verified':len(files),'completed_utc':guard_finished.isoformat(),
              'total_session_seconds':(guard_finished-dt.datetime.fromisoformat(cfg['started_utc'])).total_seconds()}
(OUT/'checks/archive_verification.json').write_text(json.dumps(verification,indent=2)+'\n')
assert sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())<cfg['max_new_storage_bytes']
print(json.dumps({'packet_verification':receipt,'archive_verification':verification},indent=2))
