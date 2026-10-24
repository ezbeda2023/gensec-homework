"""Check ranking boundaries, invalid input, and MCP host policy."""

import asyncio

import pytest

from agent import ToolRouter
from triage import assess_assets, list_assets, remediation_plan


def test_inventory_filter_and_patched_asset_exclusion():
    """Include only the two unpatched Requests assets in descending priority."""
    assert len(list_assets("requests")) == 3
    findings = assess_assets("requests", "2.32.4", 6.5)
    assert [(f["id"], f["score"], f["priority"]) for f in findings] == [
        ("web-01", 79.0, "P2"), ("jobs-01", 54.0, "P3")]
    assert "api-01" not in [f["id"] for f in findings]
    assert remediation_plan(findings)["actions"][0]["owner"] == "Web team"


@pytest.mark.parametrize("severity", [-1, 11, float("nan"), float("inf")])
def test_invalid_severity(severity):
    """Reject non-finite and out-of-range severities."""
    with pytest.raises(ValueError):
        assess_assets("requests", "2.32.4", severity)


def test_numeric_versions_empty_results_and_score_cap():
    """Use semantic versions rather than string order and cap scores at 100."""
    assert len(assess_assets("requests", "2.100.0", 10)) == 3
    assert assess_assets("requests", "2.100.0", 10)[0]["score"] == 100
    assert assess_assets("unknown", "1.0", 5) == []
    assert remediation_plan([])["actions"] == []


def test_router_rejects_unapproved_url_before_server_call():
    """Block arbitrary network destinations even when the model requests them."""
    router = ToolRouter()
    router.routes["fetch__fetch"] = (None, "fetch")
    with pytest.raises(ValueError, match="approved"):
        asyncio.run(router.call("fetch__fetch", {"url": "http://127.0.0.1/secrets"}))
    with pytest.raises(ValueError, match="Unknown"):
        asyncio.run(router.call("shell__execute", {}))
