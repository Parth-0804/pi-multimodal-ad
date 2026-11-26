"""Independent source joins and saved-prediction recomputation, without fitting."""
from collections import Counter
import json
import numpy as np

from .common import PROJECT,config,core,read,resolve,sha,write
from .metrics import metrics,independent_check
from .splits import prepare,require_oof


def native_labels(c=None):
    c=c or config();base=resolve(c['historical_root'])/'source_evidence'
    originals={};sources={}
    for path in sorted((base/'original/annotated_data').rglob('*_annotations.json')):
        receipt=read(path.with_name(path.name+'.receipt.json'))
        assert sha(path)==receipt['sha256'],'NATIVE_ANNOTATION_SOURCE_DRIFT'
        sources[str(path.relative_to(PROJECT.parent))]=sha(path)
        for record in read(path):
            key=record['video'];assert key not in originals,'AMBIGUOUS_NATIVE_EPISODE'
            assert record['failure_detection'] in ['yes','no'];originals[key]=record
    metadata=base/'vifailback/meta/vifailback_annotations.jsonl'
    assert sha(metadata)==read(metadata.with_name(metadata.name+'.receipt.json'))['sha256']
    converted=[json.loads(line) for line in metadata.open()]
    episodes=[json.loads(line) for line in (base/'vifailback/meta/episodes.jsonl').open()]
    ep={r['episode_index']:r for r in episodes};assert len(ep)==len(converted)==len(originals)==5202
    targets={};native_ids=set()
    for record in converted:
        annotation=record['annotation'];key=annotation['video'];original=originals[key]
        assert key not in native_ids;native_ids.add(key)
        assert all(annotation.get(k)==v for k,v in original.items()),'NATIVE_CONVERSION_ANNOTATION_MISMATCH'
        label=int(original['failure_detection']=='yes');e=record['episode_index'];assert e not in targets
        assert record['episode_success']==('failure' if label else 'success')
        assert ep[e]['length']==record['num_frames'] and original['task'] in ep[e]['tasks']
        targets[e]=label
    counts=Counter(targets.values());assert counts=={1:4545,0:657}
    candidates=core(c);assert all(targets[r['episode_index']]==r['label'] for r in candidates)
    assert len({r['sensor_content_sha256'] for r in candidates})==len(candidates),'DUPLICATE_NUMERICAL_TRAJECTORY'
    result={'native_episodes':5202,'native_failure':4545,'native_no_failure':657,'source_annotation_files':len(sources),
            'converted_metadata_sha256':sha(metadata),'native_source_sha256':sources,
            'all_native_to_converted_to_core_joins':True,'core_episodes':len(candidates),
            'core_failure':3755,'core_no_failure':629,'core_tasks':99,'core_full_numeric_arrays_unique':True,
            'original_HDF5_scope':'Previously bounded checks of3 anomalous source episodes/9 arrays; not every original HDF5 downloaded',
            'hardware_alignment':'Converted relative25Hz index agreement only; hardware clock calibration not established'}
    destination=PROJECT/'02_dataset_verification/label_audit'/c['run_id']/'INDEPENDENT_NATIVE_RECOUNT.json'
    if destination.exists():assert read(destination)==result,'NATIVE_SOURCE_OR_JOIN_DRIFT'
    else:write(destination,result)
    return result


def saved_results(c=None):
    c=c or config();jobs=prepare(c);verified=[];incomplete=[];job_index={j['id']:j for j in jobs}
    native_labels(c)
    from .cohort import finalize
    targets={r['episode_index']:r['label'] for r in finalize(c)}
    banks={}
    root=PROJECT/'06_training_experiments'
    # Every report is regenerated from the saved per-example probabilities.
    paths=list(root.glob(f'*/runs/{c["run_id"]}/**/predictions.json'))
    paths+=list((root/'fusion_experiments/augmentation/runs'/c['run_id']).glob('*/seed*/outer*/predictions.json'))
    for path in sorted(paths):
        if not path.with_name('COMPLETE.json').exists():
            incomplete.append({'path':str(path.relative_to(PROJECT.parent)),'reason':'NO_COMPLETION_RECEIPT; not accepted as final evidence'});continue
        rows=read(path)
        if not rows:continue
        assert all(r['label']==targets[r['episode_index']] for r in rows),'PREDICTION_TARGET_DRIFT'
        job=job_index[rows[0]['fit_id']]
        assert [r['episode_index'] for r in rows]==job['ids']['A'],'PREDICTION_UNIT_OR_SPLIT_MISMATCH'
        report_path=path.with_name('metrics.json')
        assert report_path.exists(),'PREDICTIONS_WITHOUT_METRIC_REPORT'
        report=read(report_path);y=np.asarray([r['label'] for r in rows])
        if 'F2_aug_probability' in rows[0]:mapping={'F2_aug':'F2_aug_probability','Gate_aug':'gate_aug_probability','Gate_static_aug':'gate_static_aug_probability'}
        elif 'S3_probability' in rows[0]:mapping={'S3':'S3_probability','S2':'S2_probability','T_prevalence_reference':'training_prevalence_probability'}
        elif 'F2_probability' in rows[0]:mapping={'F1_average':'F1_average','F2':'F2_probability','quality_gate':'gate_probability','gate_static':'gate_static_probability'}
        else:mapping={None:'probability'}
        for key,column in mapping.items():
            p=np.asarray([r[column] for r in rows]);actual=metrics(y,p);expected=report if key is None else report[key]
            independent_check(y,p,expected)
            for name,value in actual.items():
                if isinstance(value,(float,int)):assert np.isclose(value,expected[name],rtol=0,atol=1e-12),(path,key,name)
        completed=read(path.with_name('COMPLETE.json'));assert sha(path)==completed['prediction_sha256']
        if (path.parent/'HISTORY.json').exists():
            history=read(path.parent/'HISTORY.json')
            assert [r['epoch'] for r in history]==list(range(1,101))
            selected=1+int(np.argmax([r['V_macro_AP'] for r in history]))
            assert completed['selected_epoch']==selected
            assert sha(path.parent/'BEST_MODEL.pt')==completed['best_checkpoint_sha256']
            assert sha(path.parent/'FINAL_EPOCH100.pt')==completed['final_checkpoint_sha256']
            import torch
            selected_state=torch.load(path.parent/'BEST_MODEL.pt',map_location='cpu',weights_only=True)
            assert selected_state['selected_epoch']==selected
            from .feature_bank import pooled_bank
            from .reference import primitives
            condition=completed['condition'];bank_key='V3' if condition=='V3' else 'V1_high_only' if condition=='V1_high_only' else 'V1'
            if bank_key not in banks:banks[bank_key]=pooled_bank(c,bank_key)
            bank,bank_receipt=banks[bank_key]
            index={r['episode_index']:i for i,r in enumerate(finalize(c))}
            mean,std=primitives()['standardizer'](bank[[index[e] for e in job['ids']['T']]])
            assert np.array_equal(selected_state['model']['mean'].numpy(),mean)
            assert np.array_equal(selected_state['model']['std'].numpy(),std)
            assert selected_state['bank_sha256']==bank_receipt['sha256']
            cal=read(path.parent/'CALIBRATION_PREDICTIONS.json')
            assert [r['episode_index'] for r in cal]==job['ids']['C']
            assert all(r['label']==targets[r['episode_index']] for r in cal)
            fresh=primitives()['calibrate'](np.asarray([r['raw'] for r in cal],dtype='float32'),np.asarray([r['label'] for r in cal]))
            old=read(path.parent/'CALIBRATOR.json')
            assert np.allclose(fresh['coefficient'],old['coefficient'],rtol=0,atol=1e-12)
            assert abs(fresh['intercept']-old['intercept'])<1e-12
        verified.append({'predictions':str(path.relative_to(PROJECT.parent)),'sha256':sha(path),'rows':len(rows),'metrics_recomputed':True})
    for path in sorted((root/'fusion_experiments/runs'/c['run_id']).glob('*/seed*/outer*/META_TRAINING_PREDICTIONS.json')):
        outer=int(path.parent.name.removeprefix('outer'));require_oof(jobs,outer,read(path))
    for path in sorted((root/'fusion_experiments/augmentation/runs'/c['run_id']).glob('*/seed*/outer*/AUGMENTED_OOF_RECORDS.json')):
        outer=int(path.parent.name.removeprefix('outer'));require_oof(jobs,outer,read(path))
    for path in sorted((PROJECT/'07_robustness_experiments/combined_corruption/runs'/c['run_id']).glob('*/seed*/outer*/predictions.json')):
        if not path.with_name('COMPLETE.json').exists():
            incomplete.append({'path':str(path.relative_to(PROJECT.parent)),'reason':'NO_COMPLETION_RECEIPT; not accepted as final stress evidence'});continue
        records=read(path);report=read(path.with_name('metrics.json'))
        completed=read(path.with_name('COMPLETE.json'));assert sha(path)==completed['prediction_sha256']
        for name,result in report.items():
            part=[r for r in records if r['scenario']==name and r['status']=='PREDICTED']
            assert len(part)==result['scored']
            assert all(r['label']==targets[r['episode_index']] for r in part)
            for key in ['visual_probability','S3_probability','S2_probability','F1_average','F2_probability','gate_probability','gate_static_probability','F2_aug_probability','gate_aug_probability','gate_static_aug_probability']:
                if not part:continue
                if key not in result:continue
                y=np.asarray([r['label'] for r in part]);p=np.asarray([r[key] for r in part])
                independent_check(y,p,result[key])
        verified.append({'predictions':str(path.relative_to(PROJECT.parent)),'sha256':sha(path),'rows':len(records),'stress_metrics_recomputed':True})
    result={'verified_saved_prediction_tables':verified,'incomplete_unaccepted_prediction_tables':incomplete,'independent_person_signoff':False,
            'verification_scope':'separate AP/confusion/Brier formulas plus full sklearn recomputation from saved probabilities; automatic checks, no second-human signoff'}
    write(PROJECT/'10_final_research_reports/reproducibility'/c['run_id']/'INDEPENDENT_RESULT_CHECK.json',result)
    return result
