"""Extract only actually completed ViFailback fits and saved prediction evidence."""
from pathlib import Path
import numpy as np

from audit_common import OUT,REPO,NR,DEFAULT,read,evidence,digest,rel,write
from metrics_check import metrics,compare

ROOT=Path('VIFAILBACK')


def scalar_metrics(report):
    result={k:v for k,v in report.items() if isinstance(v,(int,float)) and not isinstance(v,bool)}
    cm=report.get('confusion_matrix_0_1')
    if cm is not None:
        matrix=np.asarray(cm).reshape(2,2)
        result.update(TN=int(matrix[0,0]),FP=int(matrix[0,1]),FN=int(matrix[1,0]),TP=int(matrix[1,1]))
    return result


def extract(audit):
    cpath=ROOT/'configs/experiment.json';c=read(cpath)
    splitroot=REPO/ROOT/'04_evaluation_splits'
    jobs=None
    for path in splitroot.rglob('*.json'):
        if 'writing' in path.name:continue
        obj=read(path)
        candidate=obj.get('jobs') if isinstance(obj,dict) else obj
        if isinstance(candidate,list) and candidate and isinstance(candidate[0],dict) and 'ids' in candidate[0]:
            jobs={j['id']:j for j in candidate};break
    assert jobs is not None,'VIFAILBACK_SPLIT_JOBS_NOT_LOCATED'
    pooled={}
    base=REPO/ROOT/'06_training_experiments'
    for done in sorted(base.glob('*/runs/*/seed*/outer*/COMPLETE.json')):
        item=read(done);folder=done.parent;family=folder.parts[-5]
        if family not in ['visual_frozen','visual_frozen_high_only','sensor_baselines']:continue
        seed=item['seed'];job=jobs[item['fit_id']];stage='HELD-OUT' if job['inner']==-1 else 'INNER-OOF ASSESSMENT'
        runid=rel(folder);prediction=folder/'predictions.json'
        assert digest(prediction)==item['prediction_sha256']
        predictions=read(prediction);report=read(folder/'metrics.json')
        common={'seed':seed,'outer_fold':job['outer'],'inner_fold':job['inner'],
                'split_identifier':item.get('split_sha256',item.get('identity',NR)),
                'dataset_version':c['revision'],'threshold':.5,
                'normalization':'T-only standardization; sigmoid calibration on task-disjoint C',
                'class_weighting':'T negative/positive or balanced','precision':'float32'}
        labels=[r['label'] for r in predictions]
        assert [r['episode_index'] for r in predictions]==job['ids']['A']
        assert len(labels)==len(set(r['episode_index'] for r in predictions))
        if family.startswith('visual'):
            condition=item['condition'];history=read(folder/'HISTORY.json')
            assert item['executed_epochs']==len(history)==100
            assert [h['epoch'] for h in history]==list(range(1,101))
            assert digest(folder/'BEST_MODEL.pt')==item['best_checkpoint_sha256']
            assert digest(folder/'FINAL_EPOCH100.pt')==item['final_checkpoint_sha256']
            maxV=max(h['V_macro_AP'] for h in history)
            selected=next(h['epoch'] for h in history if h['V_macro_AP']==maxV)
            assert selected==item['selected_epoch']
            cfg={**common,'optimizer':'AdamW','head_learning_rate':c['head_lr'],
                'backbone_learning_rate':0,'weight_decay':c['weight_decay'],'betas':DEFAULT,'epsilon':DEFAULT,
                'gradient_clipping':c['gradient_clip'],'effective_batch_size':c['gradient_accumulation'],
                'batch_size':c['gradient_accumulation'],'microbatch_size':'8 cached pooled feature vectors',
                'gradient_accumulation':'no separate accumulation for frozen head; batch8',
                'scheduler':'cosine multiplier1 to0.1 over100 epochs','scheduler_parameters':{'horizon':100},
                'max_configured_epochs':100,'executed_epochs':100,'early_stopping':False,
                'selected_epoch':selected,'selection_metric':'V macro AP, first strict maximum',
                'checkpoint_selection':'validation-selected epoch; execute all100 epochs',
                'loss':'T-weighted BCEWithLogits','augmentation':'none',
                'feature_dimension':896,'hidden_dimensions':[128],'dropout':.1,
                'trainable_layers':'fresh original classifier head only','trainable_parameters':114945,
                'frozen_parameters':11190112,'total_parameters':11305057,
                'backbone':'RT-DETR R18vd CNN only','camera_count':1 if condition=='V1_high_only' else 3,
                'frames_per_camera':16,'sampling':'round(linspace(0,N-1,16)); fixed camera order',
                'initialization':'original pinned pretrained CNN feature bank; fresh seeded classifier'}
            audit.run('VIFAILBACK',c['run_id'],condition,runid,cpath,cfg,
                training_status='COMPLETE',evidence_status='VERIFIED',checkpoint_path=rel(folder/'BEST_MODEL.pt'),
                last_checkpoint_path=rel(folder/'FINAL_EPOCH100.pt'),history_source=rel(folder/'HISTORY.json'),
                train_N=len(job['ids']['T']),validation_N=len(job['ids']['V']),calibration_N=len(job['ids']['C']),
                assessment_N=len(job['ids']['A']),duration_train_plus_validation_hours=item['training_and_validation_seconds']/3600,
                entry_point='VIFAILBACK/scripts/worker.py --stage train --condition '+condition,
                configuration_function='vifailback.training.fit/optimizer_for',actual_scope=stage)
            for h in history:
                audit.histories.append({'dataset':'VIFAILBACK','experiment_id':c['run_id'],'run_id':runid,
                    'model':condition,'seed':seed,'outer_fold':job['outer'],'role':stage,
                    'history_source':rel(folder/'HISTORY.json'),**h})
            model_reports={condition:(report,[r['probability'] for r in predictions])}
        else:
            model=read(folder/'S3_MODEL.json');selection=read(folder/'S2_SELECTION_AND_CALIBRATION.json')
            assert digest(folder/'S3_MODEL.json')==item['S3_checkpoint_sha256']
            assert digest(folder/'S2_MODEL.joblib')==item['S2_checkpoint_sha256']
            cfg={**common,'C':1.,'solver':'lbfgs','penalty':DEFAULT,'max_iter':2000,
                'tolerance':DEFAULT,'feature_dimension':280,'class_weighting':'balanced',
                'executed_epochs':'NOT APPLICABLE','selection_metric':'predefined C1; separate C calibration',
                'sensor_channels':28,'initialization':'new logistic fit','trainable_parameters':281}
            audit.run('VIFAILBACK',c['run_id'],'S1_equals_S3_sensor_logistic',runid+'::S3',folder/'S3_MODEL.json',cfg,
                training_status='COMPLETE',evidence_status='VERIFIED',checkpoint_path=rel(folder/'S3_MODEL.json'),
                train_N=len(job['ids']['T']),validation_N=len(job['ids']['V']),calibration_N=len(job['ids']['C']),
                assessment_N=len(job['ids']['A']),entry_point='VIFAILBACK/scripts/worker.py --stage baselines',
                configuration_function='vifailback.baselines.run / source sensor_fit')
            import joblib
            from sklearn.ensemble import HistGradientBoostingClassifier
            hgb=joblib.load(evidence(folder/'S2_MODEL.joblib','source-identified study estimator; receipt SHA verified'))
            assert isinstance(hgb,HistGradientBoostingClassifier)
            params=hgb.get_params(deep=True)
            for candidate in selection['candidates']:
                leaves=candidate['max_leaf_nodes'];is_selected=leaves==selection['selected_max_leaf_nodes']
                candidate_params={**params,'max_leaf_nodes':leaves}
                hcfg={**common,**candidate_params,'feature_dimension':280,
                      'class_weighting':'balanced','normalization':'native statistics; HGB missing handling; C sigmoid calibration only on selected model',
                      'executed_epochs':'NOT APPLICABLE','selection_metric':'V macro AP across leaves7/15/31',
                      'selected_max_leaf_nodes':selection['selected_max_leaf_nodes'],
                      'estimator_parameters':candidate_params,'selection_candidate_V_macro_AP':candidate['V_macro_AP']}
                audit.run('VIFAILBACK',c['run_id'],'S2_sensor_HGB',runid+f'::S2_leaves{leaves}',folder/'S2_SELECTION_AND_CALIBRATION.json',hcfg,
                    training_status='COMPLETE',evidence_status='VERIFIED' if is_selected else 'PARTIALLY VERIFIED',
                    checkpoint_path=rel(folder/'S2_MODEL.joblib') if is_selected else 'NOT RETAINED — unselected HPO candidate',
                    train_N=len(job['ids']['T']),validation_N=len(job['ids']['V']),
                    assessment_N=len(job['ids']['A']) if is_selected else 0,
                    selected_candidate=is_selected,entry_point='VIFAILBACK/scripts/worker.py --stage baselines',
                    configuration_function='vifailback.baselines.run: for leaves in[7,15,31]')
            model_reports={name:(report[name],[r[name+'_probability'] for r in predictions]) for name in ['S3','S2']}
        for name,(saved,probabilities) in model_reports.items():
            vals=scalar_metrics(saved)
            check=compare(labels,probabilities,{'AP':saved['AP_failure'],'AUROC':saved['AUROC'],'Brier':saved['Brier'],'log_loss':saved['log_loss']})
            audit.checks.append({'check':'VIFAILBACK_saved_metrics','run_id':runid,'model':name,**check})
            audit.result('VIFAILBACK',c['run_id'],name,vals,folder/'metrics.json',stage=stage,
                seed=seed,fold=job['outer'],run_id=runid,held_out_N=len(labels),
                positive_count=sum(labels),negative_count=len(labels)-sum(labels),
                train_N=len(job['ids']['T']),validation_N=len(job['ids']['V']),
                prediction_file=rel(prediction),evaluation_script='VIFAILBACK/src/vifailback/metrics.py',threshold=.5)
            if stage=='HELD-OUT':pooled.setdefault((seed,name),[]).extend([(r['episode_index'],r['label'],float(p)) for r,p in zip(predictions,probabilities)])
    for done in sorted((base/'fusion_experiments/runs').glob('*/*/seed*/outer*/COMPLETE.json')):
        item=read(done);folder=done.parent;condition=item['condition'];seed=item['seed'];outer=item['outer']
        assert digest(folder/'predictions.json')==item['prediction_sha256']
        assert digest(folder/'F2_COEFFICIENTS.json')==item['f2_sha256']
        assert digest(folder/'QUALITY_GATE.pt')==item['gate_sha256']
        assert digest(folder/'QUALITY_NEUTRAL_GATE.pt')==item['gate_static_sha256']
        rows=read(folder/'predictions.json');saved=read(folder/'metrics.json')
        for name,checkpoint in [('F2','F2_COEFFICIENTS.json'),('quality_gate','QUALITY_GATE.pt'),('gate_static','QUALITY_NEUTRAL_GATE.pt')]:
            cfg={'seed':seed,'outer_fold':outer,'threshold':.5,'class_weighting':None,
                 'selection_metric':'predefined configuration','augmentation':False,
                 'feature_dimension':2 if name=='F2' else 13,'precision':'float32'}
            if name=='F2':cfg.update(C=1.,solver='lbfgs',penalty=DEFAULT,max_iter=2000,tolerance=DEFAULT,trainable_parameters=3,executed_epochs='NOT APPLICABLE')
            else:cfg.update(optimizer='AdamW',learning_rate=.001,weight_decay=.001,batch_size=64,
                            gradient_clipping=1.,hidden_dimensions=[16],max_configured_epochs=40,
                            executed_epochs=40,selected_epoch=40,early_stopping=False,
                            normalization='meta-training quality mean/std plus availability',betas=DEFAULT,epsilon=DEFAULT)
            audit.run('VIFAILBACK',c['run_id'],condition+'_'+name,rel(folder)+'::'+name,folder/checkpoint,cfg,
                training_status='COMPLETE',evidence_status='VERIFIED',checkpoint_path=rel(folder/checkpoint),
                train_N=item['meta_rows'],assessment_N=item['outer_rows'],
                entry_point='VIFAILBACK/scripts/worker.py --stage fusion --condition '+condition,
                configuration_function='vifailback.fusion.run/fit_gate; source stacker')
        for name,column in [('F1_average','F1_average'),('F2','F2_probability'),('quality_gate','gate_probability'),('gate_static','gate_static_probability')]:
            vals=scalar_metrics(saved[name]);labels=[r['label'] for r in rows];p=[r[column] for r in rows]
            check=compare(labels,p,{'AP':saved[name]['AP_failure'],'AUROC':saved[name]['AUROC'],'Brier':saved[name]['Brier'],'log_loss':saved[name]['log_loss']})
            audit.checks.append({'check':'VIFAILBACK_saved_fusion_metrics','run_id':rel(folder),'model':name,**check})
            audit.result('VIFAILBACK',c['run_id'],name,vals,folder/'metrics.json',stage='HELD-OUT',seed=seed,fold=outer,
                held_out_N=len(rows),positive_count=sum(labels),negative_count=len(rows)-sum(labels),
                prediction_file=rel(folder/'predictions.json'),evaluation_script='VIFAILBACK/src/vifailback/metrics.py',threshold=.5)
            pooled.setdefault((seed,name),[]).extend([(r['episode_index'],r['label'],float(v)) for r,v in zip(rows,p)])
    for (seed,name),rows in pooled.items():
        assert len(rows)==4382 and len({r[0] for r in rows})==4382
        y=[r[1] for r in rows];p=[r[2] for r in rows];score=metrics(y,p)
        success=metrics(1-np.asarray(y),1-np.asarray(p))['AP']
        score.update(AP_failure=score['AP'],AP_success=success,macro_AP=(score['AP']+success)/2)
        audit.result('VIFAILBACK',c['run_id'],name,score,ROOT/'06_training_experiments',stage='HELD-OUT POOLED',seed=seed,fold='pooled3',
            held_out_N=4382,positive_count=sum(y),negative_count=4382-sum(y),threshold=.5,
            evaluation_script='audit_utilities/metrics_check.py; no refitting',
            metric_origin='AUDIT_RECOMPUTED_FROM_EXISTING_PREDICTIONS',
            bootstrap_interval='NOT AVAILABLE in inspected completed-run evidence')
    for path in [ROOT/'logs/20261029T004900Z/PIPELINE_STATUS.json',ROOT/'logs/20261029T004900Z/CONTROLLER_PROCESS.json']:
        read(path)
    print('VIFAILBACK_EXTRACTED','jobs',len(jobs),'pooled model-seed banks',len(pooled),flush=True)
