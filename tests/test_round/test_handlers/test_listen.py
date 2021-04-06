from unittest.mock import Mock

from flask.helpers import url_for

from musicrecs import spotify_iface
from musicrecs.spotify import spotify_user
from musicrecs.enums import MusicType, RoundStatus, SnoozinRecType
from musicrecs.spotify.item.spotify_playlist import SpotifyPlaylist
from musicrecs.database.helpers import add_round_to_db, add_submission_to_db

from tests.test_round import RoundTestCase


class RoundListenTestCase(RoundTestCase):
    """Test POST and GET to round.listen route

    For an album round, and a track round, test that the submissions
    are present on the round page.

    For the track round, also test that playlist creation works.
    """
    def test_album_listen(self):
        # Add a round to the database
        round = add_round_to_db(
            description="Albumrecs random round",
            music_type=MusicType.album,
            snoozin_rec_type=SnoozinRecType.random,
            status=RoundStatus.listen
        )

        # Add a couple submissions to the round
        add_submission_to_db(round.id, "Nick Jones", "https://open.spotify.com/album/3a0UOgDWw2pTajw85QPMiz")
        add_submission_to_db(round.id, "snoozin", "https://open.spotify.com/album/5Z9iiGl2FcIfa3BMiv6OIw")

        # Verify that the round page contains submissions
        response = self.client.get(url_for('round.listen', long_id=round.long_id))
        self.assert_200(response)
        self.assertIn(bytes("Nick Jones", 'utf-8'), response.data)
        self.assertIn(bytes("https://open.spotify.com/album/3a0UOgDWw2pTajw85QPMiz", 'utf-8'), response.data)
        self.assertIn(bytes("snoozin", 'utf-8'), response.data)
        self.assertIn(bytes("https://open.spotify.com/album/5Z9iiGl2FcIfa3BMiv6OIw", 'utf-8'), response.data)

    def test_track_listen(self):
        # Add a round to the database
        round = add_round_to_db(
            description="Trackrecs random round",
            music_type=MusicType.track,
            snoozin_rec_type=SnoozinRecType.random,
            status=RoundStatus.listen
        )

        # Add a couple submissions to the round
        add_submission_to_db(round.id, "John Doe", "http://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
        add_submission_to_db(round.id, "snoozin", "http://open.spotify.com/track/7GhIk7Il098yCjg4BQjzvb")

        # Verify that the round page contains submissions
        response = self.client.get(url_for('round.listen', long_id=round.long_id))
        self.assert_200(response)
        self.assertIn(bytes("John Doe", 'utf-8'), response.data)
        self.assertIn(bytes("http://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6", 'utf-8'), response.data)
        self.assertIn(bytes("snoozin", 'utf-8'), response.data)
        self.assertIn(bytes("http://open.spotify.com/track/7GhIk7Il098yCjg4BQjzvb", 'utf-8'), response.data)

        # Mock the required spotify interfaces for creating a playlist
        playlist_mock = Mock(spec=SpotifyPlaylist)
        playlist_mock.link = "https://open.spotify.com/playlist/32O0SSXDNWDrMievPkV0Im"

        def _mock_create_playlist(*args, **kwargs):
            if "name" in kwargs:
                playlist_mock.name = kwargs["name"]
            else:
                playlist_mock.name = args[0]

            return playlist_mock

        spotify_user.create_playlist = Mock(side_effect=_mock_create_playlist)

        spotify_iface.get_playlist_from_link = Mock(return_value=playlist_mock)

        # Make a post to create a playlist
        response = self.client.post(
            url_for('round.listen', long_id=round.long_id),
            data=dict(name="john doe and snoozin make a playlist"),
            follow_redirects=False
        )

        # Verify that post was successfull, and redirected
        self.assertRedirects(response, url_for('round.listen', long_id=round.long_id))

        # Verify that the playlist link was added to the db
        self.assertEqual(round.playlist_link, "https://open.spotify.com/playlist/32O0SSXDNWDrMievPkV0Im")

        # Verify that the round page now contains the playlist name
        response = self.client.get(url_for('round.listen', long_id=round.long_id))
        self.assert_200(response)
        self.assertIn(bytes("john doe and snoozin make a playlist", 'utf-8'), response.data)
