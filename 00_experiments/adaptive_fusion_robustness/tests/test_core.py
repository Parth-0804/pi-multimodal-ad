import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
import numpy as np
from audit import success_value
from quality_fusion import *
class Checks(unittest.TestCase):
 def test_strict_annotations(self):
  for v in [True,False,np.int32(0),np.uint8(1)]:self.assertIn(success_value(v),[0,1])
  for v in ['False','True','0','1',None,np.nan,0.,2,[],[True]]:
   with self.assertRaises(ValueError):success_value(v)
 def test_quality_received_inputs(self):
  black=np.zeros((8,8,3),np.uint8);x=image_quality([black],[2]);np.testing.assert_array_equal(x,[0,1,0,1/16]);np.testing.assert_array_equal(image_quality([],[]),np.zeros(4))
  t=np.linspace(0,1,11);v=np.ones((11,2));q=sensor_quality([('x',t,v)],0,1,np.ones(2));self.assertEqual(q[0],1);self.assertEqual(q[1],1);self.assertEqual(q[3],0)
  broken=v.copy();broken[3:8]=np.nan;z=sensor_quality([('x',t,broken)],0,1,np.ones(2));self.assertLess(z[0],q[0]);self.assertGreater(z[2],q[2])
 def test_no_oracle_arguments(self):
  import inspect
  self.assertEqual(list(inspect.signature(image_quality).parameters),['images','frame_ids'])
  self.assertEqual(list(inspect.signature(sensor_quality).parameters),['streams','start','end','scales'])
 def test_interaction_identity(self):
  p=np.array([[.2,.7],[.8,.3]]);q=np.arange(16).reshape(2,8)/10;n={'mean':[0]*8,'std':[1]*8};x=design(p,q,'quality_interaction',n);b=np.arange(26)/100
  direct=x@b;conditional=b[0]*p[:,0]+b[1]*p[:,1]+q@b[2:10]+p[:,0]*(q@b[10:18])+p[:,1]*(q@b[18:26]);np.testing.assert_allclose(direct,conditional)
 def test_same_weights_and_serialized_predictor(self):
  rng=np.random.default_rng(3);parents=np.repeat(np.arange(20),3);p=rng.uniform(.1,.9,(60,2));q=rng.uniform(size=(60,8));y=np.repeat(np.arange(20)%2,3);w=np.tile([.5,.25,.25],20);m=fit_all(p,q,y,w,parents)
  for c,model in m.items():
   restored=json.loads(json.dumps(model));np.testing.assert_array_equal(predict(p,q,model),predict(p,q,restored));self.assertEqual(model['threshold'],.5)
  with self.assertRaises(AssertionError):fit_all(p,q,y,np.ones(60),parents)
 def test_normalizer_training_only_weighted(self):
  q=np.zeros((3,8));q[0]=2;n=normalize_fit(q,np.array([.5,.25,.25]));np.testing.assert_allclose(n['mean'],1);np.testing.assert_allclose(n['std'],1)
 def test_absence(self):
  self.assertEqual(route(.2,.8,True,False,.9),(.2,'visual_only_fallback'));self.assertEqual(route(.2,.8,False,True,.9),(.8,'sensor_only_fallback'));self.assertEqual(route(.2,.8,False,False,.9),(None,'unavailable_both_absent'));self.assertEqual(route(.2,.8,True,True,.9),(.9,'fusion'))
 def test_fixed_disjoint_seeds(self):
  self.assertNotIn(TRAIN_SEED,ASSESS_SEEDS)
  for modality in ['image','sensor']:
   self.assertEqual(training_variant('a',modality),training_variant('a',modality));self.assertIn(training_variant('a',modality)['seed'],[TRAIN_SEED])
if __name__=='__main__':unittest.main()
