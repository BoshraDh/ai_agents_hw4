"""Unit tests for agent tools."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

import hw4.shared.config as cfg_mod
from hw4.agent.tools import (
    find_files_mentioning,
    get_top_pagerank_nodes,
    read_obsidian_page,
    read_source_file,
    summarize_graph_for_prompt,
)
from hw4.graphify.runner import GraphifyRunner


MINIMAL_GRAPH = {
    "directed": True,
    "multigraph": False,
    "graph": {},
    "nodes": [{"id": "A"}, {"id": "B"}, {"id": "C"}],
    "links": [{"source": "A", "target": "B"}, {"source": "B", "target": "C"}],
}


@pytest.fixture()
def runner_with_graph(tmp_path):
    arts = tmp_path / "artifacts"
    arts.mkdir()
    (arts / "graph.json").write_text(json.dumps(MINIMAL_GRAPH))
    return GraphifyRunner(source_dir=str(tmp_path / "scrapy"), output_dir=str(arts))


def test_read_obsidian_page_missing(tmp_path):
    result = read_obsidian_page("nonexistent", vault_dir=str(tmp_path))
    assert "not found" in result


def test_read_obsidian_page_found(tmp_path):
    (tmp_path / "index.md").write_text("# Index content")
    result = read_obsidian_page("index", vault_dir=str(tmp_path))
    assert "Index content" in result


def test_read_source_file_missing(tmp_path, tmp_config):
    cfg_mod._config = None
    result = read_source_file("nonexistent.py", source_root=str(tmp_path))
    assert "not found" in result


def test_read_source_file_found(tmp_path, tmp_config):
    cfg_mod._config = None
    (tmp_path / "test.py").write_text("def hello(): pass")
    result = read_source_file("test.py", source_root=str(tmp_path))
    assert "hello" in result


def test_summarize_graph_for_prompt(runner_with_graph):
    runner_with_graph.load_graph()
    summary = summarize_graph_for_prompt(runner_with_graph, k=2)
    assert "Top modules" in summary
    assert "degree=" in summary


def test_get_top_pagerank_nodes(runner_with_graph):
    runner_with_graph.load_graph()
    top = get_top_pagerank_nodes(runner_with_graph, k=2)
    assert len(top) == 2
    assert all(isinstance(score, float) for _, score in top)


def test_find_files_mentioning(tmp_path, tmp_config):
    cfg_mod._config = None
    py_dir = tmp_path / "scrapy"
    py_dir.mkdir()
    (py_dir / "a.py").write_text("allowed_domains = ['example.com']")
    (py_dir / "b.py").write_text("unrelated code here")
    results = find_files_mentioning("allowed_domains", source_root=str(tmp_path))
    assert any("a.py" in r for r in results)
    assert not any("b.py" in r for r in results)
