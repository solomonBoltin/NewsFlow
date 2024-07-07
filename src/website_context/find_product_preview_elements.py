import logging

from src.ask_llm.llm_tasks.product_preview_elements_extractor import extract_product_preview_element
from src.scrap.tree_selectors import *
from src.utils.__init__ import extract_base_url

logger = logging.getLogger("actor").getChild("find_product_preview_elements")


def extract_urls(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    all_links = soup.find_all('a', href=True)

    urls = []
    for link in all_links:
        href = link['href']
        urls.append(href)

    return urls


def looks_like_product(element):
    # check if element looks like a product (has between 2-30 children, at least one url, some text, and possibly an
    # image)
    count = len(element.find_all())

    if 2 <= count:
        urls = extract_urls(element.__str__())
        images = element.find_all('img')
        if urls and len(element.text) > 5 and (images or '$' in element.text or '€' in element.text):
            return True

    return False


def looks_like_products(elements_group: list):
    # check if group of elements looks like products (has at least 3 elements)
    if len(elements_group) >= 3:
        return True
    return False


def extract_groups(html_content):
    # extract groups of elements that look like products
    soup = BeautifulSoup(html_content, "html.parser")

    filtered_elements = [element for element in soup.find_all() if looks_like_product(element)]

    # group by tag tree
    grouped_elements = {}
    for element in filtered_elements:
        tag_tree = extract_tag_tree(element.__str__())
        if tag_tree in grouped_elements:
            grouped_elements[tag_tree].append(element)
        else:
            grouped_elements[tag_tree] = [element]

    # filter groups
    grouped_elements = {key: value for key, value in grouped_elements.items() if looks_like_products(value)}

    # removing trees that are in other trees
    new_grouped_elements = grouped_elements.copy()
    for tree, group in grouped_elements.items():
        for other_tree, other_group in grouped_elements.items():
            # if tree is in other tree and has fewer elements
            if tree != other_tree and tree in other_tree and len(group) <= len(other_group):
                del new_grouped_elements[tree]
                break

    sorted_results = sorted(new_grouped_elements.items(), key=lambda x: len(x[1]), reverse=True)

    return sorted_results


async def find_product_preview_elements(product_page_url, caching=True, ai_caching=True):
    # returns jsons representing products with selectors to element, title, link, price, image
    logger.info(f"Getting product preview elements from {product_page_url}")

    base_url = extract_base_url(product_page_url)

    html_content = await get_html_async(product_page_url, cache=caching, clean=False)


    grouped_elements = extract_groups(html_content)
    logger.info(f"Found {len(grouped_elements)} groups of elements that are potential product previews.")

    product_elements = {}
    for tree, group in grouped_elements:
        first_element = group[0]
        first_element_html = first_element.__str__()
        element_analysis = extract_product_preview_element(base_url, first_element_html, ai_caching)

        if element_analysis["is_product"]:
            product_elements[tree] = element_analysis

    logger.info(f"Found {len(product_elements)} product preview elements.")
    return product_elements


async def test_extract_products_css():
    # logger.setLevel(logging.DEBUG)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

    logger.info("Testing product preview elements extraction...")

    product_page_url = "https://sananes.co.il/collections/%D7%A4%D7%A8%D7%A7%D7%98-%D7%A4%D7%A8%D7%A7%D7%98-%D7%A2%D7%A5"
    res = await find_product_preview_elements(product_page_url)

    print("Product preview elements:")
    print(res)
    for tree, element in res.items():
        print(f"Tree: {tree}")
        print(f"Element: {element}")
        print()


if __name__ == '__main__':
    asyncio.run(test_extract_products_css())

