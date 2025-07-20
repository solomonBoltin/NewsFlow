# Parallelism Management in NewsFlow

This document describes the parallelism improvements implemented to fix issues with concurrent web scraping.

## Overview

NewsFlow is a Python news scraper that fetches articles from multiple websites concurrently. The previous implementation had several parallelism issues that have been addressed.

## Issues Fixed

### 1. Busy Waiting Problem
**Before**: The `Scrapper.get_available_page()` method used recursive calls with `await asyncio.sleep(1)`, leading to:
- Inefficient CPU usage
- Potential stack overflow with many concurrent requests
- Poor responsiveness

**After**: Implemented `asyncio.BoundedSemaphore` for proper concurrency control:
- Efficient blocking until resources are available
- No recursive calls or busy waiting
- Better resource utilization

### 2. Resource Leak Prevention
**Before**: Pages could get stuck in "busy" state without timeout or cleanup.

**After**: Added automatic cleanup mechanisms:
- Page timeout tracking with `_page_timestamps`
- Automatic cleanup of stuck pages after configurable timeout (default: 60 seconds)
- Proper resource release in `finally` blocks

### 3. Rate Limiting Improvements
**Before**: Fixed incremental delays (15 seconds between each request).

**After**: Configurable rate limiting with:
- Environment variable configuration
- Randomization to prevent thundering herd effects
- Optional rate limiting disable for testing

## Configuration

Configure parallelism behavior through environment variables:

```bash
# Maximum number of concurrent browser pages
MAX_PAGES=5

# Base delay between requests (seconds)
BASE_DELAY=15.0

# Enable/disable rate limiting
RATE_LIMIT_ENABLED=true

# Timeout for stuck pages (seconds)
PAGE_TIMEOUT=60
```

## Usage Example

```python
from src.scrap import get_html_async

# The scrapper automatically manages parallelism
html = await get_html_async("https://example.com")
```

## Architecture

```
main.py
├── Creates tasks for each website
├── Applies configurable delays
└── Uses asyncio.gather() for concurrent execution

article_preview_scraper.py
├── Coordinates scraping for each website
└── Calls get_html_async for each section

get_html_async (scrap/__init__.py)
├── Creates Scrapper instance
└── Calls scrapper.get_html()

Scrapper (scrap/scrapper.py)
├── Manages browser page pool
├── Uses semaphore for concurrency control
├── Handles timeouts and cleanup
└── Implements proper resource management
```

## Performance Benefits

1. **Better Resource Management**: Semaphore prevents resource exhaustion
2. **Improved Responsiveness**: No more busy waiting or recursive calls
3. **Configurable Limits**: Tune parallelism based on your needs
4. **Automatic Cleanup**: Prevents memory leaks from stuck pages
5. **Rate Limiting**: Respects website policies and prevents being blocked

## Monitoring

The scrapper logs important events:
- Page acquisition and release
- Stuck page cleanup
- Configuration warnings
- Error handling

Monitor logs for patterns like:
```
Cleaning up stuck page after 60s timeout
Request 1: Got semaphore after 0.10s
```

## Testing

Run the included tests to verify parallelism improvements:

```bash
# Basic functionality and concurrency tests
python test_parallelism.py

# Integration tests (requires playwright browsers)
python test_integration.py
```