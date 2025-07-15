import logging

from flask import Flask
from src.admin_page.cli import register_commands
from src.admin_page.extensions import (
    csrf,
    db,
    fsession,
    migrate,
)


def create_app(config_object) -> Flask:
    """
    Create and configure the Flask application.
    """
    logger = logging.getLogger(__name__)

    app = Flask(__name__, static_folder="assets")  # global static
    app.config.from_object(config_object)

    # --- init extensions -------------------
    db.init_app(app)
    csrf.init_app(app)
    fsession.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all()

    from src.admin_page.blueprints import register_blueprints

    register_blueprints(app)

    # --- register CLI commands -------------
    register_commands(app)
    logger.info("Flask app created and configured.")
    return app
