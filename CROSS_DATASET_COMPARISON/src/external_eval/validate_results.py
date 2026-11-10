"""Post-fit audit: budgets, native units, split roles and exact saved-OOF F2."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from external_eval.io import write_json,sha


def audit(root,predictions,cases):
    root=Path(root);config=json.loads((root/'04_experiment_protocol/experiment_config.json').read_text())
    plans=json.loads((root/'03_processed_model_inputs/split_manifests/frozen_splits.json').read_text())
    frame=pd.read_csv(root/'03_processed_model_inputs/final_sample_manifest.csv').set_index('sample_id',drop=False)
    selected=pd.read_csv(root/'02_labels_and_alignment/alignment_manifest.csv');id_column='sample_id' if 'sample_id' in selected else 'interval_id'
    selected=selected[selected[id_column].isin(frame.index)]
    content=selected.groupby(id_column).decoded_frame_sha256.nunique()
    if (content!=16).any() or set(content.index)!=set(frame.index):raise ValueError('Primary16-frame examples contain missing or exact repeated RGB content')
    conditions=sorted(predictions.initialization.unique());expected={(c,p,int(seed),k) for c in conditions for p,d in plans.items() for seed in config['seeds'] for k in range(len(d['plan']))}
    actual={(c['initialization'],c['protocol'],int(c['seed']),int(c['fold'])) for c in cases}
    if expected!=actual or len(actual)!=len(cases):raise ValueError('Incomplete or repeated predeclared matrix')
    records=[];fits=0;max_f2_difference=0.
    case_map={c['case_id']:c for c in cases}
    for ident,rows in predictions.groupby('case_id',sort=False):
        case=case_map[ident];definition=plans[case['protocol']];fold=definition['plan'][case['fold']]
        ids=np.asarray(definition['sample_ids']);train=set(ids[np.asarray(fold['train'],int)]);test=set(ids[np.asarray(fold['test'],int)])
        for role in rows.role.unique():
            expected_ids=test if role=='test' else set(ids[np.asarray(fold['validation'],int)])
            if set(rows.loc[rows.role==role,'sample_id'])!=expected_ids:raise ValueError('Wrong native assessment units')
            if expected_ids&train:raise ValueError('Assessment entered final fit')
        truth=frame.loc[rows.sample_id,'native_label'].to_numpy(int)
        target=(truth==1).astype(int) if config['dataset']=='MSM' else (truth!=0).astype(int)
        if not np.array_equal(truth,rows.native_label.to_numpy(int)) or not np.array_equal(target,rows.target.to_numpy(int)):raise ValueError('Prediction/native target association changed')
        log=json.loads((Path(case['predictions']).parent/'training_and_runtime.json').read_text())
        final_train=None
        for fit in log['base_fits']:
            fits+=1;allowed=set(fit['train_sample_ids'])
            if not allowed<=train or allowed&test:raise ValueError('Base fit includes assessment identities')
            updates=int(np.ceil(len(allowed)/config['visual']['batch_size']))*config['visual']['epochs']
            if fit['log']['updates']!=updates or len(fit['log']['losses'])!=updates:raise ValueError('Head training budget differs from frozen protocol')
            if not fit['log']['finite_losses'] or not fit['log']['all_head_parameters_nonzero_gradient']:raise ValueError('Head numerical/gradient failure')
            if fit['reload_max_abs_difference']!=0 or fit['strong_reload_max_abs_difference']!=0:raise ValueError('Exact reload failed')
            if sha(fit['visual_checkpoint'])!=fit['visual_sha256']:raise ValueError('Visual checkpoint bytes changed')
            if fit['classical_checkpoint'] and sha(fit['classical_checkpoint'])!=fit['classical_sha256']:raise ValueError('HGB checkpoint bytes changed')
            if fit['role']=='final_refit':
                if allowed!=train:raise ValueError('Final refit omits frozen training units')
                if fit['actual_seed']!=case['seed']+99:raise ValueError('Final derived seed mismatch')
                final_train=fit
            elif fit['role'].startswith('inner'):
                if fit['actual_seed']!=case['seed']+int(fit['role'].removeprefix('inner')):raise ValueError('Inner derived seed mismatch')
        if final_train is None:raise ValueError('No final model receipt')
        if config['dataset']=='MSM':
            fusion=root/'05_trained_models/f2_fusion'/ident/Path(case['predictions']).parent.name
            with np.load(fusion/'OOF_bank.npz',allow_pickle=False) as z:
                oo_ids=z['sample_ids'];p=z['probabilities'][0];y=z['targets'];row_indices=z['train_rows']
                if set(oo_ids)!=train or len(set(oo_ids))!=len(train):raise ValueError('OOF native units differ from final training set')
                if not np.array_equal(frame.iloc[row_indices].sample_id.to_numpy(str),oo_ids):raise ValueError('OOF positional/native-ID association changed')
                if not np.array_equal(y,frame.loc[oo_ids,'target'].to_numpy(int)):raise ValueError('OOF label association changed')
            provenance=json.loads((fusion/'stacking_provenance.json').read_text());grouping=definition['grouping']
            train_groups=set(frame.loc[list(train),grouping].astype(str));test_groups=set(frame.loc[list(test),grouping].astype(str))
            if train_groups&test_groups:raise ValueError('Outer groups overlap')
            for sample in oo_ids:
                group=str(frame.loc[sample,grouping])
                for branch in ['visual','sensor']:
                    entry=provenance[sample][branch];fit_groups=set(map(str,entry['fit_groups']))
                    if not fit_groups or not fit_groups<=train_groups or group in fit_groups or fit_groups&test_groups:raise ValueError('OOF base group contamination')
                    if entry['selection_groups']:raise ValueError('Undeclared inner selection groups')
            original=json.loads((fusion/'F2.json').read_text())
            # Refit only the same fixed three-parameter OOF estimator, using no
            # outer rows, as an independent serialization/provenance check.
            reproduced=LogisticRegression(C=1,class_weight=None,solver='lbfgs',max_iter=2000,random_state=0).fit(p,y)
            difference=max(float(np.max(abs(reproduced.coef_-np.asarray(original['coef'])))),float(np.max(abs(reproduced.intercept_-np.asarray(original['intercept'])))))
            if difference>1e-12:raise ValueError('Saved F2 differs from the actual clean OOF estimator')
            max_f2_difference=max(max_f2_difference,difference)
            for name in ['QG_clean','QG_aug']:
                gate=json.loads((fusion/(name+'.json')).read_text())
                if len(gate['loss_by_epoch'])!=config['quality_gate']['epochs'] or gate['reload_max_abs_difference']!=0:raise ValueError('Gate epoch/reload mismatch')
        records.append({'case_id':ident,'passed':True,'native_assessment_units':len(test),'native_train_units':len(train),'actual_final_seed':final_train['actual_seed']})
    result={'passed':True,'cases':len(cases),'base_fits_audited':fits,'all_predeclared_cases_present':True,
        'minimum_distinct_decoded_RGB_contents_per_example':int(content.min()),'examples_with_exact_repeated_RGB_content':int((content<16).sum()),
        'all_native_labels_and_prediction_units_match':True,'all_final_and_inner_training_budgets_match':True,
        'all_saved_reload_differences_zero':True,'F2_refit_from_saved_clean_OOF_max_abs_difference':max_f2_difference if config['dataset']=='MSM' else None,
        'F2_no_assessment_rows_or_groups':config['dataset']=='MSM','Handover_participant_fusions_not_substituted':config['dataset']=='HANDOVER',
        'case_checks':records}
    write_json(root/'06_evaluation_results/implementation_validation.json',result)
    return result
