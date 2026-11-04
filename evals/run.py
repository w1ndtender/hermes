#!/usr/bin/env python3
"""Serial, one-shot Hermes evaluations. No API calls are made with --dry-run."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parent
TYPES = {'tool_called', 'tool_not_called', 'pattern_present', 'pattern_absent'}


def fingerprint(home):
    result = {'model.default': 'unavailable', 'soul_sha256': None, 'memory_chars': {}}
    try:
        # PyYAML is optional; the simple nested model.default form works without it.
        config = (home / 'config.yaml').read_text()
        try:
            import yaml
            model = yaml.safe_load(config).get('model', {})
            result['model.default'] = model.get('default', 'unavailable')
        except ImportError:
            match = re.search(r'^model:\s*\n(?:[ \t]+.*\n)*?[ \t]+default:\s*([^\n#]+)', config, re.M)
            if match:
                result['model.default'] = match[1].strip().strip('\"\'')
    except (OSError, ValueError, AttributeError):
        pass
    soul = home / 'SOUL.md'
    if soul.is_file():
        result['soul_sha256'] = hashlib.sha256(soul.read_bytes()).hexdigest()[:8]
    for name in ('MEMORY.md', 'USER.md'):
        path = home / 'memories' / name
        result['memory_chars'][name] = len(path.read_text()) if path.is_file() else None
    return result


def validate(criteria):
    for c in criteria:
        if c.get('type') not in TYPES:
            raise ValueError(f'不支持的判据: {c}')
        key = 'pattern' if c['type'].startswith('pattern_') else 'tool'
        if not isinstance(c.get(key), str) or not c[key]:
            raise ValueError(f'无效判据: {c}')
        if key == 'pattern':
            re.compile(c[key])


def tools_from_trace(path):
    names = set()
    def visit(obj):
        if isinstance(obj, list):
            for item in obj:
                visit(item)
        elif isinstance(obj, dict):
            for call in obj.get('tool_calls', []) or []:
                name = call.get('function', {}).get('name') or call.get('name')
                if name:
                    names.add(name)
            if obj.get('type') in ('tool_call', 'function_call'):
                name = obj.get('name') or obj.get('tool') or obj.get('function', {}).get('name')
                if name:
                    names.add(name)
            for key, value in obj.items():
                if key not in ('arguments', 'content', 'tool_calls'):
                    visit(value)
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if not rows:
        raise ValueError('会话轨迹为空')
    visit(rows)
    return names


def find_trace(home, output):
    clean = re.sub(r'\x1b\[[0-9;]*m', '', output)
    ids = re.findall(r'(?:session[_ ]id|session)\s*[:=]\s*[\"\']?([\w-]+)', clean, re.I)
    # Hermes session identifiers also appear without a label in CLI output.
    ids += re.findall(r'\b\d{8}_\d{6}_[\w-]+\b', clean)
    directory = home / 'logs' / 'sessions'
    for sid in dict.fromkeys(ids):
        direct = directory / f'{sid}.jsonl'
        if direct.is_file():
            return sid, direct
        for path in directory.glob('*.jsonl'):
            rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
            if any(isinstance(row, dict) and (row.get('session_id') == sid or
                   row.get('metadata', {}).get('session_id') == sid) for row in rows):
                return sid, path
    raise ValueError('无法按 session id 找到会话轨迹')


def evaluate(criteria, output, tools):
    details = []
    for c in criteria:
        kind = c['type']
        found = bool(re.search(c['pattern'], output)) if kind.startswith('pattern_') else c['tool'] in tools
        passed = not found if kind in ('pattern_absent', 'tool_not_called') else found
        details.append({'criterion': c, 'passed': passed,
                        'reason': '' if passed else f'判据未过: {json.dumps(c, ensure_ascii=False)}'})
    return details


def run_case(case, home, dry_run=False):
    start = time.monotonic()
    row = {'id': case['id'], 'status': 'errored', 'output': '', 'stderr': '',
           'criteria': [], 'error': None, 'session_id': None}
    try:
        validate(case['criteria'])
        if dry_run:
            row['status'] = 'dry_run'
            row['criteria'] = [{'criterion': c, 'passed': None, 'reason': '未执行'} for c in case['criteria']]
        else:
            proc = subprocess.run(['hermes', '-z', case['input'], '--cli', '--pass-session-id'],
                                  capture_output=True, text=True, timeout=180)
            row.update(output=proc.stdout, stderr=proc.stderr, returncode=proc.returncode)
            if proc.returncode:
                raise ValueError(f'hermes 退出码 {proc.returncode}: {proc.stderr}')
            tools = set()
            if any(c['type'].startswith('tool_') for c in case['criteria']):
                sid, path = find_trace(home, proc.stdout + '\n' + proc.stderr)
                row['session_id'] = sid
                tools = tools_from_trace(path)
            row['criteria'] = evaluate(case['criteria'], proc.stdout, tools)
            row['status'] = 'passed' if all(c['passed'] for c in row['criteria']) else 'failed'
    except subprocess.TimeoutExpired as exc:
        row['status'] = 'timeout'
        row['error'] = 'timeout: 超过 180 秒，不重试'
        for key in ('stdout', 'stderr'):
            value = getattr(exc, key) or ''
            row['output' if key == 'stdout' else key] = value.decode(errors='replace') if isinstance(value, bytes) else value
    except (OSError, ValueError, TypeError, KeyError, re.error) as exc:
        row['error'] = str(exc)
    row['duration_seconds'] = round(time.monotonic() - start, 3)
    return row


def write_reports(report, directory):
    directory.mkdir(parents=True, exist_ok=True)
    (directory / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    def cell(value):
        return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('|', '&#124;').replace('\r', '').replace('\n', '<br>')
    lines = ['# Eval report', '', f"配置指纹：{json.dumps(report['fingerprint'], ensure_ascii=False)}", '',
             f"汇总：{report['counts']}；总耗时 {report['duration_seconds']} 秒；dry-run={report['dry_run']}", '',
             '| 用例 id | 结果 | 失败判据 / 错误 | 输出前 120 字 |', '| --- | --- | --- | --- |']
    for row in report['results']:
        reasons = [c['reason'] for c in row['criteria'] if c['passed'] is False]
        lines.append('| ' + ' | '.join(map(cell, [row['id'], row['status'], row['error'] or '; '.join(reasons), row['output'][:120]])) + ' |')
    lines += ['', '## 判据明细', '']
    for row in report['results']:
        lines.append(f"- {cell(row['id'])}: {cell(row['error'] or '')}")
        for detail in row['criteria']:
            lines.append(f"  - {cell(json.dumps(detail['criterion'], ensure_ascii=False))}: {detail['passed']} {cell(detail['reason'])}")
    (directory / 'report.md').write_text('\n'.join(lines) + '\n')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only')
    parser.add_argument('--limit', type=int)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)
    if args.limit is not None and args.limit < 1:
        parser.error('--limit 必须大于 0')
    start = time.monotonic()
    home = Path(os.environ.get('HERMES_HOME', Path.home() / '.hermes'))
    fp = fingerprint(home)
    print('配置指纹：' + json.dumps(fp, ensure_ascii=False), flush=True)
    cases = [json.loads(line) for line in (ROOT / 'cases.jsonl').read_text().splitlines() if line.strip()]
    if args.only:
        cases = [c for c in cases if c['id'] == args.only]
        if not cases:
            parser.error(f'不存在的用例 id: {args.only}')
    if args.limit:
        cases = cases[:args.limit]
    chars = sum(len(c['input']) for c in cases)
    print(f'成本估算：{len(cases)} 条 × 平均 {chars / max(len(cases), 1):.1f} 字 = {chars} 输入字符；'
          f'粗按 1 字/token、$1/百万输入 token 约 ${chars / 1_000_000:.6f}。'
          '仅示例单价，不含系统提示、memory、输出及工具多轮，实际费用取决于模型。', flush=True)
    results = []
    for case in cases:
        row = run_case(case, home, args.dry_run)
        results.append(row)
        print(f"{row['id']}: {row['status']} {row['error'] or ''}", flush=True)
        for detail in row['criteria']:
            print(f"  {detail['criterion']}: {detail['passed']} {detail['reason']}")
    counts = {status: sum(r['status'] == status for r in results)
              for status in ('passed', 'failed', 'errored', 'timeout', 'dry_run')}
    report = {'fingerprint': fp, 'dry_run': args.dry_run, 'counts': counts,
              'duration_seconds': round(time.monotonic() - start, 3), 'results': results}
    write_reports(report, ROOT)
    print(f'汇总：{counts}；总耗时 {report["duration_seconds"]} 秒')
    return int(any(counts[s] for s in ('failed', 'errored', 'timeout')))


if __name__ == '__main__':
    raise SystemExit(main())
