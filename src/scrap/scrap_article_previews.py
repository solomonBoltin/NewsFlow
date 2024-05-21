import logging

from src.news_actor import NewsActor
from src.scrap import get_html, clean_html
from src.scrap.find_article_preview_elements import extract_article_previews
from src.website_context import WebsiteContext


class ArticlePreviewScraper:

    def __init__(self, base_url, caching=False):
        self.base_url = base_url
        self.caching = caching
        self.website_context: WebsiteContext = WebsiteContext(base_url, caching)

        self.logger = logging.getLogger('actor')
        self.logger = self.logger.getChild(f"article_previews_scraper({base_url})")

    def scrap_section(self, section, caching=False):
        section_html = get_html(section, caching, clean=True)

        try:
            article_previews = extract_article_previews(section_html, self.website_context.article_elements)
            groups = [article.by_tag_tree for article in article_previews.values()]
            groups = list(dict.fromkeys(groups))
            self.logger.info(f"Found {len(article_previews)} articles from {len(groups)} groups in section {section}")
        except Exception as e:
            self.logger.error(f"Error: {e.__str__()}")
            raise e

        return article_previews

    async def scarp_website_async(self, caching=False):
        if not self.website_context.context:
            logging.warning("Website context not found, ignoring task.")
            return

        scraped_article_previews = {}
        for section in self.website_context.top_sections:
            self.logger.info("Scrapping section: " + section)
            article_previews = self.scrap_section(section)

            for link, article in article_previews.items():
                scraped_article_previews[link] = article
                await NewsActor.process_article_preview(article)

        logging.info(f"Scrapped {len(scraped_article_previews)} articles in total")
        return scraped_article_previews
