"""One-off approved location migration. Never read/hash/copy source payloads.

prepare writes a fresh metadata/ignore-policy snapshot only. apply requires a
matching explicit execution gate supplied by the coordinating agent. Frozen
studies additionally require independently prepared path-adapter gates.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import stat
import subprocess
import uuid

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'AGENTS.md').is_file() and (p / 'pyproject.toml').is_file())
GROUPS = [
    ('handover_raw', 'HANDOVER/01_raw_dataset', 'implementations/HANDOVER/01_raw_dataset'),
    ('reboot_raw', 'REBOOT/01_raw_dataset', 'implementations/REBOOT/01_raw_dataset'),
    ('reboot_runs', 'REBOOT/runs', 'implementations/REBOOT/runs'),
    ('vifailback', 'VIFAILBACK', 'implementations/VIFAILBACK'),
    ('milling_legacy', 'MILLING DATASET', 'implementations/MSM/experiments/legacy'),
    ('cross_examples', 'CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE/10_Visual_And_Sensor_Examples', 'implementations/cross_dataset/results/INDEPENDENT_REVIEW_PACKAGE/10_Visual_And_Sensor_Examples'),
    ('vif_verification', 'DATASET_RESEARCH/VIFAILBACK_VERIFICATION', 'implementations/VIFAILBACK/02_dataset_verification/independent_verification'),
    ('discovery_sources', 'DATASET_RESEARCH/NEW_DATASET_SELECTION_20261028/source_evidence', 'implementations/general/docs/dataset_research/NEW_DATASET_SELECTION_20261028/source_evidence'),
    ('feedback', '26.10.2026_feedback_experiments', 'implementations/REASSEMBLE/experiments/cnn_seed_stability/phase1_feedback'),
    ('bootstrap', 'parth_ws_bootstrap', 'implementations/REASSEMBLE/experiments/bootstrap'),
    ('phm_historical_eda', 'experiments/exp_a_initial_eda_r1_r3_r5', 'implementations/PHM2026/experiments/exp_a_initial_eda_r1_r3_r5'),
]
FROZEN = {'vifailback', 'feedback', 'bootstrap'}
SKIP = {'.git', '.aws', '.codex', '.agents', '.ssh', 'ma_thesis_env', '.venv', 'venv', 'node_modules'}
CONTAINERS = ['HANDOVER', 'REBOOT', 'CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE', 'CROSS_DATASET_COMPARISON', 'DATASET_RESEARCH/NEW_DATASET_SELECTION_20261028', 'DATASET_RESEARCH', 'experiments']


def now():
    return datetime.now(timezone.utc).isoformat()


def fail(message):
    raise RuntimeError(message)


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def metadata(path):
    s = path.lstat()
    result = {'device': s.st_dev, 'inode': s.st_ino, 'size': s.st_size, 'mode': s.st_mode, 'mtime_ns': s.st_mtime_ns}
    if stat.S_ISLNK(s.st_mode):
        result['link_text'] = os.readlink(path)
    return result


def exists(path):
    return os.path.lexists(path)


def sensitive(name):
    name = name.lower()
    return name in {'.env', '.envrc', 'synology_cookies.txt', 'credentials', 'id_rsa', 'id_ed25519'} or name.startswith('.env.') or name.endswith(('.pem', '.key')) or 'session_cookie' in name or 'access_token' in name


def walk(path):
    yield path
    if path.is_dir() and not path.is_symlink():
        for base, directories, files in os.walk(path, followlinks=False):
            for name in sorted(directories + files):
                yield Path(base) / name


def repo_entries():
    """Metadata enumeration, excluding private/environment and this phase itself."""
    for base, directories, files in os.walk(ROOT, followlinks=False):
        parent = Path(base)
        directories[:] = sorted(d for d in directories if d not in SKIP and not sensitive(d) and parent / d != HERE)
        for name in directories + sorted(files):
            if not sensitive(name):
                yield parent / name


def select(value):
    ids = {g[0] for g in GROUPS}
    if value == 'all':
        selected = ids
    elif value == 'nonfrozen':
        selected = ids - FROZEN - {'vif_verification'}
    else:
        selected = set(value.split(','))
    if not selected or selected - ids:
        fail('Unknown or empty group selection: ' + value)
    return [g for g in GROUPS if g[0] in selected]


def mappings(groups, extras=True):
    pairs = [(old, new) for _, old, new in groups]
    ids = {g[0] for g in groups}
    special = {}
    if 'vifailback' in ids:
        special['VIFAILBACK/README.md'] = 'implementations/VIFAILBACK/docs/WORKSPACE_BEFORE_CONSOLIDATION.md'
    if 'milling_legacy' in ids:
        special['MILLING DATASET/.gitignore'] = str((HERE / 'preserved_collisions/milling_root.gitignore').relative_to(ROOT))
    if extras:
        if 'handover_raw' in ids and exists(ROOT / 'HANDOVER/.gitignore'):
            special['HANDOVER/.gitignore'] = 'implementations/HANDOVER/.gitignore'
        if 'reboot_raw' in ids and 'reboot_runs' in ids and exists(ROOT / 'REBOOT/.gitignore'):
            special['REBOOT/.gitignore'] = 'implementations/REBOOT/.gitignore'
        if 'cross_examples' in ids and exists(ROOT / 'CROSS_DATASET_COMPARISON/.gitignore'):
            special['CROSS_DATASET_COMPARISON/.gitignore'] = str((HERE / 'preserved_collisions/cross_dataset_root.gitignore').relative_to(ROOT))
    return pairs, special


def mapper(groups, extras=True):
    pairs, special = mappings(groups, extras)
    def mapped(relative):
        text = str(relative)
        if text in special:
            return special[text]
        for old, new in sorted(pairs, key=lambda pair: len(pair[0]), reverse=True):
            if text == old or text.startswith(old + '/'):
                return new + text[len(old):]
        return text
    return mapped


def target_absolute(path, text):
    return Path(os.path.normpath(text if os.path.isabs(text) else path.parent / text))


def all_links():
    output = []
    for path in repo_entries():
        if path.is_symlink():
            text = os.readlink(path)
            absolute = target_absolute(path, text)
            row = {'path': str(path.relative_to(ROOT)), 'link_text': text, 'absolute_target': str(absolute), 'target_exists': path.exists(), 'link_identity': metadata(path)}
            if path.exists():
                s = path.stat()
                row['target_identity'] = {'device': s.st_dev, 'inode': s.st_ino}
            output.append(row)
    return output


def plan(groups):
    mapped = mapper(groups)
    actions, conflicts, records = [], [], []
    proxies = set()
    ids = {g[0] for g in groups}
    if 'vif_verification' in ids and 'vifailback' not in ids:
        parent = ROOT / 'implementations/VIFAILBACK/02_dataset_verification'
        if parent.is_symlink():
            conflicts.append({'reason': 'VIF verification destination is still a browsing proxy; move VIFAILBACK first.'})
    sources = [(gid, ROOT / old) for gid, old, _ in groups]
    _, special = mappings(groups)
    for old in special:
        if not any(old == a or old.startswith(a + '/') for _, a, _ in groups):
            sources.append(('supporting_ignore_policy', ROOT / old))
    seen = set()
    for gid, source in sources:
        if not exists(source):
            conflicts.append({'old': str(source.relative_to(ROOT)), 'reason': 'Source does not exist; do not replay an already applied group.'})
            continue
        for path in walk(source):
            old = str(path.relative_to(ROOT))
            if old in seen:
                continue
            seen.add(old)
            if sensitive(path.name):
                conflicts.append({'old': old, 'reason': 'Sensitive-name candidate; no contents accessed and automatic relocation blocked.'})
            records.append({'group': gid, 'old': old, 'new': mapped(old), **metadata(path)})

    def visit(a, b, gid):
        old, new = str(a.relative_to(ROOT)), str(b.relative_to(ROOT))
        ancestor = b.parent
        while not exists(ancestor):
            ancestor = ancestor.parent
        if a.lstat().st_dev != ancestor.stat().st_dev:
            conflicts.append({'old': old, 'new': new, 'reason': 'Different filesystem'})
            return
        if b.is_symlink():
            if a.resolve(strict=True) == b.resolve(strict=True):
                proxies.add(new)
                actions.append({'operation': 'remove_proxy', 'path': new, 'identity': metadata(b), 'group': gid})
                actions.append({'operation': 'rename', 'old': old, 'new': new, 'group': gid})
            else:
                conflicts.append({'old': old, 'new': new, 'reason': 'Independent destination symlink'})
        elif not exists(b):
            actions.append({'operation': 'rename', 'old': old, 'new': new, 'group': gid})
        elif a.is_dir() and not a.is_symlink() and b.is_dir():
            for child in sorted(a.iterdir(), key=lambda p: (p.name == ".gitignore", p.name)):
                visit(child, ROOT / mapped(child.relative_to(ROOT)), gid)
            actions.append({'operation': 'rmdir_empty', 'path': old, 'group': gid, 'original_identity': metadata(a)})
        else:
            conflicts.append({'old': old, 'new': new, 'reason': 'Independent destination file; no overwrite permitted'})

    ordered = sorted(sources, key=lambda pair: (0 if pair[0] == 'vifailback' else 2 if pair[0] == 'supporting_ignore_policy' else 1))
    for gid, source in ordered:
        if exists(source):
            visit(source, ROOT / mapped(source.relative_to(ROOT)), gid)
    links = all_links()
    repairs = []
    for link in links:
        if link['path'] in proxies:
            continue
        old_path = ROOT / link['path']
        new_path = ROOT / mapped(link['path'])
        target = Path(link['absolute_target'])
        original_target = target
        special_msm = False
        if link['path'] == 'implementations/MSM/01_raw_dataset/official_dataset' and 'milling_legacy' in ids:
            if link['link_text'] != '../../MILLING DATASET/data/raw/msm/versions/2':
                conflicts.append({'path': link['path'], 'reason': 'MSM historical link text changed; review intended target'})
                continue
            target = ROOT / 'MILLING DATASET/data/raw/msm/versions/2'
            if not target.is_dir():
                conflicts.append({'path': link['path'], 'reason': 'Verified MSM intended source target is unavailable'})
                continue
            original_target = target
            special_msm = True
        try:
            target = ROOT / mapped(target.relative_to(ROOT))
        except ValueError:
            pass
        prospective = target_absolute(new_path, link['link_text'])
        if target != prospective:
            if not link['target_exists'] and not special_msm:
                conflicts.append({'path': link['path'], 'reason': 'Relocation would require repairing an unverified pre-existing broken link'})
                continue
            s = original_target.stat()
            repairs.append({'path': str(new_path.relative_to(ROOT)), 'old_path': link['path'], 'old_link_text': link['link_text'], 'new_link_text': os.path.relpath(target, new_path.parent), 'expected_target': str(target), 'target_identity': {'device': s.st_dev, 'inode': s.st_ino}, 'original_identity': link['link_identity'], 'known_preexisting_msm_link_correction': special_msm})
    return {'groups': [g[0] for g in groups], 'prefix_mappings': [{'id': g, 'old': a, 'new': b} for g, a, b in groups], 'special_mappings': special, 'actions': actions, 'conflicts': conflicts, 'records': records, 'symlinks': links, 'repairs': repairs}


def git_ignored(paths, cwd, worktree=None):
    command = ['git']
    if worktree:
        command += ['--git-dir=' + str(ROOT / '.git'), '--work-tree=' + str(worktree)]
    command += ['check-ignore', '--no-index', '--verbose', '--stdin', '-z']
    result = subprocess.run(command, input=('\0'.join(paths) + '\0').encode(), cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode not in (0, 1):
        fail('git check-ignore failed: ' + result.stderr.decode(errors='replace'))
    words = result.stdout.decode().split('\0')
    output = {}
    for i in range(0, len(words) - 1, 4):
        source, line, pattern, path = words[i:i + 4]
        output[path] = {'source': source, 'line': line, 'pattern': pattern, 'ignored': not pattern.startswith('!')}
    return output


def ignore_audit(info, directory):
    """Mirror only .gitignore policy text, never source/dataset payloads."""
    groups = [g for g in GROUPS if g[0] in info['groups']]
    mapped = mapper(groups)
    shadow = directory / 'ignore_policy_shadow'
    shadow.mkdir()
    policy_inputs = []
    for path in repo_entries():
        if path.name != '.gitignore' or not path.is_file() or path.is_symlink():
            continue
        relative = str(path.relative_to(ROOT))
        destination = shadow / mapped(relative)
        # Preserved collisions end in *_root.gitignore and are not active policy.
        if destination.name != '.gitignore':
            continue
        before = metadata(path)
        content = path.read_bytes()
        if metadata(path) != before:
            fail('Ignore policy changed during inspection: ' + relative)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            fail('Two independent ignore policies collide in shadow: ' + relative)
        destination.write_bytes(content)
        policy_inputs.append({'path': relative, 'mapped_path': mapped(relative), 'identity': before})
    regular = [r for r in info['records'] if stat.S_ISREG(r['mode'])]
    old = git_ignored([r['old'] for r in regular], ROOT)
    new = git_ignored([r['new'] for r in regular], shadow, shadow)
    exposed, newly_ignored = [], []
    summary = Counter()
    for row in regular:
        a = old.get(row['old'], {'ignored': False})
        b = new.get(row['new'], {'ignored': False})
        summary['regular_files'] += 1
        summary['old_ignored'] += a['ignored']
        summary['new_ignored'] += b['ignored']
        if a['ignored'] and not b['ignored']:
            exposed.append({'old': row['old'], 'new': row['new'], 'bytes': row['size'], 'old_rule': a, 'new_rule': b, 'group': row['group']})
        elif b['ignored'] and not a['ignored']:
            newly_ignored.append({'old': row['old'], 'new': row['new'], 'bytes': row['size'], 'old_rule': a, 'new_rule': b, 'group': row['group']})
    summary['ignored_to_exposed'] = len(exposed)
    summary['newly_ignored'] = len(newly_ignored)
    dump(directory / 'IGNORE_EXPOSURES.json', exposed)
    dump(directory / 'NEWLY_IGNORED.json', newly_ignored)
    dump(directory / 'IGNORE_POLICY_INPUTS.json', policy_inputs)
    dump(directory / 'IGNORE_SUMMARY.json', dict(summary))
    return dict(summary)


def prepare(groups):
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    directory = HERE / ('preflight_' + stamp)
    directory.mkdir()
    info = plan(groups)
    records = info.pop('records')
    with (directory / 'FILE_METADATA_BEFORE.jsonl').open('x') as stream:
        for row in records:
            stream.write(json.dumps(row) + '\n')
    info['records'] = records
    ignore = ignore_audit(info, directory)
    del info['records']
    dump(directory / 'PLAN.json', info)
    status = {'utc': now(), 'phase': 'PREPARED_NO_MOVES', 'groups': info['groups'], 'source_nodes': len(records), 'regular_files': sum(stat.S_ISREG(r['mode']) for r in records), 'logical_bytes': sum(r['size'] for r in records if stat.S_ISREG(r['mode'])), 'actions': dict(Counter(a['operation'] for a in info['actions'])), 'conflicts': info['conflicts'], 'symlinks_inspected': len(info['symlinks']), 'preexisting_broken_links': sum(not s['target_exists'] for s in info['symlinks']), 'planned_symlink_repairs': len(info['repairs']), 'ignore_audit': ignore, 'frozen_groups_requiring_adapter_gate': sorted(set(info['groups']) & FROZEN), 'payloads_read_hashed_copied': False}
    dump(directory / 'STATUS.json', status)
    print(json.dumps({'preflight': str(directory.relative_to(ROOT)), **status}, indent=2))
    return directory


def journal(directory, state, operation_id, action, **extra):
    row = {'utc': now(), 'state': state, 'operation_id': operation_id, **action, **extra}
    with (directory / 'ACTIONS.jsonl').open('a') as stream:
        stream.write(json.dumps(row) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


def unchanged(path, expected):
    return exists(path) and metadata(path) == expected


def ensure_parents(path, directory):
    missing = []
    while not exists(path):
        missing.append(path)
        path = path.parent
    if path.is_symlink():
        fail('Destination ancestor remains a symlink: ' + str(path))
    for p in reversed(missing):
        action = {'operation': 'mkdir', 'path': str(p.relative_to(ROOT))}
        opid = uuid.uuid4().hex
        journal(directory, 'INTENT', opid, action)
        p.mkdir()
        journal(directory, 'DONE', opid, action, post_identity=metadata(p))


def check_gate(directory, gate_file, info):
    approval = json.loads((HERE / 'APPROVAL.json').read_text())
    approved = {(r['old'], r['new']) for r in approval['scope']}
    if approved != {(a, b) for _, a, b in GROUPS}:
        fail('Recorded approval is not the exact eleven-group scope')
    gate = json.loads(gate_file.read_text())
    if gate.get('preflight') != str(directory.relative_to(ROOT)) or set(gate.get('groups', [])) != set(info['groups']) or gate.get('process_gate_passed') is not True:
        fail('Execution gate does not bind this preflight/group set and passed process check')
    if gate.get('scientific_jobs_will_not_be_resumed') is not True:
        fail('Missing explicit no-resume gate')
    checked = datetime.fromisoformat(gate['checked_utc'])
    if (datetime.now(timezone.utc) - checked).total_seconds() > 1800:
        fail('Execution process gate older than 30 minutes; refresh it')
    gpu = json.loads((HERE / 'GPU_GATE_BEFORE.json').read_text())
    if gpu['returncode'] != 0 or gpu['stdout'].strip():
        fail('Recorded GPU gate failed')
    for gid in FROZEN & set(info['groups']):
        location = gate.get('adapter_gates', {}).get(gid)
        if not location:
            fail('Missing frozen path-adapter gate: ' + gid)
        report = json.loads((ROOT / location).read_text())
        if report.get('status') != 'PASS' or report.get('frozen_source_unchanged') is not True or report.get('no_resume') is not True or gid not in report.get('groups', []):
            fail('Frozen adapter gate did not pass: ' + gid)
    return gate


def apply(directory, gate_file):
    directory = directory.resolve(strict=True)
    if directory.parent != HERE:
        fail('Only this phase preflights may be applied')
    if (directory / 'ACTIONS.jsonl').exists() or (directory / 'APPLY_STATUS.json').exists():
        fail('Attempt already started; use recovery or inspect journal, never replay')
    info = json.loads((directory / 'PLAN.json').read_text())
    status = json.loads((directory / 'STATUS.json').read_text())
    if info['conflicts'] or status['ignore_audit']['ignored_to_exposed']:
        fail('Unresolved collisions or ignore exposure; make a new preflight after resolving')
    gate = check_gate(directory, gate_file, info)
    records = [json.loads(line) for line in (directory / 'FILE_METADATA_BEFORE.jsonl').read_text().splitlines()]
    for row in records:
        expected = {k: row[k] for k in ('device', 'inode', 'size', 'mode', 'mtime_ns')}
        if 'link_text' in row:
            expected['link_text'] = row['link_text']
        if not unchanged(ROOT / row['old'], expected):
            fail('Source changed since preflight: ' + row['old'])
    for item in json.loads((directory / 'IGNORE_POLICY_INPUTS.json').read_text()):
        if not unchanged(ROOT / item['path'], item['identity']):
            fail('Ignore policy changed since preflight; prepare again: ' + item['path'])
    dump(directory / 'EXECUTION_GATE_USED.json', gate)
    renamed_records = []
    try:
        for action in info['actions']:
            opid = uuid.uuid4().hex
            kind = action['operation']
            if kind == 'rename':
                a, b = ROOT / action['old'], ROOT / action['new']
                ensure_parents(b.parent, directory)
                if exists(b) or a.lstat().st_dev != b.parent.stat().st_dev:
                    fail('Destination conflict or filesystem mismatch at rename: ' + action['new'])
                subset = [r for r in records if r['old'] == action['old'] or r['old'].startswith(action['old'] + '/')]
                for row in subset:
                    oldmeta = {k: row[k] for k in ('device', 'inode', 'size', 'mode', 'mtime_ns')}
                    if 'link_text' in row:
                        oldmeta['link_text'] = row['link_text']
                    if not unchanged(ROOT / row['old'], oldmeta):
                        fail('Source changed immediately before rename: ' + row['old'])
                journal(directory, 'INTENT', opid, action, source_identity=metadata(a))
                os.rename(a, b)
                for row in subset:
                    expected = {k: row[k] for k in ('device', 'inode', 'size', 'mode', 'mtime_ns')}
                    if 'link_text' in row:
                        expected['link_text'] = row['link_text']
                    if not unchanged(ROOT / row['new'], expected):
                        fail('Metadata changed immediately after rename: ' + row['new'])
                journal(directory, 'DONE', opid, action, post_identity=metadata(b), verified_nodes=len(subset))
                renamed_records.extend(subset)
            elif kind == 'remove_proxy':
                p = ROOT / action['path']
                if not unchanged(p, action['identity']) or not p.is_symlink():
                    fail('Browsing proxy changed: ' + action['path'])
                journal(directory, 'INTENT', opid, action)
                p.unlink()
                journal(directory, 'DONE', opid, action)
            elif kind == 'rmdir_empty':
                p = ROOT / action['path']
                if p.is_symlink() or any(p.iterdir()):
                    fail('Expected empty source container is not empty: ' + action['path'])
                journal(directory, 'INTENT', opid, action, pre_identity=metadata(p))
                p.rmdir()
                journal(directory, 'DONE', opid, action)
            else:
                fail('Unknown action: ' + kind)
        for repair in info['repairs']:
            p = ROOT / repair['path']
            if not p.is_symlink() or os.readlink(p) != repair['old_link_text']:
                fail('Link changed before repair: ' + repair['path'])
            target = Path(repair['expected_target'])
            s = target.stat()
            if {'device': s.st_dev, 'inode': s.st_ino} != repair['target_identity']:
                fail('Symlink target identity changed: ' + repair['path'])
            action = {'operation': 'repair_symlink', **repair}
            opid = uuid.uuid4().hex
            journal(directory, 'INTENT', opid, action, pre_identity=metadata(p))
            temporary = p.with_name('.' + p.name + '.relocation-' + opid)
            if exists(temporary):
                fail('Temporary symlink conflict')
            temporary.symlink_to(repair['new_link_text'])
            os.replace(temporary, p)
            if not p.exists() or p.stat().st_ino != s.st_ino or p.stat().st_dev != s.st_dev:
                fail('Repaired link did not retain target identity: ' + repair['path'])
            journal(directory, 'DONE', opid, action, post_identity=metadata(p))
        for relative in CONTAINERS:
            p = ROOT / relative
            if p.is_dir() and not p.is_symlink() and not any(p.iterdir()):
                action = {'operation': 'rmdir_empty', 'path': relative, 'original_identity': metadata(p)}
                opid = uuid.uuid4().hex
                journal(directory, 'INTENT', opid, action)
                p.rmdir()
                journal(directory, 'DONE', opid, action)
        regulars = [r for r in records if stat.S_ISREG(r['mode'])]
        mismatches = []
        with (directory / 'FILE_METADATA_AFTER.jsonl').open('x') as stream:
            for row in regulars:
                actual = metadata(ROOT / row['new'])
                expected = {k: row[k] for k in ('device', 'inode', 'size', 'mode', 'mtime_ns')}
                if actual != expected:
                    mismatches.append(row['new'])
                stream.write(json.dumps({'old': row['old'], 'new': row['new'], **actual}) + '\n')
        if mismatches:
            fail('Final regular-file metadata preservation failed: ' + str(mismatches[:10]))
        after = all_links()
        dump(directory / 'SYMLINKS_AFTER.json', after)
        after_by_path = {r['path']: r for r in after}
        mapped = mapper([g for g in GROUPS if g[0] in info['groups']])
        removed = {a['path'] for a in info['actions'] if a['operation'] == 'remove_proxy'}
        new_broken = [r['path'] for r in info['symlinks'] if r['target_exists'] and r['path'] not in removed and not after_by_path.get(mapped(r['path']), {}).get('target_exists')]
        actual_ignore = git_ignored([r['new'] for r in regulars], ROOT)
        expected_ignore = git_ignored([r['new'] for r in regulars], directory / 'ignore_policy_shadow', directory / 'ignore_policy_shadow')
        ignore_mismatches = [r['new'] for r in regulars if actual_ignore.get(r['new'], {}).get('ignored', False) != expected_ignore.get(r['new'], {}).get('ignored', False)]
        result = {'utc': now(), 'status': 'PASS' if not new_broken and not ignore_mismatches else 'FAIL', 'groups': info['groups'], 'regular_files_preserved': len(regulars), 'metadata_mismatches': mismatches, 'newly_broken_links': new_broken, 'symlink_repairs': len(info['repairs']), 'ignore_policy_mismatches': ignore_mismatches, 'old_group_roots_remaining': [g['old'] for g in info['prefix_mappings'] if exists(ROOT / g['old'])], 'payloads_read_hashed_copied': False, 'experiments_or_jobs_started': False}
        dump(directory / 'APPLY_STATUS.json', result)
        if result['status'] != 'PASS' or result['old_group_roots_remaining']:
            fail('Post-relocation validation failed; inspect append-only journal')
        print(json.dumps(result, indent=2))
    except BaseException as exc:
        if not (directory / 'FAILURE.json').exists():
            dump(directory / 'FAILURE.json', {'utc': now(), 'error_type': type(exc).__name__, 'error': str(exc), 'instruction': 'Stop further moves. Inspect ACTIONS.jsonl; recovery must verify every successful operation and refuse original-path conflicts.'})
        raise


def recover(directory, execute=False):
    """Reverse only recorded completed actions, never overwrite emerging paths."""
    directory = directory.resolve(strict=True)
    if directory.parent != HERE:
        fail('Recovery accepts this phase preflights only')
    rows = [json.loads(line) for line in (directory / 'ACTIONS.jsonl').read_text().splitlines()]
    intents = {r['operation_id']: r for r in rows if r['state'] == 'INTENT'}
    done = [r for r in rows if r['state'] == 'DONE']
    completed = {r['operation_id'] for r in done}
    pending = [r for oid, r in intents.items() if oid not in completed]
    if pending:
        fail('Unfinished journal intent requires identity audit before automatic recovery: ' + json.dumps(pending))
    recovery = [{'reverse_of': r['operation_id'], 'operation': r['operation'], 'old': r.get('old'), 'new': r.get('new'), 'path': r.get('path')} for r in reversed(done)]
    if not execute:
        print(json.dumps({'status': 'DRY_RUN', 'reverse_actions': recovery, 'note': 'Each live identity and original-path vacancy is checked immediately before its inverse operation.'}, indent=2))
        return
    if (directory / 'RECOVERY_STATUS.json').exists() or (directory / 'RECOVERY_ACTIONS.jsonl').exists():
        fail('Recovery already started; inspect its journal, never repeat blindly')
    def record(action):
        with (directory / 'RECOVERY_ACTIONS.jsonl').open('a') as stream:
            stream.write(json.dumps({'utc': now(), **action}) + '\n');stream.flush();os.fsync(stream.fileno())
    for row in reversed(done):
        kind = row['operation'];record({'state': 'INTENT', 'reverse_of': row['operation_id'], 'operation': kind})
        if kind == 'repair_symlink':
            p = ROOT / row['path']
            if not unchanged(p, row['post_identity']):fail('Repaired link changed; recovery refused: ' + row['path'])
            temp = p.with_name('.' + p.name + '.recovery-' + uuid.uuid4().hex);temp.symlink_to(row['old_link_text']);os.replace(temp, p)
        elif kind == 'rmdir_empty':
            p = ROOT / row['path']
            if exists(p):fail('Original container path reappeared: ' + row['path'])
            identity = row.get('original_identity') or intents[row['operation_id']]['pre_identity']
            p.mkdir(mode=stat.S_IMODE(identity['mode']))
        elif kind == 'rename':
            a, b = ROOT / row['old'], ROOT / row['new']
            if exists(a):fail('Original path reappeared; never overwrite: ' + row['old'])
            expected = row['post_identity'];actual = metadata(b)
            # Child-container merges can change directory mtime after the rename;
            # regular-file preservation remains exact and is checked below.
            if any(actual[k] != expected[k] for k in ('device', 'inode', 'mode')):fail('Moved node identity changed: ' + row['new'])
            if stat.S_ISREG(expected['mode']) and actual != expected:fail('Moved file changed: ' + row['new'])
            records = [json.loads(line) for line in (directory / 'FILE_METADATA_BEFORE.jsonl').read_text().splitlines()]
            for item in records:
                if stat.S_ISREG(item['mode']) and (item['old'] == row['old'] or item['old'].startswith(row['old'] + '/')):
                    expected_file = {k: item[k] for k in ('device', 'inode', 'size', 'mode', 'mtime_ns')}
                    if not unchanged(ROOT / item['new'], expected_file):fail('Scientific file changed; recovery refused: ' + item['new'])
            if a.parent.is_symlink() or b.stat().st_dev != a.parent.stat().st_dev:fail('Recovery destination is unsafe')
            os.rename(b, a)
        elif kind == 'remove_proxy':
            p = ROOT / row['path']
            if exists(p):fail('Proxy recovery path is occupied: ' + row['path'])
            p.symlink_to(row['identity']['link_text'])
        elif kind == 'mkdir':
            p = ROOT / row['path']
            if p.is_symlink() or metadata(p)['inode'] != row['post_identity']['inode'] or any(p.iterdir()):fail('Created container changed or not empty: ' + row['path'])
            p.rmdir()
        else:fail('Unknown inverse action: ' + kind)
        record({'state': 'DONE', 'reverse_of': row['operation_id'], 'operation': kind})
    records = [json.loads(line) for line in (directory / 'FILE_METADATA_BEFORE.jsonl').read_text().splitlines()]
    regulars = [row for row in records if stat.S_ISREG(row['mode'])]
    for row in regulars:
        expected = {k: row[k] for k in ('device', 'inode', 'size', 'mode', 'mtime_ns')}
        if not unchanged(ROOT / row['old'], expected):
            fail('Restored regular-file identity mismatch: ' + row['old'])
    dump(directory / 'RECOVERY_STATUS.json', {'utc': now(), 'status': 'REVERSED', 'actions': len(done), 'regular_files_revalidated': len(regulars), 'regular_payloads_overwritten_or_deleted': False})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('prepare');p.add_argument('--groups', default='all')
    p = sub.add_parser('apply');p.add_argument('--preflight', required=True);p.add_argument('--gate', required=True)
    p = sub.add_parser('recover');p.add_argument('--preflight', required=True);p.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    if args.command == 'prepare':prepare(select(args.groups))
    elif args.command == 'apply':apply(ROOT / args.preflight, ROOT / args.gate)
    else:recover(ROOT / args.preflight, args.execute)


if __name__ == '__main__':
    main()
