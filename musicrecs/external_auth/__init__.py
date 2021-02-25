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

from flask import Blueprint

bp = Blueprint('external_auth', __name__)

from musicrecs.external_auth import handlers
