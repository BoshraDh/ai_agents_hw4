# TODO — HW4 Task Tracker

**Version:** 1.00  
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

## Phase 1 — Project Skeleton

- [x] `pyproject.toml` with uv + ruff + coverage config
- [x] `.env-example`
- [x] `.gitignore`
- [x] `config/setup.json`
- [x] `config/rate_limits.json`
- [x] `src/hw4/__init__.py`
- [x] `src/hw4/shared/version.py`
- [x] `src/hw4/shared/constants.py`

---

## Phase 2 — Clone & Graphify

- [ ] Clone scrapy at buggy commit → `data/scrapy/`
- [ ] Run `uv run graphifyy data/scrapy/ --output artifacts/`
- [ ] Verify `artifacts/graph.json` + `artifacts/GRAPH_REPORT.md`

---

## Phase 3 — Core Implementation (TDD)

- [ ] `src/hw4/shared/config.py` (+ tests)
- [ ] `src/hw4/shared/gatekeeper.py` (+ tests)
- [ ] `src/hw4/graphify/runner.py` (+ tests)
- [ ] `src/hw4/graphify/obsidian_builder.py` (+ tests)
- [ ] `src/hw4/analysis/token_counter.py` (+ tests)
- [ ] `src/hw4/analysis/comparator.py` (+ tests)
- [ ] `src/hw4/agent/prompts.py`
- [ ] `src/hw4/agent/tools.py` (+ tests)
- [ ] `src/hw4/agent/nodes.py` (+ tests)
- [ ] `src/hw4/agent/workflow.py`
- [ ] `src/hw4/baseline/naive_agent.py`
- [ ] `src/hw4/sdk/sdk.py`

---

## Phase 4 — Obsidian Vault

- [ ] `obsidian/index.md` — full system overview from graph
- [ ] `obsidian/hot.md` — top-K nodes by PageRank
- [ ] `obsidian/architecture_blocks.md` — block diagram scrapy
- [ ] `obsidian/oop_summary.md` — OOP class summary
- [ ] `obsidian/investigation_log.md` — debugging journal
- [ ] `obsidian/fix_before_after.md` — before/after the patch

---

## Phase 5 — Bug Fix

- [ ] Apply fix to `data/scrapy/scrapy/spidermw/offsite.py`
- [ ] Document fix in `obsidian/fix_before_after.md`
- [ ] Write `reports/bug_analysis.md`

---

## Phase 6 — Token Comparison

- [ ] Run graph-guided agent, record token counts
- [ ] Run naive agent, record token counts
- [ ] Write `reports/token_comparison.md`

---

## Phase 7 — Verification & Push

- [ ] `uv run ruff check src/` → 0 violations
- [ ] `uv run pytest --cov=src/hw4 --cov-fail-under=85`
- [ ] Write `README.md`
- [ ] `git push` to `https://github.com/BoshraDh/ai_agents_hw4.git`
