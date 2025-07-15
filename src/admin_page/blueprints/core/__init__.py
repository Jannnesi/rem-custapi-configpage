from flask import Blueprint, render_template

from ..auth import login_required

core_bp = Blueprint(
    "main",
    __name__,
)


@core_bp.route("/", methods=["GET"])
@login_required
def index():
    """
    Main page of the application.
    """
    return render_template("index.html")


def init_app(app):
    app.register_blueprint(core_bp)
