"""Finish provenance, inspect split roles, and enumerate source-backed legacy evidence."""
from pathlib import Path
import ast
import collections
import datetime as dt
import itertools
import json
import re
import subprocess
import importlib.metadata
from audit_common import Audit,OUT,REPO,NR,DEFAULT,read,text,evidence,digest,rel,write,csv_read,csv_write,flush_evidence


def main():
    state=read(OUT/'provenance/FINAL_AUDIT_STATE_03.json');a=Audit()
    for key in ['runs','results','histories','checks','parameters']:setattr(a,key,state[key])
    # Preserve official validation, rather than falsely calling it inner-OOF.
    corrected=0
    for r in a.results:
        if r['dataset']=='HANDOVER' and r['evaluation_scope']=='INNER-OOF ASSESSMENT':
            r['evaluation_scope']='VALIDATION OFFICIAL';corrected+=1
    for r in a.runs:
        if r['model']=='Ridge':r['entry_point']='scripts/phm2026/training/train_patchtst.py';r['configuration_function']='src/phm2026/models/patchtst/regression.py::ridge_predictions'
        if r.get('entry_point')=='00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/run_experiment.py':
            r['entry_point']='00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/source/run_study.py'
    # Completed aggregate output corroborates source control flow, but not per-fit epochs/states.
    p=Path('docs/thesis/SQ2_SQ3_RESULTS.json');x=read(p)
    basecfg={'optimizer':'AdamW','learning_rate':.001,'weight_decay':.0001,'batch_size':4,
             'max_configured_epochs':80,'executed_epochs':NR,'selected_epoch':NR,
             'early_stopping':True,'early_stopping_patience':10,'minimum_improvement':1e-8,
             'loss':'training-target-standardized SmoothL1','selection_metric':'validation SmoothL1',
             'betas':DEFAULT,'epsilon':DEFAULT,'precision':'FP32','feature_dimension':72,
             'model_architecture_configuration':{'patch_length':16,'stride':8,'d_model':32,'heads':4,'layers':2,'FF':64,'dropout':.1,'head_hidden':64},
             'target_definition':'historical provisional image-derived damage, v3 claimed in source',
             'normalization':'ONE fixed EXP-B normalizer before LOEO; violates fold-local scope when B is validation/held-out'}
    variants=[(arm,'clean',s) for arm in x['arms'] for s in [1,2,3]]
    variants += [(key.split('|')[0],key.split('|')[1],s) for key in x['robustness'] for s in [1,2,3]]
    variants += [(next(iter(x['arms'])),'redundant_constant_reference',1)]
    for arm,condition,seed in variants:
        for held,train in {'EXP-A':'EXP-F','EXP-B':'EXP-F','EXP-F':'EXP-B'}.items():
            a.run('PHM2026','PHM_SQ2_SQ3_AGGREGATE',arm,rel(p)+f'::{arm}::{condition}::seed{seed}::{held}',
                  'scripts/phm2026/results/sq2_sq3_fusion.py',{**basecfg,'seed':seed,'outer_fold':held,'augmentation':'none; '+condition+' applied after fitting',
                    'split_identifier':f'train{train}, validate third experiment, assess{held}'},
                  training_status='COMPLETE',evidence_status='PARTIALLY VERIFIED',checkpoint_path='NOT RETAINED — aggregate evidence only',
                  entry_point='scripts/phm2026/results/sq2_sq3_fusion.py',configuration_function='main/evaluate/train_fold',
                  fit_unit='SOURCE_CONTROL_FLOW_INFERRED: completed aggregate plus current source, not an individual receipt')
    for arm,v in x['arms'].items():
        for i,mae in enumerate(v['per_seed'],1):a.result('PHM2026','PHM_SQ2_SQ3_AGGREGATE',arm,{'MAE':mae},p,stage='LOEO HELD-OUT — preprocessing limitation',seed=i,fold='pooled3',held_out_N=20)
        a.result('PHM2026','PHM_SQ2_SQ3_AGGREGATE',arm,{k:v for k,v in v.items() if isinstance(v,(int,float))},p,stage='LOEO HELD-OUT SEED SUMMARY — preprocessing limitation',bootstrap_method='run resampling after mean error across seeds',bootstrap_draws=10000,confidence_level=.95,bootstrap_unit='run')
    for key,v in x['robustness'].items():a.result('PHM2026','PHM_SQ2_SQ3_AGGREGATE',key.split('|')[0],v,p,stage='LOEO ROBUSTNESS — preprocessing limitation',corruption=key.split('|')[1])
    for v in x['pairwise']:a.result('PHM2026','PHM_SQ2_SQ3_AGGREGATE',v['a']+' minus '+v['b'],v,p,stage='PAIRED DIFFERENCE',bootstrap_method='run paired percentile',bootstrap_draws=10000,bootstrap_unit='run',confidence_level=.95)
    splits=[]
    # Phase1 sample and recording separation from executed plan, not folder names.
    from primary_reassemble import BASE
    jobs=read(BASE/'26102026_evidence/PHASE1_FIT_PLAN.json')
    for j in jobs:
        roles={'TRAINING':set(j['training']),'VALIDATION':set(j['validation']),'CALIBRATION':set(j['C']),'ASSESSMENT':set(j['predict'])}
        disjoint=all(not v&w for v,w in itertools.combinations(roles.values(),2));assert disjoint
        assert set(j['training'])|set(j['validation'])==set(j['G'])
        assert not set(j['G_recordings'])&set(j['C_recordings'])
        assert not (set(j['G_recordings'])|set(j['C_recordings']))&set(j['prediction_recordings'])
        splits.append({'dataset':'REASSEMBLE','split_id':j['job_index'],'sample_roles_pairwise_disjoint':True,'recording_assessment_disjoint':True,'limitation':'T/V IDs disjoint; group separation follows saved training/validation construction, source independently indexed','source':rel(BASE/'26102026_evidence/PHASE1_FIT_PLAN.json')})
    p=next((REPO/'VIFAILBACK/04_evaluation_splits').rglob('fit_partitions.json'));jobs=read(p)
    for j in jobs:
        assert all(not set(v)&set(w) for v,w in itertools.combinations(j['ids'].values(),2))
        assert all(not set(v)&set(w) for v,w in itertools.combinations(j['groups'].values(),2))
        splits.append({'dataset':'VIFAILBACK','split_id':j['id'],'sample_roles_pairwise_disjoint':True,'task_roles_pairwise_disjoint':True,'source':rel(p)})
    for outer in range(3):
        js=[j for j in jobs if j['outer']==outer];final=next(j for j in js if j['inner']==-1)
        oof=[eid for j in js if j['inner']>=0 for eid in j['ids']['A']]
        assert len(oof)==len(set(oof));assert set(oof)==set(final['ids']['T']+final['ids']['V']+final['ids']['C']);assert not set(oof)&set(final['ids']['A'])
    # Per-sample predictions joined to immutable final manifests: all roles and corruptions.
    import pandas as pd
    for ds,root in [('MSM',Path('MSM')),('HANDOVER',Path('HANDOVER/experiments/common_support_v2'))]:
        manifest=csv_read(root/'03_processed_model_inputs/final_sample_manifest.csv');lookup={r['sample_id']:r for r in manifest};assert len(lookup)==len(manifest)
        expected=digest(root/'03_processed_model_inputs/final_sample_manifest.csv');cfg=read(root/'04_experiment_protocol/experiment_config.json');assert expected==cfg['sample_manifest_sha256']
        complete=read(root/'06_evaluation_results/P_EVALUATION_COMPLETE.json')
        for case in complete['cases']:
            frame=pd.read_csv(evidence(case['predictions'],'prediction/label identity join'),compression='gzip',usecols=['sample_id','target','role','corruption','model'])
            assert all(s in lookup for s in frame.sample_id.unique())
            expected_labels=frame.sample_id.map(lambda s:int(lookup[s]['target']));assert (expected_labels.to_numpy()==frame.target.to_numpy()).all()
            clean=frame.loc[frame.corruption=='clean'];part={role:set(part.sample_id) for role,part in clean.groupby('role')}
            assert all(not v&w for v,w in itertools.combinations(part.values(),2))
            splits.append({'dataset':ds,'split_id':case['case_id'],'sample_roles_pairwise_disjoint':True,'prediction_native_labels_match':True,'rows_checked':len(frame),'participant_disjoint_verified':'NO — native identifiers absent' if ds=='HANDOVER' else 'NOT APPLICABLE','source':case['predictions']})
    csv_write(OUT/'07_scientific_validity/SPLIT_AND_LABEL_VERIFICATION.csv',splits)
    # Enumerate actual source symbols for every executed entry and architecture implementation.
    paths=set()
    for r in a.runs:
        for key in ['entry_point','configuration_source']:
            val=r.get(key,'').split(' --')[0]
            if val.endswith('.py') and (REPO/val).is_file():paths.add(REPO/val)
    for root in ['src/reassemble','src/phm2026','VIFAILBACK/src','CROSS_DATASET_COMPARISON/src','MSM/src','HANDOVER/src','scripts/phm2026']:
        paths.update((REPO/root).rglob('*.py'))
    symbols=[]
    for p in sorted(paths):
        try:tree=ast.parse(text(p))
        except SyntaxError:continue
        for node in ast.walk(tree):
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                symbols.append({'path':rel(p),'sha256':digest(p),'kind':type(node).__name__,'symbol':node.name,'line':node.lineno,'end_line':node.end_lineno})
    csv_write(OUT/'02_model_architecture/SOURCE_FUNCTION_INDEX.csv',symbols)
    # Read-only gate recheck; do not call any function capable of loading/running a model.
    old=read('CROSS_DATASET_COMPARISON/provenance/R_source_gate_after_P.json');folder=REPO/old['canonical_folder'];receipt=read(folder/'PHASE1_FIT_COMPLETE.json')
    gate={'historical_gate':old,'canonical_receipt_exists_now':True,'executed_epochs_now':receipt['executed_epochs'],
          'selected_checkpoint_sha_matches':digest(folder/'PHASE1_BEST_MODEL.pt')==receipt['selected_model_sha256'],
          'remaining_MSM_HANDOVER_barrier':'validated_source rejects executed_epochs<25; current20',
          'remaining_VIFAILBACK_barrier':'resources.gpu_state requires75-fit completion marker; approved cap25',
          'transfer_fitting_performed_by_audit':False}
    write(OUT/'provenance/TRANSFER_GATE_RECHECK.json',gate)
    # Keep exact current dependency versions without touching environments.
    versions={name:importlib.metadata.version(name) for name in ['torch','torchvision','transformers','numpy','pandas','scikit-learn','scipy','matplotlib','joblib','pytest']}
    write(OUT/'provenance/SOFTWARE_VERSIONS.json',versions)
    a.parameters=[]
    for r in a.runs:
        for k,v in r['effective_configuration'].items():
            a.parameters.append({'run_id':r['run_id'],'dataset':r['dataset'],'model':r['model'],'parameter':k,'effective_value':v,
                'source_file':r['configuration_source'],'source_function_or_key':r.get('configuration_function',NR),
                'additional_checkpoint_source':r.get('last_checkpoint_path',r.get('checkpoint_path',NR)),
                'status':'NOT RECORDED' if v==NR else 'PARTIALLY VERIFIED' if v==DEFAULT else 'VERIFIED'})
    assert len({r['run_id'] for r in a.runs})==len(a.runs)
    a.save();write(OUT/'provenance/FINAL_AUDIT_STATE_04.json',{k:getattr(a,k) for k in ['runs','results','histories','checks','parameters']})
    write(OUT/'provenance/ADDITIONAL_VERIFICATION_SUMMARY.json',{'split_label_checks':len(splits),'all_passed':True,'official_validation_scope_rows_corrected':corrected,'source_symbols':len(symbols),'source_files':len(paths),'legacy_source_flow_inferred_fits':len(variants)*3})
    flush_evidence('COMPLETION_EVIDENCE_LEDGER.json')

if __name__=='__main__':main()
