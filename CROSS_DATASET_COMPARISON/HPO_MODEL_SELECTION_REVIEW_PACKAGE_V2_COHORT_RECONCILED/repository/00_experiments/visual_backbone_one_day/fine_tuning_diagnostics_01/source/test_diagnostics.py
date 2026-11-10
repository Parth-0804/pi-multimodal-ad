"""Small synthetic checks of nontrivial diagnostic calculations; no dataset fixtures."""
import unittest
import numpy as np
import pandas as pd
from scipy.special import expit, logit
from sklearn.metrics import average_precision_score
from analyse_saved_results import ap_contributions, top_mask


class DiagnosticsTests(unittest.TestCase):
    def test_perfect_and_reverse_ranking(self):
        np.testing.assert_allclose(ap_contributions([1,0,1],[.9,.5,.1]),[.5,0,1/3])
        np.testing.assert_allclose(ap_contributions([0,0,1],[.9,.5,.1]),[0,0,1/3])

    def test_tied_scores_allocate_identical_precision_to_tied_positives(self):
        np.testing.assert_allclose(ap_contributions([1,0,1],[.5,.5,.5]),[1/3,0,1/3])

    def test_random_discrete_scores_reconcile_with_sklearn(self):
        rng=np.random.default_rng(42)
        for size in [8,39,117]:
            for _ in range(20):
                y=rng.integers(0,2,size);y[0]=1
                score=rng.integers(0,5,size)
                contributions=ap_contributions(y,score)
                self.assertAlmostEqual(contributions.sum(),average_precision_score(y,score),places=13)
                self.assertTrue(np.all(contributions[y==0]==0))

    def test_no_positive_is_explicitly_undefined(self):
        self.assertTrue(np.isnan(ap_contributions([0,0],[.1,.9])).all())

    def test_label_blind_budget_and_deterministic_ties(self):
        data=pd.DataFrame({'sample_id':['z','b','a','c'], 'fold_name':['f1','f1','f1','f2'], 'score':[.5,.5,.5,.1]})
        self.assertEqual(top_mask(data,'score',.2).tolist(),[False,False,True,True])

    def test_exact_symmetric_decomposition(self):
        pa,pb=np.array([.1,.4,.9]),np.array([.2,.2,.8]);sensor=np.array([.5,.1,.7])
        av,bv,ass,bss,ia,ib=2.,3.,5.,4.,-2.,-3.
        observed=logit(expit(bv*pb+bss*sensor+ib))-logit(expit(av*pa+ass*sensor+ia))
        split=(av+bv)/2*(pb-pa)+(bv-av)*(pa+pb)/2+(bss-ass)*sensor+(ib-ia)
        np.testing.assert_allclose(split,observed,atol=1e-13)


if __name__=='__main__':
    unittest.main(verbosity=2)
