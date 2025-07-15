# src/admin_page/blueprints/__init__.py
from importlib import import_module

# list folder names → dotted import path
_BLUEPRINT_PKGS = [
    "blueprints.auth",
    "blueprints.core",
    "blueprints.customers",
    "blueprints.settings",
    "blueprints.manual_run",
    "blueprints.api",
]


def register_blueprints(app) -> None:
    """Import each package so it calls init_app(app)."""
    for path in _BLUEPRINT_PKGS:
        mod = import_module(f"src.admin_page.{path}")
        if hasattr(mod, "init_app"):
            mod.init_app(app)
