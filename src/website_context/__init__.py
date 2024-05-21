import json
import logging
from time import sleep

from src.ask_llm.llm_tasks.top_15_sections import ask_ai_on_top_15_sections
from src.scrap.__init__ import get_html, clean_html
from src.utils.__init__ import url_to_filename
from src.website_context.find_article_preview_elements import find_article_preview_elements
from src.website_context.find_sections import find_sections


class WebsiteContext:

    def __init__(self, base_url, caching=False, ai_caching=True):
        self.base_url = base_url
        self.caching = caching
        self.ai_caching = ai_caching

        self.logger = logging.getLogger('actor')
        self.logger = self.logger.getChild(f"website_context({base_url})")

    def generate_website_context(self):
        self.logger.info("Generating website context")
        website_context = {"base": self.base_url}

        main_html = get_html(self.base_url, self.caching, clean=True)

        sections = find_sections(self.base_url, main_html)
        website_context["sections"] = sections
        self.logger.info(f"Found {len(sections)} sections: {sections}")

        top_sections = ask_ai_on_top_15_sections(self.base_url, sections, model_name="gemini", max_retries=3)
        website_context["top_sections"] = top_sections
        self.logger.info(f"Top sections: {top_sections}")

        if not all([section in sections for section in top_sections]):
            self.logger.warning("No top sections found in sections")

        logging.info("Finding article elements")
        website_context["article_elements"] = {}
        for section in top_sections:
            article_elements = find_article_preview_elements(section, caching=self.caching, ai_caching=self.ai_caching)
            for article_element in article_elements.values():
                website_context["article_elements"][article_element["element_tree"]] = article_element
                self.logger.debug(f"Found article element: {article_element}")

        self.save_website_context(website_context)
        self.logger.info(
            f"Website context generated, sections_length: {len(sections)}, top_sections_length: {len(top_sections)},"
            f" article_elements_length: {len(website_context['article_elements'])}")
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

    def get_or_generate_website_context(self):
        return self.context or self.generate_website_context()

    @property
    def file_path(self):
        return f"./storage/websites_context/{url_to_filename(self.base_url)}.json"

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
    def article_elements(self):
        return self.context["article_elements"]




def main():
    website_context = WebsiteContext("https://www.calcalist.co.il/")
    websites = ["https://www.calcalist.co.il/"]
    websites = [WebsiteContext(website) for website in websites]
    while True:
        for websites in websites:
            websites.get_or_generate_website_context()

            # scarp_website(websites)

        sleep(60 * 60 * 2)
