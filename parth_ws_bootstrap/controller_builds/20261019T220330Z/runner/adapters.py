"""Typed boundaries. No command supplied by a model/report is executable here."""
from pathlib import Path
import sys

MARKER = 'SYNTHETIC_ORCHESTRATION_TEST'
SCENARIOS = frozenset({'success', 'negative', 'invalid_high_score', 'missing_output',
                       'fabricated_done', 'hash_mismatch', 'malformed', 'nonzero',
                       'technical_failure', 'flaky', 'timeout', 'review_reject', 'self_review'})


class Refused(ValueError):
    pass


def arguments(value):
    if not isinstance(value, dict) or set(value) != {'scenario', 'delay'}:
        raise Refused('Only registered scenario/delay arguments allowed')
    if value['scenario'] not in SCENARIOS:
        raise Refused('Unregistered scenario or command')
    if type(value['delay']) not in (int, float) or not 0 <= value['delay'] <= 5:
        raise Refused('Invalid synthetic delay')
    return value


class FakeAdapter:
    """Known local synthetic worker/reviewer only; no project imports or network."""
    name = 'fake'

    def argv(self, role, task, attempt, input_path):
        arguments(task['arguments'])
        if role not in ('worker', 'reviewer') or type(attempt) is not int or attempt < 1:
            raise Refused('Invalid registered dispatch')
        return [sys.executable, '-I', '-B', str(Path(__file__).with_name('synthetic_worker.py')),
                role, task['id'], task['arguments']['scenario'], str(task['arguments']['delay']),
                str(attempt), str(input_path)]


class CodexAdapter:
    """Inspected interface, intentionally inoperable until an external host gate exists.

    Changing JSON, state, a chmod bit, or a worker verdict cannot activate this class.
    A later approved integration must add a host-owned launcher and real handlers.
    """
    name = 'codex-disabled'

    def prepare_argv(self, executable, cwd, schema, output, model):
        if not isinstance(model, str) or not model or model.startswith('-') or len(model) > 128:
            raise Refused('An explicitly approved model identity is required')
        paths = [executable, cwd, schema, output]
        if any(not isinstance(p, Path) or not p.is_absolute() for p in paths):
            raise Refused('Launcher must supply confined absolute Path arguments')
        return [str(executable), 'exec', '--sandbox', 'read-only', '--json',
                '--output-schema', str(schema), '--output-last-message', str(output),
                '-C', str(cwd), '--model', model, '-']

    def execute(self, *args, **kwargs):
        raise Refused('LIVE_DISABLED: external host-enforced authority/isolation, budgets '
                      'and registered research handlers are not provisioned')
