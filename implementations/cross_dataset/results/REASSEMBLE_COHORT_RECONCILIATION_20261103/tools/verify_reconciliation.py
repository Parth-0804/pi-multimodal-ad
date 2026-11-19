"""Independent standard-library checks of exported identities and saved scores."""
from pathlib import Path
import collections
import csv
import hashlib
import itertools
import json
import math
import struct
import sys
import time

csv.field_size_limit(256*1024**2)

def verify(root):
    root=Path(root);checks=[];started=time.monotonic()
    def rows(name):
        with (root/name).open(newline='') as f:return list(csv.DictReader(f))
    def digest(v):return hashlib.sha256(('\n'.join(v)+'\n').encode()).hexdigest()
    canon=rows('CANONICAL_ACTION_MANIFEST.csv');native={r['native_key']:r for r in canon}
    assert len(canon)==len(native)==4530
    assert len({r['recording_id'] for r in canon})==148
    assert sum(int(r['failure']) for r in canon)==509
    checks.append('canonical4530 unique native actions, labels and148 recordings')
    cs={r['cohort_id']:r for r in rows('COHORT_REGISTRY.csv')};members=collections.defaultdict(set)
    with (root/'COHORT_ACTION_MEMBERSHIP.csv').open(newline='') as f:
        for r in csv.DictReader(f):
            k=r['native_key'];assert k in native;assert r['failure']==native[k]['failure']
            assert r['recording_id']==native[k]['recording_id'];assert k not in members[r['cohort_id']]
            members[r['cohort_id']].add(k)
    for cid,c in cs.items():
        keys=sorted(members[cid]);assert len(keys)==int(c['N'])
        assert digest(keys)==c['action_set_sha256']
        assert digest([k+'\t'+native[k]['failure'] for k in keys])==c['label_map_sha256']
        assert sorted({native[k]['recording_id'] for k in keys})==json.loads(c['recordings'])
    checks.append('all cohort action hashes, labels, counts and recording lists')
    folds=rows('ORIGINAL_OUTER_FOLDS.csv');tests=[members[f['held_out_cohort_id']] for f in folds]
    assert [len(v) for v in tests]==[753,964,1037,906,870]
    assert set.union(*tests)==set(native)
    for a,b in itertools.combinations(tests,2):
        assert not a&b
        assert not {native[k]['recording_id'] for k in a}&{native[k]['recording_id'] for k in b}
    proof=json.loads((root/'SMALLER_COHORT_SUBSET_PROOF.json').read_text())
    assert tests[0]<set(native);assert len(tests[0])==753
    assert len({native[k]['recording_id'] for k in tests[0]})==26
    assert sum(int(native[k]['failure']) for k in tests[0])==77
    assert proof['strict_action_subset'] and proof['same_native_labels']
    checks.append('five recording-disjoint outer folds partition all4530; exact753 subset')
    runs=rows('ALL_TRAINING_RUN_COHORTS.csv');assert len(runs)==6894
    assert all(r['ASSESSMENT_cohort_id'] in cs for r in runs)
    for r in runs:
        for role in ['TRAIN','VALIDATION','CALIBRATION','META_FIT','ASSESSMENT']:
            cid=r[role+'_cohort_id']
            if cid in cs:assert int(r[role+'_N'])==len(members[cid])
        if r['TRAIN_cohort_id'] in cs:
            a,b=members[r['TRAIN_cohort_id']],members[r['ASSESSMENT_cohort_id']]
            assert not a&b,(r['run_id'],'train/assessment action leakage')
            assert not {native[k]['recording_id'] for k in a}&{native[k]['recording_id'] for k in b},r['run_id']
    checks.append('all6894 run assessment identities and recorded role counts; train/test recording separation')
    selected=[r for r in runs if r['experiment_id']=='REASSEMBLE_100E_SINGLE_FIT'];assert len(selected)==2
    c20=[r for r in runs if r['experiment_id']=='REASSEMBLE_PHASE1_C20'];assert len(c20)==25
    inner=next(r for r in c20 if r['job_index']=='2')
    outer=next(r for r in c20 if r['job_index']=='4')
    for r in selected:
        assert [int(r[k+'_N']) for k in ['TRAIN','VALIDATION','CALIBRATION','ASSESSMENT']]==[1752,419,686,753]
        assert r['validation_partition_seed']==r['validation_partition_seed_in_original_plan']=='20261028'
        assert all(r[role+'_cohort_id']==inner[role+'_cohort_id'] for role in ['TRAIN','VALIDATION','CALIBRATION'])
        assert r['ASSESSMENT_cohort_id']==outer['ASSESSMENT_cohort_id']
        assert not members[inner['ASSESSMENT_cohort_id']]&members[r['ASSESSMENT_cohort_id']]
    assert inner['ASSESSMENT_N']=='920' and outer['ASSESSMENT_N']=='753'
    conflict=rows('METADATA_CONFLICTS.csv');assert len(conflict)==1
    assert conflict[0]['stored_recording_count']=='28' and conflict[0]['actual_recording_count_from_prediction_IDs']=='26'
    checks.append('selected inner fit3 vs outer identities;100-epoch T/V/C conservation; stale recording metadata flagged')
    es={e['evaluation_id']:e for e in rows('ALL_EVALUATION_COHORTS.csv')};groups=collections.defaultdict(list)
    for e in es.values():
        assert int(e['N'])==len(members[e['cohort_id']])
        if e['matched_comparison_group']!='NOT PERMITTED':
            assert e['evaluation_scope']=='OUTER HELD-OUT' and e['label_contract']=='NATIVE FAILURE'
            groups[e['matched_comparison_group']].append(e)
    for g,vs in groups.items():
        assert len({(v['action_set_sha256'],v['label_map_sha256'],v['condition'],v['evaluation_scope']) for v in vs})==1
        if vs[0]['condition']!='clean':assert len({v['prediction_source'] for v in vs})==1
    matrix=rows('COMPARABILITY_MATRIX.csv')
    for r in matrix:
        a,b=es[r['left_evaluation_id']],es[r['right_evaluation_id']]
        same=a['matched_comparison_group']==b['matched_comparison_group'] and a['matched_comparison_group']!='NOT PERMITTED'
        assert (r['direct_descriptive_comparison_permitted']=='True')==same
        if a['N']!=b['N']:assert not same
    assert any(r['left_N']=='4530' and r['right_N']=='753' and r['direct_descriptive_comparison_permitted']=='False' for r in matrix)
    checks.append('matching requires exact action/label/assessment/observation identity;753 vs4530 comparisons rejected')
    aliases=rows('SAMPLE_ID_ALIAS_MAP.csv')
    assert len({r['sample_id'] for r in aliases})==len(aliases)
    assert all(r['native_key'] in native for r in aliases)
    checks.append('hashed sample-ID aliases map unambiguously to native actions')
    scores=collections.defaultdict(list);n=0
    with (root/'ALL_CLEAN_HELD_OUT_PREDICTIONS.csv').open(newline='') as f:
        for r in csv.DictReader(f):
            eid,k=r['evaluation_id'],r['native_key'];e=es[eid]
            assert k in members[e['cohort_id']] and r['failure']==native[k]['failure']
            p=float(r['probability']);assert math.isfinite(p) and 0<=p<=1
            scores[eid].append((k,p));n+=1
    for eid,vs in scores.items():
        e=es[eid];vs.sort();assert len(vs)==int(e['N'])
        assert len({k for k,p in vs})==len(vs)
        h=hashlib.sha256((e['action_set_sha256']+'\n').encode())
        for k,p in vs:h.update(struct.pack('<d',p))
        assert h.hexdigest()==e['prediction_vector_sha256'],eid
    assert all(eid in scores for eid,e in es.items() if e['condition']=='clean' and e['matched_comparison_group']!='NOT PERMITTED')
    checks.append('all exported clean probabilities retain exact vector hashes, IDs and labels')
    result={'passed':True,'checks':checks,'canonical_actions':len(native),'fit_records':len(runs),
        'evaluations':len(es),'exact_cohort_sets':len(cs),'clean_prediction_rows_verified':n,
        'clean_prediction_vectors_verified':len(scores),'explicit_comparability_rows_verified':len(matrix),
        'model_seed_fields_unresolved':len(rows('UNRECORDED_SEED_FIELDS.csv')),'elapsed_seconds':round(time.monotonic()-started,3),
        'training_or_inference_run':False}
    return result

if __name__=='__main__':
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
    result=verify(root);print(json.dumps(result,indent=2))
