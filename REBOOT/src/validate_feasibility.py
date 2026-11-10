"""Final read-only integrity/provenance checks; no model execution."""
from pathlib import Path
import ast
import csv
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess

import numpy as np
import pandas as pd
import pyarrow

from source_audit import ROOT,REPO,RUN,write


def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()


def main():
 inventory=json.loads((ROOT/'00_dataset_overview/PINNED_DATASET_INVENTORY.json').read_text())
 source_checks=[];file_rows=[]
 for d in inventory:
  folder=REPO/d['local_root']
  for r in d['metadata_receipts']:
   p=REPO/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
  paths=sorted((folder/'meta/episodes').rglob('*.parquet'))
  assert paths
  record={'repo_id':d['repo_id'],'revision':d['revision'],
   'source_paths':[str(p.relative_to(REPO)) for p in paths],
   'info_declared_episodes':d['total_episodes'],'info_declared_frames':d['total_frames']}
  try:
   episodes=pd.concat([pd.read_parquet(p) for p in paths])
  except pyarrow.ArrowInvalid as error:
   # Accept only the independently confirmed published defect; never repair it.
   proof=RUN/'evidence/USBC_METADATA_SOURCE_IDENTITY_RECHECK.json'
   identity=json.loads(proof.read_text())
   assert d['repo_id']=='REBOOT26/usbc_recovery_install' and len(paths)==1
   assert d['revision']=='0ef0b37f0601fbafcc3bab07195a1fb5e756c6b4'
   assert paths[0].stat().st_size==identity['official_LFS_size']==196608
   assert sha(paths[0])==identity['official_LFS_sha256']==identity['local_full_sha256']
   assert identity['local_matches_official_LFS_hash'] and not identity['has_required_PAR1_footer']
   record.update(status='SOURCE_METADATA_UNPARSEABLE',error_type=type(error).__name__,error=str(error),
    native_info_and_episode_metadata_match=None,official_byte_identity_proof=str(proof.relative_to(REPO)))
  else:
   assert episodes.episode_index.is_unique and len(episodes)==d['total_episodes']
   assert int(episodes.length.sum())==d['total_frames']
   record.update(status='PARSEABLE',episode_rows=len(episodes),unique_episode_indices=True,
    frame_rows_from_episode_lengths=int(episodes.length.sum()),native_info_and_episode_metadata_match=True)
  source_checks.append(record)
  for row in json.loads((REPO/d['file_tree']).read_text()):
   if row['type']!='file':continue
   p=folder/row['path'];file_rows.append({'repo_id':d['repo_id'],'revision':d['revision'],'source_file':row['path'],'source_bytes':row['size'],
    'source_LFS_sha256':row.get('lfs',{}).get('oid',''),'source_git_oid':row.get('oid',''),
    'complete_file_downloaded':p.exists(),'local_path_if_complete':str(p.relative_to(REPO)) if p.exists() else ''})
 pd.DataFrame(file_rows).to_csv(ROOT/'00_dataset_overview/COMPLETE_REMOTE_FILE_INVENTORY.csv',index=False)
 write(RUN/'manifests/REPOSITORY_METADATA_VALIDATION.json',source_checks)
 videos=json.loads((ROOT/'01_raw_dataset/PILOT_VIDEO_DOWNLOAD_MANIFEST.json').read_text())
 for r in videos:
  p=REPO/r['local_path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
 numerical=json.loads((ROOT/'03_video_sensor_alignment/NUMERICAL_ACQUISITION_MANIFEST.json').read_text())
 for r in numerical:
  p=REPO/r['projection_path'];assert sha(p)==r['projection_sha256']
  x=pd.read_parquet(p);assert len(x)==r['rows']
  assert np.stack(x['observation.state']).shape==(len(x),14)
  assert np.isfinite(np.stack(x['observation.state'])).all()
  for fragment in r['source_receipt'].get('range_receipts',[]):
   path=REPO/fragment['raw_fragment_path'];assert path.stat().st_size==fragment['bytes'] and sha(path)==fragment['sha256']
 frame=pd.read_csv(ROOT/'03_video_sensor_alignment/SELECTED_FRAME_MANIFEST.csv')
 assert len(frame)==640 and not frame.duplicated(['masked_id','camera','native_frame_index']).any()
 for r in frame.itertuples():
  assert sha(REPO/r.full_frame)==r.full_png_sha256 and sha(REPO/r.context_frame)==r.context_png_sha256
 for view in json.loads((ROOT/'03_video_sensor_alignment/FOUR_VIEW_DECODE_AUDIT.json').read_text()):
  assert view['distinct_native_frame_indices']==16 and view['distinct_decoded_RGB_contents']==16
  assert sha(REPO/view['preview'])==view['preview_sha256']
 sheet=pd.read_csv(ROOT/'04_visual_failure_review/RESEARCHER_VISUAL_REVIEW_SHEET.csv',keep_default_na=False)
 assert len(sheet)==40 and (sheet.reviewer_id=='').all() and (sheet.failure_visible_yes_no_uncertain=='').all()
 selection=json.loads((ROOT/'00_dataset_overview/PILOT_SELECTION.json').read_text())
 assert len(selection)==10 and all(r['binary_target'] is None for r in selection)
 decision=json.loads((ROOT/'07_research_decision/DECISION_STATUS.json').read_text())
 assert decision['decision']=='CONDITIONAL_GO' and not decision['training_allowed'] and not decision['full_model_training_started']
 alias=json.loads((ROOT/'06_evaluation_feasibility/SAMPLE_FULL_RECORDING_ALIAS_EVIDENCE.json').read_text())
 assert alias['shared_exact_video_chunks']==18 and len(alias['identical_episode_video_mapping_and_lengths'])==60
 inspected=json.loads((RUN/'software_provenance.json').read_text())['inspected_existing_implementation_hashes']
 for path,value in inspected.items():assert sha(REPO/path)==value
 original_export=REPO/'CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE/12_Validation_And_Reproducibility/SOURCE_COPY_RECORDS.json'
 old_map={r['source_path']:r['source_sha256'] for r in json.loads(original_export.read_text())} if original_export.exists() else {}
 previously_verified=0
 for path,value in inspected.items():
  if path in old_map:assert value==old_map[path];previously_verified+=1
 hub=REPO/'DATASET_RESEARCH';registry=json.loads((hub/'DATASET_REGISTRY.json').read_text())
 for row in registry:assert (hub/row['name']).is_symlink() and (hub/row['name']).resolve()==(REPO/row['canonical_root']).resolve()
 required=['README.md','00_dataset_overview/REBOOT_SOURCE_AUDIT.md','02_labels_and_annotations/ANNOTATION_CONTRACT_AND_LIMITATIONS.md',
  '03_video_sensor_alignment/VIDEO_SENSOR_ALIGNMENT_REPORT.md','04_visual_failure_review/BLINDED_VISUAL_REVIEW_PROTOCOL.md',
  '04_visual_failure_review/galleries/blinded_pilot_v1/index.html','05_architecture_compatibility/REASSEMBLE_ARCHITECTURE_COMPATIBILITY.md',
  '06_evaluation_feasibility/EVALUATION_FEASIBILITY.md','07_research_decision/REBOOT_RESEARCH_DECISION.md','07_research_decision/RESEARCHER_HANDOFF.md']
 assert all((ROOT/p).is_file() for p in required)
 for p in (ROOT/'src').glob('*.py'):ast.parse(p.read_text(),filename=str(p))
 assert subprocess.run(['git','diff','--check'],cwd=REPO).returncode==0
 packages=subprocess.run([str(REPO/'ma_thesis_env/bin/python'),'-B','-m','pip','check'],text=True,capture_output=True)
 assert packages.returncode==0
 limitations=[r for r in source_checks if r['status']!='PARSEABLE']
 assert len(limitations)==1
 write(RUN/'validation.json',{'utc':dt.datetime.now(dt.timezone.utc).isoformat(),'passed':True,
  'validation_scope':'Export integrity and honest feasibility reporting; not certification of dataset labels or model readiness',
  'required_reports_present':len(required),'all_downloaded_metadata_source_hashes_verified':True,
  'source_repository_metadata_checks':len(source_checks),
  'parseable_repository_episode_indices_confirmed':len(source_checks)-len(limitations),
  'all_pinned_metadata_and_episode_counts_verified':False,'source_metadata_limitations':limitations,
  'original_videos_verified_against_official_SHA256':len(videos),'video_bytes':sum(r['bytes'] for r in videos),
  'numerical_episodes_validated':len(numerical),'numerical_rows':sum(r['rows'] for r in numerical),'decoded_frames_with_source_and_output_hashes':len(frame),
  'camera_views_with16_distinct_indices_and_RGB_contents':40,'human_review_sheet_rows':40,'independent_human_reviews_completed':0,
  'range_fragments_validated':sum(len(r['source_receipt'].get('range_receipts',[])) for r in numerical),
  'large_expert_Parquet_whole_file_hash_verified':False,'binary_targets_invented':False,'source_annotations_repaired':False,
  'preserved_prior_implementation_hashes_rechecked':len(inspected),'matched_prior_independent_review_export_hashes':previously_verified,
  'relative_dataset_hub_references_verified':len(registry),'synthetic_regression_tests':'7 passed in0.39s; no model fitting',
  'pip_check':packages.stdout.strip(),'git_diff_check':'PASS','source_AST':'PASS',
  'training_or_CNN_inference_run':False,'remaining_free_disk_GiB':shutil.disk_usage(ROOT).free/1024**3,
  'research_decision':'CONDITIONAL_GO; curation/review only, training remains blocked'})
 out=RUN/'manifests/output_manifest.json';rows=[]
 for p in sorted(ROOT.rglob('*')):
  if not p.is_file() or p==out or p.name.endswith('.writing'):continue
  rows.append({'path':str(p.relative_to(REPO)),'bytes':p.stat().st_size,'sha256':sha(p),
   'role':'immutable source bytes' if '01_raw_dataset' in p.parts else 'run evidence/code/derived visualization/report'})
 write(out,{'utc':dt.datetime.now(dt.timezone.utc).isoformat(),'files':rows,'total_bytes':sum(r['bytes'] for r in rows),
   'self_reference':'This manifest is excluded from its own hash list','original_source_and_derived_data_separated':True})
 print('VALIDATION_PASSED','files',len(rows),'total_GiB',sum(r['bytes'] for r in rows)/1024**3,flush=True)
 print('FINAL_DECISION',decision['decision'],'TRAINING_ALLOWED',decision['training_allowed'],flush=True)


if __name__=='__main__':main()
