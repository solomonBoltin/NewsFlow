import json
import logging
from os import path

from bs4 import BeautifulSoup

from src.ask_llm.__init__ import ask_llm
from src.scrap.tree_selectors import get_parents, find_by_parents, extract_tag_tree
from src.utils.__init__ import url_to_filename

logger = logging.getLogger("actor").getChild("article_preview_element_processor")

article_preview_selectors_chat = [
    {
        "role": "user",
        "content": """Task:
Given an HTML snippet representing a news article or article preview, extract the following information:
Is Article? (Boolean): Determine if the snippet represents an article or some other element.
Title Selector: CSS selector that accurately targets the article's title.
Link Selector: CSS selector that targets the link leading to the full article.
Date Selector: CSS selector that targets the element containing the publication or update date of the article.
Input:
A string containing the HTML snippet of the article or article preview.
Output:
A JSON object with the following structure:
{
  "is_article": true/false,
  "title_selector": "CSS selector string",
  "link_selector": "CSS selector string",
  "date_selector": "CSS selector string"
}
        """
    },
    {
        "role": "model",
        "content": "Ok i understand. give me the first html_element text."
    },
    {
        "role": "user",
        "content": """<div class="duet--content-cards--content-card group relative bg-white text-black dark:bg-gray-13 dark:text-white pb-24 border-b border-gray-cc dark:border-gray-4a sm:border-b-0 sm:mx-15 sm:w-1/2 lg:pb-24"><div class="flex md:flex-row ml-auto md:ml-none w-[320px] mt-24 sm:w-full sm:mt-0"><div class="relative w-full rounded-[2px] border border-solid border-gray-cc dark:border-gray-31"><div class="relative block w-full aspect-standard relative w-full"><a aria-hidden="true" class="block h-full w-full" href="/2024/4/12/24128584/spotify-music-pro-lossless-audio" tabindex="-1"><span style="box-sizing:border-box;display:block;overflow:hidden;width:initial;height:initial;background:none;opacity:1;border:0;margin:0;padding:0;position:absolute;top:0;left:0;bottom:0;right:0"></span></a></div><div class="below-0 pointer-events-none top-auto h-full w-full translate-y-0 bg-gradient-to-t from-black/10 to-transparent dark:absolute"></div><div class="below-0 pointer-events-none top-auto h-1/3 w-full translate-y-0 bg-gradient-to-t from-black/30 to-transparent dark:absolute"></div></div></div><a aria-label="Spotify’s lossless audio could finally arrive as part of ‘Music Pro’ add-on" class="after:absolute after:inset-0 group-hover:shadow-highlight-franklin dark:group-hover:shadow-highlight-blurple" href="/2024/4/12/24128584/spotify-music-pro-lossless-audio"></a><div class="relative z-10 pt-[12px] md:px-[16px] dark:border-none border-t-[3px] border-blurple dark:bg-transparent bg-white lg:mb-8 mr-[25px] md:mr-0 md:ml-40 lg:w-[440px] lg:ml-auto -mt-30 pr-12"><h2 class="mb-8 font-polysans text-30 font-bold leading-100 sm:text-35" style="text-shadow:0 0 40px rgb(0, 0, 0)"><a aria-label="Spotify’s lossless audio could finally arrive as part of ‘Music Pro’ add-on" class="after:absolute after:inset-0 group-hover:shadow-highlight-franklin dark:group-hover:shadow-highlight-blurple" href="/2024/4/12/24128584/spotify-music-pro-lossless-audio">Spotify’s lossless audio could finally arrive as part of ‘Music Pro’ add-on</a></h2><p class="duet--article--dangerously-set-cms-markup sm:text-23 font-fkroman text-20 font-light leading-120 tracking-1 sm:text-23">Major new features are coming to Spotify. The big question continues to be when it’ll happen.</p><div class="relative z-10 inline-block pt-4 font-polysans text-11 uppercase leading-140 tracking-15 text-gray-31 dark:text-gray-bd"><div class="inline-block"><a class="text-gray-31 hover:shadow-underline-inherit dark:text-franklin mr-8" href="/authors/chris-welch">Chris Welch</a></div><div class="inline-block text-gray-63 dark:text-gray-94"><time datetime="2024-04-12T18:25:02.352Z">Apr 12</time><span class="hide-coral-new-count byline-comment-count"><span class="mx-8">|</span><a aria-label="Spotify’s lossless audio could finally arrive as part of ‘Music Pro’ add-on" class="group hover:text-white" href="/2024/4/12/24128584/spotify-music-pro-lossless-audio?showComments=1"><span class="coral-count" data-coral-id="acce22c7-f27c-487c-80bb-5534afa78b82" data-coral-notext="true" data-coral-url="https://www.theverge.com/2024/4/12/24128584/spotify-music-pro-lossless-audio"></span></a></span></div></div></div></div>"""
    },
    {
        "role": "model",
        "content": """
        {
          "is_article": true,
          "title_selector": "h2 a",
          "link_selector": "h2 a",
          "date_selector": "time"
        }
        """
    },
    {
        "role": "user",
        "content": """<div class="af ag ot ou ov ow np ab"><a data-test="link" href="/tmr/wallstreet/2024-04-15/ty-article/.premium/0000018e-e2e5-de89-afbf-ffe59eb50000"><h3 class="jl as cc cg jm el ce ch jn cf jo af ag ot ou ov ow np ab">מינויו של ראש הממשלה הבא של סינגפור מסמן שינוי רחב יותר במדינה</h3></a></div>""",
    },
    {
        "role": "model",
        "content": """
        {
          "is_article": true,
          "title_selector": "h3",
          "link_selector": "a",
          "date_selector": null
        }
        """
    },
    {
        "role": "user",
        "content": """<div class="flexcss w12 displayflex bb2_solid borderColorwhite-5 pb3"><div class="flexrsc displayflex"><a class="colorwhite mr3 bgorange-light radiimedium px2 py1 fontWeightbold displaynone fontSize10" data-google-interstitial="false" data-link="go-premium" href="https://lp.tipranks.com/go-pro-v2?llf=paid-only-article&amp;custom18=news" title="Upgrade to Premium to unlock this investment idea"><span>Premium</span></a><span class="fontSize8 fontWeightnormal colorgray-2 alignstart mt2 mb1 ipadpro_fontSize10 ipadpro_mb0 laptop_fontSize10">Market News</span></div><a href="/news/lawmakers-consider-merging-safer-banking-act-with-crypto-regulation"><span class="fontSize7small fontWeightsemibold truncate2 lineHeight3 h_pxsmall60 overflowhidden pb4 w11 maxWparent ipad_fontSize7 ipad_h_pxsmall35" title="Lawmakers Consider Merging SAFER Banking Act with Crypto Regulation">Lawmakers Consider Merging SAFER Banking Act with Crypto Regulation</span></a></div>""",
    },
    {
        "role": "model",
        "content": """
        {
          "is_article": true,
          "title_selector": "a[href="/news/lawmakers-consider-merging-safer-banking-act-with-crypto-regulation"] span",
          "link_selector": "a[href="/news/lawmakers-consider-merging-safer-banking-act-with-crypto-regulation"]",
          "date_selector": null
        }
        """
    }
]

element = """<div class="relative z-10 inline-block pt-4 font-polysans text-11 uppercase leading-140 tracking-15 text-gray-31 dark:text-gray-bd"><div class="inline-block"><a class="text-gray-31 hover:shadow-underline-inherit dark:text-franklin mr-8" href="/authors/chris-welch">Chris Welch</a></div><div class="inline-block text-gray-63 dark:text-gray-94"><time datetime="2024-04-12T18:25:02.352Z">Apr 12</time><span class="hide-coral-new-count byline-comment-count"><span class="mx-8">|</span><a aria-label="Spotify’s lossless audio could finally arrive as part of ‘Music Pro’ add-on" class="group hover:text-white" href="/2024/4/12/24128584/spotify-music-pro-lossless-audio?showComments=1"><span class="coral-count" data-coral-id="acce22c7-f27c-487c-80bb-5534afa78b82" data-coral-notext="true" data-coral-url="https://www.theverge.com/2024/4/12/24128584/spotify-music-pro-lossless-audio"></span></a></span></div></div>"""
element1 = """<div class="basic-card__body__1c4ca"><header class="header"><a class="text__text__1FZLe text__inherit-color__3208F text__inherit-font__1Y8w3 text__inherit-size__1DZJi link__link__3Ji6W link__underline_on_hover__2zGL4 title__link__1zUJP basic-card__title__3byru" data-testid="Link" href="/world/us/palestinian-americans-fundraise-gaza-aid-groups-receive-record-donations-2023-10-31/"><span class="text__text__1FZLe text__dark-grey__3Ml43 text__medium__1kbOh text__heading_6__1qUJ5 heading__base__2T28j heading__heading_6__RtD9P" data-testid="Heading">Palestinian Americans fundraise for Gaza, as aid groups receive record donations</span></a></header><time class="text__text__1FZLe text__medium-grey__3A_RT text__light__1nZjX text__ultra_small__37j9j date-line__time__1VR1r basic-card__time__316Dt" data-testid="Text" datetime="2024-04-15T02:06:24Z">2 min ago</time></div>"""
element1 = """<div class="media-story-card__body__3tRWy"><span class="text__text__1FZLe text__dark-grey__3Ml43 text__light__1nZjX text__extra_small__1Mw6v label__label__f9Hew label__kicker__RW9aE media-story-card__section__SyzYF" data-testid="Label"><a class="text__text__1FZLe text__inherit-color__3208F text__inherit-font__1Y8w3 text__inherit-size__1DZJi link__link__3Ji6W link__underline_on_hover__2zGL4" data-testid="Link" href="/business/">Business<span style="border: 0px; clip: rect(0px, 0px, 0px, 0px); clip-path: inset(50%); height: 1px; margin: -1px; overflow: hidden; padding: 0px; position: absolute; width: 1px; white-space: nowrap;">category</span></a></span><a class="text__text__1FZLe text__dark-grey__3Ml43 text__medium__1kbOh text__heading_6__1qUJ5 heading__base__2T28j heading__heading_6__RtD9P media-story-card__headline__tFMEu" data-testid="Heading" href="/business/china-vanke-says-it-faces-short-term-liquidity-pressure-2024-04-15/">China Vanke says it faces short-term liquidity pressure</a><time class="text__text__1FZLe text__inherit-color__3208F text__regular__2N1Xr text__extra_small__1Mw6v label__label__f9Hew label__small__274ei" data-testid="Label" datetime="2024-04-15T01:36:58Z">4:36 AM GMT+3 · Updated an hour ago</time></div>"""
element1 = """<ul class="nav-dropdown__sections-group__37b4Y"><li><a class="text__text__1FZLe text__medium-grey__3A_RT text__regular__2N1Xr text__small__1kGq2 body__base__22dCE body__small_body__2vQyf nav-dropdown__subsection-link__2DOwM" data-subnav="World_Africa" data-testid="Body" href="/world/africa/">Africa</a></li><li><a class="text__text__1FZLe text__medium-grey__3A_RT text__regular__2N1Xr text__small__1kGq2 body__base__22dCE body__small_body__2vQyf nav-dropdown__subsection-link__2DOwM" data-subnav="World_Americas" data-testid="Body" href="/world/americas/">Americas</a></li><li><a class="text__text__1FZLe text__medium-grey__3A_RT text__regular__2N1Xr text__small__1kGq2 body__base__22dCE body__small_body__2vQyf nav-dropdown__subsection-link__2DOwM" data-subnav="World_Asia Pacific" data-testid="Body" href="/world/asia-pacific/">Asia Pacific</a></li><li><a class="text__text__1FZLe text__medium-grey__3A_RT text__regular__2N1Xr text__small__1kGq2 body__base__22dCE body__small_body__2vQyf nav-dropdown__subsection-link__2DOwM" data-subnav="World_China" data-testid="Body" href="/world/china/">China</a></li><li><a class="text__text__1FZLe text__medium-grey__3A_RT text__regular__2N1Xr text__small__1kGq2 body__base__22dCE body__small_body__2vQyf nav-dropdown__subsection-link__2DOwM" data-subnav="World_Europe" data-testid="Body" href="/world/europe/">Europe</a></li><li><a class="text__text__1FZLe text__medium-grey__3A_RT text__regular__2N1Xr text__small__1kGq2 body__base__22dCE body__small_body__2vQyf nav-dropdown__subsection-link__2DOwM" data-subnav="World_India" data-testid="Body" href="/world/india/">India</a></li><li><a class="text__text__1FZLe text__medium-grey__3A_RT text__regular__2N1Xr text__small__1kGq2 body__base__22dCE body__small_body__2vQyf nav-dropdown__subsection-link__2DOwM" data-subnav="World_Israel and Hamas at War" data-testid="Body" href="/world/israel-hamas/">Israel and Hamas at War</a></li></ul>"""
element1 = """<div class="flexc__ w12 px3 displayflex mb3 h_pxmedium"><a class="w12" href="/news/tesla-nasdaqtsla-lays-off-employees-amid-slowing-ev-sales"></a><div class="flexrsc mt2 displayflex"><a class="w12" href="/news/tesla-nasdaqtsla-lays-off-employees-amid-slowing-ev-sales"></a><a class="colorwhite mr3 bgorange-light radiimedium px2 py1 fontWeightbold displaynone fontSize10" data-google-interstitial="false" data-link="go-premium" href="https://lp.tipranks.com/go-pro-v2?llf=paid-only-article&amp;custom18=news" title="Upgrade to Premium to unlock this investment idea"><span>Premium</span></a><span class="fontSize8 fontWeightnormal colorgray-2 mt3 mb1 ipadpro_mb0 laptop_fontSize10">Market News</span></div><span class="fontSize7small fontWeightsemibold truncate2 laptop_h_pxauto">Tesla (NASDAQ:TSLA) Lays Off Employees amid Slowing EV Sales</span></div>"""


def extract_articles_selectors(html_element):
    # returns a dictionary with selections or empty dictionary
    response_text = ask_llm(article_preview_selectors_chat, html_element, model_name="gemini")

    try:
        json_string = response_text[response_text.find("{"):response_text.rfind("}") + 1]
        output = json.loads(json_string)
        return output

    except json.JSONDecodeError as e:

        logger.error(f"Failed parsing ai json response: {response_text}, error: {e}")

    return {}


def save_element_tree_map_to_cache(base_url, tree, map):
    filename = f"./storage/article_preview_map/{url_to_filename(base_url)}.json"
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
    filename = f"./storage/article_preview_map/{url_to_filename(base_url)}.json"
    try:
        with open(filename, "r") as f:
            js = json.load(f)
            return js.get(tree)
    except FileNotFoundError:
        return None


def process_article_preview_element(base_url, element_text, caching=True):
    element_tree = extract_tag_tree(element_text)

    if caching:
        cache = load_element_tree_map_from_cache(base_url, element_tree)
        if cache:
            return cache

    logger.debug(f"Processing article preview element: {element_tree} from {base_url}")
    element_soup = BeautifulSoup(element_text, "html.parser")
    output = extract_articles_selectors(element_text)

    if not output or not output.get("is_article"):
        indexer = {"is_article": False}
        save_element_tree_map_to_cache(base_url, element_tree, indexer)
        return indexer

    logger.debug(f"Extracted article preview selectors: {output}")

    title_css = output.get("title_selector")
    link_css = output.get("link_selector")
    date_css = output.get("date_selector")

    title_elements = element_soup.select(title_css) if title_css else None
    link_elements = element_soup.select(link_css) if link_css else None
    date_elements = element_soup.select(date_css) if date_css else None

    title_element = title_elements[0] if title_elements else None
    link_element = link_elements[0] if link_elements else None
    date_element = date_elements[0] if date_elements else None

    title_tree = get_parents(title_element) if title_element else None
    link_tree = get_parents(link_element) if link_element else None
    date_tree = get_parents(date_element) if date_element else None

    title_text = title_element.text if title_element else None
    link_text = link_element['href'] if link_element else None
    date_text = date_element.text if date_element else None

    title_text_by_tree = find_by_parents(element_text, title_tree)[0].text if title_tree else None
    link_text_by_tree = find_by_parents(element_text, link_tree)[0]['href'] if link_tree else None
    date_text_by_tree = find_by_parents(element_text, date_tree)[0].text if date_tree else None

    if title_text != title_text_by_tree:
        logger.warning(f"Title text mismatch: {title_text} != {title_text_by_tree} for {element_tree} from {base_url}")
        input()

    if link_text != link_text_by_tree:
        logger.warning(f"Link text mismatch: {link_text} != {link_text_by_tree} for {element_tree} from {base_url}")
        input()

    article_map = {
        "is_article": True,
        "element_tree": element_tree,
        "title": title_text_by_tree,
        "title_css": title_css,
        "title_parents_tree": title_tree,
        "link": link_text_by_tree,
        "link_css": link_css,
        "link_parents_tree": link_tree,
        "date": date_text_by_tree,
        "date_css": date_css,
        "date_parents_tree": date_tree
    }
    save_element_tree_map_to_cache(base_url, element_tree, article_map)
    return article_map


def test_process_article_preview_element():
    res = process_article_preview_element("http://www.theverge.com", element1)
    logger.info(res)

# test_process_article_preview_element()
