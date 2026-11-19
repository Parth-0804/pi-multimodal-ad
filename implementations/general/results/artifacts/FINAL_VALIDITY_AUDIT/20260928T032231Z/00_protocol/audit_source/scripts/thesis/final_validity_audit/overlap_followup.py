"""Bounded annotation-only follow-up to positive-overlap findings; no performance refit."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from .common import read,write,textfile,csvfile,table,config_for,freeze_revision
from .numerical import load_cohort

def run(c):
 root=Path(c['run']);out=root/'02_task_and_shortcut_audit';freeze_revision(root,'annotation_overlap_followup');frame,_=load_cohort(c);keys={(r.recording_id,r.segment_id):r for r in frame.itertuples()};rows=[]
 for rid in sorted(frame.recording_id.unique()):
  allsegments=read(Path(c['sources']['inventory'])/'records'/f'{rid}.json')['segments'];segments=sorted([s for s in allsegments if s['valid_interval']],key=lambda x:(x['start'],x['segment_id']))
  with np.load(Path(c['sources']['S1'])/'features'/f'{rid}.npz',allow_pickle=False) as z:
   local={int(v):i for i,v in enumerate(z['row_index'])}
   for i,a in enumerate(segments):
    for b in segments[i+1:]:
     if b['start']>=a['end']:break
     overlap=min(a['end'],b['end'])-b['start']
     if overlap<=0:continue
     ka,kb=(rid,str(a['segment_id'])),(rid,str(b['segment_id']));pa,pb=ka in keys,kb in keys
     rec={'recording_id':rid,'segment_a':str(a['segment_id']),'segment_b':str(b['segment_id']),'action_a':a['action'],'action_b':b['action'],'failure_a':a['failure'],'failure_b':b['failure'],'a_primary':pa,'b_primary':pb,'overlap_seconds':float(overlap),'same_start_end':a['start']==b['start'] and a['end']==b['end'],'same_fold':True,'same_selected_frames':None,'same_statistics':None}
     if pa and pb:
      ia,ib=local[keys[ka].Index],local[keys[kb].Index];rec['same_selected_frames']=bool(np.array_equal(z['frame_indices'][ia],z['frame_indices'][ib]));rec['same_statistics']=bool(np.array_equal(z['statistics'][ia],z['statistics'][ib],equal_nan=True));assert keys[ka].fold==keys[kb].fold
     rows.append(rec)
 csvfile(out/'all_positive_annotation_overlaps.csv',rows)
 primary=[x for x in rows if x['a_primary'] and x['b_primary']]
 summary={'question':'Do observed annotation overlaps cross a fitting boundary or change the task-count interpretation?','reason':'Follow up the timestamp audit before interpreting semantic boundary validity.','method':'All positive interval-overlap pairs among high-level annotations in the148 included recordings; for pairs in the primary cohort compare frozen frame indices and statistics, without re-scoring or deleting anything.','positive_pairs_all_annotations':len(rows),'primary_pairs':primary,'cross_recording_or_outer_fold_overlap':False,'historical_leakage_audit_scope':'src/reassemble/audit_report.py retains duplicate sensor sets only when len(distinct recording IDs)>1; within-recording repeated annotations were not excluded by that gate.','interpretation':'Within-recording repeated/overlapping annotation windows are not cross-fold leakage under recording grouping. Count4530 refers to annotation rows, not4530 distinct nonoverlapping physical actions. Same-action/same-outcome overlap requires annotation adjudication before any claim of unique physical-action counts.','performance_or_labels_modified':False,'adjudication_required_before_annotation_correction':True,'status':'TASK_BOUNDARY_QUALIFICATION_HUMAN_REVIEW_PENDING'}
 write(out/'overlap_followup.json',summary)
 textfile(out/'ANNOTATION_ADJUDICATION_REQUEST.md','# Annotation-boundary adjudication request\n\nThe automated audit found positive overlaps among stored high-level annotations. The following pairs affect the frozen primary cohort:\n\n'+table(pd.DataFrame(primary))+'\nThe two exact repeated input windows and the contained partial window have matching action/outcome labels and remain in the same recording/fold. This is not evidence of cross-fold leakage. The original cross-recording duplicate gate did not claim to exclude within-recording repeated annotations. Preserve the original4530-row evaluation and all uncertainty as defined.\n\nPlease adjudicate whether these are duplicate annotations, intended alternative spans or annotation errors before any correction. Do not remove rows, alter labels or recalculate performance without a separately approved correction protocol. The frozen balanced64-case human review sample is unchanged; these targeted source identities are kept outside its blinded export. No nonoverlap/unique-physical-action claim is supported until adjudication.\n')
 print('OVERLAP_FOLLOWUP_COMPLETE',len(primary),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--run',required=True);a=p.parse_args();run(config_for(a.run))
