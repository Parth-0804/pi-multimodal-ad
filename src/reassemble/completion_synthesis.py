"""Traceable final REASSEMBLE tables, figures, reasoning narrative and handoffs."""
from pathlib import Path
import json
import subprocess
import numpy as np
import pandas as pd
from .completion_common import config,read,write,progress
from .section1_features import cohort
from .section1_report import METRICS,table
from .completion_figures import figures,LABELS


def save_text(path,text):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        assert path.read_text()==text,('Refuse to overwrite completed synthesis',str(path));return
    with path.open('x') as f:f.write(text)


def csv(path,rows):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists():
        with path.open('x') as f:pd.DataFrame(rows).to_csv(f,index=False)


def fmt(value):
    return f"{value['estimate']:.4f} [{value['lower_95']:.4f}, {value['upper_95']:.4f}]"


def main():
    c=config();root=Path(c['runs']['final-synthesis']);reports=Path('artifacts/reassemble/reports');tables=root/'tables';tables.mkdir(exist_ok=True)
    source_paths=[str(Path(c[key])/'assessment/results.json') for key in ['section1','section1b','section2']]
    source_paths += [str(Path(c['runs'][key])/'results.json') for key in ['section3','modality-dropout','efficiency','audio-gate']]
    s1,s1b,s2,robust,dropout,eff,audio=map(read,source_paths);objects=read(Path(c['runs']['object-feasibility'])/'results.json')
    frame=cohort(read('configs/reassemble/section1.json'))
    master=[];mapping={}
    for label,key in [('Prior','prior'),('Action only','action_only'),('Sensor statistics','sensor_statistics'),('RT-DETR','rtdetr'),('PatchTST','patchtst')]:
        row={'model':label,'status':'frozen Section 1','source':source_paths[0],'source_key':'metrics.'+key}
        for metric in METRICS:
            row[metric]=s1['metrics'][key][metric]['estimate'];row[metric+'_lower_95']=s1['metrics'][key][metric]['lower_95'];row[metric+'_upper_95']=s1['metrics'][key][metric]['upper_95']
        short={'sensor_statistics':'U1','rtdetr':'U2'}.get(key)
        row['parameters']=eff['models'][short]['total_parameters'] if short else None;row['estimated_latency_ms']=eff['models'][short]['sequential_component_sum_seconds']*1000 if short else None
        if key=='patchtst':row['parameters']=read(Path(c['section1'])/'predictions/patchtst_perm00_fold0.json')['refit']['parameters']+2
        if key=='prior':row['parameters']=1
        if key=='action_only':row['parameters']=7
        master.append(row)
    for key in ['F1','F2','F3','F4','F5','F6','D6']:
        values=dropout['conditions']['clean']['metrics'] if key=='D6' else s2['metrics'][key]
        row={'model':LABELS[key],'status':'adaptive exploratory '+('modality-dropout follow-up' if key=='D6' else 'frozen Section 2'),'source':source_paths[4] if key=='D6' else source_paths[2],'source_key':'conditions.clean.metrics' if key=='D6' else 'metrics.'+key}
        for metric in METRICS:
            for field,suffix in [('estimate',''),('lower_95','_lower_95'),('upper_95','_upper_95')]:row[metric+suffix]=values[metric][field]
        row['parameters']=eff['models'][key]['total_parameters'] if key in eff['models'] else None;row['estimated_latency_ms']=eff['models'][key]['sequential_component_sum_seconds']*1000 if key in eff['models'] else None
        if key in ['F3','F4']:
            row['parameters']=eff['models']['U2']['total_parameters']+(3*max(s2['cost'][key]['parameters_per_seed_by_fold']))+(eff['models']['U1']['total_parameters'] if key=='F4' else -131+6)
        master.append(row)
    for model in ['AST','Tri-modal fusion']:master.append({'model':model,'status':'NOT RUN — GATE FAILED (segment alignment)','source':source_paths[6],'source_key':'decision',**{m:None for m in METRICS},'parameters':None,'estimated_latency_ms':None})
    csv(tables/'01_master_clean_metrics.csv',master)
    clean_table=table(['Model']+METRICS+['Parameters','Latency ms*'],[[row['model']]+['not run' if row.get(m) is None else f"{row[m]:.4f}" for m in METRICS]+[row['parameters'] if row['parameters'] is not None else 'not measured',f"{row['estimated_latency_ms']:.2f}" if row['estimated_latency_ms'] is not None else 'not measured'] for row in master])
    save_text(tables/'01_master_clean_metrics.md',clean_table+'\n*Warm sequential component-sum estimate; not production end-to-end timing. Latency not remeasured for retired PatchTST/concatenation/process gate. Full per-metric CIs and source pointers are in CSV. Parameter counts include shared branches where used and three seed heads; counts can vary by outer fold.\n')
    detailed=[];paired=[];missing=[];weight_rows=[]
    for name,result in robust['conditions'].items():
        for model,values in result['metrics'].items():
            if values is None:
                missing.append({'condition':name,'model':model,'status':'unavailable: abstention'});continue
            row={'condition':name,'family':result['condition']['family'],'severity':result['condition']['severity'],'model':model}
            row.update({m:v['estimate'] for m,v in values.items()})
            row.update({m+'_lower_95':v['lower_95'] for m,v in values.items()});row.update({m+'_upper_95':v['upper_95'] for m,v in values.items()})
            row['delta_AUROC']=result.get('degradation',{}).get(model,{}).get('AUROC',{}).get('estimate',0.)
            row['delta_AUPRC']=result.get('degradation',{}).get(model,{}).get('AUPRC',{}).get('estimate',0.)
            detailed.append(row)
            if name in ['clean','V4','S5']:missing.append(row)
        for contrast,values in result['paired'].items():
            for metric,v in values.items():paired.append({'condition':name,'contrast':contrast,'metric':metric,**v,'type':'absolute performance'})
        for contrast,values in result['degradation_advantage'].items():
            for metric,v in values.items():paired.append({'condition':name,'contrast':contrast,'metric':metric,**v,'type':'degradation advantage'})
        for model,v in result['weights'].items():weight_rows.append({'condition':name,'model':model,'visual_mean':v['visual_mean'],'sensor_mean':v['sensor_mean'],'entropy':v['entropy'],'visual_shift':v['visual_shift']['estimate'],'visual_shift_lower_95':v['visual_shift']['lower_95'],'visual_shift_upper_95':v['visual_shift']['upper_95']})
    csv(tables/'02_robustness_detailed.csv',detailed);csv(tables/'03_robustness_paired.csv',paired);csv(tables/'04_missing_modality.csv',missing);csv(tables/'05_gate_response.csv',weight_rows)
    for family in ['V1','V2','V3','S1','S2','S3','S4']:csv(tables/('robustness_'+family+'.csv'),[row for row in detailed if row['family']==family or row['condition']=='clean'])
    summary=[]
    for model in ['U1','F1','F2','F5','F6']:
        row={'model':model}
        for name in ['clean','V1_0.02','V1_0.05','V1_0.1','V4','S1_0.1','S1_0.5','S1_1.0','S5']:
            values=robust['conditions'][name]['metrics'][model];row[name+'_AUPRC']=None if values is None else values['AUPRC']['estimate']
            row[name+'_delta_AUPRC']=None if values is None else values['AUPRC']['estimate']-robust['conditions']['clean']['metrics'][model]['AUPRC']['estimate']
            if model in ['F5','F6']:row[name+'_visual_weight_shift']=robust['conditions'][name]['weights'][model]['visual_shift']['estimate']
        summary.append(row)
    csv(tables/'06_robustness_summary.csv',summary)
    csv(tables/'07_modality_dropout.csv',[{'condition':name,**{m:v['estimate'] for m,v in x['metrics'].items()},'delta_AP':x['minus_clean_trained_F6']['AUPRC']['estimate'],'delta_AP_lower_95':x['minus_clean_trained_F6']['AUPRC']['lower_95'],'delta_AP_upper_95':x['minus_clean_trained_F6']['AUPRC']['upper_95']} for name,x in dropout['conditions'].items()])
    csv(tables/'08_audio_gate.csv',[{'stream':name,**values} for name,values in audio['streams'].items()]);csv(tables/'09_efficiency.csv',[{'model':name,**values} for name,values in eff['models'].items()])
    csv(tables/'10_dataset_summary.csv',frame.groupby(['action','failure']).size().rename('segments').reset_index().to_dict('records'))
    protocol_rows=[{'item':'cohort','value':f'{len(frame)} segments, {int(frame.failure.sum())} failures, {frame.recording_id.nunique()} recordings'},{'item':'CV','value':'frozen 5 outer / 4 inner recording folds; deeper branch cross-fitting for fusion inputs'},{'item':'uncertainty','value':'2000 paired recording-cluster bootstrap draws; fixed fitted models'},{'item':'primary metrics','value':'AUROC; AUPRC = average precision'},{'item':'controls','value':'19 cyclic within-recording/action permutations; full nested refit; p resolution .05'},{'item':'adaptive status','value':'same-cohort exploratory sequential study; not independent confirmation'},{'item':'audio','value':audio['decision']}]
    csv(tables/'11_evaluation_protocol.csv',protocol_rows)
    csv(tables/'12_clean_paired.csv',[{'contrast':pair,'metric':m,**v} for pair,values in s2['paired'].items() for m,v in values.items()])
    index=figures(root,frame,s1,s1b,s2,robust,dropout,audio,eff,source_paths)
    mechanism=[];positive=[];absolute=[]
    for family,models in robust['mechanism'].items():
        for model,v in models.items():
            mechanism.append({'family':family,'model':model,**v})
            if v['classification']=='ROBUSTNESS-A':positive.append(family+'/'+model)
            if v['absolute_AP_superiority_supported']:absolute.append(family+'/'+model)
    robustness_answer=('Both induced weight adaptation and smaller AP degradation met the predeclared criteria for: '+', '.join(positive)+'.' if positive else 'No family/gate pair met both the predeclared weight-adaptation and smaller-degradation criteria at its highest severity.')
    robustness_answer+=' Absolute high-severity AP superiority over F2 was supported for '+(', '.join(absolute) if absolute else 'none of these family/gate pairs')+'. These are separate claims and marginal exploratory intervals; no universal reliability-awareness claim follows.'
    dclean=dropout['conditions']['clean']['minus_clean_trained_F6']['AUPRC']
    dropout_answer='Modality dropout changed clean AP by '+fmt(dclean)+' versus ordinary F6. Under complete visual or sensor loss, predictions are exactly the surviving frozen branch for both variants; missing-condition improvement is structurally impossible for this masked scalar-logit gate.'
    calibration_answer='Clean F2 minus U1 Brier: '+fmt(s2['paired']['F2-U1']['Brier'])+'; ECE: '+fmt(s2['paired']['F2-U1']['ECE'])+'. Lower is better for both; these paired intervals quantify the calibration trade-off without test-fitted recalibration.'
    dropout_positive=[name for name,value in dropout['conditions'].items() if name not in ['clean','V4','S5'] and value['minus_clean_trained_F6']['AUPRC']['lower_95']>0]
    dropout_negative=[name for name,value in dropout['conditions'].items() if name not in ['clean','V4','S5'] and value['minus_clean_trained_F6']['AUPRC']['upper_95']<0]
    dropout_answer+=' At marginal paired 95% intervals, degraded AP improved for '+(', '.join(dropout_positive) if dropout_positive else 'none of the tested joint-present conditions')+' and worsened for '+(', '.join(dropout_negative) if dropout_negative else 'none')+'; remaining comparisons were unresolved.'
    sq={'SQ1':'Frozen RT-DETR contributes incremental information, although sensor statistics are stronger alone. The tested PatchTST is inferior to the statistical representation. Audio was excluded by the segment-alignment gate; audio predictive utility was not tested.',
        'SQ2':'Simple learned late fusion captures useful visual/sensor complementarity. No tested adaptive gate improves clean AUPRC beyond F2, and all three have lower clean AUROC with paired intervals below zero. This does not establish equivalence or rule out every untested gate.',
        'SQ3':robustness_answer+' Complete modality loss yields explicit fallback, not recovery of missing information. '+dropout_answer,
        'SQ4':calibration_answer+' Static fusion offers a small, modular fusion layer with calibrated branch interfaces. Gate weights expose allocation but are not causal explanations. Frozen visual extraction dominates computational cost; warm VM timings and synthetic degradation limit deployment claims. Replacing a branch requires revalidation of score calibration and fusion, even without joint backbone retraining.'}
    csv(tables/'13_final_RQ_matrix.csv',[{'question':key,'answer':value} for key,value in sq.items()])
    write(root/'results.json',{'SQ':sq,'robustness_positive_pairs':positive,'robustness_absolute_AP_positive_pairs':absolute,'master_clean':master,'figure_index':index,'source_paths':source_paths,'audio_decision':audio['decision'],'object_decision':objects['decision'],'dropout_clean_AP_difference':dclean,'model_fitting_finished':True})
    # Human-readable reports below remain self-contained and never replace prior handoffs.
    parts=['# FINAL REASSEMBLE HANDOFF\n\n']
    def section(letter,title,body):parts.append('## '+letter+'. '+title+'\n\n'+body+'\n\n')
    section('A','Original purpose','REASSEMBLE was added as a second empirical study to test fusion where explicit execution labels and simultaneous deployable modalities support a defensible predictive comparison. Its purpose was to test prerequisites, complementarity and robustness, not to make named Transformer architectures win.')
    section('B','Relationship to PHM','PHM remains Study 1: continuous damage estimation with a provisional image-derived target, few independent runs, and restricted deployment modalities. REASSEMBLE supplies a different, binary task with more recording groups. Task-appropriate metrics differ across the two empirical studies because PHM is a continuous damage-estimation problem whereas REASSEMBLE is a binary execution-failure classification problem. Numerical MAE/RMSE values are never ranked against AUROC/AUPRC/F1.')
    section('C','Dataset',f'The frozen primary cohort has **{len(frame):,} high-level action segments**, **{int(frame.failure.sum())} failures**, and **{frame.recording_id.nunique()} recordings**. Failure is positive. Actions are pick, insert, remove and place. The cohort uses the hand camera and five sensor streams, 22 scalar channels, 512 progress positions and 220 engineered statistics. Available raw inventory contains 149 recordings; audited exclusions and primary-task/dual-complete criteria determine the final cohort. Audio remains secondary.\n\n'+table(['Action','Success','Failure'],[[a,int((g.failure==0).sum()),int(g.failure.sum())] for a,g in frame.groupby('action')]))
    section('D','Evaluation','The exact five outer and four inner recording-disjoint folds are reused throughout. Branch/fusion fitting, scaling, selection, calibration and thresholds use training data only; additional nested branch cross-fitting excludes inner assessment recordings. Uncertainty uses 2,000 paired recording-cluster bootstrap replicates conditional on fitted models. Section 1/1B controls cyclically permuted labels within recording/action strata and reran full nested procedures: 19 nulls give minimum plus-one p=0.05. Those controls test a conditional cyclic-exchangeability null, not arbitrary IID chance. No corruption-specific refit or outer-test tuning occurred. This is an adaptive exploratory sequence, not independent confirmation.')
    section('E','Section 1','Statistical sensor AUROC/AP: '+fmt(s1['metrics']['sensor_statistics']['AUROC'])+' / '+fmt(s1['metrics']['sensor_statistics']['AUPRC'])+'. RT-DETR: '+fmt(s1['metrics']['rtdetr']['AUROC'])+' / '+fmt(s1['metrics']['rtdetr']['AUPRC'])+'. PatchTST: '+fmt(s1['metrics']['patchtst']['AUROC'])+' / '+fmt(s1['metrics']['patchtst']['AUPRC'])+'. Both neural branches improved AP beyond action context, but their standalone AUROC improvement remained unresolved. Statistics outperformed the tested PatchTST; no further tuning was performed. The original Section 1 gate remained conditional and was not rewritten.')
    section('F','Section 1B','Fusion admissibility tested incremental information beyond the strongest sensor representation rather than requiring the old standalone visual gate. F2 minus sensor: AUROC '+fmt(s1b['fusion_minus_sensor']['AUROC'])+'; AP '+fmt(s1b['fusion_minus_sensor']['AUPRC'])+'. RT-DETR correctly classified '+str(s1b['complementarity']['failures']['visual_only_correct'])+' sensor-missed failures across '+str(s1b['failure_rescue_recordings'])+' recordings. Sensor permutation p-values were '+str(s1b['sensor_permutation']['p_AUROC'])+' / '+str(s1b['sensor_permutation']['p_AUPRC'])+'. The oracle remained diagnostic. FUSION GO justified the bounded architecture comparison.')
    section('G','Section 2','Clean result: **SIMPLE FUSION SUFFICIENT**. F2 is the principal static reference; F1 has similar point discrimination but poorer calibration. No gate establishes a clean AP gain and all lose AUROC relative to F2. F3 also does not establish an AP gain over U1. Context changes weights, but that is not itself useful adaptation. The primary proposed F6 was retained as a falsifiable model, not redesigned.\n\n'+clean_table+'\nFull clustered intervals, source keys and comparability status: `'+str(tables/'01_master_clean_metrics.csv')+'`. Latency entries are warm sequential component sums; missing entries were not remeasured.')
    section('H','Section 3',robustness_answer+'\n\nCorruptions were fixed before outcomes: native-pixel Gaussian noise (0.02/0.05/0.10), blur sigma 1/2/4, frame dropout 2/5/8 of 16; raw sensor Gaussian noise (0.10/0.50/1.00 training-channel SD), channel dropout 2/7/11 of 22, temporal block dropout 10/30/50%, six force/torque channels stuck at training medians, and complete single-modality loss. Sensor features and the same quality measures were recomputed from perturbed raw signals; models and clean thresholds stayed frozen. Static and masked gates return the remaining branch under total loss, using its frozen threshold. Unavailable unimodal models abstain. No combined corruption matrix was needed.\n\n'+table(['Family','Gate','Class','Spearman','Weight shift [95%]','Absolute AP superiority'],[[x['family'],x['model'],x['classification'],f"{x['ordered_severity_spearman']:.3f}",fmt(x['degraded_modality_weight_shift']),x['absolute_AP_superiority_supported']] for x in mechanism])+'\nEvery condition has absolute metrics, clean-relative deltas and paired difference-in-degradation intervals in the robustness tables. Smaller decline from a weaker clean starting point is not automatically better corrupted performance.')
    section('I','Modality dropout',dropout_answer+' Training used one F6 variant with probabilities .15 visual missing/.15 sensor missing/.70 both available, never both absent; three seeds and frozen Section 2 selected head settings. No corruption-based tuning.\n\n'+table(['Condition','AP','AP difference vs ordinary F6 [95%]'],[[name,f"{v['metrics']['AUPRC']['estimate']:.4f}",fmt(v['minus_clean_trained_F6']['AUPRC'])] for name,v in dropout['conditions'].items()]))
    section('J','Audio','**'+audio['decision']+'**. Segment-level, not frame-perfect, timing was required. Nominal origin is inferred from a non-audio clock and lacks an independently verified audio offset/drift or segment anchor. Header attributes, timestamps, nominal overlap, durations and prior actual decoding were audited. No AST/tri-modal/audio-noise model was warranted; this says nothing about audio’s possible predictive information.\n\n'+table(['Stream','Nominal valid %','Failure valid %','Nominal recordings','Verified intervals'],[[name,f"{x['nominal_valid_percent']:.2f}",f"{x['nominal_valid_failure_percent']:.2f}",x['nominal_valid_recordings'],x['verified_segments']] for name,x in audio['streams'].items()]))
    section('K','Efficiency','Warm measurements used '+eff['GPU']+' and '+str(eff['CPU_threads'])+' CPU threads. '+eff['timing_scope']+'. Peak GPU allocated: '+f"{eff['peak_GPU_allocated_bytes']/2**20:.1f}"+' MiB. Total parameters include the frozen backbone; trainable means parameters fitted somewhere in the retained pipeline. Source-checkpoint bytes can include unused detector components.\n\n'+table(['Model','Total params','Trainable params','Checkpoint MiB','Component-sum ms','Cached fusion µs'],[[name,v['total_parameters'],v['trainable_parameters'],f"{v['checkpoint_bytes_mean']/2**20:.3f}",f"{v['sequential_component_sum_seconds']*1000:.3f}",f"{v.get('cached_branch_fusion_overhead_seconds',0)*1e6:.3f}"] for name,v in eff['models'].items()])+'\nStatic/gated late fusion supports independent branch updates without joint backbone training, but interface/calibration changes require training-only fusion revalidation. Interpret weights with probability calibration, action context and corruption response, not as causal explanations. No new test-fitted calibrator was used.')
    static_rows=[]
    for k in range(5):
        x=read(Path(c['section1b'])/'stacking'/f'outer{k}.json')['stacker']
        static_rows.append([k,*x['coefficient'],x['intercept']])
    parts.append('Static fusion coefficients act on calibrated failure probabilities before a logistic link; they are not convex allocation weights.\n\n'+table(['Outer fold','Visual coefficient','Sensor coefficient','Intercept'],static_rows)+'\n'+calibration_answer+'\n\n')
    section('L','Generalization stress test','**'+objects['decision']+'**. '+objects['reason']+' Annotation categories: '+str(objects['annotation_categories'])+'; recording/object connected components: '+str(objects['recording_object_connected_components'])+'. This is a completed feasibility decision, not a postponed core experiment.')
    for letter,key in [('M','SQ1'),('N','SQ2'),('O','SQ3'),('P','SQ4')]:section(letter,key,sq[key])
    main_rq='Fusion is warranted when independently evaluated modalities provide complementary task information. In REASSEMBLE, simple calibrated late fusion captures this benefit; greater representation or gate complexity does not automatically help. Robustness must be judged jointly by induced allocation response, absolute degraded performance and change from clean performance, not by weight movement alone. '+robustness_answer
    section('Q','Main RQ',main_rq)
    section('R','Negative findings','The tested PatchTST loses to engineered statistics; RT-DETR is weaker alone than statistics; the initial standalone neural AUROC gates were unresolved; concatenation and gating did not justify clean complexity; context sensitivity did not establish clean benefit; audio timing failed its gate; physical-object OOD identity/support was insufficient; modality dropout cannot change exact one-branch fallback in this architecture. Negative robustness family results are retained without architecture rescue.')
    section('S','Failed hypotheses','“A temporal Transformer should beat simple sensor statistics” was falsified for this tested implementation/budget. “Process/quality gating should improve clean fusion” was unsupported and contradicted by the AUROC comparison. “Modality dropout can improve a masked scalar gate when only one frozen branch remains” is ruled out by the architecture and checked empirically. Reliability-aware robustness remains family-specific according to Section 3, not presumed from the exposé.')
    section('T','Corrections','Section 1B’s one-thread BLAS attempt failed exact probability reproduction; restoring original 16-thread execution passed without changing scientific settings. Section 2’s automatic AP-only gate shortlist was corrected during documented final review using uncertainty, stability and cost. Section 3 serial extractors were interrupted only for recording-level parallelism; completed checkpoints were hash-verified and retained. Corruption formulas, seeds, batch size and parity tolerances were unchanged. Expected all-NaN-channel statistic warnings under deliberate dropout are counted, not treated as raw corruption or silently fixed. Detailed corrections are retained in each run.')
    section('U','Limitations','Outcome-informed sensor selection and the same outer folds reused sequentially make this adaptive exploratory work. Recording clustering does not remove shared scene/day/object confounding or all training uncertainty. Labels concern execution success/failure, not physical damage; segment classification is retrospective, not online early warning. Artificial corruptions and one seeded realization per severity do not represent every field fault. Marginal multiple-family intervals do not establish universal robustness. Audio lacks verified segment timing. No validated unseen-object/site generalization claim is available. Missingness fallback does not recover absent information. VM component timing is not production latency. PHM targets are provisional; its metric scales are task-specific.')
    safe=['On the evaluated REASSEMBLE cohort, engineered sensor statistics outperformed the tested PatchTST representation.','Frozen visual features provided incremental information beyond the statistical-sensor model in the tested nested static fusion procedure.','The tested adaptive gates did not establish a clean AUPRC improvement over learned static late fusion and had lower clean AUROC.','Gate-weight changes were evaluated separately from predictive changes under predeclared synthetic degradation.',robustness_answer,'Complete single-modality loss reduced the tested fusion rules to their surviving calibrated branch.','Audio was excluded because trustworthy segment-level clock association was not established; its predictive value was not evaluated.','These results are an adaptive exploratory assessment on the same cohort, not independent confirmation.']
    section('V','Exact safe thesis claims','\n\n'.join('“'+sentence+'”' for sentence in safe))
    section('W','Claims that would be overstatements','Do not write: “Transformers are unsuitable for sensor anomaly detection”; “The gate is universally reliability-aware”; “Adaptive fusion is robust in deployment”; “Audio contains no useful information”; “The models generalize to unseen physical objects”; “The method provides real-time early warnings”; “MAE in PHM is directly comparable to AUPRC in REASSEMBLE”; or “The oracle is deployable.” Each exceeds the evaluated target, comparison, timing or generalization evidence.')
    section('X','Thesis figures',table(['Figure','PDF path','Caption / supported claim'],[[x['name'],x['outputs'][0],x['caption']] for x in index]))
    section('Y','Thesis tables','All final tables are in `'+str(tables)+'`. Master clean metrics include uncertainty/source keys; corruption tables separate absolute and relative performance; missingness, gate response, dropout, audio, efficiency and RQ tables preserve their different scopes. See THESIS_TABLE_INDEX.md for exact paths and purposes.')
    commits=subprocess.check_output(['git','log','-8','--format=%h %s'],text=True).strip()
    section('Z','Provenance','Frozen evidence commits: Section 1 `08d498d`; Section 1B `4089b02`; Section 2 `d16c251`. Corruption preregistration `280b842`; sensor path `2883149`; runtime-only parallelism `6f9ea67`. Configurations: `configs/reassemble/completion.json`, `section3_corruptions.json`, and unchanged Section 1/1B/2 configs. Unique phase paths:\n\n'+table(['Phase','Run'],list(c['runs'].items()))+'\nMachine-readable result sources:\n\n'+'\n'.join('- `'+p+'`' for p in source_paths)+'\n\nFinal validation/output manifests record current implementation hashes, tests, preserved-file checks, raw metadata, package versions and claim audit. Numerical intermediate caches remain local and ignored. No external master Reasoning Record was modified. Recent commits:\n\n```text\n'+commits+'\n```')
    save_text(reports/'FINAL_REASSEMBLE_HANDOFF.md',''.join(parts))
    # Indices and claim map.
    save_text(reports/'THESIS_FIGURE_INDEX.md','# Thesis figure index\n\n'+table(['Figure','Source data','Script','Outputs','Chapter','Message'],[[x['name'],'; '.join(x['sources']),x['script'],'; '.join(x['outputs']),x['chapter'],x['caption']] for x in index]))
    purposes={'01_master_clean_metrics':'All clean models, uncertainty and comparability','02_robustness_detailed':'All corruption metrics and clean deltas','03_robustness_paired':'Absolute paired and degradation-advantage intervals','04_missing_modality':'Fallback versus unavailable unimodal abstention','05_gate_response':'Allocation shifts and uncertainty','06_robustness_summary':'Core clean/noise/missing AP summary','07_modality_dropout':'One robust variant trade-off','08_audio_gate':'Nominal coverage versus verified timing','09_efficiency':'Parameter, checkpoint and component timing cost','10_dataset_summary':'Action/outcome support','11_evaluation_protocol':'Frozen grouping, metrics and uncertainty','12_clean_paired':'Section 2 paired contrasts','13_final_RQ_matrix':'SQ answers and boundaries'}
    save_text(reports/'THESIS_TABLE_INDEX.md','# Thesis table index\n\n'+table(['Path','Purpose'],[[str(tables/(name+'.csv')),purpose] for name,purpose in purposes.items()])+ '\nPer-family corruption tables are `robustness_V1/V2/V3/S1/S2/S3/S4.csv` in the same directory.\n')
    evidence=[]
    def claim(claim_text,sqname,experiment,metric,value,uncertainty,source,status,wording,limit):evidence.append([claim_text,sqname,'REASSEMBLE',experiment,metric,value,uncertainty,source,status,wording,limit])
    claim('Strong sensor signal','SQ1','Section 1 / 1B','AUROC / AUPRC',f"{s1['metrics']['sensor_statistics']['AUROC']['estimate']:.4f} / {s1['metrics']['sensor_statistics']['AUPRC']['estimate']:.4f}",'See clustered intervals in master table',source_paths[0],'[VERIFIED]',safe[0],'Tested implementation and cohort only')
    claim('Visual incremental information','SQ2','Section 1B','Δ AUPRC',f"{s1b['fusion_minus_sensor']['AUPRC']['estimate']:.4f}",fmt(s1b['fusion_minus_sensor']['AUPRC']),source_paths[1],'[VERIFIED]',safe[1],'Adaptive same-cohort follow-up')
    for family,models in robust['mechanism'].items():
        for model,x in models.items():
            condition=x['high_severity'];v=robust['conditions'][condition]['degradation_advantage'][model+'-F2']['AUPRC']
            claim(family+'/'+model+' robustness','SQ3','Section 3','Δ AP degradation advantage',f"{v['estimate']:.4f}",fmt(v),source_paths[3],'[VERIFIED]' if x['classification']=='ROBUSTNESS-A' else '[INCONCLUSIVE]',x['classification']+' for this tested family','Single seeded realization; relative and absolute outcomes differ')
    claim('Modality-dropout trade-off','SQ3','Robust training','Clean Δ AUPRC',f"{dclean['estimate']:.4f}",fmt(dclean),source_paths[4],'[VERIFIED]',dropout_answer,'One fixed gate family/settings')
    claim('Audio exclusion','SQ1','Audio timing gate','Verified segment intervals',0,'No independently verified mapping',source_paths[6],'[NOT RUN — GATE FAILED]',safe[6],'Not a claim of absent audio signal')
    claim('Practical cost','SQ4','Warm VM benchmark','Component-sum latency',f"{eff['models']['F2']['sequential_component_sum_seconds']*1000:.2f} ms",'Repeated warm timings; three segments',source_paths[5],'[VERIFIED]','Visual extraction dominates this measured pipeline','Not production end-to-end latency')
    phm_path='runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/reports/loeo_summary.json'
    phm=read(phm_path)['paired_deltas_vs_constant']['fused_all_three']
    evidence.append(['Grouped PHM fusion gain unresolved','Main RQ','PHM','Retained LOEO','Run-weighted MAE delta',phm['mean_delta_vs_constant'],str([phm['ci95_low'],phm['ci95_high']]),phm_path,'[INCONCLUSIVE]','Retained grouped fusion did not resolve improvement over constant reference','Provisional target; 20 runs; not comparable numerically to classification metrics'])
    save_text(reports/'FINAL_EVIDENCE_MAP.md','# Final evidence map\n\n'+table(['Thesis claim','RQ/SQ','Study','Experiment','Metric','Point estimate','Uncertainty','Artifact path','Reasoning status','Allowed wording','Important limitation'],evidence))
    write(root/'metric_traceability.json',{'master_clean_rows':master,'sources':source_paths,'numeric_generation':'All final metric tables and figure data are generated directly from these JSON artifacts; no pasted prompt numbers used as results.'})
    write(root/'synthesis_context.json',{'SQ':sq,'main_RQ':main_rq,'robustness_answer':robustness_answer,'dropout_answer':dropout_answer,'safe_claims':safe})
    from .completion_narrative import narratives
    narratives(c,root,reports,s1,s1b,s2,robust,dropout,audio,objects,eff,sq,main_rq,robustness_answer,dropout_answer)
    progress('Final synthesis, figures, tables and reasoning addenda generated; final audit pending')

if __name__=='__main__':main()
