# scrapy — Block Diagram

```
CLI (cmdline)
    └─► CrawlerRunner
            └─► Engine
                    ├─► Scheduler      (priority queue for Requests)
                    ├─► Downloader     (HTTP fetch + middleware chain)
                    │       └─► Spider (parse HTML, yield Items + Requests)
                    ├─► Pipeline       (process yielded Items)
                    └─► Extension      (event/signal subscribers)
```

## Middleware Chains

```
Request path:  Spider → SpiderMiddleware → Scheduler → DownloaderMiddleware → Downloader
Response path: Downloader → DownloaderMiddleware → Spider → SpiderMiddleware → Pipeline
```

## OffsiteMiddleware location

`OffsiteMiddleware` is a **SpiderMiddleware** — it intercepts Requests after the Spider
yields them and before they reach the Scheduler. It filters out domains not in
`spider.allowed_domains`.

**Bug**: when `allowed_domains` contains `None`, the domain-regex construction crashes.
