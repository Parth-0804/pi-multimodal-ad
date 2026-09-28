"""Consolidate only executed evidence; never promote pending work to complete."""
from pathlib import Path
import json
import subprocess
from datetime import datetime,timezone
import numpy as np
import pandas as pd
from reassemble.completion_audit import preservation
from reassemble.section2_data import verify_manifest
from reassemble.section1_features import cohort,sha
from reassemble.section1_report import metrics,METRICS,table
from .common import config,read,write,identity,TASKS
from .numerical_audit import audit as numerical_audit

PRINCIPAL=[(1,'comparison/results.json','V-TEMP minus V-MEAN'),(2,'comparison/results.json','S-LONG minus S-6'),(3,'comparison/results.json','A-ADAPTIVE minus A0')]

def main():
    c=config();root=Path(c['run_dir']);out=root/'05_final_comparison';states={name:read(root/name/'status.json') for name in TASKS}
    assert not any(v['state'] in ['not_started','running'] for v in states.values()),'Pending work: cannot finalize yet'
    completed=all(v['state']=='complete' for v in states.values());status='ADDITIONAL IMPROVEMENTS EXECUTED — EXPLORATORY RESULTS READY FOR REVIEW' if completed else 'ADDITIONAL IMPROVEMENTS PARTIALLY EXECUTED — BLOCKERS DOCUMENTED'
    base=read(c['section1_config']);frame=cohort(base);y=frame.failure.to_numpy(int);contrasts={};registry=[];clean=[];source_reports=[]
    for task,relative,key in PRINCIPAL:
        path=root/TASKS[task-1]/relative
        if not path.exists():continue
        result=read(path);contrasts[key]=dict(task=task,**result['contrasts'][key],source=identity(path))
        for name,record in result['models'].items():
            clean.append(dict(task=task,model=name,**{m:record['metrics'][m]['estimate'] for m in METRICS}))
            registry.append(dict(task=task,variant=name,source=identity(path),status='executed',folds=record['folds'],seeds=record['seeds']))
    robust_path=root/TASKS[3]/'results.json'
    if robust_path.exists():
        result=read(robust_path);effect=result['primary_seen_family_contrast'];ap=effect['AUPRC'];interpretation='supported improvement' if ap['lower_95']>0 else ('supported deterioration' if ap['upper_95']<0 else 'inconclusive difference')
        contrasts['augmented A-ADAPTIVE minus augmented F2, mean seen-family AP']=dict(task=4,metrics=effect,AP_interpretation=interpretation,source=identity(robust_path))
        pd.read_csv(root/TASKS[3]/'paired_comparisons.csv').to_csv(out/'robustness_comparisons.csv',index=False)
        for model,record in result['absolute']['clean'].items():clean.append(dict(task=4,model=model,**{m:record[m]['estimate'] for m in METRICS}))
        registry.extend(dict(task=4,variant=model,status='executed',source=identity(robust_path)) for model in result['absolute']['clean'])
    else:pd.DataFrame(columns=['condition','contrast','AUPRC','AP_lower95','AP_upper95']).to_csv(out/'robustness_comparisons.csv',index=False)
    for task,relative in [(1,'finetune_comparison/results.json'),(2,'hybrid_comparison/results.json')]:
        path=root/TASKS[task-1]/relative
        if path.exists():
            result=read(path)
            for name,record in result['models'].items():
                if name not in ['V-FT','S-HYBRID']:continue
                clean.append(dict(task=task,model=name,**{m:record['metrics'][m]['estimate'] for m in METRICS}));registry.append(dict(task=task,variant=name,status='executed',source=identity(path),folds=record['folds'],seeds=record['seeds']))
    pd.DataFrame(clean).to_csv(out/'clean_comparisons.csv',index=False)
    write(out/'experiment_registry.json',dict(label=c['status_label'],models=registry,task_statuses=states,configuration=identity('configs/reassemble/additional_improvements/execution.json'),source_directory='src/reassemble/additional_improvements',checkpoints='Per-fit checkpoint paths and SHA256 are retained in each task fits/*.json and the output manifest'))
    historical=read(c['completed_config']);preserved=preservation(historical);preserved['completed_manifests']={str(Path(path)/'output_manifest.json'):verify_manifest(Path(path)/'output_manifest.json') for path in historical['runs'].values()}
    write(root/'00_protocol_and_preservation/preservation_after.json',preserved)
    validations=[]
    for task in TASKS[:2]:
        for path in (root/task).glob('*_predictions.npz'):
            with np.load(path) as z:
                assert np.array_equal(z['y'],y) and len(z['p'])==len(frame);assert np.isfinite(z['p']).all()
                assert np.all((z['p']>=0)&(z['p']<=1))
                for rid,rows in frame.groupby('recording_id'):assert len(np.unique(z['fold'][rows.index]))==1
                if 'seed_p' in z:assert np.allclose(z['p'],z['seed_p'].mean(0),atol=1e-12,rtol=0)
            validations.append(identity(path))
    command_checks=[]
    for command in [[str(Path('ma_thesis_env/bin/python')),'-B','-m','pytest','-q','tests/reassemble'],['git','diff','--check']]:
        process=subprocess.run(command,text=True,capture_output=True,env={**__import__('os').environ,'PYTHONPATH':'src'})
        record=dict(command=command,returncode=process.returncode,stdout=process.stdout,stderr=process.stderr);command_checks.append(record)
        if process.returncode:write(out/'validation_failed.json',dict(checks=command_checks));raise RuntimeError('Required validation failed')
    numerical=numerical_audit(c,frame)
    validation=dict(preservation=preserved,checks=command_checks,prediction_integrity=validations,numerical_recalculation=numerical,dependency_check='Existing environment pip check passed; no dependency changes made',timestamp_UTC=datetime.now(timezone.utc).isoformat())
    write(out/'validation.json',validation)
    commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();gitstate=subprocess.check_output(['git','status','--short','--branch','--untracked-files=all'],text=True)
    source=[identity(p) for p in sorted(Path('src/reassemble/additional_improvements').glob('*.py'))]
    write(out/'results_summary.json',dict(label=c['status_label'],status=status,primary_contrasts=contrasts,task_statuses=states,cohort=dict(segments=len(frame),failures=int(y.sum()),recordings=frame.recording_id.nunique()),git_commit=commit,git_state=gitstate,sources=source,configuration=identity('configs/reassemble/additional_improvements/execution.json')))
    rows=[];sentences=[]
    for name,r in contrasts.items():
        ap=r['metrics']['AUPRC'];au=r['metrics']['AUROC'];rows.append([r['task'],name,f'{ap["estimate"]:+.4f} [{ap["lower_95"]:+.4f},{ap["upper_95"]:+.4f}]',f'{au["estimate"]:+.4f} [{au["lower_95"]:+.4f},{au["upper_95"]:+.4f}]',r['AP_interpretation']])
        sentences.append(f'In additional exploratory experiments on the same REASSEMBLE cohort, {name} changed average precision by {ap["estimate"]:+.4f} (marginal paired95% interval {ap["lower_95"]:+.4f} to {ap["upper_95"]:+.4f}); the AP contrast was classified as {r["AP_interpretation"]}.')
    summary_table=table(['Task','Frozen primary contrast','ΔAP,95%','ΔAUROC,95%','Interpretation'],rows)
    reports=['01_TEMPORAL_VISUAL_RESULTS.md','02_PATCHTST_BUDGET_RESULTS.md','03_STATIC_ANCHORED_ADAPTATION_RESULTS.md','04_CORRUPTION_TRAINING_RESULTS.md']
    for report in reports:
        path=root/'reports'/report
        if path.exists():source_reports.append(identity(path))
    attempts=sorted(str(p) for p in root.rglob('*') if p.is_file() and ('correction' in p.name or 'attempt' in p.name or 'failure' in p.name or 'deviation' in p.name))
    text='# Additional improvements executed — handoff\n\n'+status+'\n\nADDITIONAL EXPLORATORY EXPERIMENTS. Original study remains completed evidence.\n\n'
    text+='Why these follow-ups: temporal averaging may discard visual order (Task1); the original PatchTST selected its six-epoch ceiling (Task2); successful F2 and unsuccessful original F6 differ in fusion link, motivating bounded adjustments around F2 (Task3); clean-only training may explain poor degradation handling, requiring exposure-matched static and adaptive controls (Task4). None was assumed to win.\n\n'
    text+=summary_table+'\n'
    text+='Historical references and matched controls are both retained. Exact configurations, selected/refit epochs, learning curves, predictions, all eight metrics, per-seed/per-fold results, compute costs, diagnostics and limitations are in the four task reports and machine-readable sources below. AP means average precision; all intervals are marginal and conditional on fitted models. Task4 additionally resamples realization indices and averages per-realization metrics, not noisy predictions. The prespecified .01 AP reference is not an industrial requirement.\n\n'
    text+='Thesis-safe result sentences:\n\n'+''.join('- '+sentence+'\n' for sentence in sentences)+'\n'
    text+='Original conclusions remain tied to their original tested procedures and budgets. Longer training can qualify the scope of the earlier PatchTST negative finding, but cannot change its recorded result. A successful new anchored form would extend the original clean-fusion comparison, not retroactively make original F6 successful. Reliability adaptation requires both predictive gain over equally augmented static fusion and appropriate coefficient response; structural missing-modality fallback is not learned recovery.\n\n'
    text+='Unsupported claims: independent confirmation, universal temporal-Transformer superiority, causal reliability coefficients, equivalence from non-significance, general industrial robustness, audio/physical-object generalization, or benefits of combining winners. No new combined architecture was trained; any combination requires a separate protocol.\n\n'
    text+='Task status:\n\n'+''.join(f'- {name}: {state["state"]} — {state["stage"]}.\n' for name,state in states.items())+'\n'
    text+='Failed attempts/corrections/deviations (all retained):\n\n'+''.join('- `'+path+'`\n' for path in attempts)+'\n'
    text+='Evidence paths:\n\n'+''.join('- `'+record['path']+'` (SHA256 '+record['sha256']+').\n' for record in source_reports)+'\n'
    text+=f'Protocol commit:26ae3a7. Initial completed Task3/source commit:484bd35. Final source commit at consolidation:`{commit}`. Exact current source hashes, configuration identity and Git state: `05_final_comparison/results_summary.json`. All artifact/checkpoint identities: `05_final_comparison/output_manifest.json`; fit metadata retains training and assessment row identities. Validation/preservation: `05_final_comparison/validation.json`. External master Reasoning Record was not modified.\n'
    (root/'reports/ADDITIONAL_IMPROVEMENTS_EXECUTED_HANDOFF.md').write_text(text)
    storyline='# Additional improvements — storyline addendum\n\nADDITIONAL EXPLORATORY EXPERIMENTS. Append-only thesis material; external master record untouched.\n\n'
    for task,question,hypothesis,method,consequence in [
        (1,'Does visual frame order help?','Temporal averaging may lose execution cues.','Matched mean/temporal/no-position heads and separate limited spatial fine-tuning.','Require the no-position comparison before attributing a benefit to order.'),
        (2,'Did the six-epoch cap limit PatchTST?','A reasonable longer budget may change the relative ranking.','Identical PatchTST with matched3/6 and bounded100-epoch budgets; strictly nested same-sensor hybrid.','Distinguish budget benefit, superiority to statistics, and incremental temporal information.'),
        (3,'Can adaptation improve the successful static fusion form?','Bounded context-dependent coefficients may exploit information missed by a fixed stacker.','Frozen F2 anchor versus global and contextual tanh adjustments.','Action priors and ordinary coefficient changes remain alternatives to reliability explanations.'),
        (4,'Does degradation exposure support adaptive robustness?','Clean-only fitting may explain previous fragile gates.','Equal corruption exposure for static/F6/anchored models, separate fault realizations and augmentation-held-out families.','Require improvement beyond equally exposed static fusion plus an appropriate response; preserve clean-performance uncertainty.')]:
        storyline+=f'QUESTION: {question}\n\nORIGINAL EVIDENCE: see the completed study references in the execution protocol; its conclusions remain frozen.\n\n[HYPOTHESIS] {hypothesis}\n\nMETHOD: {method}\n\n'
        for name,r in contrasts.items():
            if r['task']==task:
                v=r['metrics']['AUPRC'];tag='[INCONCLUSIVE]' if r['AP_interpretation']=='inconclusive difference' else '[OBSERVED RESULT]';storyline+=f'{tag} {name}: ΔAP {v["estimate"]:+.4f},95% [{v["lower_95"]:+.4f},{v["upper_95"]:+.4f}].\n\n'
        storyline+='ALTERNATIVE EXPLANATIONS: same-cohort outcome-informed design, finite seeds and recording-cluster uncertainty; no independent confirmation.\n\nCONSEQUENCE: '+consequence+'\n\n'
    storyline+='[CORRECTED] Failed attempts and numerical/engineering corrections are listed in the executed handoff. [NOT RUN] Automatic combination of whichever interventions perform best; new architectures/budgets; audio; object-OOD; PHM experiments.\n'
    (root/'reports/ADDITIONAL_IMPROVEMENTS_STORYLINE_ADDENDUM.md').write_text(storyline)
    (root/'reports/ADDITIONAL_IMPROVEMENTS_STATUS.md').write_text('# Additional improvements status\n\n'+status+'\n\n'+''.join(f'- {name}: **{state["state"]}** — {state["stage"]}.\n' for name,state in states.items())+'\nSee executed handoff, storyline addendum, results_summary.json and validation.json. No automatic next model is authorized. Stop after this extension.\n')
    (root/'reports/CONTINUATION.md').write_text('# Additional exploratory experiments — continuation\n\n'+status+'\n\nRun: `'+str(root)+'`. See `ADDITIONAL_IMPROVEMENTS_EXECUTED_HANDOFF.md`, `ADDITIONAL_IMPROVEMENTS_STATUS.md`, and `05_final_comparison/validation.json`.\n\nNo further model, budget expansion, or winner combination is authorized. Original study and external Reasoning Record are unchanged.\n')
    # Reuse identities already recorded on successful cache writes; hash compact files directly.
    known={}
    def collect(value):
        if isinstance(value,dict):
            if all(k in value for k in ['path','sha256','bytes']):known[value['path']]=value
            for v in value.values():collect(v)
        elif isinstance(value,list):
            for v in value:collect(v)
    for p in root.rglob('*.json'):
        try:collect(read(p))
        except (ValueError,OSError):pass
    manifest=[]
    for path in sorted(root.rglob('*')):
        if not path.is_file() or path==out/'output_manifest.json' or path.name.endswith('.log') or '.writing' in path.name or path.name.startswith('supervisor'):continue
        entry=known.get(str(path))
        if entry is None or path.stat().st_size!=entry['bytes'] or path.suffix not in ['.npz','.pt','.joblib']:entry=identity(path)
        manifest.append(entry)
    write(out/'output_manifest.json',dict(files=manifest,scope='New extension only; numerical outputs/checkpoints retained locally. Cache hashes reused from successful immutable writes; original preservation verified separately.',timestamp_UTC=datetime.now(timezone.utc).isoformat()))
    print(status,flush=True)

if __name__=='__main__':main()
