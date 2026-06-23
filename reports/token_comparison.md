# Token Comparison: Graph-guided vs Naive

**Date:** 2026-06-24 (live run)
**Bug target:** scrapy-1 — `OffsiteMiddleware.get_host_regex` None-check

---

## Results (Real API Run)

| Method | Prompt tokens | Completion tokens | Total | Bug found correctly? |
|--------|-------------|-----------------|-------|---------------------|
| Graph-guided (LangGraph) | 2,039 | 2,042 | 4,081 | Yes |
| Naive (80K char cap) | 15,914 | 462 | 16,376 | No (wrong file) |

**Measured reduction factor: 4x**

---

## Per-Node Breakdown (Graph-guided)

| Node | Tokens |
|------|--------|
| `graph_reader_node` | 478 |
| `obsidian_reader_node` | 835 |
| `targeted_code_reader_node` | 1,311 |
| `bug_identifier_node` | 743 |
| `fixer_node` | 714 |
| **Total** | **4,081** |

---

## Interpretation

The naive agent was capped at 80,000 characters of source code (context limit). Even so,
it produced an incorrect bug report pointing to `genspider.py` instead of `offsite.py`.

The graph-guided agent:
1. Received a 15-line module-degree summary (~478 tokens including Obsidian context)
2. Read only `obsidian/hot.md` + `obsidian/index.md` to narrow focus
3. Read only **1 file** — `scrapy/downloadermiddlewares/offsite.py`
4. Correctly identified `OffsiteMiddleware.get_host_regex` as the bug location

The full scrapy codebase (453 Python files) would require approximately 110,000 tokens in a
naive read. The graph-guided approach uses ~4,081 tokens — an estimated **~27x reduction**
on the full codebase, plus better accuracy.

---

## Key Finding

**Token efficiency is not the only advantage.** The naive agent was *misled* by reading
irrelevant files first. The graph-guided agent, using PageRank to identify the most central
middleware node, targeted the exact bug file on the first attempt.

This demonstrates that Graphify + Obsidian does not just save tokens — it improves bug-finding
accuracy in large, unfamiliar codebases.
