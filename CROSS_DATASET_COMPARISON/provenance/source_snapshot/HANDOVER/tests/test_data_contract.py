"""Synthetic timestamp, native-label and split-namespace regression checks."""
import importlib.util
import json
import sys
from pathlib import Path
import cv2
import numpy as np
import pytest

sys.path[:0]=['src','MSM/99_preserved_previous_work/MILLING_DATASET/source','CROSS_DATASET_COMPARISON/src']
spec=importlib.util.spec_from_file_location('handover_validation',Path('HANDOVER/src/validate_full.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def synthetic(tmp_path):
    folder=tmp_path/'trial0000';folder.mkdir()
    metadata={'task':'robot to human handover','robot':'Toyota HSR'}
    (folder/'task_info.json').write_text(json.dumps(metadata))
    t=np.arange(120)/30+.01;wt=np.arange(350)/100
    w=np.stack([np.sin(wt*(i+1)) for i in range(6)],axis=1)
    nearest=np.array([np.argmin(abs(wt-v)) for v in t]);aligned=w[nearest]
    for name,array in [('head_cam_ts',t),('wrench_ts',wt),('wrench',w),('wrench_resampled',aligned)]:np.save(folder/(name+'.npy'),array)
    writer=cv2.VideoWriter(str(folder/'head_cam.mp4'),cv2.VideoWriter_fourcc(*'mp4v'),30,(64,64))
    assert writer.isOpened()
    for i in range(len(t)):
        image=np.full((64,64,3),i,np.uint8);image[8:24,(i%40):(i%40)+10]=255;writer.write(image)
    writer.release()
    label=tmp_path/'trial0000.json';label.write_text(json.dumps({**metadata,'outcome':1}))
    classes={'robot to human handover outcomes':['success','no approach','no grasp','drop']}
    return folder,label,metadata,classes


def test_common_support_preserves_exact_alignment_without_sensor_tail_padding(tmp_path,monkeypatch):
    folder,label,metadata,classes=synthetic(tmp_path)
    monkeypatch.setattr(module,'ROOT',tmp_path/'full');monkeypatch.setattr(module,'COMMON_SUPPORT',False)
    full=module.trial(folder,'train',label,{**metadata,'outcome':1},classes)
    assert not full['record']['eligible'] and 'wrench_nearest_time_gap_exceeds_0.1s' in full['record']['exclusion_reasons']
    monkeypatch.setattr(module,'ROOT',tmp_path/'common');monkeypatch.setattr(module,'COMMON_SUPPORT',True)
    common=module.trial(folder,'train',label,{**metadata,'outcome':1},classes)
    assert common['record']['eligible'] and len(common['frames'])==16
    assert common['record']['end_s']<3.5 and common['clock']['provided_vs_nearest_max_abs_difference']==0
    assert len(common['features'])==37 # ID plus 36 numerical values
    assert common['record']['native_label']==1 and common['record']['target']==1


def test_native_outcome_does_not_affect_temporal_sampling(tmp_path,monkeypatch):
    folder,label,metadata,classes=synthetic(tmp_path);monkeypatch.setattr(module,'COMMON_SUPPORT',True)
    monkeypatch.setattr(module,'ROOT',tmp_path/'one')
    first=module.trial(folder,'test',label,{**metadata,'outcome':1},classes)
    monkeypatch.setattr(module,'ROOT',tmp_path/'zero')
    second=module.trial(folder,'test',label,{**metadata,'outcome':0},classes)
    assert first['record']['frame_indices_json']==second['record']['frame_indices_json']
    assert [x['decoded_frame_sha256'] for x in first['frames']]==[x['decoded_frame_sha256'] for x in second['frames']]
    assert first['record']['target']==1 and second['record']['target']==0


def test_trial_numbers_are_qualified_by_official_partition(tmp_path,monkeypatch):
    folder,label,metadata,classes=synthetic(tmp_path);monkeypatch.setattr(module,'COMMON_SUPPORT',True)
    monkeypatch.setattr(module,'ROOT',tmp_path/'namespace')
    a=module.trial(folder,'train',label,{**metadata,'outcome':1},classes)
    b=module.trial(folder,'test',label,{**metadata,'outcome':1},classes)
    assert a['record']['sample_id']=='train/trial0000' and b['record']['sample_id']=='test/trial0000'
    assert a['record']['participant_id']==b['record']['participant_id']==''
