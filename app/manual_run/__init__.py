from flask import Blueprint

bp = Blueprint(
    "manual_run",
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix="/manual_run",
)

# Import routes so they attach to `bp` *after* it is created.
from . import routes             # noqa: E402  pylint: disable=wrong-import-position


def init_app(app):
    app.register_blueprint(bp)