"""Write cohort-qualified interpretation from reconciled saved evidence only."""
from pathlib import Path
import collections
import csv
import hashlib
import itertools
import json

ROOT=Path(__file__).resolve().parents[1]
csv.field_size_limit(256*1024**2)
def load(name):
    with (ROOT/name).open(newline='') as f:return list(csv.DictReader(f))
def save(name,rows):
    with (ROOT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def js(name,x):(ROOT/name).write_text(json.dumps(x,indent=2)+'\n')


def main():
    es=load('ALL_EVALUATION_COHORTS.csv');runs=load('ALL_TRAINING_RUN_COHORTS.csv')
    small=json.loads((ROOT/'SMALLER_COHORT_SUBSET_PROOF.json').read_text())
    cohorts={r['cohort_id']:r for r in load('COHORT_REGISTRY.csv')}
    canon=load('CANONICAL_ACTION_MANIFEST.csv');folds=load('ORIGINAL_OUTER_FOLDS.csv')
    S=small['smaller_cohort']['cohort_id'];L=small['larger_cohort']['cohort_id']
    def select(exp,model,N=753):
        matches=[e for e in es if e['experiment_id']==exp and e['model']==model and e['N']==str(N) and e['condition']=='clean' and e['evaluation_scope']=='OUTER HELD-OUT']
        assert matches,(exp,model,N)
        return matches[0]
    original='runs/reassemble/20260927T154732Z-section1'
    origf2='runs/reassemble/20260927T175336Z-section1b/stacking/oof.npz'
    labels=[('Original frozen visual (original recipe)',select(original,'rtdetr_perm00')),
        ('C20 full CNN outer refit, seed42',select('REASSEMBLE_PHASE1_C20','C_full_finetuned16')),
        ('Frozen CNN100 (M1)',select('CNN100_STATIC_SENSOR_F2','M1_frozen100')),
        ('Full CNN100 (M2)',select('CNN100_STATIC_SENSOR_F2','M2_finetuned100')),
        ('Static sensor (M3; original sensor scores)',select('CNN100_STATIC_SENSOR_F2','M3_sensor')),
        ('Original static F2, restricted to fold0',select(origf2,'F2_original')),
        ('Frozen CNN100 + F2 (M4)',select('CNN100_STATIC_SENSOR_F2','M4_F2_frozen')),
        ('Full CNN100 + F2 (M5)',select('CNN100_STATIC_SENSOR_F2','M5_F2_finetuned')),
        ('Frozen CNN100 + averaging (M6)',select('CNN100_STATIC_SENSOR_F2','M6_average_frozen')),
        ('Full CNN100 + averaging (M7)',select('CNN100_STATIC_SENSOR_F2','M7_average_finetuned'))]
    pooled=[('Original frozen visual',select(original,'rtdetr_perm00',4530)),
        ('Original static sensor',select(original,'sensor_statistics_perm00',4530)),
        ('Original static F2',select(origf2,'F2_original',4530)),
        ('C20 full CNN, seed42',select('REASSEMBLE_PHASE1_C20','C_full_finetuned16',4530))]
    save('KEY_MATCHED_PERFORMANCE.csv',[{'display_model':name,**e} for name,e in labels+pooled])
    matrix=[]
    def pair(name,a,b,caveat):
        same=(a['matched_comparison_group']==b['matched_comparison_group'] and a['matched_comparison_group']!='NOT PERMITTED')
        matrix.append({'comparison':name,'left_evaluation_id':a['evaluation_id'],'right_evaluation_id':b['evaluation_id'],
            'left_cohort_id':a['cohort_id'],'right_cohort_id':b['cohort_id'],'left_N':a['N'],'right_N':b['N'],
            'identical_held_out_actions_and_labels':same,'direct_descriptive_comparison_permitted':same,
            'classification':'MATCHED ACTIONS; PROTOCOL LIMITATIONS APPLY' if same else 'NOT DIRECTLY COMPARABLE',
            'reason':caveat})
    byname=dict(labels);bylabel=lambda prefix:next(e for n,e in labels if n.startswith(prefix))
    for (na,a),(nb,b) in itertools.combinations(labels,2):
        pair(na+' vs '+nb,a,b,'Same clean outer753 actions/labels. Different training pools, schedules, checkpoint rules and stacking recipes must remain explicit; descriptive comparison is not an isolated causal or confirmatory claim.')
    for (na,a),(nb,b) in itertools.combinations(pooled,2):
        pair(na+' pooled vs '+nb+' pooled',a,b,'Same4530 pooled outer actions and fold assignment. C20 and original branches use different T/V/C, schedules and seeds; preserve per-fold results.')
    for na,a in pooled:
        for nb,b in labels:pair(na+' pooled vs '+nb,a,b,'4530 pooled actions versus selected753-action outer fold: use corresponding fold0 predictions instead. Different prevalence and AP estimands.')
    inner=next(e for e in es if e['experiment_id']=='REASSEMBLE_PHASE1_C20' and e['N']=='920' and e['evaluation_scope']=='INNER-OOF ASSESSMENT')
    pair('Selected C20 inner fit3 vs CNN100 outer assessment',inner,bylabel('Full CNN100 (M2)'),
        '920 inner assessment actions are disjoint from753 outer test actions. Matching selected-fit training identity does not match evaluation identity.')
    save('COMPARABILITY_MATRIX.csv',matrix)
    js('COMPARISON_RULES.json',{'required':['same native recording_id::segment_id set','same native labels','same held-out assessment role','same observation/corruption condition'],
        'comparison_group_field':'matched_comparison_group','equal_sample_count_is_insufficient':True,
        'pooled_AP_and_fold_AP_are_distinct_estimands':True,'non_clean_groups_are_source_specific':True,
        'matching_actions_does_not_equal_matching_training_protocol':True,'duplicate_probability_vectors_are_not_independent_replicates':True,
        'new_significance_tests_or_winner_selection':False})
    save('SMALLER_COHORT_EXACT_ACTIONS.csv',[r for r in canon if r['outer_fold_zero_based']=='0'])
    save('SMALLER_COHORT_EXACT_RECORDINGS.csv',[{'recording_id':r} for r in sorted({r['recording_id'] for r in canon if r['outer_fold_zero_based']=='0'})])
    count_unknown=len(load('UNRECORDED_SEED_FIELDS.csv'))
    summary=json.loads((ROOT/'RECONCILIATION_SUMMARY.json').read_text())
    lines=['# Matched REASSEMBLE comparison and interpretation','',
        '**The753-action cohort is exactly original outer fold0 (legacy fold_01), a strict subset of the4,530-action cohort.** The intersection has753 actions,77 failures and26 recordings; no unmatched smaller-cohort action or label was found. The full cohort has509 failures and148 recordings. Native keys, timestamps, action names and labels were checked; legacy hashed sample IDs are retained as aliases.','',
        '## Exact outer partitions','',
        '| Zero-based outer fold | Legacy fold | Training N | Held-out N | Failures | Held-out recordings |','|---|---|---:|---:|---:|---:|']
    for f in folds:lines.append('| '+' | '.join(f[k] for k in ['outer_fold_zero_based','legacy_fold_name','train_N','held_out_N','held_out_failures','held_out_recording_N'])+' |')
    lines+=['','Every exact recording list is in [ORIGINAL_OUTER_FOLDS.csv](ORIGINAL_OUTER_FOLDS.csv); every exact action membership is in [COHORT_ACTION_MEMBERSHIP.csv](COHORT_ACTION_MEMBERSHIP.csv). All five outer test sets partition4,530 actions and148 recordings without overlap.','',
        '## Clean comparisons on the identical753 outer actions','',
        '| Model and recipe | AP | Evaluation ID |','|---|---:|---|']
    for name,e in labels:lines.append(f'| {name} | {float(e["AP_saved_probability_recomputation"]):.10f} | {e["evaluation_id"]} |')
    lines+=['',
        'These point estimates were recomputed from saved probabilities. All rows use the same native failure labels and clean held-out actions. They permit descriptive comparison on this fold; training and selection differences prevent treating every pair as a controlled intervention. The original sensor row and M3 are the same saved score vector, not independent sensor replications. M1/M2 also alias their standalone100-epoch visual outputs.','',
        '**Fine-tuning improves the100-epoch visual recipe from0.1937756 to0.2125845 on this fold.** That statement compares frozen100 with full100. The original frozen recipe scores0.2328051 on these same actions, so the result does not establish superiority over that original recipe. Full100 F2 improves its point AP over frozen100 F2 (0.3490942 versus0.3349774); the existing paired uncertainty interval crosses zero. No new significance test was performed. Original F2 scores0.3671552 on the same fold, but uses a different nested stacking protocol. Do not attribute differences across those recipes solely to CNN fine-tuning.','',
        '## Separate4,530-action pooled comparisons','',
        '| Model | Pooled AP | Evaluation ID |','|---|---:|---|']
    for name,e in pooled:lines.append(f'| {name} | {float(e["AP_saved_probability_recomputation"]):.10f} | {e["evaluation_id"]} |')
    lines+=['',
        '**Do not rank these pooled AP values against the753-action table.** Use the matched fold0 results above for a common-action comparison, or compare complete five-fold pooled outputs separately. The smaller subset has failure prevalence77/753; the larger cohort has509/4530. There is no100-epoch prediction bank for the other3,777 outer-assessment actions.','',
        '## What selected “fit3” means','',
        '| Run | Gradient train | Validation | Calibration | Assessment |','|---|---:|---:|---:|---|',
        '| C20 job_index2, inner fit3 | 1,752 | 419 | 686 | 920 inner actions |',
        '| Frozen100 / full100 selected job2 | 1,752 | 419 | 686 | 753 outer actions |',
        '| C20 outer refit job_index4 | 2,385 | 581 | 811 | Same753 outer actions |','',
        'The100-epoch pilot retained the selected C20 inner fit’s exact T/V/C identities and order, then changed assessment to the original outer fold0. Its reserved920 inner actions later form the single holdout fusion-fitting bank. That920-action bank is inside the original3,777 outer-training pool and is disjoint from the753 outer test actions. “Fit3” is an inner job name, not outer fold3. The saved partition seed and estimator RNG seed are separate fields; validation_split_seed for original job2 and its100-epoch copy is20261028.','',
        'The100-epoch selected-job JSON has a stale prediction_recordings list:28 inner-bank recordings, while actual predict indices, executed sample IDs and outer_E_recordings identify26 outer test recordings. The two lists are disjoint. The original JSON remains unchanged; [METADATA_CONFLICTS.csv](METADATA_CONFLICTS.csv) gives the exact differing identities.','',
        '## Coverage and reviewer workflow','',
        f'This supplement reconciles {summary["fit_records_reconciled"]:,} saved fit records across {summary["experiment_records"]} training groups, plus {summary["evaluation_records"]:,} saved evaluation records, including inference-only and robustness workflows. It does not assert that every fit is a distinct independent model: reused sensor fits, repeated seed families and identical saved scores are explicitly retained. Zero assessment-identity rows remain unresolved in the completed audit inventory. This is a cohort reconciliation, not a rerun of the comprehensive audit.','',
        '1. Start with [EXPERIMENT_COHORT_SPLIT_SEED_SUMMARY.csv](EXPERIMENT_COHORT_SPLIT_SEED_SUMMARY.csv) and [ALL_PREDICTION_WORKFLOW_SUMMARY.csv](ALL_PREDICTION_WORKFLOW_SUMMARY.csv).',
        '2. Find a fit in [ALL_TRAINING_RUN_COHORTS.csv](ALL_TRAINING_RUN_COHORTS.csv); resolve each role cohort through [COHORT_REGISTRY.csv](COHORT_REGISTRY.csv) and [COHORT_ACTION_MEMBERSHIP.csv](COHORT_ACTION_MEMBERSHIP.csv).',
        '3. Find an evaluation in [ALL_EVALUATION_COHORTS.csv](ALL_EVALUATION_COHORTS.csv). Direct descriptive comparisons require the same permitted matched_comparison_group. Non-clean observations are source-specific: a shared corruption name alone does not prove equal corrupted inputs.',
        '4. Consult [COMPARABILITY_MATRIX.csv](COMPARABILITY_MATRIX.csv) for the explicit key comparisons, and [MATCHED_COMPARISON_GROUPS.csv](MATCHED_COMPARISON_GROUPS.csv) for lossless grouping of every evaluation.',
        '5. Recalculate from [ALL_CLEAN_HELD_OUT_PREDICTIONS.csv](ALL_CLEAN_HELD_OUT_PREDICTIONS.csv), joined by evaluation_id to the evaluation table and by native_key to the action manifest. Scores are exported without threshold changes. [IDENTICAL_PREDICTION_ALIASES.csv](IDENTICAL_PREDICTION_ALIASES.csv) identifies repeated evidence.',
        '6. Inspect [SOURCE_PROVENANCE.csv](SOURCE_PROVENANCE.csv) for original source paths and SHA256 hashes. Larger source probability banks remain external; the clean held-out score rows used here are included.','',
        f'Exact fit-level estimator seed fields unresolved by this adapter: {count_unknown}. Nominal seed families, split/role seeds, validation seeds, estimator random_state and reused-fit provenance remain separate. A pooled outer result may have a different actual training seed per fold; per-run seed records govern. A seed-mean row is an ensemble, not one extra seed. Original audit fields are preserved alongside recovered values.']
    (ROOT/'MATCHED_COMPARISON_SUMMARY.md').write_text('\n'.join(lines)+'\n')
    (ROOT/'MISSING_EVIDENCE.md').write_text('''# Missing evidence and limits of this reconciliation

All6,894 fit records in the completed audit now have recoverable assessment identities. This statement is limited to that inventory and the saved probability workflows enumerated here; it is not a census of deleted or never-saved experiments. Exact code versions cannot be inferred where historical provenance is absent. The original audit missing-evidence report remains applicable.

- No100-epoch predictions exist for the other four outer folds or other planned seeds. The753-action pilot cannot establish a4,530-action pooled result or seed stability.
- No completed C20 F2 finalization or deferred seed7/2026 fits are invented. C20 visual outputs cover five outer folds at seed42 only.
- Some saved prediction-bank seed fields describe nominal families or ensembles; use the exact fit registry. Reused sensor results are not independent fits. Missing/irrelevant role fields stay NOT RECORDED; do not interpret them as zero-size partitions.
- Non-clean robustness banks remain identified by original source hashes and paths. Clean per-action probabilities and all cohort memberships are included. Identical corruption names from different banks do not establish identical corrupted realizations; cross-source robustness matching is not certified.
- The stale28-recording prediction_recordings field is preserved and flagged. Actual753-row executed predictions identify26 outer recordings.
- A matched held-out set does not remove training/validation/calibration/OOF/checkpoint differences or historical test exposure. No untouched confirmatory set or new paired confidence interval is created by this export.
- Checkpoints, raw recordings and feature caches remain external by the package size policy. Their manifest identities permit locating originals; independent weight-level inference requires access to those artifacts.

See [MISSING_IDENTITY_EVIDENCE.csv](MISSING_IDENTITY_EVIDENCE.csv), [UNRECORDED_SEED_FIELDS.csv](UNRECORDED_SEED_FIELDS.csv), [METADATA_CONFLICTS.csv](METADATA_CONFLICTS.csv) and the preserved original audit for row-level qualifications. No model was fitted, no inference was run and no existing experiment was modified.
''')
    print(json.dumps({'key_performance_rows':len(labels)+len(pooled),'explicit_comparisons':len(matrix),'unknown_model_seed_rows':count_unknown}))

if __name__=='__main__':main()
