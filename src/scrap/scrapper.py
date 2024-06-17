# import asyncio
# import aiohttp
# from playwright.async_api import async_playwright
# from bs4 import BeautifulSoup
# from threading import Lock
#
# import threading
# from queue import Queue
# from playwright.sync_api import sync_playwright
#
#
# class Scrapper:
#     _instance = None
#     _lock = threading.Lock()
#
#     def __new__(cls, max_pages=5):
#         with cls._lock:
#             if cls._instance is None:
#                 cls._instance = super(Scrapper, cls).__new__(cls)
#                 cls._instance._initialize_playwright(max_pages)
#             return cls._instance
#
#     def _initialize_playwright(self, max_pages):
#         self.playwright = sync_playwright().start()
#         self.browser = self.playwright.chromium.launch()
#         self.page_pool = Queue(max_pages)
#         self.max_pages = max_pages
#         self.created_pages = 0
#         self.pool_lock = threading.Lock()
#
#     def get_page(self):
#         with self.pool_lock:
#             if not self.page_pool.empty():
#                 page = self.page_pool.get()
#             elif self.created_pages < self.max_pages:
#                 page = self.browser.new_page()
#                 self.created_pages += 1
#             else:
#                 page = self.page_pool.get()
#         return page
#
#     def release_page(self, page):
#         self.page_pool.put(page)
#
#     def get_html(self, url):
#         page = self.get_page()
#         try:
#             page.goto(url)
#             html = page.content()
#         finally:
#             self.release_page(page)
#         return html
#
#     def __del__(self):
#         while not self.page_pool.empty():
#             page = self.page_pool.get_nowait()
#             page.close()
#         self.browser.close()
#         self.playwright.stop()
#
#
# # Usage example
# if __name__ == "__main__":
#     import threading
#
#
#     def fetch_html(url):
#         singleton = Scrapper(max_pages=2)
#         html = singleton.get_html(url)
#         print(f"Fetched HTML from {url} with length {len(html)}")
#
#
#     urls = ['https://example.com', 'https://example.org', 'https://example.net']
#
#     threads = [threading.Thread(target=fetch_html, args=(url,)) for url in urls]
#
#     for thread in threads:
#         thread.start()
#
#     for thread in threads:
#         thread.join()
#
#
# async def main():
#     urls = ["https://google.com", "https://bing.com", "https://yahoo.com", "https://duckduckgo.com"]
#     tasks = []
#     scraper = Scrapper(max_pages=2)
#     for url in urls:
#         # scraper = Scraper(max_pages=2)
#         task = scraper.get_html(url)
#         tasks.append(task)
#
#     html_contents = await asyncio.gather(*tasks)
#
#     # Process the extracted HTML content here
#
#     await scraper.close()
#
#
# asyncio.run(main())


import asyncio
from typing import List

from playwright.async_api import async_playwright, Page
from threading import Lock


class PlaywrightSingleton:
    _max_pages = 5
    _browser = None
    _pages: List[(Page, bool)] = []

    @property
    def available_pages(self):
        return [page for page, busy in self._pages if not busy]

    async def get_page(self):
        if self.available_pages:
            page, _ = self.available_pages[0]
            return page

        if len(self._pages) < self._max_pages:
            page = self._browser.new_page()
            self._pages.append((page, False))
            return page

        await asyncio.sleep(1)
        return await self.get_page()








class PlaywrightSingleton:
    _instance = None
    _lock = Lock()

    def __new__(cls, max_pages=5):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(PlaywrightSingleton, cls).__new__(cls)
                cls._instance._initialize_playwright(max_pages)
            return cls._instance

    def _initialize_playwright(self, max_pages):
        self.max_pages = max_pages
        self.page_pool = asyncio.Queue(max_pages)
        self.created_pages = 0
        self.playwright = None
        self.browser = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch()

    async def get_page(self):
        if not self.page_pool.empty():
            return await self.page_pool.get()
        elif self.created_pages < self.max_pages:
            self.created_pages += 1
            return await self.browser.new_page()
        else:
            return await self.page_pool.get()

    async def release_page(self, page):
        await self.page_pool.put(page)

    async def get_html(self, url):
        page = await self.get_page()
        try:
            await page.goto(url)
            html = await page.content()
        finally:
            await self.release_page(page)
        return html

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.browser.close()
        await self.playwright.stop()


# Usage example
async def fetch_html(url):
    async with PlaywrightSingleton(max_pages=2) as singleton:
        html = await singleton.get_html(url)
        print(f"Fetched HTML from {url} with length {len(html)}")


async def main():
    urls = ['https://example.com', 'https://example.org', 'https://example.net']
    tasks = [fetch_html(url) for url in urls]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
