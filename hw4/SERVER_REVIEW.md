# Published MCP server review — 2026-10-23

Selected server: **Fetch**, Python distribution `mcp-server-fetch==2025.4.7`.

## Authenticity investigation performed before execution

- Started at the assignment's official source:
  https://github.com/modelcontextprotocol/servers
- Confirmed Fetch's upstream directory and documented module invocation:
  https://github.com/modelcontextprotocol/servers/tree/main/src/fetch
- Retrieved PyPI metadata from https://pypi.org/pypi/mcp-server-fetch/json;
  checked the exact published distribution name and release existence. The project
  points back to the official MCP servers repository and identifies Anthropic.
- Inspected installed `mcp_server_fetch/server.py` before launching it: the code
  registers the fetch tool and prompt, checks robots.txt, performs HTTP retrieval,
  and converts HTML through readabilipy/markdownify. This is a focused review,
  not a comprehensive audit of every transitive dependency.
- Locked the full resolved dependency graph, including distribution hashes, in
  `uv.lock`. Reproduce it with `uv sync --frozen`.

## Compatibility choice and material limits

The exact 2025.4.7 release uses the MCP Python SDK v1 API used in this project.
The locked SDK is 1.30.0. Upstream main has since moved to SDK v2; its newer
README and security protections do not necessarily describe this older package.
The version pin is for reproducibility and compatibility, not a claim that this
release is the latest or free of vulnerabilities. Re-review and upgrade the
server and SDK together before expanding this classroom application.

The older Fetch server follows redirects and does not provide the private-address
protection documented in the newest upstream release. It must not be exposed to
arbitrary URLs or used as a general network proxy. A server authentic to its
publisher can still have vulnerabilities; package metadata is not cryptographic
proof of publisher identity or a safety guarantee.

## Host restrictions in this application

- The router accepts exactly the Requests v2.32.4 HISTORY.md URL from the upstream
  Python Software Foundation repository on raw.githubusercontent.com. This reduces
  destination exposure, but cannot independently guarantee upstream availability,
  integrity, DNS behavior, or redirect behavior.
- MCP servers receive a minimal environment without Gemini or OpenAI keys.
- The published process uses its installed module rather than shell interpolation
  or an unpinned `uvx` download on every run.
- Read-only workflow: no shell tool, arbitrary file tool, patching, or real asset
  modification is offered to the model. Fetch output is capped at 12,000 characters.
- Webpage and tool output are untrusted data in the system prompt. This reduces
  instruction confusion but does not guarantee resistance to prompt injection.
- API calls have timeouts and retries, MCP sessions have read timeouts, and the
  agent loop is bounded. Dependencies are third-party code executed locally and
  are not sandboxed by Python or MCP.

Decision: suitable for this narrow classroom demonstration with synthetic data
and a fixed public source. Do not broaden the allowlist without a fresh review.
