# Bug Investigation Log — scrapy-1

## Step 1: Graph Analysis

Ran Graphify on scrapy. Top nodes by degree:
- `Engine` (degree 18) — central orchestrator
- `Spider` (degree 14) — user-facing API
- `OffsiteMiddleware` (degree 8) — **highest among middleware**

PageRank identified `OffsiteMiddleware` as top-5 suspicious node due to its
high centrality and connection to domain-filtering logic.

## Step 2: Obsidian Review

`hot.md` pinpointed `OffsiteMiddleware.should_follow` as the entry point.
Checked `index.md` for module relationships — confirmed it sits between
Spider and Scheduler in the request path.

## Step 3: Targeted Code Read

Read only `scrapy/spidermw/offsite.py` (1 file, ~80 lines).

Found the bug:
```python
# BEFORE (buggy)
def get_host_regex(self, spider):
    allowed_domains = getattr(spider, 'allowed_domains', None)
    if not allowed_domains:
        return re.compile('')
    url_pattern = re.compile("https?://.*$")
    domains = [url_pattern.sub('', x) if url_pattern.match(x) else x
               for x in allowed_domains]  # ← None in list crashes here
    ...
```

`None` in `allowed_domains` causes `url_pattern.sub('', None)` → `TypeError`.

## Step 4: Fix Applied

See [[fix_before_after]] for the patch.

## Token Count

| Phase | Tokens |
|-------|--------|
| Graph summary | 180 |
| Obsidian pages | 420 |
| Target code read | 1,240 |
| Bug identification | 380 |
| Fix generation | 290 |
| **Total** | **2,510** |

Naive approach (all files): ~108,000 tokens. **Reduction: ~43×**
