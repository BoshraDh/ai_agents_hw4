# PRD — LangGraph Agent Mechanism

**Version:** 1.00  
**Date:** 2026-06-24

---

## 1. Purpose

A five-node LangGraph state machine that locates and patches a real bug in scrapy using
graph-guided context loading rather than reading the entire codebase.

---

## 2. State Schema

```python
class AgentState(TypedDict):
    graph: dict            # parsed graph.json
    obsidian_context: str  # content of hot.md + index.md
    target_code: str       # specific files read (≤ 3 files)
    bug_report: str        # identified bug description
    patch: str             # proposed fix (diff format)
    token_log: list[dict]  # per-node token counts
```

---

## 3. Nodes

| Node | Input | Output | Max tokens consumed |
|------|-------|--------|-------------------|
| `graph_reader_node` | raw `graph.json` path | `state.graph` summary | ~200 |
| `obsidian_reader_node` | `obsidian/hot.md`, `index.md` | `state.obsidian_context` | ~500 |
| `targeted_code_reader_node` | top-3 suspicious files from hot.md | `state.target_code` | ~1,500 |
| `bug_identifier_node` | graph + obsidian + target_code | `state.bug_report` | ~800 |
| `fixer_node` | bug_report + target_code | `state.patch` | ~600 |

---

## 4. Interfaces

```python
# Entry via SDK only
from hw4.sdk.sdk import run_agent
result = run_agent()   # returns AgentState

# Internal: all LLM calls via gatekeeper
from hw4.shared.gatekeeper import get_gatekeeper
gk = get_gatekeeper()
response = gk.chat_complete(messages=[...], model="...", max_tokens=800)
```

---

## 5. Constraints

- Each node may read ≤ 3 files from `data/scrapy/`
- No node calls LLM directly — must go through `ApiGatekeeper`
- Total pipeline must use ≤ 4,000 tokens (vs naive ~120,000)

---

## 6. Success Criteria

- Bug correctly identified as `OffsiteMiddleware.should_follow` None-check
- Patch produces valid Python (no syntax errors)
- Token total < 5,000
