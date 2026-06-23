"""Unit tests for ApiGatekeeper — LLM is mocked."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

import hw4.shared.config as cfg_mod
import hw4.shared.gatekeeper as gk_mod


@pytest.fixture(autouse=True)
def reset_gatekeeper(tmp_config):
    gk_mod._gatekeeper = None
    cfg_mod._config = None
    yield
    gk_mod._gatekeeper = None
    cfg_mod._config = None


def _make_response(input_tokens: int = 10, output_tokens: int = 5, text: str = "ok"):
    usage = MagicMock()
    usage.input_tokens = input_tokens
    usage.output_tokens = output_tokens
    content = MagicMock()
    content.text = text
    resp = MagicMock()
    resp.usage = usage
    resp.content = [content]
    return resp


def test_chat_complete_returns_text(monkeypatch):
    with patch("hw4.shared.gatekeeper.anthropic.Anthropic") as MockClient:
        mock_client = MockClient.return_value
        mock_client.messages.create.return_value = _make_response(text="hello")
        from hw4.shared.gatekeeper import ApiGatekeeper
        gk = ApiGatekeeper()
        result = gk.chat_complete([{"role": "user", "content": "test"}], "model", 100)
    assert result == "hello"


def test_token_tracking(monkeypatch):
    with patch("hw4.shared.gatekeeper.anthropic.Anthropic") as MockClient:
        mock_client = MockClient.return_value
        mock_client.messages.create.return_value = _make_response(input_tokens=20, output_tokens=8)
        from hw4.shared.gatekeeper import ApiGatekeeper
        gk = ApiGatekeeper()
        gk.chat_complete([{"role": "user", "content": "x"}], "model", 100)
    summary = gk.token_summary()
    assert summary["prompt_tokens"] == 20
    assert summary["completion_tokens"] == 8
    assert summary["total_tokens"] == 28


def test_reset_counts(monkeypatch):
    with patch("hw4.shared.gatekeeper.anthropic.Anthropic") as MockClient:
        mock_client = MockClient.return_value
        mock_client.messages.create.return_value = _make_response(10, 5)
        from hw4.shared.gatekeeper import ApiGatekeeper
        gk = ApiGatekeeper()
        gk.chat_complete([{"role": "user", "content": "x"}], "model", 100)
        gk.reset_counts()
    assert gk.token_summary()["total_tokens"] == 0
