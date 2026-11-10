"""Audit-only IO, provenance and strict separation of fits and evaluations."""
from pathlib import Path
import csv
import datetime as dt
import hashlib
import json
import math

csv.field_size_limit(256*1024**2)  # Complete provenance lists can exceed the stdlib131072-byte default.

from discover import OUT, REPO

NR = 'NOT RECORDED'
DEFAULT = 'FRAMEWORK DEFAULT — NOT VERIFIED'
USED = {}


def rel(path):
    path = Path(path)
    if not path.is_absolute(): return str(path)
    try: return str(path.relative_to(REPO))
    except ValueError: return str(path)


def resolve(path):
    p = Path(path)
    return p if p.is_absolute() else REPO/p


def digest(path):
    p = resolve(path)
    h = hashlib.sha256()
    with p.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8*1024**2), b''): h.update(chunk)
    return h.hexdigest()


def evidence(path, role='source'):
    p = resolve(path)
    name = rel(p)
    if name not in USED:
        stat = p.stat()
        USED[name] = {'path': name, 'bytes': stat.st_size, 'mtime_ns': stat.st_mtime_ns,
                      'sha256': digest(p), 'role': role}
    return p


def read(path):
    p=resolve(path)
    if not p.exists() and p.suffix=='.json' and p.with_suffix('.json.gz').exists():
        import gzip
        with gzip.open(evidence(p.with_suffix('.json.gz'),'compressed task-owned audit working state'),'rt') as stream:
            return json.load(stream)
    return json.loads(evidence(path, 'structured experiment evidence').read_text())


def text(path):
    return evidence(path, 'implementation or report').read_text(errors='replace')


def write(path, value):
    p = resolve(path)
    assert p.resolve().is_relative_to(OUT.resolve()), 'AUDIT_WRITE_OUTSIDE_NEW_FOLDER'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def csv_write(path, rows, fields=None):
    p = resolve(path)
    assert p.resolve().is_relative_to(OUT.resolve()), 'AUDIT_WRITE_OUTSIDE_NEW_FOLDER'
    if fields is None:
        fields = list(dict.fromkeys(key for row in rows for key in row))
    with p.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields or ['no_records'])
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else v
                             for k, v in row.items()})


def csv_read(path):
    with evidence(path, 'original metric table').open(newline='') as stream:
        return list(csv.DictReader(stream))


def flush_evidence(name):
    write(OUT/'provenance'/name, list(USED.values()))


CONFIG_FIELDS = ['seed','dataset_version','split_identifier','outer_fold','inner_fold',
    'class_weighting','loss','threshold','selection_metric','optimizer','learning_rate',
    'backbone_learning_rate','head_learning_rate','weight_decay','momentum','betas','epsilon',
    'gradient_clipping','batch_size','microbatch_size','gradient_accumulation','effective_batch_size',
    'precision','scheduler','scheduler_parameters','warmup','minimum_learning_rate',
    'optimizer_updates','backbone','feature_dimension','hidden_dimensions','dropout',
    'normalization','layers','trainable_layers','max_configured_epochs','executed_epochs',
    'early_stopping','early_stopping_patience','minimum_improvement','checkpoint_selection',
    'selected_epoch','augmentation','sampling','workers','initialization','C','penalty',
    'solver','max_iter','tolerance','max_leaf_nodes','max_depth','min_samples_leaf',
    'l2_regularization','trainable_parameters','total_parameters','frozen_parameters']


class Audit:
    def __init__(self):
        self.runs=[];self.results=[];self.parameters=[];self.histories=[];self.checks=[]

    def run(self, dataset, experiment, model, run_id, source, config=None, **meta):
        config = config or {}
        record = {'run_id': run_id, 'dataset': dataset, 'experiment_id': experiment,
                  'model': model, 'configuration_source': rel(source),
                  'evidence_status': 'PARTIALLY VERIFIED', **meta,
                  'effective_configuration': {k: config.get(k, NR) for k in CONFIG_FIELDS}|config}
        self.runs.append(record)
        for key,value in record['effective_configuration'].items():
            self.parameters.append({'run_id':run_id,'dataset':dataset,'model':model,
                'parameter':key,'effective_value':value,'source_file':rel(source),
                'source_function_or_key':meta.get('configuration_function', NR),
                'status':'NOT RECORDED' if value==NR else 'PARTIALLY VERIFIED' if value==DEFAULT else 'VERIFIED'})
        return record

    def result(self, dataset, experiment, model, metrics, source, *, stage,
               seed=NR, fold=NR, run_id=NR, **meta):
        record={'dataset':dataset,'experiment_id':experiment,'model':model,
                'run_id':run_id,'seed':seed,'fold':fold,'evaluation_scope':stage,
                'metric_output_file':rel(source),'evidence_status':'VERIFIED',**meta}
        for key,value in metrics.items():
            if isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value):
                record[key]=value
        self.results.append(record)
        return record

    def save(self):
        write(OUT/'03_hyperparameter_configuration/EFFECTIVE_CONFIGURATIONS.json',self.runs)
        flattened=[{k:v for k,v in r.items() if k!='effective_configuration'}|r['effective_configuration'] for r in self.runs]
        csv_write(OUT/'03_hyperparameter_configuration/ALL_RUN_HYPERPARAMETERS.csv',flattened)
        csv_write(OUT/'03_hyperparameter_configuration/PARAMETER_PROVENANCE.csv',self.parameters)
        csv_write(OUT/'04_training_and_checkpoints/TRAINING_RUN_INVENTORY.csv',flattened)
        aggregate=[row for row in self.results if 'epoch' not in row]
        csv_write(OUT/'05_results/ALL_MODEL_RESULTS_SUMMARY.csv',aggregate)
        nonmetrics={'dataset','experiment_id','model','run_id','seed','fold','evaluation_scope',
                    'metric_output_file','evidence_status','held_out_N','train_N','validation_N',
                    'positive_count','negative_count','checkpoint_path','prediction_file',
                    'evaluation_script','split_identifier','threshold','corruption','protocol',
                    'bootstrap_method','bootstrap_unit','bootstrap_draws','confidence_level',
                    'model_status','metric_definition','n_groups','class_definition',
                    'epoch','metric_path','metric_origin','csv_row','label_permutation',
                    'permutation','source_role_note','bootstrap_interval','subgroup_type',
                    'subgroup','update'}
        long=[]
        for result in self.results:
            meta={k:v for k,v in result.items() if k in nonmetrics}
            for key,value in result.items():
                if key not in nonmetrics and isinstance(value,(int,float)):
                    long.append({**meta,'metric':key,'metric_value':value})
        csv_write(OUT/'05_results/ALL_RECORDED_METRICS_LONG.csv',long)
        provenance=[{k:v for k,v in row.items() if k in nonmetrics and k!='epoch'} for row in self.results]
        provenance=list({json.dumps(row,sort_keys=True):row for row in provenance}.values())
        csv_write(OUT/'05_results/RESULTS_PROVENANCE.csv',provenance)
        for dataset in ['REASSEMBLE','MSM','HANDOVER','VIFAILBACK']:
            csv_write(OUT/f'06_dataset_specific/{dataset}/COMPLETE_RESULTS.csv',
                      [r for r in aggregate if r['dataset']==dataset])
        csv_write(OUT/'06_dataset_specific/REASSEMBLE/EPOCH_HISTORIES.csv',
                  [r for r in self.histories if r['dataset']=='REASSEMBLE'])
        csv_write(OUT/'04_training_and_checkpoints/ALL_DATASET_EPOCH_HISTORIES.csv',self.histories)
        write(OUT/'provenance/EXTRACTION_CHECKS.json',self.checks)
        summary={'run_records':len(self.runs),'result_rows':len(self.results),
                 'numeric_metric_records':len(long),'epoch_history_rows':len(self.histories),
                 'parameter_provenance_records':len(self.parameters),
                 'completed_training_records':sum(r.get('training_status')=='COMPLETE' for r in self.runs)}
        write(OUT/'provenance/EXTRACTION_SUMMARY.json',summary)
        print(json.dumps(summary),flush=True)
