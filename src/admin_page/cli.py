"""
admin_page/cli.py
-----------------
Flask-CLI commands to seed reference data.

$ flask bootstrap-base-columns
$ flask bootstrap-customers
$ flask bootstrap-all          # convenience wrapper
"""

from __future__ import annotations

import json
from pathlib import Path

import click
from blueprints.customers.services import save_config  # existing helper
from extensions import db
from flask import current_app
from models.base_column_model import BaseColumn
from sqlalchemy.orm import Session

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError) as exc:
        click.echo(click.style(f"❌  {exc}", fg="red"))
        raise click.Abort() from exc


def _app_root() -> Path:
    """Return <project-root>/src/admin_page (where this file lives)."""
    return Path(current_app.root_path)  # works inside app context


# ---------------------------------------------------------------------------
# individual commands
# ---------------------------------------------------------------------------


@click.command("bootstrap-base-columns")
def bootstrap_base_columns() -> None:
    """
    Create / update rows in `base_columns` from base_columns.json.
    """
    app_root = _app_root()
    json_path = app_root.parent.parent / "base_columns.json"  # same as old script
    data = _load_json(json_path)["base_columns"]

    engine = db.engine
    BaseColumn.metadata.create_all(bind=engine, checkfirst=True)

    with Session(engine) as session:
        for position, (key, spec) in enumerate(data.items(), start=1):
            session.merge(
                BaseColumn(
                    key=key,
                    name=spec["name"],
                    dtype=spec["dtype"],
                    length=spec.get("length"),
                    decimals=spec.get("decimals"),
                    order=position,
                )
            )
        session.commit()

        count = session.query(BaseColumn).count()
        click.echo(click.style(f"✓  {count} base columns loaded", fg="green"))


@click.command("bootstrap-customers")
def bootstrap_customers() -> None:
    """
    Insert / update customer configs found in blueprints/customers/customer_configs/*.json
    """
    cfg_dir = _app_root() / "blueprints" / "customers" / "customer_configs"
    json_files = sorted(cfg_dir.glob("*.json"))
    if not json_files:
        click.echo(click.style(f"⚠  No JSON files in {cfg_dir}", fg="yellow"))
        return

    for jf in json_files:
        data = _load_json(jf)
        try:
            save_config(data)
            click.echo(click.style(f"✓  {jf.name} → {data.get('name','?')}", fg="green"))
        except Exception as exc:
            click.echo(click.style(f"❌  {jf.name}: {exc}", fg="red"))


# ---------------------------------------------------------------------------
# bundle command
# ---------------------------------------------------------------------------


@click.command("bootstrap-all")
@click.pass_context
def bootstrap_all(ctx: click.Context) -> None:
    """
    Run both bootstrap commands in order.
    """
    ctx.invoke(bootstrap_base_columns)
    ctx.invoke(bootstrap_customers)


# ---------------------------------------------------------------------------
# registration helper
# ---------------------------------------------------------------------------


def register_commands(app) -> None:
    """
    Call from create_app() to register the commands.
    """
    for cmd in (bootstrap_base_columns, bootstrap_customers, bootstrap_all):
        app.cli.add_command(cmd)
