from .artist import Artist


class Music:
    """Base class for a music object. Holds selected information
    about a spotify music item (either track or album)
    """

    def __init__(self, spotify_music, search_term=None):
        # Name of the spotify music object
        self.name = spotify_music["name"]

        # List of artists credited
        self.artists = [
            Artist(artist) for artist in spotify_music["artists"]
        ]

        # Get the open.spotify link to the music
        self.link = spotify_music["external_urls"]["spotify"]

        # Get the spotify id of the music
        self.id = spotify_music["id"]

        # Set search term that was used to get music
        self.search_term = search_term

    def format(self, fmt_type):
        if fmt_type == "text":
            return (f"{self.name} by "
                    f"{', '.join(artist.name for artist in self.artists)}")

        elif fmt_type == "html":
            img_link = (
                f"<a href='{self.link}'>"
                f"<img src='{self.img_url}'"
                f"alt='{self.name}"
                f"style='width:{self.IMG_DIMEN}px;"
                f"height:{self.IMG_DIMEN}px;"
                "border:0;'>"
                "</a>"
            )

            return (
                f"<b>{self.name}</b> by "
                f"{', '.join(artist.name for artist in self.artists)}<br>"
                f"{img_link}"
            )
        else:
            raise Exception(
                f"Unknown format type {fmt_type}. Options are ['text', 'html']"
            )

    def get_primary_artist(self):
        return self.artists[0]

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

        # Get the release year
        self.release_year = int(spotify_album["release_date"].split("-")[0])

class Track(Music):
    """Class to hold selected information about a spotify track."""

    IMG_DIMEN = 64

    def __init__(self, spotify_track, search_term=None):

        # Initialize base class
        super().__init__(spotify_track, search_term)

        # Get image url with given IMG_DIMEN
        self._set_album_img(spotify_track["album"], self.IMG_DIMEN)

        # Get the release year (of the album)
        self.release_year = int(spotify_track["album"]["release_date"].split("-")[0])
