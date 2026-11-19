"""Final human-review tables and measured computational-cost distinctions."""
import csv
import json
import re
from audit_common import OUT,REPO,read,text,csv_read,csv_write,flush_evidence
from render_reports import table,report,FAMILIES


def replace_section(path,heading,body):
    p=OUT/path;s=p.read_text();start=s.index(heading);end=s.find('\n## ',start+4)
    p.write_text(s[:start]+heading+'\n\n'+body.strip()+'\n'+(s[end:] if end>=0 else ''))


def main():
    executive='01_executive_overview/EXECUTIVE_AUDIT_SUMMARY.md'
    a=table(['Dataset','Model','Architecture','Status','Results available'],[
        [d,m,arch,'Evaluation/diagnostic only' if i in ['F01','F30','F31'] else 'PARTIAL aggregate lineage' if i=='F32' else 'Implemented; completed variants indexed',
         'Saved metrics/linked sources; no gradient fit' if i in ['F01','F30','F31'] else 'Per-study/fold/seed result CSVs; missing variants explicit'] for i,d,m,arch,s,f in FAMILIES])
    replace_section(executive,'## TABLE A — ALL IMPLEMENTED MODELS',a)
    pair=[r for r in read(OUT/'03_hyperparameter_configuration/EFFECTIVE_CONFIGURATIONS.json') if r['experiment_id']=='REASSEMBLE_100E_SINGLE_FIT']
    cost=csv_read(OUT/'04_training_and_checkpoints/TRAINING_DURATION_AND_GPU_USAGE.csv');byid={r['run_id']:r for r in cost}
    d=table(['Model','Executed epochs','Selected epoch','Training hours','Peak allocated GiB','AP','AUROC','Checkpoint path'],[
        [r['model'],100,r['effective_configuration']['selected_epoch'],r['duration_training_hours'],float(byid[r['run_id']]['peak_allocated_VRAM_GiB']),
         .19377557761499092 if r['model']=='B_frozen100' else .21258450333908707,
         .6646046261430877 if r['model']=='B_frozen100' else .6753246753246753,r['checkpoint_path']] for r in pair])
    replace_section(executive,'## TABLE D — FROZEN VS FINETUNED CNN',d)
    g=table(['Model/study','Code available','Config available','Checkpoint available','Predictions available','Split available','Overall status'],[
        ['Phase1 C20/B and B/C100','Yes,with provenance','Yes','Best + rotating resumable last states','Yes','Yes','COMPLETE saved chain; training replay not performed'],
        ['Original REASSEMBLE branches','Yes','Yes','Selected outer states; many inner states absent','Yes','Yes','PARTIAL'],
        ['Original F2','Yes','Yes','JSON coefficients','Yes,OOF and held-out','Yes','COMPLETE fitted-state chain'],
        ['100-epoch F2','Yes','Yes','Coefficients/calibrators','Yes,M1–M7','Yes,920 stack and753 assessment','COMPLETE artifacts; limited design'],
        ['MSM/Handover baselines','Yes','Yes','Fitted heads/LR/HGB','Yes','Yes;Handover participants absent','INFERENCE_ONLY / PARTIAL exact resume'],
        ['MSM F2/gates','Yes','Yes','JSON/PT states','Yes,OOF/held-out','Yes','INFERENCE_ONLY'],
        ['Handover F2/gates','Yes','Yes','No','No','Participant OOF unavailable','MISSING_ARTIFACTS; NOT EXECUTED'],
        ['Vi frozen V1/high-only','Yes','Yes','BEST and FINAL_EPOCH100','Yes','Yes,task groups','COMPLETE saved chain'],
        ['Vi sensors/meta','Yes','Yes','Selected models; discarded HGB candidates absent','Yes','Yes','INFERENCE_ONLY / PARTIAL candidate replay'],
        ['PHM canonical models','Yes,current/recorded revision','Yes','Present; some safe loaders decline','Yes','Yes','PARTIAL; provisional target'],
        ['PHM aggregate fusions','Current source','Yes/source constants','Per-fit states not retained','Aggregate scores only','Source-defined','METRICS_ONLY']])
    replace_section(executive,'## TABLE G — REPRODUCIBILITY',g)
    missing=[
        ['Handover fusion','Official pseudonymous participant mapping','Cannot certify participant OOF or split independence','Publisher metadata may recover it','Obtain mapping; do not infer identities'],
        ['REASSEMBLE original75','50 other-seed fits and C20 F2 finalization','One-seed coverage only;fusion result absent','Requires future authorized work','Review scope/cap before any execution'],
        ['100-epoch pilot','Other seeds/folds,fresh assessment,full nested100-epoch OOF','Cannot generalize visual/fusion gain','Requires separate study','Agree independent comparison design'],
        ['Vi full/transfer','V2/V3 trained head/fusion results','No adaptation/transfer performance claim','Future authorized work only','Resolve75-fit gate versus25-fit cap'],
        ['External R transfer','Completed R runs and accepted canonical donor','20 epochs fails validator minimum25','Protocol/validator decision required','Resolve contract; preserve historical evidence'],
        ['Historical states','Inner weights,optimizer/scheduler/RNG,exact epochs','Not every fit is loadable/resumable','Some logs may recover metadata','Keep graded reproducibility status'],
        ['GPU cost','Full allocation/extraction/telemetry history','No exact global GPU-hours total','Scheduler logs if retained','Recover accounting separately'],
        ['Physical independence','Tool/workpiece/session/clock metadata','Nominal groups may not equal physical independence','Publisher evidence may help','Declare actual grouping limits'],
        ['PHM legacy','Per-fit states/epochs and consistent target/scaler lineage','Aggregate-only results and preprocessing defect','Some records may exist;correction is separate work','Review defects without rewriting outputs'],
        ['Future HPO','Agreed endpoint,assessment,selection criteria and budget','No justified final choice yet','Independent research decision','Review audit before authorization'],
        ['Audit coverage','Unlogged/deleted fits or external artifacts','Counts cover discovered evidence,not unknown history','Only with additional records','Supply any missing provenance']]
    h=table(['Experiment','Missing evidence','Impact','Can it be recovered?','Required next action'],missing)
    replace_section(executive,'## TABLE H — MISSING EVIDENCE',h)
    report('07_scientific_validity/MISSING_EVIDENCE.md','Missing evidence required for independent verification',h+"""

Unknown values remain NOT RECORDED; suspected defaults are FRAMEWORK DEFAULT — NOT VERIFIED; absent intervals are NOT AVAILABLE. Blocked or planned models are NOT EXECUTED,not failed trained models. Large raw data/checkpoints/predictions intentionally remain at original paths,with recorded hashes and source identities. No deleted/unlogged historical work can be reconstructed from a folder name alone.
""")
    report('04_training_and_checkpoints/REPRODUCIBILITY_ASSESSMENT.md','Reproducibility assessment',g+"""

Loading for inference,replaying evaluation,resuming optimization and reproducing from initialization are different capabilities. Selected model states may support inference while lacking optimizer/scheduler/RNG for exact resume. A last recovery slot does not replace the validation-selected best model. Current code bytes are not proof of historical execution: use preserved snapshots and recorded source hashes. Existing dirty worktree provenance is retained.

The audit hashed4,920 binary candidates and safely inspected3,828 on CPU. Declined weights-only Torch loads were not retried with unsafe pickle. Known study-owned small sklearn models were inspected only after receipt-hash verification. Twenty-eight Phase1/100-epoch AdamW states yielded literal betas/epsilon by static pickle-opcode inspection without execution. No checkpoint used GPU memory.

JSON_FITTED_STATE_REFERENCES.csv adds428 run-to-JSON-state references beyond the binary inventory; several can reference the same file. CHECKPOINT_INVENTORY records aliases and available optimizer/scheduler/RNG evidence. Complete training status does not automatically certify independent assessment,exact replay or all-state resume.
""")
    provenance='26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_evidence/PHASE1_COMPARISON_PROVENANCE.json'
    read(provenance)
    report('04_training_and_checkpoints/GPU_AND_COMPUTATIONAL_COST_AUDIT.md','GPU and computational cost audit',"""
Historical100-epoch provenance records **one NVIDIA Tesla T4,16,384MiB,driver580.167.08**. A metadata-only end snapshot again shows that visible device with0MiB allocated and0% compute activity. The audit made zero GPU allocations and did not use any other user's job/device. Visibility alone is not a general proof of allocation entitlement; the historical report records the study's single-T4 allocation.

| Scope | Measured training hours | Measured validation hours | Interpretation |
|---|---|---|---|
|25 C20 fits |126.231610656|9.555842562|Sum of per-fit measured processing times;excludes unrecorded allocation/downtime/extraction |
| B100 cached head |0.060992387|0.001820982|CNN feature extraction excluded |
| C100 full CNN |23.964191181|1.629114685|Separate inference/calibration0.062891223h |
|72 Vi frozen heads |NOT SEPARATELY RECORDED|NOT SEPARATELY RECORDED|Combined training+validation sum0.490804938h;cached feature extraction excluded |

The paired100-epoch active-child process attempts sum to25.89373 wall hours (C-only25.81836h),not pure C training or GPU kernel time. Calendar duration includes gaps and can be longer. A complete historical global GPU-job-hours total is NOT RECORDED; adding overlapping categories or treating all CPU fitting time as GPU-hours would be misleading.

C100 mean sampled TRAINING compute activity is99.713245%,with peak allocated VRAM7.770030499GiB. B100 cached-head training averages21.4613% activity and peak allocated0.080301GiB. Memory fraction and compute activity are different quantities. Per-epoch averaging is not a time-integrated kernel-busy counter; maximum reserved VRAM and exact kernel compute-hours remain NOT RECORDED. This audit ran no utilization benchmark.

TRAINING_DURATION_AND_GPU_USAGE.csv retains every available run-level timing,epoch duration,actions/second,update count,effective batch and memory/activity value. Unknown extraction/resource fields remain explicit. C20/100-epoch repeats across additional seeds/folds would be expensive,but this audit does not select a future compute budget. Reproducibility and assessment design must precede any authorization.
""",[(provenance,'recorded GPU identity'),('26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_reports/PHASE1_GPU_INTEGRATION.md','allocated single-T4 report and historical planning estimate')])
    histories=csv_read(OUT/'06_dataset_specific/REASSEMBLE/EPOCH_HISTORIES.csv')
    diagnostics=[]
    for model,epochs in [('B_frozen100',[1,14,100]),('C_full_finetuned16',[1,47,100])]:
        for epoch in epochs:
            r=next(r for r in histories if r['experiment_id']=='REASSEMBLE_100E_SINGLE_FIT' and r['model']==model and int(r['epoch'])==epoch)
            diagnostics.append([model,epoch,float(r['training_loss']),float(r['validation_loss']),float(r['validation_AP']),float(r['validation_AUROC'])])
    body=table(['Model','Epoch','TRAINING weighted BCE','VALIDATION weighted BCE','VALIDATION AP','VALIDATION AUROC'],diagnostics)+"""

The recorded curves show a pronounced training/validation gap. Training loss approaches zero while validation weighted BCE rises substantially. This supports an overfitting/poor raw validation-probability diagnostic under these logged objectives,not an inference about every unseen cohort. AP measures ranking while BCE measures probability errors; the objectives need not improve together. The source selects by validation AP,so14/47 remain the evaluated selected checkpoints even though100 epochs executed. Epoch100 is not the reported best held-out model. Calibration is a later training-side operation;these epoch curves do not show a post-calibration held-out trajectory.

The pilot's observed held-out AP improvement therefore does not justify saying that longer training improved all generalization metrics. No per-epoch test curve was computed,as that would repeatedly inspect the assessment set. All points above come from saved histories;no training or inference was rerun.
"""
    report('06_dataset_specific/REASSEMBLE/TRAINING_GENERALIZATION_DIAGNOSTICS.md','Recorded training and validation gap',body)
    p=OUT/'06_dataset_specific/REASSEMBLE/FROZEN_VS_FINETUNED_100_EPOCHS.md'
    s=p.read_text();pos=s.find('\n## Evidence anchors')
    note='\n## Training/validation diagnostic\n\nThe logged curves show strong overfitting: at epoch100,training weighted BCE is0.005231 frozen and approximately1.4e-9 full CNN,while validation weighted BCE is17.493164 and26.145111. AP-based selection still uses epochs14/47. See [the exact selected/final-epoch table](TRAINING_GENERALIZATION_DIAGNOSTICS.md). A100-epoch budget is not evidence that the final epoch generalizes best.\n'
    if '## Training/validation diagnostic' not in s:p.write_text(s[:pos]+note+s[pos:] if pos>=0 else s+note)
    flush_evidence('SUPPLEMENTARY_REPORT_EVIDENCE_LEDGER.json')
    print('FINAL_REVIEW_TABLES_WRITTEN',flush=True)

if __name__=='__main__':main()
