from typing import Any

import bson
from flask import Flask
from werkzeug.exceptions import BadRequest
from werkzeug.routing import BaseConverter


class ObjectIdConverter(BaseConverter):

    def to_python(self, value: str) -> bson.ObjectId:
        try:
            return bson.ObjectId(value)
        except bson.errors.InvalidId as e:
            raise BadRequest(str(e))

    def to_url(self, value: Any) -> str:
        return str(value)

    @classmethod
    def register_in_flask(cls, flask_app: Flask) -> None:
        flask_app.url_map.converters['id'] = cls
