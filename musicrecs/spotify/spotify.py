import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from random_words import RandomWords

from .music import Album, Track


class Spotify:
    """Class to interface with Spotify API through an
    instance of spotipy.
    """

    def __init__(self, music_type):
        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials())
        self.MUSIC_TYPE = music_type

    def get_random_music(self):
        """Gets random spotify music by searching random words

        Args:
            type: Type of music object. Either album or track

        """

        def get_search_term():
            random_words = RandomWords()
            word_list = random_words.random_words(count=2)
            return " ".join(word_list)

        SEARCH_LIMIT = 10
        num_searches = 0
        while num_searches < SEARCH_LIMIT:
            num_searches += 1

            search_term = get_search_term()
            search = self.sp.search(search_term, type=self.MUSIC_TYPE,
                                    market="US")

            items = search[f'{self.MUSIC_TYPE}s']['items']
            if len(items) == 0:
                continue
            else:
                for item in items:
                    if self.MUSIC_TYPE == "album":
                        if item['album_type'] == "album":
                            return Album(item, search_term)
                    elif self.MUSIC_TYPE == "track":
                        if item['type'] == "track":
                            return Track(item, search_term)
                    else:
                        raise Exception(
                            f"Unknown music type {self.MUSIC_TYPE}")

        raise Exception(
            "\nError: No {} found after {} searches".format(
                self.MUSIC_TYPE, SEARCH_LIMIT
            )
        )

    def get_music_from_link(self, link):
        if self.MUSIC_TYPE == "album":
            spotify_album = self.sp.album(link)
            return Album(spotify_album)
        elif self.MUSIC_TYPE == "track":
            spotify_track = self.sp.track(link)
            return Track(spotify_track)
        else:
            raise Exception(f"Unknown music type {self.MUSIC_TYPE}")
