import logging

from flask import render_template

from ..auth import login_required
from ..customers.services import list_configs
from . import manual_run_bp

logger = logging.getLogger(__name__)


@manual_run_bp.route("/", methods=["GET"])
@login_required
def index():
    """
    Show manual run page.
    """
    customers = list_configs()
    return render_template("run.html", customers=customers)
