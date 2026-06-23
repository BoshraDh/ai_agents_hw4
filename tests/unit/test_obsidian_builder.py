"""Unit tests for ObsidianBuilder."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

import hw4.shared.config as cfg_mod
from hw4.graphify.obsidian_builder import ObsidianBuilder
from hw4.graphify.runner import GraphifyRunner


@pytest.fixture(autouse=True)
def reset_config(tmp_config):
    cfg_mod._config = None
    yield
    cfg_mod._config = None


@pytest.fixture()
def mock_runner(tmp_graph) -> GraphifyRunner:
    runner = GraphifyRunner(
        source_dir=str(tmp_graph / "scrapy"),
        output_dir=str(tmp_graph / "artifacts"),
    )
    runner.load_graph()
    return runner


def test_build_all_creates_index(tmp_graph, mock_runner):
    vault = tmp_graph / "obsidian"
    builder = ObsidianBuilder(runner=mock_runner, vault_dir=str(vault))
    builder.build_all()
    assert (vault / "index.md").exists()


def test_build_all_creates_hot(tmp_graph, mock_runner):
    vault = tmp_graph / "obsidian"
    builder = ObsidianBuilder(runner=mock_runner, vault_dir=str(vault))
    builder.build_all()
    assert (vault / "hot.md").exists()


def test_index_contains_top_nodes(tmp_graph, mock_runner):
    vault = tmp_graph / "obsidian"
    builder = ObsidianBuilder(runner=mock_runner, vault_dir=str(vault))
    builder.build_all()
    content = (vault / "index.md").read_text()
    assert "Top Modules" in content


def test_hot_contains_pagerank(tmp_graph, mock_runner):
    vault = tmp_graph / "obsidian"
    builder = ObsidianBuilder(runner=mock_runner, vault_dir=str(vault))
    builder.build_all()
    content = (vault / "hot.md").read_text()
    assert "PageRank" in content


def test_write_architecture_blocks(tmp_graph, mock_runner):
    vault = tmp_graph / "obsidian"
    builder = ObsidianBuilder(runner=mock_runner, vault_dir=str(vault))
    builder.write_architecture_blocks()
    content = (vault / "architecture_blocks.md").read_text()
    assert "Engine" in content
