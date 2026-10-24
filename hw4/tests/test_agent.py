"""Exercise the Gemini-compatible tool loop without making paid API calls."""

import asyncio
from types import SimpleNamespace

import pytest
from openai.types.chat import ChatCompletion

from agent import run_agent


def completion(tool=None, arguments="{}", content=None):
    """Build a real SDK response shape for a model tool request or final text."""
    message = {"role": "assistant", "content": content}
    if tool:
        message["tool_calls"] = [{"id": "call_" + tool, "type": "function",
                                   "function": {"name": tool, "arguments": arguments}}]
    return ChatCompletion.model_validate({"id": "test", "object": "chat.completion",
        "created": 0, "model": "test", "choices": [{"index": 0, "message": message,
        "finish_reason": "tool_calls" if tool else "stop"}]})


def install_fake_client(monkeypatch, responses):
    """Replace the HTTP client while retaining SDK response parsing."""
    requests = []

    class FakeClient:
        """Async API client with deterministic queued model responses."""

        def __init__(self, **kwargs):
            """Record destination configuration without connecting to a network."""
            assert kwargs["base_url"].startswith("https://generativelanguage.googleapis.com/")
            self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

        async def __aenter__(self):
            """Enter the API lifetime."""
            return self

        async def __aexit__(self, *args):
            """Close the simulated client."""

        async def create(self, **kwargs):
            """Return the next queued model response and record the request."""
            requests.append(kwargs)
            return responses.pop(0)

    monkeypatch.setenv("GEMINI_API_KEY", "fake-test-key")
    monkeypatch.setattr("openai.AsyncOpenAI", FakeClient)
    return requests


class FakeRouter:
    """Model-side orchestration fixture, separate from real MCP integration tests."""

    def __init__(self):
        """Initialize per-run trace storage."""
        self.config = {"approved_urls": ["https://example.invalid/release"]}
        self.definitions = []
        self.trace = []

    async def call(self, name, arguments):
        """Return a successful tool result without a server process."""
        self.trace.append({"tool": name, "is_error": False})
        return {"is_error": False, "content": [{"type": "text", "text": "test evidence"}]}


def test_model_coordinates_both_servers_and_receives_tool_results(monkeypatch):
    """Return every result to the model before accepting its final report."""
    tools = ["fetch__fetch", "triage__list_assets", "triage__assess_assets",
             "triage__remediation_plan"]
    responses = [completion(tool) for tool in tools] + [completion(content="Completed report")]
    requests = install_fake_client(monkeypatch, responses)
    router = FakeRouter()
    assert asyncio.run(run_agent(router, "Triage", 6)) == "Completed report"
    assert [entry["tool"] for entry in router.trace] == tools
    tool_messages = [m for m in requests[-1]["messages"] if m["role"] == "tool"]
    assert len(tool_messages) == 4
    assert all("test evidence" in m["content"] for m in tool_messages)


def test_missing_tools_cannot_be_reported_as_completed(monkeypatch):
    """Stop at the turn limit if the model repeatedly skips required tools."""
    requests = install_fake_client(monkeypatch, [completion(content="Done") for _ in range(2)])
    with pytest.raises(RuntimeError, match="turn limit"):
        asyncio.run(run_agent(FakeRouter(), "Triage", 2))
    assert any("missing tools" in m.get("content", "") for m in requests[-1]["messages"])


def test_malformed_tool_json_is_returned_as_error_to_model(monkeypatch):
    """Allow the model to repair malformed arguments on a subsequent turn."""
    requests = install_fake_client(monkeypatch, [
        completion("triage__list_assets", arguments="broken"), completion(content="Done")])
    with pytest.raises(RuntimeError, match="turn limit"):
        asyncio.run(run_agent(FakeRouter(), "Triage", 2))
    assert any('"is_error": true' in m.get("content", "")
               for m in requests[-1]["messages"] if m["role"] == "tool")
