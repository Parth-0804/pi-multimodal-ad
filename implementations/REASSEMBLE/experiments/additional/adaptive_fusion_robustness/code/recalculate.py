"""Independent saved-table primary estimand, no model or pipeline imports."""
from pathlib import Path
import json
import numpy as np,pandas as pd
from sklearn.metrics import average_precision_score
RUN=Path(__file__).resolve().parents[1]/'results/run_01'
def main():
 frames=[];verified=0;saved=pd.read_csv(RUN/'comparison/per_condition_metrics.csv')
 for path in sorted((RUN/'predictions').glob('fold_*/**/predictions.csv')):
  t=pd.read_csv(path,dtype={'recording_id':str,'segment_id':str});assert not t.duplicated(['recording_id','segment_id']).any()
  for model in ['historical_static','static_augmented','quality_additive','quality_interaction','visual','sensor']:
   p=t['p_'+model]
   if not np.isfinite(p).all():continue
   ap=average_precision_score(t.failure,p);fold=t.fold.iloc[0];family=t.family.iloc[0];level=t.level.iloc[0];repeat=int(t.repeat.iloc[0]);row=saved.loc[(saved.scope=='fold')&(saved.fold==fold)&(saved.family==family)&(saved.level==level)&(saved.repeat==repeat)&(saved.model==model)];assert len(row)==1 and abs(ap-row.AP.iloc[0])<=1e-12;verified+=1;frames.append({'fold':fold,'family':family,'level':level,'repeat':repeat,'model':model,'AP':ap})
 t=pd.DataFrame(frames);primary=t.loc[t.family.isin(['image_noise','sensor_noise'])];summary=primary.groupby(['fold','family','level','model']).AP.mean().groupby(['fold','family','model']).mean().groupby(['fold','model']).mean().groupby('model').mean();delta=float(summary.quality_interaction-summary.static_augmented);intervals=pd.read_csv(RUN/'comparison/paired_intervals.csv');reported=intervals.loc[intervals.contrast=='interaction_minus_augmented_static_PRIMARY','AP_difference'].iloc[0];assert abs(delta-reported)<=1e-12
 result={'passed':True,'AP_values_recalculated':verified,'primary_interaction_minus_augmented_static':delta,'aggregation':'Pandas groupby means: repeats, severities, families, folds; separate sklearn AP per original CSV','not_external_review':True};(RUN/'checks/independent_recalculation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
