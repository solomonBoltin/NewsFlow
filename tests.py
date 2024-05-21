from src.ask_llm import ask_ai_on_top_15_sections
from src.website_context.__init__ import load_website_context, scarp_website


def test_get_top_15():
    sections = ['https://www.calcalist.co.il/allnews', 'https://www.calcalist.co.il/buzz',
                'https://www.calcalist.co.il/market', 'https://www.calcalist.co.il/calcalistech',
                'https://www.calcalist.co.il/local_news', 'https://www.calcalist.co.il/real-estate',
                'https://www.calcalist.co.il/world_news', 'https://www.calcalist.co.il/local_news/category/3772',
                'https://www.calcalist.co.il/local_news/car',
                'https://www.calcalist.co.il/consumer/home/0,7340,L-3,00.html',
                'https://www.calcalist.co.il/supplement', 'https://www.calcalistech.com/ctechnews',
                'https://www.calcalist.co.il/local_news/category/5494',
                'https://www.calcalist.co.il/stock/category/3960', 'https://www.calcalist.co.il/stock/category/3959',
                'https://www.calcalist.co.il/tv', 'https://www.calcalist.co.il/investing',
                'https://www.calcalist.co.il/photo', 'https://www.calcalist.co.il/market/category/3874',
                'https://www.calcalist.co.il/stock/category/36062', 'https://www.calcalist.co.il/category/24188',
                'https://www.calcalist.co.il/category/34862', 'https://www.calcalist.co.il/local_news/category/3782',
                'https://www.calcalist.co.il/shopping/category/30862',
                'https://www.calcalist.co.il/stock/category/4135',
                'https://www.calcalist.co.il/local_news/category/3791', 'https://www.calcalist.co.il/category/5065',
                'https://www.calcalist.co.il/category/3717', 'https://www.calcalist.co.il/category/3847',
                'https://www.calcalist.co.il/podcast', 'https://www.calcalist.co.il/calcalistech/category/5783',
                'https://www.calcalist.co.il/calcalistech/category/3928',
                'https://www.calcalist.co.il/calcalistech/category/4799', 'https://www.calcalist.co.il/category/3837',
                'https://www.calcalist.co.il/calcalistech/category/5631', 'https://www.calcalist.co.il/category/33762',
                'https://www.calcalist.co.il/category/34582', 'https://www.calcalist.co.il/category/34742',
                'https://www.calcalist.co.il/local_news/category/35882', 'https://www.calcalist.co.il/category/35862',
                'https://www.calcalist.co.il/category/36622', 'https://www.calcalist.co.il/category/33122',
                'https://www.calcalist.co.il//www.calcalist.co.il/podcast',
                'https://www.calcalist.co.il//www.calcalist.co.il/tv', 'https://www.calcalist.co.il/tags/מלחמה_בעזה',
                'https://www.calcalist.co.il/tags/אוניברסיטת_קולומביה', 'https://www.calcalist.co.il/tags/קקאו',
                'https://www.calcalist.co.il/redmail', 'https://www.calcalist.co.il/home/0,7340,L-3673,00.html',
                'https://www.calcalist.co.il/podcast/category/36388',
                'https://www.calcalist.co.il/calcalistech/category/5203',
                'https://www.calcalist.co.il/local_news/category/3794',
                'https://www.calcalist.co.il/local_news/category/34462',
                'https://newmedia.calcalist.co.il/calcalist-special-projects/index.html',
                'https://100-2020.webflow.io/unicornes-2024',
                'https://newmedia.calcalist.co.il/calcalist-2023-netanyahu/index.html',
                'https://100-2020.webflow.io/calcalist-100-2023',
                'https://www.calcalist.co.il/calcalistech/category/36182', 'https://www.calcalist.co.il/style',
                'https://www.calcalist.co.il/home/0,7340,L-3839,00.html',
                'https://www.calcalist.co.il/home/0,7340,L-3802,00.html',
                'https://www.calcalist.co.il//www.calcalist.co.il/photo',
                'https://www.calcalist.co.il/stocks/home/0,7340,L-4135,00.html',
                'https://www.calcalist.co.il/home/0,7340,L-3854,00.html',
                'https://www.calcalist.co.il/home/0,7340,L-3801,00.html',
                'https://www.calcalist.co.il/home/0,7340,L-3856,00.html',
                'https://www.calcalist.co.il/home/0,7340,L-3855,00.html']

    top_15_sections = ask_ai_on_top_15_sections("https://www.calcalist.co.il/", sections, model_name="gemini")
    print("Top 15 sections:")
    for section in top_15_sections:
        print(section)




def test_context_and_get_articles(base_url, caching=True, ai_caching=True):
    # generate_website_context(base_url, caching, ai_caching=ai_caching)
    website_context = load_website_context(base_url)
    print(website_context)

    input("Press enter to scrap website")
    scarp_website(base_url, caching=caching)


# generate_website_context("https://www.calcalist.co.il/", caching=False, ai_caching=True)
scarp_website("https://www.calcalist.co.il/", caching=False)

# test_context_and_get_articles("https://www.calcalist.co.il/", caching=False, ai_caching=True)
