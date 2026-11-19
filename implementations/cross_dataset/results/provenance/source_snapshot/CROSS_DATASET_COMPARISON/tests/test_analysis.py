"""Exact cluster-bootstrap AP against the independently implemented metric."""
import sys
import numpy as np
from sklearn.metrics import average_precision_score
sys.path.insert(0,'CROSS_DATASET_COMPARISON/src')
from external_eval.analysis import weighted_bootstrap_ap
from external_eval.analysis import read_predictions
from external_eval.evaluate import metrics
from external_eval.io import write_json,sha
import pandas as pd


def test_cluster_multiplicities_and_tied_thresholds_match_sklearn():
    y=np.array([0,1,0,1,1,0]);p=np.array([.2,.2,.8,.8,.9,.1]);groups=np.array([0,0,1,1,2,2])
    draws=np.array([[1,1,1],[3,0,0],[0,2,1],[0,0,3],[2,1,0]])
    actual=weighted_bootstrap_ap(y,p,groups,draws)
    expected=[average_precision_score(y,p,sample_weight=row[groups]) for row in draws]
    np.testing.assert_allclose(actual,expected,rtol=0,atol=1e-15)


def test_near_one_probabilities_reproduce_log_loss_after_csv_round_trip(tmp_path):
    # One ulp of CSV parser drift is amplified by log(1-p); this fixture needs
    # no dataset input or training and failed under the former default parser.
    p=np.array([0.9999999933950987,.5],np.float64);y=np.array([0,1])
    root=tmp_path/'06_evaluation_results';root.mkdir()
    pred=root/'synthetic_predictions.csv';saved=root/'synthetic_metrics.csv'
    frame=pd.DataFrame({'sample_id':['synthetic0','synthetic1'],'target':y,'probability':p,'model':'visual',
        'role':'test','corruption':'clean','initialization':'P','protocol':'synthetic','seed':42})
    frame.to_csv(pred,index=False);expected=metrics(y,p)
    pd.DataFrame([{'role':'test','corruption':'clean','model':'visual',**expected}]).to_csv(saved,index=False)
    write_json(root/'P_EVALUATION_COMPLETE.json',{'cases':[{'case_id':'synthetic_precision_case','predictions':str(pred),'metrics':str(saved),
        'output_hashes':{str(pred):sha(pred),str(saved):sha(saved)}}]})
    actual,pooled,checks,_=read_predictions(tmp_path)
    np.testing.assert_array_equal(actual.probability,p)
    assert pooled.iloc[0].log_loss==expected['log_loss'] and len(checks)==1
