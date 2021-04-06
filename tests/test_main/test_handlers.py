import re
from urllib.parse import urlparse

from flask import url_for

from musicrecs.database.models import Round
from musicrecs.enums import MusicType, RoundStatus, SnoozinRecType

from tests import MusicrecsTestCase


class MainIndexTestCase(MusicrecsTestCase):
    """Test GET and POST on the main index route.

    For POST test, try posting with form data filled in
    to create a new round.
    """
    ROUND_URL_RE_PATTERN = "(?<=/round/)(.{22})$"

    def test_get(self):
        response = self.client.get(url_for("main.index"))
        self.assert_200(response)
        self.assertIn(b"Musicrecs", response.data)

    def test_create_round_track_random(self):
        self._test_create_round(
            description="Test trackrecs round with random snoozin pick",
            music_type=MusicType.track,
            snoozin_rec_type=SnoozinRecType.random
        )

    def test_create_round_track_similar(self):
        self._test_create_round(
            description="Test trackrecs round with similar snoozin pick",
            music_type=MusicType.track,
            snoozin_rec_type=SnoozinRecType.similar
        )

    def test_create_round_album_random(self):
        self._test_create_round(
            description="Test albumrecs round with random snoozin pick",
            music_type=MusicType.album,
            snoozin_rec_type=SnoozinRecType.random
        )

    def test_create_round_album_similar(self):
        self._test_create_round(
            description="Test albumrecs round with similar snoozin pick",
            music_type=MusicType.album,
            snoozin_rec_type=SnoozinRecType.similar
        )

    def _test_create_round(self, description, music_type, snoozin_rec_type):
        # Make post with `NewRoundForm` data
        response = self.client.post(url_for("main.index"), data=dict(
            description=description,
            music_type=music_type,
            snoozin_rec_type=snoozin_rec_type
        ), follow_redirects=False)

        # Verify that post was successfull, and redirected (302)
        self.assertEqual(response.status_code, 302)

        # Verify that the redirect url is of the correct form, and retrieve the round's long id
        long_id_search = re.search(self.ROUND_URL_RE_PATTERN, urlparse(response.location).path)
        self.assertIsNotNone(long_id_search)
        long_id = long_id_search.group()

        # Verify that the round was created and has been initialized with the
        # correct values
        round = Round.query.filter_by(long_id=long_id).first()
        self.assertIsNotNone(round)
        self.assertEqual(round.description, description)
        self.assertEqual(round.music_type, music_type)
        self.assertEqual(round.snoozin_rec_type, snoozin_rec_type)
        self.assertEqual(round.status, RoundStatus.submit)
