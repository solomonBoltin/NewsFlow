
from peewee_migrate import Router
from peewee import SqliteDatabase, CharField

from src.data import db
from src.data.article_prview import ArticlePreview

router = Router(db)

# Create migration
router.create('scraper_datetime')
router.migrator.add_fields(ArticlePreview, scrape_datetime=CharField(null=True))

# Run migration/migrations
router.run('scraper_datetime')

# Run all unapplied migrations
router.run()
