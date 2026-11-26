import pytest
from vifailback.splits import plans,require_oof


def rows():
    return [{'episode_index':2*g+y,'canonical_task_id':g,'label':y} for g in range(33) for y in [0,1]]


def test_assignment_label_blind_and_all_tasks_held_out_once():
    a=plans(rows(),42);b=plans([{**r,'label':1-r['label']} for r in rows()],42)
    assert [j['ids'] for j in a]==[j['ids'] for j in b]
    assert sorted(e for j in a if j['inner']==-1 for e in j['ids']['A'])==list(range(66))
    for outer in range(3):
        oof=[{'fit_id':j['id'],'episode_index':e} for j in a if j['outer']==outer and j['inner']>=0 for e in j['ids']['A']]
        require_oof(a,outer,oof)
        with pytest.raises(AssertionError):require_oof(a,outer,oof+oof[:1])


def test_in_sample_record_rejected_by_oof_validator():
    jobs=plans(rows(),42);fit=next(j for j in jobs if j['outer']==0 and j['inner']==0)
    with pytest.raises(AssertionError):
        require_oof(jobs,0,[{'fit_id':fit['id'],'episode_index':fit['ids']['T'][0]}])
