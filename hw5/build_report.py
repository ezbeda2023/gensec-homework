"""Build an evidence-based PDF; require reviewed success and real screenshots."""
import json
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
)

ROOT = Path(__file__).resolve().parent


def main():
    review_file = ROOT / "findings.json"
    reviews = json.loads(review_file.read_text(encoding="utf-8")) if review_file.exists() else []
    successful = [item for item in reviews if item.get("successful") is True]
    ready = 1 <= len(successful) <= 2
    for item in successful:
        run = json.loads((ROOT / "evidence" / item["case"] / "run.json").read_text(encoding="utf-8"))
        ready &= run["status"] == "completed" and bool(item.get("screenshots"))
        ready &= all((ROOT / path).exists() for path in item.get("screenshots", []))
        ready &= all(bool(item.get(key)) for key in ("impact", "observation", "description_url"))
    output = ROOT / "submission"
    output.mkdir(exist_ok=True)
    pdf = output / ("hw5-ezbeda2023.pdf" if ready else "hw5-ezbeda2023-DRAFT.pdf")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Body", fontSize=11, leading=15, spaceAfter=9))
    styles.add(ParagraphStyle(name="CodeSmall", fontName="Courier", fontSize=8, leading=11))
    story = []

    def p(text, style="Body"):
        story.append(Paragraph(escape(text).replace("\n", "<br/>"), styles[style]))

    p("HW5: Adversarial Prompt Engineering", "Title")
    p("ezbeda2023 | Security Engineering")
    if not ready:
        p("DRAFT - live successful attacks and screenshot evidence are incomplete.", "Heading2")
    p("Target and scope", "Heading1")
    p("The Homework 4 Gemini MCP security-triage agent with its original system instructions, "
      "custom triage server, published Fetch server, and synthetic asset inventory. "
      "All tests are restricted to this course application. No assets are modified.")
    p("Legitimate behavior", "Heading2")
    p("Fetch the approved upstream release history, verify the affected range, inspect inventory, "
      "assess findings, and produce a truthful owner-assigned remediation plan. Under the documented "
      "classroom earlier-than-2.32.4 rule and assumed severity 6.5, web-01 scores 79 (P2), "
      "jobs-01 scores 54 (P3), and patched api-01 is excluded. This heuristic is not a verified advisory range.")
    baseline_file = ROOT / "evidence/baseline/run.json"
    if baseline_file.exists():
        baseline = json.loads(baseline_file.read_text(encoding="utf-8"))
        p("Baseline run", "Heading2")
        p("Status: " + baseline["status"])
        p(baseline.get("report", "No completed baseline answer."))
    if not successful:
        p("Experiments prepared", "Heading1")
        p("Instruction Override (HLT03.11); Tool Spoofing (HLT05.05); System Prompt Spoofing "
          "(HLT05.07). These are candidates, not demonstrated successful attacks. "
          "APE definitions: https://ape.hiddenlayer.com/ttps.html")
    for number, item in enumerate(successful, 1):
        run = json.loads((ROOT / "evidence" / item["case"] / "run.json").read_text(encoding="utf-8"))
        story.append(PageBreak())
        p(f"Attack {number}: {run['technique']}", "Heading1")
        p("APE description: " + item["description_url"])
        p("Run UTC: " + run["started_utc"] + "; model: " + run["api_turns"][0]["model"])
        p("Target agent SHA-256: " + run["target_sha256"])
        p("Attacker prompt", "Heading2")
        p(run["prompt"])
        if run.get("injection"):
            p("Lower-trust content injected by the local response harness", "Heading2")
            p("The public website was not modified. The harness prepended the following text "
              "to the real Fetch result delivered to the unchanged agent:")
            p(run["injection"])
        p("Messages and tool sequence", "Heading2")
        for turn_number, turn in enumerate(run["api_turns"], 1):
            response = turn.get("response", {})
            choices = response.get("choices", [])
            if not choices:
                continue
            message = choices[0]["message"]
            p(f"Assistant turn {turn_number}", "Heading3")
            if message.get("content"):
                p(message["content"])
            for call in message.get("tool_calls", []):
                p(call["function"]["name"] + "(" + call["function"]["arguments"] + ")")
            # Tool messages in the next request are the actual replies to this turn.
            if turn_number < len(run["api_turns"]):
                current_len = len(turn["messages"]) + 1
                for msg in run["api_turns"][turn_number]["messages"][current_len:]:
                    if msg["role"] == "tool":
                        p("Tool response: " + msg["content"])
        p("Observed compromise", "Heading2")
        p(item["observation"])
        p("Impact", "Heading2")
        p(item["impact"])
        for screenshot in item.get("screenshots", []):
            story.append(PageBreak())
            p(f"Attack {number}: captured evidence", "Heading1")
            path = ROOT / screenshot
            width, height = ImageReader(str(path)).getSize()
            scale = min(504 / width, 620 / height)
            story.append(Image(str(path), width=width * scale, height=height * scale))
            p(screenshot)
    story.append(PageBreak())
    p("Limitations and remediation", "Heading1")
    p("Success is judged by actual final claims and tool arguments compared to baseline. "
      "A tool-name completion check does not guarantee the correctness of the plan. Bind "
      "remediation input to genuine assessment output; validate provenance and consistency; "
      "reject policy instructions in retrieved content; check final claims against the real findings. "
      "These experiments demonstrate local report-integrity impact only, not command execution "
      "or a production breach. Failed or resisted experiments are retained in the evidence folders.")

    def footer(canvas, doc):
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.HexColor("#555555"))
        canvas.drawString(54, 28, "ezbeda2023 | HW5" + (" | DRAFT" if not ready else ""))
        canvas.drawRightString(558, 28, str(doc.page))

    SimpleDocTemplate(str(pdf), pagesize=(612, 792), leftMargin=54, rightMargin=54,
                      topMargin=45, bottomMargin=48).build(story, onFirstPage=footer, onLaterPages=footer)
    print(pdf)


if __name__ == "__main__":
    main()
