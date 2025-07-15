"""Azure SQL database handler for storing customer data."""

from __future__ import annotations

import logging
import os

from urllib import parse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from importlib import import_module
from app.models.general_settings_model import GeneralSettings
from app.models.email_model import EmailModel
from . import Base

logger = logging.getLogger(__name__)

class DatabaseHandler:
    """Singleton wrapper around an Azure SQL database."""

    _instance: "DatabaseHandler | None" = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        odbc_driver = "ODBC Driver 18 for SQL Server"
        server      = os.getenv("SQL_SERVER")
        database    = os.getenv("SQL_DATABASE")
        usr         = os.getenv("SQL_USERNAME")
        pwd         = os.getenv("SQL_PASSWORD")

        # 1) build your raw ODBC string (same as above)
        raw_conn_str = (
            f"DRIVER={{{odbc_driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={usr};PWD={pwd};"
            "Encrypt=yes;"
            "TrustServerCertificate=yes;"
            "Connection Timeout=30;"
        )

        # 2) quote it for a URL
        quoted = parse.quote_plus(raw_conn_str)

        # 3) hand it to SQLAlchemy
        try:
            self.engine = create_engine(f"mssql+pyodbc:///?odbc_connect={quoted}")
        except Exception as e:
            logger.error(f"Failed to create database engine: {e}")
            return
        # 1. make sure all model modules are imported so their tables are on Base
        import_module("app.models")

        # 2. create any tables that don’t yet exist
        # TODO: for prod alembic revision --autogenerate -m "add extra_columns"
        #Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

        logger.info("Tables now: %s", Base.metadata.tables.keys())
        
        # now you can do:
        with self.engine.connect() as conn:
            # wrap the SQL string in text()
            result = conn.execute(text("SELECT @@version;"))
            logger.info("\n%s", result.scalar())

        self._Session = scoped_session(
            sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
        )

        self._initialized = True

    @property
    def session(self):
        """Return a short-lived SQLAlchemy Session."""
        return self._Session()