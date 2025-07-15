# tests/conftest.py
import pytest
from admin_page import create_app
from admin_page.config import Dev
from admin_page.extensions import db


@pytest.fixture
def app(tmp_path):
    Dev.SQLALCHEMY_DATABASE_URI = f"sqlite:///{tmp_path/'test.db'}"
    app = create_app(Dev)
    with app.app_context():
        db.create_all()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()
