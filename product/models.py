from flask_mongoengine import Document
from mongoengine import StringField, ListField, DecimalField


class Product(Document):
    title = StringField(max_length=120, required=True)
    image = StringField(max_length=256, required=True)
    description = StringField(max_length=500, required=True)
    price = DecimalField(min_value=0, required=True)
    category = StringField(max_length=100, required=True)
