"""Reconstruct original and 20/100-epoch REASSEMBLE evidence without fitting."""
from pathlib import Path
import json
import re
import numpy as np

from audit_common import OUT,REPO,NR,DEFAULT,read,text,evidence,digest,rel,write
from metrics_check import metrics,compare

BASE=Path('26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability')
VISUAL_SOURCE='26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_source/phase_model.py'


def neural_config(c,seed,full,epochs,scheduler_horizon):
    return {'seed':seed,'optimizer':'AdamW','head_learning_rate':c['head_lr'],
        'backbone_learning_rate':c['backbone_lr'] if full else 0,'weight_decay':c['weight_decay'],
        'betas':DEFAULT,'epsilon':DEFAULT,'gradient_clipping':c['gradient_clip'],
        'microbatch_size':c['microbatch_actions'],'batch_size':c['effective_batch_actions'],
        'gradient_accumulation':c['effective_batch_actions'],'effective_batch_size':c['effective_batch_actions'],
        'precision':c['precision'],'scheduler':'cosine multiplier 1 to0.1',
        'scheduler_parameters':{'horizon':scheduler_horizon,'floor_multiplier':.1},
        'warmup':'none','backbone':'RT-DETR R18vd CNN only','feature_dimension':896,
        'hidden_dimensions':[128],'dropout':.1,'normalization':'T-only fixed feature moments; FrozenBN moments fixed',
        'trainable_layers':'all executed CNN convolutions and promoted normalization affine plus head' if full else 'head only; CNN cached',
        'max_configured_epochs':epochs,'augmentation':'none','workers':c['loader_workers'],
        'sampling':'16 original uniform action frames; deterministic per-epoch permutation',
        'initialization':'original pretrained CNN and freshly seeded head',
        'loss':'positive-class-weighted BCEWithLogits; T negative/positive ratio',
        'checkpoint_selection':'highest V AP; ties lower V weighted BCE then earliest',
        'selection_metric':'validation AP','threshold':.5}


def extract_long(audit):
    base=read(BASE/'26102026_configuration/PHASE1_CONFIG.json')
    revision=read(BASE/'26102026_c_only_20epoch_revision_01/26102026_configuration/PHASE1_C_ONLY_CONFIG.json')
    plan=read(BASE/'26102026_evidence/PHASE1_FIT_PLAN.json')
    comparison=BASE/'26102026_bestfit_100epoch_frozen_vs_full_cnn'
    comp=read(comparison/'26102026_configuration/PHASE1_COMPARISON_CONFIG.json')
    roots=[(BASE/'26102026_execution/26102026_main_run_01',False),(comparison/'26102026_execution',True)]
    pooled20=[];pooled20sources=[]
    for parent,is100 in roots:
        for done in sorted((REPO/parent).glob('*/PHASE1_FIT_COMPLETE.json')):
            info=read(done);folder=done.parent
            full=info['arm']=='C_full_finetuned16';seed=info['seed'];job=plan[info['job_index']]
            horizon=100 if is100 else 50
            epochs=100 if is100 else 20 if full else base['max_epochs']
            conf=neural_config(comp if is100 else base,seed,full,epochs,horizon)
            conf.update(executed_epochs=info['executed_epochs'],selected_epoch=info['best']['epoch'],
                outer_fold=job['outer_fold_original'],inner_fold=job['role'],
                split_identifier=str(BASE/'26102026_evidence/PHASE1_FIT_PLAN.json'),
                early_stopping=False if is100 or full else True,
                early_stopping_patience='disabled' if is100 or full else base['patience_epochs'],
                optimizer_updates=sum(row['optimizer_updates'] for row in info['history']))
            gradient_path=folder/'PHASE1_FIRST_EPOCH_GRADIENT_UPDATES.json'
            gradient=read(gradient_path)
            if 'head_parameters' in gradient:
                cnn_count=gradient['CNN_parameters'] if full else 11190112
                conf.update(trainable_parameters=gradient['head_parameters']+(cnn_count if full else 0),
                            frozen_parameters=0 if full else cnn_count,
                            total_parameters=gradient['head_parameters']+cnn_count,
                            loaded_fit_module_parameters=gradient['head_parameters']+gradient['CNN_parameters'],
                            parameter_count_scope='full CNN-feature-plus-head pipeline; frozen CNN can be cached outside fit module')
            prediction=folder/'PHASE1_PREDICTIONS.json';selected=folder/'PHASE1_BEST_MODEL.pt'
            assert digest(prediction)==info['predictions_sha256']
            assert digest(selected)==info['selected_model_sha256']
            assert [row['epoch'] for row in info['history']]==list(range(1,info['executed_epochs']+1))
            stage='HELD-OUT' if is100 or job['role']=='outer_assessment' else 'INNER-OOF ASSESSMENT'
            run_id=rel(folder);experiment='REASSEMBLE_100E_SINGLE_FIT' if is100 else 'REASSEMBLE_PHASE1_C20' if full else 'REASSEMBLE_PHASE1_ORIGINAL_B'
            cfgsource=comparison/'26102026_configuration/PHASE1_COMPARISON_CONFIG.json' if is100 else BASE/'26102026_c_only_20epoch_revision_01/26102026_configuration/PHASE1_C_ONLY_CONFIG.json' if full else BASE/'26102026_configuration/PHASE1_CONFIG.json'
            audit.run('REASSEMBLE',experiment,info['arm'],run_id,cfgsource,conf,
                training_status='COMPLETE',evidence_status='VERIFIED',
                checkpoint_path=rel(selected),last_checkpoint_pointer=rel(folder/'PHASE1_LATEST_EPOCH.json'),
                history_source=rel(done),entry_point=rel(comparison/'26102026_source/compare100_train.py') if is100 else rel(BASE/'26102026_c_only_20epoch_revision_01/26102026_source/c20_train.py') if full else rel(BASE/'26102026_source/phase_training.py'),
                source_revision='source hashes in execution provenance',configuration_function='phase_model.make_optimizer/make_scheduler; c20 epoch cap or compare100 horizon override',
                configuration_sources=[str(BASE/'26102026_configuration/PHASE1_CONFIG.json'),str(cfgsource),rel(done)],
                train_N=len(info.get('T_sample_ids',[])),validation_N=len(info.get('V_sample_ids',[])),
                calibration_N=len(info.get('C_sample_ids',[])),assessment_N=len(info.get('prediction_sample_ids',[])),
                duration_training_hours=info['training_seconds']/3600,
                duration_inference_calibration_hours=info['inference_calibration_seconds']/3600,
                actual_scope=stage)
            predictions=read(prediction)
            if isinstance(predictions,dict):
                if 'predictions' in predictions: predictions=predictions['predictions']
                elif 'rows' in predictions: predictions=predictions['rows']
            if isinstance(predictions,list) and predictions:
                keys=predictions[0].keys()
                pk=next((k for k in ['probability','p','p_visual'] if k in keys),None)
                yk=next((k for k in ['failure','label','y','target'] if k in keys),None)
                if pk and yk:
                    y=[r[yk] for r in predictions];p=[r[pk] for r in predictions]
                    report=metrics(y,p)
                    audit.result('REASSEMBLE',experiment,info['arm'],report,prediction,
                        stage=stage,seed=seed,fold=job['outer_fold_original'],run_id=run_id,
                        held_out_N=len(y),positive_count=sum(y),negative_count=len(y)-sum(y),
                        train_N=len(info.get('T_sample_ids',[])),validation_N=len(info.get('V_sample_ids',[])),
                        checkpoint_path=rel(selected),prediction_file=rel(prediction),
                        evaluation_script='audit_utilities/metrics_check.py (saved probabilities only)',
                        threshold=.5,metric_definition='average precision; positive=native failure')
                    if not is100 and full and job['role']=='outer_assessment':
                        pooled20.extend(predictions);pooled20sources.append(rel(prediction))
            for row in info['history']:
                h={'dataset':'REASSEMBLE','experiment_id':experiment,'run_id':run_id,'model':info['arm'],
                   'seed':seed,'outer_fold':job['outer_fold_original'],'role':job['role'],
                   'history_source':rel(done),**{k:v for k,v in row.items() if k!='host_resources'}}
                audit.histories.append(h)
                audit.result('REASSEMBLE',experiment,info['arm'],
                    {'training_loss':row['training_loss']},done,stage='TRAINING',seed=seed,fold=job['outer_fold_original'],run_id=run_id,epoch=row['epoch'])
                audit.result('REASSEMBLE',experiment,info['arm'],
                    {'validation_AP':row['validation_AP'],'validation_AUROC':row['validation_AUROC'],'validation_loss':row['validation_loss']},
                    done,stage='VALIDATION',seed=seed,fold=job['outer_fold_original'],run_id=run_id,epoch=row['epoch'])
            audit.checks.append({'check':'long_run_identity_history_and_hashes','run_id':run_id,
                                 'epochs':info['executed_epochs'],'selected_epoch':info['best']['epoch'],'passed':True})
    if len(pooled20sources)==5:
        assert len(pooled20)==4530 and len({r['sample_id'] for r in pooled20})==4530
        labels=[r['failure'] for r in pooled20];probabilities=[r['p_visual'] for r in pooled20]
        score=metrics(labels,probabilities)
        audit.result('REASSEMBLE','REASSEMBLE_PHASE1_C20','C_full_finetuned16',score,
                     BASE/'26102026_c_only_20epoch_revision_01/26102026_execution/PHASE1_C_ONLY_COMPLETED_INDEX.json',
                     stage='HELD-OUT POOLED',seed=42,fold='pooled5',held_out_N=4530,
                     positive_count=sum(labels),negative_count=4530-sum(labels),threshold=.5,
                     prediction_file=';'.join(pooled20sources),evaluation_script='audit_utilities/metrics_check.py',
                     metric_origin='AUDIT_RECOMPUTED_FROM_EXISTING_PREDICTIONS',
                     bootstrap_interval='NOT AVAILABLE — no new interval calculated by this audit')
        write(OUT/'provenance/C20_POOLED_METRIC_RECOMPUTATION.json',
              {'source_predictions':pooled20sources,'actions':4530,'failures':sum(labels),'metrics':score,
               'seed':42,'folds':5,'new_model_fitting':False,'new_fusion_fitting':False})
    status=read(BASE/'26102026_c_only_20epoch_revision_01/26102026_execution/PHASE1_C_ONLY_STATUS.json')
    stop=read(BASE/'26102026_c_only_20epoch_revision_01/02112026_stop_after25fits_01/STOP_AFTER_25_COMPLETE.json')
    write(OUT/'provenance/REASSEMBLE_CURRENT_STATUS.json',{'status':status,'stop_receipt':stop})


def extract_original(audit):
    configpath=Path('configs/reassemble/section1.json');c=read(configpath)
    root=Path(c['run_dir']);splits=read(root/'nested_splits.json')
    for summary in sorted((REPO/root/'predictions').glob('*_perm??.json')):
        info=read(summary);kind=info.get('model');permutation=info.get('permutation',0)
        if kind is None:continue
        audit.result('REASSEMBLE','SECTION1',kind,info,summary,stage='HELD-OUT POOLED' if permutation==0 else 'PERMUTATION CONTROL',
                     seed=c['seed'],fold='pooled five outer folds',held_out_N=4530,
                     positive_count=509,negative_count=4021,
                     prediction_file=rel(summary.with_suffix('.npz')),evaluation_script='src/reassemble/section1_models.py::evaluate_model',
                     prevalence=509/4530,permutation=permutation)
        for fold in info.get('folds',[]):
            outer=fold['fold'];selected=fold.get('selected',NR)
            parts=[('INNER',r['fold'],r.get('training',{})) for r in fold.get('inner',[])]
            if 'refit' in fold:parts.append(('OUTER',None,fold['refit']))
            for role,inner,training in parts:
                neural=kind in ['rtdetr','patchtst']
                cfg=c['sensor' if kind=='patchtst' else 'visual']
                baseconf={'seed':training.get('seed',c['seed']+100*outer+(99 if inner is None else inner)),
                    'outer_fold':outer,'inner_fold':inner if inner is not None else 'OUTER REFIT',
                    'split_identifier':c['splits'],'feature_dimension':896 if kind=='rtdetr' else 220 if kind=='sensor_statistics' else 22 if kind=='patchtst' else 4,
                    'selection_metric':'mean inner AP','threshold':'training OOF balanced-accuracy selection',
                    'normalization':'fit-local Standardizer','class_weighting':'balanced or T negative/positive ratio',
                    'initialization':'pretrained CNN features, fresh head' if kind=='rtdetr' else 'random initialization' if neural else 'new logistic fit',
                    'precision':'float32','augmentation':'none; circular label shift only for permutation controls'}
                if neural:
                    executed=len(training.get('loss_by_epoch',[]))
                    baseconf.update(optimizer='AdamW',learning_rate=cfg['learning_rate'],weight_decay=cfg['weight_decay'],
                        batch_size=cfg['batch_size'],effective_batch_size=cfg['batch_size'],gradient_clipping=1.,
                        max_configured_epochs=max(cfg['epochs']),executed_epochs=executed,selected_epoch=selected,
                        hidden_dimensions=[128],dropout=.1,early_stopping=False,
                        trainable_parameters=training.get('parameters',NR),betas=DEFAULT,epsilon=DEFAULT,
                        checkpoint_selection='mean-inner-AP selected shared epoch; no early stopping',
                        trainable_layers='visual head only' if kind=='rtdetr' else 'PatchTST and head',
                        backbone='frozen RT-DETR R18vd CNN only' if kind=='rtdetr' else 'PatchTST',
                        scheduler='none')
                else:
                    baseconf.update(C=selected if role=='OUTER' else 'three separate candidates:0.1,1,10',
                        solver=DEFAULT,penalty=DEFAULT,max_iter=2000,tolerance=DEFAULT,executed_epochs='NOT APPLICABLE')
                run_id=f'{rel(summary)}::{role}{inner}::outer{outer}'
                checkpoint=root/'checkpoints'/f'{kind}_fold{outer}.pt'
                audit.run('REASSEMBLE','SECTION1',kind,run_id,configpath,baseconf,
                          training_status='COMPLETE',history_source=rel(summary),
                          checkpoint_path=rel(checkpoint) if role=='OUTER' and permutation==0 and (REPO/checkpoint).exists() else NR,
                          entry_point='src/reassemble/section1_models.py',
                          configuration_function='evaluate_model/neural_fit/logistic_fit',
                          evidence_status='PARTIALLY VERIFIED',label_permutation=permutation,
                          fit_unit='one neural training trajectory' if neural else 'candidate grid bundle; subtrial count3 for inner fits',
                          source_revision=read(root/'training_implementation.json').get('implementation_git_commit',NR))
                for epoch,loss in enumerate(training.get('loss_by_epoch',[]),1):
                    audit.histories.append({'dataset':'REASSEMBLE','experiment_id':'SECTION1','run_id':run_id,
                        'model':kind,'seed':baseconf['seed'],'outer_fold':outer,'role':role,
                        'epoch':epoch,'training_loss':loss,'history_source':rel(summary)})
    resultpath=root/'assessment/results.json'
    if (REPO/resultpath).exists():
        extract_metric_tree(audit,read(resultpath),resultpath,'REASSEMBLE','SECTION1')
    f2=Path('runs/reassemble/20260927T175336Z-section1b')
    extract_metric_tree(audit,read(f2/'assessment/results.json'),f2/'assessment/results.json','REASSEMBLE','SECTION1B_F2')
    coeff=read(f2/'assessment/stacker_coefficients.json')
    for fold,row in enumerate(coeff):
        audit.run('REASSEMBLE','SECTION1B_F2','F2',f'SECTION1B_F2/outer{fold}',f2/'config.json',
            {'outer_fold':fold,'seed':0,'C':1.,'solver':'lbfgs','max_iter':2000,
             'class_weighting':None,'penalty':DEFAULT,'tolerance':DEFAULT,'threshold':row['threshold'],
             'feature_dimension':2,'trainable_parameters':3,'initialization':'new L2 logistic fit',
             'normalization':'none on calibrated probability inputs','executed_epochs':'NOT APPLICABLE'},
            training_status='COMPLETE',evidence_status='VERIFIED',checkpoint_path=rel(f2/'assessment/stacker_coefficients.json'),
            entry_point='src/reassemble/section1b.py',configuration_function='fit_stacker',
            fit_unit='one outer F2 model; calibration/meta-crossfit fits are separate nuisance steps')


def extract_metric_tree(audit,node,path,dataset,experiment,context=()):
    """Preserve all reported metrics and interval endpoints without flattening data roles."""
    if isinstance(node,dict):
        if 'estimate' in node and isinstance(node['estimate'],(float,int)):
            model=context[-2] if len(context)>1 else experiment
            metric=context[-1] if context else 'estimate'
            audit.result(dataset,experiment,model,
                {metric:node['estimate'],metric+'_lower95':node.get('lower_95',node.get('lower95')),
                 metric+'_upper95':node.get('upper_95',node.get('upper95'))},path,
                stage='PAIRED DIFFERENCE' if any('minus' in x or 'difference' in x for x in context) else 'HELD-OUT POOLED',
                fold='pooled',held_out_N=4530 if dataset=='REASSEMBLE' else NR,
                bootstrap_method='percentile paired recording-cluster',bootstrap_unit='recording',
                bootstrap_draws=2000,confidence_level=.95,metric_path='/'.join(context))
            return
        for key,value in node.items():
            if key in ['calibration_bins','draws','bootstrap_draws','predictions']:continue
            extract_metric_tree(audit,value,path,dataset,experiment,context+(str(key),))
    elif isinstance(node,list):
        for index,value in enumerate(node):
            extract_metric_tree(audit,value,path,dataset,experiment,context+(str(index),))


def extract_fusion100(audit):
    root=Path('experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison')
    source=root/'07_evaluation_results/ALL_MODEL_METRICS.json';data=read(source)
    if 'models' in data:data=data['models']
    for name,row in data.items():
        if not isinstance(row,dict) or 'AP' not in row:continue
        audit.result('REASSEMBLE','CNN100_STATIC_SENSOR_F2',name,row,source,stage='HELD-OUT',
            seed=42,fold=0,held_out_N=753,positive_count=77,negative_count=676,
            prediction_file=rel(root/'06_held_out_predictions/ALL_MODELS_IDENTICAL_OUTER_IDS.csv'),
            evaluation_script=rel(root/'src/evaluate.py'),threshold=.5,
            class_definition='native action failure',n_groups=26)
    for name in ['F2_FROZEN100','F2_FINETUNED100']:
        path=root/'05_fusion_models'/f'{name}.json';row=read(path)
        audit.run('REASSEMBLE','CNN100_STATIC_SENSOR_F2',name,name,path,
            {'seed':0,'C':1.,'class_weighting':None,'solver':'lbfgs','max_iter':2000,
             'threshold':row.get('threshold',row.get('native_threshold',NR)),
             'feature_dimension':2,'trainable_parameters':3,
             'normalization':'none; calibrated visual and canonical sensor probabilities',
             'executed_epochs':'NOT APPLICABLE','selection_metric':'fixed C; original meta-crossfit threshold rule'},
            training_status='COMPLETE',evidence_status='VERIFIED',checkpoint_path=rel(path),
            entry_point=rel(root/'src/evaluate.py'),configuration_function='original src/reassemble/section1b.py::fit_stacker',
            train_N=920,assessment_N=753,
            coverage_note='one held-out base-model bank, not complete four-fold nested100epoch OOF')
    for path in [root/'07_evaluation_results/PAIRED_RECORDING_BOOTSTRAP.json',
                 root/'09_reproducibility/FINAL_VALIDATION.json']:
        read(path)


def extract(audit):
    extract_long(audit)
    extract_original(audit)
    extract_fusion100(audit)
