from dotenv import load_dotenv
import os
import aiogram
import asyncio

load_dotenv()

GENAI_KEY = os.getenv("GENAI_KEY")
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_ARTICLE_PREVIEW_CHANNEL = os.getenv('TELEGRAM_ARTICLE_PREVIEW_CHANNEL')

# assert all values are set
assert GENAI_KEY, "GENAI_KEY environment variable is not set"
assert TELEGRAM_BOT_TOKEN, "TELEGRAM_BOT_TOKEN environment variable is not set"
assert TELEGRAM_ARTICLE_PREVIEW_CHANNEL, "TELEGRAM_ARTICLE_PREVIEW_CHANNEL environment variable is not set"

# # get all updates from bot and print them
#
# async def main():
#     bot = aiogram.Bot(token=TELEGRAM_BOT_TOKEN)
#     updates = await bot.get_updates()
#     print("Updates:")
#     for update in updates:
#         print(update.json())
#
#     input("Press Enter to continue...")
#     print("End of updates")
#     await bot.send_message("249080408", "Hello, world!")
#     await bot.delete_webhook()
#     await bot.close()
# # run the main function
# asyncio.run(main())
