"""Unit tests for TokenCounter and Comparator."""

from __future__ import annotations

from pathlib import Path

import pytest

from hw4.analysis.comparator import Comparator
from hw4.analysis.token_counter import NodeRecord, TokenCounter


def test_node_record_total():
    r = NodeRecord("test_node", 100, 50)
    assert r.total == 150


def test_counter_accumulates():
    c = TokenCounter()
    c.add("node_a", 100, 40)
    c.add("node_b", 200, 60)
    assert c.total_prompt == 300
    assert c.total_completion == 100
    assert c.total == 400


def test_counter_files_read():
    c = TokenCounter()
    c.add("graph_reader", 50, 20)
    c.add("targeted_code_reader", 200, 80)
    c.add("bug_identifier", 100, 50)
    assert c.files_read == 1


def test_counter_summary_keys():
    c = TokenCounter()
    c.add("n", 10, 5)
    s = c.summary()
    assert set(s.keys()) == {"prompt_tokens", "completion_tokens", "total_tokens", "files_read", "node_count"}


def test_comparator_reduction_factor():
    graph = TokenCounter()
    graph.add("node", 500, 200)
    naive = TokenCounter()
    naive.add("node", 50000, 2000)
    cmp = Comparator(graph, naive)
    factor = cmp.reduction_factor()
    assert factor > 5


def test_comparator_writes_report(tmp_path):
    graph = TokenCounter()
    graph.add("node", 500, 200)
    naive = TokenCounter()
    naive.add("node", 50000, 2000)
    cmp = Comparator(graph, naive)
    report_path = tmp_path / "report.md"
    text = cmp.write_report(report_path)
    assert "Graph-guided" in text
    assert "Naive" in text
    assert report_path.exists()
