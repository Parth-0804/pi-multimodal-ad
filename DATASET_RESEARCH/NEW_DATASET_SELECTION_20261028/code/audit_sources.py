"""Recompute native counts and identity joins from original released metadata."""
import csv
import io
import json
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from acquisition import ROOT

EVIDENCE=ROOT/'source_evidence'
CHECKS=ROOT/'checks'


def load(path): return json.loads(path.read_text())
def save(name, data): (CHECKS/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
def table(name, rows):
    if not rows: return
    with (CHECKS/name).open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def audit_robofac():
    files={x['rfilename']:x for x in load(EVIDENCE/'robofac/dataset_files_with_sizes.json')['siblings']}
    base=EVIDENCE/'robofac/files'
    trajectories=[];issues=[]
    for path in sorted(p for p in files if p.startswith('simulation_data/') and p.endswith('.json')):
        try: doc=load(base/path)
        except Exception as exc: issues.append({'source':path,'error':str(exc)});continue
        h5=path[:-5]+'.h5'
        seen=set()
        for e in doc.get('episodes',[]):
            uid=e.get('unique_id');eid=e.get('episode_id')
            video=str(Path(path).parent/(str(uid)+'.mp4'))
            trajectories.append({'source':path,'episode_id':eid,'unique_id':uid,'success':e.get('success'),
                'episode_seed':e.get('episode_seed'),'elapsed_steps':e.get('elapsed_steps'),
                'env_id':doc.get('env_info',{}).get('env_id'), 'scene':path.split('/')[2] if '/success_data/' in path else path.split('/')[1],
                'h5':h5,'h5_listed':h5 in files,'video':video,'video_listed':video in files})
            if eid in seen: issues.append({'source':path,'duplicate_episode_id':eid})
            seen.add(eid)
    by_uid=defaultdict(list)
    for row in trajectories: by_uid[row['unique_id']].append(row)
    qa={};qa_record_counts=Counter();qa_fail_answers=defaultdict(set);questions=set();test_contradictions=[]
    for path in sorted(p for p in files if p.startswith('test_qa_') and p.endswith('.json')):
        doc=load(base/path)
        for uid,record in doc.items():
            video=record['video'];domain='realworld' if 'realworld' in path else 'simulation'
            qa_record_counts[domain]+=1
            entry=qa.setdefault((domain,video),{'uid':set(),'tasks':set(),'answers':set(),'sources':set()})
            entry['uid'].add(uid);entry['tasks'].add(record.get('task'));entry['sources'].add(path)
            fd=record.get('annos',{}).get('Failure detection',[])
            for turn in fd:
                if turn.get('from')=='human':questions.add(turn['value'].replace('<image>','').replace('<video>','').strip())
                if turn.get('from')=='assistant':entry['answers'].add(turn['value'].strip());qa_fail_answers[domain].add(turn['value'].strip())
    testrows=[]
    for (domain,video),entry in sorted(qa.items()):
        answers=entry['answers'];label=next(iter(answers)) if len(answers)==1 else None
        full=('realworld_data/' if domain=='realworld' else 'simulation_data/')+video
        testrows.append({'domain':domain,'video':full,'video_listed':full in files,'native_failure_detection_answer':label,
            'answer_variants':' | '.join(sorted(answers)),'uuid_count':len(entry['uid']), 'uuid':sorted(entry['uid'])[0],
            'source_files':' | '.join(sorted(entry['sources']))})
        if len(answers)>1:test_contradictions.append({'video':full,'answers':sorted(answers)})
    # Only exact native detection prompts are used. Other QA text is not converted to labels.
    training=load(base/'training_qa.json');train_videos=set();train_outcomes=defaultdict(set);prompt_counts=Counter()
    for record in training:
        train_videos.add(record['video'])
        conv=record.get('conversations',[])
        if len(conv)<2:continue
        prompt=conv[0]['value'].replace('<image>','').replace('<video>','').strip()
        if prompt in questions:
            answer=conv[1]['value'].strip();train_outcomes[record['video']].add(answer);prompt_counts[answer]+=1
    def outcome(answer):
        if answer is None:return None
        a=answer.lower().strip().rstrip('.')
        return True if a=='yes' else False if a=='no' else None
    qa_comparison=[]
    for row in testrows:
        if row['domain']!='simulation':continue
        native=outcome(row['native_failure_detection_answer'])
        matches=[x for x in by_uid[row['uuid']] if x['video']==row['video']]
        if len(matches)==1 and native is not None and type(matches[0]['success']) is bool:
            qa_comparison.append({'video':row['video'],'qa_success':native,'json_success':matches[0]['success'],
                'agreement':native==matches[0]['success'],'source':matches[0]['source'],'episode_id':matches[0]['episode_id']})
    stats={
        'revision':load(EVIDENCE/'robofac/dataset_api.json')['sha'],
        'listed_files':len(files),'total_release_bytes':sum(x['size'] for x in files.values()),
        'json_trajectory_files':sum(p.startswith('simulation_data/') and p.endswith('.json') for p in files),
        'trajectory_records':len(trajectories),'native_success_counts':dict(Counter(str(x['success']) for x in trajectories)),
        'unique_trajectory_uuids':len(by_uid),'duplicate_trajectory_uuid_count':sum(len(v)>1 for v in by_uid.values()),
        'missing_trajectory_videos':sum(not x['video_listed'] for x in trajectories),
        'missing_trajectory_h5':sum(not x['h5_listed'] for x in trajectories),
        'realworld_h5_listed':sum(p.startswith('realworld_data/') and p.endswith('.h5') for p in files),
        'video_domain_counts':dict(Counter(p.split('/')[0] for p in files if p.endswith('.mp4'))),
        'test_record_occurrences_by_domain':dict(qa_record_counts),
        'test_unique_videos':dict(Counter(x['domain'] for x in testrows)),
        'test_detection_answers':{domain:dict(Counter(x['native_failure_detection_answer'] for x in testrows if x['domain']==domain)) for domain in ['realworld','simulation']},
        'test_detection_conflicts':test_contradictions,
        'qa_success_vs_json_success_comparisons':len(qa_comparison),
        'qa_success_vs_json_success_disagreements':sum(not x['agreement'] for x in qa_comparison),
        'training_QA_records':len(training),'training_unique_videos':len(train_videos),
        'training_exact_native_detection_prompts':dict(prompt_counts),
        'training_detection_unique_video_answers':dict(Counter(' | '.join(sorted(v)) for v in train_outcomes.values())),
        'train_test_video_overlap':len(train_videos&{x['video'].removeprefix('simulation_data/').removeprefix('realworld_data/') for x in testrows}),
        'issues':issues,
    }
    table('robofac_native_trajectory_records.csv',trajectories);table('robofac_test_native_detection_records.csv',testrows)
    table('robofac_qa_json_outcome_comparison.csv',qa_comparison);save('robofac_counts.json',stats)
    return stats


def audit_cria():
    files={x['rfilename']:x for x in load(EVIDENCE/'cria/dataset_files_with_sizes.json')['siblings']}
    base=EVIDENCE/'cria/files';rows=[];taskstats=[];errors=[];groups=defaultdict(Counter);frame_count=Counter();sourcepaths=Counter()
    for path in sorted(p for p in files if p.endswith('/meta/annotation.json')):
        task=path.removesuffix('/meta/annotation.json');doc=load(base/path)
        info=load(base/task/'meta/info.json')
        eps=[json.loads(line) for line in (base/task/'meta/episodes.jsonl').read_text().splitlines() if line.strip()]
        by_id={e['episode_index']:e for e in eps}
        if len(eps)!=len(by_id):errors.append([task,'duplicate episode_index'])
        local=[]
        for key,a in doc['episodes'].items():
            eid=a['episode_index'];meta=by_id.get(eid,{})
            n=a['num_frames'];ranges=a.get('anomaly',{}).get('manual',{}).get('ranges')
            mask=set();range_errors=[]
            if ranges is None:errors.append([task,eid,'missing manual ranges']);ranges=[]
            for start,end in ranges:
                if not 0<=start<=end<n:range_errors.append([start,end])
                mask.update(range(start,end+1))
            declared=a.get('anomaly',{}).get('manual',{}).get('failure_frame_count')
            if declared!=len(mask):errors.append([task,eid,'manual anomaly count mismatch',declared,len(mask)])
            for field,expected in [('episode_label',a.get('episode_label')),('length',n),('source',a.get('source'))]:
                if meta.get(field)!=expected:errors.append([task,eid,'metadata mismatch',field])
            source=meta.get('source_h5','');sourcepaths[source]+=1
            date_match=re.search(r'_(20\d{6})_\d{6}\.h5$',source)
            date=date_match.group(1) if date_match else 'UNKNOWN'
            all_videos=[f'{task}/videos/{view}/chunk-{eid//1000:03d}/episode_{eid:06d}.mp4' for view in ['wrist','side_1','side_2']]
            parquet=f'{task}/'+a['parquet_path']
            missing=[p for p in [parquet]+all_videos if p not in files]
            if missing:errors.append([task,eid,'missing listed files',missing])
            if range_errors:errors.append([task,eid,'invalid ranges',range_errors])
            label=a.get('episode_label')
            if label not in [0,1]:errors.append([task,eid,'invalid outcome',label])
            row={'task':task,'episode_index':eid,'episode_label':label,'anomaly_present':bool(mask),
                'anomaly_events':len(ranges),'anomalous_frames':len(mask),'nominal_frames':n-len(mask),'num_frames':n,
                'source':meta.get('source'),'control_group':meta.get('control_group'),'candidate_recording_date':date,
                'source_h5_identity':source,'reviewed':a.get('reviewed'),'parquet':parquet,
                'wrist_video':all_videos[0],'source_annotation':path,'missing_files':len(missing)}
            rows.append(row);local.append(row)
            groups[(task,date)][f'outcome_{label}']+=1;groups[(task,date)]['anomaly_present' if mask else 'no_anomaly']+=1
            frame_count['anomalous']+=len(mask);frame_count['nominal']+=n-len(mask)
        taskstats.append({'task':task,'episodes':len(local),'failed_outcome':sum(x['episode_label']==0 for x in local),
            'successful_outcome':sum(x['episode_label']==1 for x in local),'anomaly_containing':sum(x['anomaly_present'] for x in local),
            'anomaly_free':sum(not x['anomaly_present'] for x in local),'anomaly_events':sum(x['anomaly_events'] for x in local),
            'anomalous_frames':sum(x['anomalous_frames'] for x in local),'nominal_frames':sum(x['nominal_frames'] for x in local),
            'candidate_days':len({x['candidate_recording_date'] for x in local}),
            'info_total_episodes':info['total_episodes'],'info_total_frames':info['total_frames']})
        if info['total_episodes']!=len(local) or info['total_frames']!=sum(x['num_frames'] for x in local):errors.append([task,'info count mismatch'])
    cross=Counter((x['episode_label'],x['anomaly_present']) for x in rows)
    out={'revision':load(EVIDENCE/'cria/dataset_api.json')['sha'],'total_release_bytes':sum(x['size'] for x in files.values()),
        'episodes':len(rows),'tasks':len(taskstats),'outcome_counts':dict(Counter(str(x['episode_label']) for x in rows)),
        'anomaly_containing':sum(x['anomaly_present'] for x in rows),'anomaly_free':sum(not x['anomaly_present'] for x in rows),
        'anomaly_events':sum(x['anomaly_events'] for x in rows),'frame_counts_from_manual_ranges_inclusive':dict(frame_count),
        'outcome_vs_anomaly':{f'outcome_{k[0]}__anomaly_{k[1]}':v for k,v in cross.items()},
        'source_counts':dict(Counter(x['source'] for x in rows)), 'reviewed_counts':dict(Counter(str(x['reviewed']) for x in rows)),
        'duplicate_source_h5':{k:v for k,v in sourcepaths.items() if v>1},'errors':errors,
        'task_summary':taskstats}
    table('cria_native_episode_records.csv',rows);table('cria_counts_by_task.csv',taskstats)
    table('cria_candidate_task_day_groups.csv',[{'task':k[0],'date':k[1],'failed':v['outcome_0'],'successful':v['outcome_1'],'anomaly_containing':v['anomaly_present'],'anomaly_free':v['no_anomaly']} for k,v in sorted(groups.items())])
    save('cria_counts.json',out);return out


def audit_failure():
    inventory=load(CHECKS/'failure_archive_inventory.json');members={x['name']:x for x in inventory}
    rgb=defaultdict(set);depth=defaultdict(set);stamps=defaultdict(set);audio={};invalid=[]
    for name in members:
        parts=name.split('/')
        if len(parts)==5 and parts[1] in ['rgb_imgs','depth_imgs']:
            key=(parts[2],parts[3]);stem=Path(parts[4]).stem
            if name.endswith('.png'):rgb[key].add(stem)
            if name.endswith('.tiff'):depth[key].add(stem)
            if name.endswith('.txt'):stamps[key].add(stem)
        if len(parts)==4 and parts[1]=='audio' and name.endswith('.wav'):audio[(parts[2],Path(parts[3]).stem)]=name
    rows=[];stats=[]
    with zipfile.ZipFile(EVIDENCE/'failure/annotation.zip') as archive:
        for name in archive.namelist():
            action=name.removesuffix('_annotation.txt');native=list(csv.DictReader(io.StringIO(archive.read(name).decode())))
            seen=set();local=[]
            for index,row in enumerate(native,start=2):
                key=(action,row['name']);label=int(row['label'])
                if key in seen:invalid.append([action,row['name'],'duplicate annotation'])
                seen.add(key)
                color=rgb.get(key,set());distance=depth.get(key,set());time=stamps.get(key,set())
                out={'action':action,'recording_id':row['name'],'label':label,'source_member':name,'source_line':index,
                    'rgb_frames':len(color),'depth_frames':len(distance),'timestamp_files':len(time),
                    'audio_listed':key in audio,'rgb_depth_stem_mismatches':len(color^distance),
                    'rgb_timestamp_stem_mismatches':len(color^time),
                    'complete_modalities':bool(color and color<=distance and key in audio and color==time)}
                local.append(out);rows.append(out)
            stats.append({'action':action,'annotations':len(local),'failed_label_1':sum(x['label']==1 for x in local),
                'successful_label_0':sum(x['label']==0 for x in local),
                'all_modalities_listed':sum(x['complete_modalities'] for x in local),
                'joined_failure':sum(x['complete_modalities'] and x['label']==1 for x in local),
                'joined_success':sum(x['complete_modalities'] and x['label']==0 for x in local)})
    labeled={(x['action'],x['recording_id']) for x in rows};available=set(rgb)|set(depth)|set(audio)
    out={'annotation_records':len(rows),'native_class_counts':dict(Counter(str(x['label']) for x in rows)),
        'per_action':stats,'audio_files':len(audio),'rgb_recordings':len(rgb),'depth_recordings':len(depth),
        'all_modalities_listed_for_annotated':sum(x['complete_modalities'] for x in rows),
        'missing_or_incomplete_annotated_recordings':[x for x in rows if not x['complete_modalities']],
        'unlabeled_available_recordings':[list(x) for x in sorted(available-labeled)],
        'extra_modalities':sorted({x['name'].split('/')[1] for x in inventory if len(x['name'].split('/'))>2}),
        'invalid':invalid,'archive_bytes':10197520375,'archive_uncompressed_bytes':sum(x['bytes'] for x in inventory)}
    table('failure_native_annotation_records.csv',rows);table('failure_counts_by_action.csv',stats);save('failure_counts.json',out);return out


if __name__=='__main__':
    # CRIA code is retained as the historical audit trace, but is not executed.
    for name,func in [('robofac',audit_robofac),('failure',audit_failure)]:
        data=func();print(name,json.dumps({k:v for k,v in data.items() if not isinstance(v,list)},ensure_ascii=False)[:10000])
