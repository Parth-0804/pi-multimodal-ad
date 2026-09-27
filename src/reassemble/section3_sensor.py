"""Preregistered raw-sensor faults, exact frozen statistics and quality recomputation."""
from pathlib import Path
import time
import warnings
import numpy as np
import pandas as pd
import h5py
import joblib
from sklearn.linear_model import LogisticRegression
from threadpoolctl import threadpool_limits
from .completion_common import config,read,write,storage,seed_for,progress
from .section1_features import cohort,statistics,sha
from .section1_models import load_features,Standardizer,sigmoid
from .alignment import timestamps_1d,interval_indices,resample_progress,sensor_quality


def corrupt_stream(values,timestamps,start,end,family,severity,seed,sigma,median,channel_mask,offset,block_start):
    x=values.copy(); ix=interval_indices(timestamps,start,end)
    width=x.shape[1]
    if family=='S1':
        noise=np.random.default_rng(seed).normal(size=(len(ix),width))
        x[ix] += severity*sigma[offset:offset+width]*noise
    elif family=='S2':
        selected=channel_mask[(channel_mask>=offset)&(channel_mask<offset+width)]-offset
        x[np.ix_(ix,selected)]=np.nan
    elif family=='S3':
        selected=ix[(timestamps[ix]>=start+block_start*(end-start))&(timestamps[ix]<=start+(block_start+severity)*(end-start))]
        x[selected]=np.nan
    elif family=='S4' and offset<6:
        width_ft=min(width,6-offset)
        x[np.ix_(ix,np.arange(width_ft))]=median[offset:offset+width_ft]
    return x


def sensor_probability(checkpoint,features):
    scaled=np.nan_to_num((features-checkpoint['mean'])/checkpoint['std'],nan=0,posinf=0,neginf=0).astype('float32')
    raw=checkpoint['model'].decision_function(scaled)
    calibration=checkpoint['calibration']
    return sigmoid(raw*calibration['coefficient']+calibration['intercept'])


def recover_models(c,base,frame,arrays,splits,folder):
    y=frame.failure.to_numpy(dtype=int); fold=np.full(len(frame),-1)
    for outer in splits['folds']:
        k=outer['fold']; path=folder/f'sensor_fold{k}.joblib'
        tr=np.flatnonzero(frame.recording_id.isin(outer['train_recordings'])); te=np.flatnonzero(frame.recording_id.isin(outer['test_recordings']));fold[te]=k
        if path.exists():continue
        metadata=read(Path(base['run_dir'])/'predictions'/f'sensor_statistics_perm00_fold{k}.json')
        scaler=Standardizer().fit(arrays['statistics'][tr])
        model=LogisticRegression(C=metadata['selected'],class_weight='balanced',max_iter=2000,random_state=0).fit(scaler.transform(arrays['statistics'][tr]),y[tr])
        # Scalar calibration is preserved; no calibrator fitted to test predictions.
        checkpoint={'model':model,'mean':scaler.mean,'std':scaler.std,'calibration':metadata['calibration'],
                    'sigma':np.nanstd(arrays['sensor'][tr].astype('float64'),axis=(0,1)),
                    'median':np.nanmedian(arrays['sensor'][tr],axis=(0,1)),'train_rows':tr,'test_rows':te}
        with np.load(Path(base['run_dir'])/'predictions/sensor_statistics_perm00.npz') as z:expected=z['p'][te]
        difference=float(np.max(abs(sensor_probability(checkpoint,arrays['statistics'][te])-expected)))
        assert difference<=1e-5,('sensor recovery parity',k,difference)
        joblib.dump(checkpoint,path)
        write(path.with_suffix('.json'),{'source_C':metadata['selected'],'max_frozen_probability_difference':difference,'sigma_from':'outer training resampled sequence only','sha256':sha(path)})
    return fold


def main():
    c=config(); s=read('configs/reassemble/section3_corruptions.json'); base=read('configs/reassemble/section1.json'); c2=read('configs/reassemble/section2.json')
    root=Path(s['run_dir']); out=root/'sensor'; out.mkdir(exist_ok=True); models=root/'branches';models.mkdir(exist_ok=True)
    storage(); frame,arrays=load_features(base);splits=read(base['splits'])
    with threadpool_limits(limits=16,user_api='blas'):
        fold=recover_models(c,base,frame,arrays,splits,models)
    checkpoints={k:joblib.load(models/f'sensor_fold{k}.joblib') for k in range(5)}
    conditions=[v for v in s['conditions'] if v['family'] in ['clean','S1','S2','S3','S4']];names=[v['name'] for v in conditions]
    recordings=pd.read_parquet(Path(base['audit_run'])/'recordings.parquet').set_index('recording_id')
    for count,(rid,rows) in enumerate(frame.groupby('recording_id',sort=True)):
        path=out/(rid+'.npz')
        if path.exists():assert sha(path)==read(path.with_suffix('.json'))['sha256'];continue
        storage();started=time.perf_counter();checkpoint=checkpoints[int(fold[rows.index[0]])]
        raw=Path(base['data_root'])/'raw/data'/recordings.loc[rid,'filename']
        with h5py.File(raw,'r') as h:
            streams={name:(timestamps_1d(h['timestamps'][name][()]),np.asarray(h['robot_state'][name][()],dtype='float64')) for name in base['sensor']['channels']}
        audits={v['segment_id']:v for v in read(Path(base['audit_run'])/'records'/(rid+'.json'))['segments']}
        stats=np.zeros((len(names),len(rows),220),dtype='float32');quality=np.zeros((len(names),len(rows),30),dtype='float32')
        statistics_difference=0.;quality_difference=0.;warning_count=0
        for i,row in enumerate(rows.itertuples()):
            for j,condition in enumerate(conditions):
                family,severity=condition['family'],condition['severity'];seed=seed_for(s['seed'],rid,row.segment_id,family,severity);rng=np.random.default_rng(seed)
                channel_mask=np.sort(rng.choice(22,int(round(22*severity)),replace=False)) if family=='S2' else np.array([],dtype=int)
                block=float(rng.uniform(0,1-severity)) if family=='S3' else 0.
                offset=0;resampled=[];measures=[]
                for n,(t,original) in streams.items():
                    values=corrupt_stream(original,t,row.start,row.end,family,severity,seed_for(seed,n),checkpoint['sigma'],checkpoint['median'],channel_mask,offset,block)
                    offset+=original.shape[1]
                    resampled.append(resample_progress(t,values,row.start,row.end,512,5))
                    q=sensor_quality(t,values,row.start,row.end,512,5)
                    measures.extend([q[k] for k in c2['quality_sensor']])
                x=np.concatenate(resampled,axis=1).astype('float32')
                with warnings.catch_warnings(record=True) as captured:
                    warnings.simplefilter('always',RuntimeWarning);stats[j,i]=statistics(x)
                warning_count+=len(captured)
                quality[j,i]=np.asarray(measures,dtype='float32')
                if family=='clean':
                    difference=np.abs(stats[j,i]-arrays['statistics'][row.Index]);statistics_difference=max(statistics_difference,float(np.nanmax(difference)))
                    assert np.allclose(stats[j,i],arrays['statistics'][row.Index],rtol=0,atol=1e-6,equal_nan=True),('clean sensor feature mismatch',rid,row.segment_id,statistics_difference)
                    expected=np.array([audits[row.segment_id]['sensor'][n][k] for n in base['sensor']['channels'] for k in c2['quality_sensor']],dtype='float32')
                    assert np.allclose(quality[j,i],expected,rtol=0,atol=1e-6,equal_nan=True),('clean quality mismatch',rid,row.segment_id)
                    quality_difference=max(quality_difference,float(np.nanmax(abs(quality[j,i]-expected))))
        np.savez_compressed(path,row_index=rows.index.to_numpy(),statistics=stats,quality=quality,names=np.asarray(names))
        write(path.with_suffix('.json'),{'sha256':sha(path),'clean_statistics_max_difference':statistics_difference,'clean_quality_max_difference':quality_difference,'expected_NaN_statistic_warnings':warning_count,'seconds':time.perf_counter()-started,'conditions':names})
        progress(f'Section 3 sensor faults: {count+1}/148 recordings complete')
    progress('Section 3 sensor corruption extraction complete')

if __name__=='__main__':main()
