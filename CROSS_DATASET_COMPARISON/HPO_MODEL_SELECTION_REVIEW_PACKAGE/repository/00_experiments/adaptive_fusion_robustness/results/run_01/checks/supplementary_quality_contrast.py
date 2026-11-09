"""Requested additive-quality contribution, from saved assessment tables only.
Declared before assessment; no predictors, fitting, selection or new trials.
"""
from pathlib import Path
import sys,json,hashlib,os
for n in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[n]='2'
if hasattr(os,'sched_getaffinity'):os.sched_setaffinity(0,[12,13])
ROOT=Path(__file__).resolve().parents[3];RUN=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'code'))
import numpy as np,pandas as pd
from sklearn.metrics import average_precision_score
from metrics import weighted_bootstrap_ap

def main():
 cfg=json.loads((RUN/'config/resolved_config.json').read_text());rng=np.random.default_rng(314159);points=[];boot=[];invalid=np.zeros(2000,bool);hashes={}
 for fold in cfg['locked_folds']:
  root=RUN/'predictions'/fold;clean=pd.read_csv(root/'clean/clean/repeat_00/predictions.csv',dtype={'recording_id':str,'segment_id':str}).sort_values(['recording_id','segment_id']).reset_index(drop=True);y=clean.failure.to_numpy();recordings=clean.recording_id.to_numpy();unique=np.unique(recordings);draws=rng.multinomial(len(unique),np.ones(len(unique))/len(unique),size=2000);weights=draws[:,np.searchsorted(unique,recordings)].astype(float);invalid|=(weights@y==0)|(weights@(1-y)==0);hashes[fold]=hashlib.sha256(draws.astype('<i8').tobytes()).hexdigest();fold_points=[];fold_boot=[]
  for family in ['image_noise','sensor_noise']:
   for level in ['mild','medium','strong']:
    for repeat in [1,2,3]:
     t=pd.read_csv(root/family/level/f'repeat_{repeat:02d}/predictions.csv',dtype={'recording_id':str,'segment_id':str}).sort_values(['recording_id','segment_id']).reset_index(drop=True);assert t[['recording_id','segment_id']].equals(clean[['recording_id','segment_id']]);assert np.array_equal(t.failure,y)
     a=t.p_quality_additive.to_numpy();b=t.p_static_augmented.to_numpy();fold_points.append(average_precision_score(y,a)-average_precision_score(y,b));fold_boot.append(weighted_bootstrap_ap(y,a,weights)-weighted_bootstrap_ap(y,b,weights))
  points.append(np.mean(fold_points));boot.append(np.mean(fold_boot,axis=0))
 values=np.mean(boot,axis=0);valid=(~invalid)&np.isfinite(values);lo,hi=np.percentile(values[valid],[2.5,97.5]);summary=pd.read_csv(RUN/'comparison/model_comparison.csv').set_index('model');difference=float(np.mean(points));assert abs(difference-(summary.loc['quality_additive','primary_mean_fold_AP']-summary.loc['static_augmented','primary_mean_fold_AP']))<1e-12
 old=json.loads((RUN/'checks/bootstrap.json').read_text());assert hashes==old['recording_draws_sha256']
 d={'contrast':'quality_additive_minus_static_augmented_PRIMARY','AP_difference':difference,'lower95':float(lo),'upper95':float(hi),'valid_replicates':int(valid.sum()),'invalid_replicates':int((~valid).sum()),'seed':314159,'exploratory_secondary':True};pd.DataFrame([d]).to_csv(RUN/'comparison/additive_quality_contribution.csv',index=False,float_format='%.17g');(RUN/'checks/additive_quality_contribution.json').write_text(json.dumps({'passed':True,'identical_recording_draws_verified':True,**d},indent=2)+'\n');print(json.dumps(d))
if __name__=='__main__':main()
