import json
import logging
import os
from os import path

from bs4 import BeautifulSoup

from src.ask_llm.__init__ import ask_llm
from src.scrap.tree_selectors import get_parents, find_by_parents, extract_tag_tree
from src.utils.__init__ import url_to_filename, storage_path

logger = logging.getLogger("actor").getChild("product_preview_element_processor")

product_preview_selectors_chat = [
    {
        "role": "user",
        "content": """Task:
Given an HTML snippet representing a product or product preview, extract the following information:
Is Product? (Boolean): Determine if the snippet represents a product or some other element.
Title Selector: CSS selector that accurately targets the product's title.
Link Selector: CSS selector that targets the link leading to the full product page.
Price Selector: CSS selector that targets the element containing the price of the product.
Image Selector: CSS selector that targets the product image.
Input:
A string containing the HTML snippet of the product or product preview.
Output:
A JSON object with the following structure:
{
  "is_product": true/false,
  "title_selector": "CSS selector string",
  "link_selector": "CSS selector string",
  "price_selector": "CSS selector string",
  "image_selector": "CSS selector string"
}
        """
    },
    {
        "role": "model",
        "content": "I understand. Please provide the HTML snippet for the product preview element."
    }
]


def extract_product_selectors(html_element):
    # returns a dictionary with selections or empty dictionary
    response_text = ask_llm(product_preview_selectors_chat, html_element, model_name="gemini")

    try:
        json_string = response_text[response_text.find("{"):response_text.rfind("}") + 1]
        output = json.loads(json_string)
        return output

    except json.JSONDecodeError as e:
        logger.error(f"Failed parsing ai json response: {response_text}, error: {e}")

    return {}


def element_map_path():
    if not path.exists(f"./{storage_path()}/product_element_maps"):
        os.mkdir(f"./{storage_path()}/product_element_maps")

    return f"./{storage_path()}/product_element_maps"


def save_element_tree_map_to_cache(base_url, tree, map):
    filename = f"{element_map_path()}/{url_to_filename(base_url)}.json"
    try:
        if path.exists(filename):
            with open(filename, "r") as f:
                js = json.load(f)
        else:
            js = {}
    except json.JSONDecodeError:
        logger.warning(f"Error loading existing JSON from {filename}. Starting with a new dictionary.")
        js = {}

    js[tree] = map

    with open(filename, "w") as f:
        json.dump(js, f)


def load_element_tree_map_from_cache(base_url, tree):
    filename = f"{element_map_path()}/{url_to_filename(base_url)}.json"
    try:
        with open(filename, "r") as f:
            js = json.load(f)
            return js.get(tree)
    except FileNotFoundError:
        return None


def extract_product_preview_element(base_url, element_text, caching=True):
    element_tree = extract_tag_tree(element_text)

    if caching:
        cache = load_element_tree_map_from_cache(base_url, element_tree)
        if cache:
            return cache

    logger.debug(f"Processing product preview element: {element_tree} from {base_url}")
    element_soup = BeautifulSoup(element_text, "html.parser")
    output = extract_product_selectors(element_text)

    if not output or not output.get("is_product"):
        indexer = {"is_product": False}
        save_element_tree_map_to_cache(base_url, element_tree, indexer)
        return indexer

    logger.debug(f"Extracted product preview selectors: {output}")

    title_css = output.get("title_selector")
    link_css = output.get("link_selector")
    price_css = output.get("price_selector")
    image_css = output.get("image_selector")

    title_elements = element_soup.select(title_css) if title_css else None
    link_elements = element_soup.select(link_css) if link_css else None
    price_elements = element_soup.select(price_css) if price_css else None
    image_elements = element_soup.select(image_css) if image_css else None

    title_element = title_elements[0] if title_elements else None
    link_element = link_elements[0] if link_elements else None
    price_element = price_elements[0] if price_elements else None
    image_element = image_elements[0] if image_elements else None

    title_tree = get_parents(title_element) if title_element else None
    link_tree = get_parents(link_element) if link_element else None
    price_tree = get_parents(price_element) if price_element else None
    image_tree = get_parents(image_element) if image_element else None

    title_text = title_element.text if title_element else None
    link_text = link_element['href'] if link_element else None
    price_text = price_element.text if price_element else None
    image_src = image_element.get("src") if image_element else None

    title_text_by_tree = find_by_parents(element_text, title_tree)[0].text if title_tree else None
    link_text_by_tree = find_by_parents(element_text, link_tree)[0]['href'] if link_tree else None
    price_text_by_tree = find_by_parents(element_text, price_tree)[0].text if price_tree else None
    image_src_by_tree = find_by_parents(element_text, image_tree)[0].get("src") if image_tree else None

    # todo assert that the text is the same as the text by tree

    product_map = {
        "is_product": True,
        "element_tree": element_tree,
        "title": title_text_by_tree,
        "title_css": title_css,
        "title_parents_tree": title_tree,
        "link": link_text_by_tree,
        "link_css": link_css,
        "link_parents_tree": link_tree,
        "price": price_text_by_tree,
        "price_css": price_css,
        "price_parents_tree": price_tree,
        "image": image_src_by_tree,
        "image_css": image_css,
        "image_parents_tree": image_tree
    }
    save_element_tree_map_to_cache(base_url, element_tree, product_map)
    return product_map


def test_process_product_preview_element():
    # You'll need to replace this with an actual product preview HTML snippet
    sample_product_html = """
    <div class="product-preview">
        <a href="/product/123">
            <img src="/images/product123.jpg" alt="Product 123">
            <h3>Product 123 Name</h3>
            <span class="price">$99.99</span>
        </a>
    </div>
    """

    logging.basicConfig(filename='actor.log', level=logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

    logger.info("Testing extract_product_preview_element")

    base_url = "https://sananes.co.il/"
    res = extract_product_preview_element(base_url, sample_product_html)
    logger.info(res)


# Uncomment to run the test
test_process_product_preview_element()
