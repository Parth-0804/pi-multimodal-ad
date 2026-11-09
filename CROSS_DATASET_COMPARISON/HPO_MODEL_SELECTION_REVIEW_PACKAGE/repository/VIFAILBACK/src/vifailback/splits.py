"""Label-blind hash assignment with task-disjoint T/V/C/assessment lineage."""
from collections import Counter
import numpy as np

from .common import PROJECT, config, read, sha, signature, write
from .cohort import finalize, folder


def ordered(groups, seed, scope):
    return sorted(set(groups),key=lambda g:signature([seed,scope,int(g)]))


def plans(rows, seed, outer_folds=3, inner_folds=3):
    groups={r['canonical_task_id'] for r in rows}
    assignment={g:i%outer_folds for i,g in enumerate(ordered(groups,seed,'outer'))}
    jobs=[]
    for outer in range(outer_folds):
        test={g for g in groups if assignment[g]==outer}; pool=groups-test
        inner={g:i%inner_folds for i,g in enumerate(ordered(pool,seed,f'inner{outer}'))}
        for fold in range(-1,inner_folds):
            assessment=test if fold==-1 else {g for g in pool if inner[g]==fold}
            training=pool if fold==-1 else pool-assessment
            sequence=ordered(training,seed,f'TVC{outer}:{fold}')
            n=len(sequence); assert n>=10
            a=round(n*.6);b=round(n*.8)
            sets={'T':set(sequence[:a]),'V':set(sequence[a:b]),'C':set(sequence[b:]),'A':assessment}
            assert set.union(*sets.values())==(pool|test if fold==-1 else pool)
            assert all(not x&y for i,x in enumerate(sets.values()) for y in list(sets.values())[i+1:])
            ids={part:[r['episode_index'] for r in rows if r['canonical_task_id'] in gs] for part,gs in sets.items()}
            counts={part:dict(Counter(r['label'] for r in rows if r['canonical_task_id'] in gs)) for part,gs in sets.items()}
            assert all(set(count)=={0,1} for count in counts.values()),'SINGLE_CLASS_PARTITION'
            jobs.append({'id':f'outer{outer}_'+('final' if fold==-1 else f'inner{fold}'),
                         'outer':outer,'inner':fold,'groups':{k:sorted(v) for k,v in sets.items()},
                         'ids':ids,'class_counts':counts})
    return jobs


def prepare(c=None):
    c=c or config(); out=PROJECT/'04_evaluation_splits/train_validation_test'/c['run_id']
    if (out/'COMPLETE.json').exists():
        assert sha(out/'fit_partitions.json')==read(out/'COMPLETE.json')['sha256']
        return read(out/'fit_partitions.json')
    rows=finalize(c); result=plans(rows,c['split_seed'],c['outer_folds'],c['inner_folds'])
    for outer in range(c['outer_folds']):
        fits=[j for j in result if j['outer']==outer]; final=next(j for j in fits if j['inner']==-1)
        oof=[e for j in fits if j['inner']>=0 for e in j['ids']['A']]
        assert len(oof)==len(set(oof))
        assert set(oof)==set(final['ids']['T']+final['ids']['V']+final['ids']['C'])
        assert not set(oof)&set(final['ids']['A'])
    write(out/'fit_partitions.json',result)
    write(out/'COMPLETE.json',{'sha256':sha(out/'fit_partitions.json'),'eligible_sha256':sha(folder(c)/'eligible.json'),
                              'jobs_per_seed_and_condition':len(result),'seeds':c['seeds'],
                              'grouping':'canonical task','labels_used_to_assign_groups':False,
                              'session_independence':'UNVERIFIED'})
    return result


def require_oof(jobs, outer, rows):
    """Validate each meta-training record against the exact branch fitting partition."""
    lookup={j['id']:j for j in jobs if j['outer']==outer and j['inner']>=0}
    seen=set()
    for row in rows:
        fit=lookup[row['fit_id']];eid=int(row['episode_index'])
        assert eid in fit['ids']['A'] and eid not in sum([fit['ids'][p] for p in ['T','V','C']],[])
        assert eid not in seen;seen.add(eid)
    expected={e for j in lookup.values() for e in j['ids']['A']}
    assert seen==expected,'INCOMPLETE_OR_CONTAMINATED_OOF'
