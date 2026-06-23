# PRD — HW4: Reverse Engineering, Debugging & Token-Efficient Agentic AI

**Version:** 1.00  
**Author:** Boshra Dhamshy  
**Course:** AI Agents Orchestration  
**Date:** 2026-06-24

---

## 1. Background & Motivation

Debugging unfamiliar, large-scale codebases is expensive in time and LLM tokens. This project
demonstrates that a knowledge-graph-guided AI agent can locate and fix a real bug in a 10,000+
line Python project while consuming dramatically fewer tokens than a naive "read everything" approach.

The chosen bug repository is [BugsInPy](https://github.com/soarsmu/BugsInPy), a curated
database of real confirmed bugs in popular Python projects. The chosen project is **scrapy** —
a production-grade web-scraping framework with 40 documented bugs.

---

## 2. Goals

| # | Goal | Metric |
|---|------|--------|
| G1 | Build knowledge graph of scrapy codebase using Graphify | `artifacts/graph.json` exists, ≥ 90% modules covered |
| G2 | Document architecture in Obsidian vault (index + hot pages) | `obsidian/index.md` + `obsidian/hot.md` complete |
| G3 | Produce block diagram + OOP summary of scrapy | `obsidian/architecture_blocks.md` + `obsidian/oop_summary.md` |
| G4 | LangGraph agent finds the real bug using graph-guided strategy | Bug correctly identified and patched |
| G5 | Token savings: graph-guided uses ≥ 5× fewer tokens than naive | Documented in `reports/token_comparison.md` |
| G6 | Original extension: PageRank-based hot-spot ranking | `obsidian/hot.md` generated dynamically |

---

## 3. Bug Target

**Project:** scrapy  
**Bug ID:** scrapy-1  
**File:** `scrapy/spidermw/offsite.py`  
**Class:** `OffsiteMiddleware`  
**Method:** `should_follow`  

**Description:** When `allowed_domains` contains `None`, the domain-matching logic raises
`TypeError` because `None` cannot be processed by the URL-matching utilities.  

**Root cause:** Missing None-filter on `allowed_domains` before construction of the regex.  

**Fix:** Add `filter(None, ...)` guard before processing `allowed_domains`.

---

## 4. User Workflow

```
uv run python -m hw4.sdk.sdk          # run full graph-guided agent pipeline
uv run python -m hw4.baseline.naive_agent  # run naive baseline for comparison
uv run pytest tests/ --cov=src/hw4   # run test suite
uv run ruff check src/               # lint check
```

---

## 5. Non-Goals

- Not a general-purpose bug-finding tool (single bug, single project)
- Not a production scraping application
- UI or web interface out of scope

---

## 6. Constraints & Standards (from software_submission_guidelines-V3)

| Constraint | Value |
|-----------|-------|
| Package manager | `uv` only |
| Max lines per file | 150 |
| Architecture | SDK layer mandatory |
| External API calls | Through `ApiGatekeeper` only |
| Config values | From `config/` JSON files only |
| Test coverage | ≥ 85% |
| Linter | `ruff` — 0 violations |
| Version | Starts at 1.00 |
| Secrets | `.env` only, `.env-example` provided |

---

## 7. Deliverables

- `artifacts/graph.json` — Graphify knowledge graph
- `artifacts/GRAPH_REPORT.md` — Graphify analysis report
- `obsidian/` — full Obsidian vault (6 pages minimum)
- `reports/bug_analysis.md` — bug investigation log
- `reports/token_comparison.md` — naive vs graph-guided token table
- `src/hw4/` — full SDK + agent + baseline implementation
- `tests/` — ≥ 85% coverage
- `README.md` — user manual
