# src/admin_page/extensions.py
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()
csrf = CSRFProtect()
fsession = Session()
migrate = Migrate()
