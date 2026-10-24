"""Deterministic classroom risk calculations; no real systems are scanned or changed."""

import json
import math
from pathlib import Path

from packaging.version import Version

ROOT = Path(__file__).resolve().parent


def list_assets(package: str = "") -> list[dict]:
    """Return the bundled synthetic inventory, optionally filtered by package name."""
    assets = json.loads((ROOT / "data" / "assets.json").read_text(encoding="utf-8"))
    return [asset for asset in assets if not package or asset["package"] == package.lower()]


def assess_assets(package: str, fixed_version: str, severity: float) -> list[dict]:
    """Rank versions below a supplied fix using a documented classroom heuristic.

    This assumes every earlier version is affected. The caller must verify that
    assumption against the advisory, including branches and affected ranges.
    Score = min(100, severity * 6 + criticality * 5 + exposure bonus of 15).
    """
    if not math.isfinite(severity) or not 0 <= severity <= 10:
        raise ValueError("severity must be a finite number between 0 and 10")
    fixed = Version(fixed_version)
    findings = []
    for asset in list_assets(package):
        if Version(asset["version"]) >= fixed:
            continue
        score = min(100, severity * 6 + asset["criticality"] * 5
                    + (15 if asset["internet_exposed"] else 0))
        findings.append({**asset, "fixed_version": str(fixed), "score": round(score, 1),
                         "priority": "P1" if score >= 80 else "P2" if score >= 60 else "P3"})
    return sorted(findings, key=lambda item: (-item["score"], item["id"]))


def remediation_plan(findings: list[dict]) -> dict:
    """Create actionable owner assignments from findings without modifying assets."""
    return {"disclaimer": "Synthetic inventory; heuristic priority, not CVSS or a production SLA.",
            "actions": [{"asset": item["id"], "owner": item["owner"],
                         "priority": item["priority"], "score": item["score"],
                         "action": f"Upgrade {item['package']} to at least {item['fixed_version']}; "
                                   "test compatibility, deploy, and verify installed version."}
                        for item in findings]}
