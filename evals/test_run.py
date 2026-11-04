"""Offline tests; subprocess is always mocked, reports use temporary directories."""
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('runner', Path(__file__).with_name('run.py'))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.case = {'id': 'fake', 'input': '确认一下', 'criteria': [
            {'type': 'pattern_present', 'pattern': '确认'},
            {'type': 'pattern_absent', 'pattern': '失败'},
            {'type': 'tool_called', 'tool': 'terminal'},
            {'type': 'tool_not_called', 'tool': 'browser'}]}

    def make_db(self):
        connection = sqlite3.connect(self.root / 'state.db')
        self.addCleanup(connection.close)
        connection.executescript("""
            CREATE TABLE sessions (id TEXT PRIMARY KEY, started_at REAL, estimated_cost_usd REAL);
            CREATE TABLE messages (id INTEGER PRIMARY KEY, session_id TEXT, role TEXT,
                                   tool_calls TEXT, tool_name TEXT, timestamp REAL);
        """)
        return connection

    def test_all_criteria_and_session_lookup(self):
        db = self.make_db()
        db.execute('INSERT INTO sessions VALUES (?, ?, ?)', ('fake-id', 100, 0.125))
        db.executemany('INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?)', [
            (1, 'fake-id', 'assistant', json.dumps([
                {'function': {'name': 'terminal'}}, {'name': 'search'}]), None, 100),
            (2, 'fake-id', 'tool', None, 'terminal', 101),
            (3, 'fake-id', 'tool', None, 'read_file', 102),
            (4, 'other', 'tool', None, 'browser', 103)])
        db.commit()
        before = (self.root / 'state.db').read_bytes()
        with patch.object(runner.time, 'time', return_value=100), patch.object(
                runner.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, '确认', '')) as run:
            row = runner.run_case(self.case, self.root)
        self.assertEqual(row['status'], 'passed')
        self.assertEqual(row['session_id'], 'fake-id')
        self.assertEqual(row['tool_names'], ['terminal', 'search', 'read_file'])
        self.assertEqual(row['estimated_cost_usd'], 0.125)
        self.assertEqual((self.root / 'state.db').read_bytes(), before)
        self.assertEqual(run.call_args.args[0], ['hermes', '-z', '确认一下', '--cli', '--pass-session-id'])
        self.assertEqual(run.call_args.kwargs['timeout'], 180)

    def test_failures_and_missing_trace(self):
        row = runner.evaluate(self.case['criteria'], '失败', {'browser'})
        self.assertTrue(all(not c['passed'] and c['reason'] for c in row))
        with patch.object(runner.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, '确认', '')):
            for criteria in (self.case['criteria'], [{'type': 'pattern_present', 'pattern': '确认'}]):
                result = runner.run_case(self.case | {'criteria': criteria}, self.root)
                self.assertEqual(result['status'], 'errored')
                self.assertEqual(result['error'], 'state.db 里没有本轮会话')
        self.assertFalse((self.root / 'state.db').exists())

    def test_trace_time_window_and_read_only(self):
        db = self.make_db()
        db.executemany('INSERT INTO sessions VALUES (?, ?, ?)', [
            ('old', 99.9, 1), ('boundary', 100, None), ('latest', 101, 0.2)])
        db.commit()
        connect = sqlite3.connect
        with patch.object(runner.sqlite3, 'connect', wraps=connect) as opened:
            self.assertEqual(runner.read_session(self.root, 100), ('latest', [], 0.2))
        self.assertTrue(opened.call_args.args[0].endswith('state.db?mode=ro'))
        self.assertTrue(opened.call_args.kwargs['uri'])
        db.execute("DELETE FROM sessions WHERE id = 'latest'")
        db.commit()
        self.assertEqual(runner.read_session(self.root, 100), ('boundary', [], None))
        with self.assertRaisesRegex(ValueError, 'state.db 里没有本轮会话'):
            runner.read_session(self.root, 100.1)

    def test_errors_timeout_and_dry_run(self):
        for error, status in [(subprocess.TimeoutExpired('hermes', 180, output=b'partial'), 'timeout'),
                              (FileNotFoundError('missing'), 'errored')]:
            with patch.object(runner.subprocess, 'run', side_effect=error) as run:
                row = runner.run_case(self.case, self.root)
                self.assertEqual(row['status'], status)
                self.assertEqual(run.call_count, 1)
        with patch.object(runner.subprocess, 'run') as run:
            self.assertEqual(runner.run_case(self.case, self.root, True)['status'], 'dry_run')
            self.case['criteria'] = [{'type': 'fact_present', 'fact': '下一根'}]
            row = runner.run_case(self.case, self.root)
            self.assertEqual(row['status'], 'errored')
            self.assertIn('fact_present', row['error'])
            run.assert_not_called()
        with patch.object(runner.subprocess, 'run', return_value=subprocess.CompletedProcess([], 2, '', 'bad')):
            self.assertEqual(runner.run_case(self.case | {'criteria': []}, self.root)['status'], 'errored')

    def test_selection_reports_and_exit_codes(self):
        cases = [self.case | {'id': 'first'}, self.case | {'id': 'second'}]
        (self.root / 'cases.jsonl').write_text('\n'.join(json.dumps(c) for c in cases))
        with patch.object(runner, 'ROOT', self.root), patch.object(runner, 'fingerprint', return_value={}), patch.object(runner.subprocess, 'run') as run:
            self.assertEqual(runner.main(['--only', 'second', '--limit', '1', '--dry-run']), 0)
            run.assert_not_called()
            report = json.loads((self.root / 'report.json').read_text())
            self.assertEqual([r['id'] for r in report['results']], ['second'])
            self.assertEqual(report['counts']['passed'], 0)
            self.assertTrue((self.root / 'report.md').is_file())
            with patch('sys.stdout', new_callable=io.StringIO) as output:
                self.assertEqual(runner.main(['--only', 'second', '--only', 'first', '--dry-run']), 0)
            report = json.loads((self.root / 'report.json').read_text())
            self.assertEqual([r['id'] for r in report['results']], ['first', 'second'])
            self.assertIn('[1/2] first ... dry_run (', output.getvalue())
            self.assertIn('[2/2] second ... dry_run (', output.getvalue())
            self.assertIn('| 会话 id | 工具调用 | 估算成本（USD） |', (self.root / 'report.md').read_text())
            for status, code in [('passed', 0), ('failed', 1), ('errored', 1), ('timeout', 1)]:
                row = {'id': 'fake', 'status': status, 'output': 'a|b\n' * 100,
                       'criteria': [], 'error': 'reason' if code else None,
                       'duration_seconds': 12.3, 'session_id': 'fake-id',
                       'tool_names': ['terminal', 'a', 'b', 'c', 'd', 'e', 'hidden'],
                       'estimated_cost_usd': 0.125}
                with patch.object(runner, 'run_case', return_value=row):
                    self.assertEqual(runner.main(['--limit', '1']), code)
                    markdown = (self.root / 'report.md').read_text()
                    self.assertIn('| fake-id | terminal, a, b, c, d, e | 0.125 |', markdown)
                    self.assertNotIn('hidden', markdown)
                    self.assertIn('本轮总成本（估算）：$0.125000', markdown)
            with self.assertRaises(SystemExit):
                runner.main(['--only', 'missing'])


if __name__ == '__main__':
    unittest.main()
