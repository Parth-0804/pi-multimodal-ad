"""Recompute multi-view, UUID and numerical-source identity screening."""
import csv
import json
from collections import Counter,defaultdict
from acquisition import ROOT


if __name__=='__main__':
    rows=list(csv.DictReader((ROOT/'checks/robofac_native_trajectory_records.csv').open()));by=defaultdict(list)
    for row in rows:by[row['unique_id']].append(row)
    joined=[x for x in rows if x['video_listed']=='True']
    files=json.loads((ROOT/'source_evidence/robofac/dataset_files_with_sizes.json').read_text())['siblings']
    hashes=defaultdict(list);video_hashes=defaultdict(list)
    for item in files:
        key=item.get('lfs',{}).get('sha256',item['blobId'])
        if item['rfilename'].endswith('.h5'):hashes[key].append(item['rfilename'])
        if item['rfilename'].endswith('.mp4'):video_hashes[key].append(item['rfilename'])
    groups=defaultdict(list)
    for row in csv.DictReader((ROOT/'checks/robofac_test_native_detection_records.csv').open()):
        if row['domain']=='realworld':
            path=row['video'].split('/');groups[(path[1],path[-1])].append(row)
    tasks=defaultdict(Counter)
    for (task,_),members in groups.items():tasks[task][members[0]['native_failure_detection_answer']]+=1
    output={'native_video_joined_records':len(joined),'native_video_joined_class_counts':dict(Counter(x['success'] for x in joined)),
        'native_video_joined_unique_uuids':len({x['unique_id'] for x in joined}),
        'uuid_conflicting_native_success_flags':sum(len({x['success'] for x in members})>1 for members in by.values()),
        'native_success_data_directory_flag_counts':dict(Counter(x['success'] for x in rows if '/success_data/' in x['source'])),
        'h5_listed':sum(x['rfilename'].endswith('.h5') for x in files),'h5_unique_lfs_hashes':len(hashes),
        'h5_duplicate_hash_groups':sum(len(v)>1 for v in hashes.values()),'realworld_unique_action_path_groups':len(groups),
        'realworld_action_class_counts':dict(Counter(v[0]['native_failure_detection_answer'] for v in groups.values())),
        'realworld_action_view_count_distribution':dict(Counter(len(v) for v in groups.values())),
        'realworld_crossview_label_conflicts':sum(len({x['native_failure_detection_answer'] for x in v})>1 for v in groups.values()),
        'realworld_classes_by_task':dict(tasks),'all_listed_videos_content_hash_unique':all(len(v)==1 for v in video_hashes.values())}
    (ROOT/'checks/robofac_extended_identity_screen.json').write_text(json.dumps(output,indent=2)+'\n')
    print('RoboFAC identity screening complete')
