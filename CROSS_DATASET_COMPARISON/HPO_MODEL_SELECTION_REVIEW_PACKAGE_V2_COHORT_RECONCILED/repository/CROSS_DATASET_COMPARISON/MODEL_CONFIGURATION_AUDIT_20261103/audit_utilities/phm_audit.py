"""Legacy PHM training evidence, separated from current native-failure research."""
from pathlib import Path
import json
import yaml

from audit_common import OUT,REPO,NR,DEFAULT,read,text,evidence,rel,csv_read,write
from historical_audit import config_values


def extract(audit):
    roots=[]
    for family in ['phm2026_patchtst_baseline','phm2026_rtdetr_detection',
                   'phm2026_rtdetr_regression','phm2026_rtdetr_multitask']:
        root=REPO/'runs'/family
        roots.extend(p for p in root.glob('*') if p.is_dir())
    for folder in sorted(roots):
        config=folder/'config/resolved_config.yaml';history=folder/'tables/training_history.csv'
        if not config.exists():continue
        resolved=yaml.safe_load(text(config));c=resolved.get('experiment_config',resolved)
        model=c.get('model',resolved.get('model',{}));train=c.get('training',resolved.get('training',{}))
        checkpoint=next(iter(sorted(folder.rglob('best*.pt'))),None)
        rows=csv_read(history) if history.exists() else []
        cfg={**config_values(train),'seed':c.get('seed',NR),'model_architecture_configuration':model,
             'training_configuration':train,'execution_overrides':resolved.get('execution',{}),
             'max_configured_epochs':train.get('maximum_epochs',train.get('max_epochs',NR)),
             'executed_epochs':len(rows) if rows else NR,
             'selection_metric':'validation loss or detector fitness; see saved selection/report',
             'split_identifier':'EXP-B train / EXP-A validation / EXP-F test',
             'target_definition':c.get('target',resolved.get('status','pseudo-target agreement; not native anomaly labels')),
             'initialization':'recorded pretrained or fresh PatchTST; see model config',
             'precision':'AMP' if train.get('amp') else NR}
        if 'finetune' in train:
            cfg.update(finetune_configuration=train['finetune'],warmup_configuration=train.get('warmup'),
                       smoke_configuration=train.get('smoke'),max_configured_epochs=train['finetune']['maximum_epochs'])
        selection=resolved.get('selection',{})
        cfg['selected_epoch']=selection.get('best_epoch',NR)
        if checkpoint:
            try:
                import torch
                obj=torch.load(checkpoint,map_location='cpu',weights_only=True)
                for key in ['epoch','best_epoch','selected_epoch']:
                    if key in obj:cfg['selected_epoch']=obj[key];break
                del obj
            except Exception:
                pass
        entry={'phm2026_patchtst_baseline':'scripts/phm2026/training/train_patchtst.py',
               'phm2026_rtdetr_detection':'scripts/phm2026/training/train_rtdetr_detector.py',
               'phm2026_rtdetr_regression':'scripts/phm2026/training/train_rtdetr_regression.py',
               'phm2026_rtdetr_multitask':'scripts/phm2026/training/train_rtdetr_multitask.py'}[folder.parent.name]
        audit.run('PHM2026',folder.parent.name,folder.parent.name,rel(folder),config,cfg,
            training_status='COMPLETE' if rows and checkpoint else 'PARTIAL',
            evidence_status='PARTIALLY VERIFIED',checkpoint_path=rel(checkpoint) if checkpoint else NR,
            history_source=rel(history) if history.exists() else NR,
            entry_point=entry,configuration_function='resolved_config.yaml + training_history.csv + safe checkpoint metadata',
            scientific_target_status='historical provisional image-derived damage regression/detection; not native failure classification')
        for index,row in enumerate(rows):
            audit.histories.append({'dataset':'PHM2026','experiment_id':folder.parent.name,'run_id':rel(folder),
                'model':folder.parent.name,'history_source':rel(history),**row})
    # Record implemented-but-unexecuted architectures independently of weights.
    for path in ['src/phm2026/fusion/modality_fusion.py','src/phm2026/fusion/late_fusion.py',
                 'scripts/phm2026/results/anomalydino_sweep.py']:
        text(path)
    print('PHM_TRAINING_DIRECTORIES',len(roots),flush=True)
