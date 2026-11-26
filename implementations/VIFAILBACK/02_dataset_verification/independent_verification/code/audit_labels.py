"""Count all native outcomes and validate episode/task/file identities."""
import csv,json,re
from collections import Counter,defaultdict
from pathlib import Path
from sources import ROOT


def lines(path):return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
def save(name,data):(ROOT/'checks'/name).write_text(json.dumps(data,indent=2)+'\n')
def table(name,rows):
    with (ROOT/'checks'/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


if __name__=='__main__':
    meta=ROOT/'source_evidence/vifailback/meta'
    ann=lines(meta/'vifailback_annotations.jsonl');eps=lines(meta/'episodes.jsonl');tasks=lines(meta/'tasks.jsonl')
    files={x['rfilename']:x for x in json.loads((ROOT/'source_evidence/vifailback_files.json').read_text())['siblings']}
    by_id={x['episode_index']:x for x in eps};by_instruction={x['task']:x['task_index'] for x in tasks}
    issues=[];rows=[];source_ids=Counter();categories=Counter();task_counts=defaultdict(Counter)
    for a in ann:
        eid=a['episode_index'];e=by_id.get(eid);native=a['annotation'];raw=native.get('failure_detection');outcome=a.get('episode_success')
        normalized='failure' if raw=='yes' else 'success' if raw=='no' else 'INVALID'
        if normalized!=outcome:issues.append([eid,'outcome mismatch',raw,outcome])
        if e is None or a['num_frames']!=e['length']:issues.append([eid,'episode length/identity mismatch'])
        if e and e['tasks']!=[native['task']]:issues.append([eid,'instruction mismatch'])
        if native['task'] not in by_instruction:issues.append([eid,'missing task instruction'])
        for kind in ['avoid','correct']:
            indices=a[kind+'_keyframe_indices']
            if any(not 0<=i<a['num_frames'] for i in indices):issues.append([eid,'invalid '+kind+' keyframe',indices])
        data=f'data/chunk-{eid//1000:03d}/episode_{eid:06d}.parquet'
        videos=[f'videos/chunk-{eid//1000:03d}/observation.images.{view}/episode_{eid:06d}.mp4' for view in ['cam_high','cam_left_wrist','cam_right_wrist']]
        missing=[p for p in [data]+videos if p not in files]
        if missing:issues.append([eid,'missing file',missing])
        category=native.get('failure_type') or 'success';categories[category]+=1
        task_counts[a['source_task']][outcome]+=1
        task_counts[a['source_task']]['category:'+category]+=1
        source_ids[a['source_hdf5']]+=1
        row={'episode_index':eid,'source_task':a['source_task'],'source_episode':a['source_episode'],'source_hdf5':a['source_hdf5'],
            'native_failure_detection':raw,'episode_success':outcome,'failure_type':category,'num_frames':a['num_frames'],
            'task_index':by_instruction.get(native['task']),'avoid_keyframe_indices':json.dumps(a['avoid_keyframe_indices']),
            'correct_keyframe_indices':json.dumps(a['correct_keyframe_indices']),'data':data,'video_high':videos[0],
            'video_left':videos[1],'video_right':videos[2],'listed_pilot_bytes':sum(files[p]['size'] for p in [data]+videos if p in files)}
        rows.append(row)
    counts=[]
    for task,c in sorted(task_counts.items()):
        counts.append({'task':task,'success':c['success'],'failure':c['failure'],
            'gripper_6d_pose':c['category:gripper 6d-pose'],'gripper_state':c['category:gripper state'],'task_planning':c['category:task planning'],
            'human_intervention':c['category:human intervention'],'both_outcomes':c['success']>0 and c['failure']>0})
    taskrows=[]
    for t in tasks:
        members=[x for x in rows if x['task_index']==t['task_index']]
        c=Counter(x['episode_success'] for x in members)
        taskrows.append({'task_index':t['task_index'],'instruction':t['task'],'source_directories':' | '.join(sorted({x['source_task'] for x in members})),
            'success':c['success'],'failure':c['failure'],'both_outcomes':c['success']>0 and c['failure']>0})
    duplicates={}
    for suffix in ['.parquet','.mp4']:
        hashes=defaultdict(list)
        for p,item in files.items():
            if p.endswith(suffix):hashes[item.get('lfs',{}).get('sha256',item['blobId'])].append(p)
        duplicates[suffix]=[v for v in hashes.values() if len(v)>1]
    report={'episodes':len(ann),'unique_episode_indices':len({x['episode_index'] for x in ann}),
        'native_failure_detection':dict(Counter(x['annotation']['failure_detection'] for x in ann)),
        'outcomes':dict(Counter(x['episode_success'] for x in ann)),'failure_categories':dict(categories),
        'source_tasks':len(task_counts),'task_metadata_rows':len(tasks),'unique_instructions':len(by_instruction),
        'source_directories_with_both_outcomes':sum(x['both_outcomes'] for x in counts),
        'tasks_with_both_outcomes':sum(x['both_outcomes'] for x in taskrows),'total_frames':sum(x['num_frames'] for x in ann),
        'min_frames':min(x['num_frames'] for x in ann),'max_frames':max(x['num_frames'] for x in ann),
        'episodes_under16_frames':sum(x['num_frames']<16 for x in ann),'duplicate_source_hdf5_identities':{k:v for k,v in source_ids.items() if v>1},
        'content_identity_duplicates':duplicates,'issues':issues,
        'metadata_fields':sorted(set(k for a in ann for k in a)),
        'original_annotation_fields':sorted(set(k for a in ann for k in a['annotation']))}
    table('all_native_episode_records.csv',rows);table('class_counts_by_source_task.csv',counts);table('class_counts_by_task.csv',taskrows);save('native_label_summary.json',report)
    print(json.dumps({k:v for k,v in report.items() if k not in ['content_identity_duplicates','metadata_fields','original_annotation_fields']},indent=2))
