class Artist:
    """Class to hold selected information about a spotify artist"""

    def __init__(self, spotify_artist):
        self.name = spotify_artist["name"]
        self.id = spotify_artist["id"]

    def get_name(self):
        return self.name
