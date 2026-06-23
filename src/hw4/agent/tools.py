"""Read-only tools used by agent nodes to load graph and code context."""

from __future__ import annotations

from pathlib import Path

from hw4.graphify.runner import GraphifyRunner
from hw4.shared.config import get_config
from hw4.shared.constants import OBSIDIAN_DIR


def read_obsidian_page(page: str, vault_dir: str | None = None) -> str:
    """Read a single Obsidian markdown page by name (without .md)."""
    base = Path(vault_dir or OBSIDIAN_DIR)
    target = base / f"{page}.md"
    if not target.exists():
        return f"[page '{page}' not found]"
    return target.read_text()


def read_source_file(relative_path: str, source_root: str | None = None) -> str:
    """Read a Python source file from the scrapy codebase."""
    cfg = get_config()
    root = Path(source_root or cfg.scrapy_source)
    target = root / relative_path
    if not target.exists():
        return f"[file '{relative_path}' not found]"
    return target.read_text()


def summarize_graph_for_prompt(runner: GraphifyRunner, k: int = 15) -> str:
    """Return a compact text summary of the top-k graph nodes."""
    top = runner.top_by_degree(k)
    lines = ["Top modules by connectivity:"]
    for name, degree in top:
        lines.append(f"  {name} (degree={degree})")
    return "\n".join(lines)


def get_top_pagerank_nodes(runner: GraphifyRunner, k: int = 10) -> list[tuple[str, float]]:
    """Return top-k nodes by PageRank score."""
    pr = runner.pagerank()
    return sorted(pr.items(), key=lambda x: x[1], reverse=True)[:k]


def find_files_mentioning(keyword: str, source_root: str | None = None) -> list[str]:
    """Return relative paths of .py files whose content mentions keyword."""
    cfg = get_config()
    root = Path(source_root or cfg.scrapy_source)
    matches: list[str] = []
    for py_file in root.rglob("*.py"):
        try:
            if keyword in py_file.read_text():
                matches.append(str(py_file.relative_to(root)))
        except (UnicodeDecodeError, OSError):
            continue
    return matches
