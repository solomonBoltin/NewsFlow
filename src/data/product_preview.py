from dataclasses import dataclass

from peewee import *

from src.data import db, BaseModel


# Define the ProductPreview model extending the base model
class ProductPreview(BaseModel):
    title: str = CharField()
    link: str = CharField(unique=True)
    price: str = CharField(null=True)
    image: str = CharField(null=True)
    website_url: str = CharField()
    by_tag_tree: str = CharField(null=True)
    scrape_datetime: str = CharField(null=True)
    html_text: str = TextField(null=True)

    def __str__(self):
        return f'{self.title} - {self.price} - {self.link} - {self.website_url}'

    class Meta:
        table_name = 'product_preview'


def test_product_preview():
    # Create a new product preview
    ProductPreview(
        title='New Product',
        link='https://www.example.com/product1',
        price='$19.99',
        image='https://www.example.com/images/product1.jpg',
        website_url='https://www.example.com')

    res = ProductPreview.create(
        title='New Product 2',
        link='https://www.example.com/product2',
        price='$29.99',
        image='https://www.example.com/images/product2.jpg',
        website_url='https://www.example.com')

    print(res)
    # Retrieve the product preview by link
    pp = ProductPreview.get_or_none(ProductPreview.link == 'https://www.example.com/product2')
    print(pp)
    input()

    # Update the product preview
    pp.price = '$24.99'
    pp.save()

    # Delete the product preview
    # pp.delete_instance()

    # Close the database connection
    db.close()

# test_product_preview()
