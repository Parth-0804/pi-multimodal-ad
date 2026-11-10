"""Reproduce preserved laboratory eligibility, without rerunning synchronization."""
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd

LEGACY=Path('MSM/99_preserved_previous_work/MILLING_DATASET')
sys.path[:0]=['src',str(LEGACY/'source'),'CROSS_DATASET_COMPARISON/src']
from finish_full_lab import validate,read_checkpoints
from external_eval.io import write_json,csv_rows,sha


def main():
    finished=Path('MSM/02_labels_and_alignment/validation_gate.json')
    if finished.exists() and Path('MSM/04_experiment_protocol/experiment_config.json').exists():
        config=json.loads(Path('MSM/04_experiment_protocol/experiment_config.json').read_text())
        if sha('MSM/03_processed_model_inputs/final_sample_manifest.csv')!=config['sample_manifest_sha256']:raise ValueError('Completed MSM sample manifest changed')
        print('REUSED complete MSM validation',flush=True);return
    original=LEGACY/'runs/20261027T015205931708Z-stage5-full-lab-validated'
    cfg=json.loads((original/'config/resolved_config.json').read_text())
    # The original checkpoint root is deliberately retained as an authoritative reference.
    cfg['run_root']=cfg['acquisition_and_audit_run'];parent=Path(cfg['run_root'])
    results=read_checkpoints(parent,cfg['selected_groups'])
    frame=pd.DataFrame([r for x in results for r in x['intervals']])
    verified=validate(results,cfg,frame)
    assert len(frame)==2512 and frame.native_label.value_counts().to_dict()=={0:1877,1:458,2:177}
    admitted=frame.loc[frame.joint_technical_pass].copy().reset_index(drop=True)
    assert len(admitted)==1895 and admitted.native_label.value_counts().to_dict()=={0:1434,1:336,2:125}
    assert admitted.group_id.nunique()==45 and admitted.loc[admitted.native_label==1].group_id.nunique()==17
    # Metadata used only for diagnostics/grouping, explicitly separate from the 90 predictors.
    native={g:pd.read_csv(Path(cfg['data_root'])/g/'label.csv') for g in admitted.group_id.unique()}
    admitted['direction']=[native[r.group_id].iloc[r.source_row-2].direction for r in admitted.itertuples()]
    admitted['target']=(admitted.native_label==1).astype(int)
    admitted['sample_id']=admitted.interval_id
    admitted['sar_num']=3;admitted['sar_den']=8
    assert all(json.loads(r.frame_indices_json).__len__()==16 for r in admitted.itertuples())
    dest=Path('MSM/02_labels_and_alignment')
    frame.to_csv(dest/'original_label_inventory.csv',index=False)
    admitted.to_csv(dest/'validated_labels.csv',index=False)
    frame.loc[~frame.joint_technical_pass].to_csv(dest/'excluded_examples.csv',index=False)
    admitted.to_csv('MSM/03_processed_model_inputs/final_sample_manifest.csv',index=False)
    old_frames=pd.read_csv(original/'manifests/selected_frame_manifest.csv')
    old_frames.loc[old_frames.interval_id.isin(admitted.interval_id)].to_csv(dest/'alignment_manifest.csv',index=False)
    old_stats=pd.read_csv(original/'manifests/common_mtc_statistics.csv').set_index('interval_id')
    old_stats.loc[admitted.interval_id].to_csv('MSM/03_processed_model_inputs/sensor_features/interval_statistics.csv')
    summary={'passed':True,'raw_native_intervals':len(frame),'native_labels':{'0':1877,'1':458,'2':177},
        'joint_intervals':len(admitted),'joint_native_labels':{'0':1434,'1':336,'2':125},'nominal_groups':45,'positive_groups':17,
        'source_validation':verified,'source_final_manifest':str(original/'MSM_FULL_LAB_ELIGIBILITY_MANIFEST.csv'),
        'source_manifest_sha256':sha(original/'MSM_FULL_LAB_ELIGIBILITY_MANIFEST.csv'),
        'direction_contingency':pd.crosstab(admitted.direction,admitted.native_label).to_dict(),
        'video_observability':'Technical alignment passes; optical anomaly visibility unverified; evaluate coarse retrospective context classification.',
        'primary_target':'1 vs 0/2','secondary_target':'1 vs 0, exclude 2'}
    # Convert pandas integer column keys for strict JSON.
    summary['direction_contingency']={str(k):{str(a):int(b) for a,b in v.items()} for k,v in summary['direction_contingency'].items()}
    write_json(dest/'validation_gate.json',summary)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
