import requests
from bs4 import BeautifulSoup

# Base URL of the wiki
base_url = "https://github.com/fhamborg/news-please/wiki/"

# Function to scrape a single page
def scrape_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract content within the main wiki content area
    content_div = soup.find("div", class_="markdown-body")
    if content_div is None:
        return ""
    page_content = content_div.get_text(separator="\n").strip()
    return page_content

# Function to get all wiki page links
def get_wiki_links_0():
    response = requests.get(base_url)
    # print(response.content)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all wiki page links
    wiki_links = []
    for link in soup.find_all("a", class_="wiki-page-link"):
        href = link.get("href")
        if href and not href.startswith("#"):
            wiki_links.append(base_url + href)
    return wiki_links

def get_wiki_links():
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, "html.parser")

    #find all href that start with /fhamborg/news-please/wiki/
    wiki_links = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and href.startswith("/fhamborg/news-please/wiki/"):
            # href with /fhamborg/news-please/wiki/ replace with base_url
            print(href)
            wiki_link = href.replace("/fhamborg/news-please/wiki/", base_url)
            print(wiki_link)
            wiki_links.append(wiki_link)

    return wiki_links

# Get all wiki page links
wiki_links = get_wiki_links()
print(f"Found {len(wiki_links)} wiki pages")

# Scrape content from each page and combine
all_content = ""
for link in wiki_links:
    page_content = scrape_page(link)
    print(f"Scraped: {link}")
    print(page_content)
    print("----\n\n\n\n")
    all_content += f"--- Page: {link} ---\n\n{page_content}\n\n"

# Save combined content to a file
with open("text/wiki_content.txt", "w", encoding="utf-8") as f:
    f.write(all_content)

print("Wiki content scraped and saved to wiki_content.txt")
