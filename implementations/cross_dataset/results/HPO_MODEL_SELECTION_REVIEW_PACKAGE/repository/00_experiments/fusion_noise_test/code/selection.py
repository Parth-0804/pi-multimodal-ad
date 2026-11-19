"""Eligibility and whole-fold coverage precede any clean AP ranking."""
from pathlib import Path
import shutil
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score
from common import RUN,REPO,STUDY,config,read,write,write_text,csv,sha,signature,local,readiness,code_identity,event
KEYS=['recording_id','segment_id']
CANDIDATES=['frozen_16_frames','fine_tuned_16_frames','frozen_32_frames','fine_tuned_32_frames','cnn_plus_encoder']


def validate_job(f,j):
    groups={k:set(f.iloc[j[k]].recording_id) for k in ['G','C','predict','T']}
    for role in groups:
        ix=j[role];assert len(ix)==len(set(ix)) and set(ix)==set(np.flatnonzero(f.recording_id.isin(groups[role]))),'PARTIAL_RECORDING'
    G,C,V,T=[groups[k] for k in ['G','C','predict','T']];E=set(j['outer_E_recordings'])
    assert not G&C and not (G|C)&V and not T&E,'LEAKAGE'
    if j['role']=='outer_assessment':assert G|C==T and V==E
    else:assert G|C|V==T and not (G|C|V)&E
    return True


def rank(candidates,reference='frozen_16_frames',terminal=True):
    """Pure selection tested with synthetic fixtures. Never reads noisy fields."""
    if not terminal:raise RuntimeError('WAITING_FOR_PREVIOUS_RESULTS')
    usable={k:v for k,v in candidates.items() if v.get('eligible') and v.get('folds') and k!='cnn_only'}
    if reference not in usable:raise RuntimeError('REFERENCE_UNAVAILABLE')
    common=set.intersection(*(set(v['folds']) for v in usable.values()))
    if not common:raise RuntimeError('NO_COMMON_WHOLE_FOLDS')
    banks={}
    for name,v in usable.items():
        t=pd.concat([v['folds'][k] for k in sorted(common)],ignore_index=True).sort_values(KEYS).reset_index(drop=True)
        assert not t.duplicated(KEYS).any(),'DUPLICATE_ASSESSMENT_KEY'
        assert set(t.failure)=={0,1},'CLASS_SUPPORT'
        banks[name]=t
    base=banks[reference]
    for t in banks.values():
        assert t[KEYS].values.tolist()==base[KEYS].values.tolist() and np.array_equal(t.failure,base.failure),'INCOMPATIBLE_ROWS'
        assert np.array_equal(t.p_sensor,base.p_sensor) or np.allclose(t.p_sensor,base.p_sensor,rtol=0,atol=1e-12),'DIFFERENT_SENSOR_REFERENCE'
    scores={k:float(average_precision_score(t.failure,t.p_fused)) for k,t in banks.items()}
    tolerance=1e-12;best=max(scores.values())
    if best<=scores[reference]+tolerance:winner=reference
    else:
        tied=[k for k,v in scores.items() if abs(v-best)<=tolerance and v>scores[reference]+tolerance]
        fewest=min(usable[k]['frames'] for k in tied);tied=[k for k in tied if usable[k]['frames']==fewest]
        if all(usable[k].get('parameters') is not None for k in tied):
            smallest=min(usable[k]['parameters'] for k in tied);tied=[k for k in tied if usable[k]['parameters']==smallest]
        winner=sorted(tied)[0]
    return {'winner':winner,'reference':reference,'folds':sorted(common),'scores':scores,'banks':banks,
            'coverage':'FULL_COVERAGE' if len(common)==5 else 'PARTIAL_COVERAGE_PILOT'}


def component_paths(root,name,fold,encoder=False):
    d=root/name/fold;visual=d/'outer_assessment'
    if not encoder:visual=visual/'visual_fit'
    sensor=root/'sensor_reference'/fold/'outer_assessment'
    return {'head':visual/'model.pt','calibrator':visual/'calibrator.json','visual_complete':visual/'complete.json',
            'sensor':sensor/'model_and_calibrator.json','sensor_complete':sensor/'complete.json',
            'stacker':d/'F2_stacker.json','condition_complete':d/'condition_complete.json','predictions':d/'assessment_predictions.csv'}


def collect(rank_allowed=False):
    cfg=config();visual=REPO/cfg['visual_run'];encoder=REPO/cfg['encoder_run']
    cohort=pd.DataFrame(read(RUN/'data/cohort_and_frames.json'));jobs=read(RUN/'data/fit_partitions.json')
    candidates={};reasons=[]
    # Alias is never admitted as a higher-scoring alternative reference.
    reference_source='frozen_16_frames'
    if not list((visual/'frozen_16_frames').glob('fold_*/condition_complete.json')):
        if list((encoder/'cnn_only').glob('fold_*/condition_complete.json')):reference_source='cnn_only'
    for name in CANDIDATES:
        is_encoder=name=='cnn_plus_encoder' or (name=='frozen_16_frames' and reference_source=='cnn_only')
        root=encoder if is_encoder else visual;source_name=reference_source if name=='frozen_16_frames' else name
        cf=read(root/'resolved_config.json') if is_encoder else read(root/'config/resolved_config.json')
        record={'eligible':True,'folds':{},'components':{},'frames':16 if name=='cnn_plus_encoder' else (32 if '32' in name else 16),'parameters':None,'origin':str(root.relative_to(REPO)),'source_name':source_name,'reasons':[]}
        cohort_path=root/('data/cohort_and_frames.json' if is_encoder else 'data_manifests/cohort_and_frames.json')
        partition_path=root/('data/fit_partitions.json' if is_encoder else 'data_manifests/fit_partitions.json')
        if sha(cohort_path)!=sha(RUN/'data/cohort_and_frames.json') or sha(partition_path)!=sha(RUN/'data/fit_partitions.json'):
            record['eligible']=False;record['reasons'].append('Incompatible cohort or saved fit memberships')
        expected={'epochs':5,'effective_batch_segments':8,'microbatch_segments':1,'precision':'float32','head_lr':.001,'weight_decay':.001,'gradient_clip':1.,'sensor_C':1.,'max_iter':2000,'fusion_C':1.,'threshold':.5,'seed':42}
        if any(cf.get(k)!=v for k,v in expected.items()):record['eligible']=False;record['reasons'].append('Unrelated fitting-policy departure')
        for k in range(5):
            fold=f'fold_{k+1:02d}';paths=component_paths(root,source_name,fold,is_encoder)
            if not paths['condition_complete'].exists():continue
            if not all(p.is_file() for p in paths.values()):record['reasons'].append(f'{fold}: missing required final fitted component');continue
            try:
                done=read(paths['condition_complete']);v=read(paths['visual_complete']);sensor=read(paths['sensor_complete'])
                job=next(j for j in jobs if j['fold_name']==fold and j['role']=='outer_assessment')
                assert v['job']==sensor['job']==job,'FINAL_FIT_ROLE'
                for j in [j for j in jobs if j['fold_name']==fold]:validate_job(cohort,j)
                ph=done['predictions_sha256'] if is_encoder else done['assessment_sha256']
                assert sha(paths['predictions'])==ph,'INCOMPLETE_PREDICTION_WRITE'
                if is_encoder:
                    assert sha(paths['head'])==v['outputs']['model.pt']
                    assert sha(paths['sensor'])==sensor['outputs']['model_and_calibrator.json']
                else:
                    assert sha(paths['head'])==v['model_sha256']
                    assert sensor['model']==read(paths['sensor'])
                    assert done['visual_fit_id']==v['fit_id'] and done['sensor_fit_id']==sensor['fit_id']
                t=pd.read_csv(paths['predictions'],dtype={k:str for k in KEYS+['sample_id']})
                expected_rows=cohort.iloc[job['predict']]
                assert not t.duplicated(KEYS).any() and t[KEYS].values.tolist()==expected_rows[KEYS].values.tolist(),'ROW_COVERAGE'
                assert np.array_equal(t.failure,expected_rows.failure) and np.isfinite(t[['p_visual','p_sensor','p_fused']]).all().all()
                assert ((t[['p_visual','p_sensor','p_fused']]>=0)&(t[['p_visual','p_sensor','p_fused']]<=1)).all().all()
                assert np.all(t.threshold==.5),'THRESHOLD_DEPARTURE'
                stack=read(paths['stacker']);m=stack['model']
                from scipy.special import expit
                assert np.max(abs(expit(t[['p_visual','p_sensor']].to_numpy()@m['coefficient']+m['intercept'])-t.p_fused))<1e-12,'STACKER_RECONCILIATION'
                # All inner probability rows are disjoint from E and cover T.
                oof=root/source_name/fold/'fusion_training/identified_oof_branch_probabilities.csv'
                assert oof.exists(),'NO_KEYED_INNER_OOF'
                ot=pd.read_csv(oof,dtype={k:str for k in KEYS+['sample_id']})
                assert not ot.duplicated(KEYS).any() and set(ot.sample_id)==set(cohort.iloc[job['T']].sample_id),'INNER_COVERAGE'
                assert not set(ot.recording_id)&set(t.recording_id),'OUTER_LEAKAGE'
                paths['oof']=oof
                if not is_encoder:
                    assert v['frames']==record['frames'] and v['epochs_complete']==5
                    assert v['final_stage_trainable']==name.startswith('fine_tuned')
                    record['parameters']=v.get('loaded_backbone_parameters')
                else:
                    if (root/'checks/real_extractor_preflight.json').exists():
                        matches=[r for r in read(root/'checks/real_extractor_preflight.json')['results'] if r['condition']==source_name]
                        if matches:record['parameters']=matches[0]['active_frozen_parameters']
                record['folds'][fold]=t
                record['components'][fold]={key:{'path':str(p.relative_to(REPO)),'sha256':sha(p)} for key,p in paths.items()}
                if not rank_allowed:
                    dest=RUN/'model_selection/unranked_upstream_predictions'/source_name/(fold+'.csv');local(dest);shutil.copyfile(paths['predictions'],dest)
            except (AssertionError,KeyError,ValueError) as exc:record['reasons'].append(f'{fold}: {type(exc).__name__}: {exc}')
        candidates[name]=record
    return candidates,reference_source


def comparison_inventory(candidates):
    return pd.DataFrame([{'condition':name,'origin':c['origin'],'eligible_design':c['eligible'],'usable_complete_folds':','.join(c['folds']),'fold_count':len(c['folds']),
        'selection_status':'NOT_RANKED_UPSTREAM_ACTIVE','fused_AP':None,'visual_AP':None,'sensor_AP':None,'delta_reference':None,'reason':'; '.join(c['reasons']) or ('Complete fold artifacts found; selection deferred' if c['folds'] else 'No complete replayable outer folds yet')} for name,c in candidates.items()])


def select():
    lock=RUN/'model_selection/selected_model.json'
    if lock.exists():
        selected=read(lock)
        assert selected['config_sha256']==sha(STUDY/'config.json'),'SELECTION_CONFIG_DRIFT'
        assert sha(lock)==read(RUN/'model_selection/selection_lock.json')['selected_model_sha256'],'SELECTION_LOCK_DRIFT'
        if selected['source_identity']!=code_identity():
            revision=read(RUN/'provenance/replay_repair_01/approved_revision.json')
            assert revision['selected_model_sha256']==sha(lock) and revision['selection_lock_sha256']==sha(RUN/'model_selection/selection_lock.json'),'REPAIR_SELECTION_DRIFT'
            assert revision['original_source_identity']==selected['source_identity'] and revision['repaired_source_identity']==code_identity(),'REPAIR_SOURCE_DRIFT'
            assert revision['config_sha256']==sha(STUDY/'config.json'),'REPAIR_CONFIG_DRIFT'
            for path,digest in revision['original_source_identity'].items():
                assert sha(RUN/'provenance/replay_repair_01'/path)==digest,'ORIGINAL_SOURCE_SNAPSHOT_DRIFT'
            tests=read(RUN/'checks/tests.json')
            assert tests['passed'] and tests['source_identity']==code_identity(),'REPAIR_TESTS_REQUIRED' 
        for parts in selected['components'].values():
            for d in parts.values():assert sha(REPO/d['path'])==d['sha256'],'SELECTED_COMPONENT_DRIFT'
        return selected
    ready=readiness()
    if not ready['terminal_inputs']:raise RuntimeError('WAITING_FOR_PREVIOUS_RESULTS')
    candidates,source=collect(rank_allowed=True);result=rank(candidates)
    from evaluation import paired_interval
    rows=[];base=result['banks'][result['reference']]
    for name,c in candidates.items():
        if name not in result['banks']:
            rows.append({'condition':name,'eligible':False,'reason':'; '.join(c['reasons']) or 'Zero complete usable folds','fused_AP':None});continue
        t=result['banks'][name];interval=paired_interval(base,[t],'p_fused',difference='new_minus_clean')
        row={'condition':name,'eligible':True,'reason':'; '.join(c['reasons']),'coverage':result['coverage'],'folds':','.join(result['folds']), 'samples':len(t),'recordings':t.recording_id.nunique(),'failures':int(t.failure.sum()),
             'fused_AP':result['scores'][name],'visual_AP':float(average_precision_score(t.failure,t.p_visual)),'sensor_AP':float(average_precision_score(t.failure,t.p_sensor)),
             'delta_reference':result['scores'][name]-result['scores'][result['reference']],**interval}
        rows.append(row);csv(RUN/'model_selection/clean_predictions'/(name+'.csv'),t)
    csv(RUN/'model_selection/clean_comparison.csv',pd.DataFrame(rows))
    winner=result['winner'];c=candidates[winner]
    selected={'condition':winner,'source_condition':c['source_name'],'reference':'frozen_16_frames','reference_source_condition':source,
        'clean_AP':result['scores'][winner],'reference_AP':result['scores']['frozen_16_frames'],'clean_AP_improvement':result['scores'][winner]-result['scores']['frozen_16_frames'],
        'coverage':result['coverage'],'folds':result['folds'],'samples':len(result['banks'][winner]),'frames':c['frames'],'precision':'float32','thresholds':{'visual':.5,'sensor':.5,'fused':.5},
        'components':{k:c['components'][k] for k in result['folds']},'config_sha256':sha(STUDY/'config.json'),'source_identity':code_identity(),
        'cohort_sha256':sha(RUN/'data/cohort_and_frames.json'),'partitions_sha256':sha(RUN/'data/fit_partitions.json'),
        'processor_and_checkpoint':read(RUN/'provenance/original_pretrained_identity.json'),'label_orientation':'failure=1; success=0','camera':'hand',
        'exposure':config()['exposure'],'selection_rule':'unrounded pooled clean fused AP; numerical tolerance1e-12; ties reference, fewer frames, reliably measured fewer executed parameters, alphabetical',
        'corruption_config_sha256':sha(STUDY/'config.json')}
    write(lock,selected);write(RUN/'model_selection/selection_lock.json',{'selected_model_sha256':sha(lock),'corruption_config_sha256':sha(STUDY/'config.json')})
    event('MODEL_SELECTED',selected_condition=winner,coverage=result['coverage'],included_folds=result['folds'])
    return selected
