"""Read-only source/artifact audit. No research imports, training or inference."""
from pathlib import Path
from functools import lru_cache
import collections,csv,datetime as dt,hashlib,importlib.metadata,json,math,os,re,subprocess,sys
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score,roc_auc_score,brier_score_loss,log_loss,confusion_matrix,f1_score,balanced_accuracy_score

OUT=Path(__file__).resolve().parents[1]
REPO=OUT.parents[2]
OLD=REPO/'CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103'
COHORT=REPO/'CROSS_DATASET_COMPARISON/REASSEMBLE_COHORT_RECONCILIATION_20261103'
BASE=Path('26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability')
FOLLOW=Path('experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison')
U='UNKNOWN';V='VERIFIED FROM SOURCE/ARTIFACTS'
INPUTS={};FILES=[];RUNS=[];CURVES=[];CHECKS=[]
csv.field_size_limit(256*1024**2)
SKIP={'.git','.aws','.ssh','.codex','.agents','ma_thesis_env','__pycache__','.pytest_cache','shared_cache','cache','raw','raw_data','data','source_snapshot','original_inputs','report_snapshots','reference_only','node_modules'}
ROOTS=['26.10.2026_feedback_experiments','00_experiments','src/reassemble','configs/reassemble','runs/reassemble',
 'experiments/reassemble','parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01']
def rel(p):
    p=Path(p)
    try:return str(p.relative_to(REPO))
    except ValueError:return str(p)
def path(p):return Path(p) if Path(p).is_absolute() else REPO/p
def sha(p):
    h=hashlib.sha256()
    with path(p).open('rb') as f:
        for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
    return h.hexdigest()
def used(p,role='evidence'):
    p=path(p);s=rel(p)
    assert not any(x in p.parts for x in ['.env','synology_cookies.txt','.aws','.ssh','.git'])
    if s not in INPUTS:
        st=p.stat();INPUTS[s]={'original_path':s,'bytes':st.st_size,'mtime_ns':st.st_mtime_ns,'sha256':sha(p),'role':role}
    return p
@lru_cache(maxsize=10000)
def read(p):return json.loads(used(p).read_text())
def rows(p):
    with used(p).open(newline='') as f:return list(csv.DictReader(f))
def write(name,x):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
    if isinstance(x,str):p.write_text(x)
    else:p.write_text(json.dumps(x,indent=2,default=str,allow_nan=False)+'\n')
def table(name,rs,fields=None):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
    fields=fields or list(dict.fromkeys(k for r in rs for k in r)) or ['no_records']
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in rs:w.writerow({k:json.dumps(v,sort_keys=True) if isinstance(v,(list,dict,tuple)) else v for k,v in r.items()})
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)
def check(name,passed,**kw):CHECKS.append({'check':name,'passed':bool(passed),**kw});assert passed,(name,kw)

def discover():
    oldhash={r['path']:r['sha256'] for r in rows(COHORT/'SOURCE_PROVENANCE.csv')}
    delta=[]
    for root in ROOTS:
        if not path(root).exists():continue
        for base,dirs,fs in os.walk(path(root),followlinks=False):
            dirs[:]=sorted(d for d in dirs if d not in SKIP and not 'REVIEW_PACKAGE' in d and not 'MODEL_CONFIGURATION_AUDIT' in d and not (Path(base)/d).is_symlink())
            for name in sorted(fs):
                p=Path(base)/name
                if p.is_symlink() or name.startswith('.env') or name in ['synology_cookies.txt','credentials']:continue
                s=rel(p);st=p.stat();r={'path':s,'bytes':st.st_size,'mtime_utc':dt.datetime.fromtimestamp(st.st_mtime,dt.timezone.utc).isoformat(),'suffix':p.suffix}
                FILES.append(r)
                if s in oldhash:
                    h=sha(p);delta.append({'path':s,'nov3_sha256':oldhash[s],'current_sha256':h,'status':'UNCHANGED' if h==oldhash[s] else 'CHANGED'})
    table('support/CURRENT_ARTIFACT_INVENTORY.csv',FILES)
    table('support/NOVEMBER3_SOURCE_DELTA.csv',delta)
    candidates=[r for r in FILES if re.search(r'(PHASE1_FIT_COMPLETE|complete\.json|fit.*\.json|PHASE1.*(STATUS|COMPLETE)|resolved.*json|model.*pt)$',Path(r['path']).name,re.I)]
    table('support/CURRENT_COMPLETION_AND_MODEL_CANDIDATES.csv',candidates)
    write('support/GIT_HISTORY.txt',git('log','-35','--date=iso-strict','--format=%H %ad %s','--','src/reassemble','configs/reassemble','26.10.2026_feedback_experiments','00_experiments','experiments/reassemble').decode())
    write('support/GIT_CHANGES_SINCE_NOV3_BASELINE.txt',git('diff','--stat','eb3888f5d23310aa097dbb1be14605e931190b4a','HEAD','--','src/reassemble','configs/reassemble','26.10.2026_feedback_experiments','00_experiments','experiments/reassemble').decode())
    print('DISCOVERY',len(FILES),'old sources',len(delta),'changed',sum(r['status']=='CHANGED' for r in delta),flush=True)

def classify(r):
    e,m=r['experiment_id'],r['model']
    if m=='C_full_finetuned16':return 'FULL CNN'
    if 'V-FT' in m:return 'FINAL STAGE + TEMPORAL HEAD'
    if m.startswith(('fine_tuned','finetuned')):return 'FINAL STAGE + MEAN HEAD'
    if m in ['cnn_plus_encoder']:return 'FROZEN CNN + HYBRID ENCODER'
    if m in ['rtdetr','B_long_frozen16','B_frozen100','cnn_only'] or m.startswith(('frozen','V-')) or e=='BOUNDARY_AWARE_VISUAL':return 'FROZEN CNN / TRAINED HEAD'
    if e in ['SECTION2','SECTION1B_F2','CNN100_STATIC_SENSOR_F2','MODALITY_DROPOUT'] or e.startswith('LEGACY_'):return 'FUSION / CACHED VISUAL CONTEXT'
    return 'SENSOR / CONTROL / OTHER CONTEXT'

def configurations():
    old=read(OLD/'03_hyperparameter_configuration/EFFECTIVE_CONFIGURATIONS.json')
    passports={r['run_id']:r for r in rows(COHORT/'ALL_TRAINING_RUN_COHORTS.csv')}
    selected=[]
    for oldr in old:
        if oldr['dataset']!='REASSEMBLE':continue
        r=dict(oldr);c=dict(r.pop('effective_configuration'));passport=passports[r['run_id']]
        r.update(cnn_scope=classify(oldr),evidence_class=V,
            configuration_verification='November3 extraction; source SHA rechecked unchanged; actual receipts rechecked below',
            original_extracted_seed=c.get('seed',U))
        r.update(c)
        for k in ['model_seed','seed_family','outer_fold_zero_based','partition_seed','validation_partition_seed','job_index','split_role','identity_evidence']:
            r[k]=passport.get(k,U)
        for role in ['TRAIN','VALIDATION','CALIBRATION','META_FIT','ASSESSMENT']:
            for tail in ['N','recording_N','cohort_id']:r[role+'_'+tail]=passport.get(role+'_'+tail,U)
        for k,v in list(r.items()):
            if isinstance(v,str) and ('NOT RECORDED' in v or 'NOT VERIFIED' in v):r[k]=U+' — '+v
        r.update(image_dimensions='640x640' if r['cnn_scope'] not in ['SENSOR / CONTROL / OTHER CONTEXT'] else 'N/A or see source',
            dropout=c.get('dropout',U),calibration=c.get('calibration',U),
            source_configuration_path=oldr['configuration_source'])
        if r['cnn_scope'] in ['FULL CNN','FINAL STAGE + MEAN HEAD','FROZEN CNN / TRAINED HEAD']:
            r['frame_count']=32 if '32' in r['model'] else 16
            r['feature_pooling']='spatial means of CNN maps128/256/512, concatenate896; arithmetic frame mean' if not r['model'].startswith('V-') and oldr['experiment_id']!='BOUNDARY_AWARE_VISUAL' else c.get('sampling','see executing source')
        RUNS.append(r)
        if r['cnn_scope']!='SENSOR / CONTROL / OTHER CONTEXT':selected.append(r['run_id'])
    check('all original REASSEMBLE run records have exact current cohort passports',len(RUNS)==6894)
    table('03_COMPLETE_MODEL_CONFIGURATIONS.csv',RUNS)
    fields=['run_id','experiment_id','model','cnn_scope','training_status','model_seed','seed_family','outer_fold_zero_based','inner_fold','split_role','partition_seed','validation_partition_seed','max_configured_epochs','executed_epochs','selected_epoch','TRAIN_N','VALIDATION_N','CALIBRATION_N','META_FIT_N','ASSESSMENT_N','ASSESSMENT_cohort_id','checkpoint_path','history_source']
    table('04_SEED_FOLD_AND_EPOCH_COVERAGE.csv',[{k:r.get(k,U) for k in fields} for r in RUNS])
    groups=[]
    for e,m in sorted({(r['experiment_id'],r['model']) for r in RUNS}):
        rs=[r for r in RUNS if (r['experiment_id'],r['model'])==(e,m)]
        groups.append({'experiment_id':e,'model':m,'scope':rs[0]['cnn_scope'],'records':len(rs),'new_complete_records':sum(r['training_status']=='COMPLETE' for r in rs),
            'reused_records':sum(r['training_status']=='REUSED' for r in rs),'model_seeds':sorted({str(r['model_seed']) for r in rs}),
            'seed_families':sorted({str(r['seed_family']) for r in rs}),'executed_epochs':sorted({str(r.get('executed_epochs',U)) for r in rs}),
            'selected_epochs':sorted({str(r.get('selected_epoch',U)) for r in rs}),'outer_folds':sorted({str(r['outer_fold_zero_based']) for r in rs})})
    table('support/EXPERIMENT_FAMILY_SUMMARY.csv',groups)

def fresh_receipts():
    known_ids={r['original_fit_id'] for r in RUNS if r.get('original_fit_id')};fresh=[];costs=[];parameters=[];checkpoint=[]
    for r in RUNS:
        p=path(r['run_id'])/'complete.json'
        if str(r['experiment_id']).startswith('REASSEMBLE_'):p=path(r['history_source'])
        if p.is_file() and (p.name=='PHASE1_FIT_COMPLETE.json' or (r['experiment_id'].startswith('00_experiments/') and r['model']!='sensor_reference')):
            info=read(p);known_ids.add(info.get('fit_id',info.get('fit_identity')))
            if p.name=='PHASE1_FIT_COMPLETE.json':
                history=info['history'];check('consecutive executed epochs', [h['epoch'] for h in history]==list(range(1,info['executed_epochs']+1)),run_id=r['run_id'])
                r['executed_epochs']=info['executed_epochs'];r['selected_epoch']=info['best']['epoch']
                for h in history:CURVES.append({'run_id':r['run_id'],'experiment_id':r['experiment_id'],'model':r['model'],'seed':info['seed'],'outer_fold':r['outer_fold_zero_based'],'selected_epoch':r['selected_epoch'],**{k:v for k,v in h.items() if k!='host_resources'}})
                train_seconds=info['training_seconds'];valid_seconds=sum(h['validation_seconds'] for h in history);inference=info['inference_calibration_seconds']
                grad=read(p.parent/'PHASE1_FIRST_EPOCH_GRADIENT_UPDATES.json')
                parameters.append({'run_id':r['run_id'],'model':r['model'],'CNN_trainable':grad['CNN_parameters'],'head_trainable':grad['head_parameters'],
                    'CNN_frozen':0 if grad['CNN_parameters'] else 11190112,'affine_policy':'promoted trainable' if grad['CNN_parameters'] else 'frozen buffers',
                    'running_statistics_unchanged':grad['running_statistics_unchanged'],'gradient_scope':sorted({'.'.join(n.split('.')[:4]) for n in grad['gradient_parameters']}),
                    'changed_state_count':len(grad['changed_state_names']),'source':rel(p.parent/'PHASE1_FIRST_EPOCH_GRADIENT_UPDATES.json')})
                q=p.parent/'PHASE1_BEST_MODEL.pt';h=sha(used(q,'selected checkpoint hash only'))
                check('selected checkpoint matches receipt',h==info['selected_model_sha256'],run_id=r['run_id'])
                pred=p.parent/'PHASE1_PREDICTIONS.json';check('predictions match completion receipt',sha(used(pred))==info['predictions_sha256'],run_id=r['run_id'])
                pointer=read(p.parent/'PHASE1_LATEST_EPOCH.json');slot=p.parent/pointer['slot'];sh=sha(used(slot,'recovery checkpoint hash only'))
                check('recovery pointer epoch/hash/identity',sh==pointer['sha256'] and pointer['completed_epoch']==info['executed_epochs'] and pointer['fit_identity']==info['fit_identity'],run_id=r['run_id'])
                for cp,kind,hs in [(q,'SELECTED BEST',h),(slot,'LAST RECOVERY',sh)]:checkpoint.append({'run_id':r['run_id'],'model':r['model'],'path':rel(cp),'kind':kind,'bytes':cp.stat().st_size,'sha256':hs,'selected_epoch':info['best']['epoch'],'last_epoch':info['executed_epochs'],'model_state_available':True,'optimizer_scheduler_RNG':'YES (recovery ZIP metadata; no resume run)' if kind=='LAST RECOVERY' else 'NO — use separate recovery slot','verification':V})
                gp=[h['GPU_compute_percent'] for h in history if h.get('GPU_compute_percent') is not None]
                peak=max(h['peak_allocated_bytes'] for h in history)
                cost={'training_only_hours':train_seconds/3600,'validation_hours':valid_seconds/3600,'inference_calibration_hours':inference/3600,
                    'component_sum_hours':(train_seconds+valid_seconds+inference)/3600,'mean_training_seconds_per_epoch':train_seconds/info['executed_epochs'],
                    'executed_epochs':info['executed_epochs'],'training_actions_presented':sum(h['training_actions'] for h in history),
                    'samples_per_second_training':sum(h['training_actions'] for h in history)/train_seconds,
                    'mean_sampled_training_GPU_compute_percent':float(np.mean(gp)) if gp else U,'peak_allocated_GiB':peak/1024**3,
                    'GPU':'Tesla T4 (saved telemetry/source evidence)','cost_scope':'components; excludes unmeasured checkpoint/launch/retry overhead'}
            else:
                train_seconds=info.get('training_wall_seconds',info.get('training_seconds',U));cost={'training_only_hours':train_seconds/3600 if isinstance(train_seconds,(float,int)) else U,
                    'executed_epochs':info.get('epochs_complete',r.get('executed_epochs',U)),
                    'peak_allocated_GiB':info.get('peak_cuda_bytes',0)/1024**3 if info.get('peak_cuda_bytes') else U,
                    'mean_sampled_training_GPU_compute_percent':U,'cost_scope':'receipt fit wall; cached frozen extraction separate'}
                parameters.append({'run_id':r['run_id'],'model':r['model'],'CNN_trainable':info.get('trainable_backbone_parameters',0),
                    'CNN_frozen':info.get('loaded_backbone_parameters',11190112)-info.get('trainable_backbone_parameters',0),
                    'head_trainable':info.get('head_parameters',U),'affine_policy':'frozen original buffers','running_statistics_unchanged':'source/replay evidence',
                    'gradient_scope':'stage3 + head' if info.get('final_stage_trainable') else 'head only','source':rel(p)})
                cp=info.get('model_reference',str(p.parent/'model.pt'));cp=path(cp)
                if cp.is_file():
                    h=sha(used(cp,'compact model hash only'));expected=info.get('model_sha256')
                    check('compact model saved hash',not expected or h==expected,run_id=r['run_id'])
                    checkpoint.append({'run_id':r['run_id'],'model':r['model'],'path':rel(cp),'kind':'FINAL FIXED EPOCH / COMPACT','bytes':cp.stat().st_size,'sha256':h,
                        'selected_epoch':info.get('epochs_complete',r.get('selected_epoch',U)),'last_epoch':info.get('epochs_complete',r.get('executed_epochs',U)),
                        'model_state_available':True,'optimizer_scheduler_RNG':'Completed optimizer files released for one-day study; others inspect retained inventory','verification':V})
            costs.append({'run_id':r['run_id'],'experiment_id':r['experiment_id'],'model':r['model'],'training_status':r['training_status'],'source':rel(p),**cost})
            fresh.append({'run_id':r['run_id'],'receipt':rel(p),'receipt_sha256':sha(p),'fit_identity':info.get('fit_id',info.get('fit_identity')),'model':r['model'],'executed_epochs':info.get('executed_epochs',info.get('epochs_complete',r.get('executed_epochs',U))),'status':r['training_status']})
    extras=[]
    for item in FILES:
        p=path(item['path'])
        if p.name not in ['complete.json','PHASE1_FIT_COMPLETE.json'] or any(x in p.parts for x in ['tests','before','provenance','temporary']):continue
        j=read(p)
        if not isinstance(j,dict) or not ('fit_id' in j or 'fit_identity' in j):continue
        fid=j.get('fit_id',j.get('fit_identity'))
        if fid in known_ids:continue
        extras.append({'receipt':rel(p),'fit_identity':fid,'condition':j.get('condition',j.get('arm','sensor/context')),
            'epochs':j.get('epochs_complete',j.get('executed_epochs',U)),
            'classification':'OLDER BOOTSTRAP / SUPERSEDED OR SOURCE-REUSED EVIDENCE' if 'parth_ws_bootstrap' in p.parts else 'REQUIRES RECONCILIATION',
            'mtime_utc':item['mtime_utc'],'sha256':sha(p)})
    table('support/CURRENT_FIT_RECEIPT_VERIFICATION.csv',fresh)
    table('support/ADDITIONAL_COMPLETION_RECEIPTS.csv',extras)
    table('support/PARAMETER_AND_GRADIENT_EVIDENCE.csv',parameters)
    table('support/CURRENT_MEASURED_COSTS.csv',costs)
    table('11_CHECKPOINT_INVENTORY.csv',checkpoint)
    table('support/PHASE1_AND_100E_EPOCH_HISTORIES.csv',CURVES)
    print('RECEIPTS',len(fresh),'CHECKPOINTS',len(checkpoint),'EXTRA',len(extras),flush=True)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if sys.argv[-1]=='discover':discover();return
    if sys.argv[-1]=='extract':
        FILES.extend(rows(OUT/'support/CURRENT_ARTIFACT_INVENTORY.csv'))
        configurations();fresh_receipts()
        table('support/EXTRACTION_INPUTS.csv',list(INPUTS.values()))
        table('support/EXTRACTION_CHECKS.csv',CHECKS)
        return
    raise SystemExit('Use discover, then the completed audit entry point.')
if __name__=='__main__':main()
