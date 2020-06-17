

class Music:
    """Base class for a music object. Holds select """

    def __init__(self, spotify_music, search_term=None):
        # Name of the spotify music object
        self.name = spotify_music["name"]

        # List of artist names credited
        self.artist_names = [
            artist["name"] for artist in spotify_music["artists"]
        ]

        # Get the open.spotify link to the album
        self.link = spotify_music["external_urls"]["spotify"]

        # Set search term that was used to get album
        self.search_term = search_term

    def _set_album_img(self, spotify_album, img_dimen):
        self.img_url = None
        for img in spotify_album["images"]:
            if img["height"] == img_dimen and img["width"] == img_dimen:
                self.img_url = img["url"]
                break
        if self.img_url is None:
            print("Error: No matching album image found")


class Album(Music):
    """Class to hold selected information about a spotify album."""

    IMG_DIMEN = 300

    def __init__(self, spotify_album, search_term=None):

        # Initialize base class
        super().__init__(spotify_album, search_term)

        # Get image url with given IMG_DIMEN
        self._set_album_img(spotify_album, self.IMG_DIMEN)


class Track(Music):
    """Class to hold selected information about a spotify track."""

    IMG_DIMEN = 64

    def __init__(self, spotify_track, search_term=None):

        # Initialize base class
        super().__init__(spotify_track, search_term)

        # Get image url with given IMG_DIMEN
        self._set_album_img(spotify_track["album"], self.IMG_DIMEN)
