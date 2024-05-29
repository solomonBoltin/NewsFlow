import asyncio
import time

from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

websites = [
    "https://www.whatismybrowser.com/",
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
            for browser_type in [p.chromium]:
                try:
                    print(f"Testing {browser_type.name} {website}")
                    if browser_type.name == "chromium":
                        browser = await browser_type.launch(headless=True, executable_path="C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe")
                    else:
                        browser = await browser_type.launch()

                    context = await browser.new_context()
                    page = await context.new_page()

                    await stealth_async(page)#, config={"user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"})
                    await page.goto(website)
                    filesafe_website = website.replace("/", "-").replace(":", "-").replace(".", "-")
                    await page.screenshot(path=f'shots/{filesafe_website}-{browser_type.name}.png', full_page=True)
                    time.sleep(50)
                    await browser.close()
                except Exception as e:
                    print(f"Error: {e}")
                    continue


asyncio.run(main())
