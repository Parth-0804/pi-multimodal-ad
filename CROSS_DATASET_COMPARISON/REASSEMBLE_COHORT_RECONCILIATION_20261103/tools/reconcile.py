"""Read saved REASSEMBLE identities/splits/predictions; never fit or import a model."""
from pathlib import Path
from functools import lru_cache
import collections
import csv
import datetime as dt
import hashlib
import itertools
import json
import math
import os
import re
import subprocess
import sys
import numpy as np
import pandas as pd

csv.field_size_limit(256*1024**2)
OUT=Path(__file__).resolve().parents[1]
REPO=OUT.parents[1]
AUDIT=REPO/'CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103'
BASE=Path('26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability')
FOLLOW=Path('experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison')
LEGACY=Path('parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01')
NR='NOT RECORDED'
USED={};SETS={};EVALS=[];RUNS=[];CONFLICTS=[];GAPS=[];ALIASES={};CANON=[];BYKEY={};FOLDS=[]
SCORE_FILE=None;SCORE_WRITER=None


def resolve(p):return p if isinstance(p,Path) and p.is_absolute() else REPO/p
def rel(p):
    p=Path(p)
    try:return str(p.relative_to(REPO))
    except ValueError:return str(p)
def sha(p):
    h=hashlib.sha256()
    with resolve(p).open('rb') as f:
        for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
    return h.hexdigest()
def used(p):
    p=resolve(p);name=rel(p)
    if name not in USED:
        st=p.stat();USED[name]={'path':name,'bytes':st.st_size,'mtime_ns':st.st_mtime_ns,'sha256':sha(p)}
    return p
@lru_cache(maxsize=8000)
def read(p):return json.loads(used(p).read_text())
def rows(p):
    with used(p).open(newline='') as f:return list(csv.DictReader(f))
def save_json(name,x):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def save_csv(name,rs,fields=None):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
    fields=fields or list(dict.fromkeys(k for r in rs for k in r))
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or ['no_records']);w.writeheader()
        for r in rs:w.writerow({k:json.dumps(v,sort_keys=True) if isinstance(v,(list,dict)) else v for k,v in r.items()})
def hash_lines(v):return hashlib.sha256(('\n'.join(v)+'\n').encode()).hexdigest()
def native_key(recording,segment):
    s=str(segment).strip()
    if re.fullmatch(r'\d+\.0',s):s=s[:-2]
    return str(recording).strip()+'::'+s
def key(row):
    if row.get('recording_id') is not None and row.get('segment_id') is not None:
        k=native_key(row['recording_id'],row['segment_id']);assert k in BYKEY,('UNKNOWN_NATIVE_ACTION',k)
    else:k=ALIASES[str(row['sample_id'])]
    if row.get('sample_id'):
        alias=str(row['sample_id']);assert alias not in ALIASES or ALIASES[alias]==k;ALIASES[alias]=k
    if 'failure' in row:assert int(float(row['failure']))==BYKEY[k]['failure'],('NATIVE_LABEL_CONFLICT',k)
    if row.get('action'):assert row['action']==BYKEY[k]['action'],('ACTION_TYPE_CONFLICT',k)
    for name in ['start','end']:
        if row.get(name) not in [None,'']:
            assert abs(float(row[name])-float(BYKEY[k][name]))<1e-6,('NATIVE_TIMESTAMP_CONFLICT',k,name)
    return k
def keys_indices(values):return [CANON[int(i)]['native_key'] for i in values]
def keys_aliases(values):return [ALIASES[str(i)] for i in values]
def register(keys,source=''):
    keys=list(keys);assert len(keys)==len(set(keys)),('DUPLICATE_ACTION_ID',source)
    values=tuple(sorted(keys));h=hash_lines(values)
    if h not in SETS:
        recordings=sorted({BYKEY[k]['recording_id'] for k in values})
        SETS[h]={'cohort_id':'C'+h[:16],'action_set_sha256':h,'label_map_sha256':hash_lines([k+'\t'+str(BYKEY[k]['failure']) for k in values]),
            'N':len(values),'failures':sum(BYKEY[k]['failure'] for k in values),'recording_N':len(recordings),
            'recording_set_sha256':hash_lines(recordings),'keys':values,'recordings':recordings,'first_source':str(source)}
    return SETS[h]
def record_role(record,name,keys,source):
    c=register(keys,source);record[name+'_cohort_id']=c['cohort_id'];record[name+'_N']=c['N'];record[name+'_recording_N']=c['recording_N']
    record[name+'_recording_ids']=c['recordings'];return c
def from_recordings(values):
    selected=set(values);assert selected<={r['recording_id'] for r in CANON}
    return [r['native_key'] for r in CANON if r['recording_id'] in selected]
def outer_parts(k,inner=None):
    obj=FOLDS[int(k)] if inner is None else FOLDS[int(k)]['inner'][int(inner)]
    return from_recordings(obj['train_recordings']),from_recordings(obj['test_recordings'] if inner is None else obj['validation_recordings'])


def canonical():
    p=Path('runs/reassemble/20260927T154732Z-section1/cohort.parquet')
    frame=pd.read_parquet(used(p));assert len(frame)==4530
    for i,r in enumerate(frame.to_dict('records')):
        r={k:(v.item() if isinstance(v,np.generic) else v) for k,v in r.items()};r['canonical_row']=i;r['native_key']=native_key(r['recording_id'],r['segment_id']);r['failure']=int(r['failure'])
        assert r['native_key'] not in BYKEY;CANON.append(r);BYKEY[r['native_key']]=r
    assert sum(r['failure'] for r in CANON)==509
    split=read(Path('runs/reassemble/20260927T154732Z-section1/nested_splits.json'));FOLDS.extend(split['folds'])
    for f in FOLDS:
        for k in from_recordings(f['test_recordings']):BYKEY[k]['outer_fold_zero_based']=f['fold'];BYKEY[k]['legacy_fold_name']=f'fold_{f["fold"]+1:02d}'
    for p in [LEGACY/'data_manifests/cohort.csv',Path('00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/data_manifests/cohort.csv')]:
        for row in rows(p):key(row)
    # Verify original row order against the inventory-source filter,not only the output filename.
    original=pd.read_parquet(used('runs/reassemble/20260927T141645Z-inventory/tables_v2/cohort.parquet'))
    original=original.loc[original.primary_task & original.dual_complete].reset_index(drop=True)
    assert [native_key(r.recording_id,r.segment_id) for r in original.itertuples()]==[r['native_key'] for r in CANON]
    assert original.failure.astype(int).tolist()==[r['failure'] for r in CANON]
    full=register([r['native_key'] for r in CANON],p)
    return full


def role_job(record,j,source,phase=False):
    mappings={'training':'TRAIN','validation':'VALIDATION','G':'FIT_G','C':'CALIBRATION','predict':'ASSESSMENT'}
    for field,name in mappings.items():
        if field in j:record_role(record,name,keys_indices(j[field]),source)
    if 'training' not in j and 'G' in j:record_role(record,'TRAIN',keys_indices(j['G']),source)
    record['outer_fold_zero_based']=j.get('outer_fold_original',NR);record['split_role']=j.get('role',NR)
    record['partition_seed']=j.get('seed',NR);record['validation_partition_seed']=j.get('validation_split_seed',NR)


def run_record(r):
    cfg=r['effective_configuration'];exp=r['experiment_id'];rid=r['run_id']
    result={'run_id':rid,'experiment_id':exp,'model':r['model'],'training_status':r['training_status'],
        'model_seed':cfg.get('seed',NR),'recorded_effective_seed_in_original_audit':cfg.get('seed',NR),
        'estimator_random_state':cfg.get('estimator_random_state',cfg.get('random_state',NR)),
        'seed_family':cfg.get('seed_family',cfg.get('nominal_split_seed',NR)),
        'outer_fold_zero_based':cfg.get('outer_fold',NR),'inner_fold':cfg.get('inner_fold',NR),
        'permutation':r.get('label_permutation',0),'label_contract':'PERMUTED CONTROL' if r.get('label_permutation',0) else 'NATIVE FAILURE',
        'source':r.get('history_source') or r['configuration_source'],'identity_evidence':'NOT RECORDED',
        'audit_train_N':r.get('train_N',NR),'audit_assessment_N':r.get('assessment_N',NR)}
    def original_split(k,inner=None):
        tr,te=outer_parts(k,inner);record_role(result,'TRAIN',tr,result['source']);record_role(result,'ASSESSMENT',te,result['source'])
        result['outer_fold_zero_based']=int(k);result['split_role']='OUTER_ASSESSMENT' if inner is None else 'INNER_SELECTION';result['identity_evidence']='SAVED RECORDING SPLIT -> VERIFIED CANONICAL ROWS'
    if exp.startswith('REASSEMBLE_PHASE1') or exp=='REASSEMBLE_100E_SINGLE_FIT':
        info=read(r['history_source']);source=r['history_source']
        for field,name in [('T_sample_ids','TRAIN'),('V_sample_ids','VALIDATION'),('C_sample_ids','CALIBRATION'),('prediction_sample_ids','ASSESSMENT')]:record_role(result,name,keys_aliases(info[field]),source)
        plan=read(BASE/'26102026_evidence/PHASE1_FIT_PLAN.json');j=plan[info['job_index']]
        result.update(job_index=info['job_index'],outer_fold_zero_based=j['outer_fold_original'],model_seed=info['seed'],partition_seed=j['seed'],validation_partition_seed=j.get('validation_split_seed',NR),
            split_role='SELECTED_INNER_TRAINING_ASSESSED_ON_OUTER' if exp=='REASSEMBLE_100E_SINGLE_FIT' else j['role'],identity_evidence='ACTUAL EXECUTED RECEIPT SAMPLE IDS',
            prediction_source=str(Path(source).parent/'PHASE1_PREDICTIONS.json'))
        if exp=='REASSEMBLE_100E_SINGLE_FIT':
            selected=read(BASE/'26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_configuration/PHASE1_SELECTED_JOB.json')
            result['validation_partition_seed_in_original_plan']=j.get('validation_split_seed',NR)
            result['validation_partition_seed']=selected.get('validation_split_seed',NR)
            result['training_validation_memberships_equal_original_job2']=selected['training']==j['training'] and selected['validation']==j['validation']
        actual=read(result['prediction_source']);actual=actual if isinstance(actual,list) else actual.get('rows',actual.get('predictions'))
        assert register([key(x) for x in actual])['cohort_id']==result['ASSESSMENT_cohort_id']
    elif exp in ['SECTION1','SECTION1B_SENSOR_NULL_CONTROLS']:
        k=int(cfg['outer_fold']);inner=cfg.get('inner_fold');m=re.search(r'::inner(\d+)',rid)
        if exp=='SECTION1B_SENSOR_NULL_CONTROLS':inner=int(m[1]) if m else None
        else:inner=inner if isinstance(inner,int) else None
        original_split(k,inner)
    elif exp=='SECTION1B_F2':
        k=int(cfg['outer_fold']);original_split(k);result['META_FIT_cohort_id']=result['TRAIN_cohort_id'];result['META_FIT_N']=result['TRAIN_N']
    elif exp=='SECTION1B_NESTED_BRANCHES':
        p=rid.split('::')[0];x=read(p);m=re.search(r'outer(\d+)(?:_inner(\d+))?',p);k=int(m[1]);part=rid.split('::')[2]
        if m[2] is None:
            if part=='refit':original_split(k)
            else:original_split(k,int(part.replace('subinner','')))
        else:
            entry=x
            if part=='refit':original_split(k,int(m[2]))
            else:
                s=entry['subfolds'][int(part.replace('subinner',''))]
                record_role(result,'TRAIN',from_recordings(s['train_recordings']),p);record_role(result,'ASSESSMENT',from_recordings(s['validation_recordings']),p)
                result.update(split_role='NESTED_SUBINNER_SELECTION',outer_fold_zero_based=k,identity_evidence='SAVED SUBFOLD RECORDING IDS')
    elif exp in ['SECTION2','MODALITY_DROPOUT']:
        p=rid;m=re.search(r'outer(\d+)_(final|inner(\d+))',p)
        if m:original_split(int(m[1]),None if m[2]=='final' else int(m[3]))
    elif exp.startswith('ADDITIONAL_') and exp!='ADDITIONAL_CORRUPTION_SMALL_STATES':
        x=read(r['history_source']);tr=x.get('train_rows',x.get('training_rows'));te=x.get('assessment_rows')
        if tr is not None:record_role(result,'TRAIN',keys_indices(tr),r['history_source'])
        if te is not None:record_role(result,'ASSESSMENT',keys_indices(te),r['history_source'])
        result['identity_evidence']='SAVED FIT ROW INDICES -> VERIFIED CANONICAL ORDER'
        result['split_role']='OUTER_REFIT' if 'refit' in Path(rid).name else 'INNER_VALIDATION_OR_NESTED_FIT'
    elif exp=='ADDITIONAL_CORRUPTION_SMALL_STATES':
        x=read(r['configuration_source']);tr=x.get('train_rows',x.get('training_rows'));te=x.get('test_rows',x.get('assessment_rows'))
        record_role(result,'TRAIN',keys_indices(tr),r['configuration_source']);record_role(result,'ASSESSMENT',keys_indices(te),r['configuration_source'])
        result['identity_evidence']='SAVED SMALL-MODEL ROW INDICES';result['split_role']='OUTER' if '_outer' in Path(rid).stem or '_refit' in Path(rid).stem or 'final' in Path(rid).stem else 'NESTED FIT'
    elif exp=='BOUNDARY_AWARE_VISUAL':
        x=read(r['history_source']);sig=x['signature'];record_role(result,'TRAIN',keys_indices(sig['train']),r['history_source']);record_role(result,'ASSESSMENT',keys_indices(sig['predict']),r['history_source'])
        result['identity_evidence']='SAVED SIGNATURE ROW INDICES';result['split_role']='OUTER_REFIT' if '/refit/' in rid else 'INNER_SELECTION'
    elif exp.startswith('00_experiments/'):
        p=Path(rid)/'complete.json';x=read(p);j=x.get('job')
        result['source']=str(p)
        if isinstance(j,dict):
            role_job(result,j,p);result['identity_evidence']='SAVED EXECUTED JOB ROW INDICES'
            if x.get('training_role_seed') is not None:result['model_seed']=x['training_role_seed']
            elif x.get('seed') is not None:result['model_seed']=x['seed']
            elif exp.startswith('00_experiments/visual_backbone_one_day') and r['model']!='sensor_reference':
                result['model_seed']=j['seed'];result['model_seed_source']='saved job.seed; source training.py explicitly seeds Python/NumPy/Torch with it'
        membership=Path(rid)/'memberships.json'
        if (REPO/membership).is_file():
            v=read(membership)
            for field,name in [('G_sample_ids','TRAIN'),('C_sample_ids','CALIBRATION'),('prediction_sample_ids','ASSESSMENT')]:
                if field in v:record_role(result,name,keys_aliases(v[field]),membership)
            result['identity_evidence']='SAVED JOB + DIRECT SAMPLE-ID MEMBERSHIP'
        if r['model']=='sensor_reference' and result['model_seed']==NR:
            impl=(Path('00_experiments/rt_detr_encoder_comparison/code/fusion.py')
                if 'rt_detr_encoder_comparison' in exp else Path('00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/source/fusion.py'))
            assert 'max_iter=2000,random_state=42' in used(impl).read_text()
            result['model_seed']=42;result['estimator_random_state']=42
            result['model_seed_source']='FIXED ESTIMATOR CONFIGURATION IN PRESERVED IMPLEMENTATION: '+str(impl)
    elif exp.startswith('LEGACY_'):
        p=r['configuration_source'];x=read(p)
        if 'training_sample_ids' in x:ids=keys_aliases(x['training_sample_ids'])
        else:ids=[key(v) for v in x['training_sample_keys']]
        record_role(result,'META_FIT',ids,p)
        m=re.search(r'fold_(\d+)',p)
        if m:
            result['outer_fold_zero_based']=int(m[1])-1;record_role(result,'ASSESSMENT',outer_parts(int(m[1])-1)[1],p)
            result['identity_evidence']='SAVED F2 FIT IDS + MATCHING RECORDED OUTER FOLD (prediction corroboration separate)'
        result['split_role']='OUTER_META_FIT'
        result['model_seed']=cfg.get('estimator_random_state',cfg.get('seed',NR))
        result['seed_family']=cfg.get('seed',NR)
    elif exp=='CNN100_STATIC_SENSOR_F2':
        x=read(r['configuration_source']);ids=x.get('training_sample_ids',x.get('sample_ids'))
        if ids:record_role(result,'META_FIT',keys_aliases(ids),r['configuration_source'])
        manifest=rows(FOLLOW/'01_experiment_definition/COMPLETE_ROLE_SAMPLE_MANIFEST.csv')
        rolemap=collections.defaultdict(list)
        for v in manifest:rolemap[v['CNN_and_fusion_role']].append(key(v))
        result['saved_role_names']=list(rolemap)
        for name,ks in rolemap.items():
            if name.lower() in ['outer_test','outer_assessment','test','held_out','assessment']:record_role(result,'ASSESSMENT',ks,FOLLOW/'01_experiment_definition/COMPLETE_ROLE_SAMPLE_MANIFEST.csv')
            elif 'fusion' in name.lower() or 'stack' in name.lower():record_role(result,'META_FIT',ks,FOLLOW/'01_experiment_definition/COMPLETE_ROLE_SAMPLE_MANIFEST.csv')
        if 'ASSESSMENT_cohort_id' not in result:record_role(result,'ASSESSMENT',[key(v) for v in read(FOLLOW/'06_held_out_predictions/ALL_MODELS_IDENTICAL_OUTER_IDS.json')],r['configuration_source'])
        result['outer_fold_zero_based']=0;result['split_role']='SINGLE_INNER_HOLDOUT_STACK_BANK_TO_OUTER';result['identity_evidence']='COMPLETE ROLE SAMPLE MANIFEST + SAVED FIT IDS'
    elif exp=='ADAPTIVE_FUSION_ROBUSTNESS_PILOT':
        components=read(r['configuration_source']);lineage=next(iter(components.values())).get('lineage')
        # Actual new meta heads use repeated clean/image/sensor views of the same outer-training parent IDs.
        tr,te=outer_parts(0);record_role(result,'META_FIT_PARENT',tr,r['configuration_source']);record_role(result,'ASSESSMENT',te,r['configuration_source'])
        result.update(outer_fold_zero_based=0,split_role='SINGLE_FOLD_ROBUSTNESS_META_FIT',identity_evidence='DECLARED OUTER-FOLD SOURCE + prediction verification',training_rows_are_presentations=True)
    if 'ASSESSMENT_cohort_id' not in result:GAPS.append({'run_id':rid,'reason':'Exact assessment membership not recovered','source':result['source']})
    for role in ['TRAIN','VALIDATION','CALIBRATION','META_FIT','ASSESSMENT']:
        result.setdefault(role+'_N',NR);result.setdefault(role+'_recording_N',NR);result.setdefault(role+'_cohort_id',NR)
    # No assumption that calibration/meta-fitting rows are independent of base OOF training pools.
    if result['TRAIN_cohort_id']!=NR and result['ASSESSMENT_cohort_id']!=NR:
        tr=next(c['keys'] for c in SETS.values() if c['cohort_id']==result['TRAIN_cohort_id']);te=next(c['keys'] for c in SETS.values() if c['cohort_id']==result['ASSESSMENT_cohort_id'])
        assert not set(tr)&set(te),(rid,'TRAIN/ASSESSMENT_OVERLAP')
    RUNS.append(result)


def ap_auc(y,p):
    order=np.argsort(-p,kind='stable');ys=y[order];ps=p[order];ends=np.r_[np.flatnonzero(np.diff(ps)!=0),len(ps)-1]
    tp=np.cumsum(ys)[ends];ap=float(np.sum(np.diff(np.r_[0,tp/y.sum()])*tp/(ends+1))) if y.sum() else None
    if y.sum() in [0,len(y)]:return ap,None
    asc=np.argsort(p,kind='stable');sp=p[asc];starts=np.r_[0,np.flatnonzero(np.diff(sp)!=0)+1];stops=np.r_[starts[1:],len(p)];rank=np.empty(len(p))
    for a,b in zip(starts,stops):rank[asc[a:b]]=(a+1+b)/2
    auc=float((rank[y==1].sum()-y.sum()*(y.sum()+1)/2)/(y.sum()*(len(y)-y.sum())))
    return ap,auc


def evaluation(study,model,source,keys,p=None,*,seed=NR,fold='pooled5',condition='clean',scope='OUTER HELD-OUT',label_values=None,contract='NATIVE FAILURE',note=''):
    keys=list(keys);assert len(keys)==len(set(keys)),(source,model,seed,fold,'DUPLICATE_EVAL_IDS')
    original_N=len(keys);y=np.array([BYKEY[k]['failure'] for k in keys],int)
    if label_values is not None:
        yy=np.asarray(label_values,int);assert len(yy)==len(keys)
        if not np.array_equal(y,yy):contract='NON-NATIVE/PERMUTED LABELS'
    if p is not None:
        p=np.asarray(p,float);assert p.shape==(len(keys),)
        mask=np.isfinite(p);keys=[k for k,ok in zip(keys,mask) if ok];y=y[mask];p=p[mask]
        assert not len(p) or ((p>=0)&(p<=1)).all(),(source,model,'INVALID_PROBABILITY_RANGE')
    c=register(keys,source)
    comparison_allowed=scope=='OUTER HELD-OUT' and contract=='NATIVE FAILURE' and len(keys)>0
    # A shared corruption name is insufficient to prove identical corrupted inputs.
    # Keep non-clean observations source-specific until draw/input identities are proven.
    observation_contract=condition if condition=='clean' else str(source)+'::'+condition
    comparison_id='MATCH_'+hash_lines([c['action_set_sha256'],c['label_map_sha256'],observation_contract,scope])[:16] if comparison_allowed else 'NOT PERMITTED'
    score=ap_auc(y,p) if p is not None and len(y)>0 and condition=='clean' and contract=='NATIVE FAILURE' else (None,None)
    prediction_hash=NR
    if p is not None:
        order=np.argsort(np.array(keys));prediction_hash=hashlib.sha256((c['action_set_sha256']+'\n').encode()+p[order].astype('<f8').tobytes()).hexdigest()
    eid='E'+str(len(EVALS)+1).zfill(6)
    if p is not None and condition=='clean' and comparison_allowed:
        for k,label,prob in zip(keys,y,p):SCORE_WRITER.writerow([eid,k,int(label),repr(float(prob))])
    EVALS.append({'evaluation_id':eid,'experiment_id':study,'model':model,'seed':seed,'fold':fold,
        'evaluation_scope':scope,'condition':condition,'cohort_id':c['cohort_id'],'action_set_sha256':c['action_set_sha256'],
        'label_map_sha256':c['label_map_sha256'],'N':c['N'],'failures':c['failures'],'recording_N':c['recording_N'],
        'expected_N':original_N,'nonfinite_prediction_N':original_N-c['N'],'label_contract':contract,
        'prediction_vector_sha256':prediction_hash,
        'matched_comparison_group':comparison_id,'direct_comparison_eligibility':'MATCHED COHORT NECESSARY; protocol limitations still apply' if comparison_allowed else 'NO',
        'AP_saved_probability_recomputation':score[0] if score[0] is not None else NR,'AUROC_saved_probability_recomputation':score[1] if score[1] is not None else NR,
        'prediction_source':str(source),'identity_evidence':note or 'ACTUAL PREDICTION IDS/EXPLICIT ROWS'})


def phase_evaluations(configs):
    pool=collections.defaultdict(list)
    for r in RUNS:
        if not r['experiment_id'].startswith('REASSEMBLE_PHASE1') and r['experiment_id']!='REASSEMBLE_100E_SINGLE_FIT':continue
        data=read(r['prediction_source']);data=data if isinstance(data,list) else data.get('rows',data.get('predictions'))
        ks=[key(v) for v in data];p=[v.get('p_visual',v.get('probability')) for v in data]
        scope='OUTER HELD-OUT' if r['split_role'] in ['outer_assessment','SELECTED_INNER_TRAINING_ASSESSED_ON_OUTER'] else 'INNER-OOF ASSESSMENT'
        evaluation(r['experiment_id'],r['model'],r['prediction_source'],ks,p,seed=r['model_seed'],fold=r['outer_fold_zero_based'],scope=scope)
        if scope=='OUTER HELD-OUT' and r['experiment_id']=='REASSEMBLE_PHASE1_C20':pool[r['model_seed']].extend(data)
    for seed,data in pool.items():evaluation('REASSEMBLE_PHASE1_C20','C_full_finetuned16','five completed outer prediction files',[key(v) for v in data],[v['p_visual'] for v in data],seed=seed)
    p=FOLLOW/'06_held_out_predictions/ALL_MODELS_IDENTICAL_OUTER_IDS.json';data=read(p);ks=[key(v) for v in data]
    for name in [k for k in data[0] if re.match(r'M[1-7]_',k)]:
        seed=42 if name.startswith(('M1_','M2_')) else 'sensor estimator0; original nested branch' if name.startswith('M3_') else 'visual42 / sensor0 / F2 estimator0' if name.startswith(('M4_','M5_')) else 'visual42 / sensor0'
        evaluation('CNN100_STATIC_SENSOR_F2',name,p,ks,[v[name] for v in data],seed=seed,fold=0)


def bank_evaluations():
    # Complete outer probability banks from every original/additional workflow; no features or weights loaded.
    paths=[]
    for root in ['runs/reassemble/20260927T154732Z-section1/predictions','runs/reassemble/20260927T175336Z-section1b/stacking',
                 'runs/reassemble/20260927T175336Z-section1b/sensor_controls/predictions','runs/reassemble/20260927T192852Z-section2/predictions',
                 'runs/reassemble/20260927T204649Z-modality-dropout/predictions','runs/reassemble/additional_improvements_executed']:
        for p in (REPO/root).rglob('*.npz'):
            s=str(p.relative_to(REPO))
            if any(t in p.parts for t in ['fits','branches','cache','corruptions','selected_checkpoint_replay','selected_short_state_replay']):continue
            if '/stacking/' in s and re.search(r'outer\d+_inner\d+',p.name):continue
            if '/sensor_controls/' in s or '/section1/' in s:
                if 'perm00' not in p.name:continue
            if '20260927T154732Z-section1' in s and 'perm00' not in p.name:continue
            if p.name.startswith(('A-CONSTANT_neutral','A-ADAPTIVE_neutral','A-CONSTANT_permuted','A-ADAPTIVE_permuted')):continue
            if '/boundary_aware_visual/' in s and '/predictions/' not in s and '/fusion/' not in s:continue
            paths.append(p)
    seeds=read('configs/reassemble/additional_improvements/execution.json').get('seeds',[20260927,20260928,20260929])
    original_seeds=read('runs/reassemble/20260927T192852Z-section2/config.json').get('seeds',[20260927,20260928,20260929])
    def exact_seed(source,model,fold):
        if '20260927T154732Z-section1' in source:
            exp='SECTION1';base=re.sub(r'_perm00(?:_fold\d+)?$','',model)
        elif '/stacking/' in source:exp='SECTION1B_F2';base='F2'
        else:return NR
        matches=[r for r in RUNS if r['experiment_id']==exp and r['model']==base and r['permutation']==0 and r['split_role']=='OUTER_ASSESSMENT'
                 and (fold is None or int(r['outer_fold_zero_based'])==fold)]
        values={str(r['outer_fold_zero_based']):r['model_seed'] for r in matches}
        return str(next(iter(values.values()))) if fold is not None and values else json.dumps(values,sort_keys=True) if values else 'N/A deterministic rule or source-specific branch; see run registry'
    for path in sorted(set(paths)):
        source=rel(path);m=re.search(r'(?:outer|_fold)(\d+)',path.name);fold=int(m[1]) if m else None
        try:
            with np.load(used(path),allow_pickle=False) as z:
                names=z.files
                indices=np.asarray(z['test_rows'] if 'test_rows' in names else z['rows'] if 'rows' in names else np.arange(len(CANON)) if fold is None else [BYKEY[k]['canonical_row'] for k in outer_parts(fold)[1]],int)
                if len(indices)==len(CANON):assert np.array_equal(indices,np.arange(len(CANON)))
                ks=keys_indices(indices);yy=z['y'] if 'y' in names else None
                if yy is not None and len(yy)!=len(ks):continue
                bank_label=path.stem
                study=source.split('/predictions')[0] if '/predictions' in source else '/'.join(Path(source).parts[:5])
                basecondition='clean'
                if 'modality-dropout' in source and path.stem!='clean':basecondition=path.stem
                conditions=z['names'].astype(str).tolist() if 'names' in names else None
                probability_names=[n for n in names if n=='p' or (n.endswith('_p') and not n.endswith('_seed_p'))]
                for col in probability_names:
                    arr=z[col]
                    if arr.ndim==1:
                        if len(arr)!=len(ks):continue
                        model=bank_label if col=='p' else col[:-2]
                        if model in ['oof','outer0','outer1','outer2','outer3','outer4'] and 'section1b' in source:model='F2_original'
                        evaluation(study,model,source,ks,arr,seed='seed-mean ensemble; nominal families '+str(original_seeds if 'section2' in source else seeds) if col[:-2]+'_seed_p' in names or 'seed_p' in names else exact_seed(source,model,fold),
                            fold=fold if fold is not None else 'pooled5',condition=basecondition,label_values=yy,
                            note='Saved explicit row indices' if 'test_rows' in names or 'rows' in names else 'Verified original cohort row order; saved fold vector checked below')
                        seedcol='seed_p' if col=='p' else col[:-2]+'_seed_p'
                        if seedcol in names:
                            sp=z[seedcol]
                            if sp.ndim==2 and sp.shape[1]==len(ks):
                                ss=original_seeds if 'section2' in source else seeds
                                for i,v in enumerate(sp):evaluation(study,model,source,ks,v,seed=ss[i] if i<len(ss) else f'seed_index{i}:NOT RECORDED',fold=fold if fold is not None else 'pooled5',condition=basecondition,label_values=yy)
                    elif arr.ndim==2 and conditions is not None and arr.shape==(len(conditions),len(ks)):
                        for condition,v in zip(conditions,arr):evaluation(study,bank_label,source,ks,v,seed=NR,fold=fold,condition=condition,label_values=yy)
                if 'fold' in names and len(ks)==len(CANON):
                    fv=z['fold'];assert np.array_equal(fv,np.array([r['outer_fold_zero_based'] for r in CANON]))
                    for col in probability_names:
                        arr=z[col]
                        if arr.ndim!=1:continue
                        model=bank_label if col=='p' else col[:-2]
                        if model=='oof' and 'section1b' in source:model='F2_original'
                        for k in range(5):
                            mask=fv==k;evaluation(study,model,source,[v for v,ok in zip(ks,mask) if ok],arr[mask],seed=exact_seed(source,model,k),fold=k,condition=basecondition,label_values=yy[mask] if yy is not None else None)
        except (KeyError,ValueError) as e:GAPS.append({'prediction_source':source,'reason':type(e).__name__+':'+str(e)[:160]})


def legacy_evaluations():
    roots=['00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning','00_experiments/frozen32_vs_finetuned32_fusion_diagnosis/results',
           '00_experiments/rt_detr_encoder_comparison/results/run_01','00_experiments/adaptive_fusion_robustness/results/run_01','00_experiments/fusion_noise_test/results/run_01',str(LEGACY)]
    pools=collections.defaultdict(dict);pool_sources=collections.defaultdict(set)
    for root in roots:
        for path in sorted((REPO/root).rglob('*.csv')):
            if any(s in str(path) for s in ['original_inputs','source_snapshot','provenance/interruption','reference_only','cache','changed_predictions']):continue
            noise_clean='fusion_noise_test' in root and 'model_selection/clean_predictions' in str(path)
            if path.name not in ['identified_assessment_predictions.csv','assessment_predictions.csv','identified_branch_predictions.csv','predictions.csv'] and not path.name.startswith('identified_outer_predictions') and not noise_clean:continue
            data=rows(path)
            if not data or not {'failure','recording_id','segment_id'}<=set(data[0]):continue
            cols=[c for c in data[0] if c.startswith('p_') or c=='probability']
            if not cols:continue
            fields=[c for c in ['condition','seed_family','fold_name','fold','family','level','repeat'] if c in data[0]]
            groups=collections.defaultdict(list)
            for row in data:groups[tuple(row[c] for c in fields)].append(row)
            for metadata,part in groups.items():
                info=dict(zip(fields,metadata));ks=[key(row) for row in part]
                scope='INNER-OOF ASSESSMENT' if 'inner_fold_' in str(path) or 'fusion_training' in str(path) else 'OUTER HELD-OUT'
                condition=info.get('family','clean')
                if condition!='clean':condition+=':'+info.get('level','')+':repeat'+info.get('repeat','0')
                fold=info.get('fold_name',info.get('fold',NR));seed=info.get('seed_family',NR)
                if fold==NR:
                    m=re.search(r'fold_(\d+)',str(path));fold=f'fold_{int(m[1]):02d}' if m else 'pooled5'
                if seed==NR:
                    m=re.search(r'seed_(\d+)',str(path))
                    if m:seed=int(m[1])
                if seed==NR and root.startswith('00_experiments/visual_backbone_one_day'):seed='role-dependent seed; see fit receipts'
                for col in cols:
                    try:p=[float(v[col]) if v[col] else float('nan') for v in part]
                    except ValueError:continue
                    model=info.get('condition',path.parent.parent.name)+'/'+col
                    evaluation(root,model,rel(path),ks,p,seed=seed,fold=fold,condition=condition,scope=scope)
                    if scope=='OUTER HELD-OUT' and (path.name in ['identified_assessment_predictions.csv','assessment_predictions.csv'] or path.name.startswith('identified_outer_predictions')):
                        # Keep exports, replay variants and source versions separate.
                        # Only fold-name variants of the same source layout can pool.
                        bundle=re.sub(r'fold_\d+', 'fold_ALL',rel(path))
                        pk=(root,model,str(seed),condition,bundle)
                        for k,prob in zip(ks,p):
                            if k in pools[pk]:assert pools[pk][k]==prob or (math.isnan(pools[pk][k]) and math.isnan(prob)),('CONFLICTING_POOLED_PROBABILITIES',pk,k)
                            pools[pk][k]=prob
                        pool_sources[pk].add(rel(path))
    for (root,model,seed,condition,bundle),values in pools.items():
        if len(values)==4530:
            evaluation(root,model,';'.join(sorted(pool_sources[(root,model,seed,condition,bundle)])),list(values),list(values.values()),seed=seed,fold='pooled5',condition=condition,note='Concatenation of existing identified outer predictions within one source-version layout; exact unique4530 canonical keys')


def reports():
    full=register([r['native_key'] for r in CANON]);small=register(outer_parts(0)[1]);rest=set(full['keys'])-set(small['keys'])
    assert set(small['keys'])<set(full['keys']);assert small['N']==753 and small['failures']==77 and small['recording_N']==26
    assert len(rest)==3777
    actual100=[r for r in RUNS if r['experiment_id']=='REASSEMBLE_100E_SINGLE_FIT'];assert len(actual100)==2
    assert all(r['ASSESSMENT_cohort_id']==small['cohort_id'] for r in actual100)
    selected=read(BASE/'26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_configuration/PHASE1_SELECTED_JOB.json')
    claimed=set(selected['prediction_recordings']);actual=set(small['recordings'])
    if claimed!=actual:CONFLICTS.append({'source':str(BASE/'26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_configuration/PHASE1_SELECTED_JOB.json'),
        'field':'prediction_recordings','stored_recording_count':len(claimed),'actual_recording_count_from_prediction_IDs':len(actual),
        'actual_minus_stored_recordings':sorted(actual-claimed),'stored_minus_actual_recordings':sorted(claimed-actual),
        'resolution':'Use actual prediction_sample_ids/outer_E_recordings and predict row indices; old list describes original920 inner assessment. Original file preserved.'})
    original_job=read(BASE/'26102026_evidence/PHASE1_FIT_PLAN.json')[2]
    if selected.get('validation_split_seed')!=original_job.get('validation_split_seed'):
        CONFLICTS.append({'source':str(BASE/'26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_configuration/PHASE1_SELECTED_JOB.json'),
            'field':'validation_split_seed','stored_value':selected.get('validation_split_seed'),'original_plan_value':original_job.get('validation_split_seed'),
            'training_and_validation_memberships_identical':selected['training']==original_job['training'] and selected['validation']==original_job['validation'],
            'resolution':'Preserve both seed declarations. Actual executed T/V IDs equal original job2; do not claim a newly sampled validation set.'})
    for r in actual100:
        assert r['TRAIN_N']==1752 and r['VALIDATION_N']==419 and r['CALIBRATION_N']==686
        rs=[set(next(c['keys'] for c in SETS.values() if c['cohort_id']==r[t+'_cohort_id'])) for t in ['TRAIN','VALIDATION','CALIBRATION','ASSESSMENT']]
        assert all(not a&b for a,b in itertools.combinations(rs,2))
        missing=set(full['keys'])-set.union(*rs)
        assert missing==set(keys_indices(selected['original_inner_prediction_indices'])) and len(missing)==920
    savedfold=[]
    for k in range(5):
        tr,te=outer_parts(k);tc=register(tr);ec=register(te)
        savedfold.append({'outer_fold_zero_based':k,'legacy_fold_name':f'fold_{k+1:02d}','train_N':tc['N'],'train_recording_N':tc['recording_N'],
            'held_out_N':ec['N'],'held_out_failures':ec['failures'],'held_out_recording_N':ec['recording_N'],'held_out_cohort_id':ec['cohort_id'],
            'held_out_recording_ids':ec['recordings'],'train_recording_ids':tc['recordings']})
    save_csv('ORIGINAL_OUTER_FOLDS.csv',savedfold)
    save_json('SMALLER_COHORT_SUBSET_PROOF.json',{'larger_cohort':{k:v for k,v in full.items() if k not in ['keys']},
        'smaller_cohort':{k:v for k,v in small.items() if k not in ['keys']},'strict_action_subset':True,'strict_recording_subset':True,
        'smaller_is_exact_original_outer_fold_zero':True,'unmatched_smaller_actions':[],'larger_minus_smaller_N':3777,
        'same_native_labels':True,'source_receipt_100_roles_verified':True,'920_is_disjoint_inner_holdout_not_another_test_cohort':True})
    save_csv('CANONICAL_ACTION_MANIFEST.csv',CANON)
    save_csv('SAMPLE_ID_ALIAS_MAP.csv',[{'sample_id':a,'native_key':k} for a,k in sorted(ALIASES.items())])
    save_csv('ALL_TRAINING_RUN_COHORTS.csv',RUNS)
    save_csv('ALL_EVALUATION_COHORTS.csv',EVALS)
    save_csv('METADATA_CONFLICTS.csv',CONFLICTS)
    save_csv('MISSING_IDENTITY_EVIDENCE.csv',GAPS)
    cohortrows=[{k:v for k,v in c.items() if k not in ['keys']} for c in SETS.values()]
    save_csv('COHORT_REGISTRY.csv',cohortrows)
    with (OUT/'COHORT_ACTION_MEMBERSHIP.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['cohort_id','native_key','canonical_row','recording_id','segment_id','failure'])
        for c in SETS.values():
            for k in c['keys']:
                r=BYKEY[k];w.writerow([c['cohort_id'],k,r['canonical_row'],r['recording_id'],r['segment_id'],r['failure']])
    summaries=[]
    for exp in sorted({r['experiment_id'] for r in RUNS}):
        rs=[r for r in RUNS if r['experiment_id']==exp];summaries.append({'experiment_id':exp,'fit_record_N':len(rs),
            'model_names':sorted({r['model'] for r in rs}),'model_seeds':sorted({str(r['model_seed']) for r in rs}),
            'seed_families':sorted({str(r['seed_family']) for r in rs}),'outer_folds':sorted({str(r['outer_fold_zero_based']) for r in rs}),
            'TRAIN_counts':sorted({str(r['TRAIN_N']) for r in rs}),'VALIDATION_counts':sorted({str(r['VALIDATION_N']) for r in rs}),
            'CALIBRATION_counts':sorted({str(r['CALIBRATION_N']) for r in rs}),'ASSESSMENT_counts':sorted({str(r['ASSESSMENT_N']) for r in rs}),
            'assessment_cohort_ids':sorted({r['ASSESSMENT_cohort_id'] for r in rs}),'identity_unresolved_records':sum(r['ASSESSMENT_cohort_id']==NR for r in rs)})
    save_csv('EXPERIMENT_COHORT_SPLIT_SEED_SUMMARY.csv',summaries)
    inference=[]
    for exp in sorted({e['experiment_id'] for e in EVALS}):
        es=[e for e in EVALS if e['experiment_id']==exp]
        inference.append({'experiment_id':exp,'saved_evaluation_records':len(es),
            'sample_counts':sorted({e['N'] for e in es}),
            'recording_counts':sorted({e['recording_N'] for e in es}),
            'seeds_as_recorded':sorted({str(e['seed']) for e in es}),
            'folds_as_recorded':sorted({str(e['fold']) for e in es}),
            'assessment_cohort_ids':sorted({e['cohort_id'] for e in es}),
            'source_paths':sorted({e['prediction_source'] for e in es})})
    save_csv('ALL_PREDICTION_WORKFLOW_SUMMARY.csv',inference)
    save_csv('UNRECORDED_SEED_FIELDS.csv',[{'run_id':r['run_id'],'experiment_id':r['experiment_id'],
        'field':'model_seed','value':NR,'source':r['source'],
        'interpretation':'No exact estimator RNG seed recovered in this adapter. Nominal families are separate fields; deterministic/reused models may not consume an RNG. Inspect preserved effective config and source.'}
        for r in RUNS if r['model_seed']==NR])
    group=collections.defaultdict(list)
    for e in EVALS:
        if e['matched_comparison_group']!='NOT PERMITTED':group[e['matched_comparison_group']].append(e)
    save_csv('MATCHED_COMPARISON_GROUPS.csv',[{'comparison_group':g,'cohort_id':es[0]['cohort_id'],'N':es[0]['N'],'recording_N':es[0]['recording_N'],
        'condition':es[0]['condition'],'evaluation_N':len(es),'models':sorted({e['experiment_id']+' / '+e['model'] for e in es}),
        'seeds':sorted({str(e['seed']) for e in es}),'policy':'Compare only within this group; training/selection differences and repeated-test exposure remain limitations.'} for g,es in group.items()])
    matched=[e for e in EVALS if e['condition']=='clean' and e['evaluation_scope']=='OUTER HELD-OUT' and e['cohort_id'] in [small['cohort_id'],full['cohort_id']]]
    save_csv('MATCHED_CLEAN_PERFORMANCE.csv',matched)
    aliases=collections.defaultdict(list)
    for e in EVALS:
        if e['prediction_vector_sha256']!=NR:aliases[(e['cohort_id'],e['condition'],e['prediction_vector_sha256'])].append(e)
    save_csv('IDENTICAL_PREDICTION_ALIASES.csv',[{'cohort_id':k[0],'condition':k[1],'prediction_vector_sha256':k[2],
        'evaluation_ids':[e['evaluation_id'] for e in es],'models':[e['experiment_id']+' / '+e['model'] for e in es],
        'note':'Identical saved scores are not additional independent result evidence.'} for k,es in aliases.items() if len(es)>1])
    # No O(E^2) pair list: cohort passports provide exact,lossless group membership for every evaluation.
    lines=['# REASSEMBLE cohort,split and seed reconciliation','',
        'The753-action evaluation is an exact strict subset of the4,530-action original cohort: original outer fold0 (legacy fold_01). All753 native recording/segment keys and labels match;there are77 failures across26 recordings. The larger cohort contains509 failures across148 recordings. The remaining3,777 actions are the original outer training pool.','',
        'The920 rows are a different,disjoint inner assessment bank inside that3,777-action pool. In the100-epoch pilot,the selected original inner-fit3 training recipe is retained (1,752 gradient-training,419 validation,686 calibration),but assessment is changed to the753 outer actions. Thus “fit3” does not mean “outer fold3”. The saved selected-job prediction_recordings field still lists28 inner-bank recordings while actual outer predictions cover26;this conflict is preserved in METADATA_CONFLICTS.csv. Actual IDs govern this reconciliation.','',
        '## Exact outer cohorts','', '| Original fold | Legacy name | Outer training actions | Held-out actions | Failures | Held-out recordings | Cohort ID |','|---|---|---|---|---|---|---|']
    for r in savedfold:lines.append('| '+' | '.join(str(r[k]) for k in ['outer_fold_zero_based','legacy_fold_name','train_N','held_out_N','held_out_failures','held_out_recording_N','held_out_cohort_id'])+' |')
    lines+=['','## Rules for direct comparisons','',
        'A direct descriptive performance comparison requires identical native action IDs,identical native labels,identical assessment role and the same corruption/observation condition. These are encoded in matched_comparison_group. Equal N alone is never evidence of equality. Pooled4,530-action AP must not be directly ranked against753-action AP;use matched fold0 results or separately report the pooled estimand. Inner validation,meta-training,permuted-label controls and diagnostic selected examples are not final held-out evaluations.','',
        'Within a matched group,model/seed differences can be described on those same actions. Different fitting rows,calibration/stacking banks,frame contracts,budgets or prior test-driven selection prevent an isolated causal attribution or a confirmatory superiority claim. AP/AUROC are recomputed only from existing probabilities;threshold-dependent metrics retain their original conventions in the historical audit and must not be mixed. No training or fitting occurred.','',
        '## Where to inspect identities','',
        '- [Every registered training run: exact role counts,seeds,folds and cohort IDs](ALL_TRAINING_RUN_COHORTS.csv).','- [Every experiment summary](EXPERIMENT_COHORT_SPLIT_SEED_SUMMARY.csv).','- [Every inspected saved evaluation and its matching passport](ALL_EVALUATION_COHORTS.csv).','- [Matched comparison groups](MATCHED_COMPARISON_GROUPS.csv).','- [Clean753/4,530-action performance,kept in separate cohort groups](MATCHED_CLEAN_PERFORMANCE.csv).','- [Every exact action membership](COHORT_ACTION_MEMBERSHIP.csv) and [recording lists](COHORT_REGISTRY.csv).','- [Canonical native keys](CANONICAL_ACTION_MANIFEST.csv) and [legacy sample-ID aliases](SAMPLE_ID_ALIAS_MAP.csv).','- [Subset proof](SMALLER_COHORT_SUBSET_PROOF.json),[metadata conflicts](METADATA_CONFLICTS.csv) and [unrecoverable identities](MISSING_IDENTITY_EVIDENCE.csv).','',
        'Row-index-only banks are linked to the original cohort after verifying its saved order and labels against the original source-manifest filter. Saved fit receipt IDs take precedence over stale human-readable recording summaries. Unknown identity evidence remains explicit;no sample/participant identity is invented. Every source path/hash is preserved.']
    (OUT/'README.md').write_text('\n'.join(lines)+'\n')
    save_json('RECONCILIATION_SUMMARY.json',{'original_cohort_N':4530,'original_recordings':148,'smaller_cohort_N':753,'smaller_recordings':26,'strict_subset_verified':True,
        'fit_records_reconciled':len(RUNS),'experiment_records':len(summaries),'evaluation_records':len(EVALS),'cohort_sets':len(SETS),
        'unresolved_identity_rows':len(GAPS),'metadata_conflicts':len(CONFLICTS),'matched_comparison_groups':len(group),
        'new_training':False,'new_fusion_fit':False,'new_feature_extraction':False,'used_source_files':len(USED)})


def main():
    global SCORE_FILE,SCORE_WRITER
    OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'RECONCILIATION_SUMMARY.json').exists() or '--refresh-working-output' in sys.argv,'Never overwrite a completed reconciliation'
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip();canonical()
    configs=read(AUDIT/'03_hyperparameter_configuration/EFFECTIVE_CONFIGURATIONS.json')
    configs=[r for r in configs if r['dataset']=='REASSEMBLE']
    for i,r in enumerate(configs):
        try:run_record(r)
        except Exception as e:
            save_json('FAILED_RUN_CONTEXT.json',{'run_id':r['run_id'],'error':str(e)});raise
        if (i+1)%1000==0:print('RUN_COHORTS',i+1,flush=True)
    SCORE_FILE=(OUT/'ALL_CLEAN_HELD_OUT_PREDICTIONS.csv').open('w',newline='')
    SCORE_WRITER=csv.writer(SCORE_FILE);SCORE_WRITER.writerow(['evaluation_id','native_key','failure','probability'])
    phase_evaluations(configs);bank_evaluations();legacy_evaluations();SCORE_FILE.close();reports()
    assert head==subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
    for r in USED.values():assert sha(r['path'])==r['sha256'],('SOURCE_CHANGED',r['path'])
    save_csv('SOURCE_PROVENANCE.csv',list(USED.values()))
    save_json('RUN_PROVENANCE.json',{'utc':dt.datetime.now(dt.timezone.utc).isoformat(),'git_head':head,'command':sys.argv,'training':False,'writes':'new reconciliation folder only','original_sources_hash_preserved':True})
    print(json.dumps(read(OUT/'RECONCILIATION_SUMMARY.json')),flush=True)

if __name__=='__main__':main()
