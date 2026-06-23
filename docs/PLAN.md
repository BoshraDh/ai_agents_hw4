# PLAN — Architecture & Implementation

**Version:** 1.02  
**Date:** 2026-06-24  
**Status:** COMPLETE. Live run verified: 42 tests pass, 89% coverage, 0 ruff violations, pipeline produces real token comparison.

---

## 1. System Architecture (C4 — Context Level)

```
User / CLI
    |
    v
SDK Layer  (hw4.sdk.sdk - sole entry point)
    |
    +-- GraphifyRunner  ->  ObsidianBuilder
    |       (graphify update, networkx, scipy PageRank)
    |
    +-- LangGraph Agent (5 nodes)
    |       |
    |       v
    |   API Gatekeeper  ->  OpenAI API (gpt-4o-mini)
    |
    +-- Naive Baseline (single-shot, all files)
            |
            v
        API Gatekeeper  ->  OpenAI API (gpt-4o-mini)
```

---

## 2. Component Breakdown

### 2.1 Graphify Runner (`src/hw4/graphify/runner.py`)
- Wraps `graphify update` CLI (AST extraction, no LLM)
- Produced: 7,480 nodes, 22,889 edges on scrapy codebase
- Exposes: `run()`, `load_graph()`, `get_neighbors()`, `top_by_degree()`, `pagerank()`
- Auto-detects `"links"` vs `"edges"` key for NetworkX compatibility

### 2.2 Obsidian Builder (`src/hw4/graphify/obsidian_builder.py`)
- Reads graph via `GraphifyRunner`; runs NetworkX + scipy PageRank
- Writes: `obsidian/index.md` (top-20 by degree)
- Writes: `obsidian/hot.md` (top-K by PageRank — task 5.6 extension)
- Static pages: `architecture_blocks.md`, `oop_summary.md`

### 2.3 LangGraph Agent (`src/hw4/agent/`)
Five-node pipeline (all LLM calls via `ApiGatekeeper`):

```
graph_reader_node          (478 tokens — graph degree summary)
    -> obsidian_reader_node    (835 tokens — hot.md + index.md)
        -> targeted_code_reader_node  (1,311 tokens — offsite.py only)
            -> bug_identifier_node    (743 tokens — structured bug report)
                -> fixer_node         (714 tokens — minimal patch)

Total: 4,081 tokens. Bug found correctly.
```

### 2.4 Naive Baseline (`src/hw4/baseline/naive_agent.py`)
- Collects all `.py` files from `data/scrapy/` (capped at 80K chars)
- Single LLM call asking for bug location
- Result: 16,376 tokens, **wrong file** identified (genspider.py)

### 2.5 API Gatekeeper (`src/hw4/shared/gatekeeper.py`)
- Uses OpenAI SDK (`openai.OpenAI`)
- Singleton; throttles to RPM limit; exponential backoff on errors
- Accumulates `total_prompt_tokens` + `total_completion_tokens`
- Config from `config/rate_limits.json`

### 2.6 Config Manager (`src/hw4/shared/config.py`)
- Singleton; loads `config/setup.json` + `config/rate_limits.json`
- Model: `gpt-4o-mini` (set in setup.json)

---

## 3. Data Flow (actual)

```
data/scrapy/ (453 .py files)
    -> graphify update (AST, no LLM)
        -> data/scrapy/graphify-out/graph.json (7,480 nodes)
            -> copied to artifacts/graph.json
                -> ObsidianBuilder
                    -> obsidian/index.md (top-20 degree)
                    -> obsidian/hot.md (PageRank top-10)
                        -> LangGraph agent (5 nodes, 4,081 tokens)
                            -> OffsiteMiddleware bug found + patch
                                -> reports/token_comparison.md
```

---

## 4. Decisions (ADRs)

### ADR-001: LangGraph over CrewAI
Per-node control enables per-step token measurement. Assignment recommendation.

### ADR-002: scrapy (BugsInPy)
Rich middleware architecture; 40 documented bugs; bug #1 is clear and well-scoped.

### ADR-003: uv as sole package manager
Required by guidelines. `uv.lock` for reproducibility.

### ADR-004: scipy for PageRank
NetworkX 3.6.1 delegates `nx.pagerank()` to scipy. Added as explicit dependency.

### ADR-005: NetworkX edges key auto-detection
Graphify outputs `"links"` key; NetworkX 3.x defaults to `"edges"`. Runner auto-detects.

### ADR-006: OpenAI SDK (not Anthropic)
User provided OpenAI API key (`sk-proj-...`). Gatekeeper switched from `anthropic` to `openai`.
Model: `gpt-4o-mini` (cost-efficient, sufficient for bug analysis).

### ADR-007: graphify update (AST-only, no LLM)
`graphify update` does AST extraction without LLM — free to run. Produces same graph.json
format. Semantic enrichment can be added later with `graphify extract`.

---

## 5. File Size (all <= 150 lines)

All source files verified within 150-line limit.

---

## 6. Actual Test Results

```
uv run pytest tests/ --cov=src/hw4
Result: 42 passed, coverage 89.38%

uv run ruff check src/
Result: All checks passed!
```

---

## 7. Live Pipeline Results

```
Graph-guided agent:  4,081 tokens — correct bug identified
Naive agent:        16,376 tokens — wrong file identified
Reduction factor:   4x measured (27x estimated on full uncapped codebase)

Key insight: token efficiency + accuracy both improved with graph-guided approach.
```
