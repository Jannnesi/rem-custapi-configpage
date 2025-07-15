import logging

from flask import Flask

from admin_page.extensions import (
    csrf,
    db,
    fsession,
    migrate,
)

logging.basicConfig(
    level=logging.INFO,  # show INFO+ from the root
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
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

    from admin_page.blueprints import register_blueprints

    register_blueprints(app)

    # --- register CLI commands -------------
    from admin_page.cli import register_commands

    register_commands(app)
    logger.info("Flask app created and configured.")
    return app
