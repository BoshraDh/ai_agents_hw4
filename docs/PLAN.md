# PLAN — Architecture & Implementation

**Version:** 1.01  
**Date:** 2026-06-24  
**Status:** Implementation complete. Verified: 42 tests pass, 89% coverage, ruff 0 violations.

---

## 1. System Architecture (C4 — Context Level)

```
User / CLI
    |
    v
SDK Layer  (hw4.sdk.sdk — sole entry point)
    |
    +-- GraphifyRunner  ->  Obsidian Builder
    |
    +-- LangGraph Agent (5 nodes)
    |       |
    |       v
    |   API Gatekeeper  ->  Anthropic API
    |
    +-- Naive Baseline
            |
            v
        API Gatekeeper  ->  Anthropic API
```

---

## 2. Component Breakdown

### 2.1 Graphify Runner (`src/hw4/graphify/runner.py`)
- Wraps `graphifyy` CLI; caches if `artifacts/graph.json` exists
- Exposes: `run()`, `load_graph()`, `get_neighbors(node)`, `top_by_degree(k)`, `pagerank()`
- Uses NetworkX + scipy for PageRank computation

### 2.2 Obsidian Builder (`src/hw4/graphify/obsidian_builder.py`)
- Reads graph via `GraphifyRunner`; runs PageRank
- Writes: `obsidian/index.md` (top-20 nodes by degree)
- Writes: `obsidian/hot.md` (top-K nodes by PageRank — the extension from task 5.6)
- Also writes static pages: `architecture_blocks.md`, `oop_summary.md`

### 2.3 LangGraph Agent (`src/hw4/agent/`)
Five-node state machine (all LLM calls via `ApiGatekeeper`):

```
graph_reader_node          (reads graph summary ~200 tokens)
    -> obsidian_reader_node    (reads hot.md + index.md ~400 tokens)
        -> targeted_code_reader_node  (reads offsite.py ~650 tokens)
            -> bug_identifier_node    (produces bug report ~380 tokens)
                -> fixer_node         (produces patch ~290 tokens)
```

State type: `AgentState` (TypedDict with 6 keys)

### 2.4 Naive Baseline (`src/hw4/baseline/naive_agent.py`)
- Collects all `.py` files from `data/scrapy/` (capped at 80K chars)
- Single LLM call asking for bug location
- Used only for token comparison

### 2.5 API Gatekeeper (`src/hw4/shared/gatekeeper.py`)
- Singleton; all LLM traffic routes here
- Rate limiting: tracks call timestamps, sleeps if RPM exceeded
- Retry: exponential backoff on `RateLimitError` / `APIError`
- Accumulates `total_prompt_tokens` + `total_completion_tokens`
- Rate limits read from `config/rate_limits.json` (never hardcoded)

### 2.6 Config Manager (`src/hw4/shared/config.py`)
- Singleton; loads `config/setup.json` + `config/rate_limits.json`
- Typed properties — no dict access outside this module

---

## 3. Data Flow (end-to-end)

```
data/scrapy/ (buggy commit 0f214b6a)
    -> graphifyy CLI
        -> artifacts/graph.json
            -> ObsidianBuilder
                -> obsidian/index.md + hot.md
                    -> LangGraph agent (5 nodes, ~2,000 tokens total)
                        -> bug found + patch generated
                            -> reports/token_comparison.md
```

---

## 4. Decisions (ADRs)

### ADR-001: LangGraph over CrewAI
**Decision:** LangGraph.  
**Reason:** Explicit per-node step control makes token counting straightforward.
Assignment recommends it for limited free API accounts.

### ADR-002: scrapy over thefuck
**Decision:** scrapy (Bug #1).  
**Reason:** Rich multi-component architecture (Engine/Spider/Middleware/Pipeline/Scheduler)
produces a meaningful knowledge graph. User explicitly rejected thefuck.

### ADR-003: uv as sole package manager
**Decision:** uv exclusively.  
**Reason:** Required by `software_submission_guidelines-V3`. `uv.lock` for reproducibility.

### ADR-004: scipy added for PageRank
**Decision:** Added `scipy` to dependencies.  
**Reason:** NetworkX 3.6.1 delegates `nx.pagerank()` to scipy when available.
Without it, pagerank raises an error on directed graphs.

### ADR-005: NetworkX node_link_graph edges key auto-detection
**Decision:** Detect `"links"` vs `"edges"` key in `_nx()`.  
**Reason:** NetworkX 3.x changed the default key from `"links"` to `"edges"`.
Graphify may output either format depending on version.

---

## 5. File Size Budget (all ≤ 150 lines)

| File | Lines |
|------|-------|
| `sdk/sdk.py` | 84 |
| `shared/gatekeeper.py` | 92 |
| `shared/config.py` | 80 |
| `agent/nodes.py` | 130 |
| `agent/workflow.py` | 40 |
| `agent/tools.py` | 60 |
| `agent/prompts.py` | 42 |
| `graphify/runner.py` | 72 |
| `graphify/obsidian_builder.py` | 117 |
| `baseline/naive_agent.py` | 55 |
| `analysis/token_counter.py` | 44 |
| `analysis/comparator.py` | 59 |

---

## 6. Testing Strategy (TDD — Red-Green-Refactor)

- Unit tests mock `anthropic.Anthropic` to avoid real LLM calls
- Integration test uses a synthetic `graph.json` fixture (5 nodes, 2 edges)
- `conftest.py` provides `tmp_graph` and `tmp_config` fixtures
- Coverage gate: `--cov-fail-under=85` in `pyproject.toml`
- **Current result: 42 tests pass, 89.29% coverage**

---

## 7. Verification Commands

```bash
uv run pytest tests/ --cov=src/hw4 --cov-report=term-missing
# Expected: 42 passed, coverage 89%

uv run ruff check src/
# Expected: All checks passed!

uv run python -m hw4.sdk.sdk
# Expected: full pipeline output + token comparison report
```
