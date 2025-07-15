# function_app.py  –  Python v2
import azure.functions as func
from app import create_app

from admin_page.config import Dev

flask_app = create_app(Dev)

# 1. expose Flask through the dedicated v2 helper
app = func.WsgiFunctionApp(  # NOTE: WsgiFunctionApp, *not* FunctionApp
    app=flask_app.wsgi_app, http_auth_level=func.AuthLevel.ANONYMOUS
)
