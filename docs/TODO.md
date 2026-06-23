# TODO — HW4 Task Tracker

**Version:** 1.02  
**Last Updated:** 2026-06-24

---

## Phase 0 — Documentation (DONE ✅)

- [x] `docs/PRD.md`
- [x] `docs/PLAN.md`
- [x] `docs/TODO.md`
- [x] `docs/PRD_langgraph_agent.md`
- [x] `docs/PRD_graphify_runner.md`
- [x] `docs/PRD_token_comparison.md`

---

## Phase 1 — Project Skeleton (DONE ✅)

- [x] `pyproject.toml` — uv + ruff + coverage + deps (langgraph, openai, networkx, scipy, graphifyy)
- [x] `uv.lock` — locked dependency versions
- [x] `.env-example` — with OPENAI_API_KEY placeholder
- [x] `.gitignore`
- [x] `config/setup.json` — model: gpt-4o-mini
- [x] `config/rate_limits.json`
- [x] `src/hw4/shared/version.py` — VERSION = "1.00"
- [x] `src/hw4/shared/constants.py` — BUG_TARGET_FILE updated to downloadermiddlewares/offsite.py

---

## Phase 2 — Clone & Graphify (DONE ✅)

- [x] Clone scrapy → `data/scrapy/` (git-ignored)
- [x] Run `uv run graphify update data/scrapy/` — produced 7,480 nodes, 22,889 edges
- [x] Copy `artifacts/graph.json` + `artifacts/GRAPH_REPORT.md`
- [x] Build Obsidian vault (index.md + hot.md auto-generated from real graph)

---

## Phase 3 — Core Implementation (DONE ✅)

All files implemented with TDD. Final coverage: **89.38%** (target: >=85%).
Switched from Anthropic SDK to OpenAI SDK (key: sk-proj-...).

- [x] `src/hw4/shared/config.py` + tests
- [x] `src/hw4/shared/gatekeeper.py` (OpenAI SDK) + tests
- [x] `src/hw4/graphify/runner.py` + tests
- [x] `src/hw4/graphify/obsidian_builder.py` + tests
- [x] `src/hw4/analysis/token_counter.py` + tests
- [x] `src/hw4/analysis/comparator.py` + tests
- [x] `src/hw4/agent/prompts.py`
- [x] `src/hw4/agent/tools.py` + tests
- [x] `src/hw4/agent/nodes.py` + tests
- [x] `src/hw4/agent/workflow.py` + integration tests
- [x] `src/hw4/baseline/naive_agent.py` + tests
- [x] `src/hw4/sdk/sdk.py` + tests

---

## Phase 4 — Obsidian Vault (DONE ✅)

- [x] `obsidian/index.md` — auto-generated from real graph (top-20 nodes by degree)
- [x] `obsidian/hot.md` — PageRank top-10 nodes from real graph
- [x] `obsidian/architecture_blocks.md` — scrapy block diagram
- [x] `obsidian/oop_summary.md` — OOP class table
- [x] `obsidian/investigation_log.md` — real token counts from live run
- [x] `obsidian/fix_before_after.md` — before/after patch

---

## Phase 5 — Bug Fix (DONE ✅)

- [x] `obsidian/fix_before_after.md` — full patch documented
- [x] `reports/bug_analysis.md` — root cause analysis
- [x] Bug confirmed: `scrapy/downloadermiddlewares/offsite.py` — `get_host_regex` None-check
      (Current code already has the fix: `if domain is None: continue`)

---

## Phase 6 — Token Comparison (DONE ✅)

Live run completed 2026-06-24:

- [x] Graph-guided agent run: **4,081 tokens**, found correct bug
- [x] Naive agent run: **16,376 tokens**, found wrong file (mislead by full codebase)
- [x] `reports/token_comparison.md` updated with live numbers

---

## Phase 7 — Verification (DONE ✅)

- [x] `uv run ruff check src/` → 0 violations
- [x] `uv run pytest --cov=src/hw4 --cov-fail-under=85` → 89.38% (42 tests)
- [x] `README.md` — full user manual
- [x] `git push` to `https://github.com/BoshraDh/ai_agents_hw4.git`

---

## All Done

Full pipeline successfully executed. All deliverables complete.
