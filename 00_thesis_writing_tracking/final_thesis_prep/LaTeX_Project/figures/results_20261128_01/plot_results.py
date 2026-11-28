"""Render four within-study summaries from retained results, without model execution.

Run from the thesis root with the existing XeLaTeX toolchain on PATH and the
repository Python environment. Outputs are immutable: choose a fresh --outdir.
The JSON receipt preserves the source strings and SHA-256 identities.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
import matplotlib
matplotlib.use('pgf')
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = Path(__file__).resolve().parent
FIGURES = HERE.parent
REPO = next(p for p in HERE.parents if (p / 'REPO_MAP.md').exists())
SOURCES = {
    'phm': 'implementations/PHM2026/results/runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/tables/loeo_summary.csv',
    'reassemble': 'implementations/REASSEMBLE/results/artifacts/reports/SECTION_2_FUSION_HANDOFF.md',
    'msm': 'implementations/MSM/results/06_evaluation_results/metrics/clean_seed_summary.csv',
    'vifailback': 'implementations/VIFAILBACK/10_final_research_reports/06_UNIMODAL_BASELINE_RESULTS.md',
}
PALETTE = {'vision': '#0072B2', 'sensor': '#009E73', 'fusion': '#CC79A7', 'baseline': '#595959'}
MARKERS = {'vision': 'o', 'sensor': 's', 'fusion': 'D', 'baseline': 'x'}

def read_csv(key):
    with (REPO / SOURCES[key]).open() as stream:
        return list(csv.DictReader(stream))

def load_data():
    phm = {r['model']: r for r in read_csv('phm')}
    p = []
    for key, label, role in [('constant_train_mean', 'Training-mean constant', 'baseline'),
                             ('patchtst_single_encoder', 'Single encoder', 'sensor'),
                             ('fused_all_three', 'Three-group fusion', 'fusion')]:
        r = phm[key]
        assert r['n_runs'] == '20'
        p.append(dict(label=label, role=role, mean=r['mae'], low=r['mae_ci95_low'], high=r['mae_ci95_high']))
    text = (REPO / SOURCES['reassemble']).read_text().split('## H. Clean results')[1].split('## I.')[0]
    names = [('U2', 'Frozen vision', 'vision'), ('U1', 'Statistical sensors', 'sensor'),
             ('F1', 'F1: probability mean', 'fusion'), ('F2', 'F2: logistic stacker', 'fusion'),
             ('F3', 'F3: representation fusion', 'fusion'), ('F4', 'F4: action gate', 'fusion'),
             ('F5', 'F5: quality gate', 'fusion'), ('F6', 'F6: combined gate', 'fusion')]
    rdata = []
    for key, label, role in names:
        line = next(l for l in text.splitlines() if l.startswith('| '+key+' '))
        cell = line.split('|')[3].strip()
        mean, low, high = re.fullmatch(r'(\d+\.\d+) \[(\d+\.\d+), (\d+\.\d+)\]', cell).groups()
        rdata.append(dict(label=label, role=role, mean=mean, low=low, high=high))
    msm = {r['model']: r for r in read_csv('msm') if r['protocol']=='primary__group_id' and r['initialization']=='P'}
    mdata = []
    for key, label, role in [('visual','Frozen vision','vision'),('sensor_logistic','Sensor logistic regression','sensor'),
        ('sensor_histgradient','Sensor HGB','sensor'),('averaging','Equal averaging','fusion'),('F2','F2','fusion'),
        ('F2_aug','F2-aug','fusion'),('QG_clean','QG-clean','fusion'),('QG_aug','QG-aug','fusion')]:
        r=msm[key]
        mdata.append(dict(label=label,role=role,mean=r['AP_mean'],sd=r['AP_seed_std']))
    vdata=[]
    text=(REPO / SOURCES['vifailback']).read_text()
    for key,label,role in [('V1','Frozen vision V1','vision'),('S3','Sensor logistic regression','sensor'),
                           ('S2','Sensor HGB','sensor'),('F1_V1','Equal averaging','fusion'),('F2_V1','Original F2','fusion')]:
        line=next(l for l in text.splitlines() if l.startswith('| '+key+' | 42 | pooled |'))
        cells=[x.strip() for x in line.split('|')[1:-1]]
        assert cells[3]=='4382'
        vdata.append(dict(label=label,role=role,failure=cells[4],success=cells[5],macro=cells[6]))
    return {'phm':p,'reassemble':rdata,'msm':mdata,'vifailback':vdata}

def setup():
    plt.style.use(FIGURES/'thesis.mplstyle')
    for face in ('regular','bold'):
        font_manager.fontManager.addfont(subprocess.check_output(['kpsewhich',f'lmroman12-{face}.otf'],text=True).strip())
    plt.rcParams.update({'pgf.texsystem':'xelatex','pgf.rcfonts':False,
        'pgf.preamble':r'\usepackage{fontspec}\usepackage{amsmath,amssymb}\usepackage{fix-cm}\pagestyle{empty}'})
    for key in ('font.size','axes.titlesize','axes.labelsize','xtick.labelsize','ytick.labelsize','legend.fontsize','legend.title_fontsize'):
        plt.rcParams[key]*=72.27/72

def axes(rows,height):
    fig,ax=plt.subplots(figsize=(452.9679/72.27,height))
    ax.set_yticks(range(len(rows)),[r['label'] for r in rows])
    ax.set_ylim(len(rows)-0.5,-0.5)
    ax.spines[['top','right']].set_visible(False)
    ax.grid(axis='x')
    return fig,ax

def save(fig,key,out):
    path=out/(key+'_results.pdf');fig.savefig(path);plt.close(fig)
    info=subprocess.check_output(['pdfinfo',str(path)],text=True)
    assert re.search(r'Pages:\s+1\b',info)
    width=float(re.search(r'Page size:\s+([0-9.]+)',info)[1])
    assert abs(width-452.9679*72/72.27)<0.01

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir',type=Path,required=True)
    args=parser.parse_args();args.outdir.mkdir(parents=True,exist_ok=True)
    for key in SOURCES:
        if (args.outdir/(key+'_results.pdf')).exists():raise FileExistsError('Choose a fresh output directory')
    data=load_data();setup()
    for key in ('phm','reassemble','msm'):
        rows=data[key];fig,ax=axes(rows,2.1 if key=='phm' else 3.2)
        for i,r in enumerate(rows):
            mean=float(r['mean'])
            errors=[[float(r['sd'])],[float(r['sd'])]] if key=='msm' else [[mean-float(r['low'])],[float(r['high'])-mean]]
            ax.errorbar(mean,i,xerr=errors,fmt=MARKERS[r['role']],color=PALETTE[r['role']],capsize=3,linestyle='none')
        ax.set_xlabel('MAE (percentage points; lower is better)' if key=='phm' else 'Failure-positive average precision (higher is better)' if key=='reassemble' else 'Average precision (higher is better)')
        ax.set_xlim((0,1.3) if key=='phm' else (0,0.55) if key=='reassemble' else (0,1))
        save(fig,key,args.outdir)
    rows=data['vifailback'];fig,ax=axes(rows,2.9)
    # Outcome classes use distinct markers and colours; rows name the models.
    for field,label,marker,colour,offset in [('failure','Failure AP','o','#595959',-0.18),
         ('success','Success AP','s','#0072B2',0),('macro','Both-class macro AP','D','#CC79A7',0.18)]:
        ax.plot([float(r[field]) for r in rows],[i+offset for i in range(len(rows))],
            marker=marker,color=colour,linestyle='none',label=label)
    ax.set_xlim(0,1);ax.set_xlabel('Average precision (higher is better)')
    ax.legend(loc='upper center',bbox_to_anchor=(0.5,1.18),ncol=3,handletextpad=0.2,columnspacing=0.8)
    save(fig,'vifailback',args.outdir)
    receipt={'scope':'Existing saved results; no training, inference or new uncertainty estimation.',
             'sources':{k:{'path':p,'sha256':hashlib.sha256((REPO/p).read_bytes()).hexdigest()} for k,p in SOURCES.items()},
             'data':data,'uncertainty':{'phm':'Retained run-cluster 95% intervals; fixed fitted models.',
             'reassemble':'Retained recording-cluster 95% intervals; fixed fitted models; individual-score intervals.',
             'msm':'Plus/minus sample SD across three fixed seeds, not a confidence interval.',
             'vifailback':'Seed42 pooled class-specific and macro AP; no uncertainty bars.'}}
    (args.outdir/'plot_data_and_sources.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('Exported four vector figures and a source/data receipt to',args.outdir)

if __name__=='__main__':main()
