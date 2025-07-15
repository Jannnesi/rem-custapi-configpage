# customers/services.py
from __future__ import annotations

from collections.abc import MutableMapping, Sequence
from typing import Any, Literal, overload

from sqlalchemy.orm import Session
from werkzeug.exceptions import BadRequest, NotFound

from admin_page.extensions import db as database
from admin_page.models.customer_model import Customer


def _dict_from_extras(items: list[Any]) -> dict[str, dict[str, str]] | None:
    """
    Accept *either* FieldList[ExtraColumnForm] *or* a list of plain dicts
    (what WTForms puts into form.data).  Returns:
        {key: {"name": ..., "dtype": ...}}   or   None
    """
    out: dict[str, dict[str, str]] = {}

    for f in items:
        # 1) If we've been given a sub-form object
        if hasattr(f, "key"):
            k = (f.key.data or "").strip()
            nm = (f.name.data or "").strip()
            dt = (f.dtype.data or "").strip()
        # 2) Plain dict (form.data case)
        elif isinstance(f, MutableMapping):
            k = (f.get("key") or "").strip()
            nm = (f.get("name") or "").strip()
            dt = (f.get("dtype") or "").strip()
        else:
            continue  # ignore anything unexpected

        if k:
            out[k] = {"name": nm, "dtype": dt}

    return out or None


def save_config(data: dict[str, Any], pk: int | None = None) -> Customer:
    """
    Create or update a CustomerConfig.

    Parameters
    ----------
    data : dict
        Typically `form.data` from WTForms.
    pk : int | None
        When None (default) we create a new row; otherwise we UPDATE
        the row whose primary-key == pk.

    Raises
    ------
    werkzeug.exceptions.NotFound
        If `pk` is given but no such row exists.
    werkzeug.exceptions.BadRequest
        If `name` is already taken on INSERT.
    """
    db: Session = database.session

    if pk is None:
        # INSERT
        if db.query(Customer).filter_by(name=data["name"]).first():
            raise BadRequest("A customer with that name already exists.")

        cfg = Customer()
        db.add(cfg)
    else:
        # UPDATE
        cfg = db.get(Customer, pk)
        if cfg is None:
            raise NotFound(f"CustomerConfig with id={pk} not found.")

    # ─── Map WTForms data → ORM ────────────────────────────────────────────
    cfg.name = data["name"]
    cfg.konserni = list({int(x) for x in data["konserni"]})
    cfg.source_container = data["source_container"]
    cfg.destination_container = data["destination_container"]
    cfg.file_format = data["file_format"]
    cfg.file_encoding = data["file_encoding"]
    cfg.extra_columns = _dict_from_extras(data["extra_columns"])
    cfg.exclude_columns = data["exclude_columns"] or None
    cfg.enabled = bool(data.get("enabled", False))

    db.commit()
    return cfg


# ─────────────────────────────────────────────────────────────────────────────
# Optional: tiny serializer so templates / JSON dumps don't have to
# touch the ORM object directly.
# ─────────────────────────────────────────────────────────────────────────────
def _to_dict(obj: Customer) -> dict[str, Any]:
    """Convert a CustomerModel into a plain dict."""
    return {
        "id": obj.id,
        "name": obj.name,
        "konserni": obj.konserni,  # list[int]
        "source_container": obj.source_container,
        "destination_container": obj.destination_container,
        "file_format": obj.file_format,
        "file_encoding": obj.file_encoding,
        "extra_columns": obj.extra_columns,
        "exclude_columns": obj.exclude_columns,
        "enabled": obj.enabled,
    }


# ── overloads ──────────────────────────────────────────────────────────


@overload
def list_configs(
    *,
    pk: int,
    as_dict: Literal[False] = False,
) -> Customer | None: ...


@overload
def list_configs(
    *,
    pk: int,
    as_dict: Literal[True],
) -> dict[str, Any] | None: ...


@overload
def list_configs(
    *,
    pk: None | Sequence[int] = None,
    as_dict: Literal[False] = False,
) -> list[Customer]: ...


@overload
def list_configs(
    *,
    pk: None | Sequence[int] = None,
    as_dict: Literal[True],
) -> list[dict[str, Any]]: ...


# ─────────────────────────────────────────────────────────────────────────────
# Implementation
# ─────────────────────────────────────────────────────────────────────────────
def list_configs(
    *, pk: None | int | Sequence[int] = None, as_dict: bool = False
) -> list[Customer] | list[dict[str, Any]] | Customer | None | dict[str, Any] | None:
    """
    Fetch customer configuration rows.

    Parameters
    ----------
    pk
        • None                → return *all* rows (list)
        • int                 → return the single row or `None`
        • list/tuple of ints  → IN-filter, return list
    as_dict
        When True, convert each result to a plain dict.

    Returns
    -------
    • single object or None (when pk is a single int)
    • list[...] for all other cases
    """
    db: Session = database.session

    q = db.query(Customer).order_by(Customer.name)

    # ----- single primary-key ------------------------------------------
    if isinstance(pk, int):
        obj = q.filter(Customer.id == pk).one_or_none()
        if as_dict and obj is not None:
            return _to_dict(obj)
        return obj

    # ----- multiple keys or "all" -------------------------------------
    if pk is not None:  # Sequence[int]
        q = q.filter(Customer.id.in_(pk))

    rows = q.all()
    return [_to_dict(r) for r in rows] if as_dict else rows


def set_customer_enabled(customer_id: int, enabled: bool) -> Customer:
    """
    Toggle Customer.enabled. Raises ValueError if the id doesn't exist.
    """

    db: Session = database.session

    customer = db.get(Customer, customer_id)
    if not customer:
        raise ValueError(f"Customer id={customer_id} not found")

    customer.enabled = bool(enabled)
    db.commit()
    db.refresh(customer)

    return customer


def delete_customer(customer_id: int) -> bool:
    """
    Delete the Customer row with the given id.
    Returns True if a row was deleted, False if not found.
    """

    db: Session = database.session

    customer = db.get(Customer, customer_id)
    if not customer:

        return False

    db.delete(customer)
    db.commit()

    return True
