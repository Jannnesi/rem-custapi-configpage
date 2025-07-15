from flask import Blueprint, render_template

  
bp = Blueprint(
    "main",
    __name__,
)


@bp.route("/", methods=["GET"])
def index():
    """
    Main page of the application.
    """
    return render_template("index.html")

def init_app(app):
    app.register_blueprint(bp)