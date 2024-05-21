import logging

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger('actor').getChild("scrap_tools")


def clean_html(html_content, remove_attributes=False):
    """
  Removes scripts, styles, and form elements from HTML content.

  Args:
    html_content (str): The HTML content as a string.

  Returns:
    str: The cleaned HTML content.
    :param html_content:
    :param remove_attributes:
  """
    soup = BeautifulSoup(html_content, "html.parser")

    tags_to_remove = ["style", "class", "input", "picture", "source", "noscript", "img", "iframe", "svg", "path",
                      "link", "meta", "script"]

    # Remove script tags
    for script in soup(tags_to_remove):
        script.decompose()

    if remove_attributes:
        for tag in soup.find_all():
            for attribute in tags_to_remove:
                del tag[attribute]

    # Remove loose text within the <body>
    body = soup.body
    if body is not None:
        for child in body.contents[:]:
            if not child.name:  # Check if it's a NavigableString
                child.extract()  # Remove the element

    # removeNewLines

    articles = []
    # for article_element in soup.find_all("article"):
    #
    #     print(article_element)
    #     title_element = article_element.find("h2").find("a")
    #     title = title_element.text.strip()
    #     link = title_element["href"]
    #
    #     date_element = article_element.find("p").find("span")
    #     date = date_element.text.strip() if date_element else None
    #
    #     summary_element = article_element.find("div", class_="post-content")
    #     summary = summary_element.text.strip() if summary_element else None
    #
    #     articles.append({
    #         "title": title,
    #         "link": link,
    #         "date": date,
    #         "summary": summary,
    #     })

    # print("Articles length: ", len(articles))
    return soup.contents.__str__()


def url_to_file_name(url):
    return url.replace("https://", "").replace("http://", "").replace("/", "").replace(".", "").replace("?",
                                                                                                        "").replace("=",
                                                                                                                    "").replace(
        "&", "").replace(":", "").replace("-", "").replace("_", "").replace("!", "").replace(";", "").replace(",",
                                                                                                              "").replace(
        " ", "").replace("%", "").replace("#", "").replace("@", "")


def get_html(url, cache=False, clean=False):
    logger.info(f"Getting html from {url}, cache: {cache}, clean: {clean}")
    if cache:
        try:
            return load_html(f"{url_to_file_name(url)}.html")
        except FileNotFoundError:
            pass

    try:
        # Use Selenium to download the source text
        # headless humen like browsing
        options = Options()
        # options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        html_content = driver.page_source
        # print(html_content)
        driver.quit()
        save_html(html_content, f"{url_to_file_name(url)}.html")
        if clean:
            html_content = clean_html(html_content)
        return html_content
    except Exception as e:
        logger.error(f"Failed to get html from {url}: {e}")
        return ""


def save_html(html, filename):
    with open(f"./storage/htmls/{filename}", "w", encoding="utf-8") as file:
        file.write(html)


def load_html(filename):
    with open(f"./storage/htmls/{filename}", "r", encoding="utf-8") as file:
        return file.read()