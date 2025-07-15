# app/models/config_model.py
from __future__ import annotations

from sqlalchemy import JSON, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from admin_page.models import Base  # your shared DeclarativeBase


class Customer(Base):
    __tablename__ = "customer_configs"

    # ── columns ──────────────────────────────────────────────────────────
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # stored as JSON array (list) but used as a set in Python code
    konserni: Mapped[list[int]] = mapped_column(JSON, nullable=False, default=list)

    source_container: Mapped[str] = mapped_column(String(100), nullable=False)
    destination_container: Mapped[str] = mapped_column(String(100), nullable=False)

    file_format: Mapped[str] = mapped_column(String(50), nullable=False)
    file_encoding: Mapped[str] = mapped_column(String(50), nullable=False)

    # Optional[Dict[str, Dict[str, str]]]
    extra_columns: Mapped[dict[str, dict[str, str]] | None] = mapped_column(JSON, nullable=True)

    # Optional[List[str]]
    exclude_columns: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # ── representation ───────────────────────────────────────────────────
    def __repr__(self) -> str:
        return (
            f"<CustomerConfig(name={self.name!r}, enabled={self.enabled}, "
            f"containers=({self.source_container!r}→{self.destination_container!r}))>"
        )
