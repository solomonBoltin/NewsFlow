import re
import time

import requests
from GoogleNews import GoogleNews
from bs4 import BeautifulSoup
from newspaper import Article
import datetime
import json
import os
import sqlite3
from newsplease import NewsPlease
from newsplease.NewsArticle import NewsArticle

# google_news = GNews()
# pakistan_news = google_news.get_news('Pakistan')
# print(pakistan_news[0])

# Set up Google News API
news = GoogleNews()  #lang='en', region='IL')  # Customize for Israel

# Get today's date and calculate a day ago
today = datetime.date.today()
dayAgo = today - datetime.timedelta(days=1)


def pre_process_google_news_result(item):
    item["url"] = item['link'].split("&")[0]
    item["source"] = item['url'].split('//')[1].split("/")[0]
    item["date"] = item['date'].__str__()
    item["datetime"] = item['datetime'].__str__()
    return item


def process_google_news_result(item):
    article = Article(item["url"])
    try:
        article.download()
        article.parse()
        item['title'] = article.title
        item['authors'] = article.authors
        item['publish_date'] = article.publish_date.__str__()
        item['text'] = article.text

    except Exception as e:
        print(f"failed getting {item['url']}")
        print(e)

    return item


def url_to_file_name(url):
    return url.replace("https://", "").replace("http://", "").replace("/", "").replace(".", "").replace("?",
                                                                                                        "").replace("=",                                                                                             "").replace(
        "&", "").replace(":", "").replace("-", "").replace("_", "").replace("!", "").replace(";", "").replace(",",
                                                                                                              "").replace(
        " ", "").replace("%", "").replace("#", "").replace("@", "")


def save_article(item):
    with open(f"{url_to_file_name(item['url'])}.json", "w") as f:
        json.dump(item, f)
        print(f"saved {item['url']}")


def check_if_exists(url):
    # check if file exists
    return os.path.exists(f"{url_to_file_name(url)}.json")


def get_g_news_loop():
    keywords = ["interest rates", "inflation", "unemployment", "earnings report", "merger", "acquisition",
                "product launch", "product recall", "war", "election", "trade deal", "natural disaster"]

    print("Starting news loop")
    while True:
        for keyword in keywords:
            news.search(keyword)
            # news.setTimeRange(dayAgo.__str__(), today.__str__())
            results = news.results(sort=True)
            for item in results:
                item = pre_process_google_news_result(item)
                if not check_if_exists(item['url']):
                    print(f"new news {item['title']}")
                    item = process_google_news_result(item)
                    save_article(item)

                else:
                    print(f"already have {item['title']}")
        time.sleep(60)


# get_g_news_loop()

def extract_urls(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    all_links = soup.find_all('a', href=True)

    urls = []
    for link in all_links:
        href = link['href']

        # Optional: Use regular expressions for refined filtering
        if re.match(r"https?://", href):  # Check for http/https
            urls.append(href)

    return urls

def get_news_pleas_loop():
    url1 = "https://www.wicz.com/story/50640064/candel-therapeutics-announces-positive-interim-data-from-randomized-phase-2-clinical-trial-of-can-2409-in-non-metastatic-pancreatic-cancer"
    url2 = "https://www.nytimes.com/2017/02/23/us/politics/cpac-stephen-bannon-reince-priebus.html?hp"
    url3 = "https://www.reuters.com/"

    from selenium import webdriver

    browser = webdriver.Chrome(

    )
    browser.get(url3)
    source = browser.page_source
    print(source)
    input("---")
    print(extract_urls(source))
    input("---")
    soup = BeautifulSoup(browser.page_source, "html.parser")
    links = soup.find_all("a")
    for link in links:
        print(link['href'])
    article: NewsArticle = NewsPlease.from_url(url3)

    print(article.get_serializable_dict())
    print(article.title)

# get_news_pleas_loop()