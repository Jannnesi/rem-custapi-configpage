# app/models/base_column_model.py
from __future__ import annotations

from typing import Optional

from sqlalchemy import Integer, String, select, func
from sqlalchemy.orm import Mapped, mapped_column, validates, object_session

from app.models import Base           # your shared DeclarativeBase

class BaseColumn(Base):
    __tablename__ = "base_columns"

    # ── columns ──────────────────────────────────────────────────────────
    id:        Mapped[int]              = mapped_column(primary_key=True, autoincrement=True)
    key:       Mapped[str]              = mapped_column(String(100),  unique=True, nullable=False)
    name:      Mapped[str]              = mapped_column(String(255),  nullable=False)
    dtype:     Mapped[str]              = mapped_column(String(20),   nullable=False)      # "string" | "float" | "int"
    length:    Mapped[Optional[int]]    = mapped_column(Integer,      nullable=True)
    decimals:  Mapped[Optional[int]]    = mapped_column(Integer,      nullable=True)
    order:     Mapped[int]              = mapped_column(Integer,      nullable=False, unique=True, index=True)

    # ── auto-assign next order value if None ─────────────────────────────
    @validates("order")
    def _validate_or_autofill(self, _key: str, value: Optional[int]) -> int:
        if value is None:
            sess = object_session(self)
            if sess is None:
                raise RuntimeError("Object must be attached to a Session before 'order' can be auto-filled")

            max_ord: int = sess.scalar(
                select(func.coalesce(func.max(BaseColumn.order), 0))
            ) or 0
            return max_ord + 1
        return value

    # ── debug representation ────────────────────────────────────────────
    def __repr__(self) -> str:
        return f"<BaseColumn {self.order:02d} {self.key} ({self.dtype})>"
