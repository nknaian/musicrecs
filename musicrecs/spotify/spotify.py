"""Spotify interface class that uses the spotipy client
credentials authentication method. This class can be used
to interface with spotify for use cases that don't require
access to individual user accounts. So, things like searching
for music, or getting information about music based on a
spotify link.
"""

import random
import copy

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from .music import Music, Album, Track

"""Popularity is a number that spotify
assigns to music based on how many listens it's
getting recently. This threshold filters out
music that is not popular enough
"""
POPULARITY_THRESHOLD = 15

"""Maximum number of samples that can be used
in spotipy's "recommendations" function
"""
MAX_REC_SEEDS = 5


class Spotify:
    """Class to interface with Spotify API through an
    instance of client credentials authenticated spotipy.
    """

    def __init__(self):
        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials())

    """Public Functions"""

    def search_for_music(self, music_type, search_term):
        """Gets spotify music by searching the search term. Filters
        music out that is below the popularity threshold
        If nothing is found it will return None

        Args:
            type: Type of music object. Either album or track
            search_term: A string containing the word/s to be
                search for music

        Return:
            A spotify link, or None if nothing was found

        """
        # Search for the music type using the search term
        search = self.sp.search(search_term, type=music_type)
        music_items = search[f'{music_type}s']['items']

        # Go through the music items brought up in the search
        if len(music_items):
            for music_item in music_items:
                # Get the popularity of the artists for this music item
                artists_popularity = self._get_artists_popularity(
                    music_item['artists'])

                # If the popularity is above the threshold, then return
                # the item
                if artists_popularity >= POPULARITY_THRESHOLD:
                    if music_type == "album":
                        if music_item['album_type'] == "album":
                            return Album(music_item, search_term).link
                    elif music_type == "track":
                        if music_item['type'] == "track":
                            return Track(music_item, search_term).link
        else:
            return None

    def recommend_music(self, music_type, spotify_links):
        """Gets a spotify recommendation based on a list of spotify
        links passed in

        Args:
            human_music_recs: list of `Music` objects that
                humans recommended.

        Return:
            A spotify link
        """
        # Assure that we have at least one human music rec
        assert len(spotify_links) > 0

        music_list = [self.get_music_from_link(music_type, link) for link in spotify_links]

        if music_type == "album":
            return self._recommend_album(music_list).link
        elif music_type == "track":
            return self._recommend_track(music_list).link

    def get_music_from_link(self, music_type, link):
        """Use spotify link to get `Music` object"""
        if music_type == "album":
            spotify_album = self.sp.album(link)
            return Album(spotify_album)
        elif music_type == "track":
            spotify_track = self.sp.track(link)
            return Track(spotify_track)

    """Private Functions"""

    def _recommend_album(self, human_album_recs: [Album]) -> Album:
        # Get artist seeds from the album list passed in
        seed_artists = [album.get_primary_artist().id
                        for album in human_album_recs]
        if len(seed_artists) > MAX_REC_SEEDS:
            seed_artists = random.sample(seed_artists, MAX_REC_SEEDS)

        # Get an album rec
        album_rec = None
        while album_rec is None:
            # Get a track rec based on the given seed artists
            track_rec = self._get_track_rec_from_seeds(
                human_album_recs, seed_artists=seed_artists)

            # Get a random album by the primary artist of the track rec
            artist_album_items = self.sp.artist_albums(
                track_rec.get_primary_artist().id, album_type="album"
            )['items']
            if len(artist_album_items):
                # Pick a random album from the artist's discography
                album_rec = Album(random.sample(artist_album_items, 1)[0])

        return album_rec

    def _recommend_track(self, human_track_recs: [Track]) -> Track:
        # Get the track seeds from the track list passed in (spotipy accepts
        # ids as one of the options for track seeds)
        seed_tracks = [track.id for track in human_track_recs]
        if len(seed_tracks) > MAX_REC_SEEDS:
            seed_tracks = random.sample(seed_tracks, MAX_REC_SEEDS)

        # Get a track rec based on the given seed tracks
        track_rec = None
        while track_rec is None:
            track_rec = self._get_track_rec_from_seeds(
                human_track_recs, seed_tracks=seed_tracks)

        return track_rec

    def _get_track_rec_from_seeds(self,
                                  human_music_recs,
                                  seed_tracks=None,
                                  seed_artists=None):
        track_items = self.sp.recommendations(
            seed_tracks=seed_tracks, seed_artists=seed_artists
        )["tracks"]
        sp_track_recs = [Track(track_item) for track_item in track_items]

        # Remove any track that shares an artist with one of the human
        # music recs
        sp_track_recs_copy = copy.deepcopy(sp_track_recs)
        for sp_track_rec in sp_track_recs_copy:
            if any(self._do_musics_share_artist(sp_track_rec, human_music_rec)
                   for human_music_rec in human_music_recs):
                self._remove_music_from_list(sp_track_rec.id, sp_track_recs)

        # Pick one random track
        if len(sp_track_recs):
            return random.sample(sp_track_recs, 1)[0]
        else:
            return None

    def _do_musics_share_artist(self, music1: Music, music2: Music):
        music1_artist_ids = [artist.id for artist in music1.artists]
        music2_artist_ids = [artist.id for artist in music2.artists]

        common_ids = set(music1_artist_ids) & set(music2_artist_ids)

        return bool(common_ids)

    def _remove_music_from_list(self, music_id: str, music_list: [Music]):
        for music in music_list:
            if music_id == music.id:
                music_list.remove(music)
                break

    def _get_artists_popularity(self, artists):
        """Get the popularity of the most popular artist in the list
        of artists
        """
        popularity = 0

        for artist in artists:
            artist_popularity = self._get_artist_popularity(artist['id'])
            if artist_popularity > popularity:
                popularity = artist_popularity

        return popularity

    def _get_artist_popularity(self, artist_id):
        return self.sp.artist(artist_id)['popularity']
