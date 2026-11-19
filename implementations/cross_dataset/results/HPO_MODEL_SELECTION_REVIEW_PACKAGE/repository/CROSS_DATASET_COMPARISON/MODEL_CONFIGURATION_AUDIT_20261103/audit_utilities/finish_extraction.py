"""Ingest remaining aggregate tables and literal checkpoint configuration metadata."""
from pathlib import Path
import json
import math
import pickletools

from audit_common import Audit,OUT,REPO,NR,DEFAULT,read,evidence,digest,rel,write,csv_read,flush_evidence
from static_optimizer_metadata import optimizer_literals


def main():
    state=read(OUT/'provenance/FINAL_AUDIT_STATE.json');a=Audit()
    for key in ['runs','results','histories','checks','parameters']:setattr(a,key,state[key])
    for dataset,root in [('MSM',Path('MSM')),('HANDOVER',Path('HANDOVER/experiments/common_support_v2'))]:
        folder=root/'06_evaluation_results/metrics'
        for name in ['pooled_heldout_metrics.csv','heldout_subgroup_metrics.csv','clean_seed_summary.csv',
                     'paired_seed_differences.csv','paired_group_bootstrap_95ci.csv','training_diagnostic_AP.csv',
                     'training_loss_curves.csv']:
            path=folder/name
            if not (REPO/path).exists():continue
            for i,row in enumerate(csv_read(path)):
                exclude={'seed','fold','update','groups','examples','positive','valid_bootstrap_replicates'}
                values={}
                for k,v in row.items():
                    if k in exclude:continue
                    try:value=float(v)
                    except (ValueError,TypeError):continue
                    if math.isfinite(value):values[k]=value
                stage='TRAINING IN-SAMPLE' if name=='training_diagnostic_AP.csv' else 'TRAINING' if name=='training_loss_curves.csv' else 'PAIRED BOOTSTRAP INTERVAL' if 'bootstrap' in name else 'PAIRED DIFFERENCE' if 'differences' in name else 'HELD-OUT SUBGROUP' if 'subgroup' in name else 'HELD-OUT POOLED SEED SUMMARY' if 'summary' in name else 'HELD-OUT POOLED'
                a.result(dataset,'EXTERNAL_P_'+row.get('protocol','recorded'),row.get('model',row.get('comparison',NR)),
                    values,path,stage=stage,seed=row.get('seed','three-seed descriptive aggregate'),fold=row.get('fold','pooled'),
                    held_out_N=row.get('examples',NR),positive_count=row.get('positive',NR),threshold=.5,
                    protocol=row.get('protocol',NR),corruption=row.get('corruption','clean'),
                    subgroup_type=row.get('subgroup_type',NR),subgroup=row.get('subgroup',NR),
                    csv_row=i+2,update=row.get('update',NR),
                    bootstrap_method='paired cluster percentile' if 'bootstrap' in name else NR,
                    bootstrap_unit=row.get('grouping',NR),bootstrap_draws=row.get('valid_bootstrap_replicates','NOT AVAILABLE'),
                    confidence_level=.95 if 'bootstrap' in name else 'NOT AVAILABLE',n_groups=row.get('groups',NR))
    # Additional JSON-retained learned heads, distinct from the neural gate family.
    path=Path('00_experiments/adaptive_fusion_robustness/results/run_01/fusion_fits/fold_01/components.json')
    components=read(path)
    for name,item in components.items():
        cfg={'seed':42,'outer_fold':0,'C':item['C'],'solver':item['solver'],'max_iter':item['max_iter'],
             'tolerance':item['tol'],'class_weighting':item['class_weight'],'threshold':item['threshold'],
             'feature_dimension':len(item['coefficient']),'trainable_parameters':len(item['coefficient'])+1,
             'executed_epochs':'NOT APPLICABLE','normalization':item['normalizer'],
             'augmentation':'three variants per parent, weights0.5/0.25/0.25; source-defined training seed50101',
             'selection_metric':'fixed settings; no outer labels used',
             'penalty':DEFAULT,'fused_calibrator':None}
        a.run('REASSEMBLE','ADAPTIVE_FUSION_ROBUSTNESS_PILOT',name,rel(path)+'::'+name,path,cfg,
            training_status='COMPLETE',evidence_status='VERIFIED',checkpoint_path=rel(path),
            train_N=3777,assessment_N=753,entry_point='00_experiments/adaptive_fusion_robustness/run_experiment.py',
            configuration_function='code/quality_fusion.py::fit_all/design')
    recovered=[]
    for run in a.runs:
        if run['experiment_id'] not in ['REASSEMBLE_100E_SINGLE_FIT','REASSEMBLE_PHASE1_C20','REASSEMBLE_PHASE1_ORIGINAL_B']:continue
        pointer=run.get('last_checkpoint_pointer')
        if not pointer:continue
        p=REPO/pointer
        value=read(p);checkpoint=p.parent/value['slot']
        assert digest(checkpoint)==value['sha256']
        meta=optimizer_literals(evidence(checkpoint,'static optimizer literal inspection; no pickle execution'))
        assert meta.get('betas')==[.9,.999] and meta.get('eps')==1e-8
        cfg=run['effective_configuration'];cfg.update(betas=meta['betas'],epsilon=meta['eps'],
            optimizer_checkpoint_literal_parameters=meta,optimizer_parameters_evidence=rel(checkpoint)+'::optimizer.param_groups (static pickle opcodes only)')
        recovered.append({'run_id':run['run_id'],'checkpoint':rel(checkpoint),'values':meta,'unsafe_deserialization':False})
    # Preserve full provenance after concrete checkpoint enrichment.
    a.parameters=[]
    for run in a.runs:
        for key,value in run['effective_configuration'].items():
            a.parameters.append({'run_id':run['run_id'],'dataset':run['dataset'],'model':run['model'],'parameter':key,
                'effective_value':value,'source_file':run['configuration_source'],
                'source_function_or_key':run.get('configuration_function',NR),
                'additional_checkpoint_source':run.get('last_checkpoint_path',run.get('checkpoint_path',NR)),
                'status':'NOT RECORDED' if value==NR else 'PARTIALLY VERIFIED' if value==DEFAULT else 'VERIFIED'})
    write(OUT/'provenance/STATIC_OPTIMIZER_METADATA_VERIFICATION.json',recovered)
    a.results=list({json.dumps(r,sort_keys=True):r for r in a.results}.values())
    a.save();flush_evidence('FINAL_EXTRACTION_EVIDENCE_LEDGER.json')
    write(OUT/'provenance/FINAL_AUDIT_STATE_02.json',
          {key:getattr(a,key) for key in ['runs','results','histories','checks','parameters']})
    print('FINAL_STATE_READY',len(a.runs),'optimizer states verified',len(recovered),flush=True)


if __name__=='__main__':main()
