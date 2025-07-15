from flask import Blueprint
import logging

bp = Blueprint(
    "api",
    __name__,
    url_prefix="/api",
)
logger = logging.getLogger(__name__)
@bp.route("/customer_configs", methods=["GET"])
def get_customers():
    """
    Get a list of customers.
    """
    from app.customers.services import list_configs
    return list_configs(as_dict=True)

@bp.route("/settings", methods=["GET"])
def get_settings():
    """
    Get general settings.
    """
    from app.settings.services import load_settings, get_base_columns
    settings = load_settings(as_dict=True)
    settings["base_columns"] = get_base_columns()
    return settings

def init_app(app):
    """
    Initialize the API blueprint and register it with the Flask app.
    """
    app.register_blueprint(bp)
