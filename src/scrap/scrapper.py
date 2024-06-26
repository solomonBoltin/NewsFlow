import asyncio
import logging
import os
from typing import Dict

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page, TimeoutError
from playwright_stealth import stealth_async

from src.utils import url_to_file_name, storage_path

logger = logging.getLogger('actor').getChild("scrapper")


# """
# This class is responsible for limiting the number of pages that can be created at the same time.
# And reusing them when they are available.
# it exposes a method to get a html from a url, and a method to close the browser and playwright.
# """
class Scrapper:
    _max_pages = 5
    _pl = None
    _browser = None
    _pages_dict: Dict[Page, bool] = {}
    _lock = None
    _instance = None

    def __new__(cls, max_pages=None):
        if max_pages is not None:
            cls._max_pages = max_pages

        if cls._instance is None:
            cls._instance = super(Scrapper, cls).__new__(cls)
            cls._lock = asyncio.Lock()
        return cls._instance

    async def _initialize_playwright(self):
        logger.info("Initializing Scrapper...")
        self._pl = await async_playwright().start()
        self._browser = await self._pl.chromium.launch(headless=False)

    @property
    def available_pages(self):
        return [page for page, busy in self._pages_dict.items() if not busy]

    async def get_available_page(self):
        async with self._lock:
            if not self._pl:
                await self._initialize_playwright()
            if self.available_pages:
                page = self.available_pages[0]
                self._pages_dict[page] = True
                return page

            if len(self._pages_dict) < self._max_pages:
                page = await self._browser.new_page()

                # Page settings
                await stealth_async(page)

                self._pages_dict[page] = True
                return page

        await asyncio.sleep(1)
        return await self.get_available_page()

    async def release_page(self, page):
        self._pages_dict[page] = False

    async def close(self):
        await self._browser.close()
        await self._pl.stop()

    async def get_html(self, url, clean=True, screenshots=True):

        page = await self.get_available_page()

        try:

            # goto page
            try:
                await page.goto(url, wait_until="networkidle", timeout=20000)
            except TimeoutError:
                logger.warning(f"Page loading not completed after {20000}ms for {url}, continuing...")

            # scroll down
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

            # wait for the page to load fully
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=30000)
            except TimeoutError as e:
                logger.warning(f"Page loading not completed after {30000}ms for {url}, continuing...")

            # take screenshot
            if screenshots:
                try:
                    screenshot_path = f"{screenshots_path(url)}/{url_to_file_name(url)}.png"
                    await page.screenshot(path=screenshot_path, full_page=True)
                except Exception as e:
                    logger.warning(f"Failed to take screenshot for {url}: {e}")

            # get html content
            html_content = await page.content()

            # release page
            await self.release_page(page)

            save_html(html_content, f"{url_to_file_name(url)}.html")
            if clean:
                html_content = clean_html(html_content)
            return html_content

        except Exception as e:
            logger.error(f"Failed while getting html from {url}: {e}")
            await self.release_page(page)
            return ""


def clean_html(html_content, remove_attributes=False):
    """
  Removes scripts, styles, and form elements from HTML content.

  Args:
    html_content (str): The HTML content as a string.

  Returns:
    str: The cleaned HTML content.
    :param html_content:
    :param remove_attributes:
  """
    soup = BeautifulSoup(html_content, "html.parser")

    tags_to_remove = ["style", "class", "input", "picture", "source", "noscript", "img", "iframe", "svg", "path",
                      "link", "meta", "script"]

    # Remove script tags
    for script in soup(tags_to_remove):
        script.decompose()

    if remove_attributes:
        for tag in soup.find_all():
            for attribute in tags_to_remove:
                del tag[attribute]

    # Remove loose text within the <body>
    body = soup.body
    if body is not None:
        for child in body.contents[:]:
            if not child.name:  # Check if it's a NavigableString
                child.extract()  # Remove the element

    # removeNewLines

    articles = []
    # for article_element in soup.find_all("article"):
    #
    #     print(article_element)
    #     title_element = article_element.find("h2").find("a")
    #     title = title_element.text.strip()
    #     link = title_element["href"]
    #
    #     date_element = article_element.find("p").find("span")
    #     date = date_element.text.strip() if date_element else None
    #
    #     summary_element = article_element.find("div", class_="post-content")
    #     summary = summary_element.text.strip() if summary_element else None
    #
    #     articles.append({
    #         "title": title,
    #         "link": link,
    #         "date": date,
    #         "summary": summary,
    #     })

    # print("Articles length: ", len(articles))
    return soup.contents.__str__()


def htmls_path():
    if not os.path.exists(f"./{storage_path()}/htmls"):
        os.mkdir(f"./{storage_path()}/htmls")
    return f"./{storage_path()}/htmls"


def save_html(html, filename):
    with open(f"{htmls_path()}/{filename}", "w", encoding="utf-8") as file:
        file.write(html)


def screenshots_path(url):
    #  extract base url
    base_url = url.split("//")[-1].split("/")[0]
    base_url = url_to_file_name(base_url)

    if not os.path.exists(f"./{storage_path()}/screenshots"):
        os.mkdir(f"./{storage_path()}/screenshots")
    if not os.path.exists(f"./{storage_path()}/screenshots/{base_url}"):
        os.mkdir(f"./{storage_path()}/screenshots/{base_url}")
    return f"./{storage_path()}/screenshots/{base_url}"


# Usage example
async def fetch_html(url):
    ps = Scrapper(max_pages=2)
    html = await ps.get_html(url)
    print(f"Fetched HTML from {url} with length {len(html)}")


async def main():
    ps = Scrapper(max_pages=2)
    urls = ['https://google.com', 'https://bing.com', 'https://yahoo.com', 'https://duckduckgo.com',
            'https://yandex.ru', 'https://baidu.com']
    tasks = [fetch_html(url) for url in urls]
    await asyncio.gather(*tasks)
    await ps.close()


if __name__ == "__main__":
    asyncio.run(main())
