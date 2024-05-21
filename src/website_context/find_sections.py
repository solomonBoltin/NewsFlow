import datetime
import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import numpy as np

from src.scrap.__init__ import get_html, clean_html
from src.ask_llm.llm_tasks.categories_urls import categories_urls_using_ai

logger = logging.getLogger("actor").getChild("find_sections")


def extract_section_urls(base_url, html_text):
    soup = BeautifulSoup(html_text, 'html.parser')

    all_links = soup.find_all('a', href=True)
    link_groups = {}

    # group links by parents-tag-tree
    for link in all_links:
        parent = link.parent
        tag_tree = link.name
        for i in range(20):
            parent = parent.parent
            if not parent:
                break
            else:
                tag_tree = parent.name + tag_tree

        link_text = link['href']
        if not link_text.startswith("http"):
            link_text = urljoin(base_url, link_text)
        if not link_text.startswith(base_url):
            continue

        if tag_tree in link_groups:
            link_groups[tag_tree].append(link_text)
        else:
            link_groups[tag_tree] = [link_text]

    # remove duplicates from groups
    link_groups = {key: list(dict.fromkeys(value)) for key, value in link_groups.items()}

    # sort by group size
    sorted_groups = sorted(link_groups.items(), key=lambda x: len(x[1]), reverse=True)
    checked_links = {link['href']: None for link in all_links}

    # Score groups so we can reduce amount of links to check. groups that score > 0.7 will be tagged as articles_page,
    # groups that score < 0.2 will be tagged as not articles_page
    for key, links_group in sorted_groups:
        random_links = np.random.choice(links_group, min(10, len(links_group)), replace=False)
        random_links = list(random_links)

        # Categorize them using AI
        output = categories_urls_using_ai(base_url, random_links, "gemini", caching=True)
        logger.debug(f"Group: {key}, len: {len(links_group)}, random_links: {random_links}")

        group_score = [output[key]["category"] == "articles_page" for key in output.keys()]
        group_score = sum(group_score) / len(group_score)
        logger.debug(f"Ai outputs: {output}, group_score: {group_score}")

        if group_score <= 0.2:
            for link in links_group:
                checked_links[link] = False

        if group_score > 0.7:
            for link in links_group:
                checked_links[link] = True

        for link, results in output.items():
            checked_links[link] = results["category"] == "articles_page"

    # categories all unchecked links
    unchecked_links = [link for link in checked_links.keys() if checked_links[link] is None]

    # loop over batches of x links and categorize them
    bs = 5
    for i in range(0, len(unchecked_links), bs):
        batch = unchecked_links[i:i + bs]
        output = categories_urls_using_ai(base_url, batch, "gemini", caching=True)
        for link, results in output.items():
            checked_links[link] = results["category"] == "articles_page"

    urls = [url for url in checked_links.keys() if checked_links[url]]
    return urls


def preprocess_urls(base_url, urls):
    results = []
    for url in urls:

        if not url.startswith("http"):
            if url.startswith("/"):
                results.append(base_url.rstrip("/") + url)
            else:
                results.append(base_url + url)
        else:
            results.append(url)

    results = list(dict.fromkeys(results))
    return results


def find_sections(base_url, html_text):
    s_time = datetime.datetime.now()

    urls = extract_section_urls(base_url, html_text)
    urls = preprocess_urls(base_url, urls)

    e_time = datetime.datetime.now()
    return urls


def test_extract_sections():
    base_url = "https://www.theverge.com/"
    html_text = get_html(base_url, cache=True)
    html_text = clean_html(html_text)

    section_urls = find_sections(base_url, html_text)
    for url in section_urls:
        logger.info("Section URL: ", url)

    logger.info(len(section_urls))

# test_extract_sections()
