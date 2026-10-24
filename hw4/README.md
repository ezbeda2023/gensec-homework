# HW4: MCP Security Triage — ezbeda2023

This application combines an original Python MCP server with the published
`mcp-server-fetch` server from the official Model Context Protocol repository.
Gemini discovers their tools and chooses calls to solve a multi-step task:
retrieve Requests release evidence, inspect a synthetic inventory, rank potentially
affected assets, and assign remediation actions to owners.

## Setup and run

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and Python 3.11–3.13.
From this directory:

```powershell
uv sync --frozen
uv run --frozen agent.py --demo
uv run --frozen agent.py --smoke-test
```

`--demo` performs real stdio MCP calls to both servers, including a live public
HTTP fetch, using a scripted workflow without an API key. `--smoke-test` starts
both servers and uses the custom tools without fetching a website. These modes
test plumbing; they are not model-driven agents.

To run the actual Gemini agent, use the hidden-input launcher:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\start-agent.ps1
```

Or set `GEMINI_API_KEY` in your process environment, then run:

```powershell
$env:GEMINI_MODEL = 'gemini-3.8-flash' # optional; choose a model your account supports
uv run --frozen agent.py
uv run --frozen agent.py --task 'Review Requests 2.32.4 and prioritize remediation for our inventory.'
```

The process-only execution policy option allows this local launcher on systems
that block scripts; it does not change the computer's persistent policy.
The `openai` Python package is used as the client for Google's documented
[OpenAI-compatible Gemini endpoint](https://ai.google.dev/gemini-api/docs/openai).
Requests go to Google; no OpenAI account or OpenAI API key is required.
`.env.example` documents variable names but is not automatically loaded.
Never commit your real key. No key is passed to either MCP server subprocess.
The launcher keeps the key out of terminal history and clears it after running.

The workspace used to build this assignment also has a local uv executable at
`../.tools/bin/uv.exe`; it is intentionally excluded from Git.

## Architecture and tools

```text
User task -> Gemini tool-calling loop -> namespaced MCP router
                                       |-- triage: custom stdio server
                                       |-- fetch: published stdio server
                         tool results -> Gemini -> cited remediation report
```

`mcp-config.json` defines both server processes. The agent uses its own uv-managed
Python executable to start them, initializes MCP sessions, and discovers tools
with `list_tools`. Names such as `triage__assess_assets` avoid server name clashes.
The host routes model requests back to the appropriate MCP session, returns
results to Gemini, and repeats for at most 12 turns (configurable up to 30).
Before accepting a final answer it checks that all four required tools succeeded.

| Server | Tool | Purpose |
| --- | --- | --- |
| Custom triage | `list_assets` | Read bundled synthetic inventory, optionally by package |
| Custom triage | `assess_assets` | Compare PEP 440 versions and rank potentially affected assets |
| Custom triage | `remediation_plan` | Assign proposed upgrades and verification to owners |
| Published Fetch | `fetch` | Retrieve the approved upstream release history |

The custom server also provides a `triage_instructions` MCP prompt.
`agent.py` contains client orchestration; `mcp-server.py` registers tools and runs
the server; `triage.py` contains the documented domain logic.

## Scoring and limitations

All assets are invented. `assess_assets` assumes every version below a supplied
fixed version is affected; the model is instructed to verify the advisory range
and disclose when that simplified rule does not apply. It is not a vulnerability
scanner. Only single-package version comparisons are supported.

Classroom score = `min(100, severity * 6 + criticality * 5 + (15 if exposed else 0))`.
P1 >= 80, P2 >= 60, otherwise P3. Severity 6.5 is an explicitly assumed input,
not a verified CVSS rating. The demo ranks `web-01` P2 / 79 and `jobs-01` P3 / 54;
already patched `api-01` is excluded. No remediation commands are executed.

The router permits exactly one checked-in public upstream URL and caps fetched
content at 12,000 characters. Source text is treated as untrusted evidence.
This is a classroom defense, not a complete sandbox or production SSRF boundary;
see [the dependency review](SERVER_REVIEW.md).

## Outputs and verification

Reports and full MCP tool traces are saved locally under ignored `output/`:
`demo-report.md`, `demo-trace.json`, or `agent-report.md`, `agent-trace.json`.
Read the agent report for evidence, affected-range qualifications and source citations.
Traces may contain task and inventory data; inspect them before sharing.

```powershell
uv run --frozen pytest -p no:cacheprovider
uv run --frozen ruff check --no-cache .
```

Automated tests cover version comparisons, ordering, exact fixed-version exclusion,
invalid severity, score caps, empty findings, host URL policy, and simulated Gemini
multi-step orchestration. The real no-key demo additionally verifies both subprocesses,
MCP initialization, tool discovery, live fetch and cross-tool results. Live Gemini
verification requires your local key; mocked tests do not prove API account access.

## Submission

1. Run the model-driven agent and inspect `output/agent-report.md` and the tool trace.
2. Capture genuine VS Code prompt/response and code screenshots for every significant
   development task. Show **ezbeda2023** in each. See `submission/TASK_LOG.md`.
3. Record a screencast explaining the two MCP servers and demonstrating the agent.
   Replace `screencast_url.txt` with its real YouTube URL.
4. Add screenshots and the screencast URL to `submission/hw3-ezbeda2023.docx`.
   The assignment explicitly requests the `hw3-` prefix despite being Homework 4.
5. Export the finished Word document as PDF, verify every page, and upload to Canvas.
6. Grant your instructor repository access if needed; this repository is private.
   Commit and push final evidence before class.

The supplied document is a draft until screenshots and the recording are added.
Do not submit it with pending evidence. Never manufacture screenshots, recordings,
API test results or development history.
