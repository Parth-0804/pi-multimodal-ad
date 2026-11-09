"""Recover nested original fusion, boundary heads and branch-bank fit records."""
from pathlib import Path
import re
import numpy as np

from audit_common import OUT,REPO,NR,DEFAULT,read,evidence,digest,rel,write
from primary_reassemble import extract_metric_tree


def sensor_controls(audit):
    base=read('configs/reassemble/section1.json')
    # Expand the known three-C inner grid bundles into their actual fitted trials.
    bundles=[r for r in audit.runs if r['experiment_id']=='SECTION1'
             and r['model'] in ['sensor_statistics','action_only']
             and r['effective_configuration']['C']=='three separate candidates:0.1,1,10']
    remove={r['run_id'] for r in bundles}
    audit.runs=[r for r in audit.runs if r['run_id'] not in remove]
    audit.parameters=[p for p in audit.parameters if p['run_id'] not in remove]
    for row in bundles:
        for value in base['logistic_C']:
            cfg={**row['effective_configuration'],'C':value,'seed':0,
                 'nominal_split_seed':base['seed']}
            audit.run('REASSEMBLE','SECTION1',row['model'],row['run_id']+f'::candidateC{value}',
                row['configuration_source'],cfg,training_status='COMPLETE',evidence_status='PARTIALLY VERIFIED',
                checkpoint_path='NOT RETAINED — inner grid candidate',entry_point='src/reassemble/section1_models.py',
                configuration_function='evaluate_model/logistic_fit',label_permutation=row['label_permutation'],
                fit_unit='one actual C-grid trial; execution corroborated by inner AP')
    root=Path('runs/reassemble/20260927T175336Z-section1b/sensor_controls/predictions')
    for path in sorted((REPO/root).glob('sensor_statistics_perm??.json')):
        obj=read(path);permutation=obj['permutation']
        audit.result('REASSEMBLE','SECTION1B_SENSOR_NULL_CONTROLS','sensor_statistics',obj,path,
            stage='OBSERVED REPRODUCTION' if permutation==0 else 'PERMUTATION CONTROL',
            seed=0,fold='pooled5',held_out_N=4530,positive_count=509,negative_count=4021,
            prediction_file=rel(path.with_suffix('.npz')),permutation=permutation)
        for fold in obj['folds']:
            trials=[('refit',fold['selected'])]+[(f'inner{part["fold"]}',value)
                    for part in fold['inner'] for value in base['logistic_C']]
            for role,value in trials:
                cfg={'seed':0,'outer_fold':fold['fold'],'inner_fold':role,'C':value,
                     'max_iter':2000,'class_weighting':'balanced','solver':DEFAULT,'penalty':DEFAULT,
                     'tolerance':DEFAULT,'feature_dimension':220,'executed_epochs':'NOT APPLICABLE',
                     'normalization':'fit-local Standardizer; selected inner-OOF sigmoid calibration',
                     'selection_metric':'mean inner AP across C0.1/1/10','nominal_split_seed':base['seed']}
                audit.run('REASSEMBLE','SECTION1B_SENSOR_NULL_CONTROLS','sensor_statistics',
                    rel(path)+f'::outer{fold["fold"]}::{role}::C{value}',path,cfg,
                    training_status='COMPLETE',evidence_status='PARTIALLY VERIFIED',
                    entry_point='src/reassemble/section1b.py',configuration_function='sensor_controls/evaluate_model/logistic_fit',
                    checkpoint_path='NOT RETAINED — null/reproduction control',label_permutation=permutation,
                    fit_unit='one actual logistic fitting trial, not an independent population')


def original_fusions(audit):
    root=Path('runs/reassemble/20260927T192852Z-section2');c=read(root/'config.json')
    for path in sorted((REPO/root/'fits').glob('*.json')):
        m=re.fullmatch(r'(F[3456])_outer(\d+)_(final|inner\d+)(?:_c(\d+))?_s(\d+)\.json',path.name)
        if not m:continue
        kind,fold,role,candidate,seedindex=m.groups();fold=int(fold);seedindex=int(seedindex)
        info=read(path);outer=read(root/'predictions'/f'outer{fold}.json')['models'][kind]
        settings=outer['settings'] if role=='final' else c['concat_configs' if kind=='F3' else 'gate_configs'][int(candidate)]
        cfg={'seed':info['seed'],'seed_family':c['seeds'][seedindex],'outer_fold':fold,'inner_fold':role,
            'optimizer':'AdamW','learning_rate':settings['lr'],'weight_decay':settings['weight_decay'],
            'batch_size':c['batch_size'],'gradient_clipping':1.,'betas':DEFAULT,'epsilon':DEFAULT,
            'hidden_dimensions':[settings['hidden']],'dropout':c['dropout'] if kind=='F3' else 'none',
            'max_configured_epochs':settings['epochs'],'executed_epochs':len(info['loss_by_epoch']),
            'selected_epoch':settings['epochs'],'early_stopping':False,
            'trainable_parameters':info['parameters'],'precision':'FP32',
            'selection_metric':'mean inner AP of three-seed mean probabilities',
            'candidate_index':outer['selected_config'] if role=='final' else int(candidate),
            'threshold':outer['threshold'] if role=='final' else 'selected later using training OOF',
            'class_weighting':'balanced BCE' if kind=='F3' else None,
            'normalization':'proper training subset feature/quality means/std; branch probabilities already calibrated'}
        checkpoint=path.with_suffix('.pt')
        audit.run('REASSEMBLE','SECTION2',kind,rel(path),root/'config.json',cfg,
            training_status='COMPLETE',evidence_status='VERIFIED',
            checkpoint_path=rel(checkpoint) if checkpoint.exists() else 'NOT RETAINED — inner candidate',
            history_source=rel(path),entry_point='src/reassemble/section2.py',
            configuration_function='cached_fit/train_outer / section2_models.fit_head',
            duration_training_hours=info['training_seconds']/3600,
            actual_scope='outer refit' if role=='final' else 'inner candidate fit')
        for epoch,loss in enumerate(info['loss_by_epoch'],1):
            audit.histories.append({'dataset':'REASSEMBLE','experiment_id':'SECTION2','run_id':rel(path),
                'model':kind,'seed':info['seed'],'outer_fold':fold,'role':role,'epoch':epoch,
                'training_loss':loss,'history_source':rel(path)})
    # Dropout checkpoints contain safe primitive/tensor-only training metadata.
    root=Path('runs/reassemble/20260927T204649Z-modality-dropout')
    if (REPO/root).exists():
        import torch
        spec=read('configs/reassemble/section3_corruptions.json')
        for path in sorted((REPO/root/'fits').glob('*.pt')):
            obj=torch.load(evidence(path,'study-owned tensor-only dropout checkpoint'),map_location='cpu',weights_only=True)
            settings=obj['settings'];m=re.search(r'outer(\d+)',path.name);fold=int(m[1]) if m else NR
            cfg={'seed':obj['seed'],'outer_fold':fold,'optimizer':'AdamW','learning_rate':settings['lr'],
                'weight_decay':settings['weight_decay'],'batch_size':128,'hidden_dimensions':[settings['hidden']],
                'max_configured_epochs':settings['epochs'],'executed_epochs':len(obj['loss_by_epoch']),
                'selected_epoch':settings['epochs'],'precision':'FP32','gradient_clipping':1.,
                'class_weighting':None,'augmentation':spec['dropout'],'betas':DEFAULT,'epsilon':DEFAULT,
                'normalization':'fit-local quality scaler; availability masks independent of labels'}
            audit.run('REASSEMBLE','MODALITY_DROPOUT','F6_dropout',rel(path),root/'config.json',cfg,
                training_status='COMPLETE',evidence_status='VERIFIED',checkpoint_path=rel(path),
                entry_point='src/reassemble/modality_dropout.py',configuration_function='fit_dropout',
                duration_training_hours=obj.get('training_seconds',0)/3600)
            del obj


def branch_banks(audit):
    root=Path('runs/reassemble/20260927T175336Z-section1b');base=read('configs/reassemble/section1.json')
    for path in sorted((REPO/root/'stacking').glob('outer*.json')):
        match=re.fullmatch(r'outer(\d+)(?:_inner(\d+))?\.json',path.name)
        if not match:continue
        fold=int(match[1]);inner=match[2];obj=read(path)
        branches=obj['refits'] if inner is None else obj['branches']
        for kind,branch in branches.items():
            fits=[('refit',branch['refit'])]+[(f'subinner{i}',v) for i,v in enumerate(branch['inner_fit'])]
            for role,info in fits:
                values=[branch['selected']] if role=='refit' or kind=='rtdetr' else base['logistic_C']
                for value in values:
                    cfg={'seed':info.get('seed',0),'outer_fold':fold,'inner_fold':inner if inner is not None else 'outer branch reconstruction',
                         'selection_metric':'mean subinner AP','threshold':branch['calibration']['threshold'],
                         'normalization':'fit-local Standardizer; sigmoid calibration on selected nested OOF',
                         'class_weighting':'balanced or T negative/positive ratio','feature_dimension':896 if kind=='rtdetr' else 220}
                    if kind=='rtdetr':
                        cfg.update(optimizer='AdamW',learning_rate=.001,weight_decay=.001,batch_size=128,
                            gradient_clipping=1.,max_configured_epochs=10,executed_epochs=len(info['loss_by_epoch']),
                            selected_epoch=branch['selected'],hidden_dimensions=[128],dropout=.1,
                            trainable_parameters=info['parameters'],precision='FP32',betas=DEFAULT,epsilon=DEFAULT,
                            trainable_layers='head only; original FP16-extracted CNN features')
                    else:cfg.update(C=value,max_iter=2000,solver=DEFAULT,penalty=DEFAULT,tolerance=DEFAULT,executed_epochs='NOT APPLICABLE')
                    runid=rel(path)+f'::{kind}::{role}::C{value}'
                    audit.run('REASSEMBLE','SECTION1B_NESTED_BRANCHES',kind,runid,path,cfg,
                        training_status='COMPLETE',evidence_status='PARTIALLY VERIFIED',
                        checkpoint_path='NOT RETAINED in original bank; saved probabilities and selected calibrator retained',
                        entry_point='src/reassemble/section1b.py',configuration_function='branch_fit/neural_fit/logistic_fit',
                        original_calibration=branch['calibration'],fit_unit='one actual base fit; source and nested logs, no saved weight state')


def boundary(audit):
    root=Path('runs/reassemble/additional_improvements_executed/20260929T162710Z/boundary_aware_visual')
    c=read(root/'config.json');base=read(c['section1_config'])
    for path in sorted((REPO/root/'fits').rglob('complete.json')):
        obj=read(path);sig=obj['signature'];kind=sig['variant'];history=obj['loss_by_epoch']
        for item in obj['files']:
            if str(item['path']).endswith('.pt'):assert digest(item['path'])==item['sha256']
        checkpoints=[item['path'] for item in obj['files'] if str(item['path']).endswith('.pt')]
        m=re.search(r'outer(\d+)',str(path));fold=int(m[1]) if m else NR
        cfg={'seed':sig['seed'],'outer_fold':fold,'optimizer':'AdamW','learning_rate':base['visual']['learning_rate'],
             'weight_decay':base['visual']['weight_decay'],'batch_size':128,'precision':'FP32',
             'max_configured_epochs':max(sig['candidates']),'executed_epochs':len(history),
             'selected_epoch':'shared epoch selected by mean inner AP; see branches/complete.json',
             'trainable_parameters':obj['parameters'],'gradient_clipping':1.,'feature_dimension':896,
             'hidden_dimensions':[64] if kind=='V5' else [128],'dropout':.1,
             'selection_metric':'mean inner AP across fixed5/10 or5/10/20 snapshots',
             'class_weighting':'T negative/positive ratio','normalization':'training segment-mean feature moments',
             'trainable_layers':'GRU or bin-pooling head only; CNN frozen',
             'initialization':'fresh seeded head','betas':DEFAULT,'epsilon':DEFAULT}
        audit.run('REASSEMBLE','BOUNDARY_AWARE_VISUAL',kind,rel(path),root/'config.json',cfg,
            training_status='COMPLETE',evidence_status='VERIFIED',checkpoint_path=';'.join(map(str,checkpoints)),
            train_N=len(sig['train']),assessment_N=len(sig['predict']),history_source=rel(path),
            entry_point='src/reassemble/boundary_visual/runner.py',configuration_function='training.fit/branch',
            duration_fit_wall_hours=obj['seconds']/3600)
        for epoch,loss in enumerate(history,1):
            audit.histories.append({'dataset':'REASSEMBLE','experiment_id':'BOUNDARY_AWARE_VISUAL','run_id':rel(path),
                'model':kind,'seed':sig['seed'],'outer_fold':fold,'epoch':epoch,'training_loss':loss,'history_source':rel(path)})


def json_results(audit):
    covered={r['metric_output_file'] for r in audit.results}
    roots=[REPO/'runs/reassemble',REPO/'00_experiments',REPO/'MILLING DATASET/runs']
    paths=[]
    for root in roots:
        paths.extend(root.rglob('results.json'));paths.extend(root.rglob('metrics.json'))
    def walk(obj,path,context=()):
        if isinstance(obj,dict):
            estimates={k:v['estimate'] for k,v in obj.items() if isinstance(v,dict) and isinstance(v.get('estimate'),(float,int))}
            numeric={k:v for k,v in obj.items() if k.lower() in ['ap','auprc','auroc','f1','macro_f1','precision','recall','brier','log_loss','ece','balanced_accuracy','failure_recall','failure_precision'] and isinstance(v,(int,float))}
            vals={**numeric,**estimates}
            if vals:
                model=obj.get('model',context[-1] if context else path.parent.name)
                stage='PAIRED DIFFERENCE' if any('minus' in x or 'difference' in x for x in context) else 'HELD-OUT — recorded aggregate; scope from metric_path'
                if any('train' in x for x in context):stage='TRAINING — recorded aggregate'
                if any('valid' in x or 'inner' in x for x in context):stage='VALIDATION/INNER — recorded aggregate'
                for k,v in obj.items():
                    if k in estimates:
                        for suffix,key in [('lower95','lower_95'),('upper95','upper_95')]:
                            if isinstance(v.get(key),(float,int)):vals[k+'_'+suffix]=v[key]
                audit.result('REASSEMBLE' if 'reassemble' in str(path) or '00_experiments' in str(path) else 'MSM_LEGACY',
                    '/'.join(Path(rel(path)).parts[:4]),str(model),vals,path,stage=stage,
                    metric_path='/'.join(context),bootstrap_interval='recorded endpoints when present; absent endpoints NOT AVAILABLE')
            for key,value in obj.items():
                if key in ['predictions','bootstrap_draws','draws','calibration_bins','history']:continue
                if isinstance(value,(dict,list)):walk(value,path,context+(str(key),))
        elif isinstance(obj,list):
            for i,value in enumerate(obj):
                if isinstance(value,(dict,list)):walk(value,path,context+(str(i),))
    for path in sorted(set(paths)):
        if rel(path) in covered or 'source_snapshot' in str(path) or 'original_inputs' in str(path):continue
        if path.stat().st_size>30*1024**2:continue
        walk(read(path),path)


def extract(audit):
    sensor_controls(audit)
    original_fusions(audit)
    branch_banks(audit)
    boundary(audit)
    json_results(audit)
    print('SUPPLEMENTARY_FITS_AND_JSON_RESULTS_COMPLETE',len(audit.runs),flush=True)
