"""
Alembic migration environment, customised for the admin-page project.

It is invoked by Flask-Migrate’s `flask db ...` wrapper, so `current_app`
is already pushed.  When run directly via `alembic` the `FLASK_APP`
environment variable must resolve to the same factory, or the path below
must import it.
"""

from __future__ import annotations

import logging
import os
import sys
from logging.config import fileConfig

from alembic import context
from flask import current_app

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")

# ---------------------------------------------------------------------------
# Ensure src/ is on sys.path when running `alembic` directly
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# ---------------------------------------------------------------------------
# Build / retrieve the app & db
# ---------------------------------------------------------------------------
try:
    # When invoked via `flask db ...`, current_app already exists
    app = current_app._get_current_object()
except RuntimeError:
    # Running via `alembic upgrade head`; build our own app instance
    from admin_page import create_app

    app = create_app()

db = app.extensions["migrate"].db  # same object as admin_page.extensions.db

# ---------------------------------------------------------------------------
# Alembic config tweaks
# ---------------------------------------------------------------------------
config.set_main_option("sqlalchemy.url", str(db.engine.url).replace("%", "%%"))
target_metadata = db.metadata  # <-- single source of truth

# Uncomment if you only want the “config” schema; otherwise drop it.
# def include_object(obj, name, type_, reflected, compare_to):
#     return obj.schema == "config" if type_ == "table" else True


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _process_revision_directives(context, revision, directives):
    """Skip empty autogen revisions."""
    if getattr(config.cmd_opts, "autogenerate", False):
        script = directives[0]
        if script.upgrade_ops.is_empty():
            directives[:] = []
            logger.info("🛈  No schema changes detected; skipping revision.")


def run_migrations_offline() -> None:
    """Offline mode: generate SQL scripts without DB connection."""
    cfg = {
        "literal_binds": True,
        "compare_type": True,
        "render_as_batch": True,
        # "include_object": include_object,
    }
    context.configure(
        url=str(db.engine.url),
        target_metadata=target_metadata,
        **cfg,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Online mode: run migrations against a live database."""
    with db.engine.connect() as connection:
        # merge our extras into the args that Flask-Migrate prepared
        cfg = app.extensions["migrate"].configure_args.copy()
        cfg.setdefault("compare_type", True)
        cfg.setdefault("render_as_batch", True)
        cfg.setdefault("process_revision_directives", _process_revision_directives)
        # cfg["include_object"] = include_object      # uncomment if used

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            **cfg,
        )
        with context.begin_transaction():
            context.run_migrations()


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
