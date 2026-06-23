# scrapy — OOP Summary

| Class | Base Class | Module | Role |
|-------|-----------|--------|------|
| `Spider` | `BaseSpider` | `scrapy.spiders` | User-defined crawl logic |
| `Request` | `object` | `scrapy.http` | Immutable HTTP request |
| `Response` | `object` | `scrapy.http` | HTTP response base |
| `TextResponse` | `Response` | `scrapy.http` | Text/HTML response with encoding |
| `Item` | `scrapy.Item` | `scrapy.item` | Structured output container |
| `OffsiteMiddleware` | `object` | `scrapy.spidermw.offsite` | Domain filter middleware |
| `DownloaderMiddleware` | ABC mixin | `scrapy.downloadermiddlewares` | Process requests/responses |
| `SpiderMiddleware` | ABC mixin | `scrapy.spidermiddlewares` | Process spider I/O |
| `Extension` | ABC | `scrapy.extension` | Signal-based plugin |
| `Settings` | `ChainMap` | `scrapy.settings` | Layered config system |
| `CrawlerRunner` | `object` | `scrapy.crawler` | Manage multiple crawlers |
| `Engine` | `object` | `scrapy.core.engine` | Central orchestrator |
| `Scheduler` | `object` | `scrapy.core.scheduler` | Request priority queue |
| `Downloader` | `object` | `scrapy.core.downloader` | HTTP client wrapper |

## Key OOP Patterns

- **Template Method**: `Spider.parse()` is the hook users override
- **Chain of Responsibility**: Middleware chains process requests/responses in order
- **Observer / Signal**: `Extension` objects subscribe to engine signals (item_scraped, spider_opened, etc.)
- **Strategy**: `Scheduler` can use different queue implementations
