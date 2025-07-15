# app/models/email_model.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models import Base

class EmailModel(Base):
    __tablename__ = "emails"

    id           = Column(Integer, primary_key=True)
    settings_id  = Column(Integer, ForeignKey("general_settings.id", ondelete="CASCADE"))
    address      = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=False)

    settings = relationship("GeneralSettings", back_populates="emails")

    def __repr__(self):
        return f"<Email {self.address} ({self.display_name})>"
