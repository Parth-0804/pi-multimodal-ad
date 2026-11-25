"""Session-local no-work contracts; imports only the copied synthetic runner."""
from pathlib import Path
import json
import subprocess
import sys
import unittest
import uuid
from unittest.mock import patch

BUILD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD / 'runner'))
import controller as c


class NoWorkTests(unittest.TestCase):
    def test_completed_resume_dispatches_nothing(self):
        root = BUILD / 'evidence/test_work' / ('no-work-' + uuid.uuid4().hex)
        c.initialize(root)
        before = c.Runner(root).run()
        self.assertEqual(before['execution_status'], 'DONE')
        with patch.object(c.FakeAdapter, 'argv', side_effect=AssertionError('Unexpected launch')):
            after = c.Runner(root).run(resume=True)
        self.assertEqual(after['execution_status'], 'DONE')
        self.assertEqual(after['dispatches'], before['dispatches'])
        self.assertEqual(after['measured_child_seconds'], before['measured_child_seconds'])

    def test_status_preview_are_read_only_and_empty_queue_refused(self):
        root = BUILD / 'evidence/test_work' / ('preview-' + uuid.uuid4().hex)
        c.initialize(root)
        files = {p.relative_to(root): c.digest(p) for p in root.rglob('*') if p.is_file()}
        for command in ['status', 'preview']:
            result = subprocess.run([sys.executable, '-I', '-B', str(BUILD / 'runner/controller.py'),
                                     command, '--root', str(root)], capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['state']['dispatches'], 0)
        self.assertEqual(files, {p.relative_to(root): c.digest(p) for p in root.rglob('*') if p.is_file()})
        cfg = c.read(root, 'workflow.json')
        cfg['tasks'] = []
        with self.assertRaisesRegex(c.Refused, 'Nonempty task graph'):
            c.validate_config(cfg)


if __name__ == '__main__':
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(NoWorkTests))
    raise SystemExit(0 if result.wasSuccessful() else 1)
