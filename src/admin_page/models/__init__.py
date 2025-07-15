from admin_page.extensions import db

Base = db.Model

from admin_page.models.base_column_model import BaseColumn  # noqa: E402, F401
from admin_page.models.customer_model import Customer  # noqa: E402, F401
from admin_page.models.email_model import EmailModel  # noqa: E402, F401
from admin_page.models.general_settings_model import GeneralSettings  # noqa: E402, F401
