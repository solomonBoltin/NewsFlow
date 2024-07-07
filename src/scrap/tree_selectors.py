# This Python file uses the following encoding: utf-8
import asyncio
from typing import List, Dict

from bs4 import BeautifulSoup, Tag

from src.scrap import get_html_async


def extract_articles(html_text, article_css_selector):
    soup = BeautifulSoup(html_text, 'html.parser')
    articles = soup.select(article_css_selector)  # Assuming 'cardlist' is the common parent class
    article_html_list = [str(article) for article in articles]
    return article_html_list


def extract_nesting_depth(html_text):
    """Extracts the nesting depth of HTML tags in the given HTML code.

    Args:
      html_text: The HTML code as a string.

    Returns:
      A number representing the maximum nesting depth of HTML tags.
    """

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html_text, 'html.parser')

    # Define a recursive function to traverse the tree and calculate depths
    def traverse_and_calculate_depth(tag, depth):
        # Initialize the current depth to 1
        current_depth = 1
        # Update the current depth based on the depth of children
        for child in tag.children:
            if child.name is not None:
                current_depth = max(current_depth, traverse_and_calculate_depth(child, depth + 1))
        return current_depth

    # Start the traversal with the root element and depth 1
    max_depth = traverse_and_calculate_depth(soup, 1)

    return max_depth


def extract_tag_tree(html_text):
    """Extracts the HTML tag tree structure without attributes, content, or spaces.

    Args:
      html_text: The HTML code as a string.

    Returns:
      A string representing the nested HTML tag tree structure.
    """

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html_text, 'html.parser')

    # Define a recursive function to traverse the tree and extract tags
    def traverse_and_extract(tag, result):
        result.append(tag.name)  # Add the current tag to the result
        for child in tag.children:
            if child.name is not None:  # Check if the child is a tag (not text or comment)
                traverse_and_extract(child, result)

    # Start the traversal with the root element and an empty list
    tag_tree = []
    traverse_and_extract(soup, tag_tree)

    # Join the tag names into a string, representing the nested structure
    return ''.join(tag_tree).replace("[document]", "")


# def extract_dad_tree(full_):


def get_parents(element, depth=20):
    parent = element.parent
    position_in_parent = [ch for ch in parent.children if ch.name == element.name].index(element)
    parents = [element.name + f"[{position_in_parent}]", ]

    for i in range(depth):
        if not parent or not parent.parent:
            break

        element = parent
        parent = parent.parent
        position_in_parent = [ch for ch in parent.children if ch.name == element.name].index(element)
        parents = [parent.name + f"[{position_in_parent}]"] + parents
    # reversed parents
    return parents


def find_by_parents(html_text, parents, or_by_css=None):
    found_by_tree = []
    soup = BeautifulSoup(html_text, 'html.parser')
    for element in soup.find_all():
        if parents == get_parents(element, len(parents)):
            found_by_tree.append(element)

    # if there are more than one element found, ex: div<span,span>, so will check if there is one that matches the css
    # other possible solution is to attach tags position in parent so parents tree would look div[0]span[1]
    if len(found_by_tree) > 1 and or_by_css:
        found_by_tree = [el for el in found_by_tree if el in soup.select(or_by_css)]

    return found_by_tree


def find_by_multiple_trees(html_text, trees) -> Dict[str, List[BeautifulSoup]]:
    found_by_tree = {}
    soup = BeautifulSoup(html_text, 'html.parser')

    for element in soup.find_all():
        tag_tree = extract_tag_tree(element.__str__())
        if tag_tree in trees:
            if tag_tree in found_by_tree:
                found_by_tree[tag_tree].append(element)
            else:
                found_by_tree[tag_tree] = [element]

    return found_by_tree


def find_by_trees(html_text, trees, or_by_css=None):
    found_by_tree = []
    soup = BeautifulSoup(html_text, 'html.parser')
    for element in soup.find_all():
        tag_tree = extract_tag_tree(element.__str__())
        if tag_tree in trees:
            found_by_tree.append(element)

    if not found_by_tree and or_by_css:
        found_by_tree = soup.select(or_by_css)

    return found_by_tree


def get_articles_tree_and_verify(html, selector):
    articles = extract_articles(html, selector)
    articles_trees = [extract_tag_tree(tree) for tree in articles]
    articles_trees = list(dict.fromkeys(articles_trees))
    found_by_trees = find_by_trees(html, articles_trees)
    return articles_trees, len(articles), (len(articles) == len(found_by_trees) & len(articles))


#
# # Example usage:
# full_html = open('./pharmatimes_com.html', 'r').read()
#
#
# website_articles_selector = '.dgbm_post_item'
#
# # extracting articles with css
# articles = extract_articles(full_html, website_articles_selector)
#
# # generating there trees
# articles_trees = [extract_tag_tree(tree) for tree in articles]
# articles_trees = list(dict.fromkeys(articles_trees))
#
# print(articles_trees)
#
# # finding articles by trees
# found_by_trees = find_by_trees(full_html, articles_trees)
#
#
# print(len(articles))
# print(len(found_by_trees))
# print(articles_trees)


def test_tag_tree():
    html_text = """<li class="grid__item">

<link href="//sananes.co.il/cdn/shop/t/38/assets/component-rating.css?v=173409050425969898561718031269" rel="stylesheet" type="text/css" media="all">

<div class="card-wrapper">
  <a href="/collections/%D7%A4%D7%A8%D7%A7%D7%98-%D7%A4%D7%A8%D7%A7%D7%98-%D7%A2%D7%A5/products/%D7%A4%D7%A8%D7%A7%D7%98-spc-%D7%93%D7%92%D7%9D-ca169" class="full-unstyled-link">
    <span class="visually-hidden">פרקט SPC דגם CA169</span>
  </a>
  <use-animate data-animate="zoom-fade-small" class="card card--product" tabindex="-1" animate="">
      <a href="/collections/%D7%A4%D7%A8%D7%A7%D7%98-%D7%A4%D7%A8%D7%A7%D7%98-%D7%A2%D7%A5/products/%D7%A4%D7%A8%D7%A7%D7%98-spc-%D7%93%D7%92%D7%9D-ca169" class="card__media media-wrapper" tabindex="-1">
        <div class="card--image-animate image-animate media media--square media--hover-effect"><img src="//sananes.co.il/cdn/shop/products/5905167839386_I_03_87bdb9c5-d609-4a27-8780-8912fa5a0e2e.webp?v=1679308322&amp;width=1100" alt="פרקט SPC דגם CA169" srcset="//sananes.co.il/cdn/shop/products/5905167839386_I_03_87bdb9c5-d609-4a27-8780-8912fa5a0e2e.webp?v=1679308322&amp;width=165 165w, //sananes.co.il/cdn/shop/products/5905167839386_I_03_87bdb9c5-d609-4a27-8780-8912fa5a0e2e.webp?v=1679308322&amp;width=360 360w, //sananes.co.il/cdn/shop/products/5905167839386_I_03_87bdb9c5-d609-4a27-8780-8912fa5a0e2e.webp?v=1679308322&amp;width=535 535w, //sananes.co.il/cdn/shop/products/5905167839386_I_03_87bdb9c5-d609-4a27-8780-8912fa5a0e2e.webp?v=1679308322&amp;width=750 750w, //sananes.co.il/cdn/shop/products/5905167839386_I_03_87bdb9c5-d609-4a27-8780-8912fa5a0e2e.webp?v=1679308322&amp;width=940 940w, //sananes.co.il/cdn/shop/products/5905167839386_I_03_87bdb9c5-d609-4a27-8780-8912fa5a0e2e.webp?v=1679308322&amp;width=1100 1100w" width="1100" height="1467" loading="lazy" class="motion-reduce loaded" sizes="(min-width: 1600px) 367px, (min-width: 990px) calc((100vw - 10rem) / 4), (min-width: 750px) calc((100vw - 10rem) / 3), calc(100vw - 3rem)" is="lazy-image"><img src="//sananes.co.il/cdn/shop/products/5905167839386_I_04_6ef1bda3-1574-4dcc-998a-dff106a6ce55.webp?v=1678364649&amp;width=1100" alt="פרקט SPC דגם CA169" srcset="//sananes.co.il/cdn/shop/products/5905167839386_I_04_6ef1bda3-1574-4dcc-998a-dff106a6ce55.webp?v=1678364649&amp;width=165 165w, //sananes.co.il/cdn/shop/products/5905167839386_I_04_6ef1bda3-1574-4dcc-998a-dff106a6ce55.webp?v=1678364649&amp;width=360 360w, //sananes.co.il/cdn/shop/products/5905167839386_I_04_6ef1bda3-1574-4dcc-998a-dff106a6ce55.webp?v=1678364649&amp;width=535 535w, //sananes.co.il/cdn/shop/products/5905167839386_I_04_6ef1bda3-1574-4dcc-998a-dff106a6ce55.webp?v=1678364649&amp;width=750 750w, //sananes.co.il/cdn/shop/products/5905167839386_I_04_6ef1bda3-1574-4dcc-998a-dff106a6ce55.webp?v=1678364649&amp;width=940 940w, //sananes.co.il/cdn/shop/products/5905167839386_I_04_6ef1bda3-1574-4dcc-998a-dff106a6ce55.webp?v=1678364649&amp;width=1100 1100w" width="1100" height="825" loading="lazy" class="motion-reduce loaded" sizes="(min-width: 1600px) 367px, (min-width: 990px) calc((100vw - 10rem) / 4), (min-width: 750px) calc((100vw - 10rem) / 3), calc(100vw - 3rem)" is="lazy-image"></div>
      </a></use-animate>

  <div class="card-information">
    <div class="card-information__wrapper"><div class="card-information__top"></div><a href="/collections/%D7%A4%D7%A8%D7%A7%D7%98-%D7%A4%D7%A8%D7%A7%D7%98-%D7%A2%D7%A5/products/%D7%A4%D7%A8%D7%A7%D7%98-spc-%D7%93%D7%92%D7%9D-ca169" class="card-information__text h4" tabindex="-1">
        פרקט SPC דגם CA169
      </a>


      <span class="caption-large light"></span>


<div class="price price--on-sale">
  <dl><div class="price__regular">
      <dt>
        <span class="visually-hidden visually-hidden--inline">מחיר באתר</span>
      </dt>
      <dd>
        <span class="price-item price-item--regular">
          <price-money><bdi><span class="price__prefix">₪</span>157<sup class="price__suffix">.50</sup> </bdi></price-money>


     למ"ר




        </span>
      </dd>
    </div>
    <div class="price__sale"><dt class="price__compare">
          <span class="visually-hidden visually-hidden--inline">מחיר באתר</span>
        </dt>
        <dd class="price__compare">
          <s class="price-item price-item--regular">
            <price-money><bdi><span class="price__prefix">₪</span>175<sup class="price__suffix">.00</sup> </bdi></price-money>
          </s>
        </dd><dt>
        <span class="visually-hidden visually-hidden--inline">מחיר מבצע</span>
      </dt>
      <dd>
        <span class="price-item price-item--sale">
          <price-money><bdi><span class="price__prefix">₪</span>157<sup class="price__suffix">.50</sup> </bdi></price-money>


     למ"ר




        </span>
      </dd>
    </div></dl></div>
</div>

    <div class="card-information__button"><quick-view-button class="button button--small" data-product-url="/collections/%D7%A4%D7%A8%D7%A7%D7%98-%D7%A4%D7%A8%D7%A7%D7%98-%D7%A2%D7%A5/products/%D7%A4%D7%A8%D7%A7%D7%98-spc-%D7%93%D7%92%D7%9D-ca169">
                בחירת אפשרויות
                <svg class="icon icon-cart" aria-hidden="true" focusable="false">
                  <use href="#icon-cart"></use>
                </svg>
              </quick-view-button></div>
  </div>

  <div class="card__badge"><span class="badge badge--onsale" aria-hidden="true">
מבצע

        </span></div><quick-view-drawer>
      <details>
        <summary class="quick-view__summary" tabindex="-1">
          <span class="visually-hidden">צפייה מהירה</span>
          <svg xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false" class="icon icon-search" fill="none" viewBox="0 0 15 17">
      <circle cx="7.11113" cy="7.11113" r="6.56113" stroke="currentColor" stroke-width="1.1" fill="none"></circle>
      <path d="M11.078 12.3282L13.8878 16.0009" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" fill="none"></path>
    </svg>
        </summary>
        <quick-view class="quick-view" data-product-url="/collections/%D7%A4%D7%A8%D7%A7%D7%98-%D7%A4%D7%A8%D7%A7%D7%98-%D7%A2%D7%A5/products/%D7%A4%D7%A8%D7%A7%D7%98-spc-%D7%93%D7%92%D7%9D-ca169">
          <div role="dialog" aria-label="" aria-modal="true" class="quick-view__content" tabindex="-1"></div>
        </quick-view>
      </details>
    </quick-view-drawer></div>

              </li>"""

    tag_tree = extract_tag_tree(html_text)
    print(tag_tree)


async def test_find_by_multiple_trees():
    html_text = await get_html_async(
        "https://sananes.co.il/collections/%D7%A4%D7%A8%D7%A7%D7%98-%D7%A4%D7%A8%D7%A7%D7%98-%D7%A2%D7%A5", clean=True)
    tree = ("lilinkdivaspanuse-animateadivimgimgdivdivdivaspandivdldivdtspanddspanprice"
            "-moneybdispansupdivdtspanddsprice-moneybdispansupdtspanddspanprice-moneybdispansupdivquick-view"
            "-buttonsvgusedivspanquick-view-drawerdetailssummaryspansvgcirclepathquick-viewdiv")

    res = find_by_multiple_trees(html_text, [tree])
    print(len(res))
    print(len(res.get(tree)[0]))


if __name__ == "__main__":
    # test_tag_tree()
    asyncio.run(test_find_by_multiple_trees())
