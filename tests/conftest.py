"""Shared pytest fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


MINIMAL_GRAPH = {
    "directed": True,
    "multigraph": False,
    "graph": {},
    "nodes": [
        {"id": "OffsiteMiddleware"},
        {"id": "CrawlerRunner"},
        {"id": "Engine"},
        {"id": "Spider"},
        {"id": "Downloader"},
    ],
    "links": [
        {"source": "CrawlerRunner", "target": "Engine"},
        {"source": "Engine", "target": "Spider"},
        {"source": "Engine", "target": "Downloader"},
        {"source": "OffsiteMiddleware", "target": "Spider"},
        {"source": "OffsiteMiddleware", "target": "Engine"},
    ],
}


@pytest.fixture()
def tmp_graph(tmp_path: Path) -> Path:
    """Write a minimal graph.json and return its directory."""
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    (artifacts / "graph.json").write_text(json.dumps(MINIMAL_GRAPH))
    return tmp_path


@pytest.fixture()
def tmp_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create minimal config files and patch the config singleton."""
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    setup = {
        "project": {"name": "test", "version": "1.00", "scrapy_bug_id": "scrapy-1", "scrapy_buggy_commit": "abc"},
        "paths": {"scrapy_source": str(tmp_path / "scrapy"), "artifacts_dir": str(tmp_path / "artifacts"), "obsidian_dir": str(tmp_path / "obsidian"), "reports_dir": str(tmp_path / "reports")},
        "graphify": {"tool": "graphifyy", "graph_json": "artifacts/graph.json", "report_md": "artifacts/GRAPH_REPORT.md", "skip_if_exists": True},
        "agent": {"model": "claude-haiku-4-5-20251001", "max_tokens_per_node": 100, "max_files_per_node": 3, "top_k_hot_nodes": 3},
        "baseline": {"model": "claude-haiku-4-5-20251001", "max_tokens": 100},
    }
    rate = {
        "anthropic": {"requests_per_minute": 10, "tokens_per_minute": 40000, "max_retries": 1, "retry_base_delay_seconds": 0.1, "retry_max_delay_seconds": 1.0},
        "queue": {"max_concurrent": 1, "timeout_seconds": 10},
    }
    (cfg_dir / "setup.json").write_text(json.dumps(setup))
    (cfg_dir / "rate_limits.json").write_text(json.dumps(rate))

    import hw4.shared.config as cfg_mod
    cfg_mod._config = None
    monkeypatch.chdir(tmp_path)
    return tmp_path
