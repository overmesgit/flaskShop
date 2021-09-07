import os
from pathlib import Path
from typing import Any

from flask import Flask, send_from_directory, render_template, Response
from flask_mongoengine import MongoEngine

import product.product_bp
from app.mongo_id_converter import ObjectIdConverter
from product import views, create_update_view, product_bp


def create_app(test_config: dict[str, Any] = None) -> Flask:
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True, template_folder='templates')
    app.config.from_mapping(
        SECRET_KEY='dev',
        UPLOAD_FOLDER=Path(app.instance_path) / 'images',
    )
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py')
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    ObjectIdConverter.register_in_flask(app)
    MongoEngine(app)

    @app.route('/uploads/<path:filename>')
    def download_file(filename: str) -> Response:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

    @app.route('/not_found')
    def not_found() -> tuple[str, int]:
        return render_template('404.html'), 404

    app.register_blueprint(create_update_view.bp)

    return app
