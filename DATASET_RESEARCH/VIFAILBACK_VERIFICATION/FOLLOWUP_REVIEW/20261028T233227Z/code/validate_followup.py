"""Independent scientific-artifact assertions plus tiny synthetic split checks."""
from pathlib import Path
from collections import Counter
import ast
import copy
import csv
import hashlib
import json
import subprocess
import sys
from audit_sensors_and_splits import build_splits

RUN = Path(__file__).resolve().parents[1]
SOURCE = RUN.parent.parent
REPO = SOURCE.parents[1]
checks = Counter()


def read(path):
    return json.loads(path.read_text())


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def assert_true(value, name):
    assert value, name
    checks[name] += 1


if __name__ == '__main__':
    # Real evidence below is validated in place, never copied into test fixtures.
    lock = read(RUN / '00_LOCKED_REVIEW/REVIEW_LOCK.json')
    assert_true(sha(SOURCE / 'VIFAILBACK_INDEPENDENT_BLINDED_VISUAL_REVIEW.md') == lock['source_sha256'], 'original review immutable')
    assert_true(sha(RUN / '00_LOCKED_REVIEW/INDEPENDENT_REVIEW_LOCKED.md') == lock['source_sha256'], 'locked copy byte identical')
    assert_true(next(row for row in lock['predictions'] if row['blind_id'] == 'B02')['locked_prediction'] == 'uncertain', 'B02 abstention preserved')
    unblind = read(RUN / '01_UNBLINDING/UNBLINDING_VERIFICATION.json')
    assert_true(unblind['comparison_counts'] == {'AGREEMENT': 19, 'UNCERTAIN_RETAINED': 1}, 'unblinding counts exact')
    for row in read(SOURCE / 'OUTPUT_MANIFEST.json'):
        path = SOURCE / row['path']
        assert_true(path.stat().st_size == row['bytes'] and sha(path) == row['sha256'], 'historical verification evidence unchanged')
    export = SOURCE / 'PORTABLE_REVIEW_EXPORTS/20261028T222841Z'
    for row in read(export / 'EXPORT_PROVENANCE.json')['packages']:
        assert_true(sha(export / row['path']) == row['sha256'], 'preserved export archive unchanged')
    original_checks = read(RUN / '03_SENSOR_QUALITY/ADDITIONAL_ORIGINAL_SENSOR_CHECKS.json')
    for row in original_checks:
        assert_true(row['status'] == 'VERIFIED', 'targeted original source check complete')
        for stream in row['checks']:
            assert_true(stream['max_abs_conversion_error'] == 0, 'targeted source arrays exactly match')
    inventory = read(RUN / 'provenance/SENSOR_TABLE_INVENTORY.json')
    assert_true(len(inventory) == 5202, 'complete numerical acquisition count')
    for row in inventory:
        assert_true(row['status'] != 'BLOCKED' and sha(SOURCE / row['local_path']) == row['expected_sha256'], 'actual numeric source hash')
    full = read(RUN / '03_SENSOR_QUALITY/FULL_SENSOR_AND_COHORT_AUDIT.json')
    assert_true(full['actual_tables_valid'] == 5202 and full['actual_sensor_rows'] == 1297146, 'actual full sensor row and table count')
    assert_true(full['nonfinite_values'] == 0 and len(full['constant_position_episode_indices']) == 173, 'finite is distinct from scientifically usable')
    base = RUN / '02_COHORT_AND_SPLITS/V2_CONSERVATIVE_CORE'
    all_rows = list(csv.DictReader((base / 'CORE_ELIGIBILITY_AND_EXCLUSIONS_V2.csv').open()))
    core_rows = list(csv.DictReader((base / 'ELIGIBLE_CORE_EPISODES_V2.csv').open()))
    by_id = {int(row['episode_index']): row for row in all_rows}
    core = {int(row['episode_index']): row for row in core_rows}
    assert_true(len(all_rows) == len(by_id) == 5202 and len(core) == 4384, 'V2 unique cohort counts')
    assert_true(Counter(row['native_outcome'] for row in core.values()) == {'failure': 3755, 'success': 629}, 'V2 class counts')
    assert_true(sum(row['core_eligible_v2'] != 'True' for row in all_rows) == 818, 'all excluded episodes accounted')
    assert_true(all(not row['exclusion_reasons_v2'] and row['core_eligible_v2'] == 'True' for row in core.values()), 'every included row passes documented flags')
    assert_true(all(int(row['canonical_task_id']) != 55 for row in core.values()), 'unresolved coordinate group quarantined')
    assert_true(1827 in core, 'B02 native episode retained despite reviewer abstention')
    assert_true(4570 not in core and 'HUMAN_INTERVENTION' in by_id[4570]['exclusion_reasons_v2'], 'B20 human confound exclusion recorded')
    assert_true(by_id[3034]['primary_acquisition_cohort_eligible_v1'] == 'True' and by_id[3034]['core_eligible_v2'] == 'False', 'regression V1 finite spike admission detected and V2 quarantined')
    assert_true(by_id[775]['core_eligible_v2'] == 'True', 'clean pilot control retained')
    assert_true(1294 not in core and 'CONSTANT_POSITION' in by_id[1294]['exclusion_reasons_v2'], 'confirmed constant source remains quarantined')

    plan = read(base / 'OUTER_INNER_SPLITS_V2.json')['partitions']
    fits = read(base / 'BASE_FIT_T_V_C_ASSESSMENT_V2.json')['fits']
    assert_true(len(plan) == 20 and len(fits) == 25, 'complete planned outer inner base fits')
    all_outer = set()
    task = lambda values: {int(core[eid]['canonical_task_id']) for eid in values}
    for outer in range(5):
        partitions = [row for row in plan if row['outer_fold'] == outer]
        assessment = set(partitions[0]['test_episode_indices'])
        assert_true(not all_outer & assessment, 'outer assessment episodes unique')
        all_outer |= assessment
        development = set(core) - assessment
        oof = set()
        for row in partitions:
            groups = [set(row[name + '_episode_indices']) for name in ('train', 'validation', 'test')]
            assert_true(set.union(*groups) == set(core), 'triple covers exact common cohort')
            assert_true(all(not a & b and not task(a) & task(b) for i, a in enumerate(groups) for b in groups[i + 1:]), 'episode and canonical task disjoint triple')
            assert_true(all({core[eid]['label'] for eid in values} == {'0', '1'} for values in groups), 'each role has both outcomes')
        for fit in [row for row in fits if row['outer_fold'] == outer]:
            roles = [set(fit[name + '_episode_indices']) for name in ('T', 'V', 'C', 'assessment')]
            assert_true(all(not a & b and not task(a) & task(b) for i, a in enumerate(roles) for b in roles[i + 1:]), 'base fit preprocessing selection calibration assessment disjoint')
            assert_true(all({core[eid]['label'] for eid in values} == {'0', '1'} for values in roles), 'base fit class support')
            if fit['role'].startswith('inner_oof'):
                assert_true(not set.union(*roles) & assessment, 'outer test absent from all OOF construction')
                assert_true(not oof & roles[-1], 'one OOF prediction per training episode')
                oof |= roles[-1]
            else:
                assert_true(roles[-1] == assessment and set.union(*roles[:3]) == development, 'final branch exact outer lineage')
        assert_true(oof == development, 'OOF meta fitting coverage exact')
    assert_true(all_outer == set(core), 'outer fold coverage exact')

    # Synthetic independence/control tests; these contain no real sensor or image data.
    synthetic = [{'episode_index': 2*task_id+label, 'canonical_task_id': task_id, 'label': label} for task_id in range(100) for label in (0,1)]
    first = build_splits(copy.deepcopy(synthetic), [[0,2]])
    second = build_splits(copy.deepcopy(synthetic), [[0,2]])
    inverted = [dict(row, label=1-row['label']) for row in synthetic]
    flipped = build_splits(inverted, [[0,2]])
    assert_true(first == second, 'synthetic deterministic split replay')
    assert_true(first[0] == flipped[0] and first[3] == flipped[3], 'synthetic changing labels never changes identities')
    assert_true(first[2] == 99, 'synthetic cross task duplicate joins task groups')
    proposal = read(RUN / 'config/EXPERIMENT_PROPOSAL.json')
    assert_true(proposal['seeds'] == [42,123,20261023] and proposal['visual']['epoch_budgets'] == [25,50], 'proposal fixed seeds and budgets')
    assert_true(proposal['sensors']['feature_width'] == 28*10, 'native sensor statistics width contract')
    assert_true(proposal['cohort_size'] == len(core) and proposal['training_performed'] is False, 'proposal references exact unexecuted V2 cohort')
    reference = read(RUN / '04_REASSEMBLE_REFERENCE/REFERENCE_AUDIT.json')
    assert_true(reference['gpu_initialized_by_this_audit'] is False and reference['ViFailback_weight_transfer_performed'] is False, 'no GPU initialization or target transfer')
    donor = next(row for row in reference['completed_100epoch_checkpoint_audits'] if row['valid_full_backbone_transfer_source'])
    assert_true(donor['backbone_tensors'] == 115 and donor['changed_backbone_tensors'] == 69 and donor['selected_epoch'] == 47, 'trained compatible donor established')
    for row in read(RUN / 'provenance/REASSEMBLE_SOURCE_AND_CHECKPOINT_HASHES.json'):
        assert_true(sha(REPO / row['path']) == row['sha256'], 'inspected immutable source checkpoint and result hashes unchanged')
    for path in (RUN / 'code').glob('*.py'):
        ast.parse(path.read_text(), filename=str(path))
        assert_true(True, 'audit source parses')
    baseline = read(RUN / 'provenance/INITIAL_REPOSITORY_STATE.json')
    status = subprocess.check_output(['git','status','--short','--untracked-files=no'], cwd=REPO, text=True)
    assert_true(status == baseline['tracked_status'], 'tracked working tree baseline preserved')
    diff = subprocess.run(['git','diff','--check'], cwd=REPO, text=True, capture_output=True)
    assert_true(diff.returncode == 0, 'git whitespace check')
    pip = subprocess.run([sys.executable,'-B','-m','pip','check'], text=True, capture_output=True)
    assert_true(pip.returncode == 0, 'repository environment dependencies consistent')
    full_status = subprocess.check_output(['git','status','--short','--branch','--untracked-files=all'], cwd=REPO, text=True)
    with (RUN / 'provenance/FINAL_REPOSITORY_STATUS.txt').open('x') as stream:
        stream.write(full_status)
    result = {'passed': True, 'assertions': sum(checks.values()), 'categories': dict(checks),
              'git_diff_check': {'returncode': diff.returncode, 'stdout': diff.stdout},
              'pip_check': {'returncode': pip.returncode, 'stdout': pip.stdout.strip()},
              'scope': 'Real-artifact integrity and lineage audit plus tiny synthetic split tests; no model fitting, forward inference or GPU benchmark',
              'full_RGB_cohort_verified': False}
    with (RUN / 'provenance/FINAL_VALIDATION.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))
