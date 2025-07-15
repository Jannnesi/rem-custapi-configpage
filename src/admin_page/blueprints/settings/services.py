# app/base_columns/services.py
from collections import OrderedDict
from typing import Any

from sqlalchemy.orm import Session, joinedload

from admin_page.extensions import db as database
from admin_page.models.base_column_model import BaseColumn
from admin_page.models.email_model import EmailModel
from admin_page.models.general_settings_model import GeneralSettings


def get_base_columns(*, as_ordered=True, as_rows=False):
    """
    Return {"key": {...}, ...} in the precise `order` you set.
    """
    db: Session = database.session

    rows = db.query(BaseColumn).order_by(BaseColumn.order).all()
    if as_rows:
        return rows
    if as_ordered:
        out = OrderedDict()
    else:
        out = {}
    for r in rows:
        out[r.key] = {"name": r.name, "dtype": r.dtype, "length": r.length, "decimals": r.decimals}
    return out


def reorder_base_columns(new_order: list[int]):
    """
    `new_order` is a list of BaseColumn.id values in desired sequence.
    """
    db: Session = database.session

    for pos, row_id in enumerate(new_order, start=1):
        db.query(BaseColumn).filter_by(id=row_id).update({"order": pos})
    db.commit()


def save_base_columns(new_columns, *, allow_deletes=True) -> None:
    # normalise ----------------------------------------------------------------
    if isinstance(new_columns, dict):
        items = list(new_columns.items())
    else:
        items = [(row["key"], row) for row in new_columns]

    db: Session = database.session

    existing = {row.key: row for row in db.query(BaseColumn).all()}
    seen = set()

    # ─── 1st pass: updates / inserts but give each row a TEMP order ──────
    temp_offset = 10000  # puts them far from real range
    for pos, (k, spec) in enumerate(items, start=1):
        seen.add(k)
        if k in existing:
            row = existing[k]
            row.name = spec["name"]
            row.dtype = spec["dtype"]
            row.length = spec.get("length")
            row.decimals = spec.get("decimals")
            row.order = temp_offset + pos  # temporary value
        else:
            db.add(
                BaseColumn(
                    key=k,
                    name=spec["name"],
                    dtype=spec["dtype"],
                    length=spec.get("length"),
                    decimals=spec.get("decimals"),
                    order=temp_offset + pos,  # temporary
                )
            )

    if allow_deletes:
        for k, row in existing.items():
            if k not in seen:
                db.delete(row)

    db.flush()  # executes all temp-order writes

    # ─── 2nd pass: set the FINAL, collision-free order values ────────────
    for pos, (k, _) in enumerate(items, start=1):
        db.query(BaseColumn).filter_by(key=k).update({"order": pos})
    db.commit()


def _to_dict(obj: GeneralSettings) -> dict[str, Any]:
    """
    Convert a GeneralSettings object to a dictionary.
    """
    emails: list[EmailModel] = obj.emails
    return {
        "retry_attempts": obj.retry_attempts,
        "retry_delay": obj.retry_delay,
        "emails": [{"address": e.address, "display_name": e.display_name} for e in emails],
    }


def load_settings(as_dict: bool = False) -> GeneralSettings:
    db: Session = database.session
    s = db.query(GeneralSettings).options(joinedload(GeneralSettings.emails)).first()
    if not s:
        s = GeneralSettings()
        db.add(s)
        db.commit()
        db.refresh(s)
    return _to_dict(s) if as_dict else s


def save_settings(updated: GeneralSettings) -> bool:
    db: Session = database.session

    existing = db.query(GeneralSettings).options(joinedload(GeneralSettings.emails)).first()
    if not existing:
        return False

    # ─── grab the *new* addresses before we mutate anything ──────────
    new_emails_data = [
        (e.address.strip(), e.display_name.strip()) for e in updated.emails if e.address.strip()
    ]

    # scalar fields
    existing.retry_attempts = updated.retry_attempts
    existing.retry_delay = updated.retry_delay

    # replace e-mails
    existing.emails.clear()
    db.flush()  # deletes issued now

    for addr, name in new_emails_data:
        existing.emails.append(EmailModel(address=addr, display_name=name))

    db.commit()
    db.refresh(existing)
    return True
