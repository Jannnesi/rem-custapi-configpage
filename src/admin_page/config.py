import os
from urllib.parse import quote_plus

basedir = os.path.abspath(os.path.dirname(__file__))


def _build_odbc():
    """
    Compose a single ODBC string from env-vars.
    Works for both local 'localhost,1433' and remote Azure SQL.
    """
    driver = os.getenv("SQL_DRIVER")
    server = os.getenv("SQL_SERVER")
    database = os.getenv("SQL_DATABASE")
    user = os.getenv("SQL_USERNAME")
    pwd = os.getenv("SQL_PASSWORD")
    encrypt = os.getenv("SQL_ENCRYPT")
    trust = os.getenv("SQL_TRUST_CERT")

    return (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={user};"
        f"PWD={pwd};"
        f"Encrypt={encrypt};"
        f"TrustServerCertificate={trust};"
        "Connection Timeout=30;"
    )


class Config:
    # Azure AD single-tenant
    AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
    AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
    AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
    AZURE_AUTHORITY = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}"
    AZURE_REDIRECT_PATH = "/auth/callback"
    AZURE_SCOPE = ["User.Read"]

    # Flask session
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

    # --- session storage ---
    SESSION_TYPE = "filesystem"  # or "redis", "memcached", etc.
    SESSION_FILE_THRESHOLD = 500  # keep a few hundred files then purge
    SESSION_FILE_DIR = "instance/sessions"  # customise as you like
    PERMANENT_SESSION_LIFETIME = 3600  # seconds

    # SQLAlchemy

    # Honour an explicit DATABASE_URI first, otherwise build one.
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URI", "mssql+pyodbc:///?odbc_connect=" + quote_plus(_build_odbc())
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Dev(Config):
    DEBUG = True


class Prod(Config):
    DEBUG = False
