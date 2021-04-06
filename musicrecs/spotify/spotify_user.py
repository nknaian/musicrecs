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
from typing import List
import uuid

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from flask import session

from musicrecs.external_auth.exceptions import ExternalAuthFailure

from .item.spotify_music import SpotifyTrack
from .item.spotify_playlist import SpotifyPlaylist


'''CONSTANTS'''


SCOPE = 'playlist-modify-public'
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


def get_user_playlists():
    sp = _get_sp_instance()

    playlist_infos = sp.current_user_playlists()

    playlists = []
    while playlist_infos:
        for playlist in playlist_infos['items']:
            playlists.append(playlist)
        if playlist_infos['next']:
            playlist_infos = sp.next(playlist_infos)
        else:
            playlist_infos = None

    return playlists


def create_playlist(name: str, tracks: List[SpotifyTrack]) -> SpotifyPlaylist:
    """Create a playlist of the passed in tracks with the given name

    It will return the spotify link of the created playlist.
    """
    # Get the spotify user account instance
    sp = _get_sp_instance()

    # Get the current user's id
    user_id = sp.current_user()["id"]

    # Create the playlist with the given name, for the current user.
    sp.user_playlist_create(user_id, name)

    # Make a playlist object for the playlist that was just created
    new_playlist = SpotifyPlaylist(sp.current_user_playlists()['items'][0])

    # Add the given tracks to the new playlist
    sp.user_playlist_add_tracks(user_id,
                                new_playlist.id,
                                [track.id for track in tracks])

    # Return the new playlist
    return new_playlist


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
