"""Offline tests; subprocess is always mocked, reports use temporary directories."""
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
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

    def test_all_criteria_and_session_lookup(self):
        logs = self.root / 'logs/sessions'
        logs.mkdir(parents=True)
        (logs / 'time.jsonl').write_text(json.dumps({'session_id': 'fake-id'}) + '\n' + json.dumps(
            {'role': 'assistant', 'tool_calls': [{'function': {'name': 'terminal'}}]}) + '\n')
        with patch.object(runner.subprocess, 'run', return_value=subprocess.CompletedProcess(
                [], 0, '确认', '')) as run:
            row = runner.run_case(self.case, self.root)
        self.assertEqual(row['status'], 'passed')
        self.assertEqual(row['session_id'], 'time')
        self.assertEqual(row['session_file'], 'time.jsonl')
        self.assertEqual(run.call_args.args[0], ['hermes', '-z', '确认一下', '--cli', '--pass-session-id'])
        self.assertEqual(run.call_args.kwargs['timeout'], 180)

    def test_failures_and_missing_trace(self):
        row = runner.evaluate(self.case['criteria'], '失败', {'browser'})
        self.assertTrue(all(not c['passed'] and c['reason'] for c in row))
        with patch.object(runner.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, '确认', '')):
            for criteria in (self.case['criteria'], [{'type': 'pattern_present', 'pattern': '确认'}]):
                result = runner.run_case(self.case | {'criteria': criteria}, self.root)
                self.assertEqual(result['status'], 'errored')
                self.assertEqual(result['error'], '未找到本轮的会话文件')

    def test_trace_time_window_and_both_directories(self):
        paths = []
        for folder, mtime in [('logs/sessions', 98), ('sessions', 101)]:
            directory = self.root / folder
            directory.mkdir(parents=True)
            path = directory / 'trace.jsonl'
            path.write_text('{}\n')
            os.utime(path, (mtime, mtime))
            paths.append(path)
        self.assertEqual(runner.find_trace(self.root, 100), paths[1])
        paths[1].unlink()
        self.assertEqual(runner.find_trace(self.root, 100), paths[0])
        with self.assertRaisesRegex(ValueError, '未找到本轮的会话文件'):
            runner.find_trace(self.root, 101)

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
            self.assertIn('| 会话文件 |', (self.root / 'report.md').read_text())
            for status, code in [('passed', 0), ('failed', 1), ('errored', 1), ('timeout', 1)]:
                row = {'id': 'fake', 'status': status, 'output': 'a|b\n' * 100,
                       'criteria': [], 'error': 'reason' if code else None,
                       'duration_seconds': 12.3, 'session_file': 'time.jsonl'}
                with patch.object(runner, 'run_case', return_value=row):
                    self.assertEqual(runner.main(['--limit', '1']), code)
                    self.assertIn('| time.jsonl |', (self.root / 'report.md').read_text())
            with self.assertRaises(SystemExit):
                runner.main(['--only', 'missing'])


if __name__ == '__main__':
    unittest.main()
