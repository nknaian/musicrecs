from importlib import import_module
from typing import Dict

from flask import session, redirect, flash
from flask.globals import request

from musicrecs.external_auth import bp
from musicrecs.spotify import spotify_user

from .exceptions import ExternalAuthFailure


"""ROUTE HANDLERS"""


@bp.route('/sp_auth_complete')
def sp_auth_complete():
    """Callback route for spotify authorization"""
    # User logged in
    if request.args.get("code"):
        # Save their authorization code
        spotify_user.auth_new_user(request.args.get("code"))

        # Call the recovered function
        retry_func_info = session.get("external_auth_retry_func_info", None)
        if retry_func_info:
            _call_retry_func(retry_func_info)

        # Redirect to the page the user was visiting when auth was required
        redirect_url = session["external_auth_request_url"]

        flash(
            f"Hello {spotify_user.get_user_display_name()}, you have successfully connected your Spotify account.",
            "success"
        )
    # User didn't log in
    else:
        redirect_url = session["external_auth_referrer_url"]
        flash("You have chosen not to connect your Spotify account right now.", "warning")

    # Clear all external auth session data
    session.pop("external_auth_request_url")
    session.pop("external_auth_referrer_url")
    session.pop("external_auth_retry_func_info")

    return redirect(redirect_url)


"""EXCEPTION HANDLERS"""


@bp.app_errorhandler(ExternalAuthFailure)
def handle_external_auth_exception(e):
    session["external_auth_request_url"] = request.url
    session["external_auth_referrer_url"] = request.referrer
    return redirect(e.auth_url)


"""PRIVATE FUNCTIONS"""


def _call_retry_func(func_info: Dict):
    """Get the function that needs to be retried and then call it
    """
    func_module = import_module(func_info["module"])
    func = getattr(func_module, func_info["qualname"])
    func(*func_info["args"], **func_info["kwargs"])
