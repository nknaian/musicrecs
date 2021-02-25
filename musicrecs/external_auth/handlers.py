from flask import session, redirect, flash
from flask.globals import request

from musicrecs.external_auth import bp
from musicrecs.spotify import spotify_user


@bp.route('/sp_auth_complete')
def sp_auth_complete():
    """Callback route for spotify authorization"""
    # User logged in
    if request.args.get("code"):
        # Save their authorization code
        spotify_user.auth_new_user(request.args.get("code"))

        # Redirect to the recovered url
        flash(
            f"Hello {spotify_user.get_user_display_name()}, you have successfully connected your Spotify account.",
            "success"
        )
        return redirect(_get_external_auth_url())
    # User didn't log in
    else:
        flash("You have chosen not to connect your Spotify account right now.", "warning")
        return redirect(_get_external_auth_referrer_url())


"""Private Functions"""


def _get_external_auth_url():
    external_auth_url = session.get("external_auth_url", None)

    # Remove both url options from the session
    session.pop("external_auth_url", None)
    session.pop("external_auth_referrer_url", None)

    return external_auth_url


def _get_external_auth_referrer_url():
    external_auth_referrer_url = session.get("external_auth_referrer_url", None)

    # Remove both url options from the session
    session.pop("external_auth_url", None)
    session.pop("external_auth_referrer_url", None)

    return external_auth_referrer_url
