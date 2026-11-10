"""Render the current audit/handoff and plots from saved evidence only."""
import audit as a
from pathlib import Path
import collections,csv,datetime as dt,importlib.metadata,json,math,os,platform,re,subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def mdtable(rows,fields):
    return '| '+' | '.join(fields)+' |\n| '+' | '.join('---' for _ in fields)+' |\n'+''.join('| '+' | '.join(str(r.get(k,a.U)).replace('|','/').replace('\n',' ') for k in fields)+' |\n' for r in rows)
def link(p):return f'[{p}]({os.path.relpath(a.path(p),a.OUT)})'
def write(name,s):a.write(name,s.strip()+'\n')
def floats(rs,k):return [float(r[k]) for r in rs if r.get(k) not in [None,'',a.U]]

def main():
    cfg=a.rows(a.OUT/'03_COMPLETE_MODEL_CONFIGURATIONS.csv')
    for r in cfg:
        exp,m=r['experiment_id'],r['model']
        mean_head=(r.get('cnn_scope') in ['FULL CNN','FINAL STAGE + MEAN HEAD'] or m in ['rtdetr','B_frozen100','B_long_frozen16','cnn_only','cnn_plus_encoder'] or m.startswith('frozen'))
        if mean_head:
            width=768 if m=='cnn_plus_encoder' else 896
            r.update(head_structure=f'Linear({width},128),ReLU,Dropout(0.1),Linear(128,1)',activation='ReLU; output logit',
                head_trainable_parameters=98561 if width==768 else 114945,input_image_dimensions='640x640 RGB',
                image_preprocessing='bilinear resize; /255; no image mean/std normalization; no padding',
                loss='BCEWithLogitsLoss; gradient-training negative/positive ratio',class_weighting='gradient-training negative/positive ratio',
                batchnorm_running_statistics='fixed original FrozenBatchNorm; never updated',warmup='none',data_augmentations='none')
            r['normalization_affine']='trainable promoted parameters' if r.get('cnn_scope')=='FULL CNN' else 'original frozen buffers'
            r['calibration']='unweighted sigmoid LogisticRegression C1 on C-only logits; max_iter2000' if exp not in ['SECTION1','SECTION1B_NESTED_BRANCHES'] else 'unweighted sigmoid LogisticRegression C1 on selected training-side OOF logits; max_iter1000'
            if exp in ['SECTION1','SECTION1B_NESTED_BRANCHES']:
                r['scheduler']='none / constant AdamW rate';r['early_stopping']='none; candidate5/10 epoch snapshots and inner mean AP selection'
                r['initialization']='fixed original CNN feature bank; fresh seeded classifier head'
            if exp.startswith('00_experiments/') or exp=='BOOTSTRAP_SUPERSEDED_FINALSTAGE5':r['scheduler']='none / fixed final epoch'
    a.table('03_COMPLETE_MODEL_CONFIGURATIONS.csv',cfg)
    histories=a.rows(a.OUT/'support/PHASE1_AND_100E_EPOCH_HISTORIES.csv')
    allhist=a.rows(a.OUT/'support/ALL_CNN_EPOCH_HISTORIES.csv')
    costs=a.rows(a.OUT/'support/CURRENT_MEASURED_COSTS.csv')
    grid=a.rows(a.OUT/'08_STATIC_SENSOR_AND_F2_RESULTS.csv')
    results=a.rows(a.OUT/'support/ALL_RECOMPUTED_CLEAN_RESULTS.csv')
    current=a.read(a.OUT/'support/CURRENT_CONTROLLER_AND_COMPLETION_STATUS.json')
    proof=a.read(a.OUT/'support/CURRENT_SUBSET_AND_ROLE_PROOF.json')
    cp=a.rows(a.OUT/'11_CHECKPOINT_INVENTORY.csv')
    # Record process matches only, never complete command lines.
    pattern=r'(^|/)c20_controller[.]py|(^|/)c20_train[.]py|(^|/)phase_training[.]py|(^|/)compare100_train[.]py'
    proc=subprocess.run(['pgrep','-f',pattern],capture_output=True,text=True)
    current['matching_live_primary_controller_or_fit_PIDs']=[int(v) for v in proc.stdout.split() if v.isdigit()]
    current['live_process_query_utc']=dt.datetime.now(dt.timezone.utc).isoformat();a.write('support/CURRENT_CONTROLLER_AND_COMPLETION_STATUS.json',current)
    # Plot existing histories, explicitly mark selected epochs.
    (a.OUT/'figures').mkdir(exist_ok=True)
    plt.rcParams.update({'font.size':10,'figure.dpi':120})
    arms=[('B_frozen100','Frozen100'),('C_full_finetuned16','Full100')]
    fig,axs=plt.subplots(1,2,figsize=(11,4))
    diagnostic=[]
    for model,label in arms:
        rs=[r for r in histories if r['experiment_id']=='REASSEMBLE_100E_SINGLE_FIT' and r['model']==model];assert len(rs)==100
        e=np.array([int(r['epoch']) for r in rs]);sel=int(rs[0]['selected_epoch'])
        for key,name in [('training_loss','Training weighted BCE'),('validation_loss','Validation weighted BCE')]:axs[0].plot(e,[float(r[key]) for r in rs],label=label+' '+name)
        axs[1].plot(e,[float(r['validation_AP']) for r in rs],label=label);axs[1].scatter([sel],[float(rs[sel-1]['validation_AP'])],marker='*',s=100)
        diagnostic.append({'model':model,'executed_epochs':100,'selected_epoch':sel,
            'selected_train_loss':rs[sel-1]['training_loss'],'selected_validation_loss':rs[sel-1]['validation_loss'],
            'selected_validation_AP':rs[sel-1]['validation_AP'],'final_train_loss':rs[-1]['training_loss'],
            'final_validation_loss':rs[-1]['validation_loss'],'final_validation_AP':rs[-1]['validation_AP']})
    axs[0].set_yscale('log');axs[0].set_ylabel('Weighted BCE (log scale)');axs[1].set_ylabel('Validation AP');axs[1].set_ylim(0,None)
    for ax in axs:ax.set_xlabel('Completed epoch');ax.legend(fontsize=7);ax.grid(alpha=.2)
    fig.suptitle('Saved100-epoch histories; stars mark validation-selected checkpoints');fig.tight_layout();fig.savefig(a.OUT/'figures/100E_LOSS_AND_VALIDATION_AP.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4))
    for model,label in arms:
        rs=[r for r in histories if r['experiment_id']=='REASSEMBLE_100E_SINGLE_FIT' and r['model']==model]
        for k in range(len(json.loads(rs[0]['learning_rates']))):ax.plot([int(r['epoch']) for r in rs],[json.loads(r['learning_rates'])[k] for r in rs],label=label+(' head' if k==0 else ' CNN'))
    ax.set_yscale('log');ax.set_xlabel('Epoch (logged start-of-epoch LR)');ax.set_ylabel('Learning rate');ax.legend();fig.tight_layout();fig.savefig(a.OUT/'figures/100E_ACTUAL_LEARNING_RATES.png');plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(11,4))
    c20cfg=[r for r in cfg if r['experiment_id']=='REASSEMBLE_PHASE1_C20' and r['split_role']=='outer_assessment']
    for r in c20cfg:
        hs=[h for h in histories if h['run_id']==r['run_id']];k=int(r['outer_fold_zero_based']);s=int(r['selected_epoch'])
        axs[0].plot([int(h['epoch']) for h in hs],[float(h['validation_AP']) for h in hs],label=f'outer{k} / selected{s}')
        axs[0].scatter([s],[float(hs[s-1]['validation_AP'])],marker='*',s=65)
        axs[1].plot([int(h['epoch']) for h in hs],[float(h['validation_loss']) for h in hs],label=f'outer{k}')
    axs[0].set_ylabel('Validation AP');axs[1].set_ylabel('Validation weighted BCE');axs[1].set_yscale('log')
    for ax in axs:ax.set_xlabel('Completed epoch');ax.legend(fontsize=7);ax.grid(alpha=.2)
    fig.suptitle('C20 outer refits:20 executed epochs on unchanged cosine50 prefix');fig.tight_layout();fig.savefig(a.OUT/'figures/C20_OUTER_REFITS.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4));legacy=[]
    for model in ['frozen_16_frames','frozen_32_frames','fine_tuned_16_frames','fine_tuned_32_frames']:
        hs=[h for h in allhist if h['model']==model and 'visual_backbone_one_day' in h['experiment_id']]
        byepoch=collections.defaultdict(list)
        for h in hs:
            value=next((h[k] for k in ['training_loss','training_BCE_mean','train_loss'] if h.get(k)),None)
            if value:byepoch[int(h['epoch'])].append(float(value))
        if byepoch:ax.plot(sorted(byepoch),[np.mean(byepoch[k]) for k in sorted(byepoch)],marker='o',label=model)
        legacy.extend(hs)
    ax.set_xlabel('Epoch');ax.set_ylabel('Mean logged training BCE across fits');ax.legend(fontsize=8);ax.set_title('Historical asymmetric5/2 budgets; no held-out selection implied');fig.tight_layout();fig.savefig(a.OUT/'figures/HISTORICAL_FIXED_BUDGET_LOSSES.png');plt.close(fig)
    a.table('support/100E_SELECTED_AND_FINAL_DIAGNOSTICS.csv',diagnostic)
    # Machine-readable source-grounded recipe inventory. These are not target-dataset runs.
    shared={'pretrained_model':'PekingU/rtdetr_r18vd','revision':'ac77a11ff0170a41b771c03264987f8ce2b0d753','frames':16,'resolution':[640,640],
        'preprocessing':'RGB bilinear resize640x640; /255; do_normalize=False; do_pad=False',
        'forward':'wrapper.model.backbone.model only; no RT-DETR hybrid encoder, decoder, proposals or detection heads',
        'pooling':'per-map spatial mean -> concat128+256+512=896 -> arithmetic frame mean',
        'head':'896 -> Linear128 -> ReLU -> Dropout0.1 -> Linear1; logit output','head_parameters':114945,
        'feature_normalization':'fit only proper gradient-training subset; fixed mean/std, floor1e-6, nonfinite transformed values0',
        'optimizer':'AdamW','head_lr':.001,'weight_decay':.001,'clip_grad_norm':1.,'warmup':'none','augmentations':'none',
        'loss':'BCEWithLogits; pos_weight=T negatives/T positives','initialization':'original pinned CNN and fresh seeded head; resume only same-fit recovery',
        'evaluation_unit':'native completed action; failure1/success0','grouping':'recording;5 outer /4 inner','threshold_policy':'preserve native trained threshold or explicitly common0.5; never mix'}
    recipes={}
    for name,scope,batch,H,maxe,entry in [
        ('ORIGINAL_FROZEN16','FROZEN CNN',128,None,'inner max10; outer selected5/10','src/reassemble/section1_models.py::main/evaluate_model'),
        ('C20_FULL_CNN','FULL CNN',8,50,20,str(a.BASE/'26102026_c_only_20epoch_revision_01/26102026_source/c20_train.py')),
        ('FROZEN100','FROZEN CNN CACHED',8,100,100,str(a.BASE/'26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_source/compare100_train.py')+' --arm B_frozen100'),
        ('FULL100','FULL CNN',8,100,100,str(a.BASE/'26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_source/compare100_train.py')+' --arm C_full_finetuned16')]:
        original=name=='ORIGINAL_FROZEN16';full=scope=='FULL CNN'
        recipes[name]={**shared,'CNN_training_scope':scope,'CNN_trainable_parameters':11199968 if full else 0,'CNN_frozen_parameters':0 if full else 11190112,
            'normalization_affine':'trainable;9856 buffers promoted' if full else 'fixed original buffers','running_statistics':'fixed unchanged FrozenBatchNorm',
            'backbone_lr':1e-5 if full else 0,'effective_batch_actions':batch,'microbatch_actions':1 if batch==8 else '128-vector head batch',
            'gradient_accumulation':'up to8 one-action losses; actual partial batch denominator' if batch==8 else 'none',
            'precision':'FP32 head on FP16-autocast extracted frozen features' if original else 'FP32 end-to-end/full; frozen arm reads original FP32 cached features',
            'betas':'UNKNOWN historical framework default' if original else [.9,.999],'eps':'UNKNOWN historical framework default' if original else 1e-8,
            'maximum_epochs':maxe,'scheduler':'constant' if original else {'kind':'LambdaLR cosine','horizon':H,'factor':'0.1+0.45*(1+cos(pi*t/H))','step':'after each completed epoch'},
            'early_stopping':'none; inner duration selection' if original else False,
            'checkpoint_selection':'mean4-inner AP chooses5/10; independent outer refit to selected duration' if original else 'highest V AP, then lower V weighted BCE, then earliest epoch',
            'calibration':'unweighted sigmoid LR C1 on selected inner OOF logits; max_iter1000' if original else 'separate recording-disjoint C logits; unweighted sigmoid LR C1 max_iter2000',
            'model_seeds':'base20260927 plus saved role/fold offsets' if original else 42,'predefined_full_study_seeds':[42,123,20261023] if name=='C20_FULL_CNN' else 'not a new target design',
            'completed_scope':'5 outer folds' if original or name=='C20_FULL_CNN' else 'one selected original job2 -> outer0/753 actions',
            'T_V_C_E':'original nested training/OOF roles' if original else 'per-job T/V/C + outer held-out; exact saved role IDs' if name=='C20_FULL_CNN' else [1752,419,686,753],
            'entry_point':entry,'workers':4 if not original else 'cached head no pixel loader','decoder_threads':2 if full else 'extraction separate',
            'pin_memory':True if not original else 'N/A cached head','persistent_workers':True if full else 'N/A cached head','prefetch_factor':2 if full else 'N/A cached head',
            'expected_outputs':['effective config + input/split hashes','all epoch histories','validation-selected checkpoint/hash','last recovery pointer with optimizer/scheduler/RNG where supported','calibrator','keyed held-out probabilities','metrics + cost telemetry'],
            'provenance':['source hashes/Git revision + dirty state','pretrained identity','native action/recording/role IDs','actual RNG seeds','frame/pixel hashes','selected epoch and checkpoint SHA256','all threshold/uncertainty conventions']}
    recipes['STATIC_SENSOR']={'features':220,'input_channels':22,'statistics_per_channel':['mean','std','median','min','max','q25','q75','range','RMS','normalized-progress slope'],
        'input_resampling':'512 normalized-progress points from aligned action interval; preserve source implementation',
        'normalizer':'training-only per-feature moments; std floor1e-6; transformed nonfinites0','classifier':'balanced L2 LogisticRegression',
        'C_original':[.1,1.,10.],'C_phase1_and_legacy':1.,'max_iter':2000,'random_state_original':0,'random_state_legacy':42,
        'calibration':'unweighted sigmoid LR on training-side OOF (original), or separate C (legacy); no outer labels',
        'important_difference':'canonical original sensor AP0.4293918694 differs from legacy fixed-C1 G/C sensor AP0.4208028940; do not substitute them'}
    recipes['F2']={'equation':'p_failure = sigmoid(b + w_v*p_visual + w_s*p_sensor)','inputs':'calibrated probabilities in [visual,sensor] order, not logits',
        'estimator':'unweighted L2 LogisticRegression C1, lbfgs, max_iter2000','original_estimator_seed':0,'legacy_estimator_seed':42,
        'extra_scaling_or_fused_calibrator':'none','training':'training-side cross-fitted inner branch probabilities; exclude each row recording from base fitting/calibration/selection',
        'original_design':'nested4-inner branch reconstruction; all5 outer F2 models saved',
        'CNN100_followup':'one920-action base-held-out stacking bank ->753 outer assessment, not full4-inner CNN100 OOF',
        'C20_status':'NOT EXECUTED; existing finalize() asserts75 complete fits'}
    a.write('support/SOURCE_GROUNDED_RECIPE_INVENTORY.json',recipes)
    # Main figures and per-family coverage are readable without opening large CSVs.
    def cost_sum(exp,k):return sum(float(r[k]) for r in costs if r['experiment_id']==exp and r.get(k) not in [None,'',a.U] and r['training_status']!='REUSED')
    c20hours=cost_sum('REASSEMBLE_PHASE1_C20','training_only_hours');c20components=cost_sum('REASSEMBLE_PHASE1_C20','component_sum_hours')
    trainrows=[
        {'Model':'Original frozen16','CNN scope':'head only','Frames':16,'Configured epochs':'inner5/10 candidates','Executed epochs':'20 inner×10; outer5/5/10/10/5','Selected epoch':'outer5/5/10/10/5','Seeds':'base20260927 + role offsets','Outer folds':'5/5','Training hours':'UNKNOWN (mixed fold wall retained)','Status':'COMPLETE'},
        {'Model':'Historical frozen16/32','CNN scope':'head only','Frames':'16 /32','Configured epochs':5,'Executed epochs':'5 each;25 fits/condition','Selected epoch':5,'Seeds':'family42; actual role seeds in CSV','Outer folds':'5/5','Training hours':'0.164 /0.160 fit wall; extraction separate','Status':'COMPLETE'},
        {'Model':'Historical adapted16/32','CNN scope':'stage3 + head','Frames':'16 /32','Configured epochs':2,'Executed epochs':'2 each;25 fits/condition','Selected epoch':2,'Seeds':'family42; actual role seeds in CSV','Outer folds':'5/5','Training hours':'9.086 /12.456 fit wall','Status':'COMPLETE; unequal budget'},
        {'Model':'Matched frozen32/adapted32','CNN scope':'head /stage3+head','Frames':32,'Configured epochs':2,'Executed epochs':'75 new +25 reused fits','Selected epoch':2,'Seeds':'42,20261023 families','Outer folds':'5/5 per seed','Training hours':f'{cost_sum("00_experiments/frozen32_vs_finetuned32_fusion_diagnosis/results","training_only_hours"):.6f} new-fit wall','Status':'COMPLETE; equal epochs, not compute'},
        {'Model':'C20 full CNN','CNN scope':'all convolutions + affine','Frames':16,'Configured epochs':20,'Executed epochs':'25×20=500','Selected epoch':'outer19,20,19,20,20','Seeds':42,'Outer folds':'5/5 +20 inner','Training hours':f'{c20hours:.6f}','Status':'APPROVED25 CAP COMPLETE'},
        {'Model':'Frozen100','CNN scope':'head only /cached CNN','Frames':16,'Configured epochs':100,'Executed epochs':100,'Selected epoch':14,'Seeds':42,'Outer folds':'outer0 only','Training hours':'0.060992','Status':'COMPLETE PILOT'},
        {'Model':'Full100','CNN scope':'all convolutions + affine','Frames':16,'Configured epochs':100,'Executed epochs':100,'Selected epoch':47,'Seeds':42,'Outer folds':'outer0 only','Training hours':'23.964191','Status':'COMPLETE PILOT'},
        {'Model':'V-FT temporal','CNN scope':'stage3 + trained temporal transformer','Frames':16,'Configured epochs':'cap20 /patience5','Executed epochs':'8,7,9,15 inner;4 refit','Selected epoch':'3,2,4,10 inner;4 refit','Seeds':20260927,'Outer folds':'outer0 only','Training hours':'fit wall in source metadata; training-only UNKNOWN','Status':'LIMITED HISTORICAL EXTENSION'},
        {'Model':'Superseded bootstrap adaptation','CNN scope':'stage3 + head','Frames':16,'Configured epochs':5,'Executed epochs':'one inner fit×5','Selected epoch':5,'Seeds':'family42 /role seed saved','Outer folds':'no complete outer evaluation','Training hours':'source receipt only','Status':'SUPERSEDED; not new post-Nov3 work'}]
    a.table('support/TABLE1_CNN_TRAINING.csv',trainrows)
    visualrows=[]
    for r in results:
        if ((r['experiment_id']=='REASSEMBLE_PHASE1_C20' and r['N']=='4530') or r['experiment_id']=='REASSEMBLE_100E_SINGLE_FIT' or
            (r['experiment_id']=='runs/reassemble/20260927T154732Z-section1' and r['model']=='rtdetr_perm00' and r['N'] in ['4530','753'])):
            visualrows.append({'Model':r['experiment_id']+' / '+r['model'],'Seed':r['seed'],'Fold':r['fold'],'Actions':r['N'],'AP':f'{float(r["AP"]):.10f}','AUROC':f'{float(r["AUROC"]):.10f}',
                'Uncertainty':'paired100 gain conditional; see interval table' if '100E' in r['experiment_id'] else 'no new CI; original saved intervals in support','Status':a.V})
    a.table('support/TABLE2_KEY_VISUAL_RESULTS.csv',visualrows)
    fusionrows=[]
    for r in grid:
        if r['assessment_N']=='4530' or r['CNN_condition'] in ['FROZEN100','FULL100'] or (r['CNN_condition']=='ORIGINAL FROZEN16' and r['assessment_N']=='753'):
            fusionrows.append({'Visual condition':r['CNN_condition'],'Sensor condition':'canonical original LR' if r['CNN_condition'] in ['ORIGINAL FROZEN16','C20 FULL CNN','FROZEN100','FULL100'] else 'legacy fixed-C1 G/C LR',
                'Sensor AP':r['static_sensor_AP'],'F2 AP':r['F2_AP'],'F2 minus sensor':r['F2_minus_sensor'],
                'Frozen vs tuned F2 difference':'+0.0141168686 [-0.0007726,0.0290893]' if r['CNN_condition']=='FULL100' else 'see same-seed paired contrasts; not cross-protocol',
                'Coverage':r['assessment_N']+' /seed'+r['seed'],'Status':r['fusion_completion_status']})
    a.table('support/TABLE3_FUSION_RESULTS.csv',fusionrows)
    reproducibility=[
        {'Model':m,'Source':'YES','Configuration':'YES; unknown defaults flagged','Checkpoint':c,'History':h,'Predictions':'YES','Evaluation verification':v}
        for m,c,h,v in [('Original frozen16','5 outer heads + pinned CNN; inner states not all retained','loss traces; no full per-epoch validation loss','current saved-bank AP and labels'),
        ('Final-stage16/32','compact stage/head; original frozen prefix required','fixed2/5 epoch losses','hashes; saved replay evidence; CPU representative loads'),
        ('Matched2','75 new +25 reused identities','two-epoch curves','saved scores and original paired intervals'),
        ('C20','25 best + recovery pointers hash checked','500 epoch rows','current visual predictions; F2 NOT EXECUTED'),
        ('Frozen100 /Full100','both best/recovery verified; CPU payloads load','all200 rows','current saved predictions; no new neural forward'),
        ('CNN100 F2','two fitted small states and coefficients','not neural; fit metadata','keyed probabilities and existing paired intervals')]]
    a.table('support/TABLE4_REPRODUCIBILITY.csv',reproducibility)
    remaining=[
        {'Task':'C20 F2','Actual blocker':'finalize() asserts75; capped run intentionally stopped at25','Evidence/action required':'separately versioned25-fit analysis admission + existing inner predictions; no changes made','New training needed':'CPU F2 fitting YES; CNN NO','Scientific justification':'would answer specified C20 fusion question; not executed here'},
        {'Task':'C20 seeds123 and20261023','Actual blocker':'explicit50-fit deferral','Evidence/action required':'new scope authorization and saved50 additional fit chains','New training needed':'YES','Scientific justification':'needed only for the original multi-seed stability estimand; not required to complete approved25 cap'},
        {'Task':'Additional100-epoch folds/seeds','Actual blocker':'only selected seed42/outer0 pilot was run','Evidence/action required':'predefined matched cohorts and independently initialized repetitions','New training needed':'YES','Scientific justification':'required for a broader100-epoch effect claim; no such claim supported now'},
        {'Task':'Historical25-source-epoch donor check','Actual blocker':'validator rejects executed20 even with valid C20 receipt/hash','Evidence/action required':'explicit versioned compatibility decision if transfer is later authorized','New training needed':'NO to identify mismatch; no retraining implied','Scientific justification':'protocol compatibility issue, not checkpoint corruption'},
        {'Task':'Vi75-fit scheduling gate','Actual blocker':'requires75 completion marker + final metric hash; approved25 stop does not create it','Evidence/action required':'explicit scheduling/scope reconciliation outside this audit','New training needed':'NO for diagnosis','Scientific justification':'a waiting marker is not active model training'},
        {'Task':'Confirmatory superiority claim','Actual blocker':'exposed test folds, limited seeds; fixed-model intervals','Evidence/action required':'independent evidence accounting for selection/refitting uncertainty','New training needed':'not performed / depends on separate study','Scientific justification':'cannot be inferred from highest observed AP'}]
    a.table('support/TABLE5_REMAINING_EXPERIMENTS.csv',remaining)
    write('01_EXECUTIVE_STATUS.md',f'''# REASSEMBLE fine-tuning: current verified status

Audit client date: **2026-11-10, Europe/Berlin**. This audit used saved artifacts, source inspection, CPU tensor metadata inspection and CPU probability arithmetic. No training, neural inference, controller restart, checkpoint/configuration modification, Git staging, commit or push occurred.

## What has actually completed?

The original frozen reference has five-fold results. The asymmetric5/2-epoch16/32-frame study is complete. The matched two-epoch32-frame study has75 new and25 reused visual fits across two seed families and five outer folds each. C20 has **25/25 approved fits**, each20 epochs, seed42,20 inner fits and5 outer refits; it is **not75/75**. Frozen100 and Full100 each executed100 epochs on one selected seed42 recipe; selected epochs are14 and47. Their static-sensor F2 follow-up is complete on753 outer actions using a separate920-action stacking bank. **C20 F2 has not executed.**

There are no matching live primary controller/fit PIDs in the current process-name query: `{current['matching_live_primary_controller_or_fit_PIDs']}`. The recorded controller PID is absent. The approved status is STOPPED_AFTER_25_COMPLETED_FITS; it is a completed capped scope, not a failed fit. Seeds **123 and20261023** are deferred. These seed values come from the actual configuration; similarly named historical studies use different seed families.

All4,713 previously reconciled source files found in the searched execution roots retain their November3 SHA256. No new full-CNN completion receipt was found. One additional **older2026-10-20 superseded five-epoch inner adaptation** was identified outside that prior run table; it is separately included, making6,895 run/context records in the new configuration table rather than inventing a new completed study. Full discovery exclusions and provenance are retained.

## Key results and interpretation

- Original pooled visual/sensor/F2 AP: **0.2306583150 /0.4293918694 /0.4472985514**, on4,530 actions.
- C20 pooled visual AP: **0.3121270257**, AUROC0.7563855574, on the same4,530 held-out actions; different fitting recipe and only one model seed. C20 F2 is NOT EXECUTED.
- On identical753 outer actions, Frozen100/Full100 visual AP is **0.1937755776 /0.2125845033**. Original frozen visual on these same actions is0.2328051167. These are distinct recipes.
- Frozen100/Full100 F2 AP is **0.3349773516 /0.3490942201**, against canonical sensor0.3277045645 and original nested F2 on the same fold0.3671552457. The full-minus-frozen F2 interval **[-0.0007726,0.0290893]** crosses zero; neither improvement nor equivalence is established.
- The753 actions/26 recordings form exactly outer fold0 within4,530 actions/148 recordings. The920 inner actions/28 recordings are disjoint from that outer set. A stale prediction_recordings field is preserved and flagged.
- C20 measured training-only time totals **{c20hours:.6f}h** for500 completed epochs; measured component sum is **{c20components:.6f}h**, excluding unmeasured overhead. Full100 training is23.964191h. Pair active process wall is25.893729h, not pure kernel GPU-hours.

## Evidence classes

**VERIFIED FROM SOURCE/ARTIFACTS:** current receipt/hash chains, executed epoch sequences, CPU-loadable selected tensor payloads, stage changes against original CNN, native split identities and saved-probability metrics. **REPORTED BUT NOT INDEPENDENTLY REPRODUCED:** historical gradient/reload/runtime/recording-bootstrap results retained with original paths; no new neural replay or bootstrap. **INFERRED:** practical inference/restart feasibility from saved shapes, source and retained recovery structure where not exercised. **NOT EXECUTED:** C20 F2, deferred seeds and additional100-epoch folds. **UNKNOWN:** unrecovered historical optimizer literals, missing stage-specific timing and missing historical per-epoch validation fields. These classes must not be conflated.

The evidence is sufficient to specify a controlled methodological handoff; it does not select an HPO winner or remove dataset-specific differences. See [the recipe handoff](13_REASSEMBLE_TO_VIFAILBACK_RECIPE_HANDOFF.md), [all configurations](03_COMPLETE_MODEL_CONFIGURATIONS.csv) and [researcher tables](15_RESEARCHER_HANDOFF.md).
''')
    family=a.rows(a.OUT/'support/EXPERIMENT_FAMILY_SUMMARY.csv')
    write('02_ALL_FINETUNING_EXPERIMENTS.md','''# Experiment inventory and distinct scientific units

The following groups are separate experiments; shared CNN names are not evidence of shared training, fitting roles or checkpoints. Source scans also cover configs/src/runs, original bootstrap references, encoder probes, boundary models, temporal models and fusion context. The source-delta table records unchanged inputs; current file inventory and extra receipts identify possible omissions. Raw datasets, caches, synthetic fixtures and copied report/source snapshots are excluded from scientific completion counts.

'''+mdtable(trainrows,list(trainrows[0]))+'''

## Additional frozen/temporal/encoder context

V-MEAN, V-TEMP and V-NOPOS each have75 fit records (three nominal seeds, five outer/four inner jobs). These train cached-feature mean/temporal heads, not a full CNN. The temporal head is a separately trained one-layer128-dimensional, four-head transformer; it is not RT-DETR's hybrid encoder. Boundary V0–V5 train mean/bin/GRU heads over frozen CNN features and are separately inventoried. F3–F6 and modality-dropout train fusion heads over cached branches. The encoder probe compares896-dimensional CNN-only features with768-dimensional CNN-plus-hybrid-encoder features; its frozen heads have114,945 and98,561 parameters respectively. It executes the hybrid encoder for the probe, but not the decoder/detection heads. It is not the CNN-only backbone condition.

Historical temporal V-FT executes only the last spatial stage plus a warm-started temporal transformer head; its5 fits cover one outer fold, not five outer folds. It uses AMP, head LR1e-4, pretrained LR1e-5, effective batch128 and cap20/patience5, unlike fresh mean-head FP32 C20/Full100. Its observed stopped/selected epochs are listed above.

The newly listed bootstrap5-epoch adaptation completed only one inner fit and was superseded by the separate two-epoch study. Its report/receipt must not be treated as a new post-November3 experiment or a five-fold result. Aliased/reused fits and label-shift controls remain visible in the configuration/coverage CSVs; controls are not independent seeds.

Full per-family counts: [EXPERIMENT_FAMILY_SUMMARY.csv](support/EXPERIMENT_FAMILY_SUMMARY.csv). Every exact fitting role and native cohort is in [03](03_COMPLETE_MODEL_CONFIGURATIONS.csv), [04](04_SEED_FOLD_AND_EPOCH_COVERAGE.csv) and the [cohort registry](support/EXACT_COHORT_REGISTRY.csv).
''')
    write('05_TRAINABLE_PARAMETER_AUDIT.md','''# Executed architecture and trainable-parameter audit

Pinned source: **PekingU/rtdetr_r18vd**, revision **ac77a11ff0170a41b771c03264987f8ce2b0d753**. [Pinned file hashes](support/PINNED_PRETRAINED_IDENTITY.json) include model.safetensors, config and preprocessor. Original paths are relative to the repository, including the external read-only pretrained folder.

The core forward is `RTDetrForObjectDetection(...).model.backbone.model(pixel_values).feature_maps`. Only the ResNet CNN executes. Spatial means of the final three maps (128,256,512 channels) concatenate to896 values per frame, followed by arithmetic frame averaging. The classifier is Linear896→128, ReLU, Dropout0.1, Linear128→1, with114,945 trainable head parameters. A separate sigmoid calibrator produces failure probabilities. The RT-DETR hybrid transformer encoder, decoder, detection proposals and detection heads are not executed in the original/C20/Frozen100/Full100 mean-head conditions. Loading their archive tensors does not mean executing them.

| Condition | Trainable CNN parameters | Frozen CNN parameters | Trainable head | Normalization affine | Running statistics |
|---|---:|---:|---:|---|---|
| Frozen mean-head |0|11,190,112|114,945|original fixed buffers|fixed|
| Final spatial-stage mean-head |8,388,608|2,801,504|114,945|original fixed buffers|fixed|
| Full CNN C20/Full100 |11,199,968|0|114,945|9,856 affine buffer elements promoted to Parameters|fixed|

The full trainable total is11,314,913. Frozen CNN parameter counts exclude normalization affine buffers; full-CNN counts include their promotion. This explains the9,856-element difference without changing state-dict names or inventing extra convolutional layers. Feature normalizer mean/std are fixed buffers, never learned through optimization.

C20/Full100 optimize the embedder/stem and CNN stages0–3 plus the head. First-epoch saved evidence has finite/nonzero gradients and parameter changes in every executed stage; original normalization running statistics are unchanged. This audit additionally compared all28 selected Phase1/pilot payloads against pinned original pretrained tensors on CPU: full conditions change every stage; representative final-stage compact payloads change only stage3; running means/variances remain unchanged. Source plus optimizer groups establish scope; the experiment names alone were not used as proof.

All42 selected/representative checkpoint payloads passed weights-only CPU loading and finite-tensor inspection. No fresh model construction, forward or update was performed. Inference replay and restart equivalence are historical reported evidence, not newly reproduced here. Recovery optimizer/scheduler/RNG presence was verified using static pickle opcodes without executing pickle.

Initialization for C20 and both100-epoch arms is fresh original pretrained CNN/fresh seeded head. Recovery resumes only the same fit; Full100 is not a continuation of a C20 selected checkpoint. Historical temporal V-FT warm-starts a previously trained TemporalHead and remains a different recipe. Encoder-probe and temporal-head transformer exceptions are described in [02](02_ALL_FINETUNING_EXPERIMENTS.md).

Sources: [source extract index](support/SOURCE_EXTRACT_INDEX.csv), [per-fit gradient/parameter evidence](support/PARAMETER_AND_GRADIENT_EVIDENCE.csv), [CPU tensor inspection](support/CHECKPOINT_CPU_TENSOR_INSPECTION.json), [actual stage changes](support/CHECKPOINT_ACTUAL_STAGE_CHANGES.csv).
''')
    write('06_TRAINING_CURVES_AND_CHECKPOINT_SELECTION.md','''# Training histories, selection and overfitting

[PHASE1_AND_100E_EPOCH_HISTORIES.csv](support/PHASE1_AND_100E_EPOCH_HISTORIES.csv) contains725 freshly extracted rows:500 C20,200 matched100-epoch arms and25 original long-frozen epochs. Each receipt was checked for consecutive epoch coverage. [ALL_CNN_EPOCH_HISTORIES.csv](support/ALL_CNN_EPOCH_HISTORIES.csv) retains14,721 available original/legacy/temporal/encoder/boundary CNN-related epoch rows. Missing validation loss/AP is UNKNOWN, not a fabricated zero or a recomputed training evaluation.

![Saved100-epoch losses and validation AP](figures/100E_LOSS_AND_VALIDATION_AP.png)

![Actual logged100-epoch learning rates](figures/100E_ACTUAL_LEARNING_RATES.png)

![C20 outer refit curves](figures/C20_OUTER_REFITS.png)

![Historical fixed-budget losses](figures/HISTORICAL_FIXED_BUDGET_LOSSES.png)

## Validation selection

C20/Frozen100/Full100 choose the lexicographic maximum `(validation_AP, -validation_weighted_BCE, -epoch)`. Thus ties prefer smaller validation loss, then the earliest epoch. Calibration is subsequently fitted on separate C recordings; outer assessment labels never select the checkpoint within a fit. C20 executes exactly20 epochs on the original cosine50 prefix;100-epoch arms use a fresh cosine100 schedule and execute all100 epochs. Neither stops early. The retained original long-frozen B executed25 epochs, selected9, under minimum25/patience10/max50; it is an inner-fit historical comparator, not a complete five-fold B20 study.

Original frozen reference chooses5 or10 epochs by mean training-side inner AP, then independently refits the outer model to that duration. Its selected outer durations are5,5,10,10,5. Inner heads may execute10 epochs while their selected prediction snapshot is5. Legacy asymmetric and matched2 studies use fixed final epochs plus separate calibration; they do not use100-epoch validation selection.

## Observed generalization gap

'''+mdtable(diagnostic,list(diagnostic[0]))+'''

By epoch100, frozen training weighted BCE is0.005231 versus validation17.493164; full-CNN training BCE is approximately1.425e-9 versus validation26.145111. These large gaps support substantial overfitting under the saved recipe. The held-out predictions come from epochs14 and47, not epoch100. Full100's terminal validation AP is not its selected AP. Class-weighted training and validation loss uses training-derived class weights; loss gaps are diagnostic, not direct AP differences or probabilities.

C20 outer selected epochs are19,20,19,20,20; inner selected epochs range1–20. Some maxima at20 mean the finite cap bounds what can be inferred about longer optimization, not proof of convergence or a need to train longer. Actual finite losses/gradients and completed receipts establish numerical execution, not global convergence. Full100 had two interrupted/failed process attempts before the completed third attempt; completed recovery epochs were preserved. Those process exits are not evidence that the final scientific fit failed. No numerical convergence result is invented where only training-loss traces survive.
''')
