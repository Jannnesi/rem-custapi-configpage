from functools import wraps

from flask import Blueprint, redirect, session, url_for


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return wrapper


auth_bp = Blueprint("auth", __name__, template_folder="templates", static_folder="static")

from . import routes  # noqa: F401, E402


def init_app(app) -> None:
    """
    Initialize the auth blueprint and register it with the Flask app.
    """
    app.register_blueprint(auth_bp, url_prefix="/auth")
