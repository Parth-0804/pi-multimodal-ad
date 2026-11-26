"""Verify completed inputs/checks before the authorized scientific fit matrix."""
from pathlib import Path
import sys,json
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source'))
from common import ROOT,REPO,read,write,sha,resources,check_originals,utc
from training import input_identity,runtime_guard,check_locked_inputs
from data import load_cohort
check_originals();runtime_guard();frame=load_cohort();check_locked_inputs(frame)
metadata=read(ROOT/'shared_cache/frozen_features_complete.json')
for name,h in metadata['hashes'].items():assert sha(ROOT/name)==h
for n in [16,32]:
 a=np.load(ROOT/f'shared_cache/original_features_{n}.npy',mmap_mode='r',allow_pickle=False);assert a.shape==(len(frame),896) and np.isfinite(a).all()
assert read(ROOT/'checks/unit_test_results.json')['passed'] and read(ROOT/'checks/evaluation_integration_results.json')['passed']
assert read(ROOT/'checks/gradient_preflight.json')['optimizer_steps']==9
write(ROOT/'checks/full_fit_admission.json',{'utc':utc(),'passed':True,'planned_full_visual_fits':100,'full_fit_cap':110,'sensor_fits':25,'precision':'float32','microbatch_segments':1,'feature_arrays_shapes':{'16':[len(frame),896],'32':[len(frame),896]},'actual_feature_extraction_seconds':metadata['seconds'],'resource_estimate':'checks/training_resource_estimate.json','estimate_limitation':'Frozen disposable timings include CNN forward; actual frozen fits use cached original features and will be cheaper. Cache/decoding/inference add uncertainty. No hour ceiling by latest launch.','checkpoint_storage_note':'50 final-stage compact states about1.56GiB plus heads/buffers;24GiB disk pixel cap and4GiB noncache reserve; actual total monitored','identities':input_identity(),'resources':resources()})
with (ROOT/'provenance/stage_invocations.jsonl').open('a') as f:
 f.write(json.dumps({'recorded_utc':utc(),'event':'preflight_and_feature_extraction_completed_and_verified','exit_code':0,'samples':len(frame),'width':896,'evidence':'shared_cache/frozen_features_complete.json'})+'\n')
 f.write(json.dumps({'recorded_utc':utc(),'command':['bash',str(ROOT.relative_to(REPO)/'source/study.sh'),'train'],'result':'ADMITTED_FOR_AUTHORIZED_FULL_FITS','log':'checks/full_study_training.log'})+'\n')
print('FULL_FIT_ADMISSION_PASSED',json.dumps(metadata['cost_totals']),flush=True)
