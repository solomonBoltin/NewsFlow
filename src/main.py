"""
This module defines the `main()` coroutine for the Apify Actor, executed from the `__main__.py` file.

Feel free to modify this file to suit your specific needs.

To build Apify Actors, utilize the Apify SDK toolkit, read more at the official documentation:
https://docs.apify.com/sdk/python
"""
import asyncio
from asyncio import sleep

from src.data.article_prview import ArticlePreview
from src.data.setup import setup_database
# Apify SDK - toolkit for building Apify Actors, read more at https://docs.apify.com/sdk/python
from src.news_actor import NewsActor
from src.scrap.article_preview_scraper import ArticlePreviewScraper
from src.website_context import WebsiteContext


async def main() -> None:
    """
    The main coroutine is being executed using `asyncio.run()`, so do not attempt to make a normal function
    out of it, it will not work. Asynchronous execution is required for communication with Apify platform,
    and it also enhances performance in the field of web scraping significantly.
    """
    # initialize program
    setup_database()

    async with NewsActor:
        # Structure of input is defined in input_schema.json
        actor_input = await NewsActor.get_input() or {}
        # websites = actor_input.get('websites')
        NewsActor.log.info("Starting actor")
        websites = [
            "https://undecidedmf.com/",
            "https://apnews.com",
            # "https://etn.news/",
            "https://www.haaretz.com/",
            "https://medicalxpress.com/",
            "https://pharmatimes.com/",
            "https://edition.cnn.com/",
            # "https://www.business-standard.com/",
            # "https://www.itnonline.com/",
            "https://www.nytimes.com/",
            # "https://www.smh.com.au/",
            # "https://www.globes.co.il/en/",
            # "https://www.calcalist.co.il/",
            # "https://www.theverge.com/",
            # "https://www.timesofisrael.com/",
            # "https://www.reuters.com/", robot detection
            # "https://www.bloomberg.com/", robot detection
        ]

        while True:
            tasks = []
            for website in websites:
                website_context = WebsiteContext(website)
                await website_context.get_or_generate_website_context()

                # try:
                #     await website_context.get_or_generate_website_context()
                # except Exception as e:
                #     NewsActor.log.error(f"Error: {e}")
                #     websites.remove(website)

            delay = 0
            for website in websites:
                article_preview_scraper = ArticlePreviewScraper(website)

                task = article_preview_scraper.scarp_website_async(delay=delay)
                delay += 15
                tasks.append(task)

            await asyncio.gather(*tasks)
            NewsActor.log.info("Sleeping")
            await sleep(60 * 5)

        # Save headings to Dataset - a table-like storage
        # await Actor.push_data(headings)
