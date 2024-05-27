import logging
from typing import Dict

from src.data.article_prview import ArticlePreview
from src.news_actor import NewsActor
from src.scrap import get_html, clean_html, get_html_async
from src.scrap.tree_selectors import find_by_multiple_trees, find_by_parents
from src.utils import extract_base_url
from src.website_context import WebsiteContext


class ArticlePreviewScraper:

    def __init__(self, base_url, caching=False):
        self.base_url = base_url
        self.caching = caching
        self.website_context: WebsiteContext = WebsiteContext(base_url, caching)

        self.logger = logging.getLogger('actor')
        self.logger = self.logger.getChild(f"article_previews_scraper({base_url})")

    def full_url(self, url):
        # use url library
        import urllib.parse
        return urllib.parse.urljoin(self.base_url, url)
        # return self.base_url + url if url.startswith("/") else url

    async def scarp_website_async(self, caching=False):
        if not self.website_context.context:
            logging.warning("Website context not found, ignoring task.")
            return

        scraped_article_previews = {}
        for section in self.website_context.top_sections:
            self.logger.info("Scrapping section: " + section)
            article_previews = await self.scrap_section(section)

            for link, article in article_previews.items():
                scraped_article_previews[link] = article
                await NewsActor.process_article_preview(article)

        logging.info(f"Scrapped {len(scraped_article_previews)} articles in total")
        return scraped_article_previews

    async def scrap_section(self, section, caching=False):
        section_html = await get_html_async(section, caching, clean=True)

        try:
            article_previews = self.scrap_article_previews(section_html)
            groups = [article.by_tag_tree for article in article_previews.values()]
            groups = list(dict.fromkeys(groups))
            self.logger.info(f"Found {len(article_previews)} articles from {len(groups)} groups in section {section}")
        except Exception as e:
            self.logger.error(f"Error: {e.__str__()}")
            raise e

        return article_previews

    def scrap_article_previews(self, html):
        article_preview_indexers = self.website_context.article_elements
        indexers_trees = list(article_preview_indexers.keys())
        elements_by_trees = find_by_multiple_trees(html, indexers_trees)

        article_previews = {}
        for element_tree, elements in elements_by_trees.items():
            element_indexes = article_preview_indexers[element_tree]
            for element in elements:
                element_html = element.__str__()

                title_parent_tree = element_indexes["title_parents_tree"]
                link_parent_tree = element_indexes["link_parents_tree"]
                date_parent_tree = element_indexes["date_parents_tree"]

                title_elements = find_by_parents(element_html, title_parent_tree) if title_parent_tree else None
                link_elements = find_by_parents(element_html, link_parent_tree) if link_parent_tree else None
                date_elements = find_by_parents(element_html, date_parent_tree) if date_parent_tree else None

                title_element = title_elements[0] if title_elements else None
                link_element = link_elements[0] if link_elements else None
                date_element = date_elements[0] if date_elements else None

                title_text = title_element.text if title_element else None
                link_text = link_element.get("href") if link_element else None
                link_text = self.full_url(link_text) if link_text else None
                date_text = date_element.text if date_element else None

                if title_text and link_text:
                    website_url = extract_base_url(link_text)
                    article_preview = ArticlePreview(
                        title=title_text,
                        link=link_text,
                        date=date_text,
                        website_url=website_url,
                        by_tag_tree=element_tree
                    )
                    article_previews[link_text] = article_preview

        return article_previews
