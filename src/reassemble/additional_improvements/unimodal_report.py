"""Report all bounded neural comparisons, including convergence and order controls."""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reassemble.section1_features import cohort
from reassemble.section1_report import metrics,METRICS,table
from .common import config,read,write,progress,identity
from .fit_summaries import summarize

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--task',type=int,choices=[1,2],required=True);args=parser.parse_args();c=config();root=Path(c['run_dir']);name='01_temporal_visual' if args.task==1 else '02_patchtst_training_budget';task=root/name
    frame=cohort(read(c['section1_config']));y=frame.failure.to_numpy(int);result=read(task/'comparison/results.json')
    variants=['V-MEAN','V-TEMP','V-NOPOS'] if args.task==1 else ['S-6','S-LONG'];epochrows=[];seedrows=[];historyrows=[];orderrows=[];compute=[]
    fig,axes=plt.subplots(2,len(variants),figsize=(5*len(variants),7),squeeze=False)
    for col,variant in enumerate(variants):
        with np.load(task/(variant+'_predictions.npz')) as z:pred={key:z[key] for key in z.files}
        for seed_index,seed in enumerate(c['seeds']):
            for fold in range(5):
                ix=pred['fold']==fold;v=metrics(y[ix],pred['seed_p'][seed_index,ix],pred['seed_hard'][seed_index,ix]);seedrows.append(dict(model=variant,seed=seed,fold=fold,**dict(zip(METRICS,map(float,v)))))
        if args.task==1:
            for change in ['reverse','permute']:
                hard=np.zeros(len(y),int)
                for fold in range(5):
                    threshold=read(task/'fits'/variant/f'outer{fold}'/'branch.json')['threshold'];ix=pred['fold']==fold;hard[ix]=pred[change][ix]>=threshold
                orderrows.append(dict(model=variant,diagnostic=change,maximum_probability_change=float(np.max(abs(pred[change]-pred['p']))),**dict(zip(METRICS,map(float,metrics(y,pred[change],hard))))))
        for fold in range(5):
            info=read(task/'fits'/variant/f'outer{fold}'/'branch.json')
            for detail in info['seeds']:
                seed=detail['seed'];epochrows.append(dict(model=variant,outer_fold=fold,seed=seed,refit_epochs=detail['refit_epochs'],inner_best_epochs=str(detail['selected_epochs'])))
                for inner,fit in enumerate(detail['inner_fits']):
                    compute.append(dict(model=variant,fold=fold,seed=seed,inner=inner,parameters=fit['parameters'],seconds=fit['seconds'],best_epoch=fit['best_epoch'],stopped_epoch=fit['stopped_epoch'],reached_100_epoch_cap=fit['stopped_epoch']==100))
                    history=fit['history'];epochs=[r['epoch'] for r in history]
                    axes[0,col].plot(epochs,[r['train_loss'] for r in history],alpha=.22,lw=.6)
                    axes[1,col].plot(epochs,[r['validation_AP'] for r in history],alpha=.22,lw=.6)
                    for row in history:historyrows.append(dict(model=variant,fold=fold,seed=seed,inner=inner,**row))
            axes[0,col].set_title(variant);axes[0,col].set_ylabel('Class-weighted training BCE');axes[1,col].set_ylabel('Inner AP');axes[1,col].set_xlabel('Epoch')
    fig.tight_layout();fig.savefig(task/'learning_curves.png',dpi=160);fig.savefig(task/'learning_curves.pdf');plt.close(fig)
    for filename,rows in [('selected_epochs',epochrows),('per_seed_fold_metrics',seedrows),('learning_curves',historyrows),('fit_compute',compute)]:pd.DataFrame(rows).to_csv(task/(filename+'.csv'),index=False)
    if orderrows:pd.DataFrame(orderrows).to_csv(task/'order_diagnostic_metrics.csv',index=False)
    rows=[]
    for model,r in result['models'].items():rows.append([model]+[f'{r["metrics"][m]["estimate"]:.4f}' for m in METRICS])
    differences=[]
    for key,r in result['contrasts'].items():
        ap=r['metrics']['AUPRC'];au=r['metrics']['AUROC'];differences.append([key,f'{ap["estimate"]:+.4f} [{ap["lower_95"]:+.4f},{ap["upper_95"]:+.4f}]',f'{au["estimate"]:+.4f} [{au["lower_95"]:+.4f},{au["upper_95"]:+.4f}]',r['AP_interpretation']])
    title='Task 1 — temporal visual representations' if args.task==1 else 'Task 2 — PatchTST training budget'
    text=f'# {title}\n\nADDITIONAL EXPLORATORY EXPERIMENTS. [VERIFIED EXECUTION]\n\n'
    if args.task==1:
        text+='Question: does frame order contribute beyond the original temporal mean, separately from increased capacity and training? The completed study retained only segment means. Actual 16-frame sequences were re-extracted at the identical saved frame positions with pinned RT-DETR and unchanged 640×640 preprocessing. Timestamps, valid masks, raw source/model/processor identities and mean-parity checks are saved per recording.\n\n'
        text+='V-MEAN retains the original head. V-TEMP uses projection896→128, fixed sinusoidal positions, one four-head Transformer layer, FFN256/dropout.1, valid-frame mean and binary head. V-NOPOS has identical capacity without positional encoding. Normalization uses training-segment mean-vector moments.\n\n'
    else:
        text+='Question: was the original six-epoch cap limiting, or do engineered statistics remain stronger after bounded convergence-oriented training? Original PatchTST selected six in every original outer fold; S-HIST remains sealed evidence. S-6 repeats original3/6 selection with three seeds. S-LONG changes only maximum training100, min10/patience12. Architecture, channels512×22, patch32/stride16, width32, layers2/heads4/FF64, pooling, missing-observation mask, train-only channel scaling and mean imputation are unchanged. S-STATS remains the established reference; this extension does not rewrite the historical negative result.\n\n'
    text+='Training uses original class-weighted BCE, AdamW lr.001/decay.001, clip1, effective batch128. Seeds20260927–29. Outer refit epochs are rounded median inner best epochs per seed (S-6 retains its explicitly requested mean-inner-AP3/6 selection). Each seed uses training-only sigmoid logistic calibration; final predictions average calibrated seed probabilities. Thresholds retain the original balanced-accuracy grid and tie rule. No outer labels select fitting, calibration or thresholds.\n\n'
    text+=table(['Model']+METRICS,rows)+'\n'+table(['Contrast','ΔAP, marginal95%','ΔAUROC, marginal95%','AP interpretation'],differences)
    text+='\nAP is average precision. Intervals use2000 paired recording-cluster resamples, conditional on fitted models, without full retraining or outcome-informed study-selection uncertainty. Fold metrics and paired fold changes are in `comparison/results.json`; `per_seed_fold_metrics.csv` gives individual seed/fold results. No non-significant comparison establishes equivalence.\n\n'
    cap=sum(row['reached_100_epoch_cap'] for row in compute);text+=f'Convergence: {cap} long-budget inner fits reached epoch100. `selected_epochs.csv`, every-epoch `learning_curves.csv`, and `learning_curves.{{png,pdf}}` show selections/loss/AP; inner AUROC is retained too. Reaching the cap permits an undertraining limitation, not automatic extra epochs. Compute/parameter records are in `fit_compute.csv`; refit timings and checkpoint/prediction hashes are in every `fits/<variant>/outer*/branch.json`.\n\n'
    if args.task==1:
        text+='Fixed-weight reversal/permutation results are in `order_diagnostic_metrics.csv`; non-positional invariance tests precede execution. Score changes alone do not establish useful temporal reasoning. A temporal-order claim additionally requires V-TEMP improvement relative to V-NOPOS; improvement only against V-MEAN may reflect capacity.\n\n'
        if (task/'finetune_comparison/results.json').exists():
            summarize(task,'finetune')
            ft=read(task/'finetune_comparison/results.json');text+='V-FT is separately evaluated after at most20 additional epochs/patience5, final spatial stage only, backbone lr1e-5/head lr1e-4, frozen BatchNorm running statistics. Synthetic memory/gradient audit is `finetune_gradient_audit.json`. It adds supervised adaptation and compute. Frozen-prefix caching was explicitly approved after exact GPU prediction/gradient parity; only unchanged stages are cached, with the adapted final stage recomputed on every update. See PROTOCOL_AMENDMENT_01_FROZEN_PREFIX_CACHE.md, finetune_learning_curves.csv/.png/.pdf and finetune_fit_compute.csv.\n\n'
            for key,r in ft['contrasts'].items():
                v=r['metrics']['AUPRC'];text+=f'- {key}: ΔAP {v["estimate"]:+.4f},95% [{v["lower_95"]:+.4f},{v["upper_95"]:+.4f}]; {r["AP_interpretation"]}.\n'
            complete=True
        else:
            audit=read(task/'finetune_gradient_audit.json') if (task/'finetune_gradient_audit.json').exists() else {};complete=False
            text+='[NOT RUN / INCOMPLETE] No completed five-fold V-FT comparison exists. The audit/status/attempt log records any actual blocker; pending work must not be described as completed or as a negative finding.\n'
    else:
        if (task/'hybrid_comparison/results.json').exists():
            hybrid=read(task/'hybrid_comparison/results.json');r=hybrid['contrasts']['S-HYBRID minus S-STATS'];v=r['metrics']['AUPRC'];text+=f'Secondary S-HYBRID−S-STATS: ΔAP {v["estimate"]:+.4f},95% [{v["lower_95"]:+.4f},{v["upper_95"]:+.4f}]; {r["AP_interpretation"]}.\n\n'
            text+='The C1 logistic hybrid uses calibrated S-LONG and statistics with nested branch predictions; even its inner threshold predictions use deeper training-only branch selection/calibration. These are two representations of one sensor modality. It does not replace the statistics branch in Tasks3/4.\n';complete=True
        else:text+='[NOT RUN / INCOMPLETE] S-HYBRID comparison is pending; no incremental temporal-sensor claim is supported yet.\n';complete=False
    text+='\nInterpretation is bounded by matched controls, seed/fold variation and paired intervals. Report supported improvements, deteriorations and inconclusive effects equally. This outcome-informed same-cohort extension is not independent confirmation. No winning changes are automatically combined. Exact protocol/config, implementation commits and artifact manifests are under the new root only; completed original study files and external Reasoning Record are unchanged.\n'
    target=root/'reports'/('01_TEMPORAL_VISUAL_RESULTS.md' if args.task==1 else '02_PATCHTST_BUDGET_RESULTS.md');target.write_text(text)
    progress(args.task,'All bounded variants, learning curves, predictions, paired comparisons and report complete' if complete else 'Primary variants reported; secondary task remains pending', 'complete' if complete else 'running')

if __name__=='__main__':main()
