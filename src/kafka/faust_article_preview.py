from dataclasses import dataclass
from typing import Optional

import faust

from src.data.article_prview import ArticlePreview


@dataclass
class FaustArticlePreview(faust.Record):
    title: str
    link: str
    date: Optional[str]
    website_url: str
    by_tag_tree: Optional[str]

    @staticmethod
    def from_peewee(model: ArticlePreview):
        return FaustArticlePreview(
            title=model.title,
            link=model.link,
            date=model.date,
            website_url=model.website_url,
            by_tag_tree=model.by_tag_tree
        )

    def to_peewee(self):
        return ArticlePreview(
            title=self.title,
            link=self.link,
            date=self.date,
            website_url=self.website_url,
            by_tag_tree=self.by_tag_tree
        )
