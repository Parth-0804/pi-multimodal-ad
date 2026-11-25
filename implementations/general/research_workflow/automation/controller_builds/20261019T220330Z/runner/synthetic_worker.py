"""Fixed, trusted synthetic subprocess fixture. Never imports the thesis project."""
import hashlib
import json
from pathlib import Path
import sys
import time

MARKER = 'SYNTHETIC_ORCHESTRATION_TEST'
role, task, scenario, delay, attempt, input_name = sys.argv[1:]
time.sleep(float(delay))
if role == 'worker':
    if scenario == 'timeout':
        time.sleep(5)
    if scenario == 'nonzero':
        raise SystemExit(17)
    if scenario == 'technical_failure' or (scenario == 'flaky' and int(attempt) == 1):
        raise SystemExit(75)
    if scenario == 'malformed':
        print('not JSON'); raise SystemExit(0)
    if scenario in ('missing_output', 'fabricated_done'):
        print(json.dumps({'status': 'DONE', 'artifacts': []})); raise SystemExit(0)
    data = json.loads(Path(input_name).read_text())
    assert data.get('kind') == MARKER
    result = {'kind': MARKER, 'task_id': task, 'method_valid': scenario != 'invalid_high_score',
              'outcome': 'negative' if scenario == 'negative' else 'inconclusive',
              'input_sha256': hashlib.sha256(Path(input_name).read_bytes()).hexdigest()}
    # Score is deliberately irrelevant to validity; invalid high-score fixture must fail.
    if scenario == 'invalid_high_score':
        result['score'] = 1.0
    Path('report.json').write_text(json.dumps(result, sort_keys=True) + '\n')
    digest = hashlib.sha256(Path('report.json').read_bytes()).hexdigest()
    print(json.dumps({'status': 'DONE', 'artifacts': [{'path': 'report.json',
                      'sha256': '0'*64 if scenario == 'hash_mismatch' else digest}]}))
else:
    raw = Path('report.json').read_bytes()
    data = json.loads(raw)
    checks = {'marker': data.get('kind') == MARKER, 'identity': data.get('task_id') == task,
              'validity': data.get('method_valid') is True,
              'input': data.get('input_sha256') == hashlib.sha256(Path(input_name).read_bytes()).hexdigest()}
    print(json.dumps({'decision': 'ACCEPT' if all(checks.values()) and scenario != 'review_reject' else 'REJECT',
                      'reviewer': 'SELF_REVIEW_ONLY' if scenario == 'self_review' else 'separate_fake_process',
                      'inspected_sha256': hashlib.sha256(raw).hexdigest(), 'checks': checks}))
