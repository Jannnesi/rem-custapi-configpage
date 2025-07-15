from flask import Blueprint

manual_run_bp = Blueprint(
    "manual_run",
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix="/manual_run",
)

# Import routes so they attach to `bp` *after* it is created.
from . import routes  # noqa: F401, E402


def init_app(app):
    app.register_blueprint(manual_run_bp)
