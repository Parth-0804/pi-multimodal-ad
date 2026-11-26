"""Read-only extraction entry point. Never imports an execution/training main."""
import argparse
import json
import math
import traceback

from audit_common import Audit,OUT,read,write,flush_evidence


def history_metrics(audit):
    train_names={'training_loss','train_loss','T_weighted_BCE','training_minibatch_loss_mean',
                 'training_scaled_smooth_l1','training_loss_scaled_mse','train_total_loss',
                 'train_detection_loss','train_regression_loss'}
    validation_names={'validation_loss','validation_AP','validation_AUROC','val_loss','val_ap',
        'V_weighted_BCE_same_T_positive_weight','V_macro_AP','V_AP_failure','V_AP_success','V_AUROC',
        'validation_scaled_smooth_l1','validation_loss_scaled_mse','validation_total_loss',
        'validation_detection_loss','validation_regression_loss'}
    for row in audit.histories:
        for stage,keys in [('TRAINING',train_names),('VALIDATION',validation_names)]:
            values={k:float(row[k]) for k in keys if k in row and row[k] is not None
                    and isinstance(row[k],(int,float)) and math.isfinite(row[k])}
            if values:
                audit.result(row['dataset'],row['experiment_id'],row['model'],values,row['history_source'],
                    stage=stage,seed=row.get('seed','NOT RECORDED'),fold=row.get('outer_fold','NOT RECORDED'),
                    run_id=row['run_id'],epoch=row.get('epoch','NOT RECORDED'))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--historical-only',action='store_true')
    args=parser.parse_args()
    audit=Audit()
    if args.historical_only:
        state=read(OUT/'provenance/PRIMARY_AUDIT_STATE.json')
        for field in ['runs','results','histories','checks','parameters']:setattr(audit,field,state[field])
    try:
        modules=[]
        if not args.historical_only:
            import primary_reassemble,external_datasets,vifailback_audit
            modules=[primary_reassemble,external_datasets,vifailback_audit]
        import historical_audit,phm_audit
        modules.extend([historical_audit,phm_audit])
        for module in modules:
            print('EXTRACTING',module.__name__,flush=True)
            write(OUT/'provenance/EXTRACTION_STATUS.json',{'stage':module.__name__,'status':'RUNNING'})
            module.extract(audit)
            flush_evidence(f'EVIDENCE_LEDGER_{module.__name__}.json')
            print('EXTRACTED',module.__name__,'runs',len(audit.runs),'results',len(audit.results),flush=True)
            if module.__name__=='vifailback_audit':
                write(OUT/'provenance/PRIMARY_AUDIT_STATE.json',
                      {field:getattr(audit,field) for field in ['runs','results','histories','checks','parameters']})
        history_metrics(audit)
        audit.save()
        flush_evidence('EXTRACTION_EVIDENCE_LEDGER.json')
        write(OUT/'provenance/FULL_AUDIT_STATE.json',
              {field:getattr(audit,field) for field in ['runs','results','histories','checks','parameters']})
        write(OUT/'provenance/EXTRACTION_STATUS.json',{'stage':'EXTRACTION_COMPLETE','status':'COMPLETE'})
    except Exception as exc:
        write(OUT/'provenance/EXTRACTION_STATUS.json',{'stage':'EXTRACTION_FAILED','status':'FAILED',
              'error':repr(exc),'traceback':traceback.format_exc()})
        raise


if __name__=='__main__':main()
