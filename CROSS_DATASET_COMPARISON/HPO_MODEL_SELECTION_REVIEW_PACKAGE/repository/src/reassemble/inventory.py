"""Read-only actual-schema recording and segment inventory, resumable by file hash."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import re
import h5py
import numpy as np
import pandas as pd
from .acquire import digest
from .alignment import action_from_text, timestamps_1d, sensor_quality, interval_coverage
from .media import inspect_video, inspect_audio


def scalar(group, key):
    value = group[key][()]
    if isinstance(value, bytes):
        return value.decode('utf-8')
    return np.asarray(value).item()


def schema(group):
    return {key: {'shape': list(value.shape), 'dtype': str(value.dtype)} if isinstance(value, h5py.Dataset) else {'group': schema(value)} for key, value in group.items()}


def audit_recording(task):
    path, config, run_dir, cache_dir = task
    path = Path(path);run_dir = Path(run_dir)
    output = run_dir / 'records' / (path.stem + '.json')
    if output.exists():
        previous = json.loads(output.read_text())
        if previous['recording']['size_bytes'] == path.stat().st_size and previous['recording']['mtime_ns'] == path.stat().st_mtime_ns:
            return str(output)
        raise RuntimeError('Cached source changed; use a fresh run')
    sha = digest(path, 'sha256')
    recording = {'recording_id': path.stem, 'filename': path.name, 'size_bytes': path.stat().st_size, 'mtime_ns': path.stat().st_mtime_ns, 'sha256': sha}
    segments = [];warnings = [];streams = {};media = {}
    with h5py.File(path, 'r') as h5:
        recording['schema'] = schema(h5)
        recording['top_level_keys'] = list(h5)
        recording['attributes'] = {k:str(v) for k,v in h5.attrs.items()}
        recording['video_streams'] = [k for k in ['hama1','hama2','hand'] if k in h5]
        recording['audio_streams'] = [k for k in h5 if 'audio' in k]
        recording['event_streams'] = [k for k in h5 if 'event' in k or 'capture' in k]
        recording['timestamp_arrays'] = list(h5.get('timestamps',{}))
        annotation = h5.get('segments_info')
        if annotation is None:
            raise ValueError(f'Missing segments_info: {path.name}')
        for key, group in annotation.items():
            start, end = float(scalar(group,'start')), float(scalar(group,'end'))
            text = str(scalar(group,'text'))
            success = scalar(group,'success')
            if success not in (0,1,False,True):
                raise ValueError('Unrecognized success label')
            if not np.isfinite(start+end) or end<=start:
                warnings.append(f'Invalid interval {key}: {start}, {end}')
                # Keep invalid annotations visible; block their availability.
            action = action_from_text(text)
            segment = {'recording_id':path.stem,'segment_id':str(key),'start':start,'end':end,'duration':end-start,'success':bool(success),'failure':int(not success),'text':text,'action':action,'object_annotation':re.sub(r'^\s*\w+\s*','',text).strip() if action!='other' else None,'low_level_count':len(group.get('low_level',group.get('Low_level',{}))),'valid_interval':bool(np.isfinite(start+end) and end>start),'sensor':{},'video':{},'audio':{}}
            segments.append(segment)
        segments.sort(key=lambda s:(s['start'],s['segment_id']))
        valid_segments = [s for s in segments if s['valid_interval']]
        recording['segment_count'] = len(segments)
        recording['low_level_segment_count'] = sum(s['low_level_count'] for s in segments)
        timestamps = h5.get('timestamps',{})
        origin = min(float(np.asarray(v[0]).flat[0]) for v in timestamps.values() if len(v))
        recording['nominal_audio_origin'] = origin
        robot = h5.get('robot_state',{})
        for name, arr in robot.items():
            if name not in timestamps:
                warnings.append(f'No timestamps for sensor {name}');continue
            try:
                t = timestamps_1d(timestamps[name][()])
                x = np.asarray(arr[()])
                if x.ndim==1:x=x[:,None]
                if x.ndim!=2 or len(t)!=len(x):raise ValueError('Shape/length mismatch')
                streams[name] = {'shape':list(x.shape),'dtype':str(x.dtype),'timestamp_count':len(t),'first':float(t[0]) if len(t) else None,'last':float(t[-1]) if len(t) else None,'median_interval':float(np.median(np.diff(t))) if len(t)>1 else None,'finite_fraction':float(np.isfinite(x).mean()) if x.size else 0}
                for seg in valid_segments:
                    if name in config['primary_sensors']:
                        q=sensor_quality(t,x,seg['start'],seg['end'],config['sensor_positions'],config['gap_multiple'])
                        indices=np.flatnonzero((t>=seg['start'])&(t<=seg['end']))
                        q['content_sha256']=hashlib.sha256(np.ascontiguousarray(x[indices]).tobytes()).hexdigest()
                        q['usable']=q['coverage']>=config['coverage_threshold'] and q['resampled_finite_fraction']>=config['coverage_threshold'] and q['missing_channels']==0 and q['count']>=2
                    else:
                        q=interval_coverage(t,seg['start'],seg['end'])
                    seg['sensor'][name]=q
            except (ValueError,TypeError) as e:
                warnings.append(f'Sensor {name}: {e}')
        for camera in ['hama1','hama2','hand']:
            if camera not in h5 or camera not in timestamps:
                warnings.append(f'Missing camera/timestamps {camera}');continue
            try:
                t=timestamps_1d(timestamps[camera][()])
                meta, quality=inspect_video(h5[camera],t,valid_segments,Path(cache_dir)/sha/(camera+'.mp4'),config['video_frames'])
                media[camera]=meta
                for seg in valid_segments:seg['video'][camera]=quality[seg['segment_id']]
            except (ValueError,RuntimeError,OSError) as e:
                warnings.append(f'Video {camera}: {type(e).__name__}: {e}')
        for name in h5:
            if 'audio' not in name or not isinstance(h5[name],h5py.Dataset):continue
            try:
                meta, quality=inspect_audio(h5[name],valid_segments,timestamps[name][()] if name in timestamps else None,origin)
                media[name]=meta
                for seg in valid_segments:seg['audio'][name]=quality[seg['segment_id']]
            except (ValueError,RuntimeError,OSError) as e:
                warnings.append(f'Audio {name}: {type(e).__name__}: {e}')
    recording['sensor_streams']=streams;recording['media']=media
    record={'recording':recording,'segments':segments,'warnings':warnings}
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x') as f:json.dump(record,f,indent=2,allow_nan=False)
    return str(output)


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',default='configs/reassemble/audit.json');p.add_argument('--run-dir',required=True);p.add_argument('--workers',type=int,default=3);p.add_argument('--limit',type=int)
    args=p.parse_args();config=json.loads(Path(args.config).read_text());root=Path(config['data_root']).resolve()/'REASSEMBLE';run=Path(args.run_dir)
    files=sorted((root/'raw').rglob('*.h5'))
    if not files:raise RuntimeError('No extracted recordings')
    if args.limit:files=files[:args.limit]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(audit_recording,(str(f),config,str(run),str(root/'cache'/'encoded_media'))):f for f in files}
        for i,future in enumerate(as_completed(futures),1):print(i,len(files),future.result(),flush=True)
    recordings=[];segments=[]
    for f in files:
        obj=json.loads((run/'records'/(f.stem+'.json')).read_text());r=obj['recording'].copy()
        for key in ['schema','sensor_streams','media','top_level_keys','attributes','video_streams','audio_streams','event_streams','timestamp_arrays']:r[key]=json.dumps(r[key])
        r['warnings']=json.dumps(obj['warnings']);recordings.append(r)
        for s in obj['segments']:
            for key in ['sensor','video','audio']:s[key]=json.dumps(s[key])
            segments.append(s)
    pd.DataFrame(recordings).to_parquet(run/'recordings.parquet',index=False)
    pd.DataFrame(segments).to_parquet(run/'segments.parquet',index=False)
    print('COMPLETE',len(recordings),len(segments),flush=True)

if __name__=='__main__':main()
