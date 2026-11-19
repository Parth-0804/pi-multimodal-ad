"""Full synthetic prediction-to-eight-reports integration, isolated in tmp."""
import importlib.util
import hashlib
import json
import sys
from pathlib import Path
import pandas as pd

sys.path[:0]=['src','MSM/99_preserved_previous_work/MILLING_DATASET/source','CROSS_DATASET_COMPARISON/src']
from external_eval.io import write_json
from external_eval.evaluate import execute_case
from external_eval import reports,publication,qualitative

spec=importlib.util.spec_from_file_location('evaluation_fixture',Path('MSM/tests/test_external_evaluation.py'))
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)


def test_saved_predictions_reproduce_metrics_figures_and_eight_reports(tmp_path,monkeypatch):
    root=tmp_path/'MSM';root.mkdir();s=fixture.FakeStore(root)
    s.dataset='MSM';s.condition='P';s.channels=['c0','c1'];s.adapter_identity={'sha256':'synthetic'}
    s.config.update(dataset='MSM',sensor_channels=s.channels,seeds=[42])
    s.config['quality_gate']['epochs']=2
    s.frame['native_label']=s.frame.target;s.frame['direction']=s.frame.target.map({0:'DOWN',1:'UP'})
    s.frame['machine']='synthetic_machine';s.frame['calendar_date_group']=s.frame.group_id
    s.frame['duration_s']=1.
    for folder in ['02_labels_and_alignment','03_processed_model_inputs/visual_features/P','04_experiment_protocol','06_evaluation_results/metrics','06_evaluation_results/calibration','07_robustness_experiments']:(root/folder).mkdir(parents=True,exist_ok=True)
    definition={'sample_ids':s.frame.sample_id.tolist(),'grouping':'group_id'}
    fold={'train':list(range(16)),'test':list(range(16,24)),
        'inner':[(list(range(8)),list(range(8,16))),(list(range(8,16)),list(range(8)))]}
    case=execute_case(s,'primary__group_id',definition,0,fold,42)
    write_json(root/'03_processed_model_inputs/split_manifests/frozen_splits.json',{'primary__group_id':{**definition,'plan':[fold]}})
    write_json(root/'06_evaluation_results/P_EVALUATION_COMPLETE.json',{'cases':[case]})
    write_json(root/'04_experiment_protocol/experiment_config.json',s.config)
    write_json(root/'02_labels_and_alignment/validation_gate.json',{'passed':True})
    write_json(root/'03_processed_model_inputs/visual_features/P/complete.json',{'synthetic_fixture':True,'examples':24})
    s.frame.to_csv(root/'03_processed_model_inputs/final_sample_manifest.csv',index=False)
    s.frame.to_csv(root/'02_labels_and_alignment/original_label_inventory.csv',index=False)
    pd.DataFrame([{'sample_id':ident,'native_frame_index':j,'decoded_frame_sha256':hashlib.sha256(f'synthetic:{ident}:{j}'.encode()).hexdigest()} for ident in s.frame.sample_id for j in range(16)]).to_csv(root/'02_labels_and_alignment/alignment_manifest.csv',index=False)
    pd.DataFrame(columns=['exclusion_reasons']).to_csv(root/'02_labels_and_alignment/excluded_examples.csv',index=False)
    (root/'README.md').write_text('Synthetic preparation placeholder\n')
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(publication,'prepare',lambda root:None)
    monkeypatch.setattr(qualitative,'make_examples',lambda *args:None)
    reports.run(root)
    required=['DATASET_OVERVIEW','DATASET_VALIDATION','MODEL_IMPLEMENTATION','EXPERIMENT_RESULTS','ROBUSTNESS_RESULTS','RESEARCH_CONCLUSIONS','REPRODUCIBILITY','REVIEW_HANDOFF']
    assert all((root/'09_final_reports'/(name+'.md')).is_file() for name in required)
    check=json.loads((root/'06_evaluation_results/metric_reproduction.json').read_text())
    assert check['all_saved_fold_metrics_match_predictions'] and check['checks']>200
    assert (root/'06_evaluation_results/figures/training_curves.png').is_file()
    reports.run(root) # Exact immutable reuse, not another fit/report mutation.
