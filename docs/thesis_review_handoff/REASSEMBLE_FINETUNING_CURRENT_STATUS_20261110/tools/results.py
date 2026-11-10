"""Recompute saved-score metrics and preserve original uncertainty; no fitting."""
import audit as a
import collections,csv,hashlib,json,math,re
import numpy as np
from sklearn.metrics import average_precision_score,roc_auc_score,brier_score_loss,log_loss,f1_score,balanced_accuracy_score,confusion_matrix

def main():
    canonical={r['native_key']:r for r in a.rows(a.COHORT/'CANONICAL_ACTION_MANIFEST.csv')}
    es={r['evaluation_id']:r for r in a.rows(a.COHORT/'ALL_EVALUATION_COHORTS.csv') if r['condition']=='clean' and r['evaluation_scope']=='OUTER HELD-OUT' and r['label_contract']=='NATIVE FAILURE' and int(r['N'])>0}
    vectors=collections.defaultdict(list)
    with a.used(a.COHORT/'ALL_CLEAN_HELD_OUT_PREDICTIONS.csv').open(newline='') as f:
        for r in csv.DictReader(f):
            if r['evaluation_id'] in es:vectors[r['evaluation_id']].append((r['native_key'],int(r['failure']),float(r['probability'])))
    result=[];checks=[]
    for eid,vs in vectors.items():
        e=es[eid];vs.sort();keys=[v[0] for v in vs];y=np.array([v[1] for v in vs]);p=np.array([v[2] for v in vs]);n=len(vs)
        assert n==int(e['N']) and len(set(keys))==n
        assert all(int(canonical[k]['failure'])==label for k,label in zip(keys,y))
        h=hashlib.sha256((e['action_set_sha256']+'\n').encode()+p.astype('<f8').tobytes()).hexdigest();assert h==e['prediction_vector_sha256']
        ap=float(average_precision_score(y,p));assert abs(ap-float(e['AP_saved_probability_recomputation']))<1e-12
        pred=p>=.5;tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel()
        fold=np.array([int(canonical[k]['outer_fold_zero_based']) for k in keys]);aps=[float(average_precision_score(y[fold==k],p[fold==k])) for k in sorted(set(fold))]
        row={**e,'AP':ap,'AUROC':float(roc_auc_score(y,p)),'Brier':float(brier_score_loss(y,p)),'log_loss':float(log_loss(y,p,labels=[0,1])),
            'F1_at_0_5':float(f1_score(y,pred,zero_division=0)),'balanced_accuracy_at_0_5':float(balanced_accuracy_score(y,pred)),
            'TN_at_0_5':int(tn),'FP_at_0_5':int(fp),'FN_at_0_5':int(fn),'TP_at_0_5':int(tp),
            'failure_prevalence':float(y.mean()),'mean_present_fold_AP':float(np.mean(aps)),'folds_present':sorted({int(k) for k in fold}),
            'threshold_convention':'AUDIT COMMON0.5; historical native-threshold results kept separately',
            'verification':a.V,'uncertainty':'existing paired intervals only; no new bootstrap or refitting'}
        result.append(row);checks.append({'evaluation_id':eid,'N':n,'AP_matches_saved_report':True,'score_vector_hash_matches':True,'labels_match_native':True})
    a.table('support/ALL_RECOMPUTED_CLEAN_RESULTS.csv',result)
    def visual(r):
        m=r['model'];return ('/p_visual' in m or m in ['C_full_finetuned16','B_frozen100','M1_frozen100','M2_finetuned100'] or m.startswith(('rtdetr','V0','V1','V2','V3','V4','V5','V-MEAN','V-TEMP','V-NOPOS','V-FT')))
    a.table('07_VISUAL_ONLY_RESULTS.csv',[r for r in result if visual(r)])
    a.table('support/CPU_METRIC_RECOMPUTATION_CHECKS.csv',checks)
    # Direct checks against current original banks and current long-fit JSON files.
    direct=[]
    for r in a.read(a.OLD/'03_hyperparameter_configuration/EFFECTIVE_CONFIGURATIONS.json'):
        if r['experiment_id'] not in ['REASSEMBLE_PHASE1_C20','REASSEMBLE_100E_SINGLE_FIT']:continue
        info=a.read(r['history_source']);p=a.path(r['history_source']).parent/'PHASE1_PREDICTIONS.json';data=a.read(p)
        data=data if isinstance(data,list) else data.get('rows',data.get('predictions'))
        score=float(average_precision_score([v['failure'] for v in data],[v['p_visual'] for v in data]))
        direct.append({'run_id':r['run_id'],'source':a.rel(p),'N':len(data),'AP':score,'source_sha256':a.sha(p),'evidence':a.V})
    for name in ['rtdetr_perm00','sensor_statistics_perm00']:
        p=a.path('runs/reassemble/20260927T154732Z-section1/predictions')/(name+'.npz')
        with np.load(a.used(p),allow_pickle=False) as z:score=float(average_precision_score(z['y'],z['p']))
        direct.append({'run_id':name,'source':a.rel(p),'N':4530,'AP':score,'source_sha256':a.sha(p),'evidence':a.V})
    p=a.path('runs/reassemble/20260927T175336Z-section1b/stacking/oof.npz')
    with np.load(a.used(p),allow_pickle=False) as z:score=float(average_precision_score(z['y'],z['p']))
    direct.append({'run_id':'ORIGINAL_F2','source':a.rel(p),'N':4530,'AP':score,'source_sha256':a.sha(p),'evidence':a.V})
    a.table('support/DIRECT_CURRENT_PREDICTION_RECOMPUTATION.csv',direct)
    # Common model grid. These are reported separately by cohort and seed, never a mixed ranking.
    grid=[]
    original='runs/reassemble/20260927T154732Z-section1'
    f2source='runs/reassemble/20260927T175336Z-section1b/stacking/oof.npz'
    def find(pred):return next((r for r in result if pred(r)),None)
    def add(label,v,s,avg,fused,epochs,status,seed=None):
        if not v:return
        grid.append({'CNN_condition':label,'CNN_epochs':epochs,'visual_AP':v['AP'],'static_sensor_AP':s['AP'] if s else a.U,
            'averaging_AP':avg['AP'] if avg else 'NOT EXECUTED / NOT SAVED','F2_AP':fused['AP'] if fused else 'NOT EXECUTED',
            'F2_minus_sensor':fused['AP']-s['AP'] if fused and s else 'NOT EXECUTED',
            'seed':seed if seed is not None else v['seed'],'outer_fold':v['fold'],'assessment_N':v['N'],'assessment_cohort_id':v['cohort_id'],
            'fusion_completion_status':status,'visual_evaluation_id':v['evaluation_id'],'F2_evaluation_id':fused['evaluation_id'] if fused else 'NOT EXECUTED',
            'sensor_identity':s['prediction_vector_sha256'] if s else a.U,'visual_identity':v['prediction_vector_sha256'],
            'F2_identity':fused['prediction_vector_sha256'] if fused else 'NOT EXECUTED'})
    for v in result:
        if v['experiment_id']==original and v['model']=='rtdetr_perm00':
            s=find(lambda r:r['experiment_id']==original and r['model']=='sensor_statistics_perm00' and r['cohort_id']==v['cohort_id'])
            f=find(lambda r:r['experiment_id']==f2source and r['model']=='F2_original' and r['cohort_id']==v['cohort_id'])
            add('ORIGINAL FROZEN16',v,s,None,f,'inner5/10 selection; selected outer duration','COMPLETE ORIGINAL NESTED F2')
        if v['experiment_id']=='REASSEMBLE_PHASE1_C20' and v['evaluation_scope']=='OUTER HELD-OUT':
            s=find(lambda r:r['experiment_id']==original and r['model']=='sensor_statistics_perm00' and r['cohort_id']==v['cohort_id'])
            add('C20 FULL CNN',v,s,None,None,20,'NOT EXECUTED (sensor row is original matched-cohort reference only)',42)
    for vm,fm,am,label in [('M1_frozen100','M4_F2_frozen','M6_average_frozen','FROZEN100'),('M2_finetuned100','M5_F2_finetuned','M7_average_finetuned','FULL100')]:
        take=lambda m:find(lambda r:r['experiment_id']=='CNN100_STATIC_SENSOR_F2' and r['model']==m)
        add(label,take(vm),take('M3_sensor'),take(am),take(fm),100,'COMPLETE SINGLE920-ROW STACK BANK / SINGLE753 OUTER',42)
    for v in result:
        exp,source,model=v['experiment_id'],v['prediction_source'],v['model']
        early='visual_backbone_one_day' in exp and '/comparison/identified_assessment_predictions.csv'==source[-len('/comparison/identified_assessment_predictions.csv'):]
        matched='frozen32_vs_finetuned32' in exp and re.search(r'/seed_\d+/(frozen32_two_epochs|finetuned32_two_epochs)/fold_\d+/assessment_predictions.csv',source)
        if not model.endswith('/p_visual') or not (early or matched):continue
        prefix=model[:-len('/p_visual')];same=lambda r:r['experiment_id']==exp and r['seed']==v['seed'] and r['cohort_id']==v['cohort_id'] and r['prediction_source']==source
        s=find(lambda r:same(r) and r['model']==prefix+'/p_sensor');f=find(lambda r:same(r) and r['model'] in [prefix+'/p_fused',prefix+'/p_F2'])
        avg=find(lambda r:same(r) and r['model']==prefix+'/p_uniform')
        add(('ASYMMETRIC ' if early else 'MATCHED2 ')+prefix,v,s,avg,f,5 if early and prefix.startswith('frozen') else 2,'COMPLETE NESTED F2',42 if early else v['seed'])
    a.table('08_STATIC_SENSOR_AND_F2_RESULTS.csv',grid)
    intervals=[]
    for root,name in [('00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/comparison','paired_comparisons.csv'),('00_experiments/frozen32_vs_finetuned32_fusion_diagnosis/results/comparison','paired_intervals.csv')]:
        p=a.path(root)/name
        for r in a.rows(p):intervals.append({**r,'original_source':a.rel(p),'uncertainty_scope':'recording resampling conditional on fixed fitted models; no refit,seed or selection uncertainty'})
    a.table('support/EXISTING_PAIRED_INTERVALS.csv',intervals)
    for name,p in [('ORIGINAL_F2_REPORTED_RESULTS.json','runs/reassemble/20260927T175336Z-section1b/assessment/results.json'),('CNN100_PAIRED_BOOTSTRAP.json',str(a.FOLLOW/'07_evaluation_results/PAIRED_RECORDING_BOOTSTRAP.json'))]:a.write('support/'+name,a.read(p))
    # Retain original conventions for threshold and diagnostic results without modifying them.
    a.table('support/ORIGINAL_RECORDED_RESULTS.csv',a.rows(a.OLD/'06_dataset_specific/REASSEMBLE/COMPLETE_RESULTS.csv'))
    a.table('support/RESULTS_INPUTS.csv',list(a.INPUTS.values()))
    print(json.dumps({'recomputed_evaluations':len(result),'saved_clean_rows':sum(len(v) for v in vectors.values()),'fusion_grid_rows':len(grid),'direct_current_prediction_checks':len(direct)}))

if __name__=='__main__':main()
