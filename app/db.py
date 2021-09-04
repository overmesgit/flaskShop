import pymongo
from flask import g, current_app
from pymongo.server_api import ServerApi


def get_db():
    if 'db' not in g:
        g.db = pymongo.MongoClient(
            current_app.config['DB'],
            server_api=ServerApi('1'))
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)
