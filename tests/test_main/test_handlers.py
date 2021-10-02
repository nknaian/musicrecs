import re
from urllib.parse import urlparse
import time

from flask import url_for

from musicrecs.database.models import Round
from musicrecs.enums import MusicType, RoundStatus, SnoozinRecType
from musicrecs.main import schedule_round_advance

from tests.test_main import MainTestCase

from musicrecs import scheduler


class MainIndexTestCase(MainTestCase):
    """Test GET on main index route."""
    def test_get_index(self):
        response = self.client.get(url_for("main.index"))
        self.assert_200(response)
        self.assertIn(b"Musicrecs is a platform for sharing", response.data)


class MainAboutTestCase(MainTestCase):
    """Test GET on main about route."""
    def test_get_about(self):
        response = self.client.get(url_for("main.about"))
        self.assert_200(response)
        self.assertIn(b"Each recommendation round has three phases", response.data)


class MainCreateRoundTestCase(MainTestCase):
    """Test GET and POST on main create_round route.

    For POST test, try posting with form data filled in
    to create a new round.
    """
    ROUND_URL_RE_PATTERN = "(?<=/round/)(.{22})$"

    def test_get_create_round(self):
        response = self.client.get(url_for("main.create_round"))
        self.assert_200(response)
        self.assertIn(b"Describe the round", response.data)

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

    def test_create_round_scheduled(self):
        round = self._test_create_round(
            description="Test scheduled round",
            music_type=MusicType.album,
            snoozin_rec_type=SnoozinRecType.random,
            scheduled_round=True,
            scheduled_round_interval=1
        )

        # Verify that the schedule round advance job is running
        self.assertIsNotNone(scheduler.get_job(schedule_round_advance.job_id(round)))

        # Verify that the round status changes to listen after 1 second
        time.sleep(1.1)
        self.assertEqual(round.status, RoundStatus.listen)

        # Vefify that the round status changes to revealed after 1 second
        time.sleep(1.1)
        self.assertEqual(round.status, RoundStatus.revealed)

        # Verify that the round status is still revealed and the
        # schedule round advance job was removed
        time.sleep(1.1)
        self.assertEqual(round.status, RoundStatus.revealed)
        self.assertIsNone(scheduler.get_job(schedule_round_advance.job_id(round)))

    def _test_create_round(self, description, music_type, snoozin_rec_type,
                           scheduled_round=None, scheduled_round_interval=None):
        # Make post with `NewRoundForm` data
        response = self.client.post(url_for("main.create_round"), data=dict(
            description=description,
            music_type=music_type,
            snoozin_rec_type=snoozin_rec_type,
            scheduled_round=scheduled_round,
            scheduled_round_interval=scheduled_round_interval
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

        return round
