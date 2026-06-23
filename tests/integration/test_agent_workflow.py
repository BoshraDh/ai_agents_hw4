"""Integration test: full agent pipeline with mocked LLM."""

from __future__ import annotations

import json
from pathlib import Path
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
    ],
}


@pytest.fixture(autouse=True)
def reset_singletons(tmp_config):
    cfg_mod._config = None
    gk_mod._gatekeeper = None
    yield
    cfg_mod._config = None
    gk_mod._gatekeeper = None


@pytest.fixture()
def setup_workspace(tmp_config):
    """Create minimal workspace: graph.json + obsidian pages + scrapy stub."""
    root = tmp_config
    artifacts = root / "artifacts"
    artifacts.mkdir(exist_ok=True)
    (artifacts / "graph.json").write_text(json.dumps(MINIMAL_GRAPH))

    obsidian = root / "obsidian"
    obsidian.mkdir(exist_ok=True)
    (obsidian / "index.md").write_text("# Index\nTop nodes: OffsiteMiddleware")
    (obsidian / "hot.md").write_text("# Hot\nOffsiteMiddleware is suspect")

    scrapy_dir = root / "scrapy" / "scrapy" / "spidermw"
    scrapy_dir.mkdir(parents=True, exist_ok=True)
    (scrapy_dir / "offsite.py").write_text(
        "class OffsiteMiddleware:\n    def should_follow(self, request, spider):\n        return True\n"
    )
    return root


def _make_response(text="fixed"):
    usage = MagicMock()
    usage.prompt_tokens = 10
    usage.completion_tokens = 5
    message = MagicMock()
    message.content = text
    choice = MagicMock()
    choice.message = message
    resp = MagicMock()
    resp.usage = usage
    resp.choices = [choice]
    return resp


def test_full_workflow_completes(setup_workspace, monkeypatch):
    with patch("hw4.shared.gatekeeper.openai.OpenAI") as MockClient:
        MockClient.return_value.chat.completions.create.return_value = _make_response()
        from hw4.agent.workflow import run_agent_workflow
        state = run_agent_workflow()
    assert "patch" in state
    assert "bug_report" in state
    assert len(state["token_log"]) == 5
