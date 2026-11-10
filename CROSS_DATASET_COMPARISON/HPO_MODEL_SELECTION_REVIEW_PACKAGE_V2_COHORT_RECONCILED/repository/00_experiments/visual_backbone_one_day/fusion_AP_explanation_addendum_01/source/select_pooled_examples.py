"""Select four explicitly illustrative failures relevant to the pooled AP question."""
from pathlib import Path
import pandas as pd

root=Path(__file__).resolve().parents[1]
selected=[]
for frames in [16,32]:
    data=pd.read_csv(root/'tables'/f'label_aware_paired_changes_{frames}_frames.csv',dtype={'sample_id':str,'recording_id':str,'segment_id':str})
    mask=(data.failure==1)&(data.visual_pooled_rank_change<0)&(data.F2_pooled_rank_change>0)
    # Pooled visual ranking improves while pooled fusion ranking worsens.
    # Select two largest visual displacements, then stable sample identity.
    candidates=data[mask].sort_values(['visual_pooled_rank_change','sample_id'],ascending=[True,True]).head(2)
    for row in candidates.to_dict('records'):
        selected.append({'selection':'Two largest visual pooled-rank improvements among failures whose pooled fusion rank worsens, per matched frame-count comparison',**row})
pd.DataFrame(selected).to_csv(root/'tables/selected_pooled_AP_rank_examples.csv',index=False)
print(pd.DataFrame(selected)[['frames','sample_id','recording_id','segment_id','visual_frozen_probability','visual_fine_tuned_probability','F2_frozen_probability','F2_fine_tuned_probability','visual_pooled_rank_change','F2_pooled_rank_change','visual_log_loss_change','F2_log_loss_change']].to_string(index=False))
