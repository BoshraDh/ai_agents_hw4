"""Unit tests for GraphifyRunner (no real graphifyy call)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

import hw4.shared.config as cfg_mod
from hw4.graphify.runner import GraphifyRunner


@pytest.fixture(autouse=True)
def reset_config(tmp_config):
    cfg_mod._config = None
    yield
    cfg_mod._config = None


def test_load_graph_returns_dict(tmp_graph, tmp_config):
    cfg_mod._config = None
    runner = GraphifyRunner(
        source_dir=str(tmp_graph / "scrapy"),
        output_dir=str(tmp_graph / "artifacts"),
    )
    graph = runner.load_graph()
    assert isinstance(graph, dict)
    assert "nodes" in graph


def test_top_by_degree_returns_k(tmp_graph, tmp_config):
    cfg_mod._config = None
    runner = GraphifyRunner(
        source_dir=str(tmp_graph / "scrapy"),
        output_dir=str(tmp_graph / "artifacts"),
    )
    runner.load_graph()
    top = runner.top_by_degree(3)
    assert len(top) == 3
    assert all(isinstance(n, str) for n, _ in top)


def test_get_neighbors_offsite(tmp_graph, tmp_config):
    cfg_mod._config = None
    runner = GraphifyRunner(
        source_dir=str(tmp_graph / "scrapy"),
        output_dir=str(tmp_graph / "artifacts"),
    )
    runner.load_graph()
    neighbors = runner.get_neighbors("OffsiteMiddleware")
    assert len(neighbors) > 0


def test_pagerank_returns_scores(tmp_graph, tmp_config):
    cfg_mod._config = None
    runner = GraphifyRunner(
        source_dir=str(tmp_graph / "scrapy"),
        output_dir=str(tmp_graph / "artifacts"),
    )
    runner.load_graph()
    pr = runner.pagerank()
    assert isinstance(pr, dict)
    assert all(isinstance(v, float) for v in pr.values())


def test_skip_if_exists(tmp_graph, tmp_config):
    cfg_mod._config = None
    runner = GraphifyRunner(
        source_dir=str(tmp_graph / "scrapy"),
        output_dir=str(tmp_graph / "artifacts"),
    )
    with patch("subprocess.run") as mock_run:
        runner.run()
        mock_run.assert_not_called()
