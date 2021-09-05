import os
import tempfile

import mongomock
import pytest
from mongoengine import connect

from app import create_app


@mongomock.patch()
@pytest.fixture
def app():
    # connect('test', host='mongomock://localhost')
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'MONGODB_SETTINGS': {'host': 'mongomock://localhost'},
    })

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
