"""Export a measured candidate for a new study; never modify or launch a fit."""
import hashlib
import json
import math
from pathlib import Path

from .benchmark import compare_throughput
from .guards import LOCAL_ROOT, PROTOCOL_SHA256, inspect_admission
from .settings import PRESETS


def _sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _json(path):
    _require(Path(path).stat().st_size <= 16 * 1024 ** 2, 'Oversized evidence receipt')
    def unique(pairs):
        result = {}
        for key, value in pairs:
            _require(key not in result, 'Duplicate JSON evidence key')
            result[key] = value
        return result
    return json.loads(Path(path).read_text(), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Nonfinite JSON evidence')))


def _digest(value):
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def _number(value, *, positive=False):
    return type(value) in (int, float) and math.isfinite(value) and (value > 0 if positive else value >= 0)


def _check_case(value, name, numerical, ids, warmup, episodes, expected_state=None):
    """Check the declared benchmark geometry and numerical evidence structure."""
    _require(value.get('config') == name and value.get('numerical_proof_pass') is numerical,
             'Case configuration/proof identity differs from its filename')
    keys = ('initial_state_sha256', 'final_state_sha256', 'scheduler_boundary_probe_sha256')
    _require(all(_digest(value.get(key)) for key in keys), 'Missing state-equivalence digests')
    if expected_state is not None:
        _require(all(value[key] == expected_state[key] for key in keys), 'Case state-equivalence mismatch')
    _require(type(value.get('measured_episodes')) is int and value['measured_episodes'] == episodes,
             'Case episode budget differs from benchmark options')
    duration, rate = value.get('measurement_seconds'), value.get('episodes_per_second')
    _require(_number(duration, positive=True) and _number(rate, positive=True), 'Invalid measured throughput')
    _require(math.isclose(rate, episodes / duration, rel_tol=1e-12, abs_tol=0), 'Throughput does not match measured duration')
    batches = value.get('batches')
    _require(isinstance(batches, list) and len(batches) == len(ids) // 8, 'Incomplete case batch evidence')
    for index, row in enumerate(batches):
        offset = index * 8
        _require(isinstance(row, dict) and type(row.get('offset')) is int and row['offset'] == offset and
                 type(row.get('episodes')) is int and row['episodes'] == 8 and row.get('warmup') is (offset < warmup),
                 'Case batch geometry differs from declared warmup/measurement')
        for field in ('loader_wait_GPU_quiescent_seconds', 'compute_wall_seconds',
                      'GPU_stream_elapsed_ms', 'guard_overhead_seconds'):
            _require(_number(row.get(field)), 'Invalid batch timing evidence')
        if numerical:
            proof = row.get('proof', {})
            inputs = proof.get('inputs', [])
            _require(len(inputs) == 8, 'Incomplete numerical input evidence')
            for expected, item in zip(ids[offset:offset + 8], inputs):
                _require(type(item.get('episode_index')) is int and item['episode_index'] == expected and
                         type(item.get('label')) is int and item['label'] in (0, 1) and
                         item.get('is_pinned') is True and _digest(item.get('tensor_sha256')),
                         'Numerical input/label/pinned-memory evidence is malformed')
            for field in ('labels_sha256', 'loss_sha256', 'logits_sha256', 'unclipped_gradients_sha256',
                          'model_sha256', 'optimizer_sha256', 'scheduler_sha256', 'RNG_sha256'):
                _require(_digest(proof.get(field)), 'Incomplete numerical update evidence')
            _require(_number(proof.get('global_gradient_norm')), 'Invalid numerical gradient norm')
        else:
            _require('proof' not in row, 'Timed cases must not contain per-step numerical hashing')
    measured = batches[warmup // 8:]
    wait = sum(row['loader_wait_GPU_quiescent_seconds'] for row in measured)
    compute = sum(row['compute_wall_seconds'] for row in measured)
    guard = sum(row['guard_overhead_seconds'] for row in measured[1:])
    for field, actual in (('loader_wait_GPU_quiescent_seconds', wait), ('compute_wall_seconds', compute),
                          ('guard_overhead_seconds_inside_measurement', guard)):
        _require(_number(value.get(field)) and math.isclose(value[field], actual, rel_tol=1e-10, abs_tol=1e-9),
                 'Aggregate timing does not match complete batch evidence')
    _require(duration + 1e-6 >= wait + compute + guard, 'Measured wall time is shorter than its timed components')


def checked_recommendation(receipt_path):
    """Check local evidence consistency, not cryptographic authorship.

    Hashes detect alteration against these receipts; an actor able to replace
    every file and every hash can fabricate a self-consistent evidence bundle.
    """
    try:
        return _checked_recommendation(receipt_path)
    except (KeyError, TypeError, IndexError, AttributeError, OSError, ZeroDivisionError) as exc:
        raise ValueError(f'Malformed or unavailable benchmark evidence: {type(exc).__name__}') from exc


def _checked_recommendation(receipt_path):
    path = Path(receipt_path).resolve()
    if LOCAL_ROOT.resolve() not in path.parents:
        raise ValueError('Use a benchmark receipt inside the isolated optimization directory')
    result = _json(path)
    _require(isinstance(result, dict) and result.get('schema') == 1, 'Unsupported benchmark evidence schema')
    if result.get('status') != 'COMPLETE' or result.get('GPU_measurement_performed') is not True:
        raise ValueError('A completed measured GPU benchmark is required')
    if result.get('numerical_equivalence_pass') is not True:
        raise ValueError('Exact numerical equivalence has not passed')
    recommendation = result.get('recommendation', {})
    name = recommendation.get('config')
    if recommendation.get('status') != 'MEASURED_CANDIDATE' or name not in PRESETS or name == 'baseline_w2_p1':
        raise ValueError('No measured improved loader candidate is available')
    configurations = result['configurations']
    names = list(configurations)
    _require(2 <= len(names) <= 4 and 'baseline_w2_p1' in names and name in names and set(names) <= set(PRESETS),
             'Incomplete or unsupported comparison configurations')
    _require(result.get('baseline') == 'baseline_w2_p1', 'Incorrect comparison baseline')
    _require(all(configurations[n] == PRESETS[n].as_dict() for n in names), 'Measured loader configuration has changed')
    options = result['options']
    rounds, episodes, warmup = options['rounds'], options['measured_episodes'], options['warmup_episodes']
    _require(type(rounds) is int and 3 <= rounds <= 8 and rounds % len(names) == 0 and
             type(episodes) is int and 16 <= episodes <= 128 and episodes % 8 == 0 and
             type(warmup) is int and warmup == 8, 'Unsupported or unbalanced benchmark budget')
    orders = result['round_orders']
    _require(isinstance(orders, list) and len(orders) == rounds and isinstance(orders[0], list) and
             len(orders[0]) == len(names) and set(orders[0]) == set(names), 'Missing balanced comparison order')
    first = orders[0]
    _require(all(order == first[index % len(names):] + first[:index % len(names)]
                 for index, order in enumerate(orders)), 'Comparison orders are not the declared balanced rotations')
    ids = result['selected_episode_ids']
    _require(isinstance(ids, list) and len(ids) == warmup + episodes and
             all(type(eid) is int for eid in ids) and len(set(ids)) == len(ids), 'Invalid ordered benchmark episode identities')
    _require(result.get('role') == 'T' and result.get('seed') == 42 and result.get('job_id') == 'outer0_inner0',
             'Benchmark role/seed/job differs from the declared comparison')
    _require(result.get('numerical_checks') == {n: True for n in names}, 'Not every measured configuration passed equivalence')
    actual = {str(p.relative_to(LOCAL_ROOT)):_sha(p) for p in sorted(LOCAL_ROOT.rglob('*.py'))}
    if result.get('isolated_source_sha256') != actual:
        raise ValueError('Isolated benchmark/loader implementation changed since measurement')
    cases = result.get('case_receipts_sha256', {})
    expected_files = {'numerical_reference.json'} | {f'numerical_{n}.json' for n in names} | {
        f'timing_round{r}_{n}.json' for r in range(1, rounds + 1) for n in names}
    _require(set(cases) == expected_files, 'Measured case receipts are incomplete or unexpected')
    evidence = {}
    for filename, digest in cases.items():
        case_path = (path.parent / filename).resolve()
        _require(case_path.parent == path.parent and _digest(digest) and _sha(case_path) == digest,
                 'Measured case receipt is missing, outside its directory, or changed')
        evidence[filename] = _json(case_path)
    reference = evidence['numerical_reference.json']
    _check_case(reference, '__reference__', True, ids, warmup, episodes)
    reference_proof = [row['proof'] for row in reference['batches']]
    for candidate_name in names:
        case = evidence[f'numerical_{candidate_name}.json']
        _check_case(case, candidate_name, True, ids, warmup, episodes, reference)
        _require(case.get('exact_reference_equivalence') is True and
                 [row['proof'] for row in case['batches']] == reference_proof,
                 'Candidate numerical proof differs from the original loader')
    timing = []
    for r in range(1, rounds + 1):
        values = {}
        for candidate_name in names:
            case = evidence[f'timing_round{r}_{candidate_name}.json']
            _check_case(case, candidate_name, False, ids, warmup, episodes, reference)
            values[candidate_name] = case
        timing.append(values)
    recomputed = compare_throughput(timing, names)
    _require(recomputed['status'] == 'MEASURED_CANDIDATE' and recommendation == recomputed,
             'Claimed improvement/recommendation does not match measured timing cases')
    cpu_path = (LOCAL_ROOT.parent/result['CPU_contract_receipt']).resolve()
    if LOCAL_ROOT.resolve() not in cpu_path.parents or _sha(cpu_path) != result['CPU_contract_receipt_sha256']:
        raise ValueError('CPU contract receipt changed since measurement')
    cpu = _json(cpu_path)
    _require(cpu.get('schema') == 1 and cpu.get('status') == 'PASS' and
             set(names) <= set(cpu.get('checked_config_names', [])), 'CPU contract evidence is not a complete PASS')
    binding = cpu['binding']
    binding_sha = hashlib.sha256(json.dumps(binding, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
    _require(binding_sha == cpu.get('binding_sha256') and
             all(binding.get('configurations', {}).get(n) == PRESETS[n].as_dict() for n in names),
             'CPU contract binding/configuration evidence differs')
    _require(binding.get('protocol_sha256') == PROTOCOL_SHA256 and all(_digest(binding.get(key)) for key in
             ('cohort_sha256', 'splits_sha256', 'legacy_config_sha256')), 'CPU data/protocol binding is incomplete')
    repo = LOCAL_ROOT.resolve().parents[3]
    expected_sources = {str((LOCAL_ROOT / 'future_dataloader' / filename).relative_to(repo)):
                        _sha(LOCAL_ROOT / 'future_dataloader' / filename)
                        for filename in ('contracts.py', 'loader.py', 'settings.py')}
    _require(binding.get('isolated_source_sha256') == expected_sources, 'CPU contract loader/source binding is stale')
    original_sources = binding.get('original_source_sha256', {})
    _require(isinstance(original_sources, dict) and original_sources, 'CPU original-source binding is missing')
    allowed_roots = [repo / 'VIFAILBACK/src', repo / 'VIFAILBACK/configs',
                     LOCAL_ROOT.parent / 'src', LOCAL_ROOT.parent / 'scripts']
    for relative, digest in original_sources.items():
        source = (repo / relative).resolve()
        _require(not Path(relative).is_absolute() and source.suffix in ('.py', '.json', '.yaml', '.yml', '.toml') and
                 any(base.resolve() in source.parents for base in allowed_roots), 'Unexpected original source binding path')
        _require(_digest(digest) and _sha(source) == digest, 'CPU original-source binding is stale')
    return result, PRESETS[name]


def export_config(receipt_path, output_dir):
    """Only export admission evidence; an existing controller never imports it."""
    result, config = checked_recommendation(receipt_path)
    admission = inspect_admission(configurations=[config])
    if not admission['ready']:
        raise ValueError('Protected queue/resources are unavailable: '+'; '.join(admission['reasons']))
    out = Path(output_dir).resolve()
    if LOCAL_ROOT.resolve() not in out.parents:
        raise ValueError('Export must remain inside the isolated preparation directory')
    value = {'schema':1,'status':'EXPORTED_MEASURED_CANDIDATE_ONLY',
             'loader_config':config.as_dict(),'benchmark_receipt_sha256':_sha(receipt_path),
             'benchmark_receipt':str(Path(receipt_path).resolve().relative_to(LOCAL_ROOT)),
             'scope':result['recommendation']['scope'],'protected_queue_complete':True,
             'production_training_started':False,'existing_controllers_modified':False,
             'activation':'Use this configuration explicitly with build_loader in a separately versioned future study; retain existing model/optimizer/epochs/seeds/splits.'}
    with (out/'FUTURE_LOADER_ADMISSION.json').open('x') as stream:
        json.dump(value,stream,indent=2)
        stream.write('\n')
    return value
