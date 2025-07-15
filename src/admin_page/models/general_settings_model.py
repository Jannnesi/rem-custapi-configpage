# app/models/general_settings_model.py

from email_model import EmailModel
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class GeneralSettings(Base):
    __tablename__ = "general_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    retry_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    retry_delay: Mapped[int] = mapped_column(Integer, nullable=False, default=5)

    emails: Mapped[list["EmailModel"]] = relationship(  # type: ignore[valid-type]
        "EmailModel",
        back_populates="settings",
        cascade="all, delete-orphan",
    )
