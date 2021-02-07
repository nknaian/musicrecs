from .spotify_item import SpotifyItem


class SpotifyPlaylist(SpotifyItem):
    """Class to hold selected information about a spotify artist"""

    def __init__(self, spotify_playlist):
        # Initialize base class
        super().__init__(spotify_playlist)
