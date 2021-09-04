from os import environ

from flask import Flask

from product import url


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        # DB=environ['DB'],
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    from . import db
    db.init_app(app)

    @app.route('/')
    def hello_world():
        return 'Hello World!'

    # @app.route('/db/')
    # def connect_to_db():
    #     db = client.test
    #     posts = db.posts
    #     post = {'counter': 1}
    #     post_id = posts.insert_one(post).inserted_id
    #     documents = posts.count_documents({})
    #     return f'Inserted {post_id=} {documents=}'

    app.register_blueprint(url.bp)

    return app
