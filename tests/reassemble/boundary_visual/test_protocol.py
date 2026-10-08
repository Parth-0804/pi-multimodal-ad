import numpy as np
import pytest
import torch
from reassemble.boundary_visual.models import aggregate,make
from reassemble.boundary_visual.report import classify
from reassemble.section1b import guard_partition
from reassemble.section1_models import VisualHead
import pandas as pd

def test_exact_predeclared_windows():
 x=np.broadcast_to(np.arange(16,dtype=np.float32)[None,:,None],(2,16,896)).copy()
 for variant,expected in {'V1':[3.5,11.5],'V2':[1.5,7.5,13.5],'V3':[13.5],'V4':[1.5,13.5]}.items():
  np.testing.assert_array_equal(aggregate(x,variant)[0,:,0],expected)
 np.testing.assert_array_equal(aggregate(x,'V5'),x)

def test_binned_capacity_is_near_control_and_last_only_matches_head():
 torch.set_num_threads(1);torch.manual_seed(17)
 base=VisualHead(896,{}).eval();control=sum(p.numel() for p in base.parameters());assert control==114945
 for name in ['V1','V2','V3','V4']:
  model=make(name);assert sum(p.numel() for p in model.parameters())<=control+256
 last=make('V3').eval();last.load_state_dict(base.state_dict());x=torch.randn(9,896)
 torch.testing.assert_close(last(x[:,None]),base(x)[0],rtol=0,atol=0)

def test_ordered_model_has_one_bounded_layer_and_uses_order():
 torch.set_num_threads(1);torch.manual_seed(21);model=make('V5').eval();x=torch.randn(5,16,896)
 assert model.encoder.num_layers==1 and model.encoder.hidden_size==64
 assert model(x).shape==(5,) and not torch.allclose(model(x),model(x.flip(1)))
 assert sum(p.numel() for p in model.parameters())<114945
 assert 'position' in dict(model.named_buffers()) and 'position' not in dict(model.named_parameters())

def case(ap=-.01,lo=-.03,hi=.01,sim=-.04,auc=-.005):return {'AUPRC':{'estimate':ap,'lower_95':lo,'upper_95':hi,'simultaneous_lower_95':sim},'AUROC':{'lower_95':auc}}
def test_gate_requires_multiplicity_and_noninferiority_and_handles_late_only():
 pairs={f'V{i}':case() for i in range(1,6)};assert classify(pairs)[0]=='D'
 pairs['V1']=case(ap=.02,lo=.002,sim=-.001);assert classify(pairs)[0]=='B'
 pairs['V1']=case(ap=.02,lo=.002,sim=.001,auc=-.02);assert classify(pairs)[0]=='B'
 pairs['V1']=case(ap=.02,lo=.002,sim=.001);assert classify(pairs)[0]=='A'
 pairs={f'V{i}':case() for i in range(1,6)};pairs['V3']=case(ap=.02,lo=.002,sim=.001);assert classify(pairs)[0]=='C'
 pairs={f'V{i}':case() for i in range(1,6)};pairs['V5']=case(hi=-.001);assert classify(pairs)[0]=='E'

def test_recording_overlap_is_rejected():
 frame=pd.DataFrame({'recording_id':['a','a','b','b','c','c']})
 with pytest.raises(AssertionError):guard_partition(frame,np.array([0,2,3]),np.array([1,4,5]),[(np.array([0]),np.array([2,3])),(np.array([2,3]),np.array([0]))])

def test_outer_labels_cannot_change_branch_selection_calibration_or_coverage(tmp_path,monkeypatch):
 import json
 from reassemble.boundary_visual import training
 frame=pd.DataFrame({'recording_id':np.repeat(list('abcdef'),2)})
 train=np.arange(8);test=np.arange(8,12);plan=[(train[~np.isin(train,[i,i+1])],np.array([i,i+1])) for i in range(0,8,2)]
 y=np.tile([0,1],6);seq=np.zeros((12,16,896),np.float32);mean=seq.mean(1)
 def fake_fit(run,location,variant,x,mean,labels,tr,te,candidates,base,seed,pause):
  assert not set(tr)&set(te)
  return {e:(2*(te%2)-1).astype(float)+labels[tr].mean()*.1 for e in candidates},{'parameters':114945}
 monkeypatch.setattr(training,'fit',fake_fit)
 outputs=[];infos=[]
 for i in range(2):
  run=tmp_path/str(i);run.mkdir();(run/'config.json').write_text(json.dumps({'epochs':{'V0':[5,10]}}));(run/'source_signature.json').write_text('[]')
  labels=y.copy()
  if i:labels[test]=1-labels[test]
  out,info=training.branch(run,'V0/outer0','V0',seq,mean,labels,frame,train,test,plan,{},17,116,lambda:None)
  outputs.append(out);infos.append(info)
 for field in ['p','hard','inner_p','coverage_cutoffs']:np.testing.assert_array_equal(outputs[0][field],outputs[1][field])
 for field in ['selected','calibration','threshold']:assert infos[0][field]==infos[1][field]

def test_atomic_predictions_resume_without_overwrite_and_reject_differences(tmp_path):
 from reassemble.boundary_visual.common import atomic_npz,sha
 p=tmp_path/'prediction.npz';values=np.array([.1,.9]);atomic_npz(p,p=values)
 before=(sha(p),p.stat().st_mtime_ns);atomic_npz(p,p=values)
 assert (sha(p),p.stat().st_mtime_ns)==before
 with pytest.raises(AssertionError):atomic_npz(p,p=values[::-1])
 assert (sha(p),p.stat().st_mtime_ns)==before

def test_clustered_metrics_match_weighted_reference():
 from reassemble.cluster_metrics import weighted_metrics
 from reassemble.section1_report import metrics
 y=np.array([0,1,0,1,1,0]);p=np.array([.1,.7,.4,.7,.2,.3]);h=(p>=.4).astype(int);w=np.array([[1,1,2,2,0,0],[1,1,1,1,1,1]],float)
 expected=np.stack([metrics(y,p,h,x) for x in w])
 np.testing.assert_allclose(weighted_metrics(y,p,h,w),expected,rtol=0,atol=1e-12)
