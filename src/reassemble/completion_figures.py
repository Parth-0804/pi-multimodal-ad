"""Standalone thesis figures generated from machine-readable study evidence."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from .completion_common import write


LABELS={'U1':'Sensor statistics','U2':'RT-DETR','F1':'Uniform late','F2':'Learned static','F3':'Concatenation','F4':'Process gate','F5':'Quality gate','F6':'Process + quality','D6':'Modality dropout'}
COLORS={'U1':'#333333','U2':'#888888','F1':'#66a61e','F2':'#1b9e77','F3':'#e6ab02','F4':'#7570b3','F5':'#d95f02','F6':'#e7298a','D6':'#1f78b4'}


def figures(root,frame,s1,s1b,s2,robust,dropout,audio,efficiency,source_paths):
    folder=Path(root)/'figures';folder.mkdir(exist_ok=True);index=[]
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.bbox':'tight'})
    def save(fig,name,caption,sources,chapter='Results'):
        files=[]
        for ext in ['pdf','png']:
            path=folder/(name+'.'+ext)
            if not path.exists():fig.savefig(path,dpi=220)
            files.append(str(path))
        plt.close(fig);index.append({'name':name,'outputs':files,'caption':caption,'sources':sources,'script':'scripts/reassemble/20_completion_synthesis.py','chapter':chapter})
    def diagram(name,boxes,caption):
        fig,ax=plt.subplots(figsize=(11,4));ax.set_xlim(0,11);ax.set_ylim(0,4);ax.axis('off')
        for i,(title,body) in enumerate(boxes):
            x=.2+i*3.7;rect=FancyBboxPatch((x,.7),3.1,2.7,boxstyle='round,pad=.15',fc=['#e7eef7','#e8f3ec','#f7eee6'][i],ec='#555');ax.add_patch(rect)
            ax.text(x+1.55,3.0,title,ha='center',weight='bold');ax.text(x+1.55,1.9,body,ha='center',va='center',linespacing=1.6)
            if i<2:ax.annotate('',xy=(x+3.55,2),xytext=(x+3.25,2),arrowprops={'arrowstyle':'->','lw':2})
        save(fig,name,caption,source_paths+['runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/reports/loeo_summary.json',str(Path(root)/'tables/10_dataset_summary.csv')],'Research design / Discussion')
    diagram('01_two_study_design',[('PHM — Study 1','Continuous damage estimation\nProvisional image-derived target\n20 run-level units\nMAE / RMSE / Spearman'),('REASSEMBLE — Study 2','Execution-failure classification\n4,530 segments / 148 recordings\nAUROC / AUPRC / calibration\nDemonstrated complementarity'),('Shared methodology','Validate targets and signal\nGroup-disjoint evaluation\nStart with simple fusion\nTest degraded modalities')],'Two task-specific studies investigate conditions for meaningful fusion; metric scales are not directly comparable.')
    counts=frame.groupby(['action','failure']).size().unstack(fill_value=0).reindex(['pick','insert','remove','place'])
    fig,ax=plt.subplots(figsize=(7,4));ax.bar(counts.index,counts[0],label='Success',color='#72a5be');ax.bar(counts.index,counts[1],bottom=counts[0],label='Failure',color='#d95f02');ax.set_ylabel('Segments');ax.legend();ax.set_title('Primary cohort: 4,530 segments, 509 failures, 148 recordings')
    save(fig,'02_cohort', 'Action and outcome support in the frozen primary cohort; segments are clustered within recordings.',[str(Path(root)/'tables/10_dataset_summary.csv')],'Dataset')
    def metric_plot(name,data,caption,sources):
        fig,axes=plt.subplots(1,2,figsize=(11,4));names=list(data)
        for ax,metric in zip(axes,['AUROC','AUPRC']):
            for i,m in enumerate(names):
                v=data[m][metric];ax.errorbar(v['estimate'],i,xerr=[[max(0,v['estimate']-v['lower_95'])],[max(0,v['upper_95']-v['estimate'])]],fmt='o',color=COLORS.get(m,'#555'),capsize=3)
            ax.set_yticks(range(len(names)),[LABELS.get(m,m) for m in names]);ax.invert_yaxis();ax.set_xlabel(metric);ax.grid(axis='x',alpha=.2)
        fig.tight_layout();save(fig,name,caption,sources)
    metric_plot('03_unimodal', {m:s1['metrics'][m] for m in ['action_only','sensor_statistics','rtdetr','patchtst']},'Unimodal discrimination with recording-clustered 95% intervals. Statistical sensors outperform the tested PatchTST; this is not a universal Transformer claim.',source_paths[:1])
    fig,axes=plt.subplots(1,2,figsize=(9,4))
    for ax,key in zip(axes,['all','failures']):
        x=s1b['complementarity'][key];matrix=np.array([[x['both_correct'],x['visual_only_correct']],[x['sensor_only_correct'],x['both_wrong']]])
        ax.imshow(matrix,cmap='Blues');ax.set_xticks([0,1],['Sensor correct','Sensor wrong']);ax.set_yticks([0,1],['Visual correct','Visual wrong']);ax.set_title(key)
        for i in range(2):
            for j in range(2):ax.text(j,i,str(matrix[i,j]),ha='center',va='center',color='white' if matrix[i,j]>matrix.max()/2 else 'black',fontsize=15)
    fig.tight_layout();save(fig,'04_complementarity','Frozen OOF correctness overlap. Visual-only correct failures number 97 across 61 recordings. The oracle is diagnostic, not deployable.',source_paths[1:2])
    metric_plot('05_clean_fusion',s2['metrics'],'Clean fusion comparison. No adaptive gate establishes incremental value over F2; intervals condition on fitted models.',source_paths[2:3])
    weights=__import__('json').loads((Path(source_paths[2]).parent/'gate_weights.json').read_text())
    fig,ax=plt.subplots(figsize=(8,4));actions=['pick','insert','remove','place'];x=np.arange(4)
    for i,m in enumerate(['F4','F5','F6']):ax.bar(x+(i-1)*.25,[weights[m]['by_action'][a]['visual_mean'] for a in actions],width=.25,label=LABELS[m],color=COLORS[m])
    ax.set_xticks(x,actions);ax.set_ylabel('Mean visual weight');ax.set_ylim(0,1);ax.legend();save(fig,'06_weights_by_action','Clean modality allocation varies by action; allocation differences do not establish causal process value.',[str(Path(source_paths[2]).parent/'gate_weights.json')])
    conditions=robust['conditions']
    for prefix,families in [('07_visual_corruptions',['V1','V2','V3']),('08_sensor_corruptions',['S1','S2','S3'])]:
        fig,axes=plt.subplots(1,3,figsize=(12,3.5))
        for ax,family in zip(axes,families):
            keys=['clean']+sorted([k for k,v in conditions.items() if v['condition']['family']==family],key=lambda k:conditions[k]['condition']['severity']);x=[conditions[k]['condition']['severity'] for k in keys]
            for m in ['U1','F1','F2','F5','F6']:
                values=[conditions[k]['metrics'][m]['AUPRC'] for k in keys]
                ax.plot(x,[v['estimate'] for v in values],'-o',label=LABELS[m],color=COLORS[m],ms=3)
                ax.fill_between(x,[v['lower_95'] for v in values],[v['upper_95'] for v in values],color=COLORS[m],alpha=.08)
            ax.set_title(family);ax.set_xlabel('Predeclared severity');ax.set_ylabel('AUPRC');ax.grid(alpha=.2)
        axes[-1].legend(fontsize=7);fig.tight_layout();save(fig,prefix,'Clean-trained model AUPRC under single-modality degradation. Shading shows marginal recording-cluster 95% intervals; one deterministic corruption realization per condition.',source_paths[3:4])
    fig,ax=plt.subplots(figsize=(10,4));x=np.arange(3)
    for i,m in enumerate(['U1','U2','F1','F2','F5','F6']):
        values=[conditions[k]['metrics'].get(m) for k in ['clean','V4','S5']];heights=[v['AUPRC']['estimate'] if v else np.nan for v in values]
        ax.bar(x+(i-2.5)*.12,heights,.12,label=LABELS[m],color=COLORS[m])
    ax.set_xticks(x,['Clean','Visual missing','Sensor missing']);ax.set_ylabel('AUPRC');ax.legend(fontsize=8,ncol=2);save(fig,'09_missing_modalities','All fusion models fall back to the remaining branch. Unavailable unimodal models abstain and have no metric bar.',source_paths[3:4])
    fig,axes=plt.subplots(2,3,figsize=(11,6))
    for ax,family in zip(axes.flat,['V1','V2','V3','S1','S2','S3']):
        levels=[0]+[conditions[k]['condition']['severity'] for k in sorted([n for n,v in conditions.items() if v['condition']['family']==family],key=lambda k:conditions[k]['condition']['severity'])]
        for m in ['F5','F6']:ax.plot(levels,robust['mechanism'][family][m]['level_mean_weights'],'-o',label=LABELS[m],color=COLORS[m])
        ax.set_title(family);ax.set_ylim(0,1);ax.set_xlabel('Severity');ax.set_ylabel('Degraded-modality weight')
    axes.flat[-1].legend(fontsize=8);fig.tight_layout();save(fig,'10_gate_response','Measured gate response, without forced monotonicity. Lower degraded-modality weight alone is insufficient to establish predictive robustness.',source_paths[3:4])
    fig,ax=plt.subplots(figsize=(8,5))
    for i,(name,result) in enumerate(dropout['conditions'].items()):
        v=result['minus_clean_trained_F6']['AUPRC'];ax.errorbar(v['estimate'],i,xerr=[[max(0,v['estimate']-v['lower_95'])],[max(0,v['upper_95']-v['estimate'])]],fmt='o',capsize=3,color=COLORS['D6'])
    ax.axvline(0,color='#555',lw=1);ax.set_yticks(range(len(dropout['conditions'])),list(dropout['conditions']));ax.invert_yaxis();ax.set_xlabel('AUPRC difference: modality dropout − ordinary F6');save(fig,'11_dropout_tradeoff','Clean and degraded performance trade-off from one preregistered modality-dropout variant. Exact zero under complete modality loss follows from the architecture.',source_paths[4:5])
    fig,ax=plt.subplots(figsize=(8,4))
    for m,e in efficiency['models'].items():
        ap=dropout['conditions']['clean']['metrics']['AUPRC']['estimate'] if m=='D6' else s2['metrics'][m]['AUPRC']['estimate']
        ax.scatter(e['sequential_component_sum_seconds']*1000,ap,color=COLORS[m]);ax.annotate(LABELS[m],(e['sequential_component_sum_seconds']*1000,ap),xytext=(4,4),textcoords='offset points',fontsize=8)
    ax.set_xscale('log');ax.set_xlabel('Estimated sequential component-sum latency (ms, warm VM)');ax.set_ylabel('Clean AUPRC');save(fig,'12_efficiency','Task-specific accuracy/cost trade-off. Latency is a sum of measured warm components on this VM, not production end-to-end timing.',[source_paths[2],source_paths[4],source_paths[5]],'Practical usability')
    fig,ax=plt.subplots(figsize=(8,4));names=list(audio['streams']);x=np.arange(len(names))
    ax.bar(x-.15,[audio['streams'][n]['nominal_valid_percent'] for n in names],.3,label='Nominal coverage');ax.bar(x+.15,[100*audio['streams'][n]['verified_segments']/4530 for n in names],.3,label='Verified segment timing');ax.set_xticks(x,names);ax.set_ylabel('Primary segments (%)');ax.legend();save(fig,'13_audio_gate','Nominal overlap is distinct from trustworthy segment alignment. Audio modelling was excluded by the timing gate, not by a negative predictive result.',source_paths[6:7],'Dataset limitations')
    diagram('14_cross_study_conditions',[('Prerequisites','Valid target / task definition\nDeployable modality signal\nIndependent evaluation units'),('Fusion evidence','Establish complementarity\nCompare simple references\nSeparate gain from complexity'),('Robustness evidence','Induce modality degradation\nMeasure weight response\nRequire predictive benefit')],'Cross-study synthesis: establish modality informativeness and complementarity before architectural complexity; flat low-signal degradation is not robustness.')
    write(Path(root)/'figure_index.json',index)
    return index
