"""Plot saved metrics only; no model loading, inference or scientific settings."""
from pathlib import Path
import os
ROOT=Path(__file__).resolve().parent.parent
os.environ['MPLCONFIGDIR']=str(ROOT/'cache/matplotlib')
for name in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[name]='2'
os.sched_setaffinity(0,[12,13])
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def main():
    comparison=ROOT/'comparison'
    summary=pd.read_csv(comparison/'model_comparison.csv').set_index('model')
    models=['historical_static','static_augmented','quality_additive','quality_interaction','visual','sensor']
    names=['Historical F2','Augmented static (A)','Additive quality (B)','Quality interactions (C)','Visual only','Sensor only']
    fig,ax=plt.subplots(figsize=(9,5),layout='constrained')
    x=np.arange(len(models));width=.36
    ax.bar(x-width/2,summary.loc[models,'clean_mean_fold_AP'],width,label='Clean',color='#557c9b')
    ax.bar(x+width/2,summary.loc[models,'primary_mean_fold_AP'],width,label='Primary Gaussian mixture',color='#bd733f')
    ax.set_xticks(x,names,rotation=22,ha='right');ax.set_ylabel('Average precision');ax.set_ylim(0,1)
    ax.set_title('Fixed one-fold pilot: clean and predefined-noise AP')
    ax.legend(frameon=False);ax.spines[['top','right']].set_visible(False)
    ax.text(0,-.32,'Point estimates. Noise AP averages repeats, severities and families equally.\nPaired recording-bootstrap contrasts are reported separately; this cohort is development-exposed.',transform=ax.transAxes,fontsize=9)
    fig.savefig(comparison/'fusion_ap_overview.png',dpi=180,bbox_inches='tight');plt.close(fig)
    table=pd.read_csv(comparison/'per_condition_metrics.csv')
    table=table[table.scope.eq('fold')&table.status.eq('COMPLETE')]
    colors=['#666666','#b96521','#357e64','#5f52a3']
    fig,axes=plt.subplots(2,2,figsize=(10,7),layout='constrained',sharey=True)
    families=['image_noise','sensor_noise','image_blur','sensor_time_loss']
    titles=['Image Gaussian noise (primary)','Sensor Gaussian noise (primary)','Image blur (held-out fitting family)','Sensor time loss (held-out fitting family)']
    for ax,family,title in zip(axes.flat,families,titles):
        for model,name,color in zip(models[:4],names[:4],colors):
            rows=table[table.family.eq(family)&table.model.eq(model)]
            # Repeats then folds, with fixed severity order.
            values=rows.groupby(['fold','level']).AP.mean().groupby('level').mean().reindex(['mild','medium','strong'])
            ax.plot(range(3),values,'o-',label=name,color=color)
        ax.set_xticks(range(3),['Mild','Medium','Strong']);ax.set_ylim(0,1);ax.set_title(title,fontsize=11)
        ax.set_ylabel('Average precision');ax.spines[['top','right']].set_visible(False)
    handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside lower center',ncols=2,frameon=False)
    fig.suptitle('Fixed one-fold pilot: per-family severity response\nMeans over fixed realizations; absence is reported separately',fontsize=12)
    fig.savefig(comparison/'fault_family_ap.png',dpi=180,bbox_inches='tight');plt.close(fig)
    print('Created comparison/fusion_ap_overview.png and comparison/fault_family_ap.png from saved metrics.')
if __name__=='__main__':main()
