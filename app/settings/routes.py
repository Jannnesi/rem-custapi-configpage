import logging

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    abort,
)
from werkzeug.exceptions import NotFound
from sqlalchemy.exc import SQLAlchemyError

from . import bp
from .services import load_settings, save_settings, get_base_columns, save_base_columns
from .forms import GeneralSettingsForm, BaseColumnListForm
from ..models import EmailModel

logger = logging.getLogger(__name__)


@bp.route("/")
def index():
    logger.info("Rendering settings index")
    return render_template("settings_index.html")


@bp.route("/base_columns", methods=["GET", "POST"])
def base_columns():
    """Add / edit / reorder the base-column definitions."""
    
    # ──────────────────────────── build the form ───────────────────────────
    if request.method == "POST":
        form = BaseColumnListForm(request.form)        # bind user input
        base_columns_for_js = None                     # template doesn't need it
    else:                                              # GET
        try:
            columns = get_base_columns(as_ordered=True)
        except Exception as err:
            logger.error("Failed to retrieve base columns: %s", err, exc_info=True)
            flash("Error retrieving base columns", "error")
            return redirect(url_for("settings.index"))

        form = BaseColumnListForm(data={"columns": columns})
        base_columns_for_js = columns                   # used by the Jinja loop

    # ─────────────────────────── validate & save ──────────────────────────
    if form.validate_on_submit():
        try:
            save_base_columns(form.columns.data)
            flash("Base columns updated successfully", "success")
            return redirect(url_for("settings.index"))
        except SQLAlchemyError:
            logger.exception("Failed to save base columns.")
            flash("Error saving base columns", "error")

    # log validation errors on POST
    if request.method == "POST" and form.errors:
        logger.warning("Base columns form validation failed: %s", form.errors)
        flash("Virheellinen syöte. Tarkista kentät.", "error")

    # ───────────────────────────── render page ────────────────────────────
    return render_template(
        "base_columns_form.html",
        form=form,
        base_columns=base_columns_for_js   # None on failed POST; template uses `form`
    )
@bp.route("/general_settings", methods=["GET", "POST"])
def general_settings():
    settings = load_settings()
    form = GeneralSettingsForm(obj=settings)
    logger.info("Rendering general settings form with settings: %s", settings.emails)
    # ensure at least one blank email row on first GET
    if not form.emails.entries:
        form.emails.append_entry()
        
    if form.validate_on_submit():
        # ── scalar fields ──────────────────────────
        settings.retry_attempts = (
            form.retry_attempts.data
            if form.retry_attempts.data is not None 
            else 3
        )
        settings.retry_delay = (
            form.retry_delay.data
            if form.retry_delay.data is not None
            else 5
        )

        # ── rebuild e-mail list ─────────────────────
        settings.emails.clear()
        for fld in form.emails.entries:
            address = (fld.form.address.data or "").strip()
            display = (fld.form.display_name.data or "").strip()
            settings.emails.append(
                EmailModel(address=address, display_name=display)
            )

        save_settings(settings)
        flash("Asetukset tallennettu", "success")
        return redirect(url_for("settings.index"))
    
    if request.method == "POST" and not form.validate():
        logger.warning("General settings form validation failed: %s", form.errors)
        flash("Virheellinen syöte. Tarkista kentät.", "error")

    return render_template("general_settings_form.html", form=form)
