# HW6 — Offline authentication-log analyzer

Coding agent: **OpenAI Codex**. Python 3.11+; no packages, API keys, or network
access are required. This CLI triages user-supplied authentication logs.

From the course repository root:

```powershell
cd hw6
python app.py samples/auth.jsonl
python -m unittest -v
python app.py samples/invalid.jsonl
python app.py samples/auth.jsonl --output my-report.json
```

The valid demo has seven events and produces `repeated_failures` and
`success_after_failures` findings for `192.0.2.10`. The invalid sample returns
exit code 2. Repeating an output filename fails without changing its contents.
Use `python app.py --help` for threshold/window options.

Each JSONL line has exactly four string fields:

```json
{"timestamp":"2026-11-08T12:00:00Z","ip":"192.0.2.10","user":"alice","result":"failure"}
```

Timestamps must include a timezone. IPv4 and IPv6 are accepted. Records are
sorted before analysis. The default rule is five failures per IP within an
inclusive 300-second window. One repeated-failure alert is emitted per IP per
run. A success alert requires five preceding failures for that same IP and
username in the window. A success clears that user's failure sequence.

Security controls: strict schema and value validation, bounded binary line
reads, 2 MiB input/10000 event/4096 byte line limits, printable usernames of
at most 64 characters, ASCII-escaped JSON output, and exclusive report creation.
Errors do not reproduce raw log content or filenames. No shell execution,
remote fetching, remediation, or input modification occurs. Run as an ordinary
user on local files you intend to analyze. Output reports contain usernames
and IPs; store them appropriately. Test samples are synthetic.

Limitations: findings are heuristics, not proof of compromise. Shared IPs can
cause false positives; slow/distributed attacks may be missed. One alert per
IP summarizes repeated failures rather than tracking every episode. The app
requires normalized JSONL, not raw SSH/Windows logs, and rejects the whole file
if any event is invalid. It does not authenticate the source of a log.

`prompts.txt` distinguishes this session's development request from prepared
replay prompts. Use the actual agent replies from your recorded replay as
evidence; generation may vary and take longer than the sample timing.

Repository: https://github.com/ezbeda2023/gensec-homework/tree/main/hw6

See `SCREENCAST_GUIDE.md` and `STATUS.md` for remaining submission work.
