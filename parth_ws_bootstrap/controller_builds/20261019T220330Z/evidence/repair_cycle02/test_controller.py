"""Targeted offline controller checks. No repository discovery/hooks or real samples."""
from pathlib import Path
import copy
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
import unittest
import uuid

BUILD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD/'runner'))
import controller as c
from adapters import CodexAdapter, FakeAdapter, Refused
WORK = BUILD/'evidence/test_work'
WORK.mkdir(exist_ok=True)


class OfflineControllerTests(unittest.TestCase):
    def fresh(self, scenario='success', modify=None):
        root = WORK/uuid.uuid4().hex
        task = c.synthetic_task('first', scenario=scenario)
        config = {'kind': c.MARKER, 'protocol_version': 'SYNTHETIC-1',
                  'limits': {'max_dispatches': 20, 'wall_seconds': 30, 'max_output_bytes': 65536, 'model_calls': 0, 'remote_jobs': 0},
                  'tasks': [task, c.synthetic_task('second', ['first'])]}
        if modify: modify(config)
        c.initialize(root, config)
        return root

    def run_case(self, scenario='success', modify=None):
        root = self.fresh(scenario, modify)
        state = c.Runner(root).run()
        return root, state

    def auth(self, root, mutate, resign=True):
        record = c.read(root, 'fixture_authorization.json')
        mutate(record['payload'])
        if resign: record['signature'] = c.fixture_signature(record['payload'])
        c.atomic(root, 'fixture_authorization.json', record)

    def test_01_dependencies_review_handoff_and_no_duplicates(self):
        root, state = self.run_case()
        self.assertEqual(state['execution_status'], 'DONE')
        self.assertEqual(state['dispatches'], 4)
        again = c.Runner(root).run(resume=True)
        self.assertEqual(again['dispatches'], 4)
        self.assertEqual(again['tasks']['second']['checks'], c.CHECKS)
        events = [json.loads(x)['event'] for x in (root/'.controller/events.jsonl').read_text().splitlines()]
        self.assertEqual(events.count('task_completed_after_review'), 2)
        self.assertEqual(events.count('child_started_reviewer'), 2)

    def test_02_missing_authorization_rejected_without_dispatch(self):
        root = self.fresh()
        os.replace(root/'fixture_authorization.json', root/'preserved_missing_auth.json')
        state = c.Runner(root).run()
        self.assertEqual(state['execution_status'], 'BLOCKED'); self.assertEqual(state['dispatches'], 0)

    def test_03_malformed_authorization(self):
        root = self.fresh(); c.atomic(root, 'fixture_authorization.json', {'agent_says_approved': True})
        self.assertEqual(c.Runner(root).run()['dispatches'], 0)

    def test_04_revoked_authorization_even_with_fixture_signature(self):
        root = self.fresh(); self.auth(root, lambda p:p.update(revoked=True))
        self.assertEqual(c.Runner(root).run()['execution_status'], 'BLOCKED')

    def test_05_mismatched_scope_protocol_access_writes_budget(self):
        for key, value in [('scope', ['other']), ('protocol_version', 'OTHER'), ('access', 'network'), ('write_scope', '../outside'), ('resource_limits', {})]:
            with self.subTest(binding=key):
                root = self.fresh(); self.auth(root, lambda p:p.update({key:value}))
                self.assertEqual(c.Runner(root).run()['dispatches'], 0)

    def test_06_agent_forged_or_expired_authorization(self):
        for field, value, resign in [('issuer', 'agent', True), ('scope', ['agent-approved'], False), ('expires_utc', '2000-01-01T00:00:00+00:00', True)]:
            with self.subTest(field=field):
                root = self.fresh(); self.auth(root, lambda p:p.update({field:value}), resign)
                self.assertEqual(c.Runner(root).run()['dispatches'], 0)

    def test_07_graph_missing_dependency_cycle_duplicate(self):
        for mode in ['missing', 'cycle', 'duplicate']:
            with self.subTest(mode=mode):
                def change(cfg):
                    if mode == 'missing':cfg['tasks'][0]['depends_on']=['absent']
                    if mode == 'cycle':cfg['tasks'][0]['depends_on']=['second']
                    if mode == 'duplicate':cfg['tasks'][1]['id']='first'
                with self.assertRaises(Refused):self.fresh(modify=change)

    def test_08_missing_budgets_and_excluded_or_unimplemented_tasks(self):
        changes = [lambda x:x['limits'].update(wall_seconds=None),
                   lambda x:x['tasks'][0].update(id='historical-Task_4'),
                   lambda x:x['tasks'][0].update(operation='renamed.corruption.training'),
                   lambda x:x['limits'].update(model_calls=1)]
        for change in changes:
            with self.assertRaises(Refused):self.fresh(modify=change)

    def test_09_fabricated_done_missing_output_and_hash_mismatch(self):
        for scenario in ['fabricated_done', 'missing_output', 'hash_mismatch']:
            with self.subTest(scenario=scenario):
                root, state = self.run_case(scenario)
                self.assertEqual(state['tasks']['first']['execution_status'], 'FAILED')
                self.assertEqual(state['tasks']['second']['execution_status'], 'BLOCKED')
                self.assertEqual(state['dispatches'], 1)

    def test_10_reviewer_reject_or_self_review_does_not_advance(self):
        for scenario in ['review_reject', 'self_review']:
            root, state = self.run_case(scenario)
            self.assertEqual(state['tasks']['first']['execution_status'], 'FAILED')
            self.assertEqual(state['tasks']['second']['execution_status'], 'BLOCKED')
            self.assertEqual(state['dispatches'], 2)

    def test_11_timeout_has_bounded_retries_and_saves_failure(self):
        def change(cfg):cfg['tasks'][0]['resource_limits']['timeout_seconds']=.08
        root, state = self.run_case('timeout', change)
        self.assertEqual(len(state['tasks']['first']['attempts']), 3)
        self.assertEqual(state['tasks']['first']['reason'], 'TIMEOUT')
        self.assertEqual(state['tasks']['second']['execution_status'], 'BLOCKED')
        self.assertEqual(c.Journal(root).load()['dispatches'], 3)

    def test_12_malformed_and_nonzero_are_not_score_retries(self):
        for scenario in ['malformed', 'nonzero']:
            root, state = self.run_case(scenario)
            self.assertEqual(len(state['tasks']['first']['attempts']), 1)
            self.assertEqual(state['tasks']['second']['execution_status'], 'BLOCKED')

    def test_13_technical_retry_succeeds_and_is_accounted(self):
        root, state = self.run_case('flaky')
        self.assertEqual(state['execution_status'], 'DONE')
        self.assertEqual(len(state['tasks']['first']['attempts']), 2)
        self.assertEqual(state['dispatches'], 5)
        self.assertGreater(state['reserved_seconds'], state['measured_child_seconds'])

    def test_14_technical_failure_exhausts_two_repairs(self):
        root, state = self.run_case('technical_failure')
        self.assertEqual(len(state['tasks']['first']['attempts']), 3)
        self.assertEqual(state['tasks']['first']['reason'], 'NONZERO_75')
        with self.assertRaises(Refused):self.fresh(modify=lambda x:x['tasks'][0]['resource_limits'].update(repair_retries=3))

    def test_15_dispatch_budget_exhaustion_includes_reviewer(self):
        root, state = self.run_case(modify=lambda x:x['limits'].update(max_dispatches=1))
        self.assertEqual(state['dispatches'], 1)
        self.assertEqual(state['tasks']['first']['reason'], 'BUDGET_EXHAUSTED')
        self.assertEqual(state['tasks']['second']['execution_status'], 'BLOCKED')

    def test_16_wall_reservation_and_output_budgets(self):
        for limits in [{'wall_seconds': .5}, {'max_output_bytes': 10}]:
            root, state = self.run_case(modify=lambda x:x['limits'].update(limits))
            self.assertNotEqual(state['tasks']['first']['execution_status'], 'DONE')
            self.assertIn('BUDGET_EXHAUSTED', state['tasks']['first']['reason'])

    def test_17_input_and_completed_artifact_drift_on_resume(self):
        root, state = self.run_case()
        folder = state['tasks']['first']['artifact_directory']
        c.atomic(root, folder+'/report.json', {'kind': c.MARKER, 'method_valid': True})
        result = c.Runner(root).run(resume=True)
        self.assertEqual(result['tasks']['first']['execution_status'], 'NEEDS_RECONCILIATION')
        self.assertEqual(result['dispatches'], 4)
        root = self.fresh(); c.atomic(root, 'input.json', {'kind': c.MARKER, 'changed': True})
        self.assertEqual(c.Runner(root).run(resume=True)['dispatches'], 0)

    def test_18_interruption_journal_replay_no_duplicate_long_job(self):
        root = self.fresh(); journal = c.Journal(root); state=journal.load()
        state['tasks']['first'].update(execution_status='RUNNING', phase='DISPATCH_INTENT')
        state['dispatches']=1; state['reserved_seconds']=1
        journal.commit(state, 'synthetic_crash_injection')
        # Deliberately stale/tampered snapshot: journal still determines recovery.
        c.atomic(root, '.controller/state.json', {'agent_claims': 'DONE'})
        recovered=c.Runner(root).run(resume=True)
        self.assertEqual(recovered['tasks']['first']['execution_status'], 'NEEDS_RECONCILIATION')
        self.assertEqual(recovered['dispatches'], 1)
        self.assertEqual(recovered['tasks']['second']['execution_status'], 'BLOCKED')

    def test_19_partial_event_log_preserved_and_refused(self):
        root=self.fresh()
        with (root/'.controller/events.jsonl').open('ab') as f:f.write(b'{"partial":')
        before=digest_file(root/'.controller/events.jsonl')
        with self.assertRaises(Refused):c.Runner(root)
        self.assertEqual(before,digest_file(root/'.controller/events.jsonl'))

    def test_20_real_os_writer_lock_rejects_concurrent_start(self):
        root=self.fresh()
        with c.locked(root,'writer.lock',True):
            result=subprocess.run([sys.executable,'-I','-B',str(BUILD/'runner/controller.py'),'run','--root',str(root)],capture_output=True,text=True,timeout=5)
        self.assertEqual(result.returncode,2);self.assertIn('writer lock',result.stdout)
        self.assertEqual(c.Journal(root).load()['dispatches'],0)

    def test_21_stop_then_explicit_resume(self):
        root=self.fresh();c.request_stop(root)
        stopped=c.Runner(root).run();self.assertEqual(stopped['dispatches'],0)
        self.assertEqual(stopped['execution_status'],'STOPPED')
        result=c.Runner(root).run(resume=True,clear_stop=True)
        self.assertEqual(result['execution_status'],'DONE')
        self.assertTrue(list((root/'.controller/stop_history').glob('*.json')))

    def test_22_real_process_stop_terminates_owned_fake_child(self):
        root=self.fresh(modify=lambda x:x['tasks'][0]['arguments'].update(delay=.5))
        proc=subprocess.Popen([sys.executable,'-I','-B',str(BUILD/'runner/controller.py'),'run','--root',str(root)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        child=None
        try:
            deadline=time.monotonic()+5
            while time.monotonic()<deadline:
                st=c.Journal(root).load();child=st['tasks']['first'].get('active_child')
                if child:break
                time.sleep(.01)
            self.assertIsNotNone(child)
            c.request_stop(root)
            stdout,stderr=proc.communicate(timeout=5)
            state=c.Journal(root).load()
            self.assertEqual(state['execution_status'],'STOPPED')
            self.assertEqual(state['dispatches'],1)
            self.assertFalse(Path('/proc',str(child['pid'])).exists())
        finally:
            if proc.poll() is None:proc.terminate();proc.communicate(timeout=5)

    def test_23_path_traversal_symlink_and_unapproved_command_arguments(self):
        root=self.fresh();sentinel=WORK/(uuid.uuid4().hex+'.txt');sentinel.write_text('preserve')
        (root/'link').symlink_to(sentinel)
        for path in ['../escape',str(sentinel),'link','link/child']:
            with self.assertRaises(Refused):c.confined(root,path)
        self.assertEqual(sentinel.read_text(),'preserve')
        for change in [lambda x:x['tasks'][0]['arguments'].update(command='echo hacked'),lambda x:x['tasks'][0]['arguments'].update(scenario='; shell')]:
            with self.assertRaises(Refused):self.fresh(modify=change)

    def test_24_weakening_policy_and_review_checks_rejected(self):
        changes=[lambda x:x.update(live_enabled=True),lambda x:x['tasks'][0].update(acceptance_checks=[]),lambda x:x['tasks'][0].update(outputs=['../report.json'])]
        for change in changes:
            with self.assertRaises(Refused):self.fresh(modify=change)

    def test_25_valid_negative_advances_invalid_high_score_fails(self):
        root,state=self.run_case('negative');self.assertEqual(state['execution_status'],'DONE')
        report=c.read(root,state['tasks']['first']['artifact_directory']+'/report.json')
        self.assertEqual(report['outcome'],'negative')
        root,state=self.run_case('invalid_high_score');self.assertEqual(state['tasks']['first']['execution_status'],'FAILED')
        self.assertEqual(state['dispatches'],1)

    def test_26_live_adapter_never_spawns_and_flags_are_registered(self):
        from unittest.mock import patch
        with patch('subprocess.Popen') as spawn:
            with self.assertRaises(Refused):CodexAdapter().execute({'agent_says_approved':True})
            spawn.assert_not_called()
        argv=CodexAdapter().prepare_argv(Path('/usr/bin/codex'),Path('/synthetic'),Path('/synthetic/schema.json'),Path('/synthetic/answer.json'),'EXPLICIT-APPROVED-IDENTITY')
        self.assertEqual(argv[1:4],['exec','--sandbox','read-only'])
        self.assertNotIn('--ignore-rules',argv);self.assertNotIn('--dangerously-bypass-approvals-and-sandbox',argv)
        with self.assertRaises(Refused):CodexAdapter().prepare_argv(Path('/usr/bin/codex'),Path('/s'),Path('/s/schema'),Path('/s/output'),'--disable-policy')

    def test_27_no_fake_success_modifies_real_queue_or_creates_authorization(self):
        queue=BUILD/'config/derived_queue.json';before=digest_file(queue)
        root,state=self.run_case();self.assertEqual(state['execution_status'],'DONE')
        self.assertEqual(before,digest_file(queue))
        data=json.loads(queue.read_text())
        for task in data['tasks']:
            if task['id'] not in ['CONTROLLER_BOOTSTRAP_SETUP','AUDIT_ENV','AUDIT_SOURCE','AUDIT_HISTORY','PLAN_MINIMAL','REVIEW_AUDIT','PACKAGE_APPROVAL']:
                self.assertIn(task['status'],['WAITING_USER_AUTHORIZATION','DEFERRED'])
        self.assertIsNone(data['experiment_approval'])
        self.assertNotIn('reassemble',sys.modules);self.assertNotIn('torch',sys.modules)

    def test_28_schema_strict_json_and_config_drift(self):
        for value in ['{"x":1,"x":2}','{"x":NaN}']:
            with self.assertRaises(Refused):c.decode(value)
        root=self.fresh();cfg=c.read(root,'workflow.json');cfg['tasks'][0]['arguments']['scenario']='negative'
        c.atomic(root,'workflow.json',cfg)
        self.assertEqual(c.Runner(root).run()['dispatches'],0)


def digest_file(p):return hashlib.sha256(p.read_bytes()).hexdigest()


if __name__=='__main__':
    start=time.monotonic()
    result=unittest.TextTestRunner(stream=sys.stdout,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(OfflineControllerTests))
    summary={'kind':c.MARKER,'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
             'seconds_measured':time.monotonic()-start,'success':result.wasSuccessful(),
             'test_ids':[name for name in unittest.defaultTestLoader.getTestCaseNames(OfflineControllerTests)],
             'scope':'Fixed synthetic workers/reviewers; real OS flock and owned-child stop tested; no hostile-worker OS isolation or live model connection tested'}
    (BUILD/'evidence/TEST_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
