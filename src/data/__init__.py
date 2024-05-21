from peewee import SqliteDatabase, Model


db = SqliteDatabase('./storage/db.sqlite')


# Define the base model
class BaseModel(Model):
    class Meta:
        database = db

