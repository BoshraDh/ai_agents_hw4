"""Unit tests for naive baseline agent."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import hw4.shared.config as cfg_mod
import hw4.shared.gatekeeper as gk_mod


def _make_response(text="found bug", input_tokens=1000, output_tokens=200):
    usage = MagicMock()
    usage.prompt_tokens = input_tokens
    usage.completion_tokens = output_tokens
    message = MagicMock()
    message.content = text
    choice = MagicMock()
    choice.message = message
    resp = MagicMock()
    resp.usage = usage
    resp.choices = [choice]
    return resp


@pytest.fixture(autouse=True)
def reset(tmp_config):
    cfg_mod._config = None
    gk_mod._gatekeeper = None
    yield
    cfg_mod._config = None
    gk_mod._gatekeeper = None


@pytest.fixture()
def scrapy_stub(tmp_config):
    root = tmp_config
    scrapy = root / "scrapy"
    scrapy.mkdir(exist_ok=True)
    (scrapy / "offsite.py").write_text("class OffsiteMiddleware:\n    def get_host_regex(self): pass\n")
    (scrapy / "engine.py").write_text("class Engine:\n    pass\n")
    return root


def test_run_naive_returns_dict(scrapy_stub):
    with patch("hw4.shared.gatekeeper.openai.OpenAI") as MockClient:
        MockClient.return_value.chat.completions.create.return_value = _make_response(
            "OffsiteMiddleware bug found", input_tokens=5000, output_tokens=300
        )
        from hw4.baseline.naive_agent import run_naive
        result = run_naive()
    assert "response" in result
    assert "total_tokens" in result
    assert result["total_tokens"] > 0


def test_run_naive_tracks_tokens(scrapy_stub):
    with patch("hw4.shared.gatekeeper.openai.OpenAI") as MockClient:
        MockClient.return_value.chat.completions.create.return_value = _make_response(
            input_tokens=8000, output_tokens=400
        )
        from hw4.baseline.naive_agent import run_naive
        result = run_naive()
    assert result["prompt_tokens"] == 8000
    assert result["completion_tokens"] == 400


def test_collect_source_counts_files(scrapy_stub):
    from hw4.baseline.naive_agent import collect_source
    code, file_count, total_lines = collect_source(scrapy_stub / "scrapy")
    assert file_count == 2
    assert total_lines > 0
    assert "OffsiteMiddleware" in code
