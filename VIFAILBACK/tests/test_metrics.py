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
