"""This module provides an interface to perform a user's
intended action that requires external authentication (ex: Spotify)
after they authenticate and are redirected back to the website.

It uses the flask session to store and retrieve information about
what the user was trying to do before they were sent away for external
authentication.
The following keys names are used in the 'session' object:
- "external_auth_request_url"
- "external_auth_referrer_url"
- "external_auth_retry_func"

An example usage is: A user presses a button to create a new spotify
playlist for a round but is not yet authenticated through spotify. This
interface accomplishes the following tasks:
1. Direct the user to the authorization url to sign in with spotify.
2. Retry the function that creates the playlist using the information the
   user had submitted.
3. Redirect the user to page they were on when they tried creating the
   playlist, this time with the playlist created.
"""

from flask import Blueprint

bp = Blueprint('external_auth', __name__)

from musicrecs.external_auth import handlers
