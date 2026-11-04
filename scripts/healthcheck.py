#!/usr/bin/env python3
"""Read-only local health checks; no agent or third-party dependencies."""
import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import urllib.request

HOME = Path.home()
HERMES = HOME / '.hermes'
NOW = datetime.now().astimezone()
SINCE = NOW - timedelta(hours=24)


def stamp(value):
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, timezone.utc)
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    return result if result.tzinfo else result.replace(tzinfo=NOW.tzinfo)


def result(status, text, **evidence):
    return dict(status=status, text=text, evidence=evidence)


def gateway():
    command = ['systemctl', '--user']
    unit = 'hermes-gateway.service'
    try:
        proc = subprocess.run(command + ['is-active', unit], capture_output=True,
                              text=True, timeout=10)
        if proc.returncode == 0 and proc.stdout.strip() == 'active':
            return result('ok', '网关 ok', state='active')
        state = proc.stdout.strip() or 'unknown'
    except (OSError, subprocess.SubprocessError) as exc:
        state = type(exc).__name__
    try:
        proc = subprocess.run(command + ['status', unit, '--no-pager', '--full'],
                              capture_output=True, text=True, timeout=10)
        lines = (proc.stdout + '\n' + proc.stderr).splitlines()
        summary = next((line.strip() for line in lines if line.strip().startswith('Active:')),
                       next((line.strip() for line in lines if line.strip()), '无状态输出'))
    except (OSError, subprocess.SubprocessError) as exc:
        summary = f'status 检查失败: {type(exc).__name__}'
    summary = compact(summary)
    return result('problem', f'网关异常（{state}）：{summary}', state=state, summary=summary)


def cron():
    path = HERMES / 'cron/executions.db'
    names = {}
    jobs_path = HERMES / 'cron/jobs.json'
    if jobs_path.exists():
        jobs = json.loads(jobs_path.read_text())
        jobs = jobs.get('jobs', []) if isinstance(jobs, dict) else jobs
        names = {j['id']: j.get('name', j['id']) for j in jobs}
    with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True, timeout=2) as conn:
        conn.row_factory = sqlite3.Row
        rows = [dict(row) for row in conn.execute('SELECT * FROM executions')]
    recent = [r for r in rows if SINCE <= stamp(r.get('started_at') or r.get('claimed_at')) <= NOW]
    failures = [r for r in recent if r['status'] not in ('ok', 'completed')]
    details = []
    for row in failures:
        error = (row.get('error') or row['status']).splitlines()[0]
        details.append(f"{names.get(row['job_id'], row['job_id'])} {stamp(row.get('started_at') or row['claimed_at']).astimezone():%m-%d %H:%M}：{compact(error, 90)}")
    text = '定时任务 ' + '；'.join(details) if failures else f'定时 {len(recent)}/{len(recent)} 成功'
    return result('problem' if failures else 'ok', text, total=len(recent), failures=[dict(job=names.get(r['job_id'], r['job_id']), status=r['status'], started_at=r.get('started_at') or r['claimed_at'], error=(r.get('error') or r['status']).splitlines()[0]) for r in failures], details=details)


def errors():
    counts = Counter()
    noise = re.compile(r'linked SQLite .*? is vulnerable|unknown config keys ignored|Background MCP discovery|memory pressure is elevated', re.I)
    pattern = re.compile(r'^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)(?:[,.]\d+)?\s+(ERROR|CRITICAL)\s+(?:\[[^\]]+\]\s+)?([^: ]+)')
    with (HERMES / 'logs/errors.log').open(errors='replace') as log:
        for line in log:
            match = pattern.match(line)
            if match and not noise.search(line) and SINCE <= stamp(match[1]) <= NOW:
                counts[match[3]] += 1
    total = sum(counts.values())
    text = f'24h 内 ERROR/CRITICAL {total} 条，集中在 ' + '、'.join(f'{m}（{n} 次）' for m, n in counts.most_common(3)) if total else '24h 无报错'
    return result('problem' if total else 'ok', text, count=total, modules=dict(counts))


def balance():
    key = None
    for line in (HERMES / '.env').read_text().splitlines():
        match = re.match(r'^\s*(?:export\s+)?DEEPSEEK_API_KEY\s*=\s*(.*?)\s*$', line)
        if match:
            key = match[1].strip('\"\'')
    if not key:
        return result('unknown', '余额未知（未配置 API key）')
    request = urllib.request.Request('https://api.deepseek.com/user/balance', headers={'Authorization': 'Bearer ' + key})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.load(response)
    except Exception:
        # Do not expose headers, credentials, or response bodies on failure.
        return result('unknown', '余额未知（检查出错: 网络请求失败）')
    entries = [b for b in data['balance_infos'] if b['currency'] == 'CNY']
    if not entries:
        return result('unknown', '余额未知（无人民币余额）')
    amount = sum(Decimal(b['total_balance']) for b in entries)
    return result('problem' if amount < 3 else 'ok', f'余额 ¥{amount}' if amount < 3 else '余额正常', cny=str(amount))


def resources():
    disk = shutil.disk_usage('/')
    percent = disk.used / disk.total * 100
    mem = dict(line.split(':', 1) for line in Path('/proc/meminfo').read_text().splitlines())
    available = int(mem['MemAvailable'].split()[0]) / 1024
    problems = []
    if percent > 85:
        problems.append(f'根分区使用 {percent:.1f}%')
    if available < 500:
        problems.append(f'可用内存 {available:.0f}MB')
    return result('problem' if problems else 'ok', '；'.join(problems) if problems else f'磁盘 {percent:.0f}%', disk_percent=percent, memory_available_mb=available)


def stop():
    if not (HOME / 'spread/STOP').exists():
        return result('ok', 'STOP 不存在', exists=False)
    active = []
    failures = 0
    for scope in ([], ['--user']):
        try:
            proc = subprocess.run(
                ['systemctl'] + scope + ['list-units', '--type=service', '--state=active',
                                        '--no-legend', '--no-pager', '--plain',
                                        'spread-hedger*.service', 'spread-exec*.service'],
                capture_output=True, text=True, timeout=10)
            if proc.returncode:
                failures += 1
            else:
                active.extend(line.split()[0] for line in proc.stdout.splitlines() if line.strip())
        except (OSError, subprocess.SubprocessError):
            failures += 1
    if active:
        return result('problem', 'STOP 文件存在（~/spread/STOP），执行器运行中：' + '、'.join(active), exists=True, active_units=active)
    if failures:
        return result('unknown', 'STOP 文件存在（执行器状态检查失败）', exists=True)
    return result('ok', 'STOP 残留（执行器未运行）', exists=True, active_units=[])


def baseline():
    path = HOME / 'repos/hermes/evals/report.json'
    age = (NOW.timestamp() - path.stat().st_mtime) / 86400
    return result('problem' if age > 14 else 'ok', f'该跑一次基线（已 {age:.0f} 天未更新）' if age > 14 else '基线未过期', age_days=age)


def compact(text, limit=240):
    text = ' '.join(str(text).split())
    return text if len(text) <= limit else text[:limit - 1] + '…'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    checks = {}
    for name, label, check in [('gateway', '网关', gateway), ('cron', '定时任务', cron), ('errors', '日志', errors), ('balance', '余额', balance), ('resources', '磁盘/内存', resources), ('stop', 'STOP', stop), ('baseline', '基线', baseline)]:
        try:
            checks[name] = check()
        except Exception as exc:
            # Exception type is useful evidence without risking secret-bearing messages.
            checks[name] = result('unknown', f'{label}未知（检查出错: {type(exc).__name__}）')
    problems = [c for c in checks.values() if c['status'] != 'ok']
    if args.json:
        print(json.dumps(dict(checked_at=NOW.isoformat(), status='attention' if problems else 'ok', checks=checks), ensure_ascii=False))
    elif problems:
        print(f'⚠️ {len(problems)} 个问题')
        for i, item in enumerate(problems, 1):
            print(f'{i}. {compact(item["text"], 2000)}')
        other = [checks[k]['text'] for k in ('gateway', 'cron', 'errors', 'resources') if checks[k]['status'] == 'ok']
        if checks['stop']['status'] == 'ok' and checks['stop']['evidence'].get('exists'):
            other.append(checks['stop']['text'])
        if other:
            print('其它：' + ' | '.join(other))
    else:
        print('✅ 一切正常 | ' + ' | '.join(checks[k]['text'] for k in ('gateway', 'cron', 'errors', 'resources')))
        if checks['stop']['evidence'].get('exists'):
            print('其它：' + checks['stop']['text'])


if __name__ == '__main__':
    main()
