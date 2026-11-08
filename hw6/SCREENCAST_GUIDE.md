# Narrated screencast target: 4:45 (maximum 5:00)

Before recording, rehearse generation time, open Codex, increase terminal/chat
font size, and prepare a fresh destination outside this working repository.
Capture real prompts and replies with readable screenshots for the Word file.
Do not expose credentials. If regeneration takes too long, simplify the prompts
and rehearse again; do not present prepared source as newly generated evidence.

1. **0:00–0:20 — Camera on initially.** Introduce yourself, HW6, Codex, and the
   offline authentication-log analyzer.
2. **0:20–0:45 — Clone.** In a fresh directory run:

   ```powershell
   git clone https://github.com/ezbeda2023/gensec-homework.git hw6-recording
   cd hw6-recording/hw6
   Get-Content prompts.txt
   mkdir replay
   cd replay
   ```

3. **0:45–2:40 — Replay.** Show the three prompts, then actually submit them
   to Codex with `replay` as the workspace. Tell it to generate fresh files
   there using the prompts, without copying the checked-in app. Show real
   responses and test results. The source repository remains available for
   the prompt overview; the replay directory starts empty.
4. **2:40–3:35 — Security.** Explain untrusted log data, exact schema, input
   limits, no shell/network actions, escaped output, and no-overwrite reports.
   Show the malformed sample failing and the relevant tests passing.
5. **3:35–4:25 — Demonstrate.** Run the valid sample, explain both alerts,
   normal IPv6 event, threshold/window controls, and output report. Try the
   same report path again to demonstrate overwrite rejection.
6. **4:25–4:45 — Limitations.** Mention shared-IP false positives, missed
   slow/distributed attacks, strict JSONL format, and unverified log provenance.

After recording: upload to YouTube as unlisted, check access in an incognito
window while signed out, put the real URL in `screencast_url.txt` and the Word
document, add repository URL and complete readable prompt/reply screenshots,
export the Word file to PDF, review it, commit/push updates, and submit to Canvas.
