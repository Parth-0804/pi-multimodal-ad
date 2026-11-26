"""Canonical MSM/Handover fits, complete metric tables and safe prediction checks."""
from pathlib import Path
import gzip
import re
import numpy as np
import pandas as pd

from audit_common import OUT,REPO,NR,DEFAULT,read,evidence,digest,rel,csv_read,write
from metrics_check import compare


def extract(audit):
    frozen=read('CROSS_DATASET_COMPARISON/configs/frozen_core.json')
    roots=[('MSM',Path('MSM')),('HANDOVER',Path('HANDOVER/experiments/common_support_v2'))]
    case_by_id={}
    verified=[]
    for dataset,root in roots:
        config=read(root/'04_experiment_protocol/experiment_config.json')
        complete=read(root/'06_evaluation_results/P_EVALUATION_COMPLETE.json')
        for case in complete['cases']:case_by_id[case['case_id']]=case
        for marker in sorted((REPO/root/'05_trained_models/visual_only').glob('*/*/FIT_COMPLETE.json')):
            item=read(marker);seed=item['actual_seed'];key=item['nominal_case'];role=item['role']
            case=case_by_id[key];fold=case['fold'];train_N=len(item['train_rows'])
            common={'seed':seed,'outer_fold':fold,'inner_fold':role,'split_identifier':case['protocol'],
                    'threshold':.5,'class_weighting':'T negative/positive for visual; balanced sensor LR',
                    'normalization':'training-only per-feature Standardizer','precision':'FP32',
                    'selection_metric':'fixed final epoch; no model search','augmentation':'none'}
            visual={**common,'optimizer':'AdamW','learning_rate':frozen['visual']['learning_rate'],
                    'weight_decay':frozen['visual']['weight_decay'],'betas':DEFAULT,'epsilon':DEFAULT,
                    'batch_size':frozen['visual']['batch_size'],'effective_batch_size':frozen['visual']['batch_size'],
                    'gradient_clipping':1.,'max_configured_epochs':10,'executed_epochs':10,
                    'selected_epoch':10,'early_stopping':False,'scheduler':'none',
                    'optimizer_updates':item['log']['updates'],'feature_dimension':896,
                    'hidden_dimensions':[128],'dropout':.1,'trainable_layers':'classifier head only',
                    'backbone':'frozen RT-DETR R18vd CNN only','trainable_parameters':114945,
                    'frozen_parameters':11190112,'total_parameters':11305057,
                    'sampling':'16 bin-center frames per admitted interval/window',
                    'initialization':'pinned pretrained CNN; new seeded classifier head'}
            vp=Path(item['visual_checkpoint']);assert digest(vp)==item['visual_sha256']
            runid=rel(marker.parent)
            audit.run(dataset,'EXTERNAL_P_'+case['protocol'],'visual',runid+'::visual',marker,visual,
                      training_status='COMPLETE',evidence_status='VERIFIED',checkpoint_path=rel(vp),
                      history_source=rel(marker),train_N=train_N,assessment_N=case['test_examples'] if role=='final_refit' else NR,
                      entry_point='CROSS_DATASET_COMPARISON/src/external_eval/evaluate.py',
                      configuration_function='external_eval.models.fit_base / msm.models.fit_visual',
                      fit_unit='one visual classifier head fit')
            sensor={**common,'C':1.,'penalty':DEFAULT,'solver':'lbfgs','max_iter':2000,
                    'tolerance':DEFAULT,'class_weighting':'balanced','feature_dimension':90 if dataset=='MSM' else 36,
                    'executed_epochs':'NOT APPLICABLE','initialization':'new logistic estimator',
                    'trainable_parameters':91 if dataset=='MSM' else 37}
            audit.run(dataset,'EXTERNAL_P_'+case['protocol'],'sensor_logistic',runid+'::sensor_logistic',marker,sensor,
                      training_status='COMPLETE',evidence_status='VERIFIED',checkpoint_path=rel(marker),
                      train_N=train_N,entry_point='CROSS_DATASET_COMPARISON/src/external_eval/models.py',
                      configuration_function='fit_base / msm.models.SensorClassifier')
            if item.get('classical_checkpoint'):
                path=Path(item['classical_checkpoint']);assert digest(path)==item['classical_sha256']
                # This is an explicitly source-identified, study-created estimator,
                # not an arbitrary downloaded pickle. Its saved hash is checked first.
                import joblib
                from sklearn.ensemble import HistGradientBoostingClassifier
                model=joblib.load(evidence(path,'trusted study-owned HGB state, receipt hash verified'))
                assert isinstance(model,HistGradientBoostingClassifier)
                params=model.get_params(deep=True)
                hgb={**common,**params,'executed_epochs':'NOT APPLICABLE',
                     'class_weighting':'balanced sample weights; estimator class_weight=None',
                     'feature_dimension':sensor['feature_dimension'],'estimator_parameters':params,
                     'normalization':'same training-only sensor Standardizer',
                     'initialization':'new HistGradientBoostingClassifier'}
                audit.run(dataset,'EXTERNAL_P_'+case['protocol'],'sensor_histgradient',runid+'::sensor_HGB',marker,hgb,
                          training_status='COMPLETE',evidence_status='VERIFIED',checkpoint_path=rel(path),train_N=train_N,
                          entry_point='CROSS_DATASET_COMPARISON/src/external_eval/models.py',
                          configuration_function='fit_base; actual saved estimator.get_params()')
            losses=item['log']['losses'];updates_per_epoch=int(np.ceil(train_N/visual['batch_size']))
            assert len(losses)==10*updates_per_epoch
            for epoch in range(10):
                vals=losses[epoch*updates_per_epoch:(epoch+1)*updates_per_epoch]
                audit.histories.append({'dataset':dataset,'experiment_id':'EXTERNAL_P_'+case['protocol'],
                    'run_id':runid+'::visual','model':'visual','seed':seed,'outer_fold':fold,'role':role,
                    'epoch':epoch+1,'training_minibatch_loss_mean':float(np.mean(vals)),
                    'loss_averaging':'unweighted mean of original minibatch losses; not an inferred validation curve',
                    'history_source':rel(marker)})
        for path in sorted((REPO/root/'05_trained_models/f2_fusion').glob('*/*/*.json')):
            if path.name not in ['F2.json','F2_aug.json','QG_clean.json','QG_aug.json']:continue
            item=read(path);case=case_by_id[path.parent.parent.name];model=path.stem
            cfg={'seed':case['seed'],'outer_fold':case['fold'],'split_identifier':case['protocol'],
                 'threshold':.5,'selection_metric':'fixed final epoch/configuration','early_stopping':False,
                 'augmentation':'fixed lowest severity corruption views, clean weight0.5' if model.endswith('aug') else 'none',
                 'class_weighting':None,'precision':'FP32'}
            if model.startswith('F2'):
                cfg.update(C=1.,penalty=DEFAULT,solver='lbfgs',max_iter=2000,tolerance=DEFAULT,
                           feature_dimension=2,trainable_parameters=3,executed_epochs='NOT APPLICABLE',
                           normalization='none on probability inputs')
                checkpoint=path
            else:
                gate=frozen['quality_gate']
                cfg.update(optimizer='AdamW',learning_rate=gate['learning_rate'],weight_decay=gate['weight_decay'],
                           batch_size=gate['batch_size'],gradient_clipping=gate['clip_grad_norm'],
                           hidden_dimensions=[gate['hidden']],feature_dimension=38 if dataset=='MSM' else NR,
                           max_configured_epochs=gate['epochs'],executed_epochs=len(item['loss_by_epoch']),
                           selected_epoch=gate['epochs'],normalization='training-OOF quality moments plus availability flags',
                           betas=DEFAULT,epsilon=DEFAULT)
                checkpoint=path.with_suffix('.pt');assert digest(checkpoint)==item['sha256']
            audit.run(dataset,'EXTERNAL_P_'+case['protocol'],model,rel(path.parent)+'::'+model,path,cfg,
                      training_status='COMPLETE',evidence_status='VERIFIED',checkpoint_path=rel(checkpoint),
                      train_N=len(item.get('native_train_ids',[])) or NR,
                      entry_point='CROSS_DATASET_COMPARISON/src/external_eval/models.py',
                      configuration_function='fit_fusions/fit_quality',source_revision='source hashes in P_EVALUATION_COMPLETE.json')
        for case in complete['cases']:
            for name,h in case['output_hashes'].items():
                assert digest(name)==h
                evidence(name,'hash-protected evaluation artifact')
            metricpath=Path(case['metrics']);rows=csv_read(metricpath)
            table=pd.read_csv(evidence(case['predictions'],'saved held-out and training predictions'),compression='gzip')
            for row in rows:
                vals={k:float(v) for k,v in row.items() if v and k not in ['dataset','initialization','protocol','fold','seed','role','corruption','model','status']}
                stage='TRAINING IN-SAMPLE' if row['role']=='train' else 'HELD-OUT' if row['role']=='test' else 'VALIDATION OFFICIAL' if row['role']=='validation' else 'INNER-OOF ASSESSMENT'
                audit.result(dataset,'EXTERNAL_P_'+case['protocol'],row['model'],vals,metricpath,
                    stage=stage,seed=int(row['seed']),fold=int(row['fold']),run_id=case['case_id'],
                    held_out_N=int(float(row['examples'])),positive_count=int(float(row.get('positive',0) or 0)),
                    negative_count=int(float(row['examples']))-int(float(row.get('positive',0) or 0)),
                    train_N=case['train_examples'],validation_N=NR,threshold=.5,
                    prediction_file=case['predictions'],evaluation_script='CROSS_DATASET_COMPARISON/src/external_eval/evaluate.py',
                    corruption=row['corruption'],protocol=case['protocol'],model_status=row['status'])
                if row['corruption']=='clean' and row['role']=='test' and row['status']=='COMPLETE':
                    subset=table.loc[(table.model==row['model'])&(table.role=='test')&(table.corruption=='clean')]
                    assert not subset.sample_id.duplicated().any()
                    check=compare(subset.target,subset.probability,vals,tolerance=1e-10)
                    verified.append({'dataset':dataset,'case_id':case['case_id'],'model':row['model'],
                                     'prediction_IDs_unique':True,**check})
            del table
        print('EXTERNAL_EXTRACTED',dataset,'cases',len(complete['cases']),flush=True)
    audit.checks.extend(verified)
    write(OUT/'provenance/EXTERNAL_INDEPENDENT_METRIC_CHECKS.json',verified)
