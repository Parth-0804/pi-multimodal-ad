"""Read-only evidence reconciliation; writes only study review tables."""
import importlib.util
from pathlib import Path
entry=Path(__file__).resolve().parents[3]/'run_experiment.py'
spec=importlib.util.spec_from_file_location('entry',entry);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
import numpy as np,pandas as pd
from sklearn.metrics import average_precision_score
from common import RUN,REPO,read,write,csv,sha,config,budget,utc
selected=read(RUN/'model_selection/selected_model.json');lock=read(RUN/'model_selection/selection_lock.json');assert sha(RUN/'model_selection/selected_model.json')==lock['selected_model_sha256']
comparison=pd.read_csv(RUN/'model_selection/clean_comparison.csv');comparison['origin']=comparison.condition.map(lambda name:config()['encoder_run'] if name=='cnn_plus_encoder' else config()['visual_run'])
csv(RUN/'model_selection/clean_comparison.csv',comparison)
rows=[]
for fold,parts in selected['components'].items():
 for item in parts.values():assert sha(REPO/item['path'])==item['sha256']
 saved=pd.read_csv(REPO/parts['predictions']['path'],dtype={'recording_id':str,'segment_id':str})
 copied=pd.read_csv(RUN/'model_selection/clean_predictions'/(selected['condition']+'.csv'),dtype={'recording_id':str,'segment_id':str})
 copied=copied.loc[copied.fold_name==fold].sort_values(['recording_id','segment_id']).reset_index(drop=True);saved=saved.sort_values(['recording_id','segment_id']).reset_index(drop=True)
 assert copied[['recording_id','segment_id','failure']].equals(saved[['recording_id','segment_id','failure']])
 assert np.allclose(copied[['p_visual','p_sensor','p_fused']],saved[['p_visual','p_sensor','p_fused']],rtol=0,atol=1e-15)
 for branch in ['visual','sensor','fused']:
  value=float(average_precision_score(copied.failure,copied['p_'+branch]));rows.append({'condition':selected['condition'],'fold_name':fold,'scope':'saved_upstream_clean','branch':branch,'AP':value,'samples':len(copied),'recordings':copied.recording_id.nunique(),'failures':int(copied.failure.sum())})
  if branch=='fused':assert value==selected['clean_AP']
csv(RUN/'model_selection/clean_per_fold_metrics.csv',pd.DataFrame(rows))
keys=[]
for p in (RUN/'cache/clean_frame_features/fold_01').glob('*.json'):
 d=read(p);assert sha(p.with_suffix('.npy'))==d['sha256'];keys.append({'recording_id':d['identity']['sample_key'][0],'segment_id':d['identity']['sample_key'][1],'fold_name':'fold_01','evidence':'passed initial clean tolerance before frame cache write','cached_features_sha256':d['sha256'],'prediction_probabilities':'not persisted before initial assertion failure'})
csv(RUN/'checks/initial_clean_replay_coverage.csv',pd.DataFrame(keys))
preservation=read(RUN/'checks/preservation_scope.json')
for name,digest in preservation['governing_hashes'].items():assert sha(REPO/name)==digest
for name,digest in read(RUN/'provenance/preparation_identity.json')['source_snapshots'].items():assert sha(REPO/name)==digest
write(RUN/'checks/final_evidence_check.json',{'checked_utc':utc(),'passed':True,'scope':'saved clean selection recomputation and selected-component/source/governing identity checks; not completed live clean replay','recomputed_fused_AP':selected['clean_AP'],'selected_lock_unchanged':True,'cached_initial_passing_rows':len(keys),'resources':budget(scientific=False)})
print('Selection AP independently recomputed; locked components and pinned source/instructions unchanged; initial cached passing rows:',len(keys))
