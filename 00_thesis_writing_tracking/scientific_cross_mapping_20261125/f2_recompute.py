#!/usr/bin/env python3
"""Read-only saved-prediction audit. No fitting, inference, or raw-data access.
Run from repository root with an existing NumPy/pandas/scikit-learn environment.
Output directory must not exist. AP is non-interpolated average precision.
"""
import argparse, datetime, hashlib, json, platform, subprocess, sys
from pathlib import Path
import numpy as np
import pandas as pd
import sklearn
from sklearn.metrics import average_precision_score, roc_auc_score
from scipy.special import expit

ROOT = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser()
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
assert not a.out.exists(), 'Refusing to overwrite an audit output'
inputs = {}
def track(path):
    path = ROOT / path
    inputs[str(path.relative_to(ROOT))] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size}
    return path
def js(path): return json.loads(track(path).read_text())
def nz(path):
    with np.load(track(path), allow_pickle=False) as z: return {k:z[k].copy() for k in z.files}
def metrics(y,p):
    assert np.isfinite(p).all() and ((p>=0)&(p<=1)).all()
    # Independent threshold-group AP implementation, checked against sklearn.
    order=np.argsort(-p,kind='stable'); yy=y[order]; pp=p[order]
    ends=np.r_[np.flatnonzero(pp[:-1]!=pp[1:]),len(pp)-1]
    tp=np.cumsum(yy)[ends]; precision=tp/(ends+1)
    manual=float(np.sum(np.diff(np.r_[0,tp])*precision)/sum(y))
    ap=float(average_precision_score(y,p)); assert abs(manual-ap)<1e-14
    return {'AP':ap,'AUROC':float(roc_auc_score(y,p)), 'Brier':float(np.mean((p-y)**2))}
b=Path('implementations/REASSEMBLE/results/runs')
s=b/'sensor_controls_f2_nested_stacking'; f=b/'fusion_method_comparison'; u=b/'unimodal_baselines_visual_sensor'
cohort=pd.read_parquet(track(u/'cohort.parquet'))
splits=js(u/'nested_splits.json'); z=nz(s/'stacking/oof.npz'); fused=nz(f/'predictions/oof.npz')
sensor=nz(s/'sensor_controls/predictions/sensor_statistics_perm00.npz')
coeff=js(s/'assessment/stacker_coefficients.json'); reported=js(s/'assessment/results.json')
reported2=js(f/'assessment/results.json')
for source in [s/'provenance.json',s/'implementation.json',s/'config.json',f/'provenance.json',u/'final_output_manifest.json',Path('implementations/REASSEMBLE/src/reassemble/section1b.py'),Path('implementations/REASSEMBLE/src/reassemble/section2.py')]: track(source)
y=z['y']; fold=z['fold']; n=len(y)
assert n==4530 and sum(y)==509 and cohort.recording_id.nunique()==148
assert not cohort.duplicated(['recording_id','segment_id']).any()
assert np.array_equal(cohort.failure.to_numpy(),y)
for other in [sensor,fused]:
    assert np.array_equal(other['y'],y) and np.array_equal(other['fold'],fold)
assert np.array_equal(fused['F2_p'],z['p'])
assert np.array_equal(sensor['p'],fused['U1_p'])
ps=fused['U1_p']; pv=fused['U2_p']; pf=z['p']; q=np.full(n,np.nan)
assert np.max(abs(fused['F1_p']-(ps+pv)/2))<1e-14
rows=[]; seen=[]; formula_max=0.
for k in range(5):
    outer=nz(s/f'stacking/outer{k}.npz'); meta=js(s/f'stacking/outer{k}.json')
    te=outer['test_rows']; tr=outer['train_rows']; spec=splits['folds'][k]
    assert np.array_equal(te,np.flatnonzero(fold==k))
    assert np.array_equal(np.sort(np.r_[tr,te]),np.arange(n))
    assert len(np.intersect1d(tr,te))==0
    assert set(cohort.iloc[te].recording_id)==set(spec['test_recordings'])
    assert set(cohort.iloc[tr].recording_id)==set(spec['train_recordings'])
    assert not set(spec['train_recordings'])&set(spec['test_recordings'])
    assert meta['meta_columns']==['p_rtdetr','p_sensor_statistics']
    assert meta['stacker']==coeff[k]
    vcoef,scoef=coeff[k]['coefficient']; intercept=coeff[k]['intercept']
    assert vcoef>0 and scoef>0
    bp=outer['test_branch_probabilities']
    assert np.array_equal(bp[:,0],pv[te]) and np.array_equal(bp[:,1],ps[te])
    assert np.array_equal(outer['p'],pf[te])
    calc=expit(intercept+vcoef*bp[:,0]+scoef*bp[:,1])
    residual=float(np.max(abs(calc-pf[te]))); assert residual<1e-14
    formula_max=max(formula_max,residual)
    q[te]=expit(intercept+scoef*ps[te])
    m={name:metrics(y[te],pred[te]) for name,pred in [('sensor',ps),('visual',pv),('F2',pf),('saved_formula_without_visual',q)]}
    for metric in ['AP','AUROC']: assert abs(m['sensor'][metric]-m['saved_formula_without_visual'][metric])<1e-14
    pos=te[y[te]==1]; neg=te[y[te]==0]
    old=np.sign(ps[pos,None]-ps[neg]); new=np.sign(pf[pos,None]-pf[neg])
    corrected=int(((old<0)&(new>0)).sum()); damaged=int(((old>0)&(new<0)).sum())
    ties_before=int((old==0).sum()); ties_after=int((new==0).sum())
    pair_delta=float(np.mean((new-old)/2))
    assert abs(pair_delta-(m['F2']['AUROC']-m['sensor']['AUROC']))<1e-14
    oldall=np.sign(ps[te,None]-ps[te]); newall=np.sign(pf[te,None]-pf[te])
    ordering_changes=int(np.triu(oldall!=newall,k=1).sum())
    rows.append({'fold':k,'n':len(te),'failures':int(y[te].sum()),'recordings':len(set(cohort.iloc[te].recording_id)),'prevalence':float(y[te].mean()),'coefficients':{'visual':vcoef,'sensor':scoef,'intercept':intercept},'formula_max_abs_error':residual,'metrics':m,'delta_F2_minus_sensor':{key:m['F2'][key]-m['sensor'][key] for key in ['AP','AUROC']},'ordering':{'all_unordered_pairs_changed':ordering_changes,'positive_negative_pairs':len(pos)*len(neg),'incorrect_to_correct':corrected,'correct_to_incorrect':damaged,'ties_before':ties_before,'ties_after':ties_after,'net_AUROC_from_pairs':pair_delta}})
    seen.extend(te.tolist())
assert sorted(seen)==list(range(n))
pooled={name:metrics(y,pred) for name,pred in [('sensor',ps),('visual',pv),('F1',fused['F1_p']),('F2',pf),('saved_formula_without_visual',q)]}
for name,key in [('sensor','sensor_statistics'),('visual','rtdetr'),('F2','F2')]:
    for metric,saved in [('AP','AUPRC'),('AUROC','AUROC')]:
        source=reported['metrics'].get(key,reported2['metrics'].get(key))
        assert abs(pooled[name][metric]-source[saved]['estimate'])<1e-14
result={'classification':'VERIFIED: recomputed saved predictions, not reproduced training', 'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'timezone_for_review':'Europe/Berlin','head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'dirty_tree':bool(subprocess.check_output(['git','status','--porcelain','--untracked-files=normal'],cwd=ROOT,text=True).strip()),'command':sys.argv,'python':platform.python_version(),'packages':{'numpy':np.__version__,'pandas':pd.__version__,'sklearn':sklearn.__version__},'cohort':{'n':n,'failures':int(sum(y)),'recordings':148,'prevalence':float(y.mean()),'positive_class':'native completed-action failure','row_identity':'cohort.parquet order; (recording_id,segment_id) unique; saved test_rows verified against nested_splits.json'},'checks':{'targets_and_folds_equal':True,'outer_recording_disjoint':True,'row_coverage_once':True,'branch_probabilities_exact_parity':True,'F2_exact_reuse':True,'F1_formula_parity':True,'coefficients_all_positive':True,'F2_formula_max_abs_error':formula_max,'manual_AP_vs_sklearn':True,'pairwise_AUROC_delta_vs_sklearn':True},'pooled':pooled,'folds':rows,'unweighted_mean_fold':{name:{metric:float(np.mean([r['metrics'][name][metric] for r in rows])) for metric in ['AP','AUROC']} for name in ['sensor','visual','F2']},'limitations':['No fitting, calibration, training or bootstrap rerun. Historical intervals are not newly verified here.','Unimodal predictions directory is empty at this location. Visual parity is verified between saved Section1B branch inputs and Section2 U2, not against unavailable original Section1 prediction files. Sensor parity additionally uses the observed Section1B sensor-control file.','Formula-without-visual is an arithmetic omission with jointly fitted parameters, not an independently fitted sensor-only control; zero is one arbitrary constant visual reference.','Five folds share training observations; foldwise directions are not five independent replications.','The diagnostic is post hoc, and fixed-prediction checks omit fitting/selection uncertainty.'],'input_manifest':inputs}
a.out.mkdir(parents=True)
(a.out/'results.json').write_text(json.dumps(result,indent=2)+'\n')
header='fold,n,failures,recordings,sensor_AP,F2_AP,delta_AP,sensor_AUROC,F2_AUROC,delta_AUROC,corrected_pairs,damaged_pairs\n'
lines=[','.join(map(str,[r['fold'],r['n'],r['failures'],r['recordings'],r['metrics']['sensor']['AP'],r['metrics']['F2']['AP'],r['delta_F2_minus_sensor']['AP'],r['metrics']['sensor']['AUROC'],r['metrics']['F2']['AUROC'],r['delta_F2_minus_sensor']['AUROC'],r['ordering']['incorrect_to_correct'],r['ordering']['correct_to_incorrect']])) for r in rows]
(a.out/'fold_metrics.csv').write_text(header+'\n'.join(lines)+'\n')
print(json.dumps({'checks':result['checks'],'pooled':pooled,'folds':[{'fold':r['fold'],'delta':r['delta_F2_minus_sensor'],'ordering':r['ordering']} for r in rows]},indent=2))
