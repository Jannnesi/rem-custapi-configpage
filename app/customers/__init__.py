"""
Customers blueprint

Defines:
    bp  – the Blueprint object
    init_app(app) – optional helper that registers the blueprint
"""

from flask import Blueprint

bp = Blueprint(
    "customers",
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix="/customers",
)


# Import routes so they attach to `bp` *after* it is created.
from . import routes             # noqa: E402  pylint: disable=wrong-import-position


def init_app(app):
    app.register_blueprint(bp)
