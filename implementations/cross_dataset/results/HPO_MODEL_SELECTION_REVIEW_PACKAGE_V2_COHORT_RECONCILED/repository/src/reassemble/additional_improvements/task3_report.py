"""Complete the clean anchored-adaptation report without changing fitted results."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reassemble.section1_features import cohort
from reassemble.section1_report import METRICS,metrics,table
from .common import config,read,write,progress,identity

def main():
    c=config();root=Path(c['run_dir']);task=root/'03_static_anchored_adaptation';base=read(c['section1_config']);frame=cohort(base);y=frame.failure.to_numpy(int)
    with np.load(task/'predictions.npz') as z:pred={k:z[k] for k in z.files}
    result=read(task/'comparison/results.json');ablations={};coefficient_records=[];seedfold=[]
    for name in ['A0','A-CONSTANT','A-ADAPTIVE']:
        for s,seed in enumerate(c['seeds']):
            for fold in range(5):
                ii=pred['fold']==fold;v=metrics(y[ii],pred[name+'_seed_p'][s,ii],pred[name+'_seed_hard'][s,ii]);seedfold.append(dict(model=name,seed=seed,fold=fold,**dict(zip(METRICS,map(float,v)))))
    for name in ['A-CONSTANT','A-ADAPTIVE']:
        for diagnostic in ['neutral_quality','permuted_action']:
            p=np.full(len(y),np.nan);hard=np.zeros(len(y),int)
            for fold in range(5):
                info=read(task/f'outer{fold}.json');te=np.flatnonzero(pred['fold']==fold);ps=[]
                for seed in c['seeds']:
                    with np.load(task/'fits'/f'outer{fold}_{name}_refit_seed{seed}.npz') as z:ps.append(z[diagnostic])
                p[te]=np.mean(ps,axis=0);hard[te]=p[te]>=info['models'][name]['threshold']
            ablations[name+' '+diagnostic]=dict(zip(METRICS,map(float,metrics(y,p,hard))))
            np.savez_compressed(task/(name+'_'+diagnostic+'.npz'),p=p,hard=hard,y=y,fold=pred['fold'])
    for fold in range(5):
        info=read(task/f'outer{fold}.json');te=np.flatnonzero(pred['fold']==fold)
        for name in ['A-CONSTANT','A-ADAPTIVE']:
            for seed in c['seeds']:
                with np.load(task/'fits'/f'outer{fold}_{name}_refit_seed{seed}.npz') as z:
                    effective=z['effective'];delta=z['delta']
                for local,row in enumerate(te):
                    coefficient_records.append(dict(model=name,seed=seed,fold=fold,row=int(row),recording_id=frame.iloc[row].recording_id,action=frame.iloc[row].action,failure=int(y[row]),a_visual=float(effective[local,0]),a_sensor=float(effective[local,1]),delta_visual=float(delta[local,0]),delta_sensor=float(delta[local,1])))
    pd.DataFrame(seedfold).to_csv(task/'per_seed_fold_metrics.csv',index=False)
    coef=pd.DataFrame(coefficient_records);coef.to_csv(task/'effective_coefficients.csv',index=False)
    summaries=coef.groupby(['model','action'])[['a_visual','a_sensor','delta_visual','delta_sensor']].agg(['mean','std','min','max'])
    summaries.to_csv(task/'effective_coefficient_summary.csv');write(task/'ablations.json',ablations)
    fig,axes=plt.subplots(2,2,figsize=(10,7))
    for col,name in enumerate(['A-CONSTANT','A-ADAPTIVE']):
        for fold in range(5):
            info=read(task/f'outer{fold}.json')['models'][name];penalty=info['selected_penalty']
            for seed in c['seeds']:
                for inner in range(4):
                    stem=f'outer{fold}_{name}_lambda{penalty}_inner{inner}_seed{seed}'.replace('.','p')
                    history=read(task/'fits'/(stem+'.json'))['history'];epochs=[r['epoch'] for r in history]
                    axes[0,col].plot(epochs,[r['train_loss'] for r in history],alpha=.2,lw=.6)
                    axes[1,col].plot(epochs,[r['validation_AP'] for r in history],alpha=.2,lw=.6)
        axes[0,col].set_title(name);axes[0,col].set_ylabel('Training objective');axes[1,col].set_ylabel('Inner validation AP');axes[1,col].set_xlabel('Epoch')
    fig.tight_layout();fig.savefig(task/'learning_curves.png',dpi=160);fig.savefig(task/'learning_curves.pdf');plt.close(fig)
    rows=[]
    for name,record in result['models'].items():rows.append([name]+[f'{record["metrics"][m]["estimate"]:.4f}' for m in METRICS])
    contrast=[]
    for name,record in result['contrasts'].items():
        ap=record['metrics']['AUPRC'];au=record['metrics']['AUROC'];contrast.append([name,f'{ap["estimate"]:+.4f} [{ap["lower_95"]:+.4f}, {ap["upper_95"]:+.4f}]',f'{au["estimate"]:+.4f} [{au["lower_95"]:+.4f}, {au["upper_95"]:+.4f}]',record['AP_interpretation']])
    text='# Task 3 — static-anchored adaptation\n\nADDITIONAL EXPLORATORY EXPERIMENTS. [VERIFIED EXECUTION]\n\n'
    text+='Question: can input-dependent coefficient changes improve the established probability-input logistic stacker while keeping its branch evidence and output link fixed? Original F6 changed this link and did not establish adaptive value, motivating this isolated test.\n\n'
    text+='Method: original Section1B/2 strictly nested visual/statistics probabilities; each proper training partition independently fits C1 F2. Freeze b,a; output sigmoid(b + sum(a*(1+tanh(h(u)))*p)). A-CONSTANT has two global parameters; A-ADAPTIVE uses action4+training-scaled quality36+availability2, MLP42→16→2, zero final initialization. Lambdas .01/.1/1; AdamW .003, decay .001, max100/min10/patience12, batch128, clip1. Select mean-inner-fold AP of three-seed probabilities. Outer epochs are per-seed rounded median inner best epochs. Threshold uses training-only inner OOF balanced accuracy. No extra output calibration is added to the prespecified logistic link. Branch calibrators remain frozen in their proper partitions.\n\n'
    text+=table(['Model']+METRICS,rows)+'\n'+table(['Contrast','ΔAP, marginal 95%','ΔAUROC, marginal 95%','AP interpretation'],contrast)
    text+='\nAP is average precision. Paired uncertainty resamples 148 recordings, 2000 times; conditional on fitted models, without retraining or study-selection uncertainty. Individual seeds are not independent recordings.\n\n'
    folds=[]
    for k in range(5):
        info=read(task/f'outer{k}.json');record=result['contrasts']['A-ADAPTIVE minus A0']['fold_differences'][str(k)]
        folds.append([k,info['models']['A-CONSTANT']['selected_penalty'],info['models']['A-ADAPTIVE']['selected_penalty'],f'{record["AUPRC"]:+.4f}',f'{record["AUROC"]:+.4f}'])
    text+=table(['Outer fold','Constant λ','Adaptive λ','ΔAP adaptive−A0','ΔAUROC adaptive−A0'],folds)
    text+='\n[OBSERVED RESULT] Clean adaptive AP improves over both matched F2 and the constant-adjustment control with positive marginal paired intervals. The AP point gain exceeds the prespecified .01 practical reference; this is not an established industrial utility requirement. Other metrics, fold changes and calibration must be read together; there is no universal metric improvement claim.\n\n'
    text+='Fixed-weight diagnostics and effective coefficients: `ablations.json`, `effective_coefficient_summary.csv`, and `effective_coefficients.csv`. These are associational coefficients, not causal explanations or normalized probability weights. Action-associated failure priors remain an alternative explanation. Single-modality fallback and total-loss abstention identities passed synthetic tests; no recovery benefit is inferred.\n\n'
    text+='[CORRECTED] First attempt stopped at signature mismatch caused by decimal-penalty filename suffix handling. `correction_001.md` and original log/unused first-fit files are retained. The corrected complete run uses unique filenames. Anchor probabilities match sealed outer stacking to <1e-8; floating-point sigmoid ties can shift pooled AUROC by a few millionths, so the exact matched A0 values above are reported.\n\n'
    text+='Artifacts: `predictions.npz`, five `outer*.json` selection/refit records, `fits/*.pt` checkpoints and `fits/*.json` every-epoch histories, `learning_curves.{png,pdf}`, `comparison/results.json`, `per_seed_fold_metrics.csv`, `input_identities.json`. Checkpoints and prediction hashes are embedded in each completed fit record; protocol commit 26ae3a7. Final implementation commit and output hashes are recorded by the extension manifest.\n\n'
    text+='Limitations: same outcome-informed cohort; exploratory marginal intervals; three seeds do not exhaust training variability; no independent validation. This task does not establish robustness or authorize combining new branches with this gate. Task4 tests exposure-matched robustness separately. Original historical conclusions remain unchanged.\n'
    (root/'reports/03_STATIC_ANCHORED_ADAPTATION_RESULTS.md').write_text(text)
    write(task/'report_artifacts.json',dict(report=identity(root/'reports/03_STATIC_ANCHORED_ADAPTATION_RESULTS.md'),curves=[identity(task/f'learning_curves.{ext}') for ext in ['png','pdf']],ablations=identity(task/'ablations.json')))
    progress(3,'All bounded clean fits, paired results, diagnostics, curves and report complete','complete')

if __name__=='__main__':main()
