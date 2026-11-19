"""Bounded REASSEMBLE saved-result consistency; no source training or raw replay."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.special import expit
from sklearn.metrics import average_precision_score,roc_auc_score
from external_eval.io import sha,write_json


def audit():
    s1=Path('runs/reassemble/20260927T154732Z-section1');s1b=Path('runs/reassemble/20260927T175336Z-section1b')
    used=[]
    def read(path):
        used.append(path);return json.loads(path.read_text())
    def array(path):
        used.append(path)
        with np.load(path,allow_pickle=False) as z:return {k:z[k] for k in z.files}
    frame_path=s1/'cohort.parquet';used.append(frame_path);frame=pd.read_parquet(frame_path)
    reference=read(s1/'assessment/results.json');fusion_reference=read(s1b/'assessment/results.json')
    rows=[]
    for name in ['sensor_statistics','rtdetr','patchtst']:
        d=array(s1/'predictions'/(name+'_perm00.npz'));ap=float(average_precision_score(d['y'],d['p']));auc=float(roc_auc_score(d['y'],d['p']))
        if not np.array_equal(d['y'],frame.failure):raise ValueError('Source saved target/cohort mismatch')
        if abs(ap-reference['metrics'][name]['AUPRC']['estimate'])>1e-12 or abs(auc-reference['metrics'][name]['AUROC']['estimate'])>1e-12:raise ValueError('Source saved discrimination differs')
        rows.append({'model':name,'AP':ap,'AUROC':auc})
    d=array(s1b/'stacking/oof.npz');ap=float(average_precision_score(d['y'],d['p']));auc=float(roc_auc_score(d['y'],d['p']))
    if not np.array_equal(d['y'],frame.failure) or abs(ap-fusion_reference['metrics']['minimal_late_fusion']['AUPRC']['estimate'])>1e-12:raise ValueError('Source F2 saved result differs')
    rows.append({'model':'F2','AP':ap,'AUROC':auc})
    splits=read(s1/'nested_splits.json');seen=set();maximum=0.
    for fold in splits['folds']:
        k=fold['fold'];train=set(fold['train_recordings']);test=set(fold['test_recordings'])
        if train&test or seen&test or train|test!=set(frame.recording_id):raise ValueError('Source recording partition invalid')
        if set(frame.loc[d['fold']==k,'recording_id'])!=test:raise ValueError('Source prediction role mismatch')
        seen|=test;bank=array(s1b/'stacking'/f'outer{k}.npz');fitted=read(s1b/'stacking'/f'outer{k}.json')['stacker']
        predicted=expit(bank['test_branch_probabilities']@np.asarray(fitted['coefficient'])+fitted['intercept'])
        maximum=max(maximum,float(np.max(abs(predicted-bank['p']))))
    if maximum>1e-12 or seen!=set(frame.recording_id):raise ValueError('Source saved F2 arithmetic mismatch')
    out={'scope':'Saved prediction/label/cohort/outer-group/metric/coefficient consistency only; no new source training, raw label binding or CNN replay.',
        'examples':len(frame),'positive':int(frame.failure.sum()),'recording_groups':frame.recording_id.nunique(),
        'positive_prevalence':float(frame.failure.mean()),'outer_folds':len(splits['folds']),
        'models':rows,'F2_saved_coefficient_replay_max_abs_difference':maximum,
        'input_hashes':{str(p):sha(p) for p in used},
        'prior_broader_audit':'MILLING DATASET/runs/20261027T011419561081Z-stage5-validated/MSM_FINAL_EVIDENCE_REVIEW.md'}
    write_json(Path('CROSS_DATASET_COMPARISON/provenance/REASSEMBLE_saved_result_consistency.json'),out)
    return out
