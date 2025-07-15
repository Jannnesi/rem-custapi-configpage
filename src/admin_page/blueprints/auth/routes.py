import logging
import uuid

import msal
from flask import current_app, redirect, render_template, request, session, url_for

from . import auth_bp

logger = logging.getLogger(__name__)

# ---------- helpers ---------- #


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


def _build_msal_app(cache=None):
    return msal.ConfidentialClientApplication(
        current_app.config["AZURE_CLIENT_ID"],
        authority=current_app.config["AZURE_AUTHORITY"],
        client_credential=current_app.config["AZURE_CLIENT_SECRET"],
        token_cache=cache,
    )


def _build_auth_url(scopes=None, state=None):
    return _build_msal_app().get_authorization_request_url(
        scopes or [],
        state=state or str(uuid.uuid4()),
        redirect_uri=url_for(".callback", _external=True),
    )


# ---------- routes ---------- #


@auth_bp.route("/login")
def login():
    session["auth_state"] = str(uuid.uuid4())
    return redirect(
        _build_auth_url(scopes=current_app.config["AZURE_SCOPE"], state=session["auth_state"])
    )


# NOTE: path must match AZURE_REDIRECT_PATH
@auth_bp.route("/callback")
def callback():
    if request.args.get("state") != session.get("auth_state"):
        return render_template("403.html"), 403

    cache = _load_cache()
    result = _build_msal_app(cache).acquire_token_by_authorization_code(
        request.args.get("code"),
        scopes=current_app.config["AZURE_SCOPE"],
        redirect_uri=url_for(".callback", _external=True),
    )

    if "error" in result:
        return render_template("error.html", error=result.get("error_description"))

    # Save user claims (you can store only what you need)
    session["user"] = {
        "name": result["id_token_claims"].get("name"),
        "email": result["id_token_claims"].get("preferred_username"),
        "oid": result["id_token_claims"].get("oid"),
    }
    _save_cache(cache)
    return redirect(url_for("main.index"))  # or wherever you land the user


@auth_bp.route("/logout")
def logout():
    session.clear()
    logout_url = (
        current_app.config["AZURE_AUTHORITY"]
        + "/oauth2/v2.0/logout"
        + "?post_logout_redirect_uri="
        + url_for("main.index", _external=True)
    )
    return redirect(logout_url)
