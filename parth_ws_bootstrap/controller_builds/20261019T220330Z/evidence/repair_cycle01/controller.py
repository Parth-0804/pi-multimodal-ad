#!/usr/bin/env python3
"""Offline sequential runner. Live execution is deliberately unavailable.

All executable operations are fixed synthetic fixtures. Filesystem validation is
application-level confinement, not an OS sandbox for hostile worker processes.
"""
import argparse
from contextlib import contextmanager
import copy
from datetime import datetime, timezone
import fcntl
import hashlib
import hmac
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
import uuid
from adapters import FakeAdapter, CodexAdapter, MARKER, Refused, arguments

BUILD = Path(__file__).resolve().parents[1]
FIXTURE_KEY = b'PUBLIC-SYNTHETIC-FIXTURE-KEY-NOT-CREDENTIAL'
TASK_FIELDS = {'id', 'depends_on', 'operation', 'authorization_requirement', 'inputs',
               'outputs', 'acceptance_checks', 'resource_limits', 'arguments', 'idempotent'}
CHECKS = ['artifact_hash', 'synthetic_identity', 'method_validity', 'separate_review']


def utc():
    return datetime.now(timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def decode(raw):
    def pairs(items):
        result = {}
        for k, v in items:
            if k in result:
                raise Refused('Duplicate JSON key')
            result[k] = v
        return result
    def reject(value):
        raise Refused('Non-finite JSON number')
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=reject)
    except (ValueError, TypeError) as exc:
        raise Refused('Malformed JSON') from exc


def confined(root, relative):
    """Reject traversal and every existing symlink, including internal links."""
    root = Path(root)
    p = Path(relative)
    if p.is_absolute() or not p.parts or '..' in p.parts or str(p) == '.':
        raise Refused('Path must be a confined relative file/directory')
    for node in [root, *root.parents]:
        if node.is_symlink():
            raise Refused('Symlink root refused')
    current = root
    for part in p.parts:
        current = current / part
        if current.is_symlink():
            raise Refused('Symlink escape refused')
    if not current.resolve().is_relative_to(root.resolve()):
        raise Refused('Path escapes root')
    return current


def run_root(path):
    p = Path(os.path.abspath(path))
    if p.is_relative_to(BUILD / 'runtime'):
        confined(BUILD, p.relative_to(BUILD))
    elif p.is_relative_to(BUILD / 'evidence/test_work'):
        confined(BUILD, p.relative_to(BUILD))
    else:
        raise Refused('Synthetic runtime must stay inside this build/runtime or evidence/test_work')
    if p in [BUILD / 'runtime', BUILD / 'evidence/test_work']:
        raise Refused('Use a dedicated runtime child directory')
    return p


def atomic(root, name, value):
    p = confined(root, name)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = confined(root, str(p.relative_to(root)) + '.' + uuid.uuid4().hex + '.tmp')
    raw = canonical(value) + b'\n'
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as f:
        f.write(raw); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, p)
    directory = os.open(p.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def read(root, name):
    return decode(confined(root, name).read_bytes())


@contextmanager
def locked(root, name, nonblocking=False):
    path = confined(root, '.controller/' + name)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | (fcntl.LOCK_NB if nonblocking else 0))
        except BlockingIOError as exc:
            raise Refused('Another coordinator owns the writer lock') from exc
        yield
    finally:
        os.close(fd)


def code_identity():
    return {name: digest(BUILD / 'runner' / name)
            for name in ['controller.py', 'adapters.py', 'synthetic_worker.py']}


def validate_config(config):
    if not isinstance(config, dict) or set(config) != {'kind', 'protocol_version', 'limits', 'tasks'}:
        raise Refused('Unknown/missing configuration or policy fields')
    if config['kind'] != MARKER or config['protocol_version'] != 'SYNTHETIC-1':
        raise Refused('Only synthetic protocol is implemented')
    limits = config['limits']
    if not isinstance(limits, dict) or set(limits) != {'max_dispatches', 'wall_seconds', 'max_output_bytes', 'model_calls', 'remote_jobs'}:
        raise Refused('Explicit complete budgets required')
    for key in ['max_dispatches', 'wall_seconds', 'max_output_bytes']:
        v = limits[key]
        if type(v) not in (int, float) or not math.isfinite(v) or v <= 0:
            raise Refused('Missing/invalid budget: ' + key)
    if type(limits['max_dispatches']) is not int or type(limits['max_output_bytes']) is not int:
        raise Refused('Counts/byte limits must be integers')
    if limits['model_calls'] != 0 or limits['remote_jobs'] != 0:
        raise Refused('Model/remote budgets are fixed at zero')
    tasks = config['tasks']
    if not isinstance(tasks, list) or not tasks:
        raise Refused('Nonempty task graph required')
    ids = []
    for task in tasks:
        if not isinstance(task, dict) or set(task) != TASK_FIELDS:
            raise Refused('Unknown/missing task fields')
        ident = task['id']
        if not isinstance(ident, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,63}', ident):
            raise Refused('Invalid task ID')
        if 'task4' in re.sub('[^a-z0-9]', '', ident.lower()):
            raise Refused('Historical Task4 and aliases excluded')
        ids.append(ident)
        if task['operation'] != 'synthetic.report':
            raise Refused('Unimplemented or excluded operation; research handlers do not exist')
        if task['authorization_requirement'] != 'SYNTHETIC_ONLY' or task['acceptance_checks'] != CHECKS:
            raise Refused('Policy/review weakening refused')
        if task['outputs'] != ['report.json'] or type(task['idempotent']) is not bool:
            raise Refused('Invalid output/operation contract')
        arguments(task['arguments'])
        resource = task['resource_limits']
        if not isinstance(resource, dict) or set(resource) != {'timeout_seconds', 'max_attempts', 'repair_retries'}:
            raise Refused('Task resource limits required')
        if type(resource['timeout_seconds']) not in (int, float) or not math.isfinite(resource['timeout_seconds']) or not 0 < resource['timeout_seconds'] <= 10:
            raise Refused('Invalid timeout')
        if type(resource['repair_retries']) is not int or not 0 <= resource['repair_retries'] <= 2:
            raise Refused('At most two automatic technical repair retries')
        if type(resource['max_attempts']) is not int or not 1 <= resource['max_attempts'] <= 3:
            raise Refused('At most three total work attempts')
        if not isinstance(task['depends_on'], list) or any(not isinstance(x, str) for x in task['depends_on']):
            raise Refused('Invalid dependencies')
        if not isinstance(task['inputs'], list) or not task['inputs']:
            raise Refused('Explicit input evidence required')
        for item in task['inputs']:
            if not isinstance(item, dict) or set(item) != {'path', 'sha256'} or not re.fullmatch('[0-9a-f]{64}', item['sha256']):
                raise Refused('Invalid input identity')
    if len(set(ids)) != len(ids):
        raise Refused('Duplicate task IDs')
    graph = {t['id']: t['depends_on'] for t in tasks}
    visited, active = set(), set()
    def visit(ident):
        if ident not in graph or ident in active:
            raise Refused('Missing dependency or dependency cycle')
        if ident in visited:
            return
        active.add(ident)
        for dep in graph[ident]:
            visit(dep)
        active.remove(ident); visited.add(ident)
    for ident in ids:
        visit(ident)


def fixture_signature(payload):
    """Public synthetic test signature; NEVER a live authorization mechanism."""
    return hmac.new(FIXTURE_KEY, canonical(payload), hashlib.sha256).hexdigest()


def fixture_authorization(root, config):
    return {'kind': MARKER, 'issuer': 'SYNTHETIC_AUTHORITY', 'revoked': False,
            'expires_utc': '2099-01-01T00:00:00+00:00',
            'protocol_version': config['protocol_version'], 'config_sha256': hashlib.sha256(canonical(config)).hexdigest(),
            'code': code_identity(), 'scope': [t['id'] for t in config['tasks']],
            'operations': ['synthetic.report'], 'access': 'synthetic-local-only',
            'write_scope': str(root.relative_to(BUILD)), 'resource_limits': config['limits']}


def verify_authorization(root, config):
    record = read(root, 'fixture_authorization.json')
    if not isinstance(record, dict) or set(record) != {'payload', 'signature'}:
        raise Refused('Missing/malformed fixture authorization')
    p = record['payload']
    expected = fixture_authorization(root, config)
    if not isinstance(p, dict) or set(p) != set(expected):
        raise Refused('Malformed authorization payload')
    if not isinstance(record['signature'], str) or not hmac.compare_digest(record['signature'], fixture_signature(p)):
        raise Refused('Agent-forged/malformed fixture signature')
    if p.get('kind') != MARKER or p.get('issuer') != 'SYNTHETIC_AUTHORITY' or p.get('revoked') is not False:
        raise Refused('Revoked or untrusted authorization')
    try:
        expires = datetime.fromisoformat(p['expires_utc'])
        if expires.tzinfo is None or expires <= datetime.now(timezone.utc):
            raise Refused('Expired fixture authorization')
    except (ValueError, TypeError) as exc:
        raise Refused('Malformed authorization expiry') from exc
    # Expiration may be shortened by the fixture authority; every other binding exact.
    expected['expires_utc'] = p['expires_utc']
    if p != expected:
        raise Refused('Authorization scope/protocol/code/access/write/budget mismatch')


class Journal:
    def __init__(self, root):
        self.root = root
        self.seq = 0
        self.previous = '0'*64
        self.state = None

    def load(self):
        p = confined(self.root, '.controller/events.jsonl')
        if not p.exists():
            raise Refused('Runtime not initialized')
        raw = p.read_bytes()
        if not raw or not raw.endswith(b'\n'):
            raise Refused('Incomplete event log: preserve and reconcile; no silent truncation')
        for line in raw.splitlines():
            e = decode(line)
            if not isinstance(e, dict) or set(e) != {'seq', 'previous', 'utc', 'event', 'state', 'sha256'}:
                raise Refused('Invalid event schema')
            value = {k:v for k,v in e.items() if k != 'sha256'}
            actual = hashlib.sha256(canonical(value)).hexdigest()
            if e['seq'] != self.seq+1 or e['previous'] != self.previous or actual != e['sha256']:
                raise Refused('Event log chain invalid')
            self.seq += 1; self.previous = actual; self.state = e['state']
        return self.state

    def commit(self, state, event):
        value = {'seq': self.seq+1, 'previous': self.previous, 'utc': utc(),
                 'event': event, 'state': copy.deepcopy(state)}
        value['sha256'] = hashlib.sha256(canonical(value)).hexdigest()
        p = confined(self.root, '.controller/events.jsonl')
        fd = os.open(p, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'ab') as f:
            f.write(canonical(value)+b'\n'); f.flush(); os.fsync(f.fileno())
        # Journal is write-ahead authority for recovery; snapshot is only a cache.
        atomic(self.root, '.controller/state.json', value['state'])
        self.seq += 1; self.previous = value['sha256']; self.state = value['state']


def synthetic_task(ident='prepare', dependencies=None, scenario='success'):
    return {'id': ident, 'depends_on': dependencies or [], 'operation': 'synthetic.report',
            'authorization_requirement': 'SYNTHETIC_ONLY', 'inputs': [], 'outputs': ['report.json'],
            'acceptance_checks': CHECKS.copy(), 'resource_limits': {'timeout_seconds': 1.0, 'max_attempts': 3, 'repair_retries': 2},
            'arguments': {'scenario': scenario, 'delay': 0.0}, 'idempotent': True}


def initialize(path, config=None):
    root = run_root(path)
    if root.exists():
        raise Refused('Existing runtime is preserved; use status/preview/resume')
    root.mkdir(parents=True, exist_ok=False)
    (root/'.controller').mkdir()
    atomic(root, 'input.json', {'kind': MARKER, 'description': 'Tiny synthetic orchestration input; no samples'})
    if config is None:
        tasks = [synthetic_task('prepare'), synthetic_task('implement', ['prepare'], 'negative'), synthetic_task('handoff', ['implement'])]
        config = {'kind': MARKER, 'protocol_version': 'SYNTHETIC-1',
                  'limits': {'max_dispatches': 20, 'wall_seconds': 30, 'max_output_bytes': 65536, 'model_calls': 0, 'remote_jobs': 0}, 'tasks': tasks}
    config = copy.deepcopy(config)
    for task in config['tasks']:
        if not task['inputs']:
            task['inputs'] = [{'path': 'input.json', 'sha256': digest(root/'input.json')}]
    validate_config(config)
    for task in config['tasks']:
        for item in task['inputs']:
            confined(root, item['path'])
    atomic(root, 'workflow.json', config)
    auth = fixture_authorization(root, config)
    atomic(root, 'fixture_authorization.json', {'payload': auth, 'signature': fixture_signature(auth)})
    state = {'kind': MARKER, 'execution_status': 'READY', 'config_sha256': hashlib.sha256(canonical(config)).hexdigest(),
             'code': code_identity(), 'dispatches': 0, 'reserved_seconds': 0.0, 'measured_child_seconds': 0.0,
             'tasks': {t['id']: {'execution_status': 'PENDING', 'authorization_status': 'UNCHECKED',
                       'evidence_status': 'UNVERIFIED', 'attempts': [], 'checks': [], 'reason': ''} for t in config['tasks']}}
    with locked(root, 'writer.lock', True):
        Journal(root).commit(state, 'initialized_synthetic_fixture')
    return state


class Runner:
    def __init__(self, path):
        self.root = run_root(path)
        self.journal = Journal(self.root)
        self.state = self.journal.load()
        self.config = read(self.root, 'workflow.json')
        validate_config(self.config)
        self.adapter = FakeAdapter()
        self.signalled = False

    def commit(self, event):
        self.journal.commit(self.state, event)

    def preflight(self):
        if self.state.get('kind') != MARKER or self.state['config_sha256'] != hashlib.sha256(canonical(self.config)).hexdigest() or self.state['code'] != code_identity():
            raise Refused('Configuration/code identity drift')
        verify_authorization(self.root, self.config)
        for task in self.config['tasks']:
            for item in task['inputs']:
                p = confined(self.root, item['path'])
                if not p.is_file() or digest(p) != item['sha256'] or read(self.root, item['path']).get('kind') != MARKER:
                    raise Refused('Input identity/type drift')
        return True

    def stop_requested(self):
        return self.signalled or confined(self.root, '.controller/STOP.json').exists()

    def dispatch(self, role, task, attempt, folder):
        timeout = task['resource_limits']['timeout_seconds']
        limits = self.config['limits']
        with locked(self.root, 'control.lock'):
            self.preflight()
            if self.stop_requested():
                raise Refused('STOP_REQUESTED')
            if self.state['dispatches'] >= limits['max_dispatches'] or self.state['reserved_seconds']+timeout > limits['wall_seconds']:
                raise Refused('BUDGET_EXHAUSTED')
            argv = self.adapter.argv(role, task, attempt, confined(self.root, task['inputs'][0]['path']))
            args_check = arguments(task['arguments'])
            self.state['dispatches'] += 1; self.state['reserved_seconds'] += timeout
            ts = self.state['tasks'][task['id']]
            ts['phase'] = 'DISPATCH_INTENT'
            self.commit('dispatch_intent_'+role)  # Count/reserve even if fork or controller fails.
            stdout = confined(self.root, str(folder.relative_to(self.root))+'/'+role+'_stdout.json')
            stderr = confined(self.root, str(folder.relative_to(self.root))+'/'+role+'_stderr.txt')
            start = time.monotonic()
            with stdout.open('xb') as of, stderr.open('xb') as ef:
                proc = subprocess.Popen(argv, cwd=folder, stdin=subprocess.DEVNULL, stdout=of, stderr=ef,
                                        env={'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'PYTHONDONTWRITEBYTECODE': '1'}, start_new_session=True)
            ts['active_child'] = {'pid': proc.pid, 'role': role, 'started_utc': utc()}
            self.commit('child_started_'+role)
        reason = None
        try:
            while proc.poll() is None:
                if self.stop_requested(): reason = 'STOP_REQUESTED'
                elif time.monotonic()-start > timeout: reason = 'TIMEOUT'
                elif stdout.stat().st_size+stderr.stat().st_size > limits['max_output_bytes']: reason = 'OUTPUT_BUDGET_EXHAUSTED'
                if reason:
                    os.killpg(proc.pid, signal.SIGTERM)
                    try: proc.wait(timeout=.2)
                    except subprocess.TimeoutExpired:
                        os.killpg(proc.pid, signal.SIGKILL); proc.wait()
                    break
                time.sleep(.01)
            proc.wait()
        finally:
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGKILL); proc.wait()
        seconds = time.monotonic()-start
        self.state['measured_child_seconds'] += seconds
        ts.pop('active_child', None)
        record = {'role': role, 'argv': argv, 'cwd': str(folder.relative_to(self.root)), 'exit_code': proc.returncode,
                  'utc': utc(), 'measured_seconds': seconds, 'reserved_seconds': timeout,
                  'reason': reason, 'stdout_sha256': digest(stdout), 'stderr_sha256': digest(stderr)}
        atomic(self.root, str(folder.relative_to(self.root))+'/'+role+'_execution.json', record)
        self.commit('child_finished_'+role)
        if stdout.stat().st_size+stderr.stat().st_size > limits['max_output_bytes']:
            reason = 'OUTPUT_BUDGET_EXHAUSTED'
        if reason:
            return None, reason, reason == 'TIMEOUT'
        if proc.returncode:
            return None, 'NONZERO_'+str(proc.returncode), proc.returncode == 75
        try:
            return decode(stdout.read_bytes()), None, False
        except Refused:
            return None, 'MALFORMED_RESPONSE', False

    def evidence(self, task, folder, receipt):
        if not isinstance(receipt, dict) or set(receipt) != {'status', 'artifacts'} or receipt['status'] != 'DONE':
            raise Refused('Fabricated or malformed DONE response')
        if not isinstance(receipt['artifacts'], list) or len(receipt['artifacts']) != 1:
            raise Refused('Missing required output')
        a = receipt['artifacts'][0]
        if not isinstance(a, dict) or set(a) != {'path', 'sha256'} or a['path'] != 'report.json':
            raise Refused('Unauthorized artifact path')
        p = confined(self.root, str(folder.relative_to(self.root))+'/'+a['path'])
        if not p.is_file() or digest(p) != a['sha256']:
            raise Refused('Artifact missing/hash inconsistent')
        data = decode(p.read_bytes())
        if not isinstance(data, dict) or data.get('kind') != MARKER or data.get('task_id') != task['id']:
            raise Refused('Artifact identity invalid')
        if data.get('method_valid') is not True or data.get('outcome') not in ['negative', 'positive', 'inconclusive']:
            raise Refused('Acceptance validity failed; score direction irrelevant')
        if data.get('input_sha256') != task['inputs'][0]['sha256']:
            raise Refused('Artifact input identity mismatch')
        return a['sha256']

    def review(self, response, sha):
        if not isinstance(response, dict) or set(response) != {'decision', 'reviewer', 'inspected_sha256', 'checks'}:
            raise Refused('Malformed review')
        if response['decision'] != 'ACCEPT' or response['reviewer'] != 'separate_fake_process':
            raise Refused('Failed or SELF_REVIEW_ONLY does not satisfy separate-review gate')
        if response['inspected_sha256'] != sha or response['checks'] != {'marker': True, 'identity': True, 'validity': True, 'input': True}:
            raise Refused('Reviewer did not establish the required evidence checks')

    def validate_done(self, task):
        ts = self.state['tasks'][task['id']]
        folder = confined(self.root, ts['artifact_directory'])
        sha = self.evidence(task, folder, read(self.root, ts['artifact_directory']+'/worker_stdout.json'))
        self.review(read(self.root, ts['artifact_directory']+'/reviewer_stdout.json'), sha)
        if ts.get('artifact_sha256') != sha:
            raise Refused('Prior completed artifact changed')

    def progress(self):
        lines = ['# Synthetic orchestration progress', '', 'Input -> registered fake work -> report.json -> independently checked fake review -> conclusion -> uncertainty.',
                 '', 'This is not research or a live Codex connection. Reservations bound dispatch wall-time; measured child time is separately recorded. Monetary usage is not estimated.']
        for ident, ts in self.state['tasks'].items():
            lines.append(f"\n- {ident}: {ts['execution_status']}; evidence {ts['evidence_status']}; authorization {ts['authorization_status']}; {ts['reason']}")
        atomic(self.root, '.controller/progress.json', {'kind': MARKER, 'teaching': '\n'.join(lines), 'state': self.state})

    def run(self, resume=False, clear_stop=False):
        with locked(self.root, 'writer.lock', True):
            # Re-read after acquiring exclusive writer lock, never use a stale in-memory snapshot.
            self.journal = Journal(self.root); self.state = self.journal.load()
            try:
                self.preflight()
            except (Refused, OSError) as exc:
                self.state['execution_status'] = 'BLOCKED'; self.state['reason'] = str(exc)
                self.commit('preflight_rejected'); return self.state
            if clear_stop:
                if not resume:
                    raise Refused('Only explicit resume may clear a stop')
                with locked(self.root, 'control.lock'):
                    p = confined(self.root, '.controller/STOP.json')
                    if p.exists():
                        archive = confined(self.root, '.controller/stop_history/'+uuid.uuid4().hex+'.json')
                        archive.parent.mkdir(exist_ok=True); os.replace(p, archive)
            for task in self.config['tasks']:
                ts = self.state['tasks'][task['id']]
                if ts['execution_status'] == 'DONE':
                    try: self.validate_done(task)
                    except (Refused, OSError) as exc:
                        ts.update(execution_status='NEEDS_RECONCILIATION', evidence_status='INVALID', reason=str(exc))
                elif ts['execution_status'] == 'RUNNING':
                    ts.update(execution_status='NEEDS_RECONCILIATION', reason='Interrupted/possibly completed work; no automatic replay')
            self.commit('resume_revalidated' if resume else 'run_revalidated')
            for task in self.config['tasks']:
                ts = self.state['tasks'][task['id']]
                if ts['execution_status'] != 'PENDING': continue
                if self.stop_requested(): break
                if any(self.state['tasks'][d]['execution_status'] != 'DONE' for d in task['depends_on']):
                    ts.update(execution_status='BLOCKED', reason='Dependency incomplete/blocked'); self.commit('dependency_blocked'); continue
                resource = task['resource_limits']
                for attempt in range(1, resource['max_attempts']+1):
                    ts.update(execution_status='RUNNING', authorization_status='VERIFIED_SYNTHETIC_ONLY', evidence_status='UNVERIFIED')
                    ts['attempts'].append({'number': attempt, 'started_utc': utc()})
                    folder = confined(self.root, 'work/'+task['id']+'/attempt'+str(attempt))
                    folder.mkdir(parents=True, exist_ok=False)
                    self.commit('work_attempt_started')
                    technical = False
                    try:
                        output, reason, technical = self.dispatch('worker', task, attempt, folder)
                        if reason: raise Refused(reason)
                        sha = self.evidence(task, folder, output)
                        ts['phase'] = 'REVIEW_PENDING'; self.commit('worker_evidence_checked')
                        review, reason, _ = self.dispatch('reviewer', task, attempt, folder)
                        if reason: raise Refused(reason)
                        self.review(review, sha)
                        ts.update(execution_status='DONE', evidence_status='VERIFIED_SYNTHETIC_ONLY', checks=CHECKS.copy(),
                                  artifact_directory=str(folder.relative_to(self.root)), artifact_sha256=sha, reason='Valid evidence, including negative results, accepted')
                        self.commit('task_completed_after_review'); break
                    except (Refused, OSError) as exc:
                        reason = str(exc)
                        ts['attempts'][-1].update(reason=reason, technical=technical)
                        retry = technical and task['idempotent'] and attempt <= resource['repair_retries'] and attempt < resource['max_attempts'] and not self.stop_requested()
                        ts.update(execution_status='RUNNING' if retry else ('NEEDS_RECONCILIATION' if reason == 'STOP_REQUESTED' else 'FAILED'), reason=reason)
                        self.commit('technical_retry' if retry else 'attempt_failed')
                        if not retry: break
            statuses = [x['execution_status'] for x in self.state['tasks'].values()]
            self.state['execution_status'] = 'DONE' if all(s == 'DONE' for s in statuses) else ('STOPPED' if self.stop_requested() else 'BLOCKED')
            self.commit('coordinator_stopped'); self.progress()
            return self.state


def request_stop(path):
    root = run_root(path)
    with locked(root, 'control.lock'):
        atomic(root, '.controller/STOP.json', {'requested_utc': utc(), 'action': 'prevent new launches; active fixed child process group terminated by coordinator'})
    return {'stop_requested': True, 'scope': MARKER}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare-demo', 'status', 'preview', 'run', 'resume', 'stop', 'activate'])
    parser.add_argument('--root', type=Path, default=BUILD/'runtime/demo')
    parser.add_argument('--research', action='store_true')
    parser.add_argument('--clear-stop', action='store_true')
    parser.add_argument('--scope', choices=['LITERATURE'])
    args = parser.parse_args()
    try:
        if args.command == 'activate':
            CodexAdapter().execute()
        if args.research:
            if args.command not in ['status', 'preview']:
                raise Refused('Research queue is read-only and has no implemented handlers')
            result = decode((BUILD/'config/derived_queue.json').read_bytes())
        elif args.command == 'prepare-demo': result = initialize(args.root)
        elif args.command == 'stop': result = request_stop(args.root)
        else:
            runner = Runner(args.root)
            if args.command in ['status', 'preview']:
                result = {'kind': MARKER, 'state': runner.state, 'stop_requested': runner.stop_requested(), 'live_enabled': False}
                if args.command == 'preview':
                    try: runner.preflight(); result['preflight'] = 'VALID_SYNTHETIC_ONLY'
                    except (Refused, OSError) as exc: result['preflight'] = 'BLOCKED: '+str(exc)
                    result['planned_operations'] = [t['operation'] for t in runner.config['tasks']]
            else:
                def interrupt(*unused): runner.signalled = True
                signal.signal(signal.SIGINT, interrupt); signal.signal(signal.SIGTERM, interrupt)
                result = runner.run(args.command == 'resume', args.clear_stop)
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except (Refused, OSError, KeyError, TypeError) as exc:
        print(json.dumps({'status': 'REFUSED', 'reason': str(exc), 'live_enabled': False}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
