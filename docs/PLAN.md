# PLAN — Architecture & Implementation

**Version:** 1.00  
**Date:** 2026-06-24

---

## 1. System Architecture (C4 — Context Level)

```
┌─────────────────────────────────────────────────────────┐
│                      User / CLI                         │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                     SDK Layer                           │
│            hw4.sdk.sdk  (entry point)                   │
└──────┬──────────┬───────────────┬───────────────────────┘
       │          │               │
       ▼          ▼               ▼
  Graphify    LangGraph        Baseline
  Runner      Agent            Naive Agent
       │          │               │
       └──────────┴───────────────┘
                  │
                  ▼
         API Gatekeeper
         (all LLM calls)
                  │
                  ▼
          Anthropic API / OpenAI
```

---

## 2. Component Breakdown (C4 — Container Level)

### 2.1 Graphify Runner (`src/hw4/graphify/runner.py`)
- Calls `graphifyy` CLI on `data/scrapy/`
- Parses `artifacts/graph.json`
- Exposes: `run_graphify()`, `load_graph()`, `get_node_neighbors()`

### 2.2 Obsidian Builder (`src/hw4/graphify/obsidian_builder.py`)
- Reads `graph.json` + runs NetworkX PageRank
- Writes `obsidian/index.md` (full system overview)
- Writes `obsidian/hot.md` (top-K suspicious nodes)
- Writes supporting pages

### 2.3 LangGraph Agent (`src/hw4/agent/`)
Five-node state machine:
```
graph_reader_node
    → obsidian_reader_node
        → targeted_code_reader_node
            → bug_identifier_node
                → fixer_node
```
- Each node calls the SDK (never LLM directly)
- Token usage tracked per node via `token_counter.py`

### 2.4 Naive Baseline (`src/hw4/baseline/naive_agent.py`)
- Single-pass: reads all `.py` files under `data/scrapy/scrapy/`
- Sends full code to LLM asking for bug location
- Token usage tracked for comparison

### 2.5 API Gatekeeper (`src/hw4/shared/gatekeeper.py`)
- Singleton managing all LLM calls
- Rate limits loaded from `config/rate_limits.json`
- Provides: `chat_complete(messages, model, max_tokens)`
- Implements exponential backoff + request queue

### 2.6 Config Manager (`src/hw4/shared/config.py`)
- Loads `config/setup.json` + `config/rate_limits.json`
- Provides typed access to all config values
- No hardcoded values anywhere else

---

## 3. Data Flow

```
data/scrapy/ (buggy commit)
    → graphifyy CLI
        → artifacts/graph.json
            → obsidian_builder
                → obsidian/*.md
                    → LangGraph agent
                        → ApiGatekeeper
                            → LLM
                                → bug location + fix
```

---

## 4. ADR-001: LangGraph over CrewAI

**Decision:** Use LangGraph for the agent framework.  
**Reason:** LangGraph gives explicit control over which nodes fire and in what order,
making token counting per-step straightforward. CrewAI abstracts the orchestration,
making it harder to prove token savings at each stage. The assignment recommends
LangGraph for accounts with limited free API quotas.

---

## 5. ADR-002: scrapy over thefuck

**Decision:** Use scrapy (Bug #1) as the target project.  
**Reason:** scrapy has a rich multi-component architecture (Engine/Spider/Middleware/
Pipeline/Scheduler) which produces a meaningful knowledge graph with clear node
separation. thefuck is simpler and would produce a less interesting graph.

---

## 6. ADR-003: uv as sole package manager

**Decision:** Use `uv` exclusively.  
**Reason:** Required by `software_submission_guidelines-V3`. Faster resolution,
`uv.lock` for reproducibility, no mixing with pip/venv.

---

## 7. File Budget (≤ 150 lines each)

| File | Estimated lines |
|------|----------------|
| sdk/sdk.py | ~80 |
| shared/gatekeeper.py | ~120 |
| shared/config.py | ~60 |
| agent/nodes.py | ~140 |
| agent/workflow.py | ~50 |
| agent/tools.py | ~100 |
| agent/prompts.py | ~80 |
| graphify/runner.py | ~100 |
| graphify/obsidian_builder.py | ~140 |
| baseline/naive_agent.py | ~80 |
| analysis/token_counter.py | ~70 |
| analysis/comparator.py | ~80 |

---

## 8. Testing Strategy (TDD)

- Write failing tests first, then implement
- Unit tests: mock `ApiGatekeeper` to avoid real LLM calls
- Integration test: use a tiny synthetic graph.json fixture
- Coverage gate: `--cov-fail-under=85`
