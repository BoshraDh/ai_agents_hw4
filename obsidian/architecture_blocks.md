# scrapy - Block Diagram

```
CLI (cmdline)
    -> CrawlerRunner
            -> Engine
                    +-> Scheduler      (request queue)
                    +-> Downloader     (HTTP fetch)
                    |      -> Spider (parse + yield)
                    -> Pipeline       (item processing)
```

Each block is a separate component connected via signals and middleware chains.
