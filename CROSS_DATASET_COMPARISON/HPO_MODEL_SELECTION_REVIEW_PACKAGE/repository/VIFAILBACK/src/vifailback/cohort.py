"""Finalize the common cohort only after complete three-camera payload QC."""
from collections import Counter
import csv

from .common import PROJECT, config, core, csv_write, read, resolve, sha, signature, write
from .video import positions


def folder(c):
    return PROJECT/'03_preprocessing/processed_manifests'/c['run_id']


def finalize(c=None):
    c=c or config(); out=folder(c)
    completed=out/'COMPLETE.json'
    if completed.exists():
        receipt=read(completed)
        assert sha(out/'eligible.json')==receipt['eligible_sha256']
        return read(out/'eligible.json')
    qc_path=PROJECT/'02_dataset_verification/video_audit/runs'/c['run_id']/'VIDEO_QC_COMPLETE.json'
    if not qc_path.exists():
        raise RuntimeError('FULL_VIDEO_QC_PENDING')
    qc=read(qc_path); candidates=core(c)
    assert qc['count']==len(candidates)*3
    index={(r['episode_index'],r['camera']):r for r in qc['cameras']}
    assert len(index)==len(candidates)*3
    eligible=[]; excluded=[]
    for row in candidates:
        views=[index[row['episode_index'],cam] for cam in c['cameras']]
        reasons=[cam+':'+v['reason'] for cam,v in zip(c['cameras'],views) if not v['technical_valid']]
        if reasons:
            excluded.append({**row,'final_exclusion_reasons':'|'.join(reasons)});continue
        expected=positions(row['frame_count']).tolist()
        for view in views:
            assert view['selected_frame_indices']==expected
            assert view['decoded_frames']==row['frame_count']
            assert len(view['selected_RGB_sha256'])==16
            assert abs(view['last_frame_time_seconds']-(row['frame_count']-1)/25)<5e-5
        # Allow-list metadata in model manifest; annotations never ordinary features.
        keep=['episode_index','canonical_task_id','label','frame_count','data','video_high','video_left','video_right',
              'sensor_content_sha256','video_triplet_hash','source_hdf5']
        eligible.append({**{k:row[k] for k in keep},'frame_indices':expected,
                         'episode_interval_start_seconds':0.,'episode_interval_stop_exclusive_seconds':row['frame_count']/25,
                         'frame_times_seconds':[i/25 for i in expected],
                         'camera_sha256':[v['source_sha256'] for v in views],
                         'camera_bytes':[v['source_bytes'] for v in views],
                         'camera_mtime_ns':[v['mtime_ns'] for v in views],
                         'selected_RGB_sha256':[v['selected_RGB_sha256'] for v in views],
                         'visual_quality_categories':[v['visual_quality_category'] for v in views],
                         'semantic_review':'UNRESOLVED_NOT_A_HUMAN_FREE_GUARANTEE'})
    assert len({r['episode_index'] for r in eligible})==len(eligible)
    assert len({r['video_triplet_hash'] for r in eligible})==len(eligible),'UNRESOLVED_DUPLICATE_VIDEO_IDENTITY'
    original=list(csv.DictReader((resolve(c['followup_root'])/'02_COHORT_AND_SPLITS/V2_CONSERVATIVE_CORE/EXCLUDED_OR_QUARANTINED_EPISODES_V2.csv').open()))
    assert len(original)==818
    exclusions=[{'episode_index':int(r['episode_index']),'canonical_task_id':int(r['canonical_task_id']),
                 'label':int(r['label']),'final_exclusion_reasons':r['exclusion_reasons_v2']} for r in original]
    exclusions += [{k:r[k] for k in ['episode_index','canonical_task_id','label','final_exclusion_reasons']} for r in excluded]
    assert len(eligible)+len(exclusions)==5202
    write(out/'eligible.json',eligible);csv_write(out/'exclusions.csv',exclusions)
    contract={'unit':'one complete recorded action episode','target':{'0':'native success/no-failure','1':'native failure'},
              'frames':{'cameras':c['cameras'],'timestamps_per_camera':16,'total_RGB_images':48,
                        'selection':'uniform rounded index; same positions in all cameras; label blind',
                        'pixels':'bilinear resize640x640, RGB /255, no mean/std image normalization'},
              'sensors':{'sampling_hz':25,'measured_channels':28,'statistics_width':280,
                         'not_force_torque':True,'action_commands_used':False},
              'eligibility':'historical V2 conservative exclusions plus technical three-camera QC; visual weakness retained',
              'clock_limitation':'converted relative index/25; no independent hardware clock offset calibration',
              'independence':'canonical task only; session/operator/object-instance independence unverified',
              'full_semantic_review_complete':False,'eligible':len(eligible),'excluded':len(exclusions),
              'labels':dict(Counter(r['label'] for r in eligible)),
              'tasks':len({r['canonical_task_id'] for r in eligible}),
              'camera_streams_with_repeated_selected_RGB_content':sum(v.get('distinct_selected_RGB_images',16)<16 for v in qc['cameras'] if v['technical_valid']),
              'distinctness_contract':'16 distinct temporal indices per camera; identical stationary image content is retained and flagged',
              'task_label_counts':{str(g):dict(Counter(r['label'] for r in eligible if r['canonical_task_id']==g))
                                   for g in sorted({r['canonical_task_id'] for r in eligible})}}
    write(PROJECT/'03_preprocessing/data_contracts'/c['run_id']/'DATASET_CONTRACT.json',contract)
    write(completed,{**contract,'video_qc_sha256':sha(qc_path),'config_sha256':signature(c),
                     'eligible_sha256':sha(out/'eligible.json'),'exclusions_sha256':sha(out/'exclusions.csv')})
    return eligible
