"""Unit tests for SDK entry point."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

import hw4.shared.config as cfg_mod
import hw4.shared.gatekeeper as gk_mod


MINIMAL_GRAPH = {
    "directed": True,
    "multigraph": False,
    "graph": {},
    "nodes": [{"id": "OffsiteMiddleware"}, {"id": "Engine"}, {"id": "Spider"}],
    "links": [
        {"source": "OffsiteMiddleware", "target": "Engine"},
        {"source": "Engine", "target": "Spider"},
        {"source": "Spider", "target": "OffsiteMiddleware"},
    ],
}


@pytest.fixture(autouse=True)
def reset(tmp_config):
    cfg_mod._config = None
    gk_mod._gatekeeper = None
    yield
    cfg_mod._config = None
    gk_mod._gatekeeper = None


@pytest.fixture()
def full_workspace(tmp_config):
    root = tmp_config
    arts = root / "artifacts"
    arts.mkdir(exist_ok=True)
    (arts / "graph.json").write_text(json.dumps(MINIMAL_GRAPH))
    obsidian = root / "obsidian"
    obsidian.mkdir(exist_ok=True)
    (obsidian / "index.md").write_text("# Index")
    (obsidian / "hot.md").write_text("# Hot")
    scrapy = root / "scrapy" / "scrapy" / "spidermw"
    scrapy.mkdir(parents=True, exist_ok=True)
    (scrapy / "offsite.py").write_text("class OffsiteMiddleware:\n    pass\n")
    (root / "reports").mkdir(exist_ok=True)
    return root


def _make_response(text="ok"):
    usage = MagicMock()
    usage.input_tokens = 10
    usage.output_tokens = 5
    content = MagicMock()
    content.text = text
    resp = MagicMock()
    resp.usage = usage
    resp.content = [content]
    return resp


def test_run_graph_agent(full_workspace):
    with patch("hw4.shared.gatekeeper.anthropic.Anthropic") as MockClient:
        MockClient.return_value.messages.create.return_value = _make_response()
        from hw4.sdk.sdk import run_graph_agent
        result = run_graph_agent()
    assert "state" in result
    assert "token_summary" in result


def test_run_baseline_agent(full_workspace):
    with patch("hw4.shared.gatekeeper.anthropic.Anthropic") as MockClient:
        MockClient.return_value.messages.create.return_value = _make_response("bug found")
        from hw4.sdk.sdk import run_baseline_agent
        result = run_baseline_agent()
    assert "result" in result
    assert "counter" in result


def test_run_comparison_writes_report(full_workspace):
    report_path = full_workspace / "reports" / "comparison.md"
    with patch("hw4.shared.gatekeeper.anthropic.Anthropic") as MockClient:
        MockClient.return_value.messages.create.return_value = _make_response()
        from hw4.sdk.sdk import run_comparison
        text = run_comparison(str(report_path))
    assert report_path.exists()
    assert "Graph-guided" in text
