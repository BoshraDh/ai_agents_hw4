# PRD — HW4: Reverse Engineering, Debugging & Token-Efficient Agentic AI

**Version:** 1.01  
**Author:** Boshra Dhamshy  
**Course:** AI Agents Orchestration  
**Date:** 2026-06-24  
**Status:** Implementation complete. Live run pending (requires ANTHROPIC_API_KEY + scrapy clone).

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

| # | Goal | Status |
|---|------|--------|
| G1 | Build knowledge graph of scrapy codebase using Graphify | Pending live run |
| G2 | Document architecture in Obsidian vault (index + hot pages) | Static pages done; dynamic pending |
| G3 | Produce block diagram + OOP summary of scrapy | Done (`obsidian/architecture_blocks.md`, `oop_summary.md`) |
| G4 | LangGraph agent finds the real bug using graph-guided strategy | Agent implemented and tested |
| G5 | Token savings: graph-guided uses ≥ 5× fewer tokens than naive | Expected ~63×; live measurement pending |
| G6 | Original extension: PageRank-based hot-spot ranking | Implemented in `GraphifyRunner.pagerank()` |

---

## 3. Bug Target

**Project:** scrapy  
**Bug ID:** scrapy-1  
**File:** `scrapy/spidermw/offsite.py`  
**Class:** `OffsiteMiddleware`  
**Method:** `get_host_regex`  

**Description:** When `allowed_domains` contains `None`, the domain-matching logic raises
`TypeError` because `None` cannot be processed by `re.compile().match()`.

**Root cause:** Missing `filter(None, ...)` guard before iterating `allowed_domains`.

**Fix:** Add `filter(None, allowed_domains)` before the list comprehension.

See `obsidian/fix_before_after.md` for full before/after.

---

## 4. User Workflow

```bash
# Setup
cp .env-example .env        # add ANTHROPIC_API_KEY
uv sync
git clone https://github.com/scrapy/scrapy data/scrapy
cd data/scrapy && git checkout 0f214b6a3a9e26e32e5b64a2a5e22c8dc28fce0e && cd ../..

# Run full pipeline
uv run python -m hw4.sdk.sdk

# Run agents individually
uv run python -m hw4.baseline.naive_agent

# Tests & lint
uv run pytest tests/ --cov=src/hw4   # 89% coverage, 42 tests
uv run ruff check src/               # 0 violations
```

---

## 5. Non-Goals

- Not a general-purpose bug-finding tool (single bug, single project)
- Not a production scraping application
- UI or web interface out of scope

---

## 6. Constraints & Standards (from software_submission_guidelines-V3)

| Constraint | Value | Status |
|-----------|-------|--------|
| Package manager | `uv` only | Done |
| Max lines per file | 150 | All files ≤ 150 lines |
| Architecture | SDK layer mandatory | `src/hw4/sdk/sdk.py` |
| External API calls | Through `ApiGatekeeper` only | `src/hw4/shared/gatekeeper.py` |
| Config values | From `config/` JSON files only | `config/setup.json`, `config/rate_limits.json` |
| Test coverage | ≥ 85% | **89.29%** |
| Linter | `ruff` — 0 violations | **0 violations** |
| Version | Starts at 1.00 | `src/hw4/shared/version.py` |
| Secrets | `.env` only, `.env-example` provided | Done |
| OOP | No code duplication | Done |

---

## 7. Deliverables

| File | Status |
|------|--------|
| `artifacts/graph.json` | Pending (needs scrapy clone) |
| `artifacts/GRAPH_REPORT.md` | Pending |
| `obsidian/index.md` | Pending (auto-generated) |
| `obsidian/hot.md` | Pending (auto-generated) |
| `obsidian/architecture_blocks.md` | Done |
| `obsidian/oop_summary.md` | Done |
| `obsidian/investigation_log.md` | Done |
| `obsidian/fix_before_after.md` | Done |
| `reports/bug_analysis.md` | Done |
| `reports/token_comparison.md` | Template done; live numbers pending |
| `src/hw4/` | Done |
| `tests/` | Done (42 tests, 89% coverage) |
| `README.md` | Done |
