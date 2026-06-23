"""Unit tests for LangGraph node functions."""

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
    "nodes": [{"id": "OffsiteMiddleware"}, {"id": "Engine"}],
    "links": [{"source": "OffsiteMiddleware", "target": "Engine"}],
}


def _make_response(text="ok"):
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


@pytest.fixture(autouse=True)
def reset(tmp_config):
    cfg_mod._config = None
    gk_mod._gatekeeper = None
    yield
    cfg_mod._config = None
    gk_mod._gatekeeper = None


@pytest.fixture()
def workspace(tmp_config):
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
    (scrapy / "offsite.py").write_text("class OffsiteMiddleware:\n    def get_host_regex(self): pass\n")
    return root


def test_graph_reader_node(workspace):
    with patch("hw4.shared.gatekeeper.openai.OpenAI") as MockClient:
        MockClient.return_value.chat.completions.create.return_value = _make_response("module list")
        from hw4.agent.nodes import AgentState, graph_reader_node
        state: AgentState = {
            "graph_summary": "", "obsidian_context": "", "target_code": "",
            "bug_report": "", "patch": "", "token_log": [],
        }
        result = graph_reader_node(state)
    assert result["graph_summary"] == "module list"
    assert len(result["token_log"]) == 1
    assert result["token_log"][0]["node"] == "graph_reader"


def test_obsidian_reader_node(workspace):
    with patch("hw4.shared.gatekeeper.openai.OpenAI") as MockClient:
        MockClient.return_value.chat.completions.create.return_value = _make_response("obsidian result")
        from hw4.agent.nodes import AgentState, obsidian_reader_node
        state: AgentState = {
            "graph_summary": "summary", "obsidian_context": "", "target_code": "",
            "bug_report": "", "patch": "", "token_log": [],
        }
        result = obsidian_reader_node(state)
    assert result["obsidian_context"] == "obsidian result"


def test_targeted_code_reader_node(workspace):
    with patch("hw4.shared.gatekeeper.openai.OpenAI") as MockClient:
        MockClient.return_value.chat.completions.create.return_value = _make_response("analysis result")
        from hw4.agent.nodes import AgentState, targeted_code_reader_node
        state: AgentState = {
            "graph_summary": "", "obsidian_context": "context", "target_code": "",
            "bug_report": "", "patch": "", "token_log": [],
        }
        result = targeted_code_reader_node(state)
    assert "OffsiteMiddleware" in result["target_code"]
    assert result["obsidian_context"] == "analysis result"


def test_bug_identifier_node(workspace):
    with patch("hw4.shared.gatekeeper.openai.OpenAI") as MockClient:
        MockClient.return_value.chat.completions.create.return_value = _make_response("bug found")
        from hw4.agent.nodes import AgentState, bug_identifier_node
        state: AgentState = {
            "graph_summary": "", "obsidian_context": "analysis", "target_code": "",
            "bug_report": "", "patch": "", "token_log": [],
        }
        result = bug_identifier_node(state)
    assert result["bug_report"] == "bug found"


def test_fixer_node(workspace):
    with patch("hw4.shared.gatekeeper.openai.OpenAI") as MockClient:
        MockClient.return_value.chat.completions.create.return_value = _make_response("fixed code")
        from hw4.agent.nodes import AgentState, fixer_node
        state: AgentState = {
            "graph_summary": "", "obsidian_context": "", "target_code": "original",
            "bug_report": "bug report", "patch": "", "token_log": [],
        }
        result = fixer_node(state)
    assert result["patch"] == "fixed code"
