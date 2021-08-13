from musicrecs.spotify.item.spotify_music import SpotifyMusic
from unittest.mock import Mock
from flask import url_for

from musicrecs.database.helpers import add_round_to_db, add_submission_to_db, add_user_to_db
from musicrecs.enums import MusicType, SnoozinRecType

from musicrecs import spotify_iface

from tests.test_user import UserTestCase


class UserRoundsTestCase(UserTestCase):
    """Test GET to the 'user.rounds' routes
    """
    def setUp(self):
        super().setUp()

        spotify_iface.get_music_from_link = Mock(side_effect=self._mock_get_music_from_link)

    def _mock_get_music_from_link(*args):
        """Return a spotify music object whose link attribute
        is equal to the link passed in
        """
        music_mock = Mock(spec=SpotifyMusic)
        music_mock.link = args[1]
        return music_mock

    def test_get_user_trackrecs(self):
        # Add a fake user to the database
        add_user_to_db(self.DUMMY_USER_SP_ID, self.DUMMY_USER_DISPLAY_NAME)

        # Mock authentication of the fake user
        self.auth_dummy_user()

        # Add a couple rounds with submissions from the dummy user
        round1 = add_round_to_db(
            description="Round 1",
            music_type=MusicType.track,
            snoozin_rec_type=SnoozinRecType.random,
        )
        round2 = add_round_to_db(
            description="Round 2",
            music_type=MusicType.track,
            snoozin_rec_type=SnoozinRecType.random,
        )
        add_submission_to_db(round1.id, 1, "John Doe", "http://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
        add_submission_to_db(round2.id, 1, "John Does", "http://open.spotify.com/track/7GhIk7Il098yCjg4BQjzvb")

        # Get trackrec rounds
        response = self.client.get(
            url_for('user.rounds'),
            query_string={'music_type': 'track'}
        )

        # Verify track page loads, with two user round entries
        self.assert_200(response)
        self.assertIn(bytes('Your trackrecs', 'utf-8'), response.data)
        self.assertEqual(response.data.count(bytes("user_round_block", 'utf-8')), 2)

    def test_get_user_albumrecs(self):
        # Add a fake user to the database
        add_user_to_db(self.DUMMY_USER_SP_ID, self.DUMMY_USER_DISPLAY_NAME)

        # Mock authentication of the fake user
        self.auth_dummy_user()

        # Add a couple rounds with submissions from the dummy user
        round1 = add_round_to_db(
            description="Round 1",
            music_type=MusicType.album,
            snoozin_rec_type=SnoozinRecType.random,
        )
        round2 = add_round_to_db(
            description="Round 2",
            music_type=MusicType.album,
            snoozin_rec_type=SnoozinRecType.random,
        )
        add_submission_to_db(round1.id, 1, "Nick Jones", "https://open.spotify.com/album/3a0UOgDWw2pTajw85QPMiz")
        add_submission_to_db(round2.id, 1, "Nick Joneses", "https://open.spotify.com/album/5Z9iiGl2FcIfa3BMiv6OIw")

        # Get trackrec rounds
        response = self.client.get(
            url_for('user.rounds'),
            query_string={'music_type': 'album'}
        )

        # Verify albums page loads, with two user round entries
        self.assert_200(response)
        self.assertIn(bytes('Your albumrecs', 'utf-8'), response.data)
        self.assertEqual(response.data.count(bytes("user_round_block", 'utf-8')), 2)
