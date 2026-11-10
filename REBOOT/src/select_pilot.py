"""Audit native phase records; select only a bounded diagnostic pilot, not labels."""
from pathlib import Path
from collections import Counter
import json
import math
import pandas as pd
from source_audit import ROOT,REPO,RUN,write

PHASES=['Align (pick)','Engage (pick)','Transport','Align (place)','Engage (place)']


def phase_checks(record,actual_length):
 f=record.get('failure',{});p=f.get('originating_phase');bounds=record.get('phase_boundaries',{})
 issues=[]
 tau=[bounds.get('tau_'+str(i)) for i in range(6)]
 if p not in range(1,6):issues.append('originating_phase_outside_explicitly_tested_one_based_1_to_5')
 numeric_bounds=all(isinstance(x,(int,float)) and math.isfinite(x) for x in tau)
 if not numeric_bounds or any(a>=b for a,b in zip(tau,tau[1:])):issues.append('nonmonotonic_or_missing_phase_boundaries')
 if record.get('duration_frames')!=actual_length:issues.append('declared_duration_differs_from_released_episode_length')
 if not numeric_bounds or tau[0]!=0 or tau[-1]>actual_length:issues.append('phase_boundaries_outside_actual_episode')
 a=f.get('induced_at_frame');b=f.get('recovery_started_at_frame')
 if not isinstance(a,int) or not isinstance(b,int) or not 0<=a<b<=actual_length:issues.append('invalid_induction_recovery_order_or_bounds')
 one_based_consistent=p in range(1,6) and numeric_bounds and isinstance(a,int) and tau[p-1]<=a<tau[p]
 if not one_based_consistent:issues.append('induction_not_inside_declared_phase_under_one_based_interpretation')
 return issues,one_based_consistent


def main():
 inventory=json.loads((ROOT/'00_dataset_overview/PINNED_DATASET_INVENTORY.json').read_text())
 sample=next(r for r in inventory if r['repo_id']=='REBOOT26/sample_recovery-demonstration')
 folder=REPO/sample['local_root'];ann=json.loads((folder/'meta/phase.json').read_text())
 episodes=pd.concat([pd.read_parquet(p) for p in (folder/'meta/episodes').rglob('*.parquet')]).set_index('episode_index')
 rows=[]
 for e in ann['episodes']:
  index=int(e['episode_index']);actual=int(episodes.loc[index,'length']);issues,consistent=phase_checks(e,actual)
  rows.append({'repo_id':sample['repo_id'],'revision':sample['revision'],'episode_index':index,'declared_repo_id':e['repo_id'],
   'repo_id_matches':e['repo_id']==sample['repo_id'],'declared_duration_frames':e['duration_frames'],'actual_length':actual,
   'originating_phase_native':e['failure']['originating_phase'],'failure_mode_native':e['failure']['failure_mode'],
   'induced_at_frame_native':e['failure']['induced_at_frame'],'recovery_started_at_frame_native':e['failure']['recovery_started_at_frame'],
   'operator_id_native':e.get('operator_id'),'collection_session_native':e.get('collection_session'),
   'one_based_phase_onset_consistent':consistent,'issues':issues,'strict_training_eligible':False,
   'binary_interval_ground_truth_created':False,'annotation':e})
 write(ROOT/'02_labels_and_annotations/NATIVE_PHASE_RECORD_AUDIT.json',rows)
 pd.DataFrame([{k:(json.dumps(v) if isinstance(v,(list,dict)) else v) for k,v in r.items() if k!='annotation'} for r in rows]).to_csv(ROOT/'02_labels_and_annotations/NATIVE_PHASE_RECORD_AUDIT.csv',index=False)
 selected=[];counts=[]
 for phase in range(1,5):
  candidates=[r for r in rows if r['originating_phase_native']==phase]
  consistent=[r for r in candidates if r['one_based_phase_onset_consistent']]
  for r in consistent[:2]:
   start=max(0,r['induced_at_frame_native']-30);end=min(r['actual_length'],r['recovery_started_at_frame_native']+30)
   selected.append({'repo_id':sample['repo_id'],'revision':sample['revision'],'local_root':sample['local_root'],
    'episode_index':r['episode_index'],'native_annotation':r['annotation'],'investigated_phase':PHASES[phase-1],
    'window_start_frame':start,'window_end_frame_exclusive':end,'label_status':'UNVERIFIED_NATIVE_ANNOTATION_DIAGNOSTIC_ONLY',
    'source_collection':'native_episode_type_recovery','binary_target':None,
    'selection':'First two source-ID-ordered annotation candidates with onset inside phase under explicit one-based diagnostic interpretation'})
  counts.append({'phase':PHASES[phase-1],'native_failure_candidates':len(candidates),'phase_onset_consistent_diagnostic_candidates':len(consistent),
    'verified_native_normal_phase_intervals':0,'verified_matched_normal_failure_pairs':0,'requested_pairs':5,'selected_diagnostic_recovery_episodes':min(2,len(consistent))})
 expert=next(r for r in inventory if r['repo_id']=='REBOOT26/16mm-cylinder_install')
 folder=REPO/expert['local_root'];e=pd.concat([pd.read_parquet(p) for p in (folder/'meta/episodes').rglob('*.parquet')]).set_index('episode_index')
 for index in [0,1]:
  selected.append({'repo_id':expert['repo_id'],'revision':expert['revision'],'local_root':expert['local_root'],'episode_index':index,
    'native_annotation':None,'investigated_phase':'whole_episode_context_phase_labels_not_released',
    'window_start_frame':0,'window_end_frame_exclusive':int(e.loc[index,'length']),
    'label_status':'EXPERT_COLLECTION_CANDIDATE_NO_VERIFIED_PHASE_NORMAL_LABEL','source_collection':'non_recovery_named_repository',
    'binary_target':None,'selection':'First two expert-named same-object/install repository episodes; not claimed as verified phase-matched negatives'})
 write(ROOT/'00_dataset_overview/PILOT_SELECTION.json',selected)
 pd.DataFrame(counts).to_csv(ROOT/'02_labels_and_annotations/PHASE_PILOT_SUPPORT_COUNTS.csv',index=False)
 summary={'release_repositories':len(inventory),'sum_repository_episode_counts_including_sample_not_unique_demonstrations':sum(r['total_episodes'] for r in inventory),
  'project_claim_demonstrations':2160,'repositories_with_released_phase_annotation_files':sum(bool(r['annotation_candidates']) for r in inventory),
  'native_annotation_records':len(rows),'source_annotation_dataset_name':ann['dataset'],'resolved_repo_name':sample['repo_id'],
  'source_declared_durations':dict(Counter(str(r['declared_duration_frames']) for r in rows)),
  'actual_released_episode_lengths':dict(Counter(str(r['actual_length']) for r in rows)),
  'issue_counts':dict(Counter(issue for r in rows for issue in r['issues'])),'native_phase_values':dict(Counter(str(r['originating_phase_native']) for r in rows)),
  'operators_in_annotation':dict(Counter(r['operator_id_native'] for r in rows)),'sessions_in_annotation':dict(Counter(r['collection_session_native'] for r in rows)),
  'strict_eligible_binary_training_examples':0,'verified_matched_pairs':0,'diagnostic_episodes_selected':len(selected),
  'selection_does_not_invent_binary_or_framewise_targets':True,'one_based_phase_indexing':'Tested for diagnostics only; not silently corrected or certified'}
 write(ROOT/'02_labels_and_annotations/LABEL_GATE_SUMMARY.json',summary)
 print(json.dumps(summary,indent=2),flush=True)


if __name__=='__main__':main()
