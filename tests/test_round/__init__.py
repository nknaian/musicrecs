from unittest.mock import Mock

from musicrecs.spotify.item.spotify_music import SpotifyMusic
from musicrecs import spotify_iface

from tests import MusicrecsTestCase


class RoundTestCase(MusicrecsTestCase):
    def setUp(self):
        super().setUp()

        # Mock the get_music_from_link spotify interface
        def _mock_get_music_from_link(*args):
            """Return a spotify music object whose link attribute
            is equal to the link passed in
            """
            music_mock = Mock(spec=SpotifyMusic)
            music_mock.link = args[1]
            return music_mock

        spotify_iface.get_music_from_link = Mock(side_effect=_mock_get_music_from_link)
