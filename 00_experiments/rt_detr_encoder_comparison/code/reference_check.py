"""Lightweight cached CPU replay of identified reference candidates, no new fits.

Does not admit reuse into the comparison: live pixel replay remains mandatory
when the GPU is available. No scores are calculated here.
"""
from pathlib import Path
import shutil
import numpy as np
import pandas as pd
import torch
from common import RUN,REPO,read,write,local,sha,config
from data import frame,KEYS
from fitting import reuse_source,reload_head,predict_head
from fusion import calibrated,sensor_predict


def check():
    torch.set_num_threads(2)
    f=frame();jobs=read(RUN/'data/fit_partitions.json');records=[];paths=[]
    prior=REPO/config()['prior_run']
    x=np.load(prior/'shared_cache/original_features_16.npy',mmap_mode='r')
    stats=np.load(RUN/'cache/sensor_statistics.npy',mmap_mode='r')
    for j in jobs:
        for component in ['visual','sensor']:
            candidate,reason=reuse_source(j,component)
            result={'fold':j['fold_name'],'role':j['role'],'component':component,'compatible_candidate':candidate is not None,'reason':reason}
            if candidate:
                path,info=candidate;rows=np.array(j['predict'][:3],int)
                table=pd.read_csv(path/'identified_branch_predictions.csv',dtype={'recording_id':str,'segment_id':str})
                assert table[KEYS].values.tolist()==f.iloc[j['predict']][KEYS].values.tolist()
                if component=='visual':
                    m,mean,std=reload_head(path/'model.pt','cpu');cal=read(path/'calibrator.json')
                    actual=calibrated(predict_head(m,x[rows],mean,std,'cpu'),cal)
                else:
                    m=read(path/'model_and_calibrator.json');_,actual=sensor_predict(stats[rows],m)
                error=float(np.max(abs(actual-table['p_'+component].iloc[:3].to_numpy())))
                assert error<=config()['probability_replay_tolerance'],'REFERENCE_CPU_REPLAY'
                destination=RUN/'data/reference_only'/j['fold_name']/j['role']/(component+'_predictions.csv')
                shutil.copyfile(path/'identified_branch_predictions.csv',local(destination))
                record={'origin':str((path/'identified_branch_predictions.csv').relative_to(REPO)),
                        'origin_sha256':sha(path/'identified_branch_predictions.csv'),
                        'local_prediction_table':str(destination.relative_to(RUN)),
                        'status':'REFERENCE_CANDIDATE_ONLY; no paired encoder predictions; not counted as completed comparison',
                        'cached_CPU_replay_max_abs':error,'replay_sample_keys':f.iloc[rows][KEYS].to_dict('records'),
                        'pending':'full pixel/extractor replay on allocated GPU before comparison reuse'}
                paths.append(record);result.update(record)
            records.append(result)
    write(RUN/'provenance/reuse_candidates.json',records)
    write(RUN/'checks/reference_cached_CPU_replay.json',{'passed':True,'scope':'Cached CPU replay, not live extractor or new training','prediction_tables':paths})
