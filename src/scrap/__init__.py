import logging
import os

from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options

from src.scrap.scrapper import Scrapper
from src.utils import storage_path, url_to_file_name

logger = logging.getLogger('actor').getChild("scrap_tools")


async def get_html_async(url, cache=False, clean=False, screenshots=True, custom_load=None):
    logger.info(f"Getting html from {url}, cache: {cache}, clean: {clean}")

    sc = Scrapper(max_pages=2)
    html = await sc.get_html(url, clean=clean, screenshots=screenshots, custom_load=custom_load)
    return html
