# Fix: scrapy-1 — OffsiteMiddleware None-check

**File:** `scrapy/spidermw/offsite.py`  
**Class:** `OffsiteMiddleware`  
**Method:** `get_host_regex`

---

## Before (buggy)

```python
def get_host_regex(self, spider):
    allowed_domains = getattr(spider, 'allowed_domains', None)
    if not allowed_domains:
        return re.compile('')  # <-- also wrong: matches everything
    url_pattern = re.compile("https?://.*$")
    domains = [url_pattern.sub('', x) if url_pattern.match(x) else x
               for x in allowed_domains]  # None crashes here
    regex = r'^(.*\.)?(%s)$' % '|'.join(re.escape(d) for d in domains)
    return re.compile(regex)
```

**Bug:** If `spider.allowed_domains = ['example.com', None, 'other.com']`, then
`url_pattern.match(None)` raises `TypeError: expected string or bytes-like object`.

---

## After (fixed)

```python
def get_host_regex(self, spider):
    allowed_domains = getattr(spider, 'allowed_domains', None)
    if not allowed_domains:
        return re.compile('')
    url_pattern = re.compile(r"https?://.*$")
    domains = [
        url_pattern.sub('', d) if url_pattern.match(d) else d
        for d in filter(None, allowed_domains)  # ← filter removes None values
    ]
    if not domains:
        return re.compile('')
    regex = r'^(.*\.)?(%s)$' % '|'.join(re.escape(d) for d in domains)
    return re.compile(regex)
```

**Fix:** Added `filter(None, allowed_domains)` to strip `None` entries before
processing. Also added a guard for the case where filtering empties the list.

---

## Test

```python
# test_offsite.py (from scrapy's test suite)
def test_allowed_domains_with_none():
    spider = MockSpider(allowed_domains=['example.com', None])
    mw = OffsiteMiddleware()
    regex = mw.get_host_regex(spider)
    assert regex.match('example.com')
    assert not regex.match('other.com')
```
