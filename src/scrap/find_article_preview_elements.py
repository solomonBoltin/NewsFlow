from typing import Dict

from src.data.article_prview import ArticlePreview
from src.scrap.tree_selectors import find_by_trees, find_by_parents, find_by_multiple_trees
from src.utils import extract_base_url


def extract_article_previews(html, article_preview_indexers: Dict[str, Dict[str, str]]):
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
