import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from random_words import RandomWords


SEARCH_LIMIT = 10


class Album:
    def __init__(self, spotify_album, search_term=None):
        self.name = spotify_album["name"]
        self.artist_names = [
            artist["name"] for artist in spotify_album["artists"]
        ]
        self.link = spotify_album["external_urls"]["spotify"]
        self.search_term = search_term


class Spotify:

    def __init__(self):
        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials())

    def get_random_album(self):
        """Gets a random spotify album by searching random words"""

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

        print(
            "Error: No album found after {} searches".format(
                SEARCH_LIMIT
            )
        )

    def get_album_from_link(self, album_link):
        spotify_album = self.sp.album(album_link)
        return Album(spotify_album)
