import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from random_word import RandomWords

"""Gets random music from spotify"""

def get_random_album():
    """Gets a random spotify album link by searching random words"""
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    r = RandomWords()

    not_found = True
    album_link = None
    while not_found:
        search_term = r.get_random_words(hasDictionaryDef="true", limit=2)

        album_search = sp.search(search_term, type="album", market="US")

        if len(album_search['albums']['items']) == 0:
            continue
        else:
            for album in album_search['albums']['items']:
                if album['album_type'] == "album":
                    album_link = album['external_urls']['spotify']
                    not_found = False
                    break
    return album_link
