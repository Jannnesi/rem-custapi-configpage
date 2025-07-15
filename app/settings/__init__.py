from flask import Blueprint

bp = Blueprint(
    "settings",
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix="/settings",
)

from . import routes  # noqa: E402  pylint: disable=wrong-import-position

def init_app(app):
    app.register_blueprint(bp)