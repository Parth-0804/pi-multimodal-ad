"""Focused tests of newly introduced controls, not a repeat of the old model suite."""
import copy
import math
import unittest
import numpy as np
import torch
from common import *
install_prior_primitives()
from visual_model import Visual,optimizer
from fusion import fused

class ProtocolTests(unittest.TestCase):
    def test_seed_families_preserve_partitions(self):
        jobs=read(STUDY/'data_manifests/fit_partitions.json')
        self.assertEqual(len(jobs),25)
        for job in jobs:
            self.assertEqual(role_seed(42,job),job['seed'])
            self.assertNotEqual(role_seed(20261023,job),job['seed'])

    def test_locked_frames_and_memberships(self):
        self.assertEqual(sha(STUDY/'data_manifests/cohort_and_frames.json'),sha(PRIOR/'data_manifests/cohort_and_frames.json'))
        self.assertEqual(sha(STUDY/'data_manifests/fit_partitions.json'),sha(PRIOR/'data_manifests/fit_partitions.json'))
        frame=read(STUDY/'data_manifests/cohort_and_frames.json')
        self.assertEqual(len(frame),4530)

    def test_exact_two_epoch_stop_and_batch_policy(self):
        cfg=config();self.assertEqual(cfg['epochs'],2);self.assertEqual(cfg['effective_batch_segments'],8);self.assertEqual(cfg['microbatch_segments'],1)
        for job in read(STUDY/'data_manifests/fit_partitions.json'):
            visits=sum(len(np.random.default_rng(role_seed(42,job)+e).permutation(len(job['G']))) for e in range(2))
            self.assertEqual(visits,2*len(job['G']))

    def test_uniform_probability_arithmetic(self):
        p=np.array([[.1,.9],[.9,.1],[0.,0.],[1.,1.]])
        np.testing.assert_array_equal(.5*p[:,0]+.5*p[:,1],[.5,.5,0.,1.])

    def test_F2_feature_order_arithmetic(self):
        p=np.array([[.1,.8],[.8,.1]]);m={'coefficient':[2.,5.],'intercept':-1.}
        expected=1/(1+np.exp(-(2*p[:,0]+5*p[:,1]-1)))
        np.testing.assert_array_equal(fused(p,m),expected)

    def test_head_checkpoint_optimizer_and_rng_restore(self):
        torch.manual_seed(1307);m=Visual(None,4,np.zeros(4),np.ones(4),False).train();opt=optimizer(m)
        x=torch.tensor([[.1,.2,.3,.4]]);y=torch.tensor([1.])
        def step():
            opt.zero_grad(set_to_none=True);value=torch.nn.functional.binary_cross_entropy_with_logits(m(x),y);value.backward();opt.step()
        step();saved=copy.deepcopy(m.state_dict());saved_opt=copy.deepcopy(opt.state_dict());rng=torch.get_rng_state().clone()
        step();expected=copy.deepcopy(m.state_dict())
        m.load_state_dict(saved);opt.load_state_dict(saved_opt);torch.set_rng_state(rng);step()
        self.assertTrue(all(torch.equal(v,expected[k]) for k,v in m.state_dict().items()))

    def test_sensor_source_is_independent_of_visual_seed(self):
        from pipeline import canonical_sensor
        jobs=read(STUDY/'data_manifests/fit_partitions.json')
        # Canonical sensor helper has no visual-seed argument and returns source fit identity.
        for job in [jobs[0],jobs[4]]:
            a,ia=canonical_sensor(job);b,ib=canonical_sensor(job)
            self.assertEqual(ia,ib);self.assertTrue(a.equals(b))

    def test_new_interval_AP_calculation_with_ties_and_zero_weights(self):
        from analysis import weighted_AP_evaluator
        from sklearn.metrics import average_precision_score
        rng=np.random.default_rng(51)
        for _ in range(12):
            y=rng.integers(0,2,15);y[:2]=[0,1];p=rng.integers(0,4,15);w=rng.integers(0,4,15);w[:2]=1
            self.assertAlmostEqual(weighted_AP_evaluator(y,p)(w),average_precision_score(y,p,sample_weight=w),places=13)

