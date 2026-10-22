"""Read-only sample helpers restored for the moved REASSEMBLE walkthrough.

Scientific cohort, interpolation and statistics implementations remain domain-owned.
"""
from pathlib import Path
import hashlib
import inspect
import json
import os


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def identity(path, root, checksum=False):
    p = Path(path); stat = p.stat()
    d = dict(path=os.path.relpath(p, root), bytes=stat.st_size, mtime_ns=stat.st_mtime_ns)
    if checksum:
        d['sha256'] = digest(p)
    return d


def reference(function, root):
    return f'{os.path.relpath(inspect.getsourcefile(function),root)}:{inspect.getsourcelines(function)[1]} — {function.__name__}'


def load_sample(row, recording, config, root, data_root):
    import numpy as np
    import h5py
    import cv2
    from reassemble.alignment import timestamps_1d, interval_indices, resample_progress
    from reassemble.inventory import scalar
    from reassemble.section1_features import statistics
    raw = data_root/'raw/data'/recording.filename
    bank = root/config['run_dir']/'features'/(row.recording_id+'.npz')
    meta_path = bank.with_suffix('.json'); meta = json.loads(meta_path.read_text())
    assert meta['source_sha256'] == recording.sha256
    assert digest(bank) == meta['feature_sha256']
    assert (raw.stat().st_size, raw.stat().st_mtime_ns) == (int(recording.size_bytes), int(recording.mtime_ns))
    with np.load(bank, allow_pickle=False) as z:
        matches = np.flatnonzero(z['row_index'] == row.name)
        assert len(matches) == 1
        slot = int(matches[0])
        saved = {k:z[k][slot].copy() for k in ('sensor','statistics','visual','frame_indices')}
    native, aligned, schema = {}, [], []
    with h5py.File(raw, 'r') as h:
        for name, obj in h.items():
            schema.append(dict(path='/'+name, shape=str(obj.shape) if isinstance(obj,h5py.Dataset) else 'group', dtype=str(obj.dtype) if isinstance(obj,h5py.Dataset) else f'{len(obj)} children'))
        for group in ('robot_state','timestamps'):
            for name,obj in h[group].items():
                schema.append(dict(path=f'/{group}/{name}',shape=str(obj.shape),dtype=str(obj.dtype)))
        annotation = {k:scalar(h['segments_info'][row.segment_id],k) for k in ('start','end','success','text','index')}
        assert annotation['success'] in (True,False,0,1)
        assert int(not annotation['success']) == int(row.failure)
        assert annotation['text'] == row.text and annotation['start'] == row.start and annotation['end'] == row.end
        vt = timestamps_1d(h['timestamps/hand'][()])
        assert config['sensor']['positions'] == 512 and config['visual']['frames'] == 16
        for name in config['sensor']['channels']:
            t = timestamps_1d(h['timestamps'][name][()]); d = h['robot_state'][name]
            assert d.size*d.dtype.itemsize < 128*1024**2
            x = d[()]; ii = interval_indices(t,row.start,row.end)
            native[name] = dict(t=t[ii], x=x[ii], native_dt=float(np.median(np.diff(t))), attrs={k:str(v) for k,v in d.attrs.items()})
            aligned.append(resample_progress(t,x,row.start,row.end,512,5))
        video_bytes = h['hand'].size*h['hand'].dtype.itemsize
    x = np.concatenate(aligned,axis=1).astype('float32'); stats = statistics(x)
    np.testing.assert_allclose(x,saved['sensor'],rtol=0,atol=0,equal_nan=True)
    np.testing.assert_allclose(stats,saved['statistics'],rtol=0,atol=0,equal_nan=True)
    ii = interval_indices(vt,row.start,row.end); chosen = saved['frame_indices']
    np.testing.assert_array_equal(chosen,ii[np.linspace(0,len(ii)-1,16).round().astype(int)])
    assert np.all((vt[chosen]>=row.start)&(vt[chosen]<=row.end))
    video = data_root/'cache/encoded_media'/recording.sha256/'hand.mp4'
    assert video.stat().st_size == video_bytes
    cap = cv2.VideoCapture(str(video)); images = []
    try:
        assert cap.isOpened() and int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) == len(vt)
        for index in chosen:
            cap.set(cv2.CAP_PROP_POS_FRAMES,int(index));ok,img=cap.read();assert ok
            images.append(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
    finally:
        cap.release()
    return dict(row=row,raw=raw,bank=bank,meta_path=meta_path,meta=meta,slot=slot,saved=saved,native=native,aligned=x,statistics=stats,vt=vt,chosen=chosen,images=np.stack(images),video=video,annotation=annotation,schema=schema)


def contact_sheet(sample,path,all_frames=True):
    import numpy as np
    import matplotlib.pyplot as plt
    r=sample['row']; slots=np.arange(16) if all_frames else np.array([0,5,10,15])
    fig,axes=plt.subplots(len(slots)//4,4,figsize=(14,3.4*len(slots)/4),squeeze=False,layout='constrained')
    for ax,slot in zip(axes.flat,slots):
        index=sample['chosen'][slot];ax.imshow(sample['images'][slot]);ax.axis('off')
        ax.set_title(f'Frame {index} | t − start = {sample["vt"][index]-r.start:.3f} s',fontsize=10)
    fig.suptitle(f'{r.recording_id} / {r.segment_id} · {r.text} · '+('failure' if r.failure else 'success')+'\n'+('All retained extraction frames' if all_frames else 'Presentation subset: 4 retained frames'))
    fig.savefig(path,dpi=120,bbox_inches='tight');plt.close(fig)


def sensor_figure(sample,path):
    import matplotlib.pyplot as plt
    r=sample['row'];fig,axes=plt.subplots(3,1,figsize=(12,8),sharex=True,layout='constrained')
    for ax,name in zip(axes,['measured_force','measured_torque','gripper_positions']):
        d=sample['native'][name];ax.plot(d['t']-r.start,d['x'][:,0],'.',markersize=1.3)
        ax.axvspan(0,r.duration,alpha=.1)
        for t in sample['vt'][sample['chosen']]-r.start:ax.axvline(t,color='#aa6b00',alpha=.35,lw=.7)
        for t in (0,r.duration):ax.axvline(t,color='black',ls='--')
        ax.set_ylabel(name+':0\nunit unknown');ax.grid(alpha=.15)
    axes[-1].set_xlabel('Seconds since annotated start')
    fig.suptitle(f'{r.recording_id} / {r.segment_id}: native observations\nGold = camera frames; dashed = action boundaries')
    fig.savefig(path,dpi=120,bbox_inches='tight');plt.close(fig)


def export_clip(sample,path):
    import cv2
    import numpy as np
    import pandas as pd
    r,vt=sample['row'],sample['vt'];ii=np.flatnonzero((vt>=r.start)&(vt<=r.end))
    native_dt=float(np.median(np.diff(vt[ii])));dt=native_dt*max(1,int(np.ceil(1/native_dt/6)))
    clock=np.arange(vt[ii[0]],vt[ii[-1]]+1e-8,dt);indices=np.searchsorted(vt,clock,side='right')-1
    if len(clock)>240:raise RuntimeError('Preview exceeds 240-frame cap')
    assert np.all(np.isin(indices,ii))
    writer=cv2.VideoWriter(str(path),cv2.VideoWriter_fourcc(*'VP80'),1/dt,(480,360))
    if not writer.isOpened():raise RuntimeError('VP8 encoder unavailable; use the contact sheet')
    cap=cv2.VideoCapture(str(sample['video']))
    try:
        for index in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES,int(index));ok,img=cap.read();assert ok
            img=cv2.resize(img,(480,360));cv2.rectangle(img,(0,331),(480,360),(0,0,0),-1)
            cv2.putText(img,f'frame {index} | source +{vt[index]-r.start:.3f} s',(8,351),cv2.FONT_HERSHEY_SIMPLEX,.5,(255,255,255),1)
            writer.write(img)
    finally:
        writer.release();cap.release()
    cap=cv2.VideoCapture(str(path));fps=cap.get(cv2.CAP_PROP_FPS);decoded=0
    while True:
        ok,img=cap.read()
        if not ok:break
        assert img.shape==(360,480,3);decoded+=1
    cap.release();assert decoded==len(clock) and fps>0
    pd.DataFrame(dict(output_seconds=np.arange(len(clock))*dt,source_frame_index=indices,source_timestamp_seconds=vt[indices])).to_csv(path.with_suffix('.csv'),index=False)
    return dict(path=path.name,frames_decoded=decoded,fps=1/dt,encoded_fps=fps,duration_seconds=decoded/fps,source_start_trim_seconds=float(clock[0]-r.start),last_output_timestamp_to_annotation_end_seconds=float(r.end-clock[-1]),playback_end_minus_annotation_end_seconds=float(clock[0]+decoded/fps-r.end),maximum_hold_delay_seconds=float(np.max(clock-vt[indices])),browser_playback_verified=False)
