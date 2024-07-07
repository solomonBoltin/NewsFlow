from apify import Actor

import src.telegram as telegram
from src.data.setup import setup_database
from src.database import save_product_preview

setup_database()


class ShopActor(Actor):

    @classmethod
    async def on_new_product_preview(cls, product_preview):
        title = product_preview.title.replace("\n", '')
        cls.log.info(f"New product preview: {title} - {product_preview.link}")
        await telegram.publish_product_preview(product_preview)

    @classmethod
    async def process_product_preview(cls, product_preview):
        is_new = save_product_preview(product_preview)
        if is_new:
            await cls.on_new_product_preview(product_preview)
