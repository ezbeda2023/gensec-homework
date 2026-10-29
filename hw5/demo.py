"""Display saved real experiment evidence. This is a replay, not a live API run."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('case', choices=['baseline', 'instruction-override', 'tool-spoofing',
                                    'indirect-system-spoofing'])
parser.add_argument('--section', choices=['prompt', 'tools', 'answer', 'all'], default='all')
args = parser.parse_args()
path = ROOT / 'evidence' / args.case / 'run.json'
data = json.loads(path.read_text(encoding='utf-8'))
print(f"ezbeda2023 | HW5 | {args.case}")
print('SAVED REAL EXPERIMENT - evidence replay, no live API request')
print(f"Recorded UTC: {data['started_utc']} | Status: {data['status']}")
print(f"Model: {data['api_turns'][0]['model']}")
if args.section in ['prompt', 'all']:
    print('\nEXACT USER PROMPT\n' + data['prompt'])
    if data.get('injection'):
        print('\nLOCAL HARNESS INJECTION INTO FETCH RESPONSE\n' + data['injection'])
if args.section in ['tools', 'all']:
    print('\nACTUAL MCP TOOL SEQUENCE')
    for i, call in enumerate(data['original_tool_trace'], 1):
        print(f"\n{i}. {call['tool']} | error={call['is_error']}")
        print('Arguments: ' + json.dumps(call['arguments'], ensure_ascii=True))
        if call['tool'] == 'fetch__fetch':
            print('Response: release-history text; full response is retained in run.json.')
        else:
            print('Response: ' + json.dumps(call.get('structured') or call['content'],
                                            ensure_ascii=True))
if args.section in ['answer', 'all']:
    print('\nACTUAL FINAL MODEL ANSWER\n' + data.get('report', 'No completed answer.'))
