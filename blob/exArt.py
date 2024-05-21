import requests
from bs4 import BeautifulSoup


def extract_articles(url, html, article_container_tag, title_tag, link_tag, date_tag=None, date_attribute=None):
    """
    Extracts articles from a news website with the given parameters.

    Args:
        base_url: The base URL of the website.
        article_container_tag: HTML tag or class that identifies article containers.
        title_tag: HTML tag or class used for article titles.
        link_tag: HTML tag or class used for article links.
        date_tag (optional): HTML tag containing the date information.
        date_attribute (optional): Attribute within date_tag containing the date (e.g., 'datetime').

    Returns:
        A list of dictionaries, where each dictionary represents an article with
        'title', 'link', and 'date' keys.
    """


    soup = BeautifulSoup(html, "html.parser")
    articles = []
    for article_element in soup.find_all(article_container_tag):
        title_element = article_element.find(title_tag).find("a")
        title = title_element.text.strip()
        link = url + title_element["href"]

        date = None
        if date_tag:
            date_element = article_element.find(date_tag)
            if date_attribute:
                date = date_element.get(date_attribute)
            else:
                date = date_element.text.strip()

        articles.append({"title": title, "link": link, "date": date})

    return articles


# PharmaTimes Configuration
config_pharmatimes = {
    # "base_url": "https://pharmatimes.com/news/",
    "article_container_tag": "article",
    "title_tag": "h2",
    "link_tag": "a",
    "date_tag": "p",
    "date_attribute": None  # Extract date directly from text content
}

# New York Times - Asia Pacific Configuration
config_nyt_asia = {
    # "base_url": "https://www.nytimes.com/section/world/asia",
    "article_container_tag": "li",  # Assuming articles are in list items
    "title_tag": "a",
    "link_tag": "a",
    "date_tag": "span",
    "date_attribute": "data-testid"  # Assuming date is in 'data-testid' attribute
}

# Business Standard Economy Configuration
config_bs_economy = {
    "base_url": "https://www.business-standard.com/economy",
    "article_container_tag": "div",  # Assuming articles are in divs with specific class
    "title_tag": "h2",
    "link_tag": "a",
    "date_tag": "div",  # Assuming date is within a div with specific class
    "date_attribute": None  # Extract date directly from text content
}