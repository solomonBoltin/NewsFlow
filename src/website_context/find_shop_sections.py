import logging

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
import html

logger = logging.getLogger("actor").getChild("find_shop_sections")


def process_url(base_url, url):
    if not url.startswith("http"):
        if url.startswith("/"):
            return base_url.rstrip("/") + url
        else:
            return base_url + url
    else:
        return url


def format_url(url):
    # Decode URL
    decoded_url = unquote(url)
    # Remove the base part of the URL if it's present
    base_url = "https://sananes.co.il"
    # if decoded_url.startswith(base_url):
    #     decoded_url = decoded_url[len(base_url):]
    return decoded_url


def find_shop_sections(base_url, html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    nav_elements = soup.find_all('nav')

    all_sections = {}
    for nav in nav_elements:
        links = nav.find_all('a', href=True)

        for link in links:
            full_link = process_url(base_url, link['href'])
            text = link.get_text(strip=True)
            logger.debug(f"Found section: {text} - {format_url(full_link)}")
            all_sections[full_link] = text

    return list(all_sections.keys())


def test_find_shop_sections():
    url = "https://sananes.co.il/"
    html_text = requests.get(url).text
    sections = find_shop_sections(url, html_text)
    for section in sections:
        logger.info(section)


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    test_find_shop_sections()
