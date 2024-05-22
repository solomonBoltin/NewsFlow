import asyncio
import os

from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_ARTICLE_PREVIEW_CHANNEL


def message_builder(article_preview):
    return f"{article_preview.title}\n{article_preview.link}\n{article_preview.date}\n{article_preview.website_url}"


async def publish_article_preview(article_preview):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    try:
        await bot.send_message(TELEGRAM_ARTICLE_PREVIEW_CHANNEL, message_builder(article_preview))

    except TelegramRetryAfter as e:
        await asyncio.sleep(e.retry_after)
        await publish_article_preview(article_preview)
