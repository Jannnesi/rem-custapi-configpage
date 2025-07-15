import logging

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    abort,
    jsonify
)
from werkzeug.exceptions import NotFound
from ..customers.services import list_configs

logger = logging.getLogger(__name__)

from . import bp

@bp.route("/", methods=["GET"])
def index():
    """
    Show manual run page.
    """
    customers = list_configs()
    return render_template("run.html", customers=customers)