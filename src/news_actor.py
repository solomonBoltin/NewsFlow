from apify import Actor

from src.database import save_article_preview
from src.utils import url_path_to_filename
import src.telegram as telegram


class NewsActor(Actor):

    @classmethod
    async def on_new_article_preview(cls, article_preview):
        cls.log.info(f"New article preview: {article_preview.title.replace('\n', '')}")
        await telegram.publish_article_preview(article_preview)

    @classmethod
    async def process_article_preview(cls, article_preview):
        is_new = save_article_preview(article_preview)
        if is_new:
            await cls.on_new_article_preview(article_preview)
