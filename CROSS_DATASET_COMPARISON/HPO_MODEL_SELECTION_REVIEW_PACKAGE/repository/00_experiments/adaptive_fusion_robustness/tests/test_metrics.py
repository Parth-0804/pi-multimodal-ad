import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
import numpy as np
from sklearn.metrics import average_precision_score
from metrics import weighted_bootstrap_ap,hierarchy
class Metrics(unittest.TestCase):
 def test_duplicate_recording_multiplicity_and_ties(self):
  y=np.array([0,1,0,1,1,0]);p=np.array([.2,.2,.6,.7,.7,.9]);w=np.array([[2,2,0,0,1,1],[0,0,1,1,2,2],[1,1,1,1,1,1]],float);actual=weighted_bootstrap_ap(y,p,w)
  for i,row in enumerate(w):
   ix=np.repeat(np.arange(len(y)),row.astype(int));self.assertAlmostEqual(actual[i],average_precision_score(y[ix],p[ix]),places=14)
 def test_hierarchy_does_not_weight_larger_folds(self):
  v={'f1':{'image':{'mild':{1:.2,2:.4}},'sensor':{'mild':{1:.8}}},'f2':{'image':{'mild':{1:.1}},'sensor':{'mild':{1:.3}}}}
  self.assertAlmostEqual(float(hierarchy(v)),.375)
if __name__=='__main__':unittest.main()
