"""Native measured channels and historical statistics, with explicit provenance."""
from __future__ import annotations

from pathlib import Path
import json
import numpy as np
import pyarrow.parquet as pq

from .common import PROJECT, config, core, event, read, resolve, sha, write
from .reference import primitives, identities

STREAMS = {'observation.state': list(range(14)), 'observation.velocity': [0,1,2,3,4,5,7,8,9,10,11,12], 'observation.effort': [6,13]}
STATS = ['mean', 'std', 'median', 'min', 'max', 'q25', 'q75', 'range', 'RMS', 'normalized_progress_slope']
CHANNELS = [stream + '.' + str(index) for stream, indices in STREAMS.items() for index in indices]
FEATURES = [channel + '.' + statistic for statistic in STATS for channel in CHANNELS]


def sensor_sources(c):
    return {row['path']: row for row in read(resolve(c['sensor_inventory']))}


def load_episode(c, row, inventory):
    item = inventory[row['data']]
    path = resolve(c['historical_root']) / item['local_path']
    if sha(path) != item['expected_sha256']:
        raise RuntimeError('SENSOR_SOURCE_DRIFT')
    df = pq.read_table(path, use_threads=False).to_pandas(use_threads=False)
    assert len(df) == row['frame_count'] and (df.episode_index == row['episode_index']).all()
    assert (df.task_index == row['canonical_task_id']).all()
    assert np.array_equal(df.frame_index, np.arange(len(df)))
    clock = df.timestamp.to_numpy(dtype=float)
    assert np.all(np.diff(clock) > 0) and np.max(abs(clock - np.arange(len(df))/25)) < 1e-5
    arrays = {stream: np.stack(df[stream]).astype('float32')[:, indices] for stream, indices in STREAMS.items()}
    values = np.concatenate(list(arrays.values()), axis=1)
    assert values.shape == (len(df),28) and np.isfinite(values).all()
    return values, clock


def statistics(values):
    result = primitives()['statistics'](np.asarray(values,dtype='float32'))
    assert result.shape == (280,)
    return result


def quality(values):
    finite = np.isfinite(values)
    with np.errstate(all='ignore'):
        lo = np.nanmin(values,axis=0)
        hi = np.nanmax(values,axis=0)
        spread = hi-lo
    valid_values = np.nan_to_num(values)
    return np.asarray([finite.mean(), (finite.sum(0)>0).mean(), (spread<=1e-8).mean(),
                       np.mean(np.abs(valid_values)>10), np.mean(np.abs(np.diff(valid_values,axis=0)))],dtype='float32')


def prepare(c=None):
    c = c or config()
    folder = PROJECT / '03_preprocessing/sensor_preprocessing/arrays' / c['run_id']
    if (folder/'COMPLETE.json').exists():
        receipt=read(folder/'COMPLETE.json')
        assert sha(folder/'statistics.npz')==receipt['sha256']
        return receipt
    folder.mkdir(parents=True,exist_ok=True)
    records=core(c);inventory=sensor_sources(c);features=[];qualities=[];moments=[]
    for row in records:
        values, clock=load_episode(c,row,inventory)
        features.append(statistics(values));qualities.append(quality(values))
        moments.append([values.mean(0).tolist(),values.std(0).tolist()])
        if len(features)%500==0:event(c,'SENSOR_FEATURES',episodes=len(features),total=len(records))
    ids=np.asarray([row['episode_index'] for row in records],dtype=int)
    path=folder/'statistics.npz'
    assert not path.exists()
    np.savez_compressed(path,episode_ids=ids,features=np.stack(features),quality=np.stack(qualities))
    receipt={'path':str(path.relative_to(PROJECT.parent)),'sha256':sha(path),'episodes':len(records),'feature_width':280,
             'channels':CHANNELS,'features':FEATURES,'source_code':identities(),
             'interpretation':'14 positions,12 joint velocities,2 gripper-effort fields; not force/torque',
             'normalization':'No population fitting here; each model fits transformations on its T task groups only'}
    write(folder/'COMPLETE.json',receipt)
    write(PROJECT/'03_preprocessing/sensor_preprocessing/SENSOR_FEATURE_CONTRACT.json',receipt)
    event(c,'SENSOR_FEATURES_COMPLETE',episodes=len(records),width=280,sha256=receipt['sha256'])
    return receipt
