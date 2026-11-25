"""Tiny synthetic safety checks; no dataset/model/process fixtures."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("boundary_guard", Path(__file__).with_name("boundary_guard.py"))
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class SafetyTests(unittest.TestCase):
    def test_lock_prevents_configuration_and_later_fits(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "next/FIT.lock"
            held = guard.acquire(path)
            calls = []
            try:
                with self.assertRaises(BlockingIOError):
                    for name in ("next", "later"):
                        lock = guard.acquire(Path(d) / name / "FIT.lock")
                        calls.append(name)
                        lock.close()
                self.assertEqual(calls, [])
                self.assertEqual([p.name for p in path.parent.iterdir()], ["FIT.lock"])
            finally:
                held.close()

    def test_reused_pid_and_changed_command_are_rejected(self):
        base = {"pid": 1, "start_ticks": 100, "cmdline": ["synthetic.py"], "cwd": "/synthetic", "state": "S"}
        self.assertTrue(guard.same_process(base, dict(base)))
        for changed in ({"start_ticks": 101}, {"cmdline": ["other.py"]}, {"cwd": "/other"}, {"state": "Z"}):
            self.assertFalse(guard.same_process(base, {**base, **changed}))

    def test_signal_is_not_sent_to_changed_process(self):
        expected = {"pid": 1}
        with patch.object(guard.os, "pidfd_open", return_value=9), patch.object(guard, "alive", return_value=False), \
             patch.object(guard.os, "close"), patch.object(guard.signal, "pidfd_send_signal") as send:
            self.assertFalse(guard.send(expected, guard.signal.SIGINT))
            send.assert_not_called()

    def test_missing_completion_is_not_complete(self):
        with tempfile.TemporaryDirectory() as d, patch.object(guard, "STUDY", Path(d)):
            self.assertIsNone(guard.completed_target({"target_fit": "synthetic"}))
            p = Path(d) / "synthetic"
            p.mkdir()
            (p / "COMPLETE.json").write_text(json.dumps({"condition": "FULL20", "seed": 42,
                "fit_id": "outer0_inner2", "executed_epochs": 19}))
            with self.assertRaisesRegex(ValueError, "executed_epochs"):
                guard.completed_target({"target_fit": "synthetic"})

    def test_elapsed_deadline_launches_nothing(self):
        with patch.object(guard.subprocess, "Popen") as launch:
            value = guard.bounded_command(["synthetic"], 0, "never.log")
            self.assertEqual(value["status"], "NOT_RUN_DEADLINE_REACHED")
            launch.assert_not_called()

    def test_timeout_terminates_only_owned_analysis_child(self):
        with tempfile.TemporaryDirectory() as d, patch.object(guard, "HERE", Path(d)), \
             patch.object(guard.subprocess, "Popen") as launch, patch.object(guard, "send") as external_signal:
            child = launch.return_value
            child.pid = 123
            child.wait.side_effect = [guard.subprocess.TimeoutExpired(["synthetic"], .01), 0]
            value = guard.bounded_command(["synthetic"], guard.time.time()+.01, "synthetic.log")
            self.assertEqual(value["status"], "STOPPED_AT_THREE_HOUR_DEADLINE")
            child.terminate.assert_called_once()
            child.kill.assert_not_called()
            external_signal.assert_not_called()


if __name__ == "__main__":
    unittest.main()
