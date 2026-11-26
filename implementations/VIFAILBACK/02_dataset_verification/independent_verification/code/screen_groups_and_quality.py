"""Screen duplicate components and quality flags without relabeling sources."""
import csv,hashlib,json,re
from collections import Counter,defaultdict
from sources import ROOT


if __name__=='__main__':
    ann=[json.loads(x) for x in (ROOT/'source_evidence/vifailback/meta/vifailback_annotations.jsonl').open()]
    mapping=defaultdict(list)
    for path in (ROOT/'source_evidence/original/annotated_data').rglob('*.json'):
        if path.name.endswith('.receipt.json'):continue
        for record in json.loads(path.read_text()):mapping[record['video']].append(record)
    original={'original_annotation_files':sum(1 for p in (ROOT/'source_evidence/original/annotated_data').rglob('*.json') if not p.name.endswith('.receipt.json')),
        'original_record_count':sum(len(v) for v in mapping.values()),'native_counts':dict(Counter(x['failure_detection'] for values in mapping.values() for x in values)),
        'duplicate_original_video_identities':sum(len(v)>1 for v in mapping.values()),'converted_records_compared':len(ann),
        'full_nested_original_record_mismatches':[a['episode_index'] for a in ann if len(mapping[a['annotation']['video']])!=1 or mapping[a['annotation']['video']][0]!=a['annotation']]}
    (ROOT/'checks/original_native_annotation_comparison.json').write_text(json.dumps(original,indent=2)+'\n')
    stats=[json.loads(x) for x in (ROOT/'source_evidence/vifailback/meta/episodes_stats.jsonl').open()];fingerprints=defaultdict(list);quality=[]
    keys=['observation.state','observation.velocity','observation.effort']
    for row in stats:
        schema={k:row['stats'][k] for k in keys};signature=hashlib.sha256(json.dumps(schema,sort_keys=True).encode()).hexdigest();fingerprints[signature].append(row['episode_index'])
        quality.append({'episode_index':row['episode_index'],**{k:sum(float(hi)-float(lo)>1e-8 for lo,hi in zip(schema[k]['min'],schema[k]['max'])) for k in keys}})
    duplicate=json.loads((ROOT/'checks/native_label_summary.json').read_text())['content_identity_duplicates']['.mp4']
    components=set(tuple(sorted({int(re.search(r'episode_(\d+)',p)[1]) for p in paths})) for paths in duplicate)
    no_motion=[x['episode_index'] for x in quality if x['observation.state']==0];by={a['episode_index']:a for a in ann}
    report={'byte_identical_video_groups':len(duplicate),'duplicate_episode_components':[list(x) for x in sorted(components)],
        'duplicate_video_episode_ids':sorted({i for component in components for i in component}),
        'conflicting_duplicate_video_outcomes':[list(ids) for ids in components if len({by[i]['episode_success'] for i in ids})>1],
        'published_identical_sensor_statistics_groups':[v for v in fingerprints.values() if len(v)>1],
        'published_constant_state_episodes':len(no_motion),'published_constant_state_class_counts':dict(Counter(by[i]['episode_success'] for i in no_motion)),
        'published_constant_state_indices':no_motion,'grouping':'Use canonical task_index to combine original source variants; keep all episode/camera/source duplicates together',
        'constant_state_policy':'Flag for QC; do not infer healthy/failure labels or automatically discard every stationary episode'}
    (ROOT/'checks/group_and_quality_screen.json').write_text(json.dumps(report,indent=2)+'\n')
    global_channels={}
    for key in keys:
        minima=[row['stats'][key]['min'] for row in stats];maxima=[row['stats'][key]['max'] for row in stats]
        global_channels[key]={'global_min_from_published_stats':[min(v[i] for v in minima) for i in range(14)],
            'global_max_from_published_stats':[max(v[i] for v in maxima) for i in range(14)],
            'always_zero_channels':[i for i in range(14) if all(v[i]==0 for v in minima) and all(v[i]==0 for v in maxima)],
            'source_scope':'5202 published episode-statistic records; raw verification limited to samples'}
    (ROOT/'checks/channel_availability_screen.json').write_text(json.dumps(global_channels,indent=2)+'\n')
    (ROOT/'checks/published_sensor_variation_screen.json').write_text(json.dumps({'episodes':len(quality),'source':'meta/episodes_stats.jsonl; source-record screening, not raw verification','rows':quality},indent=2)+'\n')
    records=list(csv.DictReader((ROOT/'checks/all_native_episode_records.csv').open()))
    extra={max(ids) for ids in components};excluded=set(no_motion)|extra
    remaining=[x for x in records if int(x['episode_index']) not in excluded];groups=defaultdict(Counter)
    for row in remaining:groups[row['task_index']][row['episode_success']]+=1
    provisional={'all_native_episodes':len(records),'flagged_constant_position':len(no_motion),'extra_duplicate_episode_copies':len(extra),
        'overlap':len(set(no_motion)&extra),'provisional_excluded':len(excluded),'provisional_remaining':len(remaining),
        'provisional_outcomes':dict(Counter(x['episode_success'] for x in remaining)),'canonical_groups_remaining':len(groups),
        'groups_with_both_outcomes':sum(v['success']>0 and v['failure']>0 for v in groups.values()),
        'definition':'Conservative metadata QC screen only, not a validated full cohort; full raw payload checks pending',
        'excluded_episode_indices':sorted(excluded)}
    (ROOT/'checks/provisional_cohort_screen.json').write_text(json.dumps(provisional,indent=2)+'\n')
    print('Duplicate episode components',len(components),'identical sensor-statistic groups',sum(len(v)>1 for v in fingerprints.values()))
