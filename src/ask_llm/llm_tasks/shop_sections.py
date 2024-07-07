import json
import logging
import os
from datetime import datetime
from os import path

from openai import APIConnectionError

from src.ask_llm.__init__ import ask_llm
from src.utils import storage_path
from src.utils.__init__ import url_to_filename

logger = logging.getLogger(__name__)

history_for_identifying_product_sections = [
    {
        "role": "user",
        "content": """You will be given base_url - the shop website url, and input_urls - links to be analyzed.
        Analyze each input_url and fit it to the most suited category:
        product_page: directs to a specific product.
        product_category_page: directs to a section containing multiple products of the same category.
        non_product_page: directs to any other page not directly related to products.
        your complete output should be in json in this format {"url": {"reasoning": "text", "category": "<one of the three>"}}.
    """
    },
    {
        "role": "model",
        "content": "Understood. Please provide the base_url and input_urls for analysis."
    },
    {
        "role": "user",
        "content": "base_url=https://www.example-shop.com\n"
                   "input_urls=['https://www.example-shop.com/products/blue-t-shirt',\n"
                   "'https://www.example-shop.com/category/mens-clothing',\n"
                   "'https://www.example-shop.com/about-us',\n"
                   "'https://www.example-shop.com/products/red-sneakers',\n"
                   "'https://www.example-shop.com/category/accessories']"
    },
    {
        "role": "model",
        "content": """```json
{
  "https://www.example-shop.com/products/blue-t-shirt": {
    "reasoning": "This URL directs to a specific product page for a blue t-shirt.",
    "category": "product_page"
  },
  "https://www.example-shop.com/category/mens-clothing": {
    "reasoning": "This URL directs to a category page containing multiple men's clothing products.",
    "category": "product_category_page"
  },
  "https://www.example-shop.com/about-us": {
    "reasoning": "This URL directs to an informational page about the company, not directly related to products.",
    "category": "non_product_page"
  },
  "https://www.example-shop.com/products/red-sneakers": {
    "reasoning": "This URL directs to a specific product page for red sneakers.",
    "category": "product_page"
  },
  "https://www.example-shop.com/category/accessories": {
    "reasoning": "This URL directs to a category page containing multiple accessory products.",
    "category": "product_category_page"
  }
}
```"""
    }
]


def product_categories_path():
    if not path.exists(f"./{storage_path()}/product_url_categories"):
        os.mkdir(f"./{storage_path()}/product_url_categories")
    return f"./{storage_path()}/product_url_categories"


def save_product_categories_to_cache(base_url, output):
    filename = f"{product_categories_path()}/{url_to_filename(base_url)}.json"
    try:
        if path.exists(filename):
            with open(filename, "r") as f:
                js = json.load(f)
        else:
            js = {}
    except json.JSONDecodeError:
        logger.warning(f"Error loading existing JSON from {filename}. Starting with a new dictionary.")
        js = {}

    for url, data in output.items():
        js[url] = data

    with open(filename, "w") as f:
        json.dump(js, f)


def get_product_categories_from_cache(base_url, input_urls):
    filename = f"{product_categories_path()}/{url_to_filename(base_url)}.json"

    results = {}
    if path.exists(filename):
        with open(filename, "r") as f:
            cache_js = json.load(f)
            logger.debug(f"Loaded {len(cache_js.keys())} categorised product urls from cache.")

            for input_url in input_urls:
                cache = cache_js.get(input_url)
                if cache:
                    results[input_url] = cache

    return results


def categorize_product_urls(base_url, input_urls, model_name="gpt4all", caching=False, max_retries=3):
    logger.debug(
        f"Categorizing product urls using ai model {model_name} for base_url {base_url} and input_urls {input_urls}")

    cache = get_product_categories_from_cache(base_url, input_urls) if caching else {}
    input_urls = [url for url in input_urls if not cache.get(url)]
    if not input_urls:
        logger.debug("All product urls are already in cache.")
        return cache

    logger.debug(f"Cache contains {len(cache.keys())} urls, {len(input_urls)} urls will be sent to ai.")

    response_text = ""
    for retries in range(max_retries):
        try:
            response_text = ask_llm(
                history_for_identifying_product_sections,
                f"base_url={base_url}\n"
                f"input_urls={input_urls}",
                model_name=model_name
            )

            json_string = response_text[response_text.find("{"):response_text.rfind("}") + 1]
            categories_js = json.loads(json_string)

            save_product_categories_to_cache(base_url, categories_js)

            categories_js.update(cache)
            return categories_js

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parsing JSON (attempt {retries + 1}): {e} Response: {response_text}")

        except (ConnectionError, APIConnectionError) as e:
            logger.error(f"Connection error (attempt {retries + 1}): {e}")

    logger.error(f"Failed to parse valid JSON after multiple retries. Response: {response_text}")
    raise ValueError("Failed to parse valid JSON after multiple retries.")


def categorize_shop_urls(base_url, input_urls, caching=False):
    return categorize_product_urls(base_url, input_urls, model_name="gpt4all", caching=caching)


def test_categorize_shop_urls():
    base_url = "https://www.example-shop.com"
    input_urls = [
        "https://www.example-shop.com/products/wireless-headphones",
        "https://www.example-shop.com/category/electronics",
        "https://www.example-shop.com/contact-us",
        "https://www.example-shop.com/products/smartphone-case",
        "https://www.example-shop.com/category/accessories",
    ]

    logger.info("Categorizing shop URLs using AI, this may take a moment...")

    start_time = datetime.now()
    logger.info(f"Start time: {start_time}")
    output = categorize_product_urls(base_url, input_urls, model_name="gemini", caching=True)
    end_time = datetime.now()
    logger.info(f"End time: {end_time}")
    logger.info(f"Time taken: {end_time - start_time}")

    for url, data in output.items():
        logger.info(f"{url}: {data} \n------\n")

# Not used -- instead all shop sections are used
if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    # test_categorize_shop_urls()
