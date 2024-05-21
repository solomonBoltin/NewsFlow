import json
import logging
from datetime import datetime
from os import path

from openai import APIConnectionError

from src.ask_llm.__init__ import ask_llm
from src.utils.__init__ import url_to_filename

logger = logging.getLogger(__name__)

history_for_identifying_sections = [
    {
        "role": "user",
        "content": """You will be given base_url - the news website url, and input_urls - links to be analized.
        Analyze each input_url and fit it to the most suited category:
        info_action_or_other_website_page: directs to action / info / outside of the website.
        article_page: directs to a specific article.
        articles_page: directs to a section containing multiple articles.
        your complete output should be in json in this format {"url": {"reasoning": "text", "category": "<one of the three>"}}.
    """
    },
    {
        "role": "model",
        "content": "Ok I understand. give me the first base_url and input_url."
    },
    {
        "role": "user",
        "content": "base_url=https://edition.cnn.com\n"
                   "input_urls=['https://edition.cnn.com/2024/04/11/economy/mortgage-rates-april-11/index.html',\n"
                   "'https://edition.cnn.com/2024/04/09/style/watches-and-wonders-womens-watches/index.html',\n"
                   "'https://edition.cnn.com/specials/photos',\n"
                   "'https://edition.cnn.com/videos/politics/2024/04/11/sean-hannity-arizona-abortion-ban-trump-roll-the-tape-keilar-vpx.cnn',\n"
                   "'https://edition.cnn.com/specials/cnn-longform']"
    },
    {
        "role": "model",
        "content": """```json
{
  "https://edition.cnn.com/2024/04/11/economy/mortgage-rates-april-11/index.html": {
    "reasoning": "This URL directs to a specific article about mortgage rates.",
    "category": "article_page"
  },
  "https://edition.cnn.com/2024/04/09/style/watches-and-wonders-womens-watches/index.html": {
    "reasoning": "This URL directs to a specific article about women's watches.",
    "category": "article_page"
  },
  "https://edition.cnn.com/specials/photos": {
    "reasoning": "This URL directs to a section containing multiple photos.",
    "category": "articles_page"
  },
  "https://edition.cnn.com/videos/politics/2024/04/11/sean-hannity-arizona-abortion-ban-trump-roll-the-tape-keilar-vpx.cnn": {
    "reasoning": "This URL directs to a specific video.",
    "category": "article_page"
  },
  "https://edition.cnn.com/specials/cnn-longform": {
    "reasoning": "This URL directs to a section containing multiple longform articles.",
    "category": "articles_page"
  }
}
```"""
    }

]


def save_categories_to_cache(base_url, output):
    filename = f"./storage/is_section/{url_to_filename(base_url)}.json"
    try:
        if path.exists(filename):
            with open(filename, "r") as f:
                js = json.load(f)
        else:
            js = {}  # Create an empty dictionary if the file doesn't exist
    except json.JSONDecodeError:
        logger.warning(f"Error loading existing JSON from {filename}. Starting with a new dictionary.")
        js = {}

    for url, data in output.items():
        js[url] = data

    with open(filename, "w") as f:  # 'w' to overwrite, consider 'a' to append
        json.dump(js, f)


def categories_urls_using_ai_cache(base_url, input_urls):
    filename = f"./storage/is_section/{url_to_filename(base_url)}.json"

    results = {}
    if path.exists(filename):
        with open(filename, "r") as f:
            cache_js = json.load(f)
            logger.debug(f"Loaded {len(cache_js.keys())} categorised urls from cache.")

            for input_url in input_urls:
                cache = cache_js.get(input_url)
                if cache:
                    results[input_url] = cache

    return results


def categories_urls_using_ai(base_url, input_urls, model_name="gpt4all", caching=False, max_retries=3):
    logger.debug(f"Categorizing url using ai model {model_name} for base_url {base_url} and input_urls {input_urls}")

    # loading available caches
    cache = categories_urls_using_ai_cache(base_url, input_urls) if caching else {}
    input_urls = [url for url in input_urls if not cache.get(url)]
    if not input_urls:
        logger.debug("All urls are already in cache.")
        return cache

    logger.debug(f"Cache contains {len(cache.keys())} urls, {len(input_urls)} urls will be sent to ai.")
    # asking ai
    response_text = ""
    for retries in range(max_retries):
        try:
            # query
            response_text = ask_llm(
                history_for_identifying_sections,
                f"base_url={base_url}\n"
                f"input_urls={input_urls}",
                model_name=model_name
            )

            # parsing answer
            json_string = response_text[response_text.find("{"):response_text.rfind("}") + 1]
            categories_js = json.loads(json_string)

            # saving to cache
            save_categories_to_cache(base_url, categories_js)

            # mixing with cache results
            categories_js.update(cache)
            return categories_js

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parsing JSON (attempt {retries + 1}): {e} Response: {response_text}")

        except (ConnectionError, APIConnectionError) as e:
            logger.error(f"Connection error (attempt {retries + 1}): {e}")

    logger.error(f"Failed to parse valid JSON after multiple retries. Response: {response_text}")
    raise ValueError("Failed to parse valid JSON after multiple retries.")


def categories_urls(base_url, input_urls, caching=False):
    return categories_urls_using_ai(base_url, input_urls, model_name="gpt4all", caching=caching)


def test_categories_urls():
    base_url = "https://www.timesofisrael.com/"
    input_urls = [
        "https://www.timesofisrael.com/israel-and-the-region/",
        "https://www.timesofisrael.com/jewish-times/",
        "https://www.timesofisrael.com/real-estate-israel-signup/",
        "https://www.timesofisrael.com/liveblog_entry/iran-says-it-wouldnt-need-to-retaliate-if-un-had-condemned-strike-on-damascus/",
        "https://google.com/",
    ]

    logger.info("Extracting sections using ai, might take a while")

    s_time = datetime.now()
    logger.info("Start time: ", s_time)
    output = categories_urls_using_ai(base_url, input_urls, model_name="gemini", caching=True)
    e_time = datetime.now()
    logger.info("End time: ", e_time)
    logger.info("Time taken: ", e_time - s_time)

    for url, data in output.items():
        logger.info(f"{url}: {data} \n------\n")


# test_categories_urls()
