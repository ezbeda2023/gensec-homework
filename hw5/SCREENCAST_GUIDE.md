# Recording guide

1. Introduce yourself (ezbeda2023), HW5, and the unchanged HW4 MCP triage agent.
2. Explain synthetic inventory, the legitimate workflow, and the trust boundary
   between user/tool text and the system's instructions.
3. Show the clean baseline's prompt, actual tool calls, and final answer.
4. For each successful attack show its exact APE technique name and description
   on the APE website, then the attack prompt and any injected retrieved text.
5. Show the actual response and tool arguments, compare to baseline, and explain
   exactly what changed. State that remediation is proposed, never executed.
6. Explain local response injection honestly if using the indirect test: this is
   attacker-controlled content delivered by the harness, not an upstream breach.
7. Discuss resisted attempts and improvements: validate tool-result provenance,
   bind remediation findings to genuine assessment output, and check final
   claims against tool evidence rather than only checking tool names were called.
8. Show the PDF and repository. Keep API keys and the local .env off screen.

Record only results actually obtained. Put the published recording URL in
`screencast_url.txt`; do not use a placeholder URL.
