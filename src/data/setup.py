from src.data import db
from src.data.article_prview import ArticlePreview
from src.data.product_preview import ProductPreview

data_models = [ArticlePreview, ProductPreview]


def setup_database():
    db.create_tables(data_models)
