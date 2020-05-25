import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from random_words import RandomWords

from .album import Album


class Spotify:
    """Class to interface with Spotify API through an
    instance of spotipy.
    """

    def __init__(self):
        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials())

    def get_random_album(self):
        """Gets a random spotify album by searching random words"""

        SEARCH_LIMIT = 10

        def get_search_term():
            random_words = RandomWords()
            return random_words.random_words(count=2)

        num_searches = 0
        while num_searches < SEARCH_LIMIT:
            search_term = get_search_term()
            album_search = self.sp.search(search_term, type="album",
                                          market="US")

            if len(album_search['albums']['items']) == 0:
                continue
            else:
                for album in album_search['albums']['items']:
                    if album['album_type'] == "album":
                        return Album(album, search_term)

            num_searches += 1

        print(f"\nError: No album found after {SEARCH_LIMIT} searches")

    def get_album_from_link(self, album_link):
        spotify_album = self.sp.album(album_link)
        return Album(spotify_album)
