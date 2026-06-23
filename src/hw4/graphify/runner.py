"""Wraps the graphifyy CLI and exposes graph query helpers."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import networkx as nx

from hw4.shared.config import get_config


class GraphifyError(RuntimeError):
    pass


class GraphifyRunner:
    """Runs graphifyy on a Python project and provides graph query interface."""

    def __init__(
        self, source_dir: str | Path | None = None, output_dir: str | Path | None = None
    ) -> None:
        cfg = get_config()
        self._source = Path(source_dir or cfg.scrapy_source)
        self._output = Path(output_dir or cfg.artifacts_dir)
        self._graph_path = self._output / "graph.json"
        self._skip_if_exists = cfg.skip_graphify_if_exists
        self._graph: dict | None = None
        self._nx_graph: nx.DiGraph | None = None

    def run(self) -> None:
        """Invoke graphifyy CLI unless output already exists and skip is set."""
        if self._skip_if_exists and self._graph_path.exists():
            return
        self._output.mkdir(parents=True, exist_ok=True)
        cmd = ["graphifyy", str(self._source), "--output", str(self._output)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise GraphifyError(f"graphifyy failed:\n{result.stderr}")

    def load_graph(self) -> dict:
        """Return parsed graph.json as a dict."""
        if self._graph is None:
            self._graph = json.loads(self._graph_path.read_text())
        return self._graph

    def _nx(self) -> nx.DiGraph:
        if self._nx_graph is None:
            data = self.load_graph()
            edges_key = "links" if "links" in data else "edges"
            self._nx_graph = nx.node_link_graph(data, edges=edges_key)
        return self._nx_graph

    def get_neighbors(self, node: str) -> list[str]:
        """Return neighbors of a node by name (partial match ok)."""
        graph = self._nx()
        matches = [n for n in graph.nodes if node in str(n)]
        if not matches:
            return []
        return list(graph.neighbors(matches[0]))

    def top_by_degree(self, k: int = 10) -> list[tuple[str, int]]:
        """Return top-k nodes by total degree."""
        graph = self._nx()
        degrees = sorted(graph.degree(), key=lambda x: x[1], reverse=True)
        return [(str(n), d) for n, d in degrees[:k]]

    def pagerank(self) -> dict[str, float]:
        """Return PageRank scores for all nodes."""
        graph = self._nx()
        return {str(n): s for n, s in nx.pagerank(graph).items()}
