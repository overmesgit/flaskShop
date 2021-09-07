from functools import wraps
from typing import Any

from flask import url_for
from mongoengine import DoesNotExist
from werkzeug import Response
from werkzeug.utils import redirect


def redirect_to_404_if_not_found(f: Any) -> Any:
    @wraps(f)
    def decorated_function(*args: list[str], **kwargs: dict[str, Any]) -> Any:
        try:
            return f(*args, **kwargs)
        except DoesNotExist:
            return redirect(url_for('not_found'))

    return decorated_function
