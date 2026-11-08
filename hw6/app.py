"""Offline authentication-log triage. Python 3.11+, standard library only."""
import argparse
from collections import defaultdict, deque
from datetime import datetime, timezone
import ipaddress
import json
from pathlib import Path
import sys

MAX_BYTES = 2 * 1024 * 1024
MAX_EVENTS = 10000
MAX_LINE = 4096


def load_events(path):
    events = []
    total = 0
    with Path(path).open('rb') as source:
        while raw := source.readline(MAX_LINE + 1):
            total += len(raw)
            if total > MAX_BYTES or len(raw) > MAX_LINE:
                raise ValueError('Input exceeds the 2 MiB file or 4096-byte line limit')
            if len(events) >= MAX_EVENTS:
                raise ValueError('Input exceeds 10000 events')
            try:
                row = json.loads(raw.decode('utf-8'))
                if not isinstance(row, dict) or set(row) != {'timestamp', 'ip', 'user', 'result'}:
                    raise ValueError()
                if not all(isinstance(value, str) for value in row.values()):
                    raise ValueError()
                if row['result'] not in ('success', 'failure'):
                    raise ValueError()
                if not 1 <= len(row['user']) <= 64 or not all(c.isprintable() for c in row['user']):
                    raise ValueError()
                stamp = datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
                if stamp.utcoffset() is None:
                    raise ValueError()
                events.append({**row, 'ip': str(ipaddress.ip_address(row['ip'])),
                               'timestamp': stamp.astimezone(timezone.utc)})
            except (ValueError, TypeError, UnicodeError, RecursionError, OverflowError):
                raise ValueError(f'Invalid event at line {len(events) + 1}') from None
    return sorted(events, key=lambda event: event['timestamp'])


def analyze(events, threshold=5, window=300):
    """One failure alert per IP; success alerts require preceding same-user failures."""
    recent = defaultdict(deque)
    alerted = set()
    findings = []
    for event in events:
        ip, stamp = event['ip'], event['timestamp']
        queue = recent[ip]
        while queue and (stamp - queue[0]['timestamp']).total_seconds() > window:
            queue.popleft()
        if event['result'] == 'failure':
            queue.append(event)
            if len(queue) >= threshold and ip not in alerted:
                alerted.add(ip)
                findings.append({'type': 'repeated_failures', 'ip': ip,
                                 'timestamp': stamp.isoformat(), 'count': len(queue)})
        else:
            count = sum(item['user'] == event['user'] for item in queue)
            if count >= threshold:
                findings.append({'type': 'success_after_failures', 'ip': ip,
                                 'timestamp': stamp.isoformat(), 'user': event['user'],
                                 'count': count})
            # A successful login ends this user's failure sequence.
            recent[ip] = deque(item for item in queue if item['user'] != event['user'])
    return {'events': len(events), 'threshold': threshold, 'window_seconds': window,
            'findings': findings,
            'limitations': 'Heuristic triage, not proof of compromise. Shared IPs can cause false positives; distributed and slow attacks may be missed.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='UTF-8 JSON Lines authentication log')
    parser.add_argument('--threshold', type=int, default=5)
    parser.add_argument('--window', type=int, default=300, help='Seconds, inclusive')
    parser.add_argument('--output', type=Path, help='New JSON report; existing files are never overwritten')
    args = parser.parse_args(argv)
    if not 2 <= args.threshold <= 1000 or not 1 <= args.window <= 86400:
        parser.error('threshold must be 2..1000 and window must be 1..86400')
    try:
        report = analyze(load_events(args.input), args.threshold, args.window)
        # ASCII escaping prevents untrusted usernames from emitting terminal controls.
        rendered = json.dumps(report, indent=2, ensure_ascii=True)
        if args.output:
            with args.output.open('x', encoding='utf-8') as target:
                target.write(rendered + '\n')
        print(rendered)
        return 0
    except (OSError, ValueError) as exc:
        # Do not echo attacker-controlled paths or raw input in diagnostics.
        message = str(exc) if isinstance(exc, ValueError) else 'Cannot read input or create output (output must be a new file)'
        print(f'Error: {message}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
