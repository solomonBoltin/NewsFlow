from dataclasses import dataclass

from peewee import *

from src.data import db, BaseModel


# Define the ArticlePreview model extending the base model
class ArticlePreview(BaseModel):
    title: str = CharField()
    link: str = CharField(unique=True)
    date: str = DateField(null=True)
    website_url: str = CharField()
    by_tag_tree: str = CharField(null=True)

    def __str__(self):
        return f'{self.title} - {self.link} - {self.date} - {self.website_url}'

    class Meta:
        table_name = 'article_preview'


def test_article_preview():
    # Create a new article preview

    ArticlePreview(
        title='New title',
        link='https://www.calcalist.co.il/',
        date='2022-01-01',
        website_url='https://www.calcalist.co.il/')

    res = ArticlePreview.create(
        title='New title 2',
        link='https://www.calcalist.co.il/22eds',
        date='2022-01-01',
        website_url='https://www.calcalist.co.il/')

    print(res)
    # Retrieve the article preview by link
    ap = ArticlePreview.get_or_none(ArticlePreview.link == 'https://www.calcalist.co.il/22')
    print(ap)
    input()

    # Update the article preview
    ap.title = 'Updated title'
    ap.save()

    # Delete the article preview
    # ap.delete_instance()

    # Close the database connection
    db.close()

# test_article_preview()
