"""Verify the actual two-trial sample before automatic full acquisition."""
import json
import sys
from pathlib import Path
import cv2
import numpy as np

sys.path[:0]=['CROSS_DATASET_COMPARISON/src']
from external_eval.io import write_json,sha


def main():
    root=Path('HANDOVER/01_raw_dataset/official_dataset');rows=[]
    classmap=json.loads((root/'archives/class_names.json').read_text())
    assert classmap['robot to human handover outcomes']==['success','no approach','no grasp','drop']
    assert classmap['human to robot handover outcomes']==['success','no approach','no release','drop']
    labels={p.stem:(p,json.loads(p.read_text())) for p in (root/'labels/train').rglob('trial*.json')}
    assert len(labels)==337
    outcomes=[x[1]['outcome'] for x in labels.values()]
    assert set(outcomes)=={0,1,2,3}
    cv2.setNumThreads(1)
    for p in sorted((root/'sample').rglob('task_info.json')):
        folder=p.parent;native=json.loads(p.read_text());label_path,label=labels[folder.name]
        assert label['task']==native['task'] and label['robot']==native['robot']
        t=np.load(folder/'head_cam_ts.npy',allow_pickle=False)
        w=np.load(folder/'wrench_resampled.npy',allow_pickle=False)
        wt=np.load(folder/'wrench_ts.npy',allow_pickle=False)
        raw=np.load(folder/'wrench.npy',allow_pickle=False)
        assert t.ndim==1 and len(t)>=16 and np.isfinite(t).all() and np.all(np.diff(t)>0)
        assert w.shape==(len(t),6) and np.isfinite(w).all() and raw.shape==(len(wt),6)
        cap=cv2.VideoCapture(str(folder/'head_cam.mp4'),cv2.CAP_FFMPEG,[cv2.CAP_PROP_N_THREADS,1])
        assert cap.isOpened() and int(cap.get(cv2.CAP_PROP_FRAME_COUNT))==len(t)
        # Equal source-clock bin centers across the entire label-independent trial.
        targets=t[0]+(np.arange(16)+.5)/16*(t[-1]-t[0])
        idx=np.searchsorted(t,targets).clip(0,len(t)-1);previous=np.maximum(idx-1,0)
        idx=np.where(abs(t[previous]-targets)<abs(t[idx]-targets),previous,idx)
        assert len(set(idx))==16
        hashes=[];pts=[]
        for j in idx:
            cap.set(cv2.CAP_PROP_POS_FRAMES,int(j));ok,image=cap.read();assert ok
            import hashlib
            hashes.append(hashlib.sha256(image.tobytes()).hexdigest());pts.append(cap.get(cv2.CAP_PROP_POS_MSEC)/1000)
        assert len(set(hashes))==16 and np.all(np.diff(pts)>0)
        cap.release()
        rows.append({'trial':folder.name,'robot':native['robot'],'outcome':label['outcome'],
            'headcam_samples':len(t),'raw_wrench_rows':len(wt),'source_clock_range_s':[float(t[0]),float(t[-1])],
            'source_clock_monotonic':True,'provided_resampled_wrench_shape':list(w.shape),'six_wrench_channels_finite':True,
            'selected_indices':idx.tolist(),'native_video_pts_s':pts,'frame_hashes':hashes,
            'label_source':str(label_path),'label_sha256':sha(label_path),
            'participant_id_in_metadata':any(k in native or k in label for k in ['participant','participant_id','subject','subject_id','person_id']),
            'label_independent_policy':'16 equal source-clock bin centers over complete head_cam_ts span; native frame index joins the provided Mx6 resampled wrench'})
    assert len(rows)==2 and {r['robot'] for r in rows}=={'Toyota HSR','Kinova Gen3'}
    members=json.loads(Path('HANDOVER/01_raw_dataset/source_evidence/sample_members.json').read_text())
    compressed=(root/'archives/sample_training_set.tar.gz').stat().st_size
    gate={'passed':True,'trials':rows,'train_labels_verified':337,'training_outcome_counts':{str(k):outcomes.count(k) for k in sorted(set(outcomes))},
        'sample_uncompressed_bytes':sum(x['bytes'] for x in members),'sample_compressed_bytes':compressed,
        'sample_uncompressed_ratio':sum(x['bytes'] for x in members)/compressed,
        'primary_sensor_contract':'6 provided wrist wrench channels x 6 fixed statistics = 36; no robot-specific joints fabricated',
        'robot_difference':'HSR measured force/torque; Gen3 estimates force/torque from sensed joint torque, documented in datasheet',
        'official_subject_split_claim':True,'participant_mapping_in_sample':False,
        'participant_oof_gate':'Requires an explicit official mapping; never infer identity from trial number or face. If absent, F2/adaptive are blocked, not silently trial-split.',
        'sample_is_not_independent_test':True}
    write_json('HANDOVER/02_labels_and_alignment/sample_gate.json',gate)
    print(json.dumps(gate,indent=2))


if __name__=='__main__':main()
