import asyncio
import json
import logging
import os
from time import sleep

from src.scrap import get_html_async
from src.utils.__init__ import url_to_filename, storage_path
from src.website_context.find_product_preview_elements import find_product_preview_elements
from src.website_context.find_shop_sections import find_shop_sections

logger = logging.getLogger("actor").getChild("shop_website_context")


class ShopWebsiteContext:

    def __init__(self, base_url, caching=False, ai_caching=True):
        self.base_url = base_url
        self.caching = caching
        self.ai_caching = ai_caching

        self.logger = logging.getLogger('actor')
        self.logger = self.logger.getChild(f"website_context({base_url})")

    async def generate_website_context(self):
        self.logger.info("Generating website context")
        website_context = {"base": self.base_url}

        main_html = await get_html_async(self.base_url, self.caching, clean=True)

        sections = find_shop_sections(self.base_url, main_html)
        website_context["sections"] = sections
        self.logger.info(f"Found {len(sections)} sections: {sections}")

        # top_sections = ask_ai_on_top_15_sections(self.base_url, sections, model_name="gemini", max_retries=3)
        top_sections = sections
        website_context["top_sections"] = top_sections
        self.logger.info(f"Top sections: {top_sections}")

        if not all([section in sections for section in top_sections]):
            self.logger.warning("No top sections found in sections")

        logging.info("Finding product elements")
        website_context["product_elements"] = {}
        for section in top_sections:
            product_elements = await find_product_preview_elements(section, caching=self.caching,
                                                                   ai_caching=self.ai_caching)
            print(product_elements.values())
            for product_element in product_elements.values():
                website_context["product_elements"][product_element["element_tree"]] = product_element
                self.logger.debug(f"Found product element: {product_element}")

        self.save_website_context(website_context)
        self.logger.info(
            f"Website context generated, sections_length: {len(sections)}, top_sections_length: {len(top_sections)},"
            f" product_elements_length: {len(website_context['product_elements'])}")
        return website_context

    def load_website_context(self):
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def save_website_context(self, website_context):
        with open(self.file_path, "w") as f:
            json.dump(website_context, f)

    async def get_or_generate_website_context(self):
        return self.context or await self.generate_website_context()

    @property
    def file_path(self):
        return f"{website_context_path()}/{url_to_filename(self.base_url)}.json"

    @property
    def context(self):
        return self.load_website_context()

    @property
    def top_sections(self):
        return self.context["top_sections"]

    @property
    def sections(self):
        return self.context["sections"]

    @property
    def product_elements(self):
        return self.context["product_elements"]


def website_context_path():
    if not os.path.exists(f"./{storage_path()}/sp_websites_context"):
        os.mkdir(f"./{storage_path()}/sp_websites_context")

    return f"./{storage_path()}/sp_websites_context"


async def main():
    websites = ["https://sananes.co.il/"]
    websites = [ShopWebsiteContext(website) for website in websites]
    while True:
        for websites in websites:
            await websites.get_or_generate_website_context()

            # scarp_website(websites)

        sleep(60 * 60 * 2)


if __name__ == "__main__":
    logger = logging.getLogger("actor")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

    logger.info("Testing shop_website_context")
    asyncio.run(main())
