from functools import wraps

from flask import session, redirect
from flask.globals import request

from musicrecs.exceptions import ExternalAuthFailure


def recover_after_auth():
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
            # Run the wrapped function
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
