import re

from flask.helpers import url_for

from musicrecs.enums import MusicType, RoundStatus, SnoozinRecType
from musicrecs.database.helpers import add_round_to_db, add_submission_to_db

from tests.test_round import RoundTestCase


class RoundRevealedTestCase(RoundTestCase):
    """Test GET to round.revealed route

    For an album round, and a track round, test that the submissions
    are present on the round page, and consist of the correct link - name pairs.
    """
    def test_album_revealed(self):
        # Add a round to the database
        round = add_round_to_db(
            description="Albumrecs random round",
            music_type=MusicType.album,
            snoozin_rec_type=SnoozinRecType.random,
            status=RoundStatus.revealed
        )

        # Add a couple submissions to the round
        add_submission_to_db(round.id, "Nick Jones", "https://open.spotify.com/album/3a0UOgDWw2pTajw85QPMiz")
        add_submission_to_db(round.id, "Jonie Nixon", "https://open.spotify.com/album/1vz94WpXDVYIEGja8cjFNa")
        add_submission_to_db(round.id, "snoozin", "https://open.spotify.com/album/5Z9iiGl2FcIfa3BMiv6OIw")

        # Verify that the round page contains the correct pairings of link with submitter
        response = self.client.get(url_for('round.listen', long_id=round.long_id))
        self.assert_200(response)
        href_results = re.findall(r'<a href=(.+?)</a>', str(response.data))
        for href_result in href_results:
            if "https://open.spotify.com/album/3a0UOgDWw2pTajw85QPMiz" in href_result:
                self.assertIn("recommended by Nick Jones", href_result)
            elif "https://open.spotify.com/album/1vz94WpXDVYIEGja8cjFNa" in href_result:
                self.assertIn("recommended by Jonie Nixon", href_result)
            elif "https://open.spotify.com/album/5Z9iiGl2FcIfa3BMiv6OIw" in href_result:
                self.assertIn("recommended by snoozin", href_result)
            else:
                raise Exception(f"Unknown link in href {href_result}")

    def test_track_revealed(self):
        # Add a round to the database
        round = add_round_to_db(
            description="Albumrecs random round",
            music_type=MusicType.track,
            snoozin_rec_type=SnoozinRecType.random,
            status=RoundStatus.revealed
        )

        # Add a few submissions to the round
        add_submission_to_db(round.id, "John Doe", "http://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
        add_submission_to_db(round.id, "Dory Johnson", "https://open.spotify.com/track/354K3xQPgALQEOiIYzAMat")
        add_submission_to_db(round.id, "snoozin", "http://open.spotify.com/track/7GhIk7Il098yCjg4BQjzvb")

        # Verify that the round page contains the correct pairings of link with submitter
        response = self.client.get(url_for('round.listen', long_id=round.long_id))
        self.assert_200(response)
        href_results = re.findall(r'<a href=(.+?)</a>', str(response.data))
        for href_result in href_results:
            if "http://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6" in href_result:
                self.assertIn("recommended by John Doe", href_result)
            elif "https://open.spotify.com/track/354K3xQPgALQEOiIYzAMat" in href_result:
                self.assertIn("recommended by Dory Johnson", href_result)
            elif "http://open.spotify.com/track/7GhIk7Il098yCjg4BQjzvb" in href_result:
                self.assertIn("recommended by snoozin", href_result)
            else:
                raise Exception(f"Unknown link in href {href_result}")
