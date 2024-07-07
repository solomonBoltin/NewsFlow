import asyncio
import datetime
import logging

from bs4 import BeautifulSoup
from playwright.async_api import Page

from src.data.product_preview import ProductPreview
from src.ShopActor import ShopActor
from src.scrap import get_html_async
from src.scrap.tree_selectors import find_by_multiple_trees, find_by_parents, extract_tag_tree
from src.utils import extract_base_url
from src.website_context.shop_website_context import ShopWebsiteContext


class ProductPreviewScraper:

    def __init__(self, base_url, caching=False):
        self.base_url = base_url
        self.caching = caching
        self.website_context: ShopWebsiteContext = ShopWebsiteContext(base_url, caching=caching)

        self.logger = logging.getLogger('actor')
        self.logger = self.logger.getChild(f"product_previews_scraper({base_url})")

    def full_url(self, url):
        import urllib.parse
        return urllib.parse.urljoin(self.base_url, url)

    async def scrape_website_async(self, caching=False, delay=0):
        await asyncio.sleep(delay)
        if not self.website_context.context:
            logging.warning("Website context not found, ignoring task.")
            return

        scraped_product_previews = {}
        for section in self.website_context.top_sections:
            self.logger.info("Scraping section: " + section)
            product_previews = await self.scrape_section(section)

            for link, product in product_previews.items():
                scraped_product_previews[link] = product
                await ShopActor.process_product_preview(product)

        logging.info(f"Scraped {len(scraped_product_previews)} products in total")
        return scraped_product_previews

    async def scrape_section(self, section, caching=False) -> ProductPreview:

        section_html = await get_html_async(section, caching, custom_load=scroll_while_growing)  # , clean=True)

        try:
            product_previews = self.scrape_product_previews(section_html)
            groups = [product.by_tag_tree for product in product_previews.values()]
            groups = list(dict.fromkeys(groups))
            self.logger.info(f"Found {len(product_previews)} products from {len(groups)} groups in category {section}")
        except Exception as e:
            self.logger.error(f"Error: {e.__str__()}")
            raise e

        return product_previews

    def scrape_product_previews(self, html):
        product_preview_indexers = self.website_context.product_elements
        indexers_trees = list(product_preview_indexers.keys())
        elements_by_trees = find_by_multiple_trees(html, indexers_trees)

        product_previews = {}
        for element_tree, elements in elements_by_trees.items():
            element_indexes = product_preview_indexers[element_tree]
            for element in elements:
                element_html = element.__str__()

                title_parent_tree = element_indexes["title_parents_tree"]
                link_parent_tree = element_indexes["link_parents_tree"]
                price_parent_tree = element_indexes["price_parents_tree"]
                image_parent_tree = element_indexes["image_parents_tree"]

                title_elements = find_by_parents(element_html, title_parent_tree) if title_parent_tree else None
                link_elements = find_by_parents(element_html, link_parent_tree) if link_parent_tree else None
                price_elements = find_by_parents(element_html, price_parent_tree) if price_parent_tree else None
                image_elements = find_by_parents(element_html, image_parent_tree) if image_parent_tree else None

                title_element = title_elements[0] if title_elements else None
                link_element = link_elements[0] if link_elements else None
                price_element = price_elements[0] if price_elements else None
                image_element = image_elements[0] if image_elements else None

                title_text = title_element.text if title_element else None
                link_text = link_element.get("href") if link_element else None
                link_text = self.full_url(link_text) if link_text else None
                price_text = price_element.text.strip() if price_element else None
                image_src = image_element.get("src") if image_element else None
                image_src = self.full_url(image_src) if image_src else None

                if title_text and link_text:
                    product_preview = ProductPreview(
                        title=title_text,
                        link=link_text,
                        price=price_text,
                        image=image_src,
                        website_url=self.base_url,
                        by_tag_tree=element_tree,
                        scrape_datetime=datetime.datetime.now().isoformat(),
                        html_text=element_html
                    )
                    product_previews[link_text] = product_preview

        return product_previews


async def scroll_while_growing(page: Page):
    page_elements_len = await page.evaluate("document.querySelectorAll('div').length")
    page_elements_len_change = 1
    while page_elements_len_change > 0:
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight - 100)")

        # wait for loading
        for i in range(5):
            await asyncio.sleep(0.5)
            new_page_elements_len = await page.evaluate("document.querySelectorAll('div').length")
            page_elements_len_change = new_page_elements_len - page_elements_len
            page_elements_len = new_page_elements_len

            if page_elements_len_change > 0:
                break


async def test_product_preview_scraper():
    # Create a new product preview scraper
    product_preview_scraper = ProductPreviewScraper('https://sananes.co.il/', caching=False)
    # Scrape the website
    await product_preview_scraper.website_context.get_or_generate_website_context()

    product_previews = await product_preview_scraper.scrape_section(
        "https://sananes.co.il/collections/%D7%A4%D7%A8%D7%A7%D7%98-%D7%A4%D7%A8%D7%A7%D7%98-spc")
    print("Product Previews Count: " + str(len(product_previews)))
    product_previews = list(product_previews.values())
    for product in product_previews:
        print(product.image)
    [print(i, product.title) for i, product in enumerate(product_previews)]
    # print(product_previews)
    input(">>>")


if __name__ == '__main__':
    asyncio.run(test_product_preview_scraper())
