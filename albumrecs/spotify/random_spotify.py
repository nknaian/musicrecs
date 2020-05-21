import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from random_words import RandomWords


class RandomSpotify:
    """Use spotipy to get random music from spotify"""

    def __init__(self):
        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials())
        self.rw = RandomWords()

    def get_random_album(self):
        """Gets a random spotify album link by searching random words"""

        not_found = True
        album_link = None
        while not_found:
            search_term = self.rw.random_words(count=2)

            album_search = self.sp.search(search_term, type="album",
                                          market="US")

            if len(album_search['albums']['items']) == 0:
                continue
            else:
                for album in album_search['albums']['items']:
                    if album['album_type'] == "album":
                        album_link = album['external_urls']['spotify']
                        not_found = False
                        break
        return album_link
