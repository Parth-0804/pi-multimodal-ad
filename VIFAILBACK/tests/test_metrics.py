import numpy as np
from vifailback.metrics import metrics,independent_check,paired_task_bootstrap


def test_co_primary_metrics_include_minority_and_tied_predictions():
    y=np.asarray([0,1,1,0,1,1]);p=np.asarray([.2,.2,.8,.5,.8,.5])
    report=metrics(y,p);assert independent_check(y,p,report)
    chance=metrics(y,np.ones(6)*y.mean())
    assert np.isclose(chance['AP_failure'],4/6) and np.isclose(chance['AP_success'],2/6)
    assert np.isclose(chance['macro_AP'],.5)


def test_paired_uncertainty_is_zero_for_identical_models():
    y=np.asarray([0,1]*8);p=np.asarray([.2,.8]*8)
    result=paired_task_bootstrap(y,p,p,np.repeat(np.arange(4),4),np.tile([42,42,123,123],4),repeats=20)
    assert result['macro_AP_A_minus_B']==0 and result['task_bootstrap_95_percentile']==[0,0]


def test_weighted_task_bootstrap_matches_explicit_episode_replication():
    from vifailback.metrics import independent_ap
    y=np.asarray([0,1]*4);a=np.asarray([.2,.7,.3,.7,.5,.6,.1,.4]);b=np.asarray([.4,.8,.2,.6,.7,.3,.1,.9])
    g=np.repeat(np.arange(4),2);s=np.ones(8,int)*42;seed=123
    actual=paired_task_bootstrap(y,a,b,g,s,repeats=25,seed=seed)
    rng=np.random.default_rng(seed);deltas=[]
    def macro(target,p):return (independent_ap(target,p)+independent_ap(1-target,1-p))/2
    for _ in range(25):
        draw=rng.integers(0,4,4);ix=np.concatenate([np.flatnonzero(g==group) for group in draw])
        deltas.append(macro(y[ix],a[ix])-macro(y[ix],b[ix]))
    assert np.allclose(actual['task_bootstrap_95_percentile'],np.quantile(deltas,[.025,.975]),atol=1e-12)
