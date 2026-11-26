"""Synthetic end-to-end metric/report check; never touches real study scores."""
from pathlib import Path
import sys,tempfile,json
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source'))
import evaluation,reporting
from common import ROOT,CONDITIONS,write,sha,config
from sklearn.metrics import average_precision_score

def main():
 events=[];settings=config().copy();settings['bootstrap_replicates']=12
 with tempfile.TemporaryDirectory(prefix='synthetic_evaluation_',dir=ROOT/'temporary') as temporary:
  root=Path(temporary);(root/'source').mkdir();(root/'source/evaluation.py').write_bytes((ROOT/'source/evaluation.py').read_bytes());(root/'checks').mkdir();(root/'comparison').mkdir();(root/'data_manifests').mkdir()
  write(root/'progress.json',{'status':'SYNTHETIC_TEST_ONLY','full_visual_fits_started':0,'preflight_optimizer_steps':0,'blocker':'Synthetic fixture is deliberately partial; no scientific fits'})
  evaluation.ROOT=root;reporting.ROOT=root;evaluation.config=lambda:settings;evaluation.event=lambda stage,**fields:events.append({'stage':stage,**fields})
  cohort=[];expected={};sensor=np.array([.12,.15,.8,.7,.25,.5,.3,.1,.65,.6,.9,.55]);truth=np.array([0,1,1,0,0,1,0,1,1,0,0,1])
  for k in range(12):cohort.append({'sample_id':f's{k:02d}','recording_id':f'recording_{k//2:02d}','segment_id':f'segment_{k%2}','failure':int(truth[k]),'action':'synthetic_action','start':0.,'end':2.,'frames16':list(range(0,32,2)),'frames32':list(range(32)),'timestamps16':np.linspace(0,2,16).tolist(),'timestamps32':np.linspace(0,2,32).tolist()})
  write(root/'data_manifests/cohort_and_frames.json',cohort)
  for index,name in enumerate(CONDITIONS):
   visual=np.clip(np.linspace(.05,.95,12)[np.roll(np.arange(12),index)],.01,.99);fused=.6*sensor+.4*visual;expected[name]=[average_precision_score(truth,p) for p in [visual,sensor,fused]]
   for outer,rows in enumerate([np.arange(6),np.arange(6,12)]):
    fold=f'fold_{outer+1:02d}';target=root/name/fold;target.mkdir(parents=True);frame=pd.DataFrame([cohort[i] for i in rows]);frame['fold_name']=fold;frame['p_visual']=visual[rows];frame['p_sensor']=sensor[rows];frame['p_fused']=fused[rows];path=target/'assessment_predictions.csv';frame.to_csv(path,index=False);write(target/'condition_complete.json',{'assessment_sha256':sha(path)})
  evaluation.evaluate();d=json.loads((root/'comparison/evaluation.json').read_text());assert d['status']=='PARTIAL' and len(d['paired_folds'])==2 and d['common_samples']==12
  table=pd.read_csv(root/'comparison/comparison_metrics.csv');assert len(table)==36
  for row in d['comparison']:
   for b,value in zip(['visual','sensor','fused'],expected[row['condition']]):assert abs(row[b+'_pooled_AP']-value)<1e-12
  bootstrap=json.loads((root/'comparison/bootstrap_policy.json').read_text());assert bootstrap['valid']==12 and bootstrap['undefined_discarded']==0
  draws=pd.read_csv(root/'comparison/bootstrap_draws.csv');assert len(draws)==12
  # Re-running the bootstrap from the same seed gives the same actual draws.
  first=(root/'comparison/bootstrap_draws.csv').read_bytes();folds,tables,sources=evaluation.paired_predictions();evaluation.bootstrap(tables);assert first==(root/'comparison/bootstrap_draws.csv').read_bytes()
  # Integer cluster weights match physical repeated sample rows for AP.
  multiplicity=np.repeat([2,0,1,1,0,2],2);repeated=np.repeat(np.arange(12),multiplicity);assert abs(average_precision_score(truth,sensor,sample_weight=multiplicity)-average_precision_score(truth[repeated],sensor[repeated]))<1e-12
  reporting.documents();assert 'PARTIAL' in (root/'README_FIRST.md').read_text();assert '12' in (root/'comparison/RESULTS_SUMMARY.md').read_text()
  assert len(list((root/'comparison/plots').glob('*.png')))==2
 write(ROOT/'checks/evaluation_integration_results.json',{'passed':True,'scope':'Synthetic temporary two-fold/four-condition probabilities only; no model fitting or real assessment scoring','synthetic_bootstrap_draws':12,'synthetic_prediction_rows_per_condition':12,'metric_rows_verified':36,'fixed_seed_draws_reproduced':True,'weighted_AP_equals_expanded_clusters':True,'partial_report_generated':True,'synthetic_plots_generated':2,'actual_study_progress_unchanged':True,'scientific_assessment_predictions_generated':False})
 print('PASS: synthetic two-fold four-condition evaluation, paired bootstrap, plots and partial report; no real study scoring.')

if __name__=='__main__':main()
