from src.data.article_prview import ArticlePreview
from src.data.product_preview import ProductPreview


def get_article_preview_by_link(link: str) -> ArticlePreview:
    return ArticlePreview.get_or_none(ArticlePreview.link == link)


def save_article_preview(article_preview: ArticlePreview) -> bool:
    if get_article_preview_by_link(article_preview.link):
        return False
    article_preview.save()
    return True


def get_product_preview_by_link(link: str) -> ProductPreview:
    return ProductPreview.get_or_none(ProductPreview.link == link)


def save_product_preview(product_preview: ProductPreview) -> bool:
    if get_product_preview_by_link(product_preview.link):
        return False
    product_preview.save()
    return True
