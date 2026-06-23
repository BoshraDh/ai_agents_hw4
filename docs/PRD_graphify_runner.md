# PRD — Graphify Runner Mechanism

**Version:** 1.00  
**Date:** 2026-06-24

---

## 1. Purpose

Wrap the `graphifyy` CLI to run on the scrapy codebase and expose its output
(`graph.json`, `GRAPH_REPORT.md`) for consumption by the Obsidian builder and
LangGraph agent.

---

## 2. Inputs / Outputs

| Item | Path |
|------|------|
| Input codebase | `data/scrapy/` |
| Output graph | `artifacts/graph.json` |
| Output report | `artifacts/GRAPH_REPORT.md` |
| Output HTML viz | `artifacts/graph.html` (optional) |

---

## 3. Interface

```python
from hw4.graphify.runner import GraphifyRunner

runner = GraphifyRunner(source_dir="data/scrapy", output_dir="artifacts")
runner.run()                          # invokes graphifyy CLI
graph = runner.load_graph()           # returns dict
neighbors = runner.get_neighbors("OffsiteMiddleware")  # returns list[str]
top_nodes = runner.top_by_degree(k=10)  # returns list[(node, degree)]
```

---

## 4. Constraints

- Must not shell-inject user input into the CLI command
- If `artifacts/graph.json` already exists, skip re-running (cached)
- Raise `GraphifyError` on CLI failure with original stderr

---

## 5. Success Criteria

- `artifacts/graph.json` contains ≥ 50 nodes
- `get_neighbors("OffsiteMiddleware")` returns non-empty list
- `top_by_degree(10)` returns exactly 10 entries
