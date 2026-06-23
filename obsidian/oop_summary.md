# scrapy - OOP Summary

| Class | Inherits | Role |
|-------|---------|------|
| `Spider` | `BaseSpider` | Define parse logic |
| `Request` | `object` | HTTP request wrapper |
| `Response` / `TextResponse` | `Response` | HTTP response |
| `Item` | `scrapy.Item` | Structured output |
| `MiddlewareMixin` | ABC | Download/spider middleware |
| `Extension` | ABC | Signal-based extensions |
| `Settings` | `ChainMap` | Layered configuration |
