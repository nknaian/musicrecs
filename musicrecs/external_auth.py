"""This module provides an interface to perform a user's
intended action that requires external authentication (ex: Spotify)
after they authenticate and are redirected back to the website.

It uses the flask session to store and retrieve information about
what the user was trying to do before they were sent away for external
authentication.
The following keys names are used in the 'session' object:
- "external_auth_url"
- "external_auth_referrer_url"
- "external_auth_form_data"

An example usage is: A user presses a button to create a new spotify
playlist for a round but is not yet authenticated through spotify. This
interface should be able to be used to save the round and new playlist
information (i.e name, description, image), and then return the user
back to the round page after spotify authentication is complete, with
the playlist created and visible.
"""

from functools import wraps

from flask import session, redirect, flash
from flask.globals import request

from musicrecs import app

from musicrecs.exceptions import ExternalAuthFailure
from musicrecs.spotify import spotify_user


"""CALLBACK ROUTES

These are the routes that will be called after external authorization
is complete.
"""

@app.route('/sp_login_success')
def sp_login_success():
    """Callback route for spotify authorization"""
    # User logged in
    if request.args.get("code"):
        # Save their authorization code
        spotify_user.auth_new_user(request.args.get("code"))

        # Redirect to the recovered url
        flash(f"Hello {spotify_user.get_user_display_name()}, you have successfully connected your Spotify account.", "success")
        return redirect(_get_external_auth_url())
    # User didn't log in
    else:
        flash("You have chosen not to connect your Spotify account right now.", "warning")
        return redirect(_get_external_auth_referrer_url())


"""DECORATORS"""


def recover_after_auth(foo):
    """A decorator to recover a user POST action after an external auth
    
    This decorator can be applied to a flask form submission route
    that involves an action that requires external authentication. It
    will recover the route the user was executing and the form data
    that they had used before the external authentication was required.

    Functions using this decorator must add a "recovered_form_data"
    keyword argument to recover the form data after authentication.

    Functions must also accept both 'GET' and 'POST' methods in their
    route decorator.

    The decorator should be applied AFTER the flask route decorator.
    """
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            # Recover form data from pre-authentication
            external_auth_form_data = session.get("external_auth_form_data", None)
            if external_auth_form_data:
                kwargs["recovered_form_data"] = external_auth_form_data
                session.pop("external_auth_form_data", None)
            # 
            try:
                ret = func(*args, **kwargs)
            # Save pre-authentication information and redirect to
            # authorization url if user is not authenticated
            except ExternalAuthFailure as e:
                session["external_auth_url"] = request.url
                session["external_auth_referrer_url"] = request.referrer
                session["external_auth_form_data"] = request.form
                ret = redirect(e.get_auth_url())
            return ret
        return decorated_function
    return decorator



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
