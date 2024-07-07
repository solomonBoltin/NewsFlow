import logging

from src.ask_llm.llm_tasks.article_preview_element_processor import process_article_preview_element
from src.scrap.tree_selectors import *
from src.utils.__init__ import extract_base_url

logger = logging.getLogger("actor").getChild("find_article_preview_elements")


def extract_urls(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    all_links = soup.find_all('a', href=True)

    urls = []
    for link in all_links:
        href = link['href']
        urls.append(href)

    return urls


def looks_like_article(element):
    # check if element looks like an article (has between 2-60 children, at least one url and some text)
    count = len(element.find_all())

    if 2 <= count <= 60:
        urls = extract_urls(element.__str__())
        if urls and len(element.text) > 10:
            return True

    return False


def looks_like_articles(elements_group: list):
    # check if group of elements looks like articles (has at least 3 elements)
    if len(elements_group) >= 3:
        return True
    return False


def extract_groups(html_content):
    # extract groups of elements that look like articles
    soup = BeautifulSoup(html_content, "html.parser")

    filtered_elements = [element for element in soup.find_all() if looks_like_article(element)]

    # group by tag tree
    grouped_elements = {}
    for element in filtered_elements:
        tag_tree = extract_tag_tree(element.__str__())
        if tag_tree in grouped_elements:
            grouped_elements[tag_tree].append(element)
        else:
            grouped_elements[tag_tree] = [element]

    # filter groups
    grouped_elements = {key: value for key, value in grouped_elements.items() if looks_like_articles(value)}

    # removing trees that are in other trees
    new_grouped_elements = grouped_elements.copy()
    for tree, group in grouped_elements.items():
        for other_tree, other_group in grouped_elements.items():
            # if tree is in other tree and has fewer elements
            if tree != other_tree and tree in other_tree and len(group) <= len(other_group):
                del new_grouped_elements[tree]
                break

    sorted_results = sorted(new_grouped_elements.items(), key=lambda x: len(x[1]), reverse=True)

    return sorted_results


async def find_article_preview_elements(section_url, caching=True, ai_caching=True):
    # returns jsons representing articles with selectors to element, title, link, date
    logger.info(f"Getting article preview elements from {section_url}")

    base_url = extract_base_url(section_url)

    html_content = await get_html_async(section_url, cache=caching, clean=True)

    grouped_elements = extract_groups(html_content)
    logger.info(f"Found {len(grouped_elements)} groups of elements that are potential article previews.")

    articles_elements = {}
    for tree, group in grouped_elements:
        first_element = group[0]
        first_element_html = first_element.__str__()
        element_analysis = process_article_preview_element(base_url, first_element_html, ai_caching)

        if element_analysis["is_article"]:
            articles_elements[tree] = element_analysis

    logger.info(f"Found {len(articles_elements)} article preview elements.")
    return articles_elements


def test_extract_articles_css():
    section_url = "https://www.breakingnews.ie/world/"
    find_article_preview_elements(section_url)

# test_extract_articles_css()
