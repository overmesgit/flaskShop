from typing import Any

from flask import Flask
from flask_mongoengine import MongoEngine

from product import views


def create_app(test_config: dict[str, Any] = None) -> Flask:
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True, template_folder='templates')
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py')
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    MongoEngine(app)

    @app.route('/')
    def hello_world() -> str:
        return 'Hello World!'

    app.register_blueprint(views.bp)

    return app
