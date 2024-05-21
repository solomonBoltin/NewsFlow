# form for adding website context
# input request website url
# -> extracting source page from url using selenium and copying html to clipboard
# input request "sections output"
# ->  extracting all links from "sections output" and saving them to website json
# -> requesting first url that isn't base, copying html text to clipboard
# requesting articles css selector
# -> extract tag tree and verify (if not reports to fails and exists) (using function, extract_tag_trees(html_text, articles_css) -> tag_trees, is_verified)
# -> save website context (base, sections, articles_css, articles_tree, is_verified) to json
import json
import re

import pyperclip

from src.scrap.tree_selectors import get_articles_tree_and_verify, find_by_trees
from src.scrap.__init__ import get_html, clean_html, save_html
from src.utils.__init__ import url_to_filename


def extract_urls(sections_text):
    print(sections_text)
    urls = re.findall(r"https?://[^\s]+", sections_text)
    return urls




caching = True

website_json = {}

print("Adding news website form")
website_url = input("Please enter the website URL\n")
website_json["base"] = website_url

print("Extracting source page from URL using Selenium and copying HTML to clipboard")
html_content = get_html(website_url, caching)
html_content = clean_html(html_content)
pyperclip.copy(html_content)

print("HTML content copied to clipboard, get sections output and paste it here")
input("Copy sections and pass enter\n")
sections_text = pyperclip.paste()
print("fSections received: {sections}")

print("Extracting all links from sections output and saving them to website JSON")
sections_urls = extract_urls(sections_text)
sections_urls = list(dict.fromkeys(sections_urls))

website_json["sections"] = sections_urls

if not sections_urls:
    print("No sections found, exiting")
    exit()

print("Requesting first URL that isn't base, copying HTML text to clipboard")
print(sections_urls)
first_url = next(url for url in sections_urls if url != website_url)
first_section_html_content = get_html(first_url, caching)
first_section_html_content = clean_html(first_section_html_content)
save_html(first_section_html_content, f"{url_to_filename(first_url)}.html")
pyperclip.copy(first_section_html_content)

print("HTML content copied to clipboard, requesting articles CSS selector")
articles_css = input("Articles CSS selector\n")
website_json["articles_css"] = articles_css



print("Extracting tag tree and verifying")
tag_trees, articles_len, is_verified = get_articles_tree_and_verify(first_section_html_content, articles_css)
website_json["articles_tree"] = tag_trees
website_json["is_verified"] = is_verified

print("Checking if tree works in other section")
sections_articles_len = {}
for url in sections_urls:
    if url not in [website_url]:
        html_content = get_html(url, caching)
        html_content = clean_html(html_content)
        articles = find_by_trees(html_content, tag_trees, articles_css)
        sections_articles_len[url] = len(articles)

website_json["sections_articles_len"] = sections_articles_len

print("Saving website context to JSON")
with open(f"{url_to_filename(website_url)}.json", "w") as f:
    json.dump(website_json, f)

print("Website context saved to JSON")
