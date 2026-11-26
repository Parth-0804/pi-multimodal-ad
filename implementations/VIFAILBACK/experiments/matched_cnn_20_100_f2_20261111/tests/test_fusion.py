"""Meaningful synthetic metric, leakage and static F2 regression checks."""
import inspect
import numpy as np
import pytest
from scipy.special import expit
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from matched_vifailback.fusion_evaluation import (
    fitted_f2, f2_probability, checked_records, verify_meta_isolation,
    vector_identity, weighted_ap_kernel, weighted_ap, paired_uncertainty,
)
from vifailback.metrics import metrics, independent_check


def test_f2_original_probability_equation_and_regularization():
    x = np.array([[.1,.3],[.2,.8],[.7,.2],[.8,.9],[.3,.2],[.6,.7],[.05,.1],[.9,.8]])
    y = np.array([0,1,0,1,0,1,0,1])
    got = fitted_f2(x, y)
    reference = LogisticRegression(C=1., penalty='l2', class_weight=None,
                                   solver='lbfgs', max_iter=2000, random_state=42).fit(x,y)
    np.testing.assert_allclose(got['coefficient'],reference.coef_[0],rtol=0,atol=1e-12)
    np.testing.assert_allclose(f2_probability(x,got),reference.predict_proba(x)[:,1],rtol=0,atol=1e-12)
    np.testing.assert_allclose(f2_probability(x,got),expit(x@np.array(got['coefficient'])+got['intercept']))
    assert not got['postfusion_calibration']
    assert 'outer' not in str(inspect.signature(fitted_f2))


def test_f2_rejects_logits_and_single_class_bank():
    with pytest.raises(ValueError, match='probabilities'):
        fitted_f2([[2,-1],[0,1]], [0,1])
    with pytest.raises(ValueError, match='both native classes'):
        fitted_f2([[.2,.3],[.8,.9]], [1,1])


def lookup():
    return {i:{'label':i%2,'canonical_task_id':i//2} for i in range(12)}


def test_prediction_ids_labels_order_and_bitwise_sensor_identity():
    context=lookup(); rows=[{'episode_index':i,'label':i%2,'probability':.1+i/20,'fit_id':'inner0'} for i in [3,2]]
    result=checked_records(rows,[2,3],context,'probability','inner0')
    assert [r['episode_index'] for r in result]==[2,3]
    assert vector_identity([3,2],[.7,.2])==vector_identity([2,3],[.2,.7])
    assert vector_identity([2,3],[.2,.7])!=vector_identity([2,3],[.2,np.nextafter(.7,1)])
    with pytest.raises(ValueError,match='Duplicate'):
        checked_records(rows+rows,[2,3],context,'probability')
    wrong=[{**r,'label':1-r['label']} for r in rows]
    with pytest.raises(ValueError,match='Native label'):
        checked_records(wrong,[2,3],context,'probability')


def test_meta_bank_excludes_training_validation_calibration_and_outer_tasks():
    context=lookup(); job={'ids':{'T':[0,1],'V':[2,3],'C':[4,5],'A':[6,7]}}
    result=verify_meta_isolation(job,[6,7],[8,9],context)
    assert result['passed'] and result['meta_N']==2
    for key in ['T','V','C']:
        bad={'ids':{k:list(v) for k,v in job['ids'].items()}}
        bad['ids'][key].append(6)
        with pytest.raises(ValueError,match='contaminated'):
            verify_meta_isolation(bad,[6,7],[8,9],context)
    with pytest.raises(ValueError,match='overlap'):
        verify_meta_isolation(job,[6,7],[7,8],context)
    context[8]['canonical_task_id']=context[6]['canonical_task_id']
    with pytest.raises(ValueError,match='task-group'):
        verify_meta_isolation(job,[6,7],[8,9],context)


def test_macro_ap_both_classes_and_independent_reconstruction():
    y=np.array([1,1,1,1,0,0]);p=np.array([.9,.6,.6,.1,.6,.2])
    value=metrics(y,p)
    assert value['macro_AP']==pytest.approx((average_precision_score(y,p)+average_precision_score(1-y,1-p))/2)
    assert value['macro_AP']!=pytest.approx(value['AP_failure'])
    assert independent_check(y,p,value)


def test_weighted_ap_handles_ties_and_zero_sampled_groups():
    y=np.array([0,1,1,0,1,0]);p=np.array([.2,.8,.8,.6,.6,.2]);gi=np.array([0,0,1,1,2,2])
    kernel=weighted_ap_kernel(y,p,gi)
    for counts in [np.array([1,1,1]),np.array([2,0,1]),np.array([0,3,0])]:
        ids=np.repeat(np.arange(len(y)),counts[gi])
        assert weighted_ap(kernel,counts)==pytest.approx(average_precision_score(y[ids],p[ids]),abs=1e-12)


def test_task_bootstrap_is_paired_and_not_equivalence():
    y=np.array([0,1,0,1,0,1,0,1]);p=np.array([.2,.8,.6,.4,.3,.9,.4,.7]);tasks=np.repeat(np.arange(4),2)
    out=paired_uncertainty(y,p,p,tasks,repeats=40,seed=7)
    assert out['valid']==40 and out['task_N']==4
    assert out['macro_AP']['difference']==0
    assert out['macro_AP']['lower95']==out['macro_AP']['upper95']==0
    assert out['macro_AP']['interpretation']=='inconclusive; not equivalence'
    assert out==paired_uncertainty(y,p,p,tasks,repeats=40,seed=7)


def test_matched_sensor_rejects_meta_changes_even_when_outer_matches():
    from matched_vifailback.fusion_evaluation import verify_matched_sensor
    meta=[{'episode_index':1,'sensor_probability':.2},{'episode_index':2,'sensor_probability':.7}]
    outer=[{'episode_index':3,'sensor_LR':.8}]
    assert verify_matched_sensor(meta, list(reversed(meta)), outer, outer)
    changed=[dict(meta[0],sensor_probability=.3),meta[1]]
    with pytest.raises(ValueError,match='meta sensor'):
        verify_matched_sensor(meta,changed,outer,outer)
    with pytest.raises(ValueError,match='outer sensor'):
        verify_matched_sensor(meta,meta,outer,[dict(outer[0],episode_index=4)])


def test_calibration_ranking_records_sign_reversal():
    from matched_vifailback.fusion_evaluation import ranking_diagnostic
    y=[0,0,1,1];raw=[-2.,-1.,1.,2.]
    rows=[{'label':a,'raw_visual':b,'visual':float(expit(-b))} for a,b in zip(y,raw)]
    out=ranking_diagnostic(rows)
    assert out['score_spearman']==pytest.approx(-1)
    assert out['raw_macro_AP']==1
    assert out['calibrated_macro_AP']<out['raw_macro_AP']
