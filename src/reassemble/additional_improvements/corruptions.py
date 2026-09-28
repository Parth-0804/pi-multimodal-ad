"""Outcome-independent corruption banks with separate train/validation/test seeds."""
from pathlib import Path
import argparse
import time
import warnings
import cv2
import h5py
import numpy as np
import pandas as pd
from reassemble.completion_common import seed_for
from reassemble.section1_features import cohort,load_visual,statistics
from reassemble.section3_visual import pooled_frames,pixel_corruption,frame_quality
from reassemble.section3_sensor import corrupt_stream
from reassemble.alignment import timestamps_1d,interval_indices,resample_progress,sensor_quality
from .common import setup,read,write,storage,progress,identity

def visual_conditions():
    conditions=[]
    for split in ['train','validation']:
        for r in range(4):conditions.append(dict(name=f'{split}_V1_r{r}',family='V1',severity=None,split=split,realization=r))
    for value in [.02,.05,.1]:
        for r in range(5):conditions.append(dict(name=f'test_V1_{value:g}_r{r}',family='V1',severity=value,split='test',realization=r))
    for value in [1,2,4]:conditions.append(dict(name=f'test_V2_{value}',family='V2',severity=value,split='test',realization=0))
    for drop in [2,5,8]:
        for r in range(5):conditions.append(dict(name=f'test_V3_{drop}_r{r}',family='V3',severity=drop/16,split='test',realization=r))
    return conditions

def sensor_conditions(split):
    if split in ['train','validation']:
        return [dict(name=f'{split}_S1_r{r}',family='S1',severity=None,split=split,realization=r) for r in range(4)]
    out=[]
    for family,values in [('S1',[.1,.5,1.]),('S2',[2/22,7/22,11/22]),('S3',[.1,.3,.5])]:
        for value in values:
            label=str(round(value*22)) if family=='S2' else f'{value:g}'
            for r in range(5):out.append(dict(name=f'test_{family}_{label}_r{r}',family=family,severity=value,split='test',realization=r))
    out.append(dict(name='test_S4_median',family='S4',severity=1.,split='test',realization=0));return out

def corruption_seed(c,row,condition):
    return seed_for(c['seed'],'additional_improvements',condition['split'],row.recording_id,row.segment_id,condition['family'],condition['severity'],condition['realization'])

def visual():
    c=setup();base=read(c['section1_config']);root=Path(c['run_dir']);out=root/'04_corruption_training/visual_bank';out.mkdir(exist_ok=True)
    storage(large=True);frame=cohort(base);conditions=visual_conditions();write(out/'conditions.json',conditions)
    estimate=len(conditions)*len(frame)*(896+6)*4;write(out/'cache_estimate.json',dict(uncompressed_feature_quality_bytes=estimate))
    recordings=pd.read_parquet(Path(base['audit_run'])/'recordings.parquet').set_index('recording_id');processor,model,info=load_visual(base);write(out/'model.json',info)
    for count,(rid,rows) in enumerate(frame.groupby('recording_id',sort=True)):
        path=out/(rid+'.npz')
        if path.exists():
            assert identity(path)==read(path.with_suffix('.json'))['output'];continue
        storage();started=time.perf_counter()
        source=root/'01_temporal_visual/features'/(rid+'.npz')
        with np.load(source) as z:assert np.array_equal(z['row_index'],rows.index);indices=z['frame_indices'];perframe=z['features']
        video=Path(base['data_root'])/'cache/encoded_media'/recordings.loc[rid,'sha256']/'hand.mp4'
        cap=cv2.VideoCapture(str(video));assert cap.isOpened()
        features=np.empty((len(conditions),len(rows),896),np.float32);quality=np.empty((len(conditions),len(rows),6),np.float32);severities=np.empty((len(conditions),len(rows)),float)
        for i,row in enumerate(rows.itertuples()):
            images=[]
            for index in indices[i]:
                cap.set(cv2.CAP_PROP_POS_FRAMES,int(index));ok,img=cap.read();assert ok;images.append(img)
            for j,condition in enumerate(conditions):
                seed=corruption_seed(c,row,condition);value=condition['severity']
                if value is None:value=float(np.random.default_rng(seed_for(seed,'severity')).uniform(.01,.08))
                severities[j,i]=value
                if condition['family']=='V3':
                    kept=np.sort(np.random.default_rng(seed).permutation(16)[int(round(value*16)):]);changed=[images[t] for t in kept]
                    features[j,i]=perframe[i,kept].mean(0)
                else:
                    changed=[pixel_corruption(img,condition['family'],value,seed_for(seed,int(index))) for img,index in zip(images,indices[i])]
                    features[j,i]=pooled_frames(changed,processor,model)[0]
                quality[j,i]=frame_quality(changed)
        cap.release();np.savez_compressed(path,row_index=rows.index.to_numpy(),features=features,quality=quality,severities=severities,names=np.array([v['name'] for v in conditions]))
        write(path.with_suffix('.json'),dict(output=identity(path),source=identity(source),seconds=time.perf_counter()-started,source_recording_sha256=recordings.loc[rid,'sha256']))
        progress(4,f'Raw-pixel corruption bank {count+1}/148 recordings complete')
    progress(4,'Raw-pixel corruption bank complete')

class SensorSource:
    def __init__(self,base,frame):
        self.base=base;self.frame=frame;self.records=pd.read_parquet(Path(base['audit_run'])/'recordings.parquet').set_index('recording_id');self.rid=None;self.streams=None
    def segment(self,row):
        if row.recording_id!=self.rid:
            path=Path(self.base['data_root'])/'raw/data'/self.records.loc[row.recording_id,'filename']
            with h5py.File(path,'r') as h:self.streams={n:(timestamps_1d(h['timestamps'][n][()]),np.asarray(h['robot_state'][n][()],dtype=np.float64)) for n in self.base['sensor']['channels']}
            self.rid=row.recording_id
        # Keep full stream: original gap rules estimate native_dt globally.
        return self.streams

def sensor_features(c,c2,row,streams,condition,sigma,median):
    seed=corruption_seed(c,row,condition);rng=np.random.default_rng(seed);family=condition['family'];value=condition['severity']
    if value is None:value=float(np.random.default_rng(seed_for(seed,'severity')).uniform(.05,.8))
    channel=np.sort(rng.choice(22,int(round(22*value)),replace=False)) if family=='S2' else np.array([],int)
    block=float(rng.uniform(0,1-value)) if family=='S3' else 0.
    offset=0;resampled=[];measures=[]
    for name,(t,x) in streams.items():
        changed=corrupt_stream(x,t,row.start,row.end,family,value,seed_for(seed,name),sigma,median,channel,offset,block);offset+=x.shape[1]
        resampled.append(resample_progress(t,changed,row.start,row.end,512,5));q=sensor_quality(t,changed,row.start,row.end,512,5)
        measures.extend([q[k] for k in c2['quality_sensor']])
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always',RuntimeWarning);features=statistics(np.concatenate(resampled,axis=1).astype(np.float32))
    return features,np.asarray(measures,np.float32),len(caught)

def main():
    p=argparse.ArgumentParser();p.add_argument('operation',choices=['visual']);args=p.parse_args()
    if args.operation=='visual':visual()

if __name__=='__main__':main()
