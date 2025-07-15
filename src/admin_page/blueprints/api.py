import logging

from flask import Blueprint

from .customers.services import list_configs
from .settings.services import get_base_columns, load_settings

api_bp = Blueprint(
    "api",
    __name__,
    url_prefix="/api",
)
logger = logging.getLogger(__name__)


@api_bp.route("/customer_configs", methods=["GET"])
def get_customers():
    """
    Get a list of customers.
    """

    return list_configs(as_dict=True)


@api_bp.route("/settings", methods=["GET"])
def get_settings():
    """
    Get general settings.
    """

    settings = load_settings(as_dict=True)
    settings["base_columns"] = get_base_columns()
    return settings


def init_app(app):
    """
    Initialize the API blueprint and register it with the Flask app.
    """
    app.register_blueprint(api_bp)
