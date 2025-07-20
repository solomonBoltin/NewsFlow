# NewsFlow
Python auto scrapper for getting recent news articles from every news website (that doesn't block you).

## Features
- Concurrent web scraping with intelligent parallelism management
- Configurable rate limiting to respect website policies
- Automatic resource cleanup and timeout handling
- Support for multiple news websites simultaneously

## Parallelism Management
NewsFlow includes advanced parallelism features to efficiently scrape multiple websites:
- Semaphore-based concurrency control (no busy waiting)
- Configurable page pool with automatic cleanup
- Intelligent rate limiting with randomization
- Resource leak prevention

See [PARALLELISM.md](PARALLELISM.md) for detailed information about parallelism configuration and management.
