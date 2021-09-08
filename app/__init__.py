import os
from pathlib import Path
from typing import Any

from flask import Flask, send_from_directory, render_template, Response
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_mongoengine import MongoEngine

from app.mongo_id_converter import ObjectIdConverter
from product import create_update_view
from user import view
from user.model import User


def create_app(test_config: dict[str, Any] = None) -> Flask:
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True, template_folder='templates')
    app.config.from_mapping(
        SECRET_KEY='dev',
        UPLOAD_FOLDER=Path(app.instance_path) / 'images',
    )
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.config['DEBUG_TB_PANELS'] = ['flask_mongoengine.panels.MongoDebugPanel']
    app.config['DEBUG_TB_ENABLED'] = True

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py')
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    ObjectIdConverter.register_in_flask(app)
    MongoEngine(app)
    DebugToolbarExtension(app)

    @app.route('/uploads/<path:filename>')
    def download_file(filename: str) -> Response:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

    @app.route('/not_found')
    def not_found() -> tuple[str, int]:
        return render_template('404.html'), 404

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.user_loader(User.load_user)
    login_manager.login_view = "user.login"

    app.register_blueprint(create_update_view.bp)
    app.register_blueprint(view.bp)

    return app
