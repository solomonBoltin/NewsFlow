from src.data.article_prview import ArticlePreview


def get_article_preview_by_link(link: str) -> ArticlePreview:
    return ArticlePreview.get_or_none(ArticlePreview.link == link)


def save_article_preview(article_preview: ArticlePreview) -> bool:
    if get_article_preview_by_link(article_preview.link):
        return False
    article_preview.save()
    return True
