import os
import tempfile
from contextlib import contextmanager

import mongomock
import pytest
from flask import template_rendered

from app import create_app


@mongomock.patch()
@pytest.fixture
def app():
    with tempfile.TemporaryDirectory() as tmpdir:

        app = create_app({
            'TESTING': True,
            'MONGODB_SETTINGS': {'host': 'mongomock://localhost'},
            'UPLOAD_FOLDER': tmpdir,
        })

        yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)
