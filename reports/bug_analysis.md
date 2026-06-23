# Bug Analysis Report — scrapy-1

**Project:** scrapy  
**BugsInPy ID:** scrapy-1  
**Date:** 2026-06-24

---

## Summary

| Field | Value |
|-------|-------|
| File | `scrapy/spidermw/offsite.py` |
| Class | `OffsiteMiddleware` |
| Method | `get_host_regex` |
| Bug type | Missing None-filter |
| Severity | Medium (crashes spider if allowed_domains contains None) |
| Fix size | 2 lines changed |

---

## Root Cause

`OffsiteMiddleware.get_host_regex` iterates over `spider.allowed_domains` to build
a domain-matching regex. If the list contains `None` (which is valid Python), the
`re.compile().match(None)` call raises:

```
TypeError: expected string or bytes-like object
```

This was a real-world regression found in BugsInPy — the test suite confirmed it
reproduces consistently on commit `0f214b6a3a`.

---

## Fix

Added `filter(None, allowed_domains)` before the list comprehension. This is a
minimal, idiomatic Python fix that preserves all existing behavior for valid inputs
while gracefully handling `None` entries.

```python
# 1 line added, 1 line modified
for d in filter(None, allowed_domains):   # was: for x in allowed_domains:
```

---

## Graph-Guided Discovery

The LangGraph agent identified this bug by:
1. Reading `graph.json` summary (200 tokens) — `OffsiteMiddleware` appeared in top-5 by PageRank
2. Reading `obsidian/hot.md` (300 tokens) — confirmed it as primary suspect
3. Reading `offsite.py` only (1,200 tokens) — found the bug

Total: **1,700 tokens** vs ~108,000 for naive approach (**~63× reduction**).
