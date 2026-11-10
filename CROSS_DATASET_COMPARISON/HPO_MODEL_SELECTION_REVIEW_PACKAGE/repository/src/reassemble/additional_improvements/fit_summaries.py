"""Curate fit histories without modifying checkpoints or training code."""
from pathlib import Path
import re
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .common import read


def summarize(task, mode, output_dir=None):
    task=Path(task);curves=[];fits=[]
    destination=task if output_dir is None else Path(output_dir)
    labels=['clean_F6','augmented_F6','clean_A-ADAPTIVE','augmented_A-ADAPTIVE'] if mode=='robust' else ['V-FT']
    fig,axes=plt.subplots(2,len(labels),figsize=(5*len(labels),7),squeeze=False)
    for path in sorted((task/'fits').rglob('*.json')):
        if mode=='robust':
            matches=[label for label in labels if '_'+label+'_' in path.name]
            if not matches:continue
            label=matches[0]
        else:
            if 'V-FT' not in path.parts or path.name.endswith('_live.json') or '_oom_' in path.name:continue
            label='V-FT'
        info=read(path)
        if 'history' not in info:continue
        fold_match=re.search(r'outer(\d+)',str(path));fold=int(fold_match.group(1)) if fold_match else None
        row=dict(model=label,fold=fold,seed=info['seed'],fit=str(path),best_epoch=info['best_epoch'],stopped_epoch=info['stopped_epoch'],seconds=info['seconds'],refit='refit' in path.name)
        if 'penalty' in info:row['penalty']=info['penalty']
        fits.append(row)
        for epoch in info['history']:curves.append({**row,**epoch})
        if row['refit']:continue
        if mode=='robust':
            selected=read(task/f'outer{fold}_{label}.json')['selected_penalty']
            if info['penalty']!=selected:continue
        col=labels.index(label);history=info['history'];x=[h['epoch'] for h in history]
        axes[0,col].plot(x,[h['train_loss'] for h in history],alpha=.2,lw=.6)
        key='validation_objective' if mode=='robust' else 'validation_AP'
        axes[1,col].plot(x,[h[key] for h in history],alpha=.2,lw=.6)
    for col,label in enumerate(labels):
        axes[0,col].set_title(label);axes[0,col].set_ylabel('Training objective')
        axes[1,col].set_ylabel('Inner selection objective' if mode=='robust' else 'Inner AP');axes[1,col].set_xlabel('Epoch')
    prefix='matched' if mode=='robust' else 'finetune'
    pd.DataFrame(curves).to_csv(destination/(prefix+'_learning_curves.csv'),index=False)
    pd.DataFrame(fits).to_csv(destination/(prefix+'_fit_compute.csv'),index=False)
    fig.tight_layout()
    for suffix in ['png','pdf']:fig.savefig(destination/(prefix+'_learning_curves.'+suffix),dpi=160)
    plt.close(fig)
    return dict(fits=len(fits),seconds=sum(r['seconds'] for r in fits))
