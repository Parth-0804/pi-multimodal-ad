"""Read-only selected clean replay diagnosis; no corrupted inference or fitting."""
import importlib.util
from pathlib import Path
entry=Path(__file__).resolve().parents[3]/'run_experiment.py'
spec=importlib.util.spec_from_file_location('entry',entry);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
import numpy as np,pandas as pd,torch
from common import RUN,REPO,read,write,config,sha
from inputs import Inputs
from corruptions import statistics_for
from pipeline import transform,linear,calibrate
selected=read(RUN/'model_selection/selected_model.json');f=pd.DataFrame(read(RUN/'data/cohort_and_frames.json'));jobs=read(RUN/'data/fit_partitions.json');j=next(j for j in jobs if j['fold_name']=='fold_01' and j['role']=='outer_assessment')
completed={p.stem for p in (RUN/'cache/clean_frame_features/fold_01').glob('*.npy')};failed=next(i for i in j['predict'] if f.iloc[i].sample_id not in completed);sample=f.iloc[failed].to_dict()
inputs=Inputs();streams,names,units=inputs.streams(sample);own=statistics_for([(n,t,x,np.zeros(x.shape,bool)) for n,t,x in streams],sample['start'],sample['end'])
prior=np.load(REPO/config()['visual_run']/'shared_cache/sensor_statistics.npy',mmap_mode='r')[failed]
m=read(REPO/selected['components']['fold_01']['sensor']['path'])
def predict(x):
 raw=linear(transform(x[None,:],m['mean'],m['std']),m['raw']);return float(raw[0]),float(calibrate(raw,m['calibrator'])[0])
old=predict(prior);new=predict(own)
out={'completed_clean_rows_before_failure':len(completed),'first_uncompleted_row':int(failed),'sample_key':[sample['recording_id'],sample['segment_id']], 'own_sensor_prediction':new,'original_sensor_statistics_prediction':old,'sensor_probability_abs':abs(old[1]-new[1]),'statistics_max_abs':float(np.max(abs(own-prior))),'differing_feature_indices':np.flatnonzero(own!=prior).tolist(),'own_feature_values':own.tolist(),'saved_feature_values':prior.tolist(),'channel_names':names}
write(RUN/'checks/clean_replay_diagnosis.json',out)
print({k:v for k,v in out.items() if k not in ['own_feature_values','saved_feature_values','differing_feature_indices','channel_names']})
