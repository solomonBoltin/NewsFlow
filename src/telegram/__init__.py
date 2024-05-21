import asyncio

from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter

token = '6807220259:AAHXS357FF3h6LwR2xlaB4QwF1RrwfX75qA'
article_preview_channel = '-1002133110831'


def message_builder(article_preview):
    return f"{article_preview.title}\n{article_preview.link}\n{article_preview.date}\n{article_preview.website_url}"


async def publish_article_preview(article_preview):
    bot = Bot(token=token)

    try:
        await bot.send_message(article_preview_channel, message_builder(article_preview))

    except TelegramRetryAfter as e:
        await asyncio.sleep(e.retry_after)
        await publish_article_preview(article_preview)


