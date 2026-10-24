"""Regression test for provider failures during an active MCP workflow."""

import asyncio

import httpx
import pytest
from openai import APIConnectionError, APITimeoutError, InternalServerError

from agent import main


def test_unavailable_api_cleans_up_before_raising_friendly_error(monkeypatch):
    """A 503 exits MCP contexts normally rather than nesting API tracebacks."""
    cleanup = []

    class Router:
        """Register task-group-like cleanup without starting server subprocesses."""

        async def connect(self, stack):
            """Require normal context exit rather than an API exception."""
            async def on_exit(exc_type, exc, traceback):
                assert exc_type is None
                cleanup.append(True)
            stack.push_async_exit(on_exit)

    async def unavailable(*args):
        """Simulate the exact provider status reported by the student."""
        response = httpx.Response(503, request=httpx.Request("POST", "https://example.invalid"))
        raise InternalServerError("high demand", response=response, body=None)

    monkeypatch.setenv("GEMINI_API_KEY", "fake-test-key")
    monkeypatch.setattr("sys.argv", ["agent.py"])
    monkeypatch.setattr("agent.ToolRouter", Router)
    monkeypatch.setattr("agent.run_agent", unavailable)
    with pytest.raises(RuntimeError, match="temporarily unavailable.*503"):
        asyncio.run(main())
    assert cleanup == [True]


@pytest.mark.parametrize("timeout", [True, False])
def test_transport_failures_distinguish_timeout_from_connection(monkeypatch, timeout):
    """Identify transport failure types without exposing raw exception secrets."""
    class Router:
        """Avoid real MCP processes in this provider-error regression."""

        async def connect(self, stack):
            """Simulate initialized servers."""

    async def failed_request(*args):
        """Simulate a timeout or connection failure with sensitive cause text."""
        request = httpx.Request("POST", "https://example.invalid")
        if timeout:
            raise APITimeoutError(request=request)
        raise APIConnectionError(request=request) from httpx.ConnectError("secret-test-key")

    monkeypatch.setenv("GEMINI_API_KEY", "fake-test-key")
    monkeypatch.setattr("sys.argv", ["agent.py"])
    monkeypatch.setattr("agent.ToolRouter", Router)
    monkeypatch.setattr("agent.run_agent", failed_request)
    expected = "timed out.*APITimeoutError" if timeout else "APIConnectionError; ConnectError"
    with pytest.raises(RuntimeError, match=expected) as caught:
        asyncio.run(main())
    assert "secret-test-key" not in str(caught.value)
