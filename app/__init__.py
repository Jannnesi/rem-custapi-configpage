
import logging
import os
from flask import Flask
from flask_wtf import CSRFProtect

def create_app() -> Flask:
    """
    Create and configure the Flask application.
    """
    logger = logging.getLogger(__name__)

    app = Flask(__name__)
    app.config.from_prefixed_env(prefix="APP")
    app.config["CLIENT_ID"] = "<GUID>"
    app.config["CLIENT_SECRET"] = "<secret>"
    app.config["AUTHORITY"] = "https://login.microsoftonline.com/<TenantID>"
    app.config["REDIRECT_PATH"] = "/auth/redirect"
    app.config["SCOPE"] = []  # (if any specific scopes needed, e.g., Graph API)
    app.config["SESSION_TYPE"] = "filesystem"  # or "filesystem" for dev, or use secure cookie

    csrf = CSRFProtect(app)
    csrf.init_app(app) 
       
    from .models.database_handler import DatabaseHandler
    DatabaseHandler()

    from .core import init_app as core_init
    core_init(app)
    
    from .customers import init_app as customers_init
    customers_init(app)
    
    from .settings import init_app as settings_init
    settings_init(app)
    
    from .manual_run import init_app as manual_run_init
    manual_run_init(app)

    from .api import init_app as api_init
    api_init(app)

    return app