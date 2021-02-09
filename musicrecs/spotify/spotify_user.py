"""A collection of functions to interface with a user's spotify
account, using the spotipy authorization code flow.

If a function is called that requires user authentication, then
the 'ExternalAuthFailure' exception shall be raised, containing
the authorization url that should be visited to log the user in
to spotify and authorize the musicrecs app. It is the caller's
responsibility to catch this exception and redirect to the authorization
url and then direct back towards what the user was trying to do.
"""

import os
import uuid

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from flask import session

from musicrecs.exceptions import ExternalAuthFailure

from .item.spotify_music import SpotifyTrack


'''CONSTANTS'''


SCOPE = 'user-read-currently-playing playlist-modify-private'
CACHE_FOLDER = '.spotify_user_caches/'


'''PUBLIC AUTH FUNCTIONS'''


def get_auth_url(show_dialog=False):
    """Get url for user to visit to sign in to spotify
    and give permission to musicrecs (permission only
    asked for on first authentication from a user)
    """
    return _get_auth_manager(show_dialog=show_dialog).get_authorize_url()


def auth_new_user(code):
    """Give user an access token to authenticate them"""
    _get_auth_manager().get_access_token(code)


def not_you():
    """A bit of a hacky solution, but the best simple one that
    seems available. This function will remove the session and
    spotify cached tokens and then return the authorization url
    with dialog shown. The permission dialog being shown gives
    the user the oppertunity to login as a different user through
    the 'not_you' button (thus the name of this function).

    """
    if os.path.exists(_session_cache_path()):
        os.remove(_session_cache_path())
        session.clear()
    return get_auth_url(show_dialog=True)


'''PUBLIC FUNCTIONS'''


def get_current_track():
    """Return information about the track the user is currently playing

    If the current user is not authenticated, then a
    'ExternalAuthFailure' exception will be raised.
    """
    track_info = _get_sp_instance().current_user_playing_track()
    if track_info is not None:
        return SpotifyTrack(track_info['item'])
    return "No track currently playing."


def get_user_display_name():
    return _get_sp_instance().me()['display_name']


'''PRIVATE FUNCTIONS'''


def _session_cache_path():
    if not os.path.exists(CACHE_FOLDER):
        os.makedirs(CACHE_FOLDER)

    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())

    return CACHE_FOLDER + session.get('uuid')


def _get_sp_instance():
    """Create an spotify auth_manager and check whether the current user has
    a token (has been authorized already). If the user has a token, then they
    are authenticated -- return their spotipy instance. If the user does not have
    a token, then they are not authenticated -- raise an exception
    """
    auth_manager = _get_auth_manager()

    if auth_manager.get_cached_token():
        return spotipy.Spotify(auth_manager=auth_manager)
    else:
        raise ExternalAuthFailure(get_auth_url())


def _get_auth_manager(show_dialog=False):
    return SpotifyOAuth(scope=SCOPE,
                        cache_path=_session_cache_path(),
                        show_dialog=show_dialog)
