"""Inventory historical fit receipts and losslessly extract aggregate metric tables."""
from pathlib import Path
import csv
import json
import re
import math
import collections
import numpy as np

from audit_common import OUT,REPO,NR,DEFAULT,read,evidence,digest,rel,csv_read,write
from discover import dataset

METRICS={'ap','auprc','auroc','f1','macro_f1','precision','recall','balanced_accuracy',
    'specificity','brier','log_loss','ece','ece10','ece15','accuracy','mae','rmse','mse',
    'r2','r_squared','ap_failure','ap_success','macro_ap','pearson_r','spearman_r',
    'train_loss','training_loss','validation_loss','val_loss','val_ap','validation_ap',
    'ap_mean','ap_seed_std','ap_min','ap_max','ap_difference','absolute_ap_degradation',
    'relative_ap_degradation_percent'}
REJECT={'source_snapshot','report_snapshots','INDEPENDENT_REVIEW_PACKAGE',
        'original_inputs','reference_only','reference_tables'}


def number(value):
    try:
        result=float(value)
        return result if math.isfinite(result) else None
    except (ValueError,TypeError):return None


def source_config(path):
    for parent in [path.parent,*path.parents]:
        if parent==REPO:break
        candidates=[parent/'config/resolved_config.json',parent/'resolved_config.json',
                    parent/'config.json',parent/'config/resolved.yaml',parent/'config/resolved_config.yaml']
        for candidate in candidates:
            if candidate.exists():return candidate
    return None


def config_values(c):
    if not isinstance(c,dict):return {}
    result={}
    aliases={'lr':'learning_rate','head_lr':'head_learning_rate','final_stage_lr':'backbone_learning_rate',
        'pretrained_lr':'backbone_learning_rate','backbone_lr':'backbone_learning_rate',
        'gradient_clip':'gradient_clipping','clip_grad_norm':'gradient_clipping',
        'effective_batch_segments':'effective_batch_size','microbatch_segments':'microbatch_size',
        'sensor_C':'C','max_epochs':'max_configured_epochs','epochs':'max_configured_epochs'}
    allowed={'seed','optimizer','learning_rate','head_learning_rate','backbone_learning_rate',
        'weight_decay','batch_size','precision','scheduler','dropout','workers','augmentation',
        'max_iter','threshold','C','penalty','solver','patience','early_stopping','hidden','d_model'}
    for k,v in c.items():
        if k in allowed or k in aliases:result[aliases.get(k,k)]=v
    return result


def extract_additional(audit):
    root=Path('runs/reassemble/additional_improvements_executed')
    configpath=Path('configs/reassemble/additional_improvements/execution.json');c=read(configpath)
    candidates=json.loads((OUT/'provenance/CHECKPOINT_CANDIDATE_PATHS.json').read_text())
    fitted=0
    for checkpoint in candidates:
        p=Path(checkpoint['path'])
        if not p.is_relative_to(root) or p.suffix!='.pt':continue
        meta=p.with_suffix('.json')
        if not (REPO/meta).exists():continue
        info=read(meta)
        if not isinstance(info,dict) or 'checkpoint' not in info or 'history' not in info:continue
        expected=info['checkpoint']
        if not isinstance(expected,dict) or 'sha256' not in expected:continue
        assert digest(p)==expected['sha256']
        kind=info.get('kind')
        if not kind:
            if 'V-FT' in p.parts:kind='V-FT_final_stage_temporal'
            else:
                kind=next((k for k in ['A-ADAPTIVE','A-CONSTANT','F6','F2'] if k in p.name),'NOT RECORDED')
        history=info['history'];seed=info.get('seed',NR)
        outer=re.search(r'outer(\d+)',str(p));fold=int(outer[1]) if outer else NR
        if kind.startswith('V-FT'):
            options=c['finetune'];source='src/reassemble/additional_improvements/finetune.py'
            cfg={'optimizer':'AdamW','head_learning_rate':options['head_lr'],
                 'backbone_learning_rate':options['pretrained_lr'],'weight_decay':options['weight_decay'],
                 'max_configured_epochs':options['max_epochs'],'early_stopping_patience':options['patience'],
                 'precision':'FP16 autocast CNN + FP32 parameters/head + GradScaler',
                 'trainable_layers':'last CNN spatial stage plus previously fitted TemporalHead; not full CNN',
                 'initialization':info.get('initial',NR),'feature_dimension':896,'hidden_dimensions':[128],
                 'trainable_parameters':NR}
        elif kind in ['V-MEAN','V-TEMP','V-NOPOS','S-6','S-LONG']:
            options=c['neural'];source='src/reassemble/additional_improvements/neural.py'
            cfg={'optimizer':'AdamW','learning_rate':options['lr'],'weight_decay':options['weight_decay'],
                 'max_configured_epochs':6 if kind=='S-6' else options['max_epochs'],
                 'early_stopping_patience':options['patience'],'precision':'float32',
                 'feature_dimension':22 if kind.startswith('S-') else 896,
                 'trainable_layers':'PatchTST and classifier' if kind.startswith('S-') else 'feature/temporal head only; frozen CNN',
                 'initialization':'fresh seeded neural parameters',
                 'trainable_parameters':info.get('parameters',NR)}
        else:
            options=c.get('adaptation',{});source='src/reassemble/additional_improvements/robust_fusion.py' if '04_corruption_training' in p.parts else 'src/reassemble/additional_improvements/anchored.py'
            cfg={'optimizer':'AdamW' if kind!='F2' else 'LogisticRegression',
                 'learning_rate':.003 if kind!='F2' else 'NOT APPLICABLE',
                 'weight_decay':.001 if kind!='F2' else 'NOT APPLICABLE',
                 'penalty_lambda':info.get('penalty',0.),'class_weighting':None,
                 'trainable_parameters':info.get('trainable_parameters',NR),
                 'max_configured_epochs':100 if kind!='F2' else 'NOT APPLICABLE',
                 'early_stopping_patience':12 if kind!='F2' else 'NOT APPLICABLE',
                 'precision':'float32','initialization':'frozen static F2 anchor with zero-initialized adjustment' if kind.startswith('A-') else 'new seeded fit'}
            if kind=='F2':cfg.update(C=1.,solver='lbfgs',max_iter=2000)
        executed=info.get('stopped_epoch',len(history))
        cfg.update(seed=seed,outer_fold=fold,inner_fold='refit' if 'refit' in p.name else 'nested inner; see metadata',
            selected_epoch=info.get('best_epoch',NR),executed_epochs=executed,
            microbatch_size=info.get('microbatch',NR),effective_batch_size=info.get('effective_batch',128),
            gradient_clipping=1.,betas=DEFAULT,epsilon=DEFAULT,
            class_weighting=cfg.get('class_weighting','T negative/positive ratio'),
            augmentation=info.get('augmented',False),
            normalization='proper training subset only; saved moments',
            selection_metric='inner AP; outer refit duration from training-side selection',
            checkpoint_selection='saved best inner epoch; fixed selected outer refit duration')
        run_id=rel(meta)
        audit.run('REASSEMBLE','ADDITIONAL_'+p.parts[3],kind,run_id,configpath,cfg,
            training_status='COMPLETE',evidence_status='VERIFIED',checkpoint_path=rel(p),
            prediction_file=info.get('predictions',{}).get('path',NR),history_source=rel(meta),
            train_N=len(info.get('train_rows',info.get('training_rows',[]))),
            assessment_N=len(info.get('assessment_rows',[])),entry_point=source,
            configuration_function='fit/_fit; executed metadata overrides selected durations',
            duration_fit_wall_hours=info.get('seconds',0)/3600,
            fit_unit='reconstruction replay' if 'selected_checkpoint_replay' in str(p) else 'one actual fit')
        for row in history:
            if isinstance(row,dict):
                audit.histories.append({'dataset':'REASSEMBLE','experiment_id':'ADDITIONAL_'+p.parts[3],
                    'run_id':run_id,'model':kind,'seed':seed,'outer_fold':fold,
                    'history_source':rel(meta),**row})
        fitted+=1
    print('ADDITIONAL_HISTORICAL_FITS',fitted,flush=True)


def extract_legacy_receipts(audit):
    roots=[Path('00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning'),
           Path('00_experiments/frozen32_vs_finetuned32_fusion_diagnosis/results'),
           Path('00_experiments/rt_detr_encoder_comparison/results/run_01')]
    for root in roots:
        count=0
        for done in sorted((REPO/root).rglob('complete.json')):
            if any(x in REJECT for x in done.parts):continue
            item=read(done)
            if not isinstance(item,dict) or 'fit_id' not in item:continue
            reused=item.get('status')=='REUSED' or item.get('reused',False)
            cfgpath=source_config(done)
            raw=read(cfgpath) if cfgpath and cfgpath.suffix=='.json' else {}
            cfg=config_values(raw)
            condition=item.get('condition',next((name for name in done.parts if name in
                ['cnn_only','cnn_plus_encoder','sensor_reference','frozen_16_frames','frozen_32_frames',
                 'fine_tuned_16_frames','fine_tuned_32_frames','frozen32_two_epochs','finetuned32_two_epochs']),NR))
            executed=item.get('epochs_complete',item.get('epochs',NR))
            if executed==NR and condition=='sensor_reference':executed='NOT APPLICABLE'
            cfg.update(seed=item.get('training_role_seed',item.get('seed',NR)),
                seed_family=item.get('seed_family',NR),executed_epochs=executed,
                selected_epoch=executed,optimizer_updates=item.get('optimizer_updates',item.get('updates',NR)),
                feature_dimension=item.get('dimension',896 if condition!='sensor_reference' else 220),
                trainable_parameters=item.get('head_parameters',NR),
                checkpoint_selection='fixed final epoch; separate C calibration',
                augmentation='none',precision=raw.get('precision','float32'),
                actual_final_stage_trainable=item.get('final_stage_trainable',False))
            if condition!='sensor_reference':
                cfg.update(optimizer='AdamW',head_learning_rate=raw.get('head_lr',.001),
                           weight_decay=raw.get('weight_decay',.001),hidden_dimensions=[128],dropout=.1,
                           trainable_layers='last CNN stage and head' if 'fine' in condition else 'head only',
                           early_stopping=False,betas=DEFAULT,epsilon=DEFAULT)
            else:cfg.update(C=raw.get('sensor_C',1.),solver='lbfgs',max_iter=2000,
                            class_weighting='balanced',normalization='G-only standardizer; C-only sigmoid calibration')
            checkpoint=item.get('model_reference',NR)
            if checkpoint==NR:
                for name in ['model.pt','model_and_calibrator.json']:
                    if (done.parent/name).exists():checkpoint=rel(done.parent/name);break
            audit.run('REASSEMBLE',str(root),condition,rel(done.parent),cfgpath or done,cfg,
                training_status='REUSED' if reused else 'COMPLETE',
                evidence_status='PARTIALLY VERIFIED',checkpoint_path=checkpoint,
                history_source=rel(done.parent/'learning_curve.csv') if (done.parent/'learning_curve.csv').exists() else NR,
                entry_point=str(root).split('/results')[0]+'/run_experiment.py',
                configuration_function='saved complete.json + resolved config + executing code',
                original_fit_id=item['fit_id'],reused_existing_fit=reused,
                fit_unit='reference/reuse, not another training run' if reused else 'one fit',
                training_wall_seconds=item.get('training_wall_seconds',item.get('training_seconds',NR)))
            curve=done.parent/'learning_curve.csv'
            if curve.exists():
                for row in csv_read(curve):
                    audit.histories.append({'dataset':'REASSEMBLE','experiment_id':str(root),
                        'run_id':rel(done.parent),'model':condition,'history_source':rel(curve),**row})
            count+=1
        print('LEGACY_RECEIPTS',str(root),count,flush=True)


def extract_metric_tables(audit):
    inventory=csv_read(OUT/'09_reviewer_handoff/REPOSITORY_ARTIFACT_INVENTORY.csv')
    seen={};nfiles=0
    permitted=('runs/','00_experiments/','parth_ws_bootstrap/','MILLING DATASET/','artifacts/','CROSS_DATASET_COMPARISON/')
    for item in inventory:
        name=item['path'];p=Path(name)
        if not name.startswith(permitted) or not name.endswith('.csv'):continue
        if any(x in REJECT for x in p.parts) or '.writing' in name:continue
        low=name.lower()
        if any(x in low for x in ['predictions','cohort','membership','manifest','feature','bootstrap_draw','frame_','channel_']):continue
        if not any(x in low for x in ['metric','result','comparison','assessment','evaluation','summary','robust','performance']):continue
        if int(item['bytes'])>30*1024**2:continue
        with (REPO/p).open(errors='replace') as stream:
            header=next(csv.reader(stream),[])
        if not any(k.lower() in METRICS for k in header) and not {'metric','value'}<=set(header):continue
        rows=csv_read(p);nfiles+=1
        for index,row in enumerate(rows):
            vals={k:number(v) for k,v in row.items() if k and k.lower() in METRICS}
            vals={k:v for k,v in vals.items() if v is not None}
            if {'metric','value'}<=set(row) and number(row['value']) is not None:
                vals[row['metric']]=number(row['value'])
            if not vals:continue
            role=str(row.get('role',row.get('scope',row.get('split','')))).lower()
            stage='TRAINING IN-SAMPLE' if 'train' in role else 'VALIDATION' if 'val' in role else 'INNER-OOF ASSESSMENT' if 'inner' in role or 'oof' in role else 'HELD-OUT' if 'test' in role or 'held' in role else 'NOT RECORDED — aggregate metric table'
            if 'permutation' in low:stage='PERMUTATION CONTROL'
            model=row.get('model',row.get('condition',row.get('variant',row.get('branch',NR))))
            ds=dataset(name)
            if ds=='OTHER_OR_SHARED' and ('phm' in low or any(x in low for x in ['anomalydino','patchtst'])):ds='PHM2026'
            if ds=='OTHER_OR_SHARED' and name.startswith(('00_experiments/','parth_ws_bootstrap/')):ds='REASSEMBLE'
            audit.result(ds,'/'.join(p.parts[:3]),model,vals,p,stage=stage,
                seed=row.get('seed',row.get('seed_family',NR)),fold=row.get('fold',row.get('outer_fold',NR)),
                held_out_N=row.get('n',row.get('N',row.get('examples',row.get('segments',NR)))),
                threshold=row.get('threshold',NR),csv_row=index+2,
                protocol=row.get('protocol',NR),corruption=row.get('corruption','clean or NOT RECORDED'),
                metric_origin='ORIGINAL_RECORDED_AGGREGATE_TABLE',
                source_role_note='Unknown roles are kept separate and never relabeled as held-out')
    print('HISTORICAL_METRIC_TABLES',nfiles,flush=True)


def extract(audit):
    extract_additional(audit)
    extract_legacy_receipts(audit)
    extract_metric_tables(audit)
