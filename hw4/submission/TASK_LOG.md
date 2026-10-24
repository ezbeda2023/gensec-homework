# Development evidence log — ezbeda2023

This log describes actual development work. It is not a substitute for the
assignment's genuine VS Code screenshots. Capture the visible original chat
prompt/response and relevant code, with ezbeda2023 visible in the IDE.

## Task 1 — Build the assignment application

Original prompt: "here are my assignment instructions help build this out
entierly and create the repo and make sure to push as in the instructions: if
you need any more info let me know and I will provide it."

The prompt then supplied the complete homework requirements. Include that full
prompt from the chat when preparing evidence. Response: the agent inspected the
workspace and proposed an MCP security-triage application, reviewed a published
server, and implemented custom tools, a two-server router, configuration, and
a demo. Code to capture: tops of agent.py, mcp-server.py, and triage.py.

## Task 2 — Create the homework repository

User clarification: "Create a new homework repository under my GitHub account".
Response: created private ezbeda2023/gensec-homework, initialized the required
files, made incremental commits, and pushed to main. Capture the actual response
and terminal Git history. No application code was generated for this clarification.

## Task 3 — Use the existing Gemini API key

User prompt: "I have a gemini api key I can input".
Response: adapted the model loop to Google's documented OpenAI-compatible
Gemini endpoint, read GEMINI_API_KEY from the environment, and added a hidden
key-input PowerShell launcher. Code to capture: run_agent in agent.py and the
top of start-agent.ps1. Do not show the actual key in any screenshot.

## Verification and remaining evidence

The live no-key demo completed calls to fetch, list_assets, assess_assets, and
remediation_plan. Initial integration testing found and fixed multiple MCP text
block decoding and Windows console Unicode handling. Unit tests and lint are
recorded in the repository. Live Gemini testing remains dependent on the key.

Supply genuine screenshots and recording; no screenshots or recordings have
been fabricated. Put images into screenshots/ and insert them in the Word draft.
