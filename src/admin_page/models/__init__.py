from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

metadata = MetaData(schema="config")
Base = declarative_base()

from .base_column_model import BaseColumn  # noqa: E402, F401
from .customer_model import Customer  # noqa: E402, F401
from .email_model import EmailModel  # noqa: E402, F401
from .general_settings_model import GeneralSettings  # noqa: E402, F401
