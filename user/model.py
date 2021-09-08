from flask_login import UserMixin
from flask_mongoengine import Document
from mongoengine import StringField, ListField, BooleanField
from werkzeug.security import check_password_hash, generate_password_hash


class User(Document, UserMixin):
    active = BooleanField(default=True)

    username = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    password_hash = StringField(required=True)

    roles = ListField(StringField(), default=[])

    def __init__(self, **kwargs):
        password_hash = kwargs.pop('password_hash', None)
        self.password = kwargs.pop('password', None)
        if self.password:
            password_hash = generate_password_hash(self.password)

        super().__init__(password_hash=password_hash, **kwargs)

    def save(self, **kwargs):
        return super().save(**kwargs)

    @property
    def is_authenticated(self):
        return False

    @property
    def is_active(self):
        return self.active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.email

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def load_user(cls, email):
        query = cls.objects(email=email)[:1]
        return query[0] if query else None
