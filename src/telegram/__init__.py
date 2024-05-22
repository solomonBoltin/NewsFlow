import asyncio
import os

from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('TELEGRAM_BOT_TOKEN')
article_preview_channel = os.getenv('TELEGRAM_ARTICLE_PREVIEW_CHANNEL')


def message_builder(article_preview):
    return f"{article_preview.title}\n{article_preview.link}\n{article_preview.date}\n{article_preview.website_url}"


async def publish_article_preview(article_preview):
    bot = Bot(token=token)

    try:
        await bot.send_message(article_preview_channel, message_builder(article_preview))

    except TelegramRetryAfter as e:
        await asyncio.sleep(e.retry_after)
        await publish_article_preview(article_preview)
