"""Deterministic nested recording-disjoint assignments; no model fitting."""
import hashlib
import json
import numpy as np
from sklearn.model_selection import StratifiedGroupKFold

ALLOWED_PREDICTOR_FIELDS = frozenset({'visual', 'sensor', 'audio', 'action', 'availability', 'quality'})
FORBIDDEN_PREDICTOR_FIELDS = frozenset({'recording_id','filename','start','end','timestamp','segment_id','text','object_annotation','success','failure'})


def validate_predictor_fields(fields):
    if not set(fields) <= ALLOWED_PREDICTOR_FIELDS:
        raise ValueError('Predictor schema includes unapproved metadata')


def nested_assignments(frame, outer=5, inner=4, seed=20260927):
    y=frame['failure'].to_numpy(dtype=int);groups=frame['recording_id'].to_numpy()
    if len(set(groups[y==1]))<10 or len(set(groups[y==0]))<10:
        raise ValueError('Insufficient independent class-bearing recordings')
    splitter=StratifiedGroupKFold(outer,shuffle=True,random_state=seed)
    records=[]
    for outer_id,(train,test) in enumerate(splitter.split(np.zeros(len(y)),y,groups)):
        if set(groups[train]) & set(groups[test]):raise AssertionError('Outer leakage')
        if len(set(y[test]))!=2:raise ValueError('Outer assessment lacks a class')
        inner_rows=[]
        for inner_id,(itr,iva) in enumerate(StratifiedGroupKFold(inner,shuffle=True,random_state=seed+outer_id+1).split(np.zeros(len(train)),y[train],groups[train])):
            itrain,ival=train[itr],train[iva]
            if set(groups[itrain])&set(groups[ival]):raise AssertionError('Inner leakage')
            if len(set(y[itrain]))!=2 or len(set(y[ival]))!=2:raise ValueError('Inner partition lacks a class')
            inner_rows.append({'fold':inner_id,'train_recordings':sorted(set(groups[itrain])),'validation_recordings':sorted(set(groups[ival])),'train_failures':int(y[itrain].sum()),'validation_failures':int(y[ival].sum())})
        records.append({'fold':outer_id,'train_recordings':sorted(set(groups[train])),'test_recordings':sorted(set(groups[test])),'train_segments':len(train),'test_segments':len(test),'test_failures':int(y[test].sum()),'inner':inner_rows})
    result={'grouping':'source HDF5 recording','seed':seed,'outer_folds':outer,'inner_folds':inner,'folds':records}
    result['sha256']=hashlib.sha256(json.dumps(result,sort_keys=True).encode()).hexdigest()
    return result
