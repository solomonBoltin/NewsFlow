import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

websites = [
    "https://www.bloomberg.com/",  #robot detection
    "https://pharmatimes.com/",
    "https://edition.cnn.com/",
    "https://www.business-standard.com/",
    "https://www.itnonline.com/",
    "https://www.nytimes.com/",
    "https://www.smh.com.au/",
    "https://www.globes.co.il/en/",
    "https://www.calcalist.co.il/",
    "https://www.theverge.com/",
    "https://www.timesofisrael.com/",
    "https://www.reuters.com/",  #robot detection
]


async def main():
    async with async_playwright() as p:
        for website in websites:
            for browser_type in [p.webkit, p.chromium, p.firefox]:
                try:
                    print(f"Testing {browser_type.name}")
                    browser = await browser_type.launch()
                    page = await browser.new_page()
                    await stealth_async(page)
                    await page.goto(website)
                    filesafe_website = website.replace("/", "-").replace(":", "-").replace(".", "-")
                    await page.screenshot(path=f'{filesafe_website}-{browser_type.name}.png')
                    await browser.close()
                except Exception as e:
                    print(f"Error: {e}")
                    continue


asyncio.run(main())
