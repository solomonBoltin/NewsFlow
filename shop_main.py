# gets website url and scraps all products from the website
from src.ShopActor import ShopActor
from src.data.setup import setup_database
from src.scrap.product_preview_scrapper import ProductPreviewScraper
from src.website_context.shop_website_context import ShopWebsiteContext


async def main() -> None:
    # initialize program
    setup_database()

    async with ShopActor:
        ShopActor.log.info("Starting actor")

        website = "https://sananes.co.il/"
        website_context = ShopWebsiteContext(website)
        await website_context.get_or_generate_website_context()

        # scarp_website
        scrapper = ProductPreviewScraper(website)
        await scrapper.scrape_website_async()


if __name__ == "__main__":
    import logging

    logger = logging.getLogger("actor")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

    logger.info("Testing shop_website_context")
    import asyncio

    asyncio.run(main())
