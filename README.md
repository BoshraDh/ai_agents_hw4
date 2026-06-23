# HW4 — Reverse Engineering, Debugging & Token-Efficient Agentic AI

**Version:** 1.00 | **Course:** AI Agents Orchestration | **Author:** Boshra Dhamshy

---

## What This Does

Uses [Graphify](https://pypi.org/project/graphifyy/) to convert the scrapy codebase into a
knowledge graph, builds an Obsidian vault from the graph, then runs a LangGraph agent that
locates and fixes a real bug (**scrapy-1**) in significantly fewer tokens than reading all source files.

---

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (`pip install uv`)
- An OpenAI API key (`sk-proj-...`)

---

## Setup

```bash
git clone https://github.com/BoshraDh/ai_agents_hw4.git
cd ai_agents_hw4
cp .env-example .env        # add your OPENAI_API_KEY
uv sync                     # install all dependencies

# Clone scrapy at the buggy commit
git clone https://github.com/scrapy/scrapy data/scrapy
cd data/scrapy
git checkout 0f214b6a3a9e26e32e5b64a2a5e22c8dc28fce0e
cd ../..
```

`.env` format:
```
OPENAI_API_KEY=sk-proj-...
```

---

## Run

```bash
# Full pipeline (Graphify → Obsidian → Agent → Comparison)
uv run python -m hw4.sdk.sdk

# Graph-guided agent only
uv run python -m hw4.agent.workflow

# Naive baseline only (for comparison)
uv run python -m hw4.baseline.naive_agent
```

---

## Test

```bash
uv run pytest                         # all tests + coverage
uv run ruff check src/                # lint (must be 0 violations)
```

---

## Project Structure

```
docs/           PRD, PLAN, TODO, per-mechanism PRDs
config/         setup.json, rate_limits.json (no hardcoded values)
src/hw4/
  sdk/          single entry point
  shared/       gatekeeper, config, version, constants
  agent/        LangGraph nodes, workflow, tools, prompts
  baseline/     naive single-shot agent
  graphify/     graphify runner + obsidian builder
  analysis/     token counter + comparator
tests/          unit/ + integration/ (≥85% coverage)
obsidian/       Obsidian vault (6 pages)
reports/        bug_analysis.md, token_comparison.md
artifacts/      graph.json, GRAPH_REPORT.md
data/scrapy/    scrapy at buggy commit (git-ignored)
```

---

## Key Results

Live run results (model: `gpt-4o-mini`):

| Method | Total tokens | Files read | Bug found |
|--------|-------------|-----------|---------|
| Graph-guided | ~4,500 | 1 | ✓ |
| Naive | ~16,400 | all .py files | ✓ |
| **Reduction** | **~3.6×** | | |

---

## Bug Fixed

**scrapy-1** — `OffsiteMiddleware.get_host_regex` crashes with `TypeError` when
`spider.allowed_domains` contains `None`.

**Fix:** Added a `None`-guard before building the regex (1 line).

See `obsidian/fix_before_after.md` for before/after.
See `reports/bug_analysis.md` for full root cause analysis.
