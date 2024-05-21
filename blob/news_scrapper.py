from typing import List


class NewsScrapper:
    pass


class ArticleElement:
    def __init__(self):

        self.tree_tag = ""
        self.selector = ""
        self.title_selector = ""
        self.link_selector = ""
        self.date_selector = ""

        self.title_parents_tree = []
        self.link_parents_tree = []
        self.date_parents_tree = []

        self.title_element = None
        self.link_element = None
        self.date_element = None

class Article:
    def __init__(self):
        self.title = ""
        self.link = ""
        self.date = ""

class WebsiteContext:
    def __init__(self, base_url: str):
        self.context_json = {}
        self.base_url = base_url
        self.sections = []
        self.article_elements: List[ArticleElement] = []
        self.articles: List[Article] = []
        self.is_ok = True


class WebsiteScrapper:
    def __init__(self, base_url: str):
        self.website_context = WebsiteContext(base_url)
        self.is_ok = True

    def scrap_section(self, section: List[str]) -> List[Article]:
        pass

    def loop(self):
        while True:
            next_section = self.website_context.sections.pop(0)
            articles = self.scrap_section(next_section)



# news scrapper loop
# for website in websites:
# if website_scarpper.is_ok:
#    website_scarpper.scrap_next()



# section_context: url, articles_len,

