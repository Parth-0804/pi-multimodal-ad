"""Read-only recovery of small fitted states omitted by binary-neural adapters."""
from pathlib import Path
import json
import re
import yaml
from audit_common import Audit, OUT, REPO, NR, DEFAULT, read, text, evidence, digest, rel, write, flush_evidence


def main():
    state=read(OUT/'provenance/FINAL_AUDIT_STATE_02.json');a=Audit()
    for key in ['runs','results','histories','checks','parameters']:setattr(a,key,state[key])
    root=REPO/'runs/reassemble/additional_improvements_executed/20260928T000346Z/04_corruption_training'
    for p in sorted(root.rglob('*.joblib')):
        side=p.with_suffix('.json')
        if not side.exists():continue
        x=read(side);kind=x.get('kind');sensor=kind is None
        identity=x['output' if sensor else 'checkpoint'];assert digest(p)==identity['sha256']
        # Source-identified, hash-verified study-owned sklearn estimator only.
        if not sensor:
            import joblib
            estimator=joblib.load(evidence(p,'hash-verified study-owned small logistic estimator'))
            assert type(estimator).__module__=='sklearn.linear_model._logistic'
            params=estimator.get_params(deep=False)
        else:params={'C':x['selected_C'],'class_weight':'balanced','max_iter':2000,'random_state':0}
        m=re.search(r'outer(\d+)',p.name);fold=int(m[1]) if m else NR
        cfg={'seed':0,'nominal_split_seed':x.get('seed',20260927),'outer_fold':fold,
             'C':params['C'],'class_weighting':params.get('class_weight'),
             'solver':params.get('solver',DEFAULT),'penalty':params.get('penalty',DEFAULT),
             'tolerance':params.get('tol',DEFAULT),'max_iter':params['max_iter'],
             'executed_epochs':'NOT APPLICABLE','estimator_parameters':params,
             'selection_metric':'fixed F2 C1' if not sensor else 'selected historical C recovered; reconstruction fit',
             'feature_dimension':220 if sensor else 2,'normalization':x.get('scale_from','branch probabilities; quality normalization does not alter F2 p inputs'),
             'augmentation':'clean plus source-defined corruption variants' if x.get('augmented') else None}
        a.run('REASSEMBLE','ADDITIONAL_CORRUPTION_SMALL_STATES',
              'sensor_reconstruction' if sensor else 'F2_augmented' if x['augmented'] else 'F2_clean',rel(side),side,cfg,
              training_status='COMPLETE',evidence_status='VERIFIED',checkpoint_path=rel(p),
              train_N=len(x.get('train_rows',x.get('training_rows',[]))),assessment_N=len(x.get('test_rows',x.get('assessment_rows',[]))),
              duration_fit_wall_hours=x['seconds']/3600 if 'seconds' in x else NR,
              entry_point='src/reassemble/additional_improvements/'+('branch_banks.py' if sensor else 'robust_fusion.py'),
              configuration_function='recover_sensor_checkpoint' if sensor else 'fit',
              fit_unit='saved reconstruction replay, not an independent scientific replicate' if sensor else 'one fitted probability stacker')
    roots=[('LEGACY_VISUAL_ONE_DAY_F2','00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning','F2_stacker.json'),
           ('LEGACY_ENCODER_F2','00_experiments/rt_detr_encoder_comparison/results/run_01','F2_stacker.json'),
           ('LEGACY_FROZEN32_F2','00_experiments/frozen32_vs_finetuned32_fusion_diagnosis/results','model.json')]
    for exp,root,name in roots:
        for p in sorted((REPO/root).rglob(name)):
            if any(s in str(p) for s in ['original_inputs','source_snapshot']):continue
            x=read(p)
            if not isinstance(x.get('model'),dict) or 'coefficient' not in x['model']:continue
            model=x['model'];m=re.search(r'seed_(\d+)',str(p));seed=int(m[1]) if m else 42
            cfg={'seed':seed,'estimator_random_state':42,'C':model['C'],'class_weighting':'balanced' if model.get('balanced') else None,
                 'solver':DEFAULT,'penalty':DEFAULT,'tolerance':DEFAULT,'max_iter':2000,
                 'executed_epochs':'NOT APPLICABLE','feature_dimension':len(model['coefficient']),
                 'trainable_parameters':len(model['coefficient'])+1,'selection_metric':'fixed recipe, no F2 HPO',
                 'normalization':'no p transform or fused calibrator','original_fit_id':x['fit_id'],
                 'fitted_iterations':model.get('iterations',NR)}
            a.run('REASSEMBLE',exp,'F2',rel(p),p,cfg,training_status='REUSED' if x.get('reused') else 'COMPLETE',
                  evidence_status='VERIFIED',checkpoint_path=rel(p),
                  train_N=len(x.get('training_sample_ids',x.get('training_sample_keys',[]))),
                  entry_point=root.split('/results')[0]+'/run_experiment.py',
                  configuration_function='source/fusion.py::fit_logistic; verify experiment source snapshots',
                  duration_fit_wall_hours=x.get('fit_seconds',x.get('seconds',0))/3600)
    # Two superseded neural runs retain real checkpoints and histories.
    for folder in sorted((REPO/'runs/_superseded/phm2026_patchtst_baseline').glob('*')):
        cp=folder/'config/resolved_config.yaml';hp=folder/'tables/training_history.csv'
        if not cp.exists() or not hp.exists():continue
        from audit_common import csv_read
        c=yaml.safe_load(text(cp));tr=c.get('training',{});rows=csv_read(hp)
        a.run('PHM2026','PHM_SUPERSEDED_PATCHTST','PatchTST_regression',rel(folder),cp,
              {'seed':c.get('seed',NR),'max_configured_epochs':tr.get('max_epochs',NR),'executed_epochs':len(rows),
               'training_configuration':tr,'model_architecture_configuration':c.get('model',{}),
               'target_definition':c.get('target',NR),'selection_metric':'validation loss; historical superseded run'},
              training_status='COMPLETE',checkpoint_path=rel(folder/'best_patchtst.pt'),history_source=rel(hp),
              entry_point='scripts/phm2026/training/train_patchtst.py',evidence_status='PARTIALLY VERIFIED')
        for row in rows:a.histories.append({'dataset':'PHM2026','experiment_id':'PHM_SUPERSEDED_PATCHTST',
            'run_id':rel(folder),'model':'PatchTST_regression','history_source':rel(hp),**row})
    # Remove the mistakenly broad training-directory placeholder: this folder is a fusion study.
    a.runs=[r for r in a.runs if not (r['dataset']=='PHM2026' and r.get('training_status')=='PARTIAL' and '20260912T053924941825Z' in r['run_id'])]
    for p in sorted((REPO/'runs').rglob('ridge_selection.json')):
        x=read(p)
        for trial in x['trials']:
            cfg={'seed':'not stochastic; Ridge','alpha':trial['alpha'],'selection_metric':'validation EXP-A MAE',
                 'selected_alpha':x['selected_alpha'],'feature_definition':x['feature_definition'],
                 'solver':DEFAULT,'tolerance':DEFAULT,'executed_epochs':'NOT APPLICABLE',
                 'target_definition':'image-derived provisional damage regression, not native anomaly labels'}
            rid=rel(p)+f'::alpha{trial["alpha"]}'
            a.run('PHM2026','PHM_RIDGE_ALPHA_SEARCH','Ridge',rid,p,cfg,training_status='COMPLETE',
                  checkpoint_path='NOT RETAINED — trial metrics only',entry_point='src/phm2026/training/patchtst.py',
                  configuration_function='Ridge alpha grid; see SOURCE_FUNCTION_INDEX.csv',evidence_status='PARTIALLY VERIFIED')
            a.result('PHM2026','PHM_RIDGE_ALPHA_SEARCH','Ridge',{'MAE':trial['validation_mae']},p,stage='VALIDATION EXP-A',run_id=rid)
    for p in sorted((REPO/'runs').rglob('late_fusion_summary.json')):
        x=read(p);cpath=p.parent.parent/'config/resolved_config.yaml';c=yaml.safe_load(text(cpath));tr=c.get('training',{})
        for v in x['variants']:
            rid=rel(p)+'::'+v['variant'];cfg={'seed':c.get('seed',NR),'model_architecture_configuration':c.get('model',{}),
                'training_configuration':tr,'learning_rate':tr.get('learning_rate',NR),'weight_decay':tr.get('weight_decay',NR),
                'batch_size':tr.get('batch_size',NR),'max_configured_epochs':tr.get('max_epochs',NR),
                'executed_epochs':v['epochs_completed'],'selected_epoch':v['best_epoch'],
                'total_parameters':v['parameter_count'],'trainable_parameters':v['parameter_count'],
                'selection_metric':'lowest raw EXP-A MAE; EXP-F not consulted for within-study choice',
                'target_definition':x.get('target_definition_version',NR),'early_stopping_patience':tr.get('patience',NR)}
            a.run('PHM2026','PHM_SENSOR_LATE_FUSION',v['variant'],rid,cpath,cfg,
                  training_status='COMPLETE',checkpoint_path='NOT RETAINED — summary only',evidence_status='PARTIALLY VERIFIED',
                  entry_point='scripts/phm2026/training/train_late_fusion.py',configuration_function='late_fusion_summary.variants',
                  duration_training_hours=v['training_seconds']/3600)
            a.result('PHM2026','PHM_SENSOR_LATE_FUSION',v['variant'],v,p,stage='VALIDATION EXP-A',run_id=rid)
        a.result('PHM2026','PHM_SENSOR_LATE_FUSION',x['selected_variant'],x['test_result'],p,stage='HELD-OUT EXP-F',held_out_N=x['test_result']['sample_count'])
    # Evaluation-only DINO banks are not falsely counted as gradient-training fits.
    from audit_common import csv_read
    p=Path('docs/thesis/ANOMALYDINO_SWEEP.csv')
    for row in csv_read(p):
        vals={}
        for k,v in row.items():
            try:vals[k]=float(v)
            except (ValueError,TypeError):pass
        a.result('PHM2026','PHM_ANOMALYDINO_APPEARANCE_SWEEP',str(row.get('backbone','DINOv2'))+':'+str(row.get('bank',''))+':'+str(row.get('aggregation','')),vals,p,
                 stage='HUMAN AGREEMENT DEVELOPMENT — same38 calls reused',class_definition='appearance call; not native anomaly outcome')
    a.parameters=[]
    for r in a.runs:
        for k,v in r['effective_configuration'].items():
            a.parameters.append({'run_id':r['run_id'],'dataset':r['dataset'],'model':r['model'],'parameter':k,
                'effective_value':v,'source_file':r['configuration_source'],'source_function_or_key':r.get('configuration_function',NR),
                'additional_checkpoint_source':r.get('last_checkpoint_path',r.get('checkpoint_path',NR)),
                'status':'NOT RECORDED' if v==NR else 'PARTIALLY VERIFIED' if v==DEFAULT else 'VERIFIED'})
    assert len({r['run_id'] for r in a.runs})==len(a.runs)
    a.save();flush_evidence('LAST_FIT_EVIDENCE_LEDGER.json')
    write(OUT/'provenance/FINAL_AUDIT_STATE_03.json',{k:getattr(a,k) for k in ['runs','results','histories','checks','parameters']})

if __name__=='__main__':main()
