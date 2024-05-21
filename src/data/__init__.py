from peewee import SqliteDatabase, Model

from src.utils import storage_path

db = SqliteDatabase(f'./{storage_path()}/db.sqlite')


# Define the base model
class BaseModel(Model):
    class Meta:
        database = db

