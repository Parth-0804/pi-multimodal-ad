"""Dataset-specific measurements, strict predictor allowlists and corruption views."""
import collections
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path[:0]=['src','MSM/99_preserved_previous_work/MILLING_DATASET/source']
from stage2.audit_sensors import new_accumulator,accumulate,finalize
from external_eval.io import write_json,sha

STATS=['mean','std','rms','min','max','peak_to_peak']


def rng_for(seed,kind,sample_id):
    value=int.from_bytes(hashlib.sha256(f'{seed}|{kind}|{sample_id}'.encode()).digest()[:8],'little')
    return np.random.default_rng(value)


def statistics(values):
    if values.ndim!=2 or not len(values) or not np.isfinite(values).all():raise ValueError('Invalid actual sensor measurements')
    result=[]
    for column in values.T:
        state=new_accumulator();accumulate(state,column);v=finalize(state);result.extend(v[k] for k in STATS)
    return np.asarray(result,np.float32)


def sensor_quality(features,missing=None):
    a=np.asarray(features).reshape(len(features),-1,6)
    absent=np.zeros(a.shape[:2],np.float32) if missing is None else np.asarray(missing,np.float32)
    return np.concatenate([np.log1p(np.maximum(a[:,:,1],0)),absent],axis=1).astype(np.float32)


class Store:
    def __init__(self,dataset,condition='P',load_visual=True):
        self.root=Path(dataset);self.dataset=dataset;self.condition=condition
        self.config=json.loads((self.root/'04_experiment_protocol/experiment_config.json').read_text())
        if sha(self.root/'03_processed_model_inputs/final_sample_manifest.csv')!=self.config['sample_manifest_sha256']:raise ValueError('Frozen native cohort identity changed')
        self.input_identity={'sample_manifest':self.config['sample_manifest_sha256'],
            'sensor_features':sha(self.root/'03_processed_model_inputs/sensor_features/interval_statistics.csv')}
        self.dataset=self.config['dataset']
        adapter_path=Path(self.dataset)/'src/dataset_adapter.py'
        spec=importlib.util.spec_from_file_location(self.dataset.lower()+'_dataset_adapter',adapter_path)
        self.adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.adapter)
        self.adapter_identity={'path':str(adapter_path),'sha256':sha(adapter_path)}
        self.frame=pd.read_csv(self.root/'03_processed_model_inputs/final_sample_manifest.csv',keep_default_na=False)
        self.channels=self.config['sensor_channels'];self.columns=[f'{c}__{s}' for c in self.channels for s in STATS]
        table=pd.read_csv(self.root/'03_processed_model_inputs/sensor_features/interval_statistics.csv').set_index('interval_id')
        self.sensor=table.loc[self.frame.interval_id,self.columns].to_numpy(np.float32)
        if self.sensor.shape!=(len(self.frame),len(self.columns)) or not np.isfinite(self.sensor).all():raise ValueError('Invalid sensor input contract')
        self.index={s:i for i,s in enumerate(self.frame.sample_id)};self.raw_cache=collections.OrderedDict()
        self.visual={};self.visual_quality={};self.cache_identity=None
        if load_visual:self.load_visual()

    def load_visual(self):
        folder=self.root/'03_processed_model_inputs/visual_features'/self.condition
        if not (folder/'complete.json').exists():raise ValueError('Feature bank incomplete: '+str(folder))
        self.cache_identity=json.loads((folder/'identity.json').read_text())
        index=json.loads((folder/'cache_index.json').read_text())
        options=[x[0] for x in self.cache_identity['options']]
        names=options+['frame_dropout_'+str(i+1) for i in range(3)]
        self.visual={n:np.empty((len(self.frame),896),np.float32) for n in names}
        self.visual_quality={n:np.empty((len(self.frame),6),np.float32) for n in names}
        seen=set()
        for item in index:
            i=self.index[item['sample_id']];path=Path(item['path'])
            if sha(path)!=item['sha256']:raise ValueError('Feature bank hash changed')
            with np.load(path,allow_pickle=False) as z:
                if str(z['signature'])!=self.cache_identity['signature']:raise ValueError('Feature bank method identity changed')
                features=z['features'];q=z['quality']
                if features.shape!=(10,16,896) or not np.isfinite(features).all():raise ValueError('Wrong CNN input/output unit')
                for j,n in enumerate(options):
                    self.visual[n][i]=features[j].mean(0);self.visual_quality[n][i]=np.r_[q[j].mean(0),1.]
                order=rng_for(self.config['corruptions']['random_seed'],'frame_dropout',item['sample_id']).permutation(16)
                for j,drop in enumerate(self.config['corruptions']['frame_dropout']):
                    keep=np.sort(order[drop:]);name='frame_dropout_'+str(j+1)
                    self.visual[name][i]=features[0,keep].mean(0);self.visual_quality[name][i]=np.r_[q[0,keep].mean(0),len(keep)/16]
            seen.add(i)
        if len(seen)!=len(self.frame):raise ValueError('Incomplete example-to-feature join')

    def raw(self,index):
        r=self.frame.iloc[index]
        key=self.adapter.source_key(r)
        if key not in self.raw_cache:
            value=self.adapter.load_source(r,self.channels)
            self.raw_cache[key]=value
            if len(self.raw_cache)>8:self.raw_cache.popitem(last=False)
        self.raw_cache.move_to_end(key);x=self.adapter.interval_values(self.raw_cache[key],r)
        if len(x)!=int(r.mtc_rows_inside_cut) or not np.isfinite(x).all():raise ValueError('Sensor source/interval identity mismatch')
        return x

    def training_scale(self,train):
        a=self.sensor[train].astype(np.float64).reshape(len(train),len(self.channels),6)
        count=self.frame.iloc[train].mtc_rows_inside_cut.to_numpy(float)[:,None]
        mean=(count*a[:,:,0]).sum(0)/count.sum()
        second=(count*(a[:,:,1]**2+a[:,:,0]**2)).sum(0)/count.sum()
        return np.sqrt(np.maximum(second-mean**2,0))

    def corrupted_sensor(self,name,rows,train):
        if name=='clean':
            values=self.sensor[rows];return values,sensor_quality(values)
        key=hashlib.sha256(json.dumps({'name':name,'train':self.frame.iloc[train].sample_id.tolist(),'rows':self.frame.iloc[rows].sample_id.tolist(),
            'config':self.config['corruptions'],'source':sha(__file__),'adapter':self.adapter_identity,'sensor_manifest':sha(self.root/'03_processed_model_inputs/sensor_features/interval_statistics.csv')},sort_keys=True).encode()).hexdigest()
        folder=self.root/'03_processed_model_inputs/sensor_features/corruptions';folder.mkdir(exist_ok=True)
        dest=folder/(key+'.npz')
        if dest.exists():
            with np.load(dest,allow_pickle=False) as z:return z['features'],z['quality']
        kind,level=name.rsplit('_',1);level=int(level)-1;values=[];masks=[]
        scale=self.training_scale(train);mean=self.sensor[train].mean(0)
        for index in rows:
            ident=self.frame.iloc[index].sample_id
            x=self.raw(int(index)).copy();d=x.shape[1];mask=np.zeros(d,np.float32)
            if kind=='sensor_noise':
                rng=rng_for(self.config['corruptions']['random_seed'],'sensor_noise',ident)
                x+=rng.normal(size=x.shape)*scale*self.config['corruptions']['sensor_noise'][level]
                feature=statistics(x)
            elif kind in ['channel_dropout','missing_sensor_channels']:
                order=rng_for(self.config['corruptions']['random_seed'],kind,ident).permutation(d)
                number=min(d,max(1,int(np.ceil(d*self.config['corruptions'][kind][level]))));missing=order[:number]
                if kind=='channel_dropout':x[:,missing]=0;feature=statistics(x)
                else:
                    feature=self.sensor[index].copy().reshape(d,6);feature[missing]=mean.reshape(d,6)[missing];feature=feature.ravel();mask[missing]=1
            else:raise ValueError('Unknown actual sensor corruption: '+name)
            values.append(feature);masks.append(mask)
        values=np.asarray(values,np.float32);q=sensor_quality(values,np.asarray(masks))
        if not np.isfinite(values).all():raise ValueError('Nonfinite sensor corruption')
        # Multiple seeds/weight conditions share exactly the same measurement perturbation.
        part=dest.with_name(dest.stem+f'.{os.getpid()}.writing.npz')
        with part.open('xb') as f:np.savez_compressed(f,features=values,quality=q)
        try:os.link(part,dest)
        except FileExistsError:
            with np.load(dest,allow_pickle=False) as z:
                if not np.array_equal(z['features'],values):raise ValueError('Corruption reproducibility failure')
        return values,q

    def view(self,name,rows,train):
        visual_name=name if name in self.visual else 'clean'
        sensor_name=name if name.startswith(('sensor_noise_','channel_dropout_','missing_sensor_channels_')) else 'clean'
        sensor,sq=self.corrupted_sensor(sensor_name,rows,train)
        vision=self.visual[visual_name][rows];vq=self.visual_quality[visual_name][rows]
        availability=np.ones((len(rows),2),np.float32)
        if name=='missing_visual':availability[:,0]=0;vq=np.zeros_like(vq)
        if name=='missing_sensor':availability[:,1]=0;sq=np.zeros_like(sq)
        return {'visual':vision,'sensor':sensor,'quality':np.concatenate([vq,sq],axis=1),
                'availability':availability,'name':name}


def all_views(config):
    names=['clean']
    for key in ['gaussian_blur','brightness_contrast','partial_occlusion','frame_dropout','sensor_noise','channel_dropout','missing_sensor_channels']:
        names.extend(key+'_'+str(i+1) for i in range(len(config['corruptions'][key])))
    return names+['missing_visual','missing_sensor']


TRAIN_VIEWS=['clean','gaussian_blur_1','brightness_contrast_1','partial_occlusion_1','frame_dropout_1',
             'sensor_noise_1','channel_dropout_1','missing_sensor_channels_1']
