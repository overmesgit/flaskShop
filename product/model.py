from flask_mongoengine import Document
from mongoengine import StringField, ListField, DecimalField
from wtforms import validators

class Product(Document):
    title = StringField(max_length=120, required=True)
    images = ListField(
        StringField(max_length=256, required=True))
    description = StringField(max_length=500, required=True)
    price = DecimalField(min_value=0, required=True)
    categories = ListField(StringField())
