"""Add remaining saved evidence, enrich from CPU metadata and save final tables."""
from pathlib import Path
import collections
import json
import numpy as np
import pandas as pd

from audit_common import Audit,OUT,REPO,NR,DEFAULT,read,evidence,digest,rel,write,csv_read,flush_evidence
from run_audit import history_metrics
from metrics_check import metrics
import supplementary_fits


def pooled_external(audit):
    root=Path('MSM');complete=read(root/'06_evaluation_results/P_EVALUATION_COMPLETE.json')
    banks=collections.defaultdict(list)
    for case in complete['cases']:
        if case['protocol']!='primary__group_id':continue
        table=pd.read_csv(evidence(case['predictions']),compression='gzip')
        clean=table.loc[(table.role=='test')&(table.corruption=='clean')]
        for name,group in clean.groupby('model'):
            banks[case['seed'],name].append(group[['sample_id','target','probability','group_id']])
    for (seed,model),parts in banks.items():
        frame=pd.concat(parts,ignore_index=True)
        assert len(frame)==1895 and not frame.sample_id.duplicated().any()
        score=metrics(frame.target,frame.probability)
        audit.result('MSM','EXTERNAL_P_primary__group_id',model,score,
            root/'06_evaluation_results/P_EVALUATION_COMPLETE.json',stage='HELD-OUT POOLED',seed=seed,fold='pooled3',
            held_out_N=1895,positive_count=int(frame.target.sum()),negative_count=int((frame.target==0).sum()),
            threshold=.5,protocol='primary__group_id',metric_origin='AUDIT_RECOMPUTED_FROM_EXISTING_PREDICTIONS',
            evaluation_script='audit_utilities/metrics_check.py',n_groups=frame.group_id.nunique())
    # Published across-seed means and robustness summaries are separate aggregates.
    for name in ['comparison_tables.csv','paired_comparison_tables.csv','robustness_comparison_tables.csv']:
        path=Path('CROSS_DATASET_COMPARISON')/name
        for index,row in enumerate(csv_read(path)):
            values={k:float(v) for k,v in row.items() if k in ['AP_mean','AP_seed_std','AP_min','AP_max','AP_difference','AP','absolute_AP_degradation','relative_AP_degradation_percent'] and v}
            audit.result(row['dataset'],'EXTERNAL_P_'+row.get('protocol','recorded'),row.get('model',row.get('comparison',NR)),
                values,path,stage='PAIRED DIFFERENCE' if 'comparison' in row else 'HELD-OUT POOLED SEED SUMMARY',
                seed=row.get('seed','three-seed descriptive aggregate'),fold='pooled',
                csv_row=index+2,protocol=row.get('protocol',NR),corruption=row.get('corruption','clean'))


def enrich(audit):
    inspected={}
    for line in (OUT/'provenance/CHECKPOINT_INSPECTION.jsonl').open():
        row=json.loads(line);inspected[row['path']]=row
    for run in audit.runs:
        cfg=run['effective_configuration']
        if run['experiment_id'] in ['REASSEMBLE_100E_SINGLE_FIT','REASSEMBLE_PHASE1_C20','REASSEMBLE_PHASE1_ORIGINAL_B']:
            full=run['model']=='C_full_finetuned16'
            cfg.update(trainable_parameters=11314913 if full else 114945,
                       frozen_parameters=0 if full else 11190112,
                       total_parameters=11314913 if full else 11305057,
                       parameter_count_scope='pipeline parameters; full CNN promotes9856 FrozenBN affine buffers to parameters')
        path=run.get('last_checkpoint_path',run.get('checkpoint_path',NR))
        row=inspected.get(path)
        visited=set()
        while row and row.get('hash_alias_of') and row['path'] not in visited:
            visited.add(row['path']);row=inspected.get(row['hash_alias_of'])
        meta=row['metadata'] if row else {}
        groups=meta.get('optimizer_param_groups')
        if groups:
            cfg['optimizer_checkpoint_parameter_groups']=groups
            cfg['betas']=groups[0].get('betas',DEFAULT)
            cfg['epsilon']=groups[0].get('eps',DEFAULT)
            cfg['optimizer_parameters_evidence']='safe CPU checkpoint optimizer.param_groups'
        if 'scheduler_state' in meta:cfg['saved_scheduler_state']=meta['scheduler_state']
    # Rebuild parameter provenance after concrete checkpoint enrichments.
    audit.parameters=[]
    for run in audit.runs:
        for key,value in run['effective_configuration'].items():
            audit.parameters.append({'run_id':run['run_id'],'dataset':run['dataset'],'model':run['model'],
                'parameter':key,'effective_value':value,'source_file':run['configuration_source'],
                'source_function_or_key':run.get('configuration_function',NR),
                'additional_checkpoint_source':run.get('last_checkpoint_path',run.get('checkpoint_path',NR)),
                'status':'NOT RECORDED' if value==NR else 'PARTIALLY VERIFIED' if value==DEFAULT else 'VERIFIED'})


def main():
    old=read(OUT/'provenance/FULL_AUDIT_STATE.json')
    audit=Audit()
    for field in ['runs','results','histories','checks','parameters']:setattr(audit,field,old[field])
    initial_histories=len(audit.histories)
    supplementary_fits.extract(audit)
    # Add new histories once; original ones are already in the long metric table.
    original_histories=audit.histories
    audit.histories=original_histories[initial_histories:]
    history_metrics(audit)
    audit.histories=original_histories
    pooled_external(audit)
    enrich(audit)
    # Exact duplicate rows are aliases, never extra evaluations.
    audit.results=list({json.dumps(r,sort_keys=True):r for r in audit.results}.values())
    ids=[r['run_id'] for r in audit.runs]
    assert len(ids)==len(set(ids)),'DUPLICATE_LOGICAL_RUN_IDS'
    assert all(check.get('passed',True) for check in audit.checks),'FAILED_INDEPENDENT_CHECK'
    audit.save()
    flush_evidence('CONSOLIDATION_EVIDENCE_LEDGER.json')
    write(OUT/'provenance/FINAL_AUDIT_STATE.json',
          {field:getattr(audit,field) for field in ['runs','results','histories','checks','parameters']})
    counts=collections.Counter((r['dataset'],r['training_status']) for r in audit.runs)
    print('FINAL_DATASET_FIT_COUNTS',dict((str(k),v) for k,v in counts.items()),flush=True)


if __name__=='__main__':main()
