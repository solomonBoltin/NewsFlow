from src.data import db
from src.data.article_prview import ArticlePreview

data_models = [ArticlePreview]


def setup_database():
    db.create_tables(data_models)
