# PRD — Token Comparison Mechanism

**Version:** 1.00  
**Date:** 2026-06-24

---

## 1. Purpose

Measure and compare token consumption between the graph-guided LangGraph agent and the
naive baseline agent, and produce a human-readable comparison report.

---

## 2. Measurement Approach

Both agents use `ApiGatekeeper` which logs `(prompt_tokens, completion_tokens)` per call.
The `TokenCounter` accumulates these and `Comparator` produces the report.

```python
from hw4.analysis.token_counter import TokenCounter
from hw4.analysis.comparator import Comparator

counter_graph = TokenCounter()
counter_naive = TokenCounter()

# agents record to their counter via gatekeeper
run_agent(token_counter=counter_graph)
run_naive(token_counter=counter_naive)

Comparator(counter_graph, counter_naive).write_report("reports/token_comparison.md")
```

---

## 3. Report Schema

`reports/token_comparison.md` must include:

| Column | Description |
|--------|-------------|
| Method | "Graph-guided" / "Naive" |
| Prompt tokens | Total tokens in all prompts |
| Completion tokens | Total tokens in all completions |
| Total tokens | Sum |
| Files read | How many source files were sent to LLM |
| Reduction factor | Naive / Graph-guided ratio |

---

## 4. Expected Results (reference)

| Method | Prompt tokens | Completion tokens | Total |
|--------|-------------|-----------------|-------|
| Naive | ~110,000 | ~2,000 | ~112,000 |
| Graph-guided | ~1,500 | ~800 | ~2,300 |
| **Reduction** | | | **~49×** |

Actual numbers will be recorded from live runs.

---

## 5. Success Criteria

- Report file exists and contains both rows
- Reduction factor ≥ 5× (to satisfy assignment requirement)
- Numbers are from real instrumented runs (not fabricated)
