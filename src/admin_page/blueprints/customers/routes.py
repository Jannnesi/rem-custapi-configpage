"""
URL endpoints for managing customer configurations.
"""

import logging

from flask import abort, flash, jsonify, redirect, render_template, request, url_for
from werkzeug.exceptions import NotFound

from ..auth import login_required
from ..settings.services import get_base_columns

# from ..auth.aad import login_required
from . import customers_bp
from .forms import CustomerForm
from .services import delete_customer, list_configs, save_config, set_customer_enabled

logger: logging.Logger = logging.getLogger(__name__)

# ───────────────────────────────────────
# List / index
# ───────────────────────────────────────


@customers_bp.route("/", methods=["GET"])
@login_required
def index():
    """
    Show all customer configs.
    """
    customers = list_configs()  # Returns list[dict] or Model objs
    return render_template("list.html", customers=customers)


# ───────────────────────────────────────
# Create
# ───────────────────────────────────────
@customers_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    form = CustomerForm()

    try:
        if form.validate_on_submit():
            save_config(form.data)  # pk=None → INSERT
            flash("Customer created successfully.", "success")
            return redirect(url_for("customers.index"), 302)
    except Exception:
        logger.exception("Error creating customer")  # stack-trace!
        flash("Error creating customer.", "error")

    if request.method == "POST" and not form.validate():
        logger.warning("Customer form validation failed: %s", form.errors)
        flash("Invalid input. Please check the fields.", "error")

    return render_template("form.html", form=form, base_columns=get_base_columns(), action="Create")


# ───────────────────────────────────────
# Edit
# ───────────────────────────────────────
@customers_bp.route("/<int:pk>/edit", methods=["GET", "POST"])
@login_required
def edit(pk: int):
    """
    Edit an existing customer configuration.
    """

    customer = list_configs(pk=pk, as_dict=True)
    if customer is None:
        raise NotFound("Customer not found")
    base_columns = get_base_columns()

    form = CustomerForm(obj=customer)  # Pre-fill with existing data
    logger.info(customer["exclude_columns"])
    logger.info(f"data: {form.data}")
    try:
        if form.validate_on_submit():
            save_config(form.data, pk=pk)
            flash(f"Changes saved for customer {customer['name']}.", "success")
            return redirect(url_for("customers.index"), 302)
    except Exception:
        logger.exception("Error saving customer")
        flash("Error saving customer.", "error")

    if request.method == "POST" and not form.validate():
        logger.warning("Customer form validation failed: %s", form.errors)
        flash("Invalid input. Please check the fields.", "error")

    customer["konserni_csv"] = ", ".join(str(x) for x in customer["konserni"])
    return render_template(
        "form.html", form=form, action="Edit", customer=customer, base_columns=base_columns
    )


# ───────────────────────────────────────
# Change enabled state
# ───────────────────────────────────────


@customers_bp.post("/<int:cust_id>/enabled")
@login_required
def toggle_customer_enabled(cust_id: int):
    # CSRF is auto-checked by CSRFProtect if you included the header
    data = request.get_json(silent=True) or {}
    if "enabled" not in data:
        abort(400, description="JSON must include 'enabled': true|false")

    try:
        customer = set_customer_enabled(cust_id, data["enabled"])
        return jsonify({"status": "ok", "enabled": customer.enabled})
    except ValueError as e:
        logger.warning(e)
        abort(404)
    except Exception:
        logger.exception("Failed to toggle customer %s", cust_id)
        abort(500, description="internal error")


# ───────────────────────────────────────
# Delete
# ───────────────────────────────────────


@customers_bp.post("/<int:pk>/delete")
@login_required
def delete(pk):
    """
    POST /customers/<pk>/delete  — remove a customer config.
    """
    if not delete_customer(pk):
        abort(404)

    flash("Customer deleted.", "success")
    next_url = request.args.get("next") or url_for("customers.index")
    return redirect(next_url)
