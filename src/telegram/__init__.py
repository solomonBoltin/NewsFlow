import asyncio
import logging
import os

from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_ARTICLE_PREVIEW_CHANNEL
from src.data.article_prview import ArticlePreview

logger = logging.getLogger('actor').getChild("telegram")


def message_builder(article_preview: ArticlePreview):
    return (f"{article_preview.title}\n{article_preview.link}"
            f"\n{article_preview.date}"
            f"\n{article_preview.scrape_datetime}"
            f"\n{article_preview.website_url}")


async def publish_article_preview(article_preview):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    try:
        await bot.send_message(TELEGRAM_ARTICLE_PREVIEW_CHANNEL, message_builder(article_preview))

    except TelegramRetryAfter as e:
        logger.warning(f"Telegram API rate limit exceeded, retrying in {e.retry_after} seconds")
        await asyncio.sleep(e.retry_after)
        await publish_article_preview(article_preview)
