import json
import re
import pyperclip

from src.website_context.find_article_preview_elements import find_article_preview_elements
from src.website_context.find_sections import find_sections
from src.scrap.tree_selectors import get_articles_tree_and_verify, find_by_trees
from src.scrap.__init__ import get_html, clean_html, save_html


def extract_urls(sections_text):
    print(sections_text)
    urls = re.findall(r"https?://[^\s]+", sections_text)
    urls = [url.split("#")[0] for url in urls]  # Remove anchors .replace(".tag", "")
    return urls


def url_to_filename(url):
    return url.split("//")[1].split("/")[0].replace(".", "_")


def save_website_context(website_context):
    with open(f"./storage/websites_context/{url_to_filename(website_context['base'])}.json", "w") as f:
        json.dump(website_context, f)
    print("Website context saved to JSON")


def load_website_context(url):
    try:
        with open(f"./storage/websites_context/{url_to_filename(url)}.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def get_website_context(test_existing_context=None, caching=True):
    website_context = {}

    website_url = None
    sections_text = None
    articles_css = None

    if test_existing_context:
        website_context = test_existing_context
        website_url = website_context.get("base")
        sections_text = website_context.get("sections_text")
        articles_css = website_context.get("articles_css")

    if not website_url:
        website_url = input("Please enter the website URL\n")

        potential_website_context = load_website_context(website_url)
        ans = input("previous context found, use it? (y/n)")
        if ans == "y":
            sections_text = potential_website_context.get("sections_text")
            articles_css = potential_website_context.get("articles_css")
            website_context = potential_website_context

    website_context["base"] = website_url
    save_website_context(website_context)

    print("Extracting source page from URL using Selenium and copying HTML to clipboard")
    html_content = get_html(website_url, caching)  # Caching incorporated here
    html_content = clean_html(html_content)
    pyperclip.copy(html_content)

    if not sections_text:
        print("Extracting sections using ai, might take a while")
        sections = find_sections(website_url, html_content)
        sections_text = str(sections)

    website_context["sections_text"] = sections_text
    save_website_context(website_context)
    print(f"Sections received: {sections_text}")

    print("Extracting all links from sections output and saving them to website JSON")
    sections_urls = extract_urls(sections_text)
    sections_urls = list(dict.fromkeys(sections_urls))
    website_context["sections"] = sections_urls
    save_website_context(website_context)

    if not sections_urls:
        print("No sections found, exiting")
        exit()

    print("Requesting first URL that isn't base, copying HTML text to clipboard")
    print(sections_urls)
    first_url = next(url for url in sections_urls if url != website_url)
    first_section_html_content = get_html(first_url, caching)  # Caching incorporated here
    first_section_html_content = clean_html(first_section_html_content)
    save_html(first_section_html_content, f"{url_to_filename(first_url)}.html")
    pyperclip.copy(first_section_html_content)

    if not articles_css:
        articles_css = input("Articles CSS selector\n")

    website_context["articles_css"] = articles_css
    save_website_context(website_context)

    print("Extracting tag tree and verifying")
    tag_trees, articles_len, is_verified = get_articles_tree_and_verify(first_section_html_content, articles_css)
    website_context["articles_tree"] = tag_trees
    website_context["is_verified"] = is_verified
    save_website_context(website_context)
    print(f"Articles length: {articles_len}, is verified: {is_verified}, tag trees: {tag_trees}")

    print("Checking if tree works in other section")
    sections_articles_len = {}
    for url in sections_urls:
        if url not in [website_url]:
            html_content = get_html(url, caching)  # Caching incorporated here
            html_content = clean_html(html_content)
            articles = find_by_trees(html_content, tag_trees, articles_css)
            [print(str(article), article.text, f"{url}----\n") for article in articles]
            sections_articles_len[url] = len(articles)
    website_context["sections_articles_len"] = sections_articles_len
    save_website_context(website_context)

    print(f"Done: {website_context}")
    return website_context


def add_website(base_url, caching=True):
    website_context = {"base": base_url}
    main_html = get_html(base_url, caching)
    sections = find_sections(base_url, main_html)

    print("Sections: ", sections)
    input()
    website_context["sections"] = {}
    website_context["article_elements"] = {}
    for section in sections:
        # section_html = get_html(section, caching)
        article_groups = find_article_preview_elements(section, caching=caching)
        website_context["sections"][section] = article_groups
        for article_key, article in article_groups.items():
            website_context["article_elements"][article_key] = article

    print("Total sections length: ", len(website_context["sections"]))
    print("Total extracted article elements length: ", len(website_context["article_elements"]))
    input("Finished, press enter to save")
    print(website_context.keys())
    with open(f"./storage/websites_context/{url_to_filename(base_url)}.json", "w") as f:
        json.dump(website_context, f)
    save_website_context(website_context)
    print(website_context)
    return website_context


def scrap_articles(page_url):
    website_context = load_website_context(page_url)
    if not website_context:
        print("No website context found, exiting")
        exit()

    page_html = get_html(page_url)
    page_html = clean_html(page_html)

    article_elements_context = website_context.get("article_elements")
    tree_results = find_by_trees(page_html, article_elements_context.keys())

    for tree_result in tree_results:
        pass



add_website("https://www.espn.com/")

input("Finished, press enter to exit")
# Example usage with predefined input

caching = True
test_context = load_website_context("https://www.timesofisrael.com/")

wc = get_website_context(caching=caching)

# Example usage with predefined input
print(json.dumps(wc, indent=4))
