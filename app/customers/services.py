# customers/services.py
from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Dict, List, Literal, Optional, Union, overload, MutableMapping

from sqlalchemy import text
from sqlalchemy.orm import Session
from werkzeug.exceptions import NotFound, BadRequest

from .forms import ExtraColumnForm
from ..models.customer_model import Customer
from ..models.database_handler import DatabaseHandler


def _dict_from_extras(items: List[Any]) -> Dict[str, Dict[str, str]] | None:
    """
    Accept *either* FieldList[ExtraColumnForm] *or* a list of plain dicts
    (what WTForms puts into form.data).  Returns:
        {key: {"name": ..., "dtype": ...}}   or   None
    """
    out: Dict[str, Dict[str, str]] = {}

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
            continue   # ignore anything unexpected

        if k:
            out[k] = {"name": nm, "dtype": dt}

    return out or None


def save_config(data: Dict[str, Any], pk: int | None = None) -> Customer:
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
    db: Session = DatabaseHandler().session

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
def _to_dict(obj: Customer) -> Dict[str, Any]:
    """Convert a CustomerModel into a plain dict."""
    return {
        "id":                    obj.id,
        "name":                  obj.name,
        "konserni":              obj.konserni,           # list[int]
        "source_container":      obj.source_container,
        "destination_container": obj.destination_container,
        "file_format":           obj.file_format,
        "file_encoding":         obj.file_encoding,
        "extra_columns":         obj.extra_columns,
        "exclude_columns":       obj.exclude_columns,
        "enabled":               obj.enabled,
    }

# ── overloads ──────────────────────────────────────────────────────────
@overload
def list_configs(
    *,                            
    pk: int,
    as_dict: Literal[False] = False, 
) -> Optional[Customer]: ...
@overload
def list_configs(
    *,
    pk: int,
    as_dict: Literal[True], 
) -> Optional[Dict[str, Any]]: ...
@overload
def list_configs(
    *,
    pk: None | Sequence[int] = None,
    as_dict: Literal[False] = False,
) -> List[Customer]: ...
@overload
def list_configs(
    *,
    pk: None | Sequence[int] = None,
    as_dict: Literal[True],
) -> List[Dict[str, Any]]: ...


# ─────────────────────────────────────────────────────────────────────────────
# Implementation
# ─────────────────────────────────────────────────────────────────────────────
def list_configs(
    *,
    pk: Union[None, int, Sequence[int]] = None,
    as_dict: bool = False
) -> Union[
    List[Customer],                         # no pk / multi pk → list ORM
    List[Dict[str, Any]],                        # no pk / multi pk → list dict
    Optional[Customer],                     # single pk → single ORM / None
    # single pk → single dict / None
    Optional[Dict[str, Any]]
]:
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
    db: Session = DatabaseHandler().session
    try:
        q = db.query(Customer).order_by(Customer.name)

        # ----- single primary-key ------------------------------------------
        if isinstance(pk, int):
            obj = q.filter(Customer.id == pk).one_or_none()
            if as_dict and obj is not None:
                return _to_dict(obj)
            return obj

        # ----- multiple keys or "all" -------------------------------------
        if pk is not None:                       # Sequence[int]
            q = q.filter(Customer.id.in_(pk))

        rows = q.all()
        return [_to_dict(r) for r in rows] if as_dict else rows

    finally:
        db.close()


def set_customer_enabled(customer_id: int, enabled: bool) -> Customer:
    """
    Toggle Customer.enabled. Raises ValueError if the id doesn't exist.
    """

    db = DatabaseHandler().session

    customer = db.get(Customer, customer_id)
    if not customer:
        raise ValueError(f"Customer id={customer_id} not found")

    customer.enabled = bool(enabled)
    db.commit()
    db.refresh(customer)

    db.close()

    return customer


def delete_customer(customer_id: int) -> bool:
    """
    Delete the Customer row with the given id.
    Returns True if a row was deleted, False if not found.
    """

    db = DatabaseHandler().session

    customer = db.get(Customer, customer_id)
    if not customer:
        db.close()
        return False

    db.delete(customer)
    db.commit()

    db.close()

    return True
