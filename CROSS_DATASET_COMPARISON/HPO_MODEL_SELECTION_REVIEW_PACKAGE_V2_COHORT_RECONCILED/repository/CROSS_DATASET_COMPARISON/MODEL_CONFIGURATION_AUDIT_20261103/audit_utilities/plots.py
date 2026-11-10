"""Publication-friendly static plots from saved histories/metrics only."""
import csv
import json
import math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from audit_common import OUT,REPO,read,csv_read,csv_write,write,evidence,flush_evidence

plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':170})
MANIFEST=[]


def save(fig,name,rows,sources):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);fig.tight_layout();fig.savefig(p);plt.close(fig)
    csv_write(p.with_suffix('.csv'),rows)
    for s in sources:
        if (REPO/s).is_file():evidence(s,'plot underlying source')
    MANIFEST.append({'figure':str(p.relative_to(OUT)),'plot_source_table':str(p.with_suffix('.csv').relative_to(OUT)),
        'original_sources':list(sources),'data_created_by_training':False,'synthetic_curves':False})


def main():
    histories=csv_read(OUT/'04_training_and_checkpoints/ALL_DATASET_EPOCH_HISTORIES.csv')
    pair=[r for r in histories if r['experiment_id']=='REASSEMBLE_100E_SINGLE_FIT']
    sources={r['history_source'] for r in pair}
    for ykey,ylabel,name in [('training_loss','Training versus validation weighted BCE','100E_LOSS.png'),('validation_AP','VALIDATION average precision','100E_VALIDATION_AP.png')]:
        fig,ax=plt.subplots(figsize=(9,4.8))
        for model,color in [('B_frozen100','#286a9c'),('C_full_finetuned16','#bb4c2b')]:
            rows=sorted([r for r in pair if r['model']==model],key=lambda r:int(r['epoch']))
            ax.plot([int(r['epoch']) for r in rows],[float(r[ykey]) for r in rows],color=color,label=model+(' TRAINING' if ykey=='training_loss' else ' VALIDATION'))
            if ykey=='training_loss':ax.plot([int(r['epoch']) for r in rows],[float(r['validation_loss']) for r in rows],color=color,linestyle='--',label=model+' VALIDATION')
        ax.set(xlabel='Executed epoch',ylabel=ylabel,title='REASSEMBLE: seed42, selected fit3; no HELD-OUT curve');ax.legend(fontsize=8)
        save(fig,'06_dataset_specific/REASSEMBLE/'+name,pair,sources)
    fig,ax=plt.subplots(figsize=(9,4.8));lrrows=[]
    for model in ['B_frozen100','C_full_finetuned16']:
        rows=sorted([r for r in pair if r['model']==model],key=lambda r:int(r['epoch']))
        for i in range(len(json.loads(rows[0]['learning_rates']))):
            values=[json.loads(r['learning_rates'])[i] for r in rows]
            label=model+(' head' if i==0 else ' backbone')
            ax.plot([int(r['epoch']) for r in rows],values,label=label)
            lrrows.extend({'model':model,'epoch':r['epoch'],'optimizer_group':i,'learning_rate':v,'source':r['history_source']} for r,v in zip(rows,values))
    ax.set(xlabel='Executed epoch',ylabel='Recorded learning rate (TRAINING)',yscale='log',title='100-epoch schedules; source optimizer group order');ax.legend(fontsize=8)
    save(fig,'06_dataset_specific/REASSEMBLE/100E_LEARNING_RATES.png',lrrows,sources)
    c20=[r for r in histories if r['experiment_id']=='REASSEMBLE_PHASE1_C20' and r['role']=='outer_assessment']
    fig,axes=plt.subplots(1,2,figsize=(12,4.6))
    for fold in sorted({r['outer_fold'] for r in c20}):
        rs=sorted([r for r in c20 if r['outer_fold']==fold],key=lambda r:int(r['epoch']))
        axes[0].plot([int(r['epoch']) for r in rs],[float(r['training_loss']) for r in rs],label='TRAINING outer'+str(fold))
        axes[1].plot([int(r['epoch']) for r in rs],[float(r['validation_AP']) for r in rs],label='VALIDATION outer'+str(fold))
    axes[0].set(xlabel='Epoch',ylabel='TRAINING weighted BCE');axes[1].set(xlabel='Epoch',ylabel='VALIDATION AP')
    for ax in axes:ax.legend(fontsize=8)
    fig.suptitle('C20 seed42: all five outer refits; cosine50 prefix to20; no HELD-OUT curve')
    save(fig,'06_dataset_specific/REASSEMBLE/C20_OUTER_REFIT_CURVES.png',c20,{r['history_source'] for r in c20})
    # A real ViFit trajectory, no invented validation series for fixed external baselines.
    vi=[r for r in histories if r['dataset']=='VIFAILBACK' and r['model']=='V1' and r['seed']=='42' and r['outer_fold']=='0' and r['role']=='HELD-OUT']
    if vi:
        vi=sorted(vi,key=lambda r:int(r['epoch']));fig,ax=plt.subplots(figsize=(9,4.6))
        for k,label in [('T_weighted_BCE','TRAINING weighted BCE'),('V_weighted_BCE_same_T_positive_weight','VALIDATION weighted BCE')]:
            ax.plot([int(r['epoch']) for r in vi],[float(r[k]) for r in vi],label=label)
        ax.set(xlabel='Epoch',ylabel='Weighted BCE',title='ViFailback V1 seed42 outer0; same T class weight');ax.legend()
        save(fig,'06_dataset_specific/VIFAILBACK/FROZEN_TRAIN_VS_VALIDATION.png',vi,{r['history_source'] for r in vi})
    scores=csv_read(OUT/'05_results/IMPORTANT_HELD_OUT_RESULTS.csv')
    vi=[r for r in scores if r['dataset']=='VIFAILBACK']
    models=['V1','V1_high_only','S3','S2','F1_average','F2','quality_gate','gate_static']
    fig,axes=plt.subplots(1,3,figsize=(14,5))
    for ax,key,title in zip(axes,['AP_failure','AP_success','macro_AP'],['Failure AP','Success AP','Both-class macro AP']):
        for seed,dx in [('42',-.15),('123',0),('20261023',.15)]:
            ys=[float(next(r[key] for r in vi if r['model']==m and r['seed']==seed)) for m in models]
            ax.scatter(np.arange(len(models))+dx,ys,label='seed'+seed,s=28)
        ax.set_xticks(range(len(models)),models,rotation=60,ha='right');ax.set(ylabel='HELD-OUT '+title,ylim=(0,1))
    axes[0].legend(fontsize=8);fig.suptitle('ViFailback: same4382 episodes across seeds; failure prevalence0.856458')
    save(fig,'06_dataset_specific/VIFAILBACK/HELD_OUT_BOTH_CLASSES_BY_SEED.png',vi,set())
    for ds in ['MSM','HANDOVER']:
        # Source mean rows already reconcile all clean primary held-out cases.
        rows=[r for r in scores if r['dataset']==ds];fig,ax=plt.subplots(figsize=(10,4.7))
        ax.bar([r['model'] for r in rows],[float(r['AP']) for r in rows],color='#40799e')
        ax.axhline(float(rows[0]['prevalence']),color='#a7442d',linestyle='--',label='Cohort failure prevalence (reference)')
        ax.set(ylabel='HELD-OUT pooled AP: mean seeds' if ds=='MSM' else 'HELD-OUT AP: mean seeds',ylim=(0,1),title=ds+': matched primary protocol; no cross-dataset ranking')
        ax.tick_params(axis='x',rotation=55);ax.legend(fontsize=8)
        save(fig,f'06_dataset_specific/{ds}/HELD_OUT_MODEL_COMPARISON.png',rows,set(s for r in rows for s in r['source'].split(';')))
        allrows=csv_read(OUT/f'06_dataset_specific/{ds}/COMPLETE_RESULTS.csv')
        primary='EXTERNAL_P_primary__group_id' if ds=='MSM' else 'EXTERNAL_P_official'
        clean=[r for r in allrows if r['experiment_id']==primary and r['evaluation_scope']=='HELD-OUT' and r.get('corruption')=='clean' and r.get('AP')]
        fig,ax=plt.subplots(figsize=(10,4.7));ms=sorted({r['model'] for r in clean});seedrows=[]
        for seed,dx in [('42',-.15),('123',0),('20261023',.15)]:
            values=[]
            for m in ms:
                vals=[float(r['AP']) for r in clean if r['model']==m and r['seed']==seed]
                values.append(float(np.mean(vals)));seedrows.append({'dataset':ds,'model':m,'seed':seed,'mean_fold_AP':float(np.mean(vals)),'folds':len(vals),'scope':'HELD-OUT'})
            ax.scatter(np.arange(len(ms))+dx,values,label='seed'+seed)
        ax.set_xticks(range(len(ms)),ms,rotation=55,ha='right');ax.set(ylabel='HELD-OUT AP (mean folds per seed)',ylim=(0,1),title=ds+': seed variation on reused held-out data');ax.legend(fontsize=8)
        save(fig,f'06_dataset_specific/{ds}/HELD_OUT_SEED_DISTRIBUTIONS.png',seedrows,set(s for r in rows for s in r['source'].split(';')))
    pilot=[r for r in scores if r['study']=='CNN100_STATIC_SENSOR_F2'];fig,ax=plt.subplots(figsize=(10,4.7))
    ax.bar([r['model'] for r in pilot],[float(r['AP']) for r in pilot],color='#6f729a');ax.axhline(77/753,color='#a7442d',linestyle='--',label='Failure prevalence77/753')
    ax.set(ylabel='HELD-OUT AP',ylim=(0,.5),title='REASSEMBLE100e pilot: same753 actions; one selected fold/seed42');ax.tick_params(axis='x',rotation=45);ax.legend()
    save(fig,'06_dataset_specific/REASSEMBLE/100E_SENSOR_VISUAL_FUSION.png',pilot,{r['source'] for r in pilot})
    write(OUT/'provenance/PLOT_MANIFEST.json',MANIFEST);flush_evidence('PLOT_EVIDENCE_LEDGER.json')
    print('PLOTS',len(MANIFEST),flush=True)

if __name__=='__main__':main()
