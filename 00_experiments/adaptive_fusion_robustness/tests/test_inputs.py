import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
import numpy as np
import engine
from corruptions import sensor_fault,survivors,image_fault
class Inputs(unittest.TestCase):
 def test_mask_vectorization_exact(self):
  t=np.linspace(0,2,201);x=np.c_[np.sin(t),np.cos(t)];mask=np.zeros_like(x,dtype=bool);mask[45:95]=True;y=x.copy();y[mask]=np.nan
  a=engine.original_resample(t,y,.1,1.9,explicit_mask=mask,time_block=(.45,.95));b=engine.resample_masked(t,y,.1,1.9,explicit_mask=mask,time_block=(.45,.95));np.testing.assert_array_equal(a,b)
 def test_only_received_sensor_interval_changes(self):
  t=np.linspace(0,2,201);x=np.c_[np.sin(t),np.cos(t)];streams=[('s',t,x)];changed,_=sensor_fault(streams,['a','b'],'sensor_noise',.5,50101,('r','s'),.3,1.7,np.ones(2));np.testing.assert_array_equal(changed[0][2][(t<.3)|(t>1.7)],x[(t<.3)|(t>1.7)]);np.testing.assert_array_equal(streams[0][2],x)
 def test_loss_counts_and_nested_masks(self):
  sets=[]
  for f,n in [(.1,14),(.3,11),(.5,8)]:
   keep,lost=survivors(16,f,50101,('r','s'),'frame_loss');self.assertEqual(len(keep),n);sets.append(set(lost))
  self.assertTrue(sets[0]<=sets[1]<=sets[2])
 def test_image_noop_and_seed(self):
  x=np.arange(8*8*3,dtype=np.uint8).reshape(8,8,3);y,_=image_fault(x,'image_noise',0,2,('r','s'),1);np.testing.assert_array_equal(np.rint(y*255).astype('uint8'),x)
  a,_=image_fault(x,'image_noise',.05,2,('r','s'),1);b,_=image_fault(x,'image_noise',.05,2,('r','s'),1);np.testing.assert_array_equal(a,b)
if __name__=='__main__':unittest.main()
