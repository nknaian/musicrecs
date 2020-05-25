class Album:
    """Class to hold selected information about a spotify
    album that is useful to albumrecs
    """

    IMG_DIMEN = 300

    def __init__(self, spotify_album, search_term=None):
        # Name of the spotify album
        self.name = spotify_album["name"]

        # List of artist names credited
        self.artist_names = [
            artist["name"] for artist in spotify_album["artists"]
        ]

        # Get the open.spotify link to the album
        self.link = spotify_album["external_urls"]["spotify"]

        # Get image url with given IMG_DIMEN
        self.img_url = None
        for img in spotify_album["images"]:
            if img["height"] == self.IMG_DIMEN and \
                    img["width"] == self.IMG_DIMEN:
                self.img_url = img["url"]
                break
        if self.img_url is None:
            print("Error: No matching album image found")

        # Set search term that was used to get album
        self.search_term = search_term
