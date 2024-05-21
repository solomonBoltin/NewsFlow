from typing import List, Dict

from bs4 import BeautifulSoup


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
