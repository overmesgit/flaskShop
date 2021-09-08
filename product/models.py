from flask_mongoengine import Document
from mongoengine import (
    StringField, DecimalField, EmbeddedDocumentListField, IntField,
    EmbeddedDocument,
)


class Review(EmbeddedDocument):
    score = IntField(StringField, required=True)
    review = StringField(max_length=200, required=True)


class Product(Document):
    title = StringField(max_length=120, required=True)
    image = StringField(max_length=256, required=True)
    description = StringField(max_length=500, required=True)
    price = DecimalField(min_value=0, required=True)
    category = StringField(max_length=100, required=True)
    reviews = EmbeddedDocumentListField(Review)
