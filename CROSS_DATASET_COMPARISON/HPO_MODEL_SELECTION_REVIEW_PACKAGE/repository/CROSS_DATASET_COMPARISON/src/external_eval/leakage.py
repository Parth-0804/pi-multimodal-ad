"""Final byte-identity and temporal-overlap gates, before any model fitting."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from external_eval.io import sha,write_json


def audit(root):
    root=Path(root);config=json.loads((root/'04_experiment_protocol/experiment_config.json').read_text())
    dataset=config['dataset'];samples=root/'03_processed_model_inputs/final_sample_manifest.csv'
    if sha(samples)!=config['sample_manifest_sha256']:raise ValueError('Frozen sample cohort changed')
    frame=pd.read_csv(samples);alignment=root/'02_labels_and_alignment/alignment_manifest.csv';selected=pd.read_csv(alignment)
    key='sample_id' if 'sample_id' in selected else 'interval_id';selected=selected[selected[key].isin(frame.sample_id)]
    if selected.groupby(key).size().to_dict()!=dict.fromkeys(frame.sample_id,16):raise ValueError('Each native example must have exactly16 source frames')
    group='group_id' if dataset=='MSM' else 'official_split'
    sample_group=frame.set_index('sample_id')[group];selected=selected.assign(leakage_group=selected[key].map(sample_group))
    if (selected.groupby('decoded_frame_sha256').leakage_group.nunique()>1).any():raise ValueError('Exact source RGB content crosses independent partitions/groups')
    if (frame.groupby('video_sha256')[group].nunique()>1).any():raise ValueError('Same source video crosses independent partitions/groups')
    overlaps=0
    if dataset=='MSM':
        for _,g in frame.groupby('group_id'):
            g=g.sort_values('start_s');overlaps+=int(np.sum(g.start_s.to_numpy()[1:]<np.maximum.accumulate(g.end_s.to_numpy())[:-1]))
        if overlaps:raise ValueError('Native eligible cutting intervals overlap')
        sources=pd.read_csv('MSM/01_raw_dataset/download_manifest.csv').to_dict('records')
    else:sources=json.loads((root/'02_labels_and_alignment/input_manifest.json').read_text())
    for item in sources:
        path=Path(item['path'])
        if not path.is_file() or sha(path)!=item['sha256']:raise ValueError('Native input bytes changed: '+str(path))
    identity={'sample_manifest_sha256':sha(samples),'alignment_manifest_sha256':sha(alignment),
        'sensor_features_sha256':sha(root/'03_processed_model_inputs/sensor_features/interval_statistics.csv'),
        'frozen_splits_sha256':sha(root/'03_processed_model_inputs/split_manifests/frozen_splits.json')}
    output={'dataset':dataset,'passed':True,'examples':len(frame),'source_frames':len(selected),'native_files_hash_verified':len(sources),
        'cross_group_or_split_duplicate_RGB_hashes':0,'cross_group_or_split_duplicate_video_hashes':0,
        'overlapping_native_cuts':overlaps,'input_identity':identity,
        'physical_tool_workpiece_or_participant_identity_not_inferred_from_hashes':True}
    write_json(root/'02_labels_and_alignment/SOURCE_LEAKAGE_GATE.json',output)
    print('SOURCE LEAKAGE GATE',dataset,'PASS',len(frame),flush=True)
    return identity
