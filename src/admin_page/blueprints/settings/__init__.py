from flask import Blueprint

settings_bp = Blueprint(
    "settings",
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix="/settings",
)

from . import routes  # noqa: F401, E402


def init_app(app):
    app.register_blueprint(settings_bp)
